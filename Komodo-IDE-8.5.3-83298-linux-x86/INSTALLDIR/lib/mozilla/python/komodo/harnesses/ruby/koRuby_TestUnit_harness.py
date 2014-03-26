#!python
# Copyright (c) 2007 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

"""Invoke a suite of Ruby tests, and parse the results.
"""

import re, sys, os
from os.path import abspath, dirname, exists, join
import logging
import sleuth

log = logging.getLogger("sleuth.ruby.pure")
#log.setLevel(logging.DEBUG)

class KoHarnessRubyTests(sleuth.KoSleuthHarness):
    def __init__(self, cmd, cwd):
        sleuth.KoSleuthHarness.__init__(self, cmd, cwd)
        self._internal_stack_trace_re = re.compile(r'harnesses[\\/]ruby[\\/]load_komodo_runner\.rb\s*:\s*\d+\s*:\s*in')
            
    def filter_line(self, line, line_num):
        if self._internal_stack_trace_re.search(line):
            return True
        
class Ruby_TestUnit_SleuthHarness(sleuth.KoSleuthHarnessRunner):
    def initialize(self, cmd, launch_dir=None, executable=None):
        """ This test plan runs Ruby tests outside rake
        @param {cmd} array of strings
        @param {launch_dir} string: directory to run tests from
        @param {exectable} string: path to program to run
        """
        if not cmd or len(cmd) != 1:
            self._initial_msgs = [
            # Report a failed test run in terms that sleuth will parse
                "@suite_started@: failed attempt to run tests",
                "@fault@: The Ruby Test::Unit test plan requires a single filename in the command-line arguments",
                "@fault@: got " + ((cmd and " ".join(cmd)) or "no arguments"),
                "@suite_finished@:",
            ]
            return
        ruby_path = executable or str(self.lookupOutsideKoPath('ruby'))
        if not ruby_path:
            self._initial_msgs = [
            # Report a failed test run in terms that sleuth will parse
                "@suite_started@: failed attempt to run tests",
                "@fault@: No Ruby interpreter specified.",
                "@suite_finished@:",
            ]
            return
        test_dir = abspath(dirname(__file__))
        launch_dir = launch_dir or test_dir
        extra_paths = sleuth.get_extra_paths("rubyExtraPaths")
        path_args = []
        for incpath in extra_paths:
            path_args += ['-I', incpath]
        cmd = [ruby_path] + path_args + ['-I', test_dir,
               '-r',
               'load_komodo_runner'] + cmd + ['--runner=komodo']
        self._harness =  KoHarnessRubyTests(cmd, launch_dir)
            
    def generate_boilerplate(self, filename, buffer):
        pass

harness_name = "Ruby - Test::Unit"
compatible_with_v_4_3 = False

def register(sleuthManager):
    sleuthManager.register('Ruby', harness_name, Ruby_TestUnit_SleuthHarness,
                           compatible_with_v_4_3)
