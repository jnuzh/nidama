#!python
# Copyright (c) 2000-2008 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

"""
This test harness works only with Python test files that run tests with the
following pattern:

if __name__ == '__main__':
    unittest.main()
"""

import os
from os.path import join
import sys
import time
import unittest
from unittest import TestResult

class _KoTextTestResult(TestResult):
    def __init__(self, stream):
        TestResult.__init__(self)
        self.stream = stream
        
    def startTest(self, test):
        TestResult.startTest(self, test)
        self.stream.writeln("@test_started@: %s" % (str(test)))
                            
    def addSuccess(self, test):
        TestResult.addSuccess(self, test)
        self.stream.writeln("@test_result@: P")
        
    def addError(self, test, err):
        TestResult.addError(self, test, err)
        self._writeFault(test, err, "E")
        
    def addFailure(self, test, err):
        TestResult.addFailure(self, test, err)
        self._writeFault(test, err, "F")
        
    def _writeFault(self, test, err, type):
        self.stream.writeln("@fault@:")
        self.stream.writeln(self._exc_info_to_string(err, test))
        self.stream.writeln("@test_result@: " + type)
    
    def result_string(self):
        return "run=%i errors=%i failures=%i" % \
                    (self.testsRun, len(self.errors), len(self.failures))


class KoTextTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwds):
        unittest.TextTestRunner.__init__(self, stream=sys.stdout, *args, **kwds)
        
    def run(self, test):
        "Run the given test case or test suite."
        self.stream.writeln("@suite_started@:")
        result = _KoTextTestResult(self.stream)
        startTime = time.time()
        test(result)
        timeTaken = time.time() - startTime
        self.stream.writeln("@suite_finished@: %s; T: %.3f seconds" %
                            (result.result_string(), timeTaken))
        return result
    
class KoTestProgram(unittest.TestProgram):
    """
    Don't do everything the 'main' part of unittest.py does.
    """
    def __init__(self,
                 module='__main__',
                 defaultTest=None,
                 argv=None,
                 testRunner=None,
                 testLoader=unittest.defaultTestLoader):
        if type(module) == type(''):
            self.module = __import__(module)
            for part in module.split('.')[1:]:
                self.module = getattr(self.module, part)
        else:
            self.module = module
        self.verbosity = 1
        self.defaultTest = defaultTest
        self.testRunner = testRunner
        self.testLoader = testLoader
        self.progName = os.path.basename((argv or sys.argv)[0])
        self.parseArgs(argv[1:])
        self.runTests()

    def parseArgs(self, args):
        if len(args) == 0 and self.defaultTest is None:
            self.test = self.testLoader.loadTestsFromModule(self.module)
            return
        if len(args) > 0:
            self.testNames = args
        else:
            self.testNames = (self.defaultTest,)
        self.createTests()

    def createTests(self):
        self.test = self.testLoader.loadTestsFromNames(self.testNames,
                                                       self.module)

    def runTests(self):
        result = self.testRunner.run(self.test)


_usage = "Usage: [-h|--help] path..."

class KoTestWrapper:
    def __init__(self, testRunner):
        self.testRunner = testRunner
        sys.path.append(os.path.curdir)

    def test(self, args, walk_dirs=True, parent_dir=None):
        """ First time through, we're parsing command-line arguments,
        and walk_dirs will be True.
        On additional runs it will be False, so we should only
        accept files that start with "test_"
        """
        for arg in args:
            full_arg = (parent_dir is None and arg) or join(parent_dir, arg)
            if not os.path.exists(full_arg):
                print "@suite_started@:"
                print "@fault@:"
                print "File not found: %s" % (full_arg,)
                print "@suite_finished@:"
                continue
            if os.path.isfile(full_arg):
                root, ext = os.path.splitext(arg)
                if ext != ".py":
                    if walk_dirs:
                        print "@suite_started@:"
                        print "@fault@:"
                        print "File %s isn't a Python file" % (full_arg,)
                        print "@suite_finished@:"
                    continue
                elif not walk_dirs and not root.startswith("test_"):
                    print "#QQQ: Skipping file %s" % root
                    continue
                try:
                    module = __import__(root)
                    testProgram = KoTestProgram(module=module,
                                                argv=[sys.argv[0]],
                                                testRunner=self.testRunner)
                except:
                    import traceback
                    exc_info = sys.exc_info()
                    traceback.print_exception(*exc_info)
            elif walk_dirs:
                if os.path.isdir(arg):
                    sys.path.append(full_arg)
                    self.test(os.listdir(full_arg), False, full_arg)
                    sys.path.pop()
                    

def _main(argv):
    import getopt
    optlist, args = getopt.getopt(argv[1:], "h:", ["help"])
    for opt, optarg in optlist:
        if opt in ('-h', '--help'):
            print "No help yet."
            return
        else:
            print "%s: Option %s not recognized. %s" % (argv[0], opt, _usage)
            return
    if len(args) > 1 and os.path.isdir(args[0]):
        del args[0]
    if not args:
        print "No unittest modules given"
        print _usage
        return
    KoTestWrapper(KoTextTestRunner()).test(args)
    return True
    
if __name__ == "__main__":
    _main(sys.argv)
