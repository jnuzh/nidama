#!python
# Copyright (c) 2003-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

"""Komodo DBGP XPCOM component and service implementations.

Dev Notes:
- Mostly the Komodo DBGP XPCOM components are light wrappers around the
  equivalently named classes in dbgp/server.py
"""

import os
import sys
import types

from xpcom import components, COMException, ServerException, nsError
from xpcom.server import WrapObject, UnwrapObject
from uriparse import getMappedURI, getMappedPath
import dbgp.common
# if js accesses a python xpcom object, and an exception occurs, and we dont
# throw a server exception, data gets dumped to the console.
class koDBGPError(ServerException):
    def __init__(self, message="Unknown DBGP Error", errno=-1):
        ServerException.__init__(self, errno, message)
dbgp.common.DBGPError = koDBGPError

import dbgp.server
from dbgp.common import DBGPError
from koTreeView import TreeView
from URIlib import URIParser
import socket, base64, types
import threading, re
from xml.dom import minidom

import uriparse
import mozutils
import logging

from zope.cachedescriptors.property import Lazy as LazyProperty

log = logging.getLogger("dbgp.xpcom")
#log.setLevel(logging.DEBUG)

# due to the multithreaded nature of the classes in this file,
# it may be best to have these initialized in the main thread
# when this file is initialy loaded, and use the global proxy
# vars from the classes
# we must also avoid doing this during xpcom registration by
# not doing this in main, so this is actually filled in during the
# managers init.
_gEncodingServices = None

def _initProxies():
    global _gEncodingServices
    _gEncodingServices = components.classes['@activestate.com/koEncodingServices;1'].\
                 getService(components.interfaces.koIEncodingServices)

def _escape_string(s):
    return re.sub(# match 0x00-0x1f except TAB(0x09), LF(0x0A), and CR(0x0D)
               '([\x00-\x08\x0b\x0c\x0e-\x1f])',
               # replace with XML decimal char entity, e.g. '&#7;'
               lambda m: '\\x%02X'%ord(m.group(1)),
               s)

def _encodeString(s):
    try:
        unicodebuffer, encoding, bom = _gEncodingServices.\
                                         getUnicodeEncodedStringUsingOSDefault(_escape_string(s))
        return unicodebuffer
    except:
        return repr(s)[1:-1] # remove quotes

dbgp.server._dataType = dbgp.server.dataType
class koDBGPDataType(dbgp.server._dataType):
    _com_interfaces_ = [components.interfaces.koIDBGPDataType]
    _reg_clsid_ = "{E5D94B47-48B8-4795-AC39-7D994B8CACEE}"
    _reg_contractid_ = "@activestate.com/koDBGPDataType;1"
dbgp.server.dataType = koDBGPDataType

dbgp.server._breakpoint = dbgp.server.breakpoint
class koDBGPBreakpoint(dbgp.server._breakpoint):
    _com_interfaces_ = [components.interfaces.koIDBGPBreakpoint]
    _reg_clsid_ = "{690C35D6-3CD4-46C2-802B-EA8BE30A045D}"
    _reg_contractid_ = "@activestate.com/koDBGPBreakpoint;1"

    __safe_for_unpickling__ = 1 # required so unpickling will use __getinitargs__'s retval
    def __getstate__(self):
        # For persisting breakpoints via the pickle module.
        state = {}
        for attrName in self._attrs:
            state[attrName] = getattr(self, attrName)
        return state
    def __getinitargs__(self):
        # Define this to ensure breakpoint.__init__() gets called
        # on unpickling.
        return tuple()

dbgp.server.breakpoint = koDBGPBreakpoint


dbgp.server._spawnpoint = dbgp.server.spawnpoint
class koDBGPSpawnpoint(dbgp.server._spawnpoint):
    _com_interfaces_ = [components.interfaces.koIDBGPSpawnpoint]
    _reg_clsid_ = "{1B829885-35C7-4102-BA35-3B7522AFDB3B}"
    _reg_contractid_ = "@activestate.com/koDBGPSpawnpoint;1"

    __safe_for_unpickling__ = 1 # required so unpickling will use __getinitargs__'s retval
    def __getstate__(self):
        # For persisting breakpoints via the pickle module.
        state = {}
        for attrName in self._attrs:
            state[attrName] = getattr(self, attrName)
        return state
    def __getinitargs__(self):
        # Define this to ensure breakpoint.__init__() gets called
        # on unpickling.
        return tuple()

dbgp.server.spawnpoint = koDBGPSpawnpoint


dbgp.server._contextType = dbgp.server.contextType
class koDBGPContextType(dbgp.server._contextType):
    _com_interfaces_ = [components.interfaces.koIDBGPContextType]
    _reg_clsid_ = "{045EAAA9-28F6-463F-8FA2-044EF6163FDC}"
    _reg_contractid_ = "@activestate.com/koDBGPContextType;1"
dbgp.server.contextType = koDBGPContextType

dbgp.server._stackFrame = dbgp.server.stackFrame
class koDBGPStackFrame(dbgp.server._stackFrame):
    _com_interfaces_ = [components.interfaces.koIDBGPStackFrame]
    _reg_clsid_ = "{1054AE33-C433-4954-ADCF-7259096415C7}"
    _reg_contractid_ = "@activestate.com/koDBGPStackFrame;1"
dbgp.server.stackFrame = koDBGPStackFrame

dbgp.server._property = dbgp.server.property
class koDBGPProperty(dbgp.server._property):
    _com_interfaces_ = [components.interfaces.koIDBGPProperty]
    _reg_clsid_ = "{9483F743-D051-4D2F-8C88-B9EFA77D32B1}"
    _reg_contractid_ = "@activestate.com/koDBGPProperty;1"

    def setValue(self, value, type):
        try:
            dbgp.server._property.setValue(self, value, type)
        except DBGPError, ex:
            lastErrorSvc = components.classes["@activestate.com/koLastErrorService;1"].\
                getService(components.interfaces.koILastErrorService)
            lastErrorSvc.setLastError(ex.errno, ex.msg)
            raise ServerException(nsError.NS_ERROR_FAILURE, ex.msg)

dbgp.server.property = koDBGPProperty

class koDBGPNotification:
    _com_interfaces_ = [components.interfaces.koIDBGPNotification]
    def __init__(self, session, name, value):
        self.session = session
        self.name = name
        self.value = value

_dbgp_uri_with_uuid_p = re.compile('(dbgp://)[-0-9a-fA-F]{36}(/.*)')

