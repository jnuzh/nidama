#!/usr/bin/env python
# Copyright (c) 2007 ActiveState Software Inc.
# License: TODO

"""Run test plans and work with the data."""

__version_info__ = (0, 1, 0)
__version__ = '.'.join(map(str, __version_info__))


import os
from os.path import abspath, dirname, join, basename, expanduser
import sys
import re
from pprint import pprint
import traceback
import logging
import optparse
import threading
import subprocess
import koprocessutils
import process
import types
import which

from xpcom import components

#---- exceptions

class Error(Exception):
    pass

class UnexpectedEventData(Exception):
    pass


#---- globals

sleuth_dir = dirname(__file__) or os.curdir 
log = logging.getLogger("sleuth.main")

#log.setLevel(logging.DEBUG)

_letter_result_re = re.compile(r'(\w):\s*(\d+)')
_curr_suite_results = None
_suite_results_stack = []

#---- module API

def run_test_plan(test_plan):
    for event in test_plan.run_tests():
        print event
 
def do_test_plan(test_plan):
    #DEPRECATED, use test_plan.run_tests() directly
    for event in test_plan.run_tests():
        yield event
 
def sleuth(test_plans):
    """Run the set of test plans.
    
    @param test_plans {TestPlans array of TestPlan} defines the test to run.
    """
    for test_plan in test_plans:
        run_test_plan(test_plan)

#---- Helper functions for managing the environment

def get_extra_paths(prefName):
    prefset = components.classes["@activestate.com/koPrefService;1"].getService().effectivePrefs
    if prefset.hasPref(prefName):
        extraPaths = prefset.getStringPref(prefName)
        if extraPaths:
            if sys.platform.startswith("win"):
                encoding = sys.getfilesystemencoding()
                try:
                    extraPaths = extraPaths.encode(encoding).replace('\\', '/')
                except UnicodeEncodeError:
                    log.warn("Could not encode pref %s, so ignoring it", prefName)
                    return []
            return [x for x in extraPaths.split(os.pathsep) if x.strip()]
    return []

def fixLanguageIncludePath(env, langPrefName, langEnvPathName, sepChar=None):
    extra_paths_list = get_extra_paths(langPrefName)
    if extra_paths_list:
        existingPaths = env.get(langEnvPathName, None)
        if existingPaths and sys.platform == 'win32':
            encoding = sys.getfilesystemencoding()
            try:
                existingPaths = existingPaths.encode(encoding).replace('\\', '/')
            except UnicodeEncodeError:
                log.warn("Could not encode pref %s, so ignoring it", prefName)
                existingPaths = None
        if existingPaths:
            # For Tcl, break the existing path using os.pathsep, but
            # put it together with the sepChar (should be a space)
            extra_paths_list += existingPaths.split(os.pathsep)
        if sepChar is None:
            sepChar = os.pathsep
            # os.pathsep not allowed in pathnames, by definition
            fixed_paths = extra_paths_list
        else:
            # Quote parts if needed.  If a path contains both the sepchar
            # and the quote char, tough.
            qq = '"'
            fixed_paths = []
            for path in extra_paths_list:
                if sepChar not in path:
                    fixed_paths.append(path)
                elif qq not in path:
                    fixed_paths.append(qq + path + qq)
        env[langEnvPathName] = sepChar.join(fixed_paths)

class _SuiteResults(object):
    """
    For now assume test-suite results don't nest
    """
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.num_tests = 0
        self.num_passes = 0
        self.num_errors = 0
        self.num_failures = 0
        self.num_skipped = 0
        self.num_incomplete = 0

    def get_status_values(self, all=True):
        a = [self.num_tests,
             self.num_passes,
             self.num_errors,
             self.num_failures]
        if all:
            a += [self.num_skipped,
                  self.num_incomplete]
        else:
            self.num_passes += self.num_skipped + self.num_incomplete
        return a

    def get_status_string(self):
        s = "%d tests, %d passed" % (self.num_tests,
                                     self.num_passes)
        if self.num_errors:
            s += ", %d errors" % (self.num_errors)
        if self.num_failures:
            s += ", %d failures" % (self.num_failures)
        if self.num_skipped:
            s += ", %d skipped" % (self.num_skipped)
        if self.num_incomplete:
            s += ", %d incomplete" % (self.num_incomplete)
        return s

#---- Test Events

class TestEvent(object):
    def add(self, info):
        raise UnexpectedEventData(info)
    
    def __repr__(self):
        return "<%s>" % self.__class__.__name__

