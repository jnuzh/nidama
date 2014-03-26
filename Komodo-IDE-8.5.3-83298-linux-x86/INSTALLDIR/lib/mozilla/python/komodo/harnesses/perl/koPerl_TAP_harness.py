#!python

import os
from os.path import join, exists, dirname, isdir
import sys
import logging
import re
from pprint import pprint
import process
import subprocess
import sleuth

try:
    import which
    haveWhich = True
except ImportError:
    haveWhich = False

log = logging.getLogger("sleuth.harness.perl")
#log.setLevel(logging.DEBUG)

_VAGUE_PLAN = -1
""" Patterns, and what we're looking for:

Put all patterns here once we know what we're looking for.
"""
# Assume test names never contain two contiguous dots
#TODO: Refine this if the test name ends with \.t\b
_test_name_re = re.compile(r'(t[\\/].+?)\.{2,}\s*(.*)\s*$')

_simple_path_re = re.compile(r'[a-zA-Z0-9_\\.:]+$')
# Banners and other patterns at the start that we can safely ignore
_start_patterns_to_ignore = [re.compile(s) for s in (
                            r'perl.*blib.lib.*blib.arch',
                            r'Microsoft.*Program Maintenance Utility',
                            r'Copyright.*Microsoft Corp.*All rights reserved',
                            # vc6 - Copyright (C) Microsoft Corp 1988-1998. All rights reserved.
                            # vc7 - Copyright (C) Microsoft Corporation.  All rights reserved.
                            # vc8 - Copyright (C) Microsoft Corporation.  All rights reserved.
                            r'make.*Entering directory',
                            r'make.*Leaving directory',
                            r'^cp lib.*blib',
                            r'^\t', # Ignore as a make command line
                         )]

_died_failed_tests_re = re.compile(r"DIED\.\s+FAILED tests? \d")
_failed_summary_re = re.compile(r'Failed \d+/\d+ test (?:script|program)s?')
_failed_test_list_re = re.compile(r"FAILED tests? \d")
_failed_cant_re = re.compile(r"failed:\s*Can't")
_failed_test_stat_summary_re = re.compile(r'''Failed\s+Test\s+Stat\s+
                                            (?:Wstat\s+)?
                                            (?:Total\s+)?
                                            (?:Fail\s+)?
                                            (?:List\s+of\s+Failed)?''', re.X)
_failed_num_re = re.compile(r'\s*\#\s*Failed')

_files_tests_summary_re = re.compile('Files=\d+, Tests=\d+,')
_test_got_something_re = re.compile(r'# Test \d+ got:.*\bat line \d')
_looks_like_your_test_died = re.compile(r'#\s+Looks like your test died before it could output anything')

_not_ok_line_re = re.compile(r'not ok\s+(\d+)\s*(.*)\s*')
_ok_line_re = re.compile(r'ok\s+(\d+)\s*\#\s*skip(?:ped|ping)?\s*(.*)\s*')
_ok_line_simple_re = re.compile(r'ok\s+(\d+)\s*(.*)\s*')

_num_dot_dot_num_re = re.compile(r'(\d+)\s*\.\.\s*(\d+)\s*$')
_undefined_sub_re = re.compile(r'Undefined subroutine .*? called at')