dbgp.server._session = dbgp.server.session
class koDBGPSession(dbgp.server._session):
    _com_interfaces_ = [components.interfaces.koIDBGPSession]
    _reg_clsid_ = "{367AA61A-9DEF-409D-B85C-E5209E7FF984}"
    _reg_contractid_ = "@activestate.com/koDBGPSession;1"

    def __init__(self, sessionHost):
        dbgp.server._session.__init__(self, sessionHost)

    @LazyProperty
    def _observerSvc(self):
        return components.classes["@mozilla.org/observer-service;1"]\
                .getService(components.interfaces.nsIObserverService)
    @LazyProperty
    def _lastErrorSvc(self):
        return components.classes["@activestate.com/koLastErrorService;1"]\
                         .getService(components.interfaces.koILastErrorService)

    def get_status(self):
        try:
            return dbgp.common.status_names.index(self.statusName)
        except ValueError, e:
            return dbgp.common.STATUS_STARTING
    
    def get_reason(self):
        return dbgp.common.reason_names.index(self.reason)

    @components.ProxyToMainThreadAsync
    def notifyDebuggerSessionNotify(self, UIManager, notification, name):
        UIManager.notifyDebuggerSessionNotify(notification, name)

    @components.ProxyToMainThreadAsync
    def client_addBreakpoint(self, bp):
        self._bpmgr.client_addBreakpoint(self, bp)

    @components.ProxyToMainThreadAsync
    def client_updateBreakpoint(self, bp):
        self._bpmgr.client_updateBreakpoint(self, bp)

    @components.ProxyToMainThreadAsync
    def client_removeBreakpoint(self, bp):
        self._bpmgr.client_removeBreakpoint(self, bp)

    # notify is not an xpcom interface
    def notify(self, name, data, node):
        # THREAD WARNING
        # this function is called from the command loop thread.  Do
        # not do anything here that will result in another command
        # being sent to the client, that will result in a lockup
        # the observerProxy is async, so it will not block the thread
        log.debug('notification %r: %r nodes %r', name, data, node)
        
        try :
            if name == "breakpoint_set":
                children = node.getElementsByTagName("breakpoint")
                for child in children:
                    bp = dbgp.server.breakpoint()
                    bp.initWithNode(child)
                    bp.filename = getMappedURI(bp.filename)
                    if bp.filename.startswith("http"):
                        bp.filename = "dbgp:///"+bp.filename
                    self.client_addBreakpoint(bp)
                return
            elif name == "breakpoint_update":
                children = node.getElementsByTagName("breakpoint")
                for child in children:
                    bp = dbgp.server.breakpoint()
                    bp.initWithNode(child)
                    bp.filename = getMappedURI(bp.filename)
                    if bp.filename.startswith("http"):
                        bp.filename = "dbgp:///"+bp.filename
                    self.client_updateBreakpoint(bp)
                return
            elif name == "breakpoint_delete":
                # data is the breakpoint id, find it, remove it
                self.client_removeBreakpoint(data)
                return
        except Exception, e:
            log.exception(e)
            return
    
        notification = koDBGPNotification(self, name, data)
        self.notifyDebuggerSessionNotify(self._application.UIManager,
                                         notification, name)
 
    @LazyProperty
    def observerSvc(self):
        return components.classes["@mozilla.org/observer-service;1"].\
               getService(components.interfaces.nsIObserverService)
    
    @components.ProxyToMainThreadAsync
    def notifyDebuggerSessionStateChange(self, UIManager, statusName):
        UIManager.notifyDebuggerSessionStateChange(self, statusName)
        self.observerSvc.notifyObservers(self, 'debugger_session_state_change',
                                         statusName)
        
    # stateChange is not an xpcom interface
    def stateChange(self, node):
        # THREAD WARNING
        # this function is called from the command loop thread.  Do
        # not do anything here that will result in another command
        # being sent to the client, that will result in a lockup
        # the observerProxy is async, so it will not block the thread
        if node:
            dbgp.server._session.stateChange(self, node)
            # grab the status name once, early, to prevent possible races where
            # it changes in the middle of this running
            statusName = node.getAttribute('status')
        else:
            statusName = self.statusName
        log.debug('Notify state change %r for %r' % (statusName, self))
        # There may not be a UI manager - such is the case for code_profiling.
        UIManager = getattr(self._application, 'UIManager', None)
        if UIManager is not None:
            self.notifyDebuggerSessionStateChange(UIManager, statusName)

    def resume(self, action):
        # set the status manually and notify the state change before sending the
        # actual command to avoid a race where the server might end up in the
        # break state before get a chance to notify about the running state
        self.statusName = "running"
        self.stateChange(None)
        result = dbgp.server._session.resume(self, action)
        return result

    def _add_uuid_to_dbgp_uri(self, name):
        if name.startswith("dbgp:"):
            parts = re.split('(//)', name, 1)
            newName = "%s%s%s/%s" % (parts[0],
                                     parts[1],
                                     self._application.uuid,
                                     parts[2])
            return newName
        return name

    def _remove_uuid_from_dbgp_uri(self, name):
        #re.compile('(dbgp://)[-0-9a-fA-F]{36}(/.*)')
        m = _dbgp_uri_with_uuid_p.match(name)
        if m is None:
            return name
        return m.group(1) + m.group(2)

    def _addApplicationTag(self, frame):
        # Insert an application-identifier after the 'dbgp://' part.
        frame.filename = self._add_uuid_to_dbgp_uri(frame.filename)
        return frame
    
    def stackGet(self, depth):
        frame = dbgp.server._session.stackGet(self, depth)
        self._addApplicationTag(frame)
        return frame
    
    def stackFramesGet(self):
        frames = dbgp.server._session.stackFramesGet(self)
        for frame in frames:
            self._addApplicationTag(frame)
        return frames
        
    def get_maxChildren(self):
        return self.maxChildren

    def set_maxChildren(self, val):
        try:
            dbgp.server._session.featureSet(self, 'max_children', val)
            self.maxChildren = int(dbgp.server._session.featureGet(self, 'max_children'))
        except Exception, e:
            log.warn('unable to set maxChildren - not supported')

    def get_maxData(self):
        return self.maxData

    def set_maxData(self, val):
        try:
            dbgp.server._session.featureSet(self, 'max_data', val)
            self.maxData = int(dbgp.server._session.featureGet(self, 'max_data'))
        except Exception, e:
            log.warn('unable to set maxData - not supported')

    def get_maxDepth(self):
        return self.maxDepth
    
    def get_maxDepth(self, val):
        try:
            dbgp.server._session.featureSet(self, 'max_depth', val)
            self.maxDepth = int(dbgp.server._session.featureGet(self, 'max_depth'))
        except Exception, e:
            log.warn('unable to set maxDepth - not supported')

    def get_application(self):
        return self._application
    
    def get_address(self):
        return self._clientAddr[0]
    
    def get_port(self):
        return self._clientAddr[1]
    
    def get_supportsDetach(self):
        return self._supportsOptionalCommand('detach')
    
    def get_supportsInteract(self):
        return self._supportsOptionalCommand('interact')

    def spawnpointSet(self, sp):
        # Override subclass for URI mapping and XPCOM error handling.
        # The Tcl client can, for example, return this:
        #   DBGPError: (u'Spawnpoints not allowed on this line', u'203')
        orig_uri = sp.filename
        try:
            # For URI mapping, ensure we unmap the URI as best we can.
            # http://bugs.activestate.com/show_bug.cgi?id=69715
            unmappedURI = getMappedPath(orig_uri, host=self.hostname)
            if unmappedURI != orig_uri:
                # Remove the host part and update the stored filename.
                uri = URIParser(unmappedURI)
                if uri.scheme == "file":
                    uri.server = ""
                sp.filename = uri.URI
            return dbgp.server._session.spawnpointSet(self, sp)
        except DBGPError, ex:
            self._lastErrorSvc.setLastError(ex.errno, ex.msg)
            raise ServerException(nsError.NS_ERROR_FAILURE, ex.msg)
        finally:
            # Restore the original filename.
            sp.filename = orig_uri

    def breakpointSet(self, bp):
        # Override subclass for URI mapping and XPCOM error handling.
        orig_uri = bp.filename
        try:
            # For URI mapping, ensure we unmap the URI as best we can.
            # http://bugs.activestate.com/show_bug.cgi?id=69715
            unmappedURI = getMappedPath(orig_uri, host=self.hostname)
            if unmappedURI != orig_uri:
                # Remove the host part and update the stored filename.
                uri = URIParser(unmappedURI)
                if uri.scheme == "file":
                    uri.server = ""
                bp.filename = uri.URI
                #print "Unmapped filename: %r to original: %r" % (orig_uri,
                #                                                 bp.filename)
            bp.filename = self._remove_uuid_from_dbgp_uri(bp.filename)
            return dbgp.server._session.breakpointSet(self, bp)
        except DBGPError, ex:
            self._lastErrorSvc.setLastError(ex.errno, str(ex.msg))
            raise ServerException(nsError.NS_ERROR_FAILURE, ex.msg)
        finally:
            # Restore the original filename.
            bp.filename = orig_uri

    def breakpointGet(self, bpid):
        bp = dbgp.server._session.breakpointGet(self, bpid)
        try:
            bp.filename = self._add_uuid_to_dbgp_uri(bp.filename)
        except AttributeError:
            pass

    def breakpointList(self):
        blist = dbgp.server._session.breakpointList(self)
        for bp in blist:
            try:
                bp.filename = self._add_uuid_to_dbgp_uri(bp.filename)
            except AttributeError:
                pass

    # By DBGP spawnpoint URIs must start with 'file://',
    # so we don't need to massage dbgp URIs for them.

    def getSourceCode(self, filename, startline, endline):
        filename_fixed = self._remove_uuid_from_dbgp_uri(filename)
        return dbgp.server._session.getSourceCode(self, filename_fixed, startline, endline)

    def propertyValue(self, name):
        # Override subclass for XPCOM Unicode-handling and Error-handling.
        try:
            return dbgp.server._session.propertyValue(self, name)
        except DBGPError, ex:
            self._lastErrorSvc.setLastError(ex.errno, ex.msg)
            raise ServerException(nsError.NS_ERROR_FAILURE, ex.msg)