class SuiteStartEvent(TestEvent):
    def __init__(self, data=None):
        self.data = data
        global _curr_suite_results, _suite_results_stack
        _curr_suite_results = _SuiteResults()
        _suite_results_stack.append(_curr_suite_results)
    
class SuiteFinishedEvent(TestEvent):
    """    
    @param summary_text {string[]} Perl, for example has this useful output when
    a test fails miserably:
            DIED. FAILED tests 1-73
                Failed 73/73 tests, 0.00% okay
        Failed Test     Stat Wstat Total Fail  List of Failed
        -------------------------------------------------------------------------------
        t/01substrate.t    1   256    20    1  1
        t/02cluster.t      1   256    21    1  1
        t/03reaction.t     1   256    53    1  1
        t/04network.t    255 65280    38   75  1-38
        t/05dynamics.t   255 65280    18   34  1-18
        t/06matrixops.t  255 65280    73  145  1-73
        Failed 6/6 test scripts. 132/223 subtests failed.
        Files=6, Tests=223,  1 wallclock secs ( 0.00 cusr +  0.00 csys =  0.00 CPU)
        Failed 6/6 test programs. 132/223 subtests failed.
        NMAKE : fatal error U1077: 'C:\Perl\bin\perl.exe' : return code '0xff'
        Stop.
        
    Other fields should be self-explanatory.
    """
    def __init__(self, elapsed_time=None):
        self.elapsed_time = elapsed_time
        self.summary_text = []
        global _curr_suite_results
        try:
            _curr_suite_results = _suite_results_stack.pop()
        except IndexError:
            # Recover in case a module returns an unmatched SuiteFinishedEvent
            _curr_suite_results = _SuiteResults()

    def get_status_string(self):
        return _curr_suite_results.get_status_string()

    def get_status_values(self):
        return _curr_suite_results.get_status_values(False)

    def __repr__(self):
        repstr =  "<%s num_tests=%d, num_passes=%d, num_errors=%d, num_failures=%d" \
               % (self.__class__.__name__,
                  _curr_suite_results.num_tests,
                  _curr_suite_results.num_passes,
                  _curr_suite_results.num_errors,
                  _curr_suite_results.num_failures)
        if _curr_suite_results.num_skipped:
            repstr += ", num_skipped=%d" % (_curr_suite_results.num_skipped)
        if _curr_suite_results.num_incomplete:
            repstr += ", num_incomplete=%d" % (_curr_suite_results.num_incomplete)
        if self.elapsed_time:
            repstr += ", elapsed_time=%s" % (self.elapsed_time)
        status_string = self.get_status_string()
        if status_string:
            repstr += ", [%s]" % (status_string,)
        repstr += ">"
        return repstr
        
    def add(self, info):
        self.summary_text.append(info)

class TestStartEvent(TestEvent):
    def __init__(self, name=None):
        """
        @param name {string} Either the test name, or a pathname relative to
            the directory containing the test plan
        """
        self.name = name
        
    def __repr__(self):
        if self.name:
            return "<%s %s>" % (self.__class__.__name__, self.name)
        else:
            return "<%s>" % (self.__class__.__name__,)
    
class TestFinishedEvent(TestEvent):
    def __init__(self, outcome="P"):
        self.outcome = outcome
        _curr_suite_results.num_tests += 1
        if outcome == "P":
            _curr_suite_results.num_passes += 1
        elif outcome == "E":
            _curr_suite_results.num_errors += 1
        elif outcome == "F":
            _curr_suite_results.num_failures += 1
        elif outcome == "S":
            _curr_suite_results.num_skipped += 1
        elif outcome == "I":
            _curr_suite_results.num_incomplete += 1

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.outcome)
    
class TestInfoEvent(TestEvent):
    def __init__(self, info=None):
        self.info = (info and [info]) or []
        
    def add(self, info):
        self.info.append(info)
        
    def __repr__(self):
        return "<%s [%s]>" % (self.__class__.__name__,
                              "\n    ".join([str(x) for x in self.info]))

class TestFaultEvent(TestInfoEvent):
    pass


#---- Test Plans
# Evenutally there should be a separate TestPlan subclass for each type of test
# harness that we support. Some likely examples:
#   PHPTestPlan     Knows how to look for and run PHPUnit-based test
#                   files in a given dir (harnesses/php).
#   RakeTestPlan    Knows how to run the "rake test" set of tasks
#                   in a Ruby/rake setup (including Rails projects).
#   ...
#
# A specific test plan type has some data (e.g. a directory in which
# to look for tests, or a project base dir from which to run rake tasks)
# and knows how to run the test suite. Some other base API methods may
# be added (e.g. being able to list all the available tests).
#


