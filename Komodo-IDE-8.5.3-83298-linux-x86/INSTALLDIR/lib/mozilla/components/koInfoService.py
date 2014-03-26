#!python
# Copyright (c) 2000-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

"""Provide general (read-only) information about a Komodo
build/installation.
"""





import sys
import os
import re
import time
import logging
import operator

from xpcom import components, nsError, ServerException, COMException



log = logging.getLogger("koInfoService")



class KoInfoService(object):
    _com_interfaces_ = [components.interfaces.koIInfoService,
                        components.interfaces.nsITimerCallback]
    _reg_clsid_ = "{EB22F329-1D99-427a-B0E1-19DFF13AFBF7}"
    _reg_contractid_ = "@activestate.com/koInfoService;1"
    _reg_desc_ = "Komodo Information Service"

    version = "8.5.3"
    buildNumber = "83298"
    buildASCTime = "Mon Nov 18 17:06:01 2013"
    buildPlatform = "linux-x86"
    #TODO: Drop mozBinDir here, only used as a "stamp" (?) in
    #      koFileLoggingService.py. koIDirs has the authoritative mozBinDir.
    mozBinDir = "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/ko-8.5.x/dist/bin"
    buildType = "release"
    buildFlavour = "full"
    productType = "ide"
    prettyProductType = "IDE"
    releaseYear = "2013"
    releaseMonth = "9"
    releaseDay = "1"

    siloedLicense = operator.truth(0)
    siloedLicenseExpires = operator.truth(0)
    siloedLicenseExpirationTime = 0

    def __init__(self):
        self.platform = sys.platform
        
        #TODO: Drop all these. They aren't necessary.
        self.isWindows = sys.platform.startswith("win")
        # XXX bug 33823
        # when building with gtk2, platform.py functions fail preventing
        # komodo startup.  os.uname should work fine on *nix platforms.
        if sys.platform.startswith("win"):
            import platform
            self.osSystem = platform.system()
            self.osRelease = platform.release()
            self.osVersion = platform.version()
        else:
            self.osSystem,node,self.osRelease,self.osVersion,machine = os.uname()
        # We are in non-interactive mode if KOMODO_NONINTERACTIVE is set
        # and non-zero.
        KOMODO_NONINTERACTIVE = os.environ.get("KOMODO_NONINTERACTIVE")
        self.nonInteractiveMode = 0
        if KOMODO_NONINTERACTIVE:
            try:
                KOMODO_NONINTERACTIVE = int(KOMODO_NONINTERACTIVE)
            except ValueError:
                pass
            if KOMODO_NONINTERACTIVE:
                self.nonInteractiveMode = 1

        self.refreshLicenseInfo()
        self._usedWindowNums = set()
        self._nextAvailWindowNum = 1

    # Note: an XPCOM category is installed via the Conscript, so that
    #       nsIUpdateTimerManager will call this method every 12 hours.
    def notify(self, timer):
        """nsIUpdateTimerManager callback"""
        days = self.daysUntilExpiration
        self.refreshLicenseInfo()
        if days != self.daysUntilExpiration:
            obsSvc = components.classes["@mozilla.org/observer-service;1"]. \
                            getService(components.interfaces.nsIObserverService)
            obsSvc.notifyObservers(None, "license_daysUntilExpiration_changed", "")

    @components.ProxyToMainThread
    def refreshLicenseInfo(self):
        """Redetermine all information relating to the installed ActiveState
        license keys.
        """
        licSvc = components.classes["@activestate.com/koLicenseInfo;8"]\
            .getService(components.interfaces.koILicenseInfo)
        rv, self.featureName, feature = licSvc.status()
        self.licenseStatus = rv
        self.licenseValid = self.licenseStatus <= licSvc.LIC_TRIAL
        if feature:
            self.licensee = licSvc.fetchValue(feature, "Licensee")
            self.licenseUserName = licSvc.fetchValue(feature, "UserName")
            self.licenseType = licSvc.fetchValue(feature, "LicenseType")
            self.licenseToken = licSvc.fetchValue(feature, "Token")
            self.licenseSerialNo = licSvc.fetchValue(feature, "SerialNo")
            self.daysUntilExpiration = licSvc.daysUntil(feature,
                                                        "ExpirationDate")
            if self.daysUntilExpiration == 9999:
                self.expires = 0
                self.expirationDate = None
            else:
                self.expires = 1
                expirationDate = licSvc.fetchValue(feature,
                                                   "ExpirationDate")
                self.expirationDate = time.strftime("%a %b %d, %Y",
                    time.strptime(expirationDate, "%d-%m-%Y"))

            # Make a nice description of the license status for the user.
            if self.daysUntilExpiration and abs(self.daysUntilExpiration) == 1:
                days = "day"
            else:
                days = "days"
            if self.licenseStatus in (licSvc.LIC_PERPETUAL,
                                      licSvc.LIC_TRIAL,
                                      licSvc.LIC_EXPIRED):
                details = ["%s license" % self.licenseType]
                if self.licenseSerialNo:
                    details.append("serial number %s" % self.licenseSerialNo)
                if not (self.licenseUserName or self.licensee):
                    licensedTo = ", ".join(details) + "."
                else:
                    licensedTo = "Licensed to %s (%s)."\
                                  % (self.licenseUserName or self.licensee,
                                     ", ".join(details))
            else:
                licensedTo = None

            if self.licenseStatus <= licSvc.LIC_TRIAL:
                self.licenseInfo = licensedTo
                if self.expires:
                    self.licenseInfo += " Expires on %s (%d %s left)."\
                                        % (self.expirationDate,
                                           self.daysUntilExpiration, days)
            elif self.licenseStatus == licSvc.LIC_EXPIRED:
                self.licenseInfo = "License has expired. %s Expired on %s (%r %s ago)."\
                    % (licensedTo, self.expirationDate, -self.daysUntilExpiration, days)
            elif self.licenseStatus == licSvc.LIC_NOTCOVERED:
                self.licenseInfo = "Your license does not cover this version of Komodo."
            elif self.licenseStatus == licSvc.LIC_NOFEATURE:
                self.licenseInfo = "Your ActiveState license does not include a Komodo license."
            elif self.licenseStatus == licSvc.LIC_NOFILE:
                self.licenseInfo = "No ActiveState license file could be found."
            elif self.licenseStatus == licSvc.LIC_ENDOFBETA:
                self.licenseInfo = "The beta period for this release has expired."

        else:
            # We don't have a feature. This either means that there is
            # no license for this Komodo or a "Trial" license has expired
            # (we don't get the feature in the latter case).
            
            # These are all technically "not applicable", but some of
            # them we set to values of the correct type so that
            # accidental usage will lead to more graceful failure.
            self.expires = True
            self.daysUntilExpiration = 0
            self.expirationDate = None
            self.licensee = None        #TODO: not used, consider dropping
            self.licenseUserName = None #TODO: not used, consider dropping
            self.licenseType = None
            self.licenseToken = None    #TODO: not used, consider dropping
            self.licenseSerialNo = None #TODO: not used, consider dropping

            self.licenseInfo = {
                licSvc.LIC_TRIAL: "Licensed.",
                licSvc.LIC_EXPIRED: "License has expired.",
                licSvc.LIC_NOTCOVERED: "Your license does not cover this version of Komodo.",
                licSvc.LIC_NOFEATURE: "Your ActiveState license does not include a Komodo license.",
                licSvc.LIC_NOFILE: "No ActiveState license file could be found.",
                licSvc.LIC_ENDOFBETA: "The beta period for this release has expired.",
            }.get(self.licenseStatus, "")

    def get_siloedLicenseExpired(self):
        if not self.siloedLicense:
            return 0
        elif not self.siloedLicenseExpires:
            return 0
        else:
            return time.time() > self.siloedLicenseExpirationTime

    def get_siloedLicenseDaysUntilExpiration(self):
        if not self.siloedLicense and not self.siloedLicenseExpires:
            raise ServerException(nsError.NS_ERROR_FAILURE)
        else:
            secs = self.siloedLicenseExpirationTime - time.time()
            import math
            days = math.floor(secs / 60.0 / 60.0 / 24.0)
            return days
        
    def nextWindowNum(self):
        loadedWindowNums = []
        prefs = components.classes["@activestate.com/koPrefService;1"].\
                        getService(components.interfaces.koIPrefService).prefs
        if prefs.hasPref("windowWorkspace"):
            windowWorkspacePrefs = prefs.getPref("windowWorkspace")
            # Get only numbered members of the windowWorkspace pref (bug 97717)
            prefIds = [x for x in windowWorkspacePrefs.getPrefIds() if
                       all([y.isdigit() for y in x])]
            for prefId in prefIds:
                try:
                    pref = windowWorkspacePrefs.getPref(prefId)
                    if pref.hasLongPref('windowNum'):
                        try:
                            windowNum = pref.getLongPref('windowNum')
                            loadedWindowNums.append(windowNum)
                        except:
                            log.exception("nextWindowNum: can't get window # for workspace %r",
                                          prefId)
                except:
                    log.exception("nextWindowNum: can't get pref windowWorkspace/%s", prefId)
        retVal = self._nextAvailWindowNum
        if retVal in self._usedWindowNums:
            while True:
                retVal += 1
                if retVal not in self._usedWindowNums:
                    break
                elif retVal not in loadedWindowNums:
                    break
        self._usedWindowNums.add(retVal)
        self._nextAvailWindowNum = retVal + 1
        return retVal
        
    def setUsedWindowNum(self, val):
        if val in self._usedWindowNums:
            raise ServerException(nsError.NS_ERROR_FAILURE,
                                  "setUsedWindowNum: %d already in use" % val)
        self._usedWindowNums.add(val)