dbgp.server.session = koDBGPSession

class koDBGPTerminalInterrupt:
    _com_interfaces_ = [components.interfaces.koITerminalInterrupt]
    _reg_clsid_ = "{760fc589-04b9-4183-8517-89dc3f24b01b}"
    _reg_contractid_ = "@activestate.com/koDBGPTerminalInterrupt;1"
    
    def __init__(self, application):
        self.application = application
    
    def puts(self, data):
        return self.write(data)

    def write(self, data):
        if self.application.currentSession.interactivePrompt:
            return self.application.currentSession.interact(data) != 0
        return 0

dbgp.server._application = dbgp.server.application
class koDBGPApplication(dbgp.server._application):
    _com_interfaces_ = [components.interfaces.koIDBGPApplication]
    _reg_clsid_ = "{3FE1F468-BACA-4252-A7F8-A15E826276BD}"
    _reg_contractid_ = "@activestate.com/koDBGPApplication;1"

    def __init__(self, appMgr):
        dbgp.server._application.__init__(self, appMgr)
        self.interactiveHandler = koDBGPTerminalInterrupt(self)
        self.terminal = None
        self.uuid = mozutils.generateUUID()
        appMgr.debugMgr._applicationFromUUID[self.uuid] = self
    
    def set_currentSession(self, session):
        sess = UnwrapObject(session)
        if not self.haveSession(sess):
            raise Exception('session is not part of this application')
        self.currentSession = sess

    def setUIManager(self, UIManager):
        self.UIManager = UIManager

    def outputHandler(self, stream, text):
        log.debug('outputHandler [%r] [%r]', stream, text)
        text = _encodeString(text)
        if stream == 'stdout' and self._stdout:
            self._stdout.write(text)
        elif stream == 'stderr' and self._stderr:
            self._stderr.write(text)

    @components.ProxyToMainThreadAsync
    def codeProfileHandler(self, session, data):
        # Notify of the code profililing data.
        # Always use base64 for profiling data on Windows - bug 95262.
        observerSvc = components.classes["@mozilla.org/observer-service;1"].\
                        getService(components.interfaces.nsIObserverService)
        if not sys.platform.startswith('win'):
            try:
                observerSvc.notifyObservers(session, 'debugger_code_profiling_data', data)
                return
            except UnicodeDecodeError:
                # Try sending as base64 then - bug 93345.
                pass
        import base64
        data = base64.b64encode(data)
        observerSvc.notifyObservers(session, 'debugger_code_profiling_data_base64', data)

    def shutdown(self):
        dbgp.server._application.shutdown(self)
        # This can be called multiple times for one app
        if self.uuid in self.appMgr.debugMgr._applicationFromUUID:
            del self.appMgr.debugMgr._applicationFromUUID[self.uuid]

    def get_uuid(self):
        return self.uuid

dbgp.server.application = koDBGPApplication