class TestPlan(object):
    def __init__(self, harness, test_dir, language, command_line):
        self._harness = harness
        self._test_dir = test_dir
        self._language = language
        if isinstance(command_line, (types.StringType, types.UnicodeType)):
            command_line = self._line2argv(command_line)
        self._command_line = command_line
        self._runLock = threading.Lock()
        self._isStopped = False
        #log.debug("@@@ Using harness %s", self._harness)
        
    def run_tests(self):
        """
        Run the full test plan and generate test results as they
        come back.

        See kd-0190 for a description of expected output from a
        test run.
            
        A test suite is always run out of process.
        The harness marks up the output stream so that test run progress
        and status can be parsed.
        
        """
        global _suite_results_stack, _curr_suite_results
        _curr_suite_results = _SuiteResults()
        _suite_results_stack.append(_curr_suite_results)
        try:
            if not getattr(self, "_iSvc", False):
                self._iSvc = components.classes["@activestate.com/koInterpolationService;1"]\
                    .getService(components.interfaces.koIInterpolationService)
            for spelling in (self._language, self._language.lower()):
                istring = "%(" + spelling + ")"
                try:
                    queries, i1strings = self._iSvc.Interpolate1([istring],
                                                                 [],
                                                                 "", 0,  # file + line
                                                                 "", "", "", None)
                    executable = i1strings[0]
                    #log.debug("interpolate(%s) => %r", istring, executable)
                except:
                    log.exception("Can't interpolate %s", istring)
                    executable = None
                if executable == istring:
                   executable = None
                if executable:
                    break
        except:
            import traceback
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            executable = None
        self._runLock.acquire()
        try:
            if self._isStopped:
                raise StopIteration
            try:
                log.debug("Running %s <%s> in dir <%s>",
                          executable, self._command_line, self._test_dir)
                self._harness.initialize(self._command_line, self._test_dir, executable)
            except:
                log.exception("Problem creating a harness")
                log.debug("%s", "=" * 70)
                raise StopIteration
        finally:
            self._runLock.release()
        for event in self.parse_test_output():
            if self._isStopped:
                raise StopIteration
            yield event
        try:
            _curr_suite_results = _suite_results_stack.pop()
        except IndexError:
            _curr_suite_results = None
            #log.error("Popped the _suite_results_stack")
        
    def stop(self):
        self._runLock.acquire()
        try:
            self._isStopped = True
            self._harness.stop()
        finally:
            self._runLock.release()

    def parse_test_output(self):
        # states
        state_in_suite  = 0x01
        state_in_test   = 0x02
        state_in_fault  = 0x04
        state_in_output = 0x08
        state = 0
        event = None  # The current event-object
        for line in self._harness.run():
            # log.debug("%s", line)
            line = line.rstrip()
            stripped_line = line.lstrip()
            if stripped_line.startswith("#QQQ:"):
                log.debug("%s", line[5:])
                continue
            m = re.compile(r'@([^@]+)@:?\s*(.*)').match(stripped_line)
            if m:
                if event:
                    yield event
                    event = None
                event_type = m.group(1)
                event_data = m.group(2)
                if event_type == "suite_started":
                    event = SuiteStartEvent(event_data)
                    state = state_in_suite
                elif event_type == "suite_finished":
                    if state & state_in_test:
                        yield TestFinishedEvent()
                    info_parts = (event_data or "").split(";", 1)
                    elapsed_time = None
                    if info_parts[0]:
                        test_results = dict(_letter_result_re.findall(info_parts[0]))
                        elapsed_time = info_parts[1]
                    else:
                        test_results = {}
                        # Pull out results
                    event = SuiteFinishedEvent(elapsed_time)
                    state = 0
                elif event_type == "test_started":
                    if state & state_in_test:
                        yield TestFinishedEvent()
                    if not (state & state_in_suite):
                        state = state_in_suite
                        yield SuiteStartEvent()
                    state |= state_in_test
                    event = TestStartEvent(event_data)
                elif event_type == "test_result":
                    if not (state & state_in_suite):
                        state = state_in_suite
                        yield SuiteStartEvent()
                    state &= ~state_in_test
                    event = TestFinishedEvent(event_data)
                elif event_type == "fault":
                    if not (state & state_in_suite):
                        state = state_in_suite
                        yield SuiteStartEvent()
                    event = TestFaultEvent(event_data)
                elif event_type == "info":
                    if not (state & state_in_suite):
                        state = state_in_suite
                        yield SuiteStartEvent()
                    event = TestInfoEvent(event_data)
                elif event_type == "output":
                    event = TestInfoEvent(event_data)
                else:
                    raise Exception("Unrecognized line: %r" % line)
            elif event and stripped_line:
                if not isinstance(event, TestInfoEvent):
                    yield event
                    event = TestInfoEvent(line)
                else:
                    event.add(line)
            elif state == 0 and stripped_line:
                # Create a suite so we have an info object to pass the output
                # back to.
                state = state_in_suite
                yield SuiteStartEvent()
                event = TestFaultEvent(line)
            elif stripped_line:
                print "*** Ignoring line %r" % (line,)
        if event:
            yield event
        if not isinstance(event, SuiteFinishedEvent):
            yield SuiteFinishedEvent()
    
    def _line2argv(self, line):
        r"""Stolen from util/cmdln.py
        """
        line = line.strip()
        argv = []
        state = "default"
        arg = None  # the current argument being parsed
        i = -1
        WHITESPACE = '\t\n\x0b\x0c\r '  # don't use string.whitespace (bug 81316)
        while 1:
            i += 1
            if i >= len(line): break
            ch = line[i]
    
            if ch == "\\": # escaped char always added to arg, regardless of state
                if arg is None: arg = ""
                i += 1
                arg += line[i]
                continue
    
            if state == "single-quoted":
                if ch == "'":
                    state = "default"
                else:
                    arg += ch
            elif state == "double-quoted":
                if ch == '"':
                    state = "default"
                else:
                    arg += ch
            elif state == "default":
                if ch == '"':
                    if arg is None: arg = ""
                    state = "double-quoted"
                elif ch == "'":
                    if arg is None: arg = ""
                    state = "single-quoted"
                elif ch in WHITESPACE:
                    if arg is not None:
                        argv.append(arg)
                    arg = None
                else:
                    if arg is None: arg = ""
                    arg += ch
        if arg is not None:
            argv.append(arg)
        if state != "default":
            raise ValueError("command line is not terminated: unfinished %s "
                             "segment" % state)
        return argv


