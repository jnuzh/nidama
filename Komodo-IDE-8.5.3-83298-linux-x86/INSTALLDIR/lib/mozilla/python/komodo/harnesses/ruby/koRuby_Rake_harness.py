#!python
# Copyright (c) 2007 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

"""Invoke a suite of Ruby tests, and parse the results.
"""

import re, sys, os
from os.path import abspath, dirname, exists, join
import logging
import sleuth

log = logging.getLogger("sleuth.ruby.rake")
#log.setLevel(logging.DEBUG)

class KoHarnessRubyTests(sleuth.KoSleuthHarness):
    def __init__(self, cmd="rake", cwd=None):
        sleuth.KoSleuthHarness.__init__(self, cmd, cwd)
        self._target_cwd = self._cwd.lower()
        if sys.platform == "win32":
            self._target_cwd = self._target_cwd.replace("\\", "/")
        self._internal_stack_trace_re = re.compile(r'harnesses[\\/]ruby[\\/]load_komodo_runner\.rb\s*:\s*\d+\s*:\s*in')
            
    def filter_line(self, line, line_num):
        if (line_num == 1
            and (line.strip().lower().replace("\\", "/") ==
                 "(in " + self._target_cwd + ")")):
                return True
        elif self._internal_stack_trace_re.search(line):
            return True
        
class Ruby_RakeTests_SleuthHarness(sleuth.KoSleuthHarnessRunner):
    def initialize(self, cmd, launch_dir=None, executable=None):
        """ Most of the time tests will be run with rake, but
        the user will need to supply an argument.  Analyze the
        supplied command, and if it is a rake command, modify it
        so it loads the Komodo test runner.
        @param {cmd} array of strings
        @param {launch_dir} string: directory to run tests from
        @param {exectable} string: path to program to run
        """
        rakefile = None
        if executable and os.path.isabs(executable):
            ruby_path = str(executable)
        else:
            ruby_path = str(self.lookupOutsideKoPath('ruby'))
        ruby_dir = dirname(ruby_path)
        if sys.platform == "win32":
            # Here's the problem: rake spawns a new ruby process
            # On Windows, if we launch a *rake* process (which is basically
            # a rake.cmd script that calls ruby <ruby-path>/rake), we fail
            # to spawn the inner ruby call.  If we're running the Ruby interpreter,
            # no problem.  I have no idea why.  Not a problem on Unix.
            rake_path_parts = [ruby_path, join(ruby_dir, 'rake')]
        else:
            rake_path_parts = [str(self.lookupOutsideKoPath('rake'))]
        if not exists(rake_path_parts[-1]):
            self._initial_msgs = [
            # Report a failed test run in terms that sleuth will parse
                "@suite_started@: failed attempt to run tests",
                "@fault@: No main rake script (%s) found in directory (%s)" %(
                      rake_path_parts[-1],
                      ruby_dir),
                "@suite_finished@:",
            ]
            return
        rake_args = []
        test_dir = abspath(dirname(__file__))
        launch_dir = launch_dir or test_dir
        if cmd and cmd[0].lower() == "rake":
            # They specified a complete command-line, so work with it.
            rake_args = cmd[1:]
            cmd = None
        if not cmd:
            if exists(join(launch_dir, "Rakefile")):
                rakefile = join(launch_dir, "Rakefile")
            elif not sys.platform.startswith("win") and exists(join(launch_dir, "rakefile")):
                rakefile = join(launch_dir, "rakefile")
            else:
                log.debug("Couldn't find Rakefile in launch_dir=%s", launch_dir)
            extra_paths = sleuth.get_extra_paths("rubyExtraPaths")
            path_args = []
            for incpath in extra_paths:
                path_args += ['--libdir=' + incpath]
            if rakefile is not None:
                cmd = rake_path_parts + path_args + [
                       '--libdir=' + test_dir,
                       '--require=add_rake_runner',
                       '-f',
                       rakefile,
                       'TESTOPTS=--runner=komodo -v']
                if rake_args:
                    cmd += rake_args
                #log.debug("Command is now: %s" % cmd)
                    
        if not cmd:
            cmd = rake_path_parts + rake_args
        
        if cmd:
            self._harness =  KoHarnessRubyTests(cmd, launch_dir)
        else:
            self._initial_msgs = [
            # Report a failed test run in terms that sleuth will parse
                "@suite_started@: failed attempt to run tests",
                "@fault@: No command-line specified, and no Rakefile found in ",
                "@fault@: directory " + launch_dir,
                "@suite_finished@:",
            ]
            
    def generate_boilerplate(self, filename, buffer):
        pass

harness_name = "Ruby - Rake tests"
compatible_with_v_4_3 = True

def register(sleuthManager):
    sleuthManager.register('Ruby', harness_name, Ruby_RakeTests_SleuthHarness,
                           compatible_with_v_4_3)
