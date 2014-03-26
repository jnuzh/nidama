#!python
# Copyright (c) 2000-2008 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

# The implementation of the Komodo Sleuth service

import os
from os.path import join, isabs, expanduser, normpath, abspath, dirname, splitext
import sys
import string, types
import re
import logging
import threading
import pprint
import which

from xpcom import components

import sleuth



#---- globals

log = logging.getLogger("koSleuth")
#log.setLevel(logging.DEBUG)



#---- Sleuth backend

class _SleuthRunner(threading.Thread):
    """Launch a unittest run based on the provided directory, language,
    and, optionally, command-line.  Feed results into the koISleuthResultsTreeView
    object.
    
    The running thread can be terminated early by calling the .stop() method.

    """
    
    def __init__(self, harness, cwd, language, commandLine, resultsMgr, resultsView):
        threading.Thread.__init__(self, name="SleuthRunner")

        self.harness = harness
        self.cwd = cwd
        self.language = language
        self.commandLine = commandLine

        class ResultsManagerProxy:
            def __init__(self, obj):
                self.obj = obj
            @components.ProxyToMainThread
            def runFinished(self, *args):
                return self.obj.runFinished(*args)
            @components.ProxyToMainThread
            def highlightLine(self, *args):
                return self.obj.highlightLine(*args)
            @components.ProxyToMainThread
            def updateResults(self, *args):
                return self.obj.updateResults(*args)
        self.resultsMgrProxy = ResultsManagerProxy(resultsMgr)

        class ResultsViewProxy:
            def __init__(self, obj):
                self.obj = obj
            @components.ProxyToMainThread
            def AddDetails(self, *args):
                return self.obj.AddDetails(*args)
            @components.ProxyToMainThread
            def UpdateTree(self, *args):
                return self.obj.UpdateTree(*args)
        self.resultsViewProxy = ResultsViewProxy(resultsView)
        
        self.lastErrorSvc = components.classes["@activestate.com/koLastErrorService;1"]\
                      .getService(components.interfaces.koILastErrorService)

        self._is_running = False # because we allow only one testrun at a time
        self._event_dispatch_table = {
            sleuth.SuiteStartEvent : self._handleSuiteStartEvent,
            sleuth.SuiteFinishedEvent : self._handleSuiteFinishedEvent,
            sleuth.TestEvent : self._handleTestEvent,
            sleuth.TestFaultEvent : self._handleTestFaultEvent,
            sleuth.TestFinishedEvent : self._handleTestFinishedEvent,
            sleuth.TestInfoEvent : self._handleTestInfoEvent,
            sleuth.TestStartEvent : self._handleTestStartEvent,
        }
        self._inSuite = False
        self._cachedData = []
        self._currentDataItem = None
        self._cachedDataThreshold = 1
        self._firstInterestingItem = -1
        self._notifiedInterestingItem = False
        self._numItemsSent = 0

    def stop(self):
        """Stop processing."""
        log.info("stopping test_plan thread")
        try:
            self.test_plan.stop()
        except AttributeError:
            pass
            
    def run(self):
        try:
            #self.resultsMgrProxy.runStarted()
            return self._run_in_ui_mode()
        finally:
            self.resultsMgrProxy.runFinished()
        
    def _run_in_ui_mode(self):
        log.debug("start sleuth thread")
        self._num_tests = self._num_passes = self._num_errors = self._num_failures = 0

        self.test_plan = sleuth.TestPlan(self.harness, self.cwd, self.language,
                                         self.commandLine)
        log.debug("In koSleuth.run, self.cwd=%s, self.language=%s, self.commandLine=[%s]",
                  self.cwd, self.language, self.commandLine)
        try:
            for event in self.test_plan.run_tests():
                log.debug("Got event %r", event)
                (self._event_dispatch_table.get(
                    event.__class__, self._handleUnknownEvent))(event)
        except StopIteration:
            log.debug("Done running test suite")
            self._relayDataIfReady(True)
        
    def _handleUnknownEvent(self, event):
        log.debug("Got unknown event %r", event)
        
    def _handleCurrentDataItem(self, force_relay=False):
        if self._currentDataItem:
            if self._firstInterestingItem == -1 and self._currentDataItem[2]:
                self._firstInterestingItem = len(self._cachedData)
            self._cachedData.append(self._currentDataItem)
            self._relayDataIfReady(force_relay)
        self._currentDataItem = None            

    def _relayDataIfReady(self, force_relay):
        if force_relay or len(self._cachedData) >= self._cachedDataThreshold:
            # Send each row to the tree view object
            # one at a time.
            for item in self._cachedData:
                log.debug("About to addDetails: %s",
                          ", ".join([repr(x) for x in item]))
                self.resultsViewProxy.AddDetails(item[0], item[1], "\n".join(item[2]))
            self.resultsViewProxy.UpdateTree()
            if self._firstInterestingItem > -1 and not self._notifiedInterestingItem:
                self._notifiedInterestingItem = True
                self.resultsMgrProxy.highlightLine(self._numItemsSent + self._firstInterestingItem)
                
            self._numItemsSent += len(self._cachedData)
            self._cachedData = []
        
    def _handleSuiteStartEvent(self, event):
        if event.data:
            self._handleCurrentDataItem()
            self._currentDataItem = ["Information", "", [event.data]]
        self._inSuite = True

    def _handleSuiteFinishedEvent(self, event):
        if not self._inSuite:
            return
        status_string = event.get_status_string()
        log.debug("_handleSuiteFinishedEvent: status=%r, time=%r",
                  status_string, event.elapsed_time)
        self._handleCurrentDataItem(True)
        # And have the UI display part
        vals = event.get_status_values()
        self._num_tests += vals[0]
        self._num_passes += vals[1]
        self._num_errors += vals[2]
        self._num_failures += vals[3]
        elapsed_time = event.elapsed_time
        if elapsed_time:
            elapsed_time = re.sub(r'^\s*T:\s*', '', elapsed_time)
        self.resultsMgrProxy.updateResults(self._num_passes,
                                           self._num_errors,
                                           self._num_failures,
                                           elapsed_time)
        self._inSuite = False
        
        
    def _handleTestFaultEvent(self, event):
        if event.info:
            if self._currentDataItem:
                self._currentDataItem[2] += event.info
            else:
                self._currentDataItem = ["Information", "", event.info]

    def _handleTestFinishedEvent(self, event):
        self._currentDataItem[1] = event.outcome
        self._handleCurrentDataItem()

    def _handleTestStartEvent(self, event):
        self._handleCurrentDataItem()
        self._currentDataItem = [event.name, "", []]
    
    def _handleTestInfoEvent(self, event):
        if event.info:
            if self._currentDataItem:
                self._currentDataItem[2] += event.info
            else:
                self._currentDataItem = ["Information", "", event.info]
        
    def _handleTestEvent(self, event):
        # Shouldn't happen
        log.debug("**** What do I do with a %r", event)
        if self._currentDataItem:
            self._currentDataItem[2] += event.info