#---- internal support stuff

class _NoReflowFormatter(optparse.IndentedHelpFormatter):
    """An optparse formatter that does NOT reflow the description."""
    def format_description(self, description):
        return description or ""

# Recipe: pretty_logging (0.1) in C:\trentm\tm\recipes\cookbook
class _PerLevelFormatter(logging.Formatter):
    """Allow multiple format string -- depending on the log level.

    A "fmtFromLevel" optional arg is added to the constructor. It can be
    a dictionary mapping a log record level to a format string. The
    usual "fmt" argument acts as the default.
    """
    def __init__(self, fmt=None, datefmt=None, fmtFromLevel=None):
        logging.Formatter.__init__(self, fmt, datefmt)
        if fmtFromLevel is None:
            self.fmtFromLevel = {}
        else:
            self.fmtFromLevel = fmtFromLevel
    def format(self, record):
        record.lowerlevelname = record.levelname.lower()
        if record.levelno in self.fmtFromLevel:
            #XXX This is a non-threadsafe HACK. Really the base Formatter
            #    class should provide a hook accessor for the _fmt
            #    attribute. *Could* add a lock guard here (overkill?).
            _saved_fmt = self._fmt
            self._fmt = self.fmtFromLevel[record.levelno]
            try:
                return logging.Formatter.format(self, record)
            finally:
                self._fmt = _saved_fmt
        else:
            return logging.Formatter.format(self, record)

def _setup_logging(stream=None):
    """Do logging setup:

    We want a prettier default format:
         do: level: ...
    Spacing. Lower case. Skip " level:" if INFO-level. 
    """
    hdlr = logging.StreamHandler(stream)
    defaultFmt = "%(name)s: %(levelname)s: %(message)s"
    infoFmt = "%(name)s: %(message)s"
    fmtr = _PerLevelFormatter(fmt=defaultFmt,
                              fmtFromLevel={logging.INFO: infoFmt})
    hdlr.setFormatter(fmtr)
    logging.root.addHandler(hdlr)

#---- base class TestHarness

