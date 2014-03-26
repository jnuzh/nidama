#!python
# Copyright (c) 2007 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

"""Invoke a suite of PHP tests, and parse the results.
"""

import sys, os
import logging
import sleuth

import which

log = logging.getLogger("sleuth.php.phpunit")
#log.setLevel(logging.DEBUG)

class KoHarnessPHPTests(sleuth.KoSleuthHarness):
    pass
            
class PHP_PHPUnit_SleuthHarness(sleuth.KoSleuthHarnessRunner):
    def initialize(self, user_args, launch_dir=None, executable=None):
        test_dir = os.path.abspath(os.path.dirname(__file__))
        launch_dir = launch_dir or test_dir
        php_harness_file = os.path.join(test_dir, 'drive_testrunner.php')
        if executable is None:
            try:
                executable = which.which("php")
            except which.WhichError:
                pass
            if executable is None:
                executable = "php"
        if os.path.exists(php_harness_file):
            extra_paths = sleuth.get_extra_paths("phpExtraPaths")
            if extra_paths:
                args = [executable,
                        '-d', "include_path='%s'" % os.path.pathsep.join(extra_paths),
                        php_harness_file, launch_dir]
            else:
                args = [executable, php_harness_file, launch_dir]
            args += user_args
        else:
            args = user_args
        if args:
            # print "Running cmd [%s] in dir %s" % (args, test_dir)
            self._harness = KoHarnessPHPTests(args, launch_dir)
        else:
            self._initial_msgs = [
            # Report a failed test run in terms that sleuth will parse
                "@suite_started@: failed attempt to run tests",
                "@fault@: No command-line specified, and no Komodo/PHP test runner ",
                "@fault@: (drive_testrunner.php) found in directory " + test_dir,
                "@suite_finished@:",
            ]
            
    def generate_boilerplate(self, filename, buffer):
        pass

harness_name = "PHP - PHPUnit"
compatible_with_v_4_3 = True
            
def register(sleuthManager):
    sleuthManager.register('PHP', harness_name, PHP_PHPUnit_SleuthHarness,
                           compatible_with_v_4_3)

if __name__ == "__main__":
    executable = None
    usage =  "usage: " + sys.argv[0] + "[ -x|--executable=interpreter-path] [cwd [command args...]]"
    import getopt
    optlist, args = getopt.getopt(sys.argv[1:], 'hx:', ['help', 'executable='])
    for opt, optarg in optlist:
        if opt in ('-x', '--executable'):
            executable = optarg
        elif opt in ('-h', '--help'):
            sys.stderr.write(usage + "\n")
            sys.exit()
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
    main(cwd, cmd, executable)
