#!python
# Copyright (c) 2000-2008 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

# A Service for providing Komodo-specific directory/filename information.

import os
from os.path import basename, dirname, join, isfile, normpath
import sys
import re
import logging
import applib

from xpcom import components, COMException

log = logging.getLogger("koDirs")


#---- component implementation

class KoDirs:
    # Dev Notes:
    # - If directory determination logic changes here, the equivalent
    #   logic in bklocal.py (for build-time config vars) must be updated
    #   as well).

    _com_interfaces_ = [components.interfaces.koIDirs]
    _reg_clsid_ = "{98435d6d-e24d-4057-a72a-dfcd1d282fae}"
    _reg_contractid_ = "@activestate.com/koDirs;1"
    _reg_desc_ = "Komodo Directory Information Service"

    _appdatadir_name = "komodoide" # e.g. "KomodoIDE"
    _ver = "8.5" # e.g. 4.2

    def __init__(self):
        self._ver_major, self._ver_minor = self._ver.split('.')

    @property
    def _userDataDir(self):
        # Workaround for os.environ not being able to deal with Unicode on
        # Windows; see bug 94439.
        if sys.platform.startswith("win"):
            import ctypes
            _wgetenv = ctypes.cdll.msvcrt._wgetenv
            _wgetenv.argtypes = [ctypes.c_wchar_p]
            _wgetenv.restype = ctypes.c_wchar_p
            result = _wgetenv("KOMODO_USERDATADIR")
        else:
            result = os.environ.get("KOMODO_USERDATADIR")
        setattr(self, "_userDataDir", result)
        return result

    def _userAppDataPath(self):
        # Allow a special environment variable to override the User Data
        # Dir for a Komodo run. The main motivation for this is bug
        # 32270.
        envPath = self._userDataDir
        if envPath:
            path = os.path.expanduser(envPath)
        else:
            path = applib.user_data_dir(self._appdatadir_name,
                                        "ActiveState")
        return path

    def _roamingUserAppDataPath(self):
        # Allow a special environment variable to override the User Data
        # Dir for a Komodo run. The main motivation for this is bug
        # 32270.
        envPath = self._userDataDir
        if envPath:
            path = os.path.expanduser(envPath)
        else:
            path = applib.roaming_user_data_dir(self._appdatadir_name,
                                                "ActiveState")
        return path

    def _commonAppDataPath(self):
        return applib.site_data_dir(self._appdatadir_name, "ActiveState")

    def _GetUserDataDirForVersion(self, major, minor):
        return os.path.join(self._userAppDataPath(),
                            "%s.%s" % (major, minor))

    def _GetCommonDataDirForVersion(self, major, minor):
        return os.path.join(self._commonAppDataPath(),
                            "%s.%s" % (major, minor))

    def get_userDataDir(self):
        return self._GetUserDataDirForVersion(self._ver_major,
                                              self._ver_minor)

    def get_roamingUserDataDir(self):
        return os.path.join(self._roamingUserAppDataPath(),
                            "%s.%s" % (self._ver_major, self._ver_minor))

    def get_hostUserDataDir(self):
        log.warn("hostUserDataDir is deprecated, use userDataDir instead")
        return self.get_userDataDir()

    def get_userCacheDir(self):
        d = applib.user_cache_dir(self._appdatadir_name, "ActiveState")
        return os.path.join(d, self._ver)

    def get_factoryCommonDataDir(self):
        #XXX Would be better called systemCommonDataDir, or
        #    defaultSystemCommonDataDir.
        return self._GetCommonDataDirForVersion(self._ver_major,
                                                self._ver_minor)
        
    # XXX this code is duplicated in koPrefs.py since the global prefs
    # service needs the commonDataDir, but cannot access it via
    # koIDirs due to chicken-egg issue.  If you change this, change
    # koPrefs also!
    def get_commonDataDir(self):
        method = "default"
        try:
            globalPrefs = components.classes["@activestate.com/koPrefService;1"]\
                          .getService(components.interfaces.koIPrefService).prefs
            if globalPrefs.hasStringPref("commonDataDirMethod"):
                method = globalPrefs.getStringPref("commonDataDirMethod")
        except COMException:
            # Robustness: in some usages of koDirs early in the Komodo
            # build process, the prefs system might not be usable yet.
            pass

        if method not in ("default", "custom"):
            log.error("bogus Common Data Dir determination method, '%s', "
                      "falling back to default", method)
        if method == "default":
            return self.get_factoryCommonDataDir()
        elif method == "custom":
            return globalPrefs.getStringPref("customCommonDataDir")

    def get_mozBinDir(self):
        # By definition this is the directory of the main komodo/mozilla
        # executable. 'koDirs.py' is in the components directory, always one
        # dir under the moz bin dir.
        return dirname(dirname(__file__))

    __isDevTreeCache = None
    def _isDevTree(self):
        """Return true if this Komodo is running in a dev tree layout."""
        if self.__isDevTreeCache is None:
            landmark = os.path.join(self.get_mozBinDir(), "is_dev_tree.txt")
            self.__isDevTreeCache = os.path.isfile(landmark)
        return self.__isDevTreeCache

    def _getKomodoBitsDir(self):
        """Return the path to the "komodo-bits" dir in a dev tree.
        
        Note: this only makes sense if _isDevTree() is true.
        """
        if sys.platform == "darwin":
            # mozBinDir:     $mozSrc/mozilla/dist/Komodo.app/Contents/MacOS
            # komodoBitsDir: $mozSrc/mozilla/dist/komodo-bits
            komodoBitsDir = normpath(join(self.get_mozBinDir(),
                                     os.pardir, os.pardir, os.pardir,
                                     "komodo-bits"))
        else:
            # mozBinDir:     $mozSrc/mozilla/dist/bin
            # komodoBitsDir: $mozSrc/mozilla/dist/komodo-bits
            komodoBitsDir = join(dirname(self.get_mozBinDir()),
                                 "komodo-bits")
        return komodoBitsDir

    def get_supportDir(self):
        if self._isDevTree(): # in a development tree
            supportDir = join(self._getKomodoBitsDir(), "support")
        else:
            if sys.platform == "darwin":
                # mozBinDir:  /Applications/Komodo.app/Contents/MacOS
                # supportDir: /Applications/Komodo.app/Contents/SharedSupport
                supportDir = join(dirname(self.get_mozBinDir()),
                                  "SharedSupport")
            else:
                # mozBinDir:  <installdir>/lib/mozilla
                # supportDir: <installdir>/lib/support
                supportDir = join(dirname(self.get_mozBinDir()), "support")
        return supportDir

    def get_sdkDir(self):
        if self._isDevTree(): # in a development tree
            sdkDir = join(self._getKomodoBitsDir(), "sdk")
        else:
            if sys.platform == "darwin":
                sdkDir = join(self.get_supportDir(), "sdk")
            else:
                # mozBinDir: <installdir>/lib/mozilla
                # sdkDir:    <installdir>/lib/sdk
                sdkDir = join(dirname(self.get_mozBinDir()), "sdk")
        return sdkDir

    def get_docDir(self):
        if self._isDevTree(): # in a development tree
            docDir = join(self._getKomodoBitsDir(), "doc")
        else:
            if sys.platform == "win32":
                # mozBinDir: <installdir>/lib/mozilla
                # docDir:    <installdir>/doc
                docDir = join(dirname(dirname(self.get_mozBinDir())), "doc")
            elif sys.platform == "darwin":
                # mozBinDir: /Applications/Komodo.app/Contents/MacOS
                # docDir:    /Applications/Komodo.app/Contents/Resources/en.lproj/KomodoHelp
                docDir = join(dirname(self.get_mozBinDir()),
                              "Resources", "en.lproj", "KomodoHelp")
            else:
                # mozBinDir: <installdir>/lib/mozilla
                # docDir:    <installdir>/share/doc
                docDir = join(dirname(dirname(self.get_mozBinDir())),
                              "share", "doc")
        return docDir

    def get_installDir(self):
        # mozBinDir (Mac OS X): <installdir>/Contents/MacOS
        # mozBinDir (others):   <installdir>/lib/mozilla
        installDir = dirname(dirname(self.get_mozBinDir()))
        return installDir

    def get_binDir(self):
        if self._isDevTree(): # in a development tree
            binDir = join(self._getKomodoBitsDir(), "stub")
        else:
            if sys.platform == "win32":
                binDir = self.get_installDir()
            elif sys.platform == "darwin":
                binDir = self.get_mozBinDir()
            else:
                binDir = join(self.get_installDir(), "bin")
        return binDir