class KoHarnessPerlTests(sleuth.KoSleuthHarness):
    """If there's a Makefile, a test.pl, or a t/ directory, simply run the
    tests through Python's subprocess module to fold stderr and stdout, and
    convert the results to Komodo test output format.
    
    See unittest/koHarnessRuby.py for a description of the format
    this file should emit.
    """
    def __init__(self, cwd, cmd=None):
        self._cwd = cwd
        self._cmd = cmd

    def set_perl(self, perl):
        self._perl = perl

    def final_initialize(self):
        if not self._cmd:
            self._cmd, msgs = self._get_argv()
            return msgs
        return []

    def _get_argv(self, rebuild_makefile=True):
        # Determine the command to run
        msgs = []
        if exists(join(self._cwd, "Makefile")):
            make_exe = None
            if sys.platform == "win32":
                make_exe = _find_nmake_exe()
            elif haveWhich:
                try:
                    make_exe = which.which("make")
                except which.WhichError:
                    pass
            else:
                make_exe = process.ProcessOpen(['which', 'make']).communicate()[0]
                if make_exe:
                    make_exe = make_exe.rstrip()
            if make_exe:
                return ([make_exe, "test"], msgs)

        # Either no Makefile, or we couldn't find a "make/nmake" to call
        # it.
        if exists(join(self._cwd, "Makefile.PL")) and rebuild_makefile:
            res = process.ProcessOpen([self._perl, 'Makefile.PL'],
                                      cwd=self._cwd).communicate()
            # Fake a test-suite
            msgs.append("@suite_started@: rebuilding the Makefile")
            msgs.append("@fault@:")
            if res[0]:
                msgs.append(res[0]);
            if res[1]:
                msgs.append(res[1])
            msgs.append("@suite_finished@:")
            args, msgs2 = self._get_argv(False)
            return (args, msgs + msgs2)
        if exists(join(self._cwd, "test.pl")):
            return ([self._perl, "test.pl"], msgs)
        elif isdir(join(self._cwd, "t")):
            s = [self._perl, "-MExtUtils::Command::MM",
                    "-e", "\"test_harness(0, 'blib/lib', 'blib/arch')\"",
                    "t/*.t"]
            return (s, msgs)
        return ([], msgs)
    
    def _ignore_at_start(self, line):
        for p in _start_patterns_to_ignore:
            if p.search(line): return True
        return False
        
    def pre_state_handle_test_end(self, line=None):
        self._msgs.append("@suite_finished@:")
        if line is not None:
            self._msgs.append(line)
        self.got_failure_line = False
        
    def state_handle_test_end(self, line):
        # Skip most unrecognized input at the end
        if not self.got_failure_line and _failed_summary_re.match(line):
            self.got_failure_line = True
            self._msgs.append(line)
        elif _files_tests_summary_re.match(line):
            self._msgs.append(line)
        elif line.startswith('All tests successful'):
            self._msgs.append(line)
        return True, self.state_handle_test_end
    
    def _process_line_in_plan(self, line):
        m = _not_ok_line_re.match(line)
        if m:
            self._test_outcome = "F"
            return True, m.group(1), '_num_failed', m.group(2)
        m = _ok_line_re.match(line)
        if m:
            self._test_outcome = "S"
            return True, m.group(1), '_num_skipped', m.group(2)
        m = _ok_line_simple_re.match(line)
        if m:
            self._test_outcome = "P"
            return True, m.group(1), '_num_passed', m.group(2)
        return False, None, None, None
                    
    def _outcome_to_tag(self, outcome):
        return outcome == "P" and "info" or "fault"
    
    def check_end_t(self, filename):
        for prefix in ("", self._cwd):
            full_name = join(prefix, filename)
            if not exists(full_name) and exists(full_name + ".t"):
                return filename + ".t"
        return filename

    def print_test_started(self, name=None):
        #@@@@ OUTPUT
        if name is None:
            self._msgs.append("@test_started@:")
        else:
            self._msgs.append("@test_started@: %s" % (self.check_end_t(name),))
     
    def print_test_finished(self):
        self._msgs.append("@test_result@: %s" % (getattr(self, '_test_outcome', 'P'),))
    
    def pre_state_in_plan(self):
        self.finish_state = self.post_state_in_plan
        
    def print_fault_tag_if_needed(self):
        if self._test_outcome != "P":
            self._msgs.append("@fault@:")
        
    def state_in_plan(self, line):
        if line.startswith("#"):
            if not self._have_details:
                self.print_fault_tag_if_needed()
                self._have_details = True
            print line
        elif 'ok' in line:
            if self._have_details:
                self._have_details = False
                self.print_test_finished()
            elif self.inside_a_test:
                self.print_test_finished()
            have_match, test_name, result_attr, details = self._process_line_in_plan(line)
            if have_match:
                self.print_test_started(test_name)
                self.inside_a_test = True
                setattr(self, result_attr, getattr(self, result_attr) + 1)
                self._num_ran += 1
                if details:
                    self._have_details = True
                    self.print_fault_tag_if_needed()
                    print details
        else:
            self.unrecognized_warning(line)
        return True, self.state_in_plan # Stay in this state until the end
    
    def post_state_in_plan(self):
        # Finish up the plan
        #XXX Use _VAGUE_PLAN
        self.print_test_finished()
        self._msgs.append("@suite_finished@: N:%d, P:%d, F:%d, S:%d\n" % (
            self._num_ran, self._num_passed, self._num_failed, self._num_skipped))

    def pre_state_start_of_plan(self):
        self._num_passed = 0
        self._num_failed = 0
        self._num_skipped = 0
        self._num_ran = 0
        self._have_details = False
    # ==> state_in_plan
    def state_start_of_plan(self, line):
        if line.startswith('#'):
            return True, self.state_start_of_plan # No transition
        if 'ok' in line:
            have_match, test_name, result_attr, details = self._process_line_in_plan(line)
            if have_match:
                self.print_test_started(test_name)
                self.inside_a_test = True
                setattr(self, result_attr, getattr(self, result_attr) + 1)
                self._num_ran += 1
                if details:
                    self._have_details = True
                    self.print_fault_tag_if_needed()
                    self._msgs.append(details + "\n")
                self.pre_state_in_plan()
                return True, self.state_in_plan
        # Ignore this line, give warning, stay in this state
        self.unrecognized_warning(line)
        return True, self.state_start_of_plan
    
    def pre_state_before_suite(self):
        self.line = None
    # ==> state_handle_test_end, state_start_of_plan, state_in_suite_do_test_start
    def state_before_suite(self, line):
        if self._ignore_at_start(line):
            return True, self.state_before_suite # stay
        m = _failed_test_stat_summary_re.match(line)
        if m:
            self.pre_state_handle_test_end()
            return True, self.state_handle_test_end
        if line.startswith("Makefile out-of-date with respect"):
            self.pre_state_handle_test_end()
            return True, self.state_handle_test_end
        m = _num_dot_dot_num_re.match(line)
        if m:
            try:
                self._expected_num_tests = int(m.group(2)) - int(m.group(1)) + 1
            except:
                self._expected_num_tests = _VAGUE_PLAN
            #@@@@ OUTPUT
            self._msgs.append("@suite_started@:")
            self.pre_state_start_of_plan()
            return True, self.state_start_of_plan
        
        m = _test_name_re.match(line) #  (t[\\/]\w+)\.{2,}(.*)
        if m:
            self._msgs.append("@suite_started@:")
            self.pre_state_in_suite(m)
            return True, self.state_in_suite
        self.unrecognized_warning(line)
        return True, self.state_before_suite
    
    def unrecognized_warning(self, line):
        self._msgs.append("**** Unrecognized input: " + line)
        if getattr(self, 'num_unrecognized_warnings', None) is None:
            self.num_unrecognized_warnings = 1
        else:
            self.num_unrecognized_warnings += 1
            if self.num_unrecognized_warnings >= 20:
                print "**** Bailing out early..."
                sys.exit(1)
        
    def pre_state_in_suite(self, m):
        self.inside_a_test = True
        self.inside_a_fault_or_info = False
        self.print_test_started(m.group(1))
        tag = m.group(2)
        if not tag:
            self._test_outcome = ""
        elif tag == "ok":
            self._test_outcome = "P"
        elif (tag.startswith("# Failed ")
              or tag.startswith("Can't")
              or _failed_test_list_re.search(tag)
              or _died_failed_tests_re.search(tag)
              or _undefined_sub_re.search(tag)
              or _test_got_something_re.match(tag)
              or _looks_like_your_test_died.match(tag)
              or _failed_cant_re.search(tag)):
            print '@fault@:' + tag
            self._test_outcome = "F"
            self.inside_a_fault_or_info = True
        else:
            self._test_outcome = "P"
            print '@info@:' + tag
            self.inside_a_fault_or_info = True
            
    def finish_state_in_suite(self):
        if self.inside_a_test:
            self.inside_a_fault_or_info = False
            self.print_test_finished()
            
    def state_in_suite(self, line):
        if line.startswith('All tests successful'):
            self.finish_state_in_suite()
            self.pre_state_handle_test_end(line)
            return True, self.state_handle_test_end
        m = _failed_test_stat_summary_re.match(line)
        if m:
            self.finish_state_in_suite()
            self.pre_state_handle_test_end()
            return True, self.state_handle_test_end
        # Assume test names end with ".t"
        m = _test_name_re.match(line) #  (t[\\/]\w+)\.{2,}(.*)
        if m:
            self.finish_state_in_suite()
            self.pre_state_in_suite(m)
            return True, self.state_in_suite
        
        if _looks_like_your_test_died.match(line):
            self._msgs.append('@fault@:' + line)
            self._test_outcome = "F"
            self.inside_a_fault_or_info = True
        elif self.inside_a_fault_or_info:
            # Assume it's unrecognized, so emit it
            self._msgs.append(line)
        else:
            m = (_failed_num_re.match(line)
                 or _failed_test_list_re.search(line)
                 or _died_failed_tests_re.search(line))
            if m:
                self._msgs.append('@fault@:' + line)
                self._test_outcome = "F"
                self.inside_a_fault_or_info = True
            else:
                self.unrecognized_warning(line)
        return True, self.state_in_suite # Always stay here

    def run_state_machine(self):
        while True:
            if self.line is None:
                line = self.p.stdout.readline()
                if not line:
                    break
                line = line.rstrip()
            else:
                line = self.line
                self.line = None
            if not line: continue
            
            # Go do the next state, maybe transition
            self._msgs = []
            keep_running, next_state = self.next_state(line)
            for msg in self._msgs:
                yield(msg)
            if not keep_running or next_state is None:
                break
            if False and self.next_state != next_state:
                self._msgs.append("**** ==> state %r" % next_state)
            self.next_state = next_state
    
    def init(self):
        self.curr_line = None

    def run(self, env=None):
        if not self._cmd:
            # Report a failed test run in terms that sleuth will parse
            yield "@suite_started@: failed attempt to run tests"
            yield "@fault@:"
            yield "No command-line specified, and no Makefile found in directory"
            yield self._cwd
            yield "@suite_finished@:"
            raise StopIteration

        # Set the PERL5LIB value instead of writing a list
        # of -I args because we might be invoking a make command
        # instead of a perl command
        if env is None:
            env = self._get_non_komodo_env()
        sleuth.fixLanguageIncludePath(env, "perlExtraPaths", "PERL5LIB")
        flags, shell = self._flags_shell_from_launch_conditions()
        log.debug("#QQQ: koRunPerlTests.py: running cmd %s, dir %s",
                  self._cmd, self._cwd)
        self.p, msgs = self._launch_process(shell, flags, env)
        if self.p is None:
            for line in msgs:
                yield line
            raise StopIteration
        self.need_new_result_set = True
        self.init()
        self.pre_state_before_suite()
        self.next_state = self.state_before_suite
        # Try working with this
        try:
            for line in self.run_state_machine():
                yield line
        except StopIteration:
            pass
        self.p.wait()

