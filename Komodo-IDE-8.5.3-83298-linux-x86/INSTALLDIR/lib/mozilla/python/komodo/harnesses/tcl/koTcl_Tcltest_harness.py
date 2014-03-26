#!python

"""
Tcl test harness for tcltest library.

This module is similar to the Perl TAP harness.  It runs and parses
the output from a tcltest run, pushing arguments into
TCLTEST_OPTIONS:

"""

#!python

import os
from os.path import abspath, join, exists, dirname, isdir
import sys
import logging
import re
from pprint import pprint
import subprocess
import sleuth

log = logging.getLogger("sleuth.tcl.tcltest")
#log.setLevel(logging.DEBUG)

""" Patterns, and what we're looking for:

Put all patterns here once we know what we're looking for.
"""

_re_end_suite = re.compile(r'^[^\s]+:\s+Total\s+(\d+)\s*Passed\s+(\d+)\s*Skipped\s+(\d+)\s*Failed\s+(\d+)')
_re_test_failed = re.compile(r'^={4} .*\s+FAILED')
_re_test_final_failed = _re_test_failed  # For now this works
_re_test_passed = re.compile(r'^\+\+\+\+ .*PASSED')
_re_test_start = re.compile(r'^----\s*(.*)\s*$')

class KoHarnessTclTests(sleuth.KoSleuthHarness):
    def __init__(self, cwd, cmd=None):
        self._cwd = cwd
        self._cmd = cmd

    def run(self):
        if not self._cmd:
            # Report a failed test run in terms that sleuth will parse
            yield "@suite_started@: failed attempt to run tests"
            yield "@fault@:"
            yield "No command-line specified, no point running in directory: "
            yield self._cwd
            yield "@suite_finished@:"
            raise StopIteration
        flags, shell = self._flags_shell_from_launch_conditions()
        log.debug("#QQQ: koTcl_Tcltest_harness.py: running cmd %s, dir %s",
                  self._cmd, self._cwd)
        env = self._get_non_komodo_env()
        sleuth.fixLanguageIncludePath(env, "tclExtraPaths", "TCLLIBPATH",
                                      sepChar=" ")
        env["TCLTEST_OPTIONS"] = "-verbose pstel"
        self.p, msgs = self._launch_process(shell, flags, env)
        if self.p is None:
            for line in msgs:
                yield line
                raise StopIteration
        try:
            yield "@suite_started@:"
            yield "@info@:"
            self._pre_state_before_suite()
            for line in self.run_state_machine():
                yield line
        except StopIteration:
            yield "@suite_finished@:"
            pass
        self.p.wait()

    def _pre_state_before_suite(self):
        self.line = None
        self.next_state = self._state_before_suite

    # State Actions: common things to do before transitioning
    def _do_start_test(self, test_name):
        self._msgs.append("@test_started@: %s" % test_name)
        return True, self._state_in_test

    def _do_finish_test(self, status):
        self._msgs.append("@test_result@: %s" % status)
        return True, self._state_before_test

    def _do_finish_suite(self, m):
        self._msgs.append("@suite_finished@: N:%d, P:%d, F:%d, S:%d;\n" % (
            int(m.group(1)),
            int(m.group(2)),
            int(m.group(3)),
            int(m.group(4))))
        return False, None

    def _do_find_failure(self, line):
        self._msgs.append("@fault@:")
        self._msgs.append(line)
        return True, self._wait_for_failure_end

    # State Input Handlers: Transition to other states,
    # or same, depending on input

    def _state_before_suite(self, line):
        self._msgs.append("@suite_started@:")
        m = _re_test_start.match(line)
        if m:
            return self._do_start_test(m.group(1))
        m = _re_end_suite.match(line)
        if m:
            return self._do_finish_suite(m)
        self._msgs.append("@info@:")
        self._msgs.append(line)
        return True, self._info_before_test

    def _info_before_test(self, line):
        if not line.strip():
            return True, self._info_before_test
        m = _re_test_start.match(line)
        if m:
            return self._do_start_test(m.group(1))
        m = _re_end_suite.match(line)
        if m:
            return self._do_finish_suite(m)
        self._msgs.append(line)
        return True, self._info_before_test

    def _state_before_test(self, line):
        if not line.strip():
            return True, self._info_before_test
        m = _re_test_start.match(line)
        if m:
            return self._do_start_test(m.group(1))
        m = _re_end_suite.match(line)
        if m:
            return self._do_finish_suite(m)
        self._msgs.append("@info@:")
        self._msgs.append(line)
        return True, self._info_before_test

    def _state_in_test(self, line):
        m = _re_test_passed.match(line)
        if m:
            return self._do_finish_test("P")
        m = _re_test_failed.match(line)
        if m:
            # First part of failure
            return self._do_find_failure(line)
        self._msgs.append("@info@:")
        self._msgs.append(line)
        return True, self._in_test_in_block
        
    def _in_test_in_block(self, line):
        m = _re_test_passed.match(line)
        if m:
            return self._do_finish_test("P")
        m = _re_test_failed.match(line)
        if m:
            # First part of failure
            return self._do_find_failure(line)
        # Continue the info block
        self._msgs.append(line)
        return True, self._in_test_in_block

    def _wait_for_failure_end(self, line):
        m = _re_test_final_failed.match(line)
        if m:
            return self._do_finish_test("F")
        # Continue the fault block
        self._msgs.append(line)
        return True, self._wait_for_failure_end            
        

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
            if self.next_state != next_state:
                log.debug("**** ==> state %r", next_state)
            self.next_state = next_state

#---- internal support stuff

class Tcl_Tcltest_SleuthHarness(sleuth.KoSleuthHarnessRunner):
    def initialize(self, cmd, launch_dir=None, executable=None):
        if not cmd or len(cmd) != 1:
            self._initial_msgs = [
            # Report a failed test run in terms that sleuth will parse
                "@suite_started@: failed attempt to run tests",
                "@fault@: The Tcltest harness requires a single filename in the command-line arguments",
                "@fault@: got " + ((cmd and " ".join(cmd)) or "no arguments"),
                "@suite_finished@:",
            ]
            return
        tcl_path = executable or str(self.lookupOutsideKoPath('tclsh'))
        if not tcl_path:
            self._initial_msgs = [
            # Report a failed test run in terms that sleuth will parse
                "@suite_started@: failed attempt to run tests",
                "@fault@: No Tcl interpreter specified.",
                "@suite_finished@:",
            ]
            return
        test_dir = abspath(dirname(__file__))
        launch_dir = launch_dir or test_dir
        cmd = [tcl_path] + cmd
        self._harness = KoHarnessTclTests(launch_dir, cmd)
        
    def generate_boilerplate(self, filename, buffer):
        pass

harness_name          = "Tcl - Tcltest"
compatible_with_v_4_3 = False
            
def register(sleuthManager):
    sleuthManager.register('Tcl', harness_name, Tcl_Tcltest_SleuthHarness,
                           compatible_with_v_4_3)