#XXX Coming later. See specs/tech/install_layout.txt
##    def get_etcDir(self):
##    def get_docDir(self):

    def get_pythonExe(self):
        if sys.platform == "darwin":
            # mozBinDir:
            #   $mozSrc/mozilla/dist/Komodo.app/Contents/MacOS (dev build)
            #   $installDir/Contents/MacOS (installation)
            # pythonExe:
            #   $mozSrc/mozilla/dist/Komodo.app/Contents/MacOS/mozpython (dev build)
            #   $installDir/Contents/MacOS/mozpython (installation)
            # See bug 84584: On OSX if we're going to launch Komodo's python,
            # we need to make sure it finds the siloed python lib.
            pythonExe = join(self.get_mozBinDir(), "mozpython")
        elif sys.platform == "win32":
            # mozBinDir:
            #   $mozSrc/mozilla/dist/bin (dev build)
            #   $installDir/lib/mozilla (installation)
            # pythonExe:
            #   $mozSrc/mozilla/dist/python/python.exe (dev build)
            #   $installDir/lib/python/python.exe (installation)
            pythonExe = join(dirname(self.get_mozBinDir()),
                             "python", "python.exe")
        else:
            # mozBinDir:
            #   $mozSrc/mozilla/dist/bin (dev build)
            #   $installDir/lib/mozilla (installation)
            # pythonExe:
            #   $mozSrc/mozilla/dist/python/bin/python (dev build)
            #   $installDir/lib/python/bin/python (installation)
            pythonExe = join(dirname(self.get_mozBinDir()),
                             "python", "bin", "python")
        return pythonExe

    def get_komodoPythonLibDir(self):
        return join(self.get_mozBinDir(), "python", "komodo")
    def get_binDBGPDir(self):
        return os.path.join(self.get_supportDir(), "dbgp", "bin")
    def get_perlDBGPDir(self):
        return os.path.join(self.get_supportDir(), "dbgp", "perllib")
    def get_pythonDBGPDir(self):
        return os.path.join(self.get_supportDir(), "dbgp", "pythonlib")
    def get_python3DBGPDir(self):
        return os.path.join(self.get_supportDir(), "dbgp", "python3lib")


if __name__ == "__main__":
    koDirSvc = components.classes['@activestate.com/koDirs;1']\
               .getService(components.interfaces.koIDirs)
    dnames = ["userDataDir", "commonDataDir",
              "factoryCommonDataDir", "supportDir", "mozBinDir",
              "binDBGPDir", "perlDBGPDir", "pythonDBGPDir"]
    for dname in dnames:
        try:
            print "koIDirs.%s: %s" % (dname, getattr(koDirSvc, dname))
        except:
            print "koIDirs.%s: <error retrieving>" % dname