#---- internal support stuff

def _find_nmake_exe():
    if haveWhich:
        try:
            return which.which("nmake")
        except which.WhichError:
            pass
    return _find_nmake_in_registry()

def _find_nmake_in_registry():
    """Use well-known registry key names for versions 6, 7, and 8 of
    Visual Studio to determine where nmake.exe is located.
    
    The pattern on registry access used here is:
    
    childKey = _winreg.openKey(parentKey, string)
    try:
        use key childKey
    except EnvironmentError:
        pass # If the tryBlock does a _winreg.OpenKey(childKey, string)
    finally:
        _winreg.closeKey(childKey)
        
    It's a little different for cKey, because that might not be set.
    
    Permanent TODO: The list of supported versions in this docstring
    should be updated when each new version of VS is released.
    """
    import _winreg
    try:
        vskey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                                r"SOFTWARE\Microsoft\VisualStudio")
        try:
            subkeyNames = []
            # Standard usage for enumerating a key is to try up to 1000 times.
            # See recipe 7.7 in Python Cookbook 1st ed.
            for vskey_count in range(1000):
                try:
                    subkeyNames.append(_winreg.EnumKey(vskey, vskey_count))
                except EnvironmentError:
                    break
            subkeyNames.sort(reverse=True) # Look at more recent first
            for sk in subkeyNames:
                subkey = _winreg.OpenKey(vskey, sk)
                try:
                    setupKey = _winreg.OpenKey(subkey, "Setup")
                    try:
                        try:
                            cKey = _winreg.OpenKey(setupKey, "VC")
                        except EnvironmentError:
                            try:
                                # VC++ 6 name
                                cKey = _winreg.OpenKey(setupKey, "Microsoft Visual C++")
                            except EnvironmentError:
                                continue
                        try:
                            productDir = _winreg.QueryValueEx(cKey, "ProductDir")[0]
                        except EnvironmentError:
                            # unlikely -- if we're at VS/x/Setup/VC|MSVC++, there's probably a ProductDir
                            continue
                        finally:
                            _winreg.CloseKey(cKey)
                        nmakePath = os.path.join(productDir, "bin", "nmake.exe")
                        if os.path.exists(nmakePath):
                            if _simple_path_re.match(nmakePath):
                                return nmakePath
                            else:
                                return nmakePath
                    finally:
                        _winreg.CloseKey(setupKey)
                except EnvironmentError:
                    # possible that $subkey/Setup doesn't exist
                    pass    
                finally:
                    _winreg.CloseKey(subkey)
        finally:
            _winreg.CloseKey(vskey)
    except EnvironmentError:
        # unlikely -- we're on a machine that has no VisualStudio installation
        pass

