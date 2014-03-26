# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is the Python XPCOM language bindings.
#
# The Initial Developer of the Original Code is
# Activestate Tool Corp.
# Portions created by the Initial Developer are Copyright (C) 2000
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#    Mark Hammond <MarkH@ActiveState.com>
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****

import os, sys, types

import xpcom
from xpcom import components, nsError, verbose, COMException
import xpcom.shutdown

import module

def _has_good_attr(obj, attr):
    # Actually allows "None" to be specified to disable inherited attributes.
    return getattr(obj, attr, None) is not None

def FindCOMComponents(py_module):
    comps = []

    # Check for the static list of Python XPCOM classes (faster).
    pyxpcom_classes = getattr(py_module, "PYXPCOM_CLASSES", None)
    if pyxpcom_classes is not None:
        # Should be a list of the available XPCOM classes.
        if isinstance(pyxpcom_classes, (tuple, list)):
            for py_class in pyxpcom_classes:
                if _has_good_attr(py_class, "_com_interfaces_") and \
                   _has_good_attr(py_class, "_reg_clsid_") and \
                   _has_good_attr(py_class, "_reg_contractid_"):
                    comps.append(py_class)
                else:
                    sys.stderr.write("PYXPCOM_CLASSES item %r does not contain"
                                     "proper pyxpcom attributes. File: %s" % (
                                     py_class, py_module.__file__))
            return comps
        else:
            sys.stderr.write("PYXPCOM_CLASSES should be a list, "
                             "not %s. File: %s" % (type(pyxpcom_classes),
                                                   py_module.__file__))

    # Else, run over all top-level objects looking for likely candidates.
    for name, obj in py_module.__dict__.items():
        try:
            # Examine class types or new style classes that inherit from object.
            if (type(obj) == types.ClassType or issubclass(obj, object)) and \
               _has_good_attr(obj, "_com_interfaces_") and \
               _has_good_attr(obj, "_reg_clsid_") and \
               _has_good_attr(obj, "_reg_contractid_"):
                comps.append(obj)
        except:
            # The issubclass call raises TypeError when the obj is not a class.
            # Something like "Ci = xpcom.components.interfaces" will raise a
            # COMException whenever we try to perform a getattr on it.
            pass
    return comps

def register_self(klass, compMgr, location, registryLocation, componentType):
    pcl = ModuleLoader
    svc = components.classes["@mozilla.org/categorymanager;1"]. \
            getService(components.interfaces.nsICategoryManager)
    # The category 'module-loader' is special - the component manager uses it
    # to create the nsIModuleLoader for a given component type.
    svc.addCategoryEntry("module-loader", pcl._reg_component_type_, pcl._reg_contractid_, 1, 1)

