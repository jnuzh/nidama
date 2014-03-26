#!python
# Copyright (c) 2007 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

""" Thin wrapper around koPythonUnittestSimple.py tests, 
    used only to run the test suite out of process.
"""

import sys, os
import logging
import sleuth

log = logging.getLogger("sleuth.python.unittest")
#log.setLevel(logging.DEBUG)

class KoHarnessPythonTests(sleuth.KoSleuthHarness):
    def run(self, env=None):
        if env is None:
            env = self._get_non_komodo_env()
        sleuth.fixLanguageIncludePath(env, "pythonExtraPaths", "PYTHONPATH")
        return sleuth.KoSleuthHarness.run(self, env)

class Python_Unittest_SleuthHarness(sleuth.KoSleuthHarnessRunner):
    def initialize(self, cmd, launch_dir=None, executable=None):
        test_dir = os.path.abspath(os.path.dirname(__file__))
        launch_dir = launch_dir or test_dir
        python_exe = executable or "python" # Not which.which!
        harness_file = os.path.join(test_dir, 'koPythonUnittestSimple.py')
        if not cmd:
            if os.path.exists(harness_file):
                cmd = [python_exe, harness_file, launch_dir]
            else:
                log.debug("No cmd, Can't find harness_file=%s", harness_file)
        else:
            cmd = [python_exe, harness_file] + cmd
        if cmd:
            log.debug("Running cmd [%s] in dir %s", cmd, test_dir)
            self._harness = KoHarnessPythonTests(cmd, launch_dir)
        else:
            self._initial_msgs = [
            # Report a failed test run in terms that sleuth will parse
                "@suite_started@: failed attempt to run tests",
                "@fault@: No command-line specified, and no Komodo/Python test runner ",
                "@fault@: (koPythonUnittestSimple.py) found in directory " + test_dir,
                "@suite_finished@:",
            ]
            
    def generate_boilerplate(self, filename, buffer):
        pass
          
harness_name = "Python - unittest"
compatible_with_v_4_3 = True

def register(sleuthManager):
    sleuthManager.register('Python', harness_name, Python_Unittest_SleuthHarness,
                           compatible_with_v_4_3)