class Perl_TAP_SleuthHarness(sleuth.KoSleuthHarnessRunner):
    def initialize(self, args, launch_dir=None, executable=None):
        self._cwd = launch_dir or os.path.abspath(os.path.basename(__file__))
        self._args = args
        self._harness = KoHarnessPerlTests(self._cwd, args)
        if executable:
            self._harness.set_perl(executable)
        else:
            self._harness.set_perl(which.which('perl') or "perl")
        self._initial_msgs = self._harness.final_initialize()
        # Walk over these in the run() routine,
        # where something's consuming output
            
    def generate_boilerplate(self, filename, buffer):
        pass

harness_name          = "Perl - TAP (*.t)"
compatible_with_v_4_3 = True
            
def register(sleuthManager):
    sleuthManager.register('Perl', harness_name, Perl_TAP_SleuthHarness,
                           compatible_with_v_4_3)

#---- mainline

def main(argv):
    perl = None
    usage =  "usage: " + argv[0] + "[ -x|--executable=interpreter-path] [cwd [command args...]]"
    import getopt
    optlist, args = getopt.getopt(sys.argv[1:], 'hx:', ['help', 'executable='])
    for opt, optarg in optlist:
        if opt in ('-x', '--executable'):
            perl = optarg
        elif opt in ('-h', '--help'):
            sys.stderr.write(usage + "\n")
            return 0
    if len(args) == 0:
        cwd = os.getcwd()
        cmd = None
    else:
        cwd = args[0]
        os.chdir(cwd)
        if len(args) == 1:
            cmd = None
        else:
            cmd = args[1:]
    harness = Perl_TAP_SleuthHarness()
    harness.initialize(args, cwd, perl)
    for line in harness.run():
        print line
    
if __name__ == "__main__":
    sys.exit(main(sys.argv))