# The Python module loader.  Called by the component manager when it finds
# a component of type self._reg_component_type_.  Responsible for returning
# an nsIModule for the file.
class ModuleLoader:

    _com_interfaces_ = components.interfaces.nsIObserver
    _platform_names = None

    def __init__(self):
        self._registred_pylib_paths = False
        self.com_modules = {} # Keyed by module's FQN as obtained from nsIFile.path
        self.moduleFactory = module.Module
        xpcom.shutdown.register(self._on_shutdown)
        # Register for profile startup notification.
        svc = components.classes["@mozilla.org/observer-service;1"]. \
                getService(components.interfaces.nsIObserverService)
        svc.addObserver(self, "profile-after-change", False)

    def observe(self, subject, topic, data):
        if topic == "profile-after-change":
            # Add the pylib paths for the user profile extensions.
            self._registred_pylib_paths = False
            self._setupPythonPaths()
            svc = components.classes["@mozilla.org/observer-service;1"]. \
                    getService(components.interfaces.nsIObserverService)
            svc.removeObserver(self, "profile-after-change")

    def _on_shutdown(self):
        self.com_modules.clear()
        svc = components.classes["@mozilla.org/observer-service;1"]. \
                getService(components.interfaces.nsIObserverService)
        try:
            svc.removeObserver(self, "profile-after-change")
        except COMException:
            pass  # Already removed itself.

    def loadModule(self, aLocalFile):
        return self._getCOMModuleForLocation(aLocalFile)

    def loadModuleFromJAR(self, aLocalFile, path):
        raise xpcom.ServerException(nsError.NS_ERROR_NOT_IMPLEMENTED)

    def _getCOMModuleForLocation(self, componentFile):
        if not self._registred_pylib_paths:
            self._setupPythonPaths()

        fqn = componentFile.path
        if fqn[-4:] in (".pyc", ".pyo"):
            fqn = fqn[:-1]
        if not fqn.endswith(".py"):
            raise xpcom.ServerException(nsError.NS_ERROR_INVALID_ARG)
        mod = self.com_modules.get(fqn)
        if mod is not None:
            return mod
        import ihooks, sys
        base_name = os.path.splitext(os.path.basename(fqn))[0]
        loader = ihooks.ModuleLoader()

        module_name_in_sys = "component:%s" % (base_name,)
        stuff = loader.find_module(base_name, [componentFile.parent.path])
        assert stuff is not None, "Couldn't find the module '%s'" % (base_name,)
        py_mod = loader.load_module( module_name_in_sys, stuff )

        # Make and remember the COM module.
        comps = FindCOMComponents(py_mod)
        mod = self.moduleFactory(comps)
        
        self.com_modules[fqn] = mod
        return mod

    def _getExtenionDirectories(self):
        directorySvc =  components.classes["@mozilla.org/file/directory_service;1"].\
                            getService(components.interfaces.nsIProperties)
        extensionDirs = []
        enum = directorySvc.get("XREExtDL", components.interfaces.nsISimpleEnumerator)
        while enum.hasMoreElements():
            nsifile = enum.getNext().QueryInterface(components.interfaces.nsIFile)
            path = nsifile.path
            if path not in extensionDirs:
                extensionDirs.append(path)

        # Allow a custom directory service to provide additional extension
        # directories using the special "PyxpcomExtDirList" key.
        try:
            enum = directorySvc.get("PyxpcomExtDirList",
                                    components.interfaces.nsISimpleEnumerator)
            while enum.hasMoreElements():
                nsifile = enum.getNext().QueryInterface(components.interfaces.nsIFile)
                path = nsifile.path
                if path not in extensionDirs:
                    extensionDirs.append(path)
        except COMException as e:
            # Okay, no one provides that key; that's okay.
            pass

        return extensionDirs

    def _getPossiblePlatformNames(self):
        if self._platform_names is None:
            xulRuntimeSvc = components.classes["@mozilla.org/xre/app-info;1"]. \
                                getService(components.interfaces.nsIXULRuntime)
            os_name = xulRuntimeSvc.OS
            abi_name = xulRuntimeSvc.XPCOMABI
            self._platform_names = [
                "%s_%s" % (os_name, abi_name),
                "%s_%s" % (os_name, abi_name.split("-", 1)[0]),
                os_name,
            ]
        return self._platform_names

    ##
    # Register all the extension pylib paths. This supports the following pylib
    # paths within an extension, which are added to sys.path automatically.
    # Version paths are added first, where 27 is the Python major/minor version
    # number):
    #
    #    ext/pylib27
    #    ext/platform/Linux_x86-gcc3/pylib27
    #    ext/platform/Linux_x86/pylib27
    #    ext/pylib
    #    ext/platform/Linux_x86-gcc3/pylib
    #    ext/platform/Linux_x86/pylib
    #
    def _setupPythonPaths(self):
        """Add 'pylib' directies for the application and each extension to
        Python's sys.path."""

        assert not self._registred_pylib_paths
        self._registred_pylib_paths = True

        from os.path import join, exists, dirname

        # Extension directories.
        try:
            extDirs = self._getExtenionDirectories()
        except COMException:
            extDirs = []
        pyverstr = "%d%d" % (sys.version_info.major, sys.version_info.minor)
        for extDir in extDirs:
            for pylibName in ("pylib" + pyverstr, "pylib"):
                pylibPath = join(extDir, pylibName)
                if exists(pylibPath) and pylibPath not in sys.path:
                    if verbose:
                        print "pyXPCOMExtensionHelper:: Adding pylib to sys.path:" \
                              " %r" % (pylibPath, )
                    sys.path.append(pylibPath)

                platformPylibPath = join(extDir, "platform")
                if exists(platformPylibPath):
                    for platform_name in self._getPossiblePlatformNames():
                        pylibPath = join(platformPylibPath, platform_name, pylibName)
                        if exists(pylibPath) and pylibPath not in sys.path:
                            if verbose:
                                print "pyXPCOMExtensionHelper:: Adding pylib to sys.path:" \
                                      " %r" % (pylibPath, )
                            sys.path.append(pylibPath)