class _BreakpointsTreeView(TreeView):
    """
    This class implements one tree per window through
    the Breakpoint Manager.
    """
    _com_interfaces_ = [components.interfaces.nsITreeView]
    def __init__(self):
        # nsITreeView setup stuff
        TreeView.__init__(self) # for debugging: , debug="bp")
        bpManager = components.classes["@activestate.com/koDBGPBreakpointManager;1"].\
                            getService(components.interfaces.koIDBGPBreakpointManager)
        self._bpManager = UnwrapObject(bpManager)
        
    def setTree(self, tree):
        TreeView.setTree(self, tree)
        if self._tree:
            self._tree.beginUpdateBatch()
            self._tree.rowCountChanged(0, len(self._bpManager._order))
            self._tree.invalidate()
            self._tree.endUpdateBatch()
            
    def updateTreeView(self, rowIndex=None, rowCount=None,
                       invalidStartIndex=None, invalidEndIndex=None):
        self._tree.beginUpdateBatch()
        if rowCount is not None:
            self._tree.rowCountChanged(rowIndex, rowCount)
        if invalidStartIndex is None:
            self._tree.invalidate()
        else:
            self._tree.invalidateRange(invalidStartIndex, invalidEndIndex)
        self._tree.endUpdateBatch()
        
    def getCurrentRow(self):
        row = self._tree.view.selection.currentIndex
        if row != -1:
            return row
        raise ServerException(nsError.NS_ERROR_FAILURE,
                                  "no currently selected breakpoint")
    #---- nsITreeView implementation for the "Breakpoints" tab
    # This is split between this class (on a per-view basis)
    # and koDBGPBreakpointManager, which handles data and methods
    # common to all windows.
    #
    #TODO:
    # - add support for multi-column sorting control
    # - add methods to style somethings, e.g. "(no condition)" could be
    #   made grey, likewise "break always"
    def invalidateRow(self, row):
        self._tree.invalidateRow(row)

    def get_rowCount(self):
        return len(self._bpManager._order)

    def getCellText(self, row, column):
        col = column.id
        try:
            guid = self._bpManager._order[row]
            datum = self._bpManager._rowData[guid][col]
        except IndexError:
            return ""
        except KeyError:
            log.error("unknown breakpoint column id: '%s'" % col)
            return ""
        if type(datum) not in types.StringTypes:
            datum = str(datum)
        return datum

    def cycleCell(self, row, column):
        col = column.id
        if col == "breakpoints-type-and-state":
            # Toggle the breakpoint enabled/disabled state.
            try:
                guid = self._bpManager._order[row]
                self._bpManager.toggleBreakpointState(guid)
            except IndexError:
                pass
            except koDBGPError, e:
                log.debug("%s: %s", e[0], e[1])
                if e[0] == 205:  # DBP_E_NoSuchBreakpoint
                    return
                log.exception(e)

    def getImageSrc(self, row, column):
        col = column.id
        if col != "breakpoints-type-and-state":
            return ""
        try:
            guid = self._bpManager._order[row]
            type_ = self._bpManager._rowData[guid]["type"]
            state = self._bpManager._rowData[guid]["state"]
            if type_ == "spawn" and state == "enabled":
                return "chrome://komodo/skin/images/spawnpoint_enabled.gif"
            elif type_ == "spawn" and state == "disabled":
                return "chrome://komodo/skin/images/spawnpoint_disabled.gif"
            if state == "enabled":
                return "chrome://komodo/skin/images/breakpoint_enabled.gif"
            elif state == "disabled":
                return "chrome://komodo/skin/images/breakpoint_disabled.gif"
            elif state == "deleted":
                log.warn("did not exist a breakpoint with state='deleted': "
                         "row %d" % row)
                return "chrome://komodo/skin/global/images/delete.png"
            else:
                log.error("unexpected breakpoint state (row %d): '%s' "
                          "(type '%s')" % (row, state, type_))
                return ""
        except IndexError:
            return ""
    