class KoSleuthHarness(object):
    def __init__(self, cmd, cwd=None):
        self._cmd = cmd
        if cwd is None:
            self._cwd = os.getcwd()
        else:
            self._cwd = cwd
            
    def filter_line(self, line, line_num):
        return False
        
    def run(self, env=None):
        flags, shell = self._flags_shell_from_launch_conditions()
        self.p, msgs = self._launch_process(shell, flags, env)
        if self.p is None:
            for line in msgs:
                yield line
            raise StopIteration
        line_num = 0
        #XXX Put the loop in a try/finally block so we always wait.
        while True:
            line = self.p.stdout.readline()
            if not line:
                break
            line_num += 1
            if self.filter_line(line, line_num):
                continue
            yield line
        self.p.wait()

    def _get_non_komodo_env(self):
        # Pull out entries that point into the Komodo area
        # Do this for all languages, not just Python, in case other
        # executables lurk that the tests might point to.
        # Also because right now I don't know which language we're running.
        env = koprocessutils.getUserEnv()
        koDir = components.classes["@activestate.com/koDirs;1"].\
            getService(components.interfaces.koIDirs).installDir
        for part in ['PYTHONPATH', 'PATH']:
            if part in env:
                arr = env[part].split(os.path.pathsep)
                arr2 = [x for x in arr if not x.startswith(koDir)]
                env[part] = os.path.pathsep.join(arr2)
        if sys.platform == 'win32' and env:
            # More code from process.py
            encoding = sys.getfilesystemencoding()
            _enc_env = {}
            for key, value in env.items():
                try:
                    _enc_env[key.encode(encoding)] = value.encode(encoding)
                except UnicodeEncodeError:
                    # Could not encode it, warn we are dropping it.
                    log.warn("Could not encode environment variable %r "
                             "so removing it", key)
            env = _enc_env
        return env

    def _launch_process(self, shell, flags, env=None):
        try:
            log.debug("Launching cmd=%s, in dir %s, shell=%r\n\n", self._cmd, self._cwd, shell)
            if env is None:
                env = self._get_non_komodo_env()
            p = subprocess.Popen(self._cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 shell=shell,
                                 cwd=self._cwd,
                                 env=env,
                                 # universal_newlines=True,
                                 creationflags=flags)
            return p, []
        except OSError, ex:
            msgs = ["@suite_started@: Failed to launch tests",
                    "@fault@:",
                    ]
            if ex.args[1] == "No such file or directory":
                log.error("Can't find [%s] in dir %s",
                          self._cmd, self._cwd)
                msgs += ["No such file or directory",
                        "  for command-line=%s" % (self._cmd, ),
                        "  for directory=%s" % (self._cwd, ),
                         ]
            else:
                msgs += ["Unexpected OSError: %s" % (ex,)]
            msgs += ["@suite_finished@:"]
            return None, msgs

    def _flags_shell_from_launch_conditions(self):
        if sys.platform.startswith("win"):
            # Don't display the Windows GPF dialog if the invoked program dies.
            # See comp.os.ms-windows.programmer.win32
            #  How to suppress crash notification dialog?, Jan 14,2004 - Raymond Chen's response
            # (URL http://groups.google.com/group/comp.os.ms-windows.programmer.win32/tree/browse_frm/thread/eeade5ecfa04d000/658b412a62ef5d7a?hl=en&rnum=1&q=suppressing+%22has+encountered+a+problem+and+needs+to+close%22+windows&_done=%2Fgroup%2Fcomp.os.ms-windows.programmer.win32%2Fbrowse_frm%2Fthread%2Feeade5ecfa04d000%2F74397b6bf9405304%3Fhl%3Den%26lnk%3Dst%26q%3Dsuppressing%2B%2522has%2Bencountered%2Ba%2Bproblem%2Band%2Bneeds%2Bto%2Bclose%2522%2Bwindows%26#doc_41fe71be34d3614b)
            import ctypes
            SEM_NOGPFAULTERRORBOX = 0x0002 # From MSDN
            ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
            CREATE_NO_WINDOW = 0x8000000 # same as win32process.CREATE_NO_WINDOW
            flags = CREATE_NO_WINDOW
            shell = not self._cmd[0].lower().endswith(".exe")
        else:
            flags = 0
            shell = False
        return (flags, shell)

    def stop(self):
        # From process.py
        if sys.platform.startswith("win"):
            import ctypes
            ctypes.windll.kernel32.TerminateProcess(int(self.p._handle), 1)
            self.p.returncode = -1
        else:
            import signal
            try:
                os.kill(self.p.pid, signal.SIGKILL)
            except OSError, ex:
                if ex.errno != 3:
                    # Ignore:   OSError: [Errno 3] No such process
                    raise
            self.p.returncode = -1
        