class KoSleuthService:
    _com_interfaces_ = components.interfaces.koISleuthService
    _reg_desc_  = "Sleuth UnitTest Service"
    _reg_clsid_ = "{ca5ccaff-35d7-4785-9ee3-a98055b59659}"
    _reg_contractid_ = "@activestate.com/koSleuthService;1"

    def __init__(self):
        global lastErrorSvc
        lastErrorSvc = components.classes["@activestate.com/koLastErrorService;1"]\
                       .getService(components.interfaces.koILastErrorService)
        self._sleuthThread = None
        self._harnessManager = KoSleuthHarnessManager()
        self._harnessManager.initialize()
        
    def get_harness_names(self):
        return self._harnessManager.get_harness_names()
    
    def language_from_harness(self, harness_name):
        return self._harnessManager.language_from_harness(harness_name)
    
    def is_v43_compatible(self, harness_name):
        return self._harnessManager.is_v43_compatible(harness_name)
       
    def run_sleuth_tests(self, cwd, harnessName, commandLine,
                         resultsMgr, resultsView):
        """
        Run Sleuth unit-tests, grab results, feed into the given koISleuthResultsView.

            "cwd" : [string] directory to run tests in
            "language" : [string]
            "commandLine" : [string] optional command to run, instead of defaults
            "resultsMgr" is a koISleuthResultsTab instance.
            "resultsView" is a koISleuthResultsView instance
        
        This process is done asynchronously -- i.e. a separate thread is
        started to do this.
        
        No return value.
        """
        log.debug("run_sleuth_tests(cwd='%s', harnessName=%s, commandLine=%r)",
                 cwd, harnessName, commandLine)
        harnessObj = self._harnessManager.get_harness(harnessName)
        if harnessObj is None:
            log.error("Can't resolve harness name %s", harnessName)
            return
        # harnessObj: instance of KoSleuthHarnessItem
        language = harnessObj.language_name
        harness = harnessObj.get_classInstance()
        
        self._sleuthThread = _SleuthRunner(harness, cwd, language, commandLine,
                                           resultsMgr, resultsView)
        resultsMgr.runStarted()
        self._sleuthThread.start()

    def stop_sleuth_tests(self):
        #XXX Do I need a lock-guard around usage of self._sleuthThread?
        if self._sleuthThread:
            self._sleuthThread.stop()
            self._sleuthThread = None
            
    def thread_ended(self):
        """
        When the UI gets a test-run-finished event, it can update the back-end
        """
        #XXX Grab mutex
        try:
            if self._sleuthThread:
                self._sleuthThread = None
        finally:
            #XXX Release mutex
            pass

    def get_TESTPLAN_PREFNAME(self):
        return "testPlans"

    def get_LAST_TESTPLAN_PREFNAME(self):
        return "lastTestPlanName"

    def get_LAST_TESTPLAN_PROJECT_URL(self):
        return "lastTestPlanProjectURL"