dbgp.server._breakpointManager = dbgp.server.breakpointManager
class koDBGPBreakpointManager(dbgp.server._breakpointManager):
    _com_interfaces_ = [components.interfaces.koIDBGPBreakpointManager,
                        components.interfaces.nsIObserver]
    _reg_clsid_ = "{3E4A2213-1483-4F6C-A8A7-CFCA4698FE7D}"
    _reg_contractid_ = "@activestate.com/koDBGPBreakpointManager;1"

    def __init__(self):
        dbgp.server._breakpointManager.__init__(self)

        self._rowData = {
            # <breakpoint guid>: <row data dict>
        }
        self._order = [] # list of breakpoint guid's in table display order
        # Key (usually a <treecol/> id) by which the list (self._order)
        # is sorted.
        self._sortedBy = None
        self._sortReversed = 0 # boolean indicating if currently reverse sorted
        self._tabMgrs = []   # List of koIBreakpointsTabManager
        self._treeViewFromTabMgr = {} # Map koIBreakpointsTabManager => koITreeView

        # self.tabMgr = None
        self._topViews = []
        
        self._wrapped = WrapObject(self, components.interfaces.nsIObserver)
        self.observerSvc = components.classes["@mozilla.org/observer-service;1"].\
                        getService(components.interfaces.nsIObserverService)
        self.observerSvc.addObserver(self._wrapped, "quit-application-granted", 0)
        self.restoreBreakpoints()
        
        #XXX Have to keep these constants in sync with value in markers.js.
        self.MARKNUM_SPAWNPOINT_ENABLED = 4
        self.MARKNUM_SPAWNPOINT_DISABLED = 3
        self.MARKNUM_BREAKPOINT_ENABLED = 2
        self.MARKNUM_BREAKPOINT_DISABLED = 1
        self._bpMarkerNums = [
            self.MARKNUM_SPAWNPOINT_ENABLED,
            self.MARKNUM_SPAWNPOINT_DISABLED,
            self.MARKNUM_BREAKPOINT_ENABLED,
            self.MARKNUM_BREAKPOINT_DISABLED,
        ]
        self._bpType2markerNum = {
            # Map a breakpoint type and state to a marker number.
            ('line', 'enabled'): self.MARKNUM_BREAKPOINT_ENABLED,
            ('line', 'disabled'): self.MARKNUM_BREAKPOINT_DISABLED,
            ('call', 'enabled'): self.MARKNUM_BREAKPOINT_ENABLED,
            ('call', 'disabled'): self.MARKNUM_BREAKPOINT_DISABLED,
            ('return', 'enabled'): self.MARKNUM_BREAKPOINT_ENABLED,
            ('return', 'disabled'): self.MARKNUM_BREAKPOINT_DISABLED,
            ('exception', 'enabled'): self.MARKNUM_BREAKPOINT_ENABLED,
            ('exception', 'disabled'): self.MARKNUM_BREAKPOINT_DISABLED,
            ('conditional', 'enabled'): self.MARKNUM_BREAKPOINT_ENABLED,
            ('conditional', 'disabled'): self.MARKNUM_BREAKPOINT_DISABLED,
            ('watch', 'enabled'): self.MARKNUM_BREAKPOINT_ENABLED,
            ('watch', 'disabled'): self.MARKNUM_BREAKPOINT_DISABLED,
            ('spawn', 'enabled'): self.MARKNUM_SPAWNPOINT_ENABLED,
            ('spawn', 'disabled'): self.MARKNUM_SPAWNPOINT_DISABLED,
        }
        self._markerHandles = {
            # <breakpoint guid>: <marker handle from ISciMoz.addMarker()>
        }

    def findBreakpointGuidById(self, session, bpid):
        sessId = (session.applicationId, session.threadId)
        if sessId in self._allSessionBPIDs:
            for guid, id in self._allSessionBPIDs[sessId].items():
                if id == bpid:
                    return guid
        return None

    #---- Methods for keeping breakpoint scintilla markers and the
    #     breakpoints in sync.
    def _getMarkerNum(self, bp):
        try:
            return self._bpType2markerNum[(bp.type, bp.state)]
        except KeyError:
            log.warn("Could not determine scintilla marker number of "
                     "breakpoint of type '%s' and state '%s' on "
                     "line %s of file '%s': no restoring marker",
                     bp.type, bp.state, bp.lineno, bp.filename)
            return None
        
    def addTopView(self, topView):
        self._topViews.append(topView)
        
    def removeTopView(self, topView):
        try:
            idx = self._topViews.index(topView)
            del self._topViews[idx]
        except IndexError:
            log.info("Can't find a topView to remove")
        
    def _addMarker(self, bp):
        """Look for the breakpoint's source in the views.  As soon
        as we find one, we can add its marker and break, since the
        marker will be shared across all other views.
        """
        log.debug("koDBGPBreakpointManager._addMarker(%s#%s)",
                  os.path.basename(bp.filename), bp.lineno)
        if bp.filename and bp.lineno > 0:
            markerNum = self._getMarkerNum(bp)
            log.debug("  views[0]: markerNum=%r", markerNum)
            if markerNum is not None:
                for topView in self._topViews:
                    views = topView.getViewsByTypeAndURIX(1, "editor", bp.filename)
                    if views:
                        view = views[0] # marker mods on any view are carried to all others
                        view = view.QueryInterface(components.interfaces.koIScintillaView)
                        log.info("add %s/%s breakpoint marker to %s, line %d",
                                 bp.type, bp.state, view.koDoc.baseName,
                                 bp.lineno)
                        markerHandle = view.scimoz.markerAdd(bp.lineno-1, markerNum)
                        self._markerHandles[bp.getGuid()] = markerHandle
                        break

    def _removeMarker(self, bp):
        log.debug("koDBGPBreakpointManager._removeMarker(%s#%s)",
                  os.path.basename(bp.filename), bp.lineno)
        if bp.filename and bp.lineno > 0:
            markerNum = self._getMarkerNum(bp)
            if markerNum is not None:
                for topView in self._topViews:
                    views = topView.getViewsByTypeAndURIX(1, "editor", bp.filename)
                    if views:
                        view = views[0] # marker mods on any view are carried to all others
                        view = view.QueryInterface(components.interfaces.koIScintillaView)
                        log.info("remove %s/%s breakpoint marker to %s, line %d",
                                 bp.type, bp.state, view.koDoc.baseName,
                                 bp.lineno)
                        view.scimoz.markerDelete(bp.lineno-1, markerNum)
                        guid = bp.getGuid()
                        if guid in self._markerHandles:
                            del self._markerHandles[guid]
                        break

    def _removeAllMarkers(self):
        log.debug("koDBGPBreakpointManager._removeAllMarkers()")
        for topView in self._topViews:
            views = topView.getViewsByTypeX(1, "editor")
            if views:
                for view in views:
                    view = view.QueryInterface(components.interfaces.koIScintillaView)
                    for markerNum in self._bpMarkerNums:
                        view.scimoz.markerDeleteAll(markerNum)
            self._markerHandles = {}

    def addMarkersForDocument(self, koDoc, scintilla):
        log.debug("koDBGPBreakpointManager.addMarkersForDocument(%r, scintilla)",
                  koDoc.baseName)
        if not koDoc.file: # then this is a new document w/o an associated file
            return
        uri = koDoc.file.URI
        scimoz = scintilla.scimoz
        #XXX This is really inefficient. Should make self._breakpoints more
        #    efficient for this lookup (or at least construct a cached
        #    data structure for this). Should do stress testing to see if
        #    there is a need.
        for bp in self._breakpoints.values():
            #XXX What about case-insensitivity on Windows?
            if bp.filename == uri and bp.lineno > 0:
                markerNum = self._getMarkerNum(bp)
                if markerNum is not None:
                    markerHandle = scimoz.markerAdd(bp.lineno-1, markerNum)
                    self._markerHandles[bp.getGuid()] = markerHandle

    def updateBreakpointsFromMarkers(self, koDoc, scintilla):
        log.debug("koDBGPBreakpointManager.updateBreakpointsFromMarkers(%r, scintilla)",
                  koDoc.baseName)
        if not koDoc.file: # then this is a new document w/o an associated file
            return
        uri = koDoc.file.URI
        scimoz = scintilla.scimoz
        #XXX As above, it might be necessary/helpful to cache the breakpoints
        #    (or their guids) by filename so don't have to iterate through
        #    all breakpoints.
        try:
            for bp in self._breakpoints.values():
                #XXX What about case-insensitivity on Windows?
                if bp.filename == uri and bp.lineno > 0:
                    guid = bp.getGuid()
                    markerHandle = self._markerHandles[guid]
                    lineno = scimoz.markerLineFromHandle(markerHandle)
                    # Make sure we do NOT forward this change to current
                    # debug sessions because they still have the unmodified
                    # file content.
                    #XXX Actually shouldn't the change only not be forwarded
                    #    if that file has already been entered in this debug
                    #    session. Presumably, though, the file has be entered
                    #    already because it is current and the user is
                    #    editing it.
                    if lineno == -1:
                        log.info("breakpoint %s marker removed while editing: "
                                 "removing breakpoint", guid)
                        self._silentlyRemoveBreakpoint(bp)
                        continue
                    lineno += 1 # Breakpoint linenos are 1-based, Scimoz 0-based.
                    if lineno != bp.lineno:
                        #XXX Subtle bug: if a breakpoint moves onto a previous
                        #    breakpoint the markers get out of sync. We _could_
                        #    just delete the breakpoint at that point. In any
                        #    case, this should be rare.
                        log.info("breakpoint %s marker move from line %s to %s: "
                                 "updating breakpoint", guid, bp.lineno, lineno)
                        self._silentlyUpdateBreakpointLineno(bp, lineno)
        except Exception, e:
            log.exception("Could not update breakpoints for '%s'." % uri)
            raise

    def _silentlyRemoveBreakpoint(self, bp):
        self._lock.acquire()
        try:
            guid = bp.getGuid()
            del self._breakpoints[guid]

            del self._rowData[guid] # 1.
            row = self._order.index(guid)
            del self._order[row] # 2.
            # 3. marker already updated, that is part of the point
            self._updateTreeViews(row, -1, row, len(self._order)) # 4.
            for tabMgr in self._tabMgrs:
                tabMgr.numBreakpointsChanged()
        finally:
            self._lock.release()

    def _silentlyUpdateBreakpointLineno(self, bp, lineno):
        self._lock.acquire()
        try:
            bp.lineno = lineno
            guid = bp.getGuid()
            self._generateRowData(guid) # 1.
            # 2. don't need to re-sort: editing can't change order
            # 3. marker already updated, that is part of the point
            row = self._order.index(guid)
            for tree in self._treeViewFromTabMgr.values():
                tree.invalidateRow(row) # 4.
            # 5. unnecessary, no change in number of breakpoints
        finally:
            self._lock.release()

    def observe(self, subject, topic, data):
        if topic == "quit-application-granted":
            self.observerSvc.removeObserver(self._wrapped, "quit-application-granted")
            self.saveBreakpoints()
            
    #---- Breakpoint persistence
    def _getBreakpointsFile(self):
        """Return the name of the file in which breakpoints are persisted."""
        koDirs = components.classes["@activestate.com/koDirs;1"].getService()
        return os.path.join(koDirs.userDataDir, "breakpoints.pickle")

    def restoreBreakpoints(self):
        import pickle
        bpFile = self._getBreakpointsFile()
        breakpointList = []
        if os.path.exists(bpFile):
            try:
                fin = open(bpFile, 'r')
                try:
                    breakpointList = pickle.load(fin)
                finally:
                    fin.close()
            except (pickle.PickleError, EnvironmentError, EOFError), ex:
                log.exception("Could not restore breakpoints from '%s'.",
                              bpFile)
            else:
                log.info("restored breakpoints from '%s'", bpFile)

        # We need to assign runtime guids to the breakpoints and create
        # the self._breakpoints mapping properly.
        self._breakpoints = {}
        self._order = []
        for bp in breakpointList:
            guid = self._makeBreakpointGuid()
            bp._guid = guid
            self._breakpoints[guid] = bp
            self._order.append(guid)

        for guid in self._order:
            self._generateRowData(guid)
        self.sort()

    def saveBreakpoints(self):
        import pickle
        bpFile = self._getBreakpointsFile()
        try:
            fout = open(bpFile, 'w')
            try:
                # We just save the breakpoints themselves (and NOT their
                # runtime GUIDs, or the GUID->breakpoint mapping).
                pickle.dump(self._breakpoints.values(), fout, 0) #XXX bin=1
            finally:
                fout.close()
        except (pickle.PickleError, EnvironmentError), ex:
            log.error("Could not save breakpoints to '%s'.", bpFile)
        log.info("saved breakpoints to '%s'", bpFile)

    def client_addBreakpoint(self, session, bp):
        # we do not want to call the client, just add it to our list
        # UI will update from the observer in debugger.js (see
        # debugger_session_notify)
        session = UnwrapObject(session)
        bp = UnwrapObject(bp)
        sessId = (session.applicationId, session.threadId)
        self._lock.acquire()
        try:
            bp._guid = self._makeBreakpointGuid()
            self._breakpoints[bp.getGuid()] = bp
            self._allSessionBPIDs[sessId][bp.getGuid()] = bp._bpid
            self.postAddBreakpoint(bp)
        finally:
            self._lock.release()
        
    def client_removeBreakpoint(self, session, bpid):
        # we do not want to call the client, just remove it to our list
        # UI will update from the observer in debugger.js (see
        # debugger_session_notify)
        session = UnwrapObject(session)
        guid = self.findBreakpointGuidById(session, bpid)
        if not guid:
            return
        self._lock.acquire()
        try:
            bp = self._breakpoints[guid]
            del self._breakpoints[guid]
            self.postRemoveBreakpoint(bp)
        finally:
            self._lock.release()

    def client_updateBreakpoint(self, session, newBp):
        session = UnwrapObject(session)
        newBp = UnwrapObject(newBp)
        guid = self.findBreakpointGuidById(session, newBp._bpid)
        if not guid:
            return
        self._lock.acquire()
        try:
            bp = self._breakpoints[guid]
            self.preUpdateBreakpoint(bp)
            attrs = bp.update(newBp)
            self.postUpdateBreakpoint(bp, attrs)
        finally:
            self._lock.release()
            
    #---- Changing breakpoints and reacting to breakpoint changes.
    def addBreakpoint(self, bp):
        # Have to unwrap the koIDBGPBreakpoint here, otherwise it does not
        # compare as expected when trying to remove.
        bp = UnwrapObject(bp)
        dbgp.server._breakpointManager.addBreakpoint(self, bp)

    def removeAllBreakpointsInURI(self, uri):
        log.debug("koDBGPBreakpointManager.removeAllBreakpointsInURI(uri='%s')",
                  uri)
        for bp in self._breakpoints.values():
            #XXX What about case-insensitive Windows?
            if bp.filename == uri:
                self.removeBreakpoint(bp.getGuid())

    def toggleBreakpointState(self, guid):
        """Toggle the state of the given breakpoint btwn "enabled" and
        "disabled".
        
            "guid" is a breakpoint guid number
        """
        bp = self._breakpoints[guid]
        log.debug("koDBGPBreakpointManager.toggleBreakpointState(guid=%s): %s#%s",
                  guid, os.path.basename(bp.filename), bp.lineno)
        newState = None
        if bp.state == "enabled":
            newState = "disabled"
        elif bp.state == "disabled":
            newState = "enabled"
        if newState:
            newBp = bp.clone()
            newBp.state = newState
            self.updateBreakpoint(bp.getGuid(), newBp)

    def toggleAllBreakpointStates(self):
        for bp in self._breakpoints.values():
            if bp.state == "enabled":
                newState = "disabled" # if any bp is enabled, disable all
                break
        else:
            newState = "enabled" # if no bp's are enabled, enable all
        for bp in self._breakpoints.values():
            if bp.state not in ("enabled", "disabled"):
                continue # Don't screw up "deleted" breakpoints.
            if bp.state != newState:
                newBp = bp.clone()
                newBp.state = newState
                #XXX Might be nice to add an optional attrs=None argument
                #    to self.updateBreakpoint().
                self.updateBreakpoint(bp.getGuid(), newBp)
                
    def _updateTreeViews(self, rowIndex=None, rowCount=None,
                         invalidStartIndex=None, invalidEndIndex=None):
        for tree in self._treeViewFromTabMgr.values():
            tree.updateTreeView(rowIndex, rowCount, invalidStartIndex, invalidEndIndex)
            

    #---- post* and pre* methods for reacting to changes in the breakpoints
    # Each of these methods must do the following:
    # 1. update self._rowData
    # 2. update self._order
    # 3. update any editor-gutter markers
    # 4. if there is a Breakpoints tree, then update the tree:
    #    .invalidate*(), .rowCountChanged()
    #    In Multi-window Komodo, do this for each window's breakpoints tree
    # 5. if the number of breakpoints changed, let the "Breakpoints" tab
    #    manager know
    def postAddBreakpoint(self, bp):
        guid = bp.getGuid()
        self._generateRowData(guid)  # 1.
        self._order.append(guid) # 2.
        self._sort(self._sortedBy)
        row = self._order.index(guid)
        self._addMarker(bp) # 3.
        self._updateTreeViews(row, 1, row, len(self._order)) # 4.
        for tabMgr in self._tabMgrs: #5
            tabMgr.numBreakpointsChanged()

    def postRemoveBreakpoint(self, bp):
        guid = bp.getGuid()
        del self._rowData[guid] # 1.
        row = self._order.index(guid)
        del self._order[row] # 2.
        self._removeMarker(bp) # 3.
        self._updateTreeViews(row, -1, row, len(self._order)) # 4.
        for tabMgr in self._tabMgrs: # 5.
            tabMgr.numBreakpointsChanged()

    def postRemoveAllBreakpoints(self):
        self._rowData = {} # 1.
        lengthChange = len(self._order)
        self._order = [] # 2.
        self._removeAllMarkers() # 3.
        self._updateTreeViews(0, -lengthChange) # 4.
        for tabMgr in self._tabMgrs: # 5.
            tabMgr.numBreakpointsChanged()

    def addTabMgr(self, tabMgr):
        self._tabMgrs.append(tabMgr)
        self._treeViewFromTabMgr[tabMgr] = _BreakpointsTreeView()

    def removeTabMgr(self, tabMgr):
        try:
            del self._treeViewFromTabMgr[tabMgr]
        except KeyError:
            # Not much users can do if we hit this exception.
            log.info("removeTabMgr: Can't find _treeViewFromTabMgr[tabMgr]")
        try:
            idx = self._tabMgrs.index(tabMgr)
            del self._tabMgrs[idx]
        except IndexError:
            log.info("Can't find a tabManager to remove")
        
    def treeViewFromTabMgr(self, tabMgr):
        return self._treeViewFromTabMgr[tabMgr]

    def preUpdateBreakpoint(self, bp):
        self._removeMarker(bp) # 3. remove marker before update...
        
    def postUpdateBreakpoint(self, bp, attrs):
        guid = bp.getGuid()
        self._generateRowData(guid) # 1.
        self._sort(self._sortedBy) # 2. re-sort
        row = self._order.index(guid)
        self._addMarker(bp) # 3. ...and re-add marker after
        self._updateTreeViews(None, None, row, len(self._order)) # 4.
        # 5. unnecessary, no change in number of breakpoints
    
    #---- Getting breakpoint info.
    def currentBreakpointFromTabMgr(self, tabMgr):
        row = self._treeViewFromTabMgr[tabMgr].getCurrentRow()
        guid = self._order[row]
        return self._breakpoints[guid]

    def currentBreakpointGuidFromTabMgr(self, tabMgr):
        row = self._treeViewFromTabMgr[tabMgr].getCurrentRow()
        return self._order[row]

    def currentBreakpointNameFromTabMgr(self, tabMgr):
        row = self._treeViewFromTabMgr[tabMgr].getCurrentRow()
        guid = self._order[row]
        return self._rowData[guid]["breakpoints-name"]

    def getBreakpointAtFileAndLine(self, filename, line):
        for bp in self._breakpoints.values():
            if bp.filename == filename and bp.lineno == line and bp.type != "spawn":
                return bp
        else:
            return None
    def getSpawnpointAtFileAndLine(self, filename, line):
        for bp in self._breakpoints.values():
            if bp.type == "spawn" and bp.filename == filename and bp.lineno == line:
                return bp
        else:
            return None

    def copyBreakpointsToNewURI(self, uri_old, uri_new):
        log.debug("koDBGPBreakpointManager.copyBreakpointsToNewURI(old='%s', new='%s')",
                  uri_old, uri_new)
        for bp in self._breakpoints.values():
            #XXX What about case-insensitive Windows?
            if bp.filename == uri_old:
                nbp = bp.clone()
                nbp.filename = uri_new
                self.addBreakpoint(nbp)

    def _generateRowData(self, guid):
        """Translate the data for the breakpoint with the given guid for
        display in the "Breakpoints" tree.
        
        Generally we are taking VS.NET's lead here.
        """
        #XXX Currently not showing these attributes: temporary, exceptionName
        bp = self._breakpoints[guid]
        conditionDesc = "(no condition)"
        typeAndState = "breakpoint-%s" % bp.state
        if bp.type == "conditional":
            #XXX is it an error if bp.expression is null or the empty string?
            conditionDesc = "when '%s' is true" % bp.expression
        elif bp.type == "spawn":
            conditionDesc = "N/A"
            typeAndState = "spawnpoint-%s" % bp.state
        if bp.type == "spawn":
            hitCountDesc = "N/A"
        elif bp.hitValue:
            if bp.hitCondition in (None, ">="):
                hitCountDesc = "break when hit count is greater than or equal to %s" % bp.hitValue
            elif bp.hitCondition == "==":
                hitCountDesc = "break when hit count is equal to %s" % bp.hitValue
            elif bp.hitCondition == "%":
                hitCountDesc = "break when hit count is a multiple of %s" % bp.hitValue
            else:
                log.error("unknown hit condition: '%s'" % bp.hitCondition)
                hitCountDesc = "???"
        else:
            hitCountDesc = "break always"
        rowData = {
            "breakpoints-name": bp.getName(),
            "breakpoints-language": bp.language,
            "breakpoints-condition": conditionDesc,
            "breakpoints-hit-count": hitCountDesc,
            "breakpoints-file": uriparse.displayPath(bp.filename),
            "breakpoints-type-and-state": "", # don't want a label, just an image
            "state": bp.state,
            "type": bp.type,
            # Used for sorting image column on both break vs spawn and
            # enabled vs disabled.
            "type-and-state": typeAndState,
            "guid": guid, #XXX May no longer be necessary.
        }
        self._rowData[guid] = rowData
    
    def _sort(self, sortBy):
        """Do the actual sorting of the rows by the given key."""
        def cond(guid1, guid2, sortBy=sortBy, rowData=self._rowData):
            return cmp(rowData[guid1][sortBy], rowData[guid2][sortBy])

        try:
            self._order.sort(cond)
            if self._sortReversed:
                self._order.reverse()
        except KeyError:
            log.error("Cannot sort breakpoints by: '%s'" % sortBy)
            raise

    def sort(self, sortBy="breakpoints-name"):
        """Sort the current rows by the given key.
        
            "sortBy" is the key by which the sort. Usually this is a
                Breakpoints <treecol/> id. If not specified it defaults
                to the "breakpoints-name" key/column.
        
        If already sorted by this key then reverse the sorting order.
        Note that the breakpoints tree supports sorting on multiple keys
        (as does bugzilla for example).
        """
        log.debug("sort breakpoints by '%s'", sortBy)
        if sortBy == "breakpoints-type-and-state":
            sortBy = "type-and-state"
        if self._sortedBy == sortBy:
            self._order.reverse()
            self._sortReversed = not self._sortReversed
        else:
            self._sortReversed = 0  # reset to non-reversed sort for a new key
            self._sort(sortBy)
        self._sortedBy = sortBy
        self._updateTreeViews() # Just invalidate the view
    