if __name__ == "__main__":
    info = components.classes['@activestate.com/koInfoService;1'].\
        getService(components.interfaces.koIInfoService)
    print "platform: %r" % info.platform
    print "osSystem: %r" % info.osSystem
    print "osRelease: %r" % info.osRelease
    print "osVersion: %r" % info.osVersion
    print "version: %r" % info.version
    print "buildNumber: %r" % info.buildNumber
    print "buildASCTime: %r" % info.buildASCTime
    print "buildType: %r" % info.buildType
    print "buildFlavour: %r" % info.buildFlavour
    print "productType: %r" % info.productType
    print "nonInteractiveMode: %r" % info.nonInteractiveMode
    print "licenseValid: %r" % info.licenseValid
    print "licenseInfo: %r" % info.licenseInfo
    print "siloedLicense: %r" % info.siloedLicense
    print "siloedLicenseExpires: %r" % info.siloedLicenseExpires
    if info.siloedLicenseExpires:
        print "siloedLicenseExpired: %r" % info.siloedLicenseExpired
        print "siloedLicenseExpirationTime: %r" % info.siloedLicenseExpirationTime
        print "siloedLicenseDaysUntilExpiration: %r" % info.siloedLicenseDaysUntilExpiration

        print "expires: %r" % info.expires
        print "daysUntilExpiration: %r" % info.daysUntilExpiration
        print "expirationDate: %r" % info.expirationDate
    print "licensee: %r" % info.licensee
    print "licenseUserName: %r" % info.licenseUserName
    print "licenseType: %r" % info.licenseType
    print "licenseStatus: %r" % info.licenseStatus