class KoSleuthHarnessItem(object):
    def __init__(self, language_name, class_ref, is_compatible_with_v_4_3):
        self.language_name = language_name
        self._class_ref = class_ref
        self.is_compatible_with_v_4_3 = is_compatible_with_v_4_3
        
    def get_classInstance(self):
        return self._class_ref() # Instantiate each time
        
import directoryServiceUtils
from glob import glob
import imp

class KoSleuthHarnessManager(object):
    def __init__(self):
        self.harness_registry = {} # Map harness name to KoSleuthHarnessItem
        self._compatible_v43_harnesses_by_lang = {}
    
    def initialize(self):
        self.load_harnesses()
        
    def get_harness_names(self):
        return self.harness_registry.keys()
        
    def get_harness(self, harness_name):
        # Allow harnessName to be either a full harness name, or the
        # name of a language for 4.3 compatibility
        #XXX Mark standard test suites for 4.3-compatibility
        harness_names = self.get_harness_names()
        if harness_name in harness_names:
            return self.harness_registry[harness_name]
        language_name_lc = harness_name.lower()
        for name in harness_names:
            if name.lower().startswith(language_name_lc):
                return self.harness_registry[name]
        return None

    def language_from_harness(self, harness_name):
        try:
            return self.get_harness(harness_name).language_name
        except:
            log.exception("language_from_harness: failed")
            return ""
    
    def is_v43_compatible(self, harness_name):
        """
        Harnesses that shipped with version 4.3 of Komodo, and
        have been modified to work with the v 4.4 advertise themselves
        as such.
        
        Third-party harnesses *can* do this, but the results will be
        undefined.  Specifically, test plans that used to work with
        version 4.3 might fail.
        """
        try:
            return self.get_harness(harness_name).is_compatible_with_v_4_3
        except:
            log.exception("is_v43_compatible: failed")
            return False
        
    def load_harnesses(self):
        """
        Komodo ships standard harnesses in <python Lib>/harnesses
        Each extension can define one or more harnesses in subdirs of
        <extdir>/harnesses
        """
        ko_python_lib_dir = os.path.join((components.classes["@activestate.com/koDirs;1"].
                                          getService(components.interfaces.koIDirs).
                                          mozBinDir),
                                          "python", "komodo")
        main_dirs = {}
        komodo_harness_dir = os.path.join(ko_python_lib_dir, 'harnesses')
        if os.path.exists(komodo_harness_dir) and os.path.isdir(komodo_harness_dir):
            main_dirs[""] = komodo_harness_dir
        for ext_dir in directoryServiceUtils.getExtensionDirectories():
            verb = 'nose' in ext_dir.lower()
            if verb: log.debug("... look at dir %s", ext_dir)
            ext_harness_dir = join(ext_dir, 'sleuth-harnesses')
            if os.path.exists(ext_harness_dir) and os.path.isdir(ext_harness_dir):
                if verb: log.debug("%s exists", ext_harness_dir)
                bname = os.path.basename(ext_dir)
                main_dirs[bname] = ext_harness_dir
            else:
                if verb: log.debug("%s not exists", ext_harness_dir)
                pass
        for bname, dir in main_dirs.items():
            try:
                for child in os.listdir(dir):
                    if os.path.isdir(join(dir, child)):
                        for module_path in glob(join(dir, child, '*_harness.py')):
                            self.load_harness(bname, module_path)
            except OSError, ex:
                log.error(ex)
    
    def load_harness(self, bname, module_path):
        # Code taken from codeintel2/manager.py.register_lang
        module_dir, module_name = os.path.split(module_path)
        module_name = splitext(module_name)[0]
        iinfo = imp.find_module(module_name, [module_dir])
        try:
            module = imp.load_module(module_name, *iinfo)
        except (ImportError, SyntaxError):
            log.exception("Error loading module %s (%s : %s)",
                          module_path, module_dir, module_name)
            module = None
        if hasattr(module, "register"):
            log.debug("register %s test harness", module_path)
            try:
                module.register(self)
            except:
                log.exception("Error registering %s (%s : %s)",
                              module_path, module_dir, module_name)
                
    def register(self, language_name, harness_name, class_ref, compatible_with_v_4_3=False):
        self.harness_registry[harness_name] = KoSleuthHarnessItem(language_name, class_ref, compatible_with_v_4_3)
        if compatible_with_v_4_3:
            self._compatible_v43_harnesses_by_lang[language_name] = harness_name