dbgp.server.breakpointManager = koDBGPBreakpointManager

    
dbgp.server._manager = dbgp.server.manager
class koDBGPManager(dbgp.server._manager):
    _com_interfaces_ = [components.interfaces.koIDBGPManager,
                        components.interfaces.nsIObserver]
    _reg_clsid_ = "{EC99C1B5-9E83-4200-BF69-F06D3B72A243}"
    _reg_contractid_ = "@activestate.com/koDBGPManager;1"
    _reg_categories_ = [
         ("komodo-delayed-startup-service", "koDBGPManager"),
    ]
    
    def __init__(self):
        dbgp.server._manager.__init__(self)
        _initProxies()
        self._prefs = components.classes["@activestate.com/koPrefService;1"].\
                        getService(components.interfaces.koIPrefService).prefs
        self._bpmgr = components.classes["@activestate.com/koDBGPBreakpointManager;1"].\
                        getService(components.interfaces.koIDBGPBreakpointManager)

        # Observers will be QI'd for a weak-reference, so we must keep the
        # observer alive ourself, and must keep the COM object alive,
        # _not_ just the Python instance!!!
        self._wrapped = WrapObject(self, components.interfaces.nsIObserver)
        self._observablePrefNames = ['debuggerListenerPortType',
                                    'debuggerListenerPort',
                                    'dbgpProxyEnabled',
                                    'dbgpProxyKey',
                                    'dbgpProxyListenAddress']
        prefObserverService = self._prefs.prefObserverService
        prefObserverService.addObserverForTopics(self._wrapped,
                                                 self._observablePrefNames,
                                                 1)

        self.observerSvc = components.classes["@mozilla.org/observer-service;1"].\
                        getService(components.interfaces.nsIObserverService)
        self.observerSvc.addObserver(self._wrapped, "quit-application-granted", 0)

    @LazyProperty
    def _lastErrorSvc(self):
        return components.classes["@activestate.com/koLastErrorService;1"]\
                         .getService(components.interfaces.koILastErrorService)

    def shutdown(self):
        if self._wrapped is None:
            return
        self.observerSvc.removeObserver(self._wrapped, "quit-application-granted")
        self._prefs.setBooleanPref("listenForDebugger", self.isListening())
        self.stop()
        prefObserverService = self._prefs.prefObserverService
        try:
            prefObserverService.removeObserverForTopics(self._wrapped,
                                                        self._observablePrefNames)
        except ServerException, e:
            log.exception(e)
        self._applicationFromUUID = {}
        self._wrapped = None

    @components.ProxyToMainThreadAsync
    def notifyObservers(self, subject, topic, data):
        self.observerSvc.notifyObservers(subject, topic, data)

    def getBreakpointManager(self):
        bpMgr = components.classes["@activestate.com/koDBGPBreakpointManager;1"]\
                .getService(components.interfaces.koIDBGPBreakpointManager)
        return bpMgr

    # non-xpcom interface used in server.py
    # XXX TODO: handle project preferences correctly, see also views.js
    def getURIMappings(self):
        mapping = self._prefs.getStringPref('mappedPaths')
        if not mapping:
            return []
        return [x for x in mapping.split('::') if len(x) > 0]
    
    def _getKey(self):
        proxyKey = None
        if self._prefs.hasPref("dbgpProxyKey"):
            proxyKey = self._prefs.getStringPref("dbgpProxyKey")
        if not proxyKey:
            proxyKey = os.getenv('USER',os.getenv('USERNAME','NOKEY'))
        return proxyKey

    def getKey(self):
        if self._server_key is None:
            return self._getKey()
        else:
            return self._server_key

    def start(self):
        self._lastErrorSvc.setLastError(0, '')
        if self.isListening():
            return
        # get address/port from prefs, then start the listener
        proxyEnabled = 0
        debuggerListenerPortType = self._prefs.getStringPref("debuggerListenerPortType")
        if debuggerListenerPortType == "specific":
            port = self._prefs.getLongPref("debuggerListenerPort")
            #XXX Should we validate the port number here?
        elif debuggerListenerPortType == "system":
            port = 0    # 0 means ask the system for a free port
        else:
            log.warn("%r: unexpected 'debuggerListenerPortType' pref "
                     "value, defaulting to 'system'",
                     debuggerListenerPortType)
            port = 0
        if self._prefs.hasPref("dbgpProxyEnabled"):
            proxyEnabled = self._prefs.getBooleanPref("dbgpProxyEnabled")
        if proxyEnabled:
            proxyKey = ''
            proxyAddr = '127.0.0.1'
            proxyPort = 9001
            proxyKey = self._getKey()
            if self._prefs.hasPref("dbgpProxyListenAddress"):
                addr = self._prefs.getStringPref("dbgpProxyListenAddress")
                (proxyAddr, _port,) = addr.split(':')
                if _port:
                    proxyPort = int(_port)

            log.debug('setting proxy key to %s', proxyKey)
            self.setKey(proxyKey)
            log.debug('setting proxy address to %s:%d', proxyAddr, proxyPort)
            self.setProxy(proxyAddr, proxyPort)
        else:
            self.setProxy('', 0)
            self.setKey('')
        
        self.listen('', port)

    def listen(self, address, port):
        try:
            dbgp.server._manager.listen(self, address, port)
        except DBGPError, ex:
            self._lastErrorSvc.setLastError(ex.errno, ex.msg)
            raise ServerException(nsError.NS_ERROR_FAILURE, ex.msg)
        try:
            self.notifyObservers(None, 'debugger_listener', 'on')
        except COMException, e:
            pass

    def stop(self):
        try:
            dbgp.server._manager.stop(self)
        except DBGPError, ex:
            self._lastErrorSvc.setLastError(ex.errno, ex.msg)
            raise ServerException(nsError.NS_ERROR_FAILURE, ex.msg)
            # likely the proxy died, but we still stopped listening, notify we're off
        try:
            self.notifyObservers(None, 'debugger_listener', 'off')
        except COMException, e:
            pass

    def isListening(self):
        if self._listener and self._listener.checkListening():
            return 1
        return 0
    
    def onConnect(self, session, client, addr):
        # before any communication, we can decide if we want
        # to allow the connection here.  return 0 to deny
        # XXX TODO add ip filtering capability
        return dbgp.server._manager.onConnect(self, session, client, addr)
    
    def notifyInit(self, session, init):
        try:
            log.debug('Notify debugger_init for %r' % session)
            self.notifyObservers(session, 'debugger_init', '')
        except COMException, e:
            log.debug('No debugger init observers %s', e)

    def notifyStartup(self, session, init):
        try:
            log.debug('Notify debugger_startup for %r' % session)
            self.notifyObservers(session, 'debugger_startup', '')
        except COMException, e:
            log.debug('No debugger startup observers %s', e)

    def observe(self, prefSet, prefName, prefSetID):
        #print "got notify for %r:%r:%r" %(prefSet, prefName, prefSetID)
        if prefName == "quit-application-granted":
            self.shutdown()
        elif prefName in self._observablePrefNames:
            self.stop()
            self.start()
        elif prefName == "komodo-delayed-startup-service":
            if self._prefs.getBooleanPref("listenForDebugger"):
                try:
                    self.start()
                except Exception, e:
                    log.exception(e)
                    wwatch = components.classes["@mozilla.org/embedcomp/window-watcher;1"].getService(components.interfaces.nsIWindowWatcher)
                    prompt = wwatch.getNewPrompter(wwatch.activeWindow)
                    msg = ('Unable to initialize the debugging system because '+
                             e.msg + '  ' +
                             'Debugging will be unavailable until '+
                             'you change the debugger port in your preferences.  '+
                             'You can try allowing the system to provide a free port.'
                             )
                    prompt.alert("Debugger Initialization Error", msg)
                            
        self.stopOnConnect = not self.isListening()
        self._applicationFromUUID = {}


    def get_address(self):
        if self._listener:
            return self._listener._address
        return ''

    def get_port(self):
        if self._listener:
            return self._listener._port
        return 0

    def get_proxyAddress(self):
        return self._proxyAddr

    def get_proxyPort(self):
        return self._proxyPort

    def get_currentSessions(self):
        return len(self.getApplicationList())

    def get_currentConnections(self):
        c = 0
        apps = self.getApplicationList()
        for app in apps:
            c = c + app.sessionCount()
        return c

    def get_totalConnections(self):
        if self._listener:
            return self._listener._totalConnections
        return 0

    def getApplicationFromUUID(self, uuid):
        try:
            return self._applicationFromUUID[uuid]
        except KeyError:
            log.error("koDBGPManager.getApplicationFromUUID: Can't find uuid %s", uuid)
            return None

dbgp.server.manager = koDBGPManager