class KoSleuthHarnessRunner(object):
    def __init__(self):
        self._harness = None
        self._initial_msgs = []
        
    def lookupOutsideKoPath(self, program):
        env = koprocessutils.getUserEnv()
        koDir = components.classes["@activestate.com/koDirs;1"].\
            getService(components.interfaces.koIDirs).installDir
        path = env["PATH"]
        fixedPathArray = [x for x in path.split(os.path.pathsep)
                          if not x.startswith(koDir)]
        try:
            return which.which(program, fixedPathArray)
        except which.WhichError, ex:
            log.info("couldn't find program %s on path %s: %s",
                     program, "\n\t".join(fixedPathArray),
                     ex.message)
            
        
    def run(self):
        for line in self._initial_msgs:
            yield line
        if not self._harness:
            return
        try:
            for line in self._harness.run():
                yield line
        except StopIteration:
            pass

    def stop(self):
        self._harness.stop()

#---- mainline

def main(argv):
    usage = "usage: %prog TEST-PLAN"
    version = "%prog "+__version__
    parser = optparse.OptionParser(usage=usage,
        version=version, description=__doc__,
        formatter=_NoReflowFormatter())
    parser.add_option("-v", "--verbose", dest="log_level",
                      action="store_const", const=logging.DEBUG,
                      help="more verbose output")
    parser.add_option("-q", "--quiet", dest="log_level",
                      action="store_const", const=logging.WARNING,
                      help="quieter output")
    parser.set_defaults(log_level=logging.INFO)
    opts, args = parser.parse_args()
    log.setLevel(opts.log_level)

    #if len(args) != 1:
    #    raise Error("incorrect number of args (see `%s --help')", argv[0])
    #test_plan = args[0]
    
    test_plans = []
    # HACK for now
    # Not ready yet.
    ####print "Run Python-hello"
    ####pyhello_dir = join(dirname(abspath(__file__)), "examples",
    ####                   "python-hello")
    ####test_plan = PyUnitTestPlan([pyhello_dir])
    ########test_plan.run_tests()
    ####test_plans.append(test_plan)
    ####print "Done Python-hello"
    
    
    # HACK for Perl testing
    if False:
        perl_hello_dir = join(dirname(abspath(__file__)), "examples",
                           "perl-hello")
        test_plan = TestPlan(perl_hello_dir, "Perl", "")
        test_plans.append(test_plan)
        
    if False:
        bioperl_dir = join(dirname(abspath(__file__)), "examples",
                           "perl-Bio-Metabolic-0.07")
        test_plan = TestPlan(bioperl_dir, "Perl", "")
        test_plans.append(test_plan)    
    
    if True:
        perl_switch_dir = join(dirname(abspath(__file__)), "examples",
                           "perl-Switch-2.09")
        test_plan = TestPlan(perl_switch_dir, "Perl", "")
        test_plans.append(test_plan)    
    
    # Hardwire Ruby tests
    if True:
        ruby_builder_dir = join(dirname(abspath(__file__)), "examples",
                           "ruby", "builder")
        test_plans.append(TestPlan(ruby_builder_dir, "Ruby", ""))
        ruby_simple_dir = join(dirname(abspath(__file__)), "examples",
                           "ruby", "simple")
        test_plans.append(TestPlan(ruby_simple_dir, "Ruby", ""))
        test_plans.append(TestPlan(join(dirname(abspath(__file__)), "examples",
                                        "ruby", "flickr-1.0.0"), "Ruby", ""))
    
    # Hardwire PHP tests
    if False:
        # PHP looks for tests as a subdir.
        php_dir = join(dirname(abspath(__file__)), "examples",
                           "php")
        test_plans.append(TestPlan(php_dir, "PHP", ""))
    
    sleuth(test_plans)


if __name__ == "__main__":
    _setup_logging()
    try:
        retval = main(sys.argv)
    except SystemExit:
        pass
    except KeyboardInterrupt:
        sys.exit(1)
    except:
        exc_info = sys.exc_info()
        if True or log.level <= logging.DEBUG:
            import traceback
            print
            traceback.print_exception(*exc_info)
        else:
            if hasattr(exc_info[0], "__name__"):
                #log.error("%s: %s", exc_info[0].__name__, exc_info[1])
                log.error(exc_info[1])
            else:  # string exception
                log.error(exc_info[0])
        sys.exit(1)
    else:
        sys.exit(retval)
