// Copyright (c) 2005-2006 ActiveState Software Inc.
// See the file LICENSE.txt for licensing information.
// adapted from browser/components/nsBrowserContentHandler.js

const licDialog = "chrome://komodo/content/dialogs/license.xul";
const winOptions = 



  "chrome,resizable=yes,menubar,toolbar,status,all";


const { classes: Cc, interfaces: Ci, utils: Cu } = Components;
Cu.import("resource://gre/modules/XPCOMUtils.jsm");

function shouldLoadURI(aURI) {
  if (aURI && !aURI.schemeIs("chrome"))
    return true;
	
  //log.warn("*** Preventing external load of chrome: URI into window\n");
  //log.warn("    Use -chrome <uri> instead\n");
  return false;
}

function resolveURIInternal(aCmdLine, aArgument) {
  var uri = aCmdLine.resolveURI(aArgument);

  if (!(uri instanceof Ci.nsIFileURL)) {
    return uri;
  }

  try {
    if (uri.file.exists())
      return uri;
  }
  catch (e) {
    Components.utils.reportError(e);
  }

  // We have interpreted the argument as a relative file URI, but the file
  // doesn't exist. Try URI fixup heuristics: see bug 290782.
 
  try {
    var urifixup = Cc["@mozilla.org/docshell/urifixup;1"]
                             .getService(Ci.nsIURIFixup);

    uri = urifixup.createFixupURI(aArgument, 0);
  }
  catch (e) {
    Components.utils.reportError(e);
  }

  return uri;
}

function openWindow(parent, url, target, features, args) {
    var wwatch = Cc["@mozilla.org/embedcomp/window-watcher;1"]
            .getService(Ci.nsIWindowWatcher);
    return wwatch.openWindow(parent, url, target, features, args);
}

// Duplicate of windowManager.js:windowManager_getMainWindow.
function getMostRecentWindow(aType) {
    var wm = Cc["@mozilla.org/appshell/window-mediator;1"]
            .getService(Ci.nsIWindowMediator);
    return wm.getMostRecentWindow(aType);
}

/* A modified copy of dialogs.js::dialog_internalError() to make
 * window launching work here.
 */
function _internalError(error, text)
{
    if (typeof(error) == 'undefined' || error == null)
        throw("Must specify 'error' argument to _internalError().");
    if (typeof(text) == 'undefined' || text == null)
        throw("Must specify 'text' argument to _internalError().");

    // Show the dialog.
    var args =  Cc["@mozilla.org/supports-array;1"]
           .createInstance(Ci.nsISupportsArray);
    var errorObj = Cc["@mozilla.org/supports-string;1"]
           .createInstance(Ci.nsISupportsString);
    errorObj.data = error;
    args.AppendElement(errorObj);
    var textObj = Cc["@mozilla.org/supports-string;1"]
            .createInstance(Ci.nsISupportsString);
    textObj.data = text;
    args.AppendElement(textObj);
    openWindow(null,
               "chrome://komodo/content/dialogs/internalError.xul",
               "_blank",
               "chrome,modal,titlebar",
               args);
}

// Check the current license validity and interact with the user accordingly.
//
//  "_mode" is an internal variable that should be used only for testing.
//
// This returns true iff the user's Komodo license is valid. Note that this
// method may involve installing a valid license as a side-effect.
//
function licenseValidOnStartup()
{
    /* We want to install a siloed license if:
     * 1. we have one; and
     * 2. doing so will make a licensing difference. Determining when it will
     *    make a difference is best left to the license installer to decide
     *    (e.g., see bug 80011).
     */
    var infoSvc = Components.classes["@activestate.com/koInfoService;1"].
          getService(Components.interfaces.koIInfoService);
    var prefSvc = Components.classes["@activestate.com/koPrefService;1"].
	  getService(Components.interfaces.koIPrefService);
    var installSiloedLic = infoSvc.siloedLicense && (
	    !infoSvc.licenseValid
	    /* Avoid unnecessary "your lic will expire in N days" dialogs (bug 87441) */
	    || infoSvc.daysUntilExpiration <= prefSvc.prefs.getLongPref("days_until_expiration_to_warn"));
    if (!installSiloedLic)
        return infoSvc.licenseValid;

    // we have a siloed license, try to install it now
    var osPathSvc = Components.classes["@activestate.com/koOsPath;1"].getService();
    var koDirSvc = Components.classes["@activestate.com/koDirs;1"].getService();
    var runSvc = Components.classes["@activestate.com/koRunService;1"].getService();

    var instlic;



    instlic = osPathSvc.join(koDirSvc.supportDir, "instlic");


    var cmd = '"'+instlic+'"';
    var outputObj = new Object();
    var errorObj = new Object();
    var retval = runSvc.RunAndCaptureOutput(cmd,
                                            null, // cwd
                                            null, // env
                                            null, // input
                                            outputObj, errorObj);
    if (retval) {
        var err = "Unexpected error installing license key.";
        _internalError(err, err+"\n\ncmd: "+cmd+
                             "\n\nstdout:\n"+outputObj.value+
                             "\n\nstderr:\n"+errorObj.value);
        throw err;
    }

    infoSvc.refreshLicenseInfo();
    return infoSvc.licenseValid;
}

function licenseInfoCallback() {}
licenseInfoCallback.prototype = {
    constructor: licenseInfoCallback,
    dialogCalled: false,
    trialDialog: function() {
        try {
        this.dialogCalled = true;
        var args =  Components.classes["@mozilla.org/supports-array;1"]
               .createInstance(Components.interfaces.nsISupportsArray);

        var paramBlock = 
            Components.classes["@mozilla.org/embedcomp/dialogparam;1"].
            createInstance(Components.interfaces.nsIDialogParamBlock);
        paramBlock.SetInt(0, Components.interfaces.koILicenseCallback.LICCB_ABORT);
        paramBlock.SetString(1, "new-trial");
        args.AppendElement(paramBlock);

        openWindow(null, licDialog,
                         "Komodo",
                         "chrome,modal=yes,titlebar",
                         args);
            // set the result
        } catch(e) {
          dump(e+"\n");
        }
        return paramBlock.GetInt(0);
    },
    QueryInterface : function(iid) {
      if (!iid.equals(Components.interfaces.nsISupports) &&
          !iid.equals(Components.interfaces.koILicenseCallback)) {
        throw Components.errors.NS_ERROR_NO_INTERFACE;
      }
      return this;
    }
}

/**
 * licenseTrialCheck
 *
 * set a callback for the trial dialog to appear and try refreshing
 * the license again.  If a trial is possible, licenseInfoCallback
 * will be called to show the dialog, otherwise, this install is no
 * longer eligible for a trial, and we need to show the expired dialog.
 */
function licenseTrialCheck()
{
    var infoSvc = Components.classes["@activestate.com/koInfoService;1"].
          getService(Components.interfaces.koIInfoService);
    var licInfo = Components.classes["@activestate.com/koLicenseInfo;8"]
                 .getService(Components.interfaces.koILicenseInfo);
    licInfo.reset();
    var callback = new licenseInfoCallback();
    licInfo.setCallback(callback);
    infoSvc.refreshLicenseInfo();
    return callback.dialogCalled;
}

function licenseCheck()
{
    try {
        var infoSvc = Components.classes["@activestate.com/koInfoService;1"].
              getService(Components.interfaces.koIInfoService);
        while (!licenseValidOnStartup()) {
            if (licenseTrialCheck()) {
                // first time install of a trial license
                if (infoSvc.licenseValid) {
                    generateLicenseHash(infoSvc);
                }
                return infoSvc.licenseValid;
            }
            // Fall through, the invalidLicense dialog will handle showing
            // the apropriate information.  The trial is now expired.

            var args =  Components.classes["@mozilla.org/supports-array;1"]
                   .createInstance(Components.interfaces.nsISupportsArray);
    
            var paramBlock = 
                Components.classes["@mozilla.org/embedcomp/dialogparam;1"].
                createInstance(Components.interfaces.nsIDialogParamBlock);
            paramBlock.SetInt(0, Components.interfaces.koILicenseCallback.LICCB_ABORT);
            args.AppendElement(paramBlock);
    
            openWindow(null, licDialog,
                             "Komodo",
                             "chrome,modal=yes,titlebar",
                             args);
            if (paramBlock.GetInt(0) == Components.interfaces.koILicenseCallback.LICCB_RETRY) {
                infoSvc.refreshLicenseInfo();
                continue;
            }
            return false;
        }
        generateLicenseHash(infoSvc);
    } catch(ex) {
        // We've already shown a dialog for this error.
        return false;
    }
    return true;
}

function generateLicenseHash(infoSvc) {
    /**
     * Convert a binary string (of octets) to a hexidecimal string
     * @param   {String} str Binary string; each character has a code point < 256
     * @returns {String} The hexidecimal string
     */
    function strToHex(str) {
      return str.split("")
                .map(function(c) ("00" + c.charCodeAt(0).toString(16)).substr(-2))
                .join("");
    }
    // Dump a hash of the license info into distribution.id.  This could be
    // using a better key, except that wouldn't actually work.  See
    // https://bugzilla.mozilla.org/show_bug.cgi?id=430235
    var hasher = Components.classes["@mozilla.org/security/hash;1"]
                           .createInstance(Components.interfaces.nsICryptoHash);
    hasher.init(Components.interfaces.nsICryptoHash.SHA1);
    // Note: licenseSerialNo can be null, such is the vase for a beta
    //       time-bomb license.
    var licenseNo = infoSvc.licenseSerialNo || "";
    var serialNo = licenseNo.split("").map(function(c) c.charCodeAt(0));
    hasher.update(serialNo, serialNo.length);
    // only supply _part_ of the hash; that's enough.
    var hash = strToHex(hasher.finish(false)).substr(0, 16);
    hasher.init(Components.interfaces.nsICryptoHash.SHA1);
    var licenseType = infoSvc.licenseType;
    if (licenseType == "Commercial" && !licenseNo.match("S[0-9A-F]{11}")) {
      // It's a site license - bug 98787.
      licenseType = "FGL";
    }
    hasher.update(licenseType.split("").map(function(c) c.charCodeAt(0)),
                  licenseType.length);
    // add the license type too. (this is a partial hash too, but since
    // there's a small set of possible values it's just obfuscation)
    hash += strToHex(hasher.finish(false)).substr(0,16);
    var prefs = Components.classes["@mozilla.org/preferences-service;1"]
                          .getService(Components.interfaces.nsIPrefService)
                          .getDefaultBranch(null);
    prefs.setCharPref("distribution.id", hash);
}

function komodoCmdLineHandler() {
  try {
    this._cleanupEnvironmentVariables();
  } catch (ex) {
    Components.utils.reportError(ex);
  }
}
komodoCmdLineHandler.prototype = {
  chromeURL : "chrome://komodo/content",

  /* nsICommandLineHandler */
  handle : function dch_handle(cmdLine) {
    if (!licenseCheck()) {
        cmdLine.preventDefault = true;
        return;
    }
    var urilist = [];
    try {
      var ar;
      while ((ar = cmdLine.handleFlagWithParam("url", false))) {
        urilist.push(resolveURIInternal(cmdLine, ar));
      }
    }
    catch (e) {
      Components.utils.reportError(e);
    }

    // Logging
    // Syntax: -log test:DEBUG -log foo:10,bar:20
    let {logging} = Components.utils.import("chrome://komodo/content/library/logging.js");
    while (null !== (ar = cmdLine.handleFlagWithParam("log", false))) {
      for (let pair of ar.split(",")) {
	let [name, level] = pair.split(":").concat("");
	if (level.length > 0) {
	  if (parseInt(level, 10) == level) {
	    logging.getLogger(name).setLevel(parseInt(level, 10));
	  } else if (("LOG_" + level) in logging) {
	    logging.getLogger(name).setLevel(logging["LOG_" + level]);
	  } else {
	    logging.getLogger("asCommandLineHandler")
	           .warn("Invalid logging level " + level + " for " + name);
	  }
	}
      }
    }

    var count = cmdLine.length;

    for (var i = 0; i < count; ++i) {
      var curarg = cmdLine.getArgument(i);
      if (curarg == "-file") {
	// Mac OS X passes this flag before the filename arguument when using
	// "open -a Komodo.app somefile.txt", see bug 86470. We just ignore this
	// flag and the filename will be opened in the next iteration.
	continue;
      } else if (curarg.match(/^-/)) {
        Components.utils.reportError("Warning: unrecognized command line flag " + curarg + "\n");
        // To emulate the pre-nsICommandLine behavior, we ignore
        // the argument after an unrecognized flag.
        ++i;
      } else {
        try {
          urilist.push(resolveURIInternal(cmdLine, curarg));
        }
        catch (e) {
          Components.utils.reportError("Error opening URI '" + curarg + "' from the command line: " + e + "\n");
        }
      }
    }

    var koWin = getMostRecentWindow("Komodo");
    if (urilist.length) {
      var obsvc = Cc["@mozilla.org/observer-service;1"].
            getService(Ci.nsIObserverService);
      var speclist = [];
      for (var uri in urilist) {
        if (shouldLoadURI(urilist[uri])) {
          // Ensure the URI is decoded, bug 72873.
          speclist.push(decodeURI(urilist[uri].spec));
        }
      }
      if (speclist.length) {
        if (speclist.length == 1) {
          speclist = speclist[0];
        } else {
          speclist = speclist.join("|");
        }
        if (!cmdLine.preventDefault && !koWin) {
          // if we couldn't load it in an existing window, open a new one
          var args =  Cc["@mozilla.org/supports-array;1"]
                 .createInstance(Ci.nsISupportsArray);
  
          var paramBlock = 
              Cc["@mozilla.org/embedcomp/dialogparam;1"].
              createInstance(Ci.nsIDialogParamBlock);
          paramBlock.SetString(0, speclist);
          args.AppendElement(paramBlock);

          openWindow(null, this.chromeURL, "_blank", winOptions, args);
          cmdLine.preventDefault = true; // stop the browser from handling this also
          return;
        }
        try {
            obsvc.notifyObservers(this, 'open-url', speclist);
        } catch(e) { /* exception if no listeners */ }
      }

    }
    else if (!cmdLine.preventDefault && !koWin) {
      openWindow(null, this.chromeURL, "_blank", winOptions);
      cmdLine.preventDefault = true; // stop the browser from handling this also
    }
  },

  /**
   * Selectively remove a few environment variables so they don't leak into
   * subprocesses (in particular, MOZ_NO_REMOTE affects Firefox if we attempt to
   * open a web page on Windows).  Note that we use the Komodo Python service
   * instead of the normal Mozilla one to make sure it's gone from Python's copy
   * too.  Also, we want a very small white list, since the user might have set
   * some of these on purpose.
   */
  _cleanupEnvironmentVariables: function cleanupEnvironmentVariables() {
    const kVarNames = [

                       // Note that _KOMODO_VERUSERDATADIR must not be removed
                       // on the Mac, otherwise add-on restart no longer works -
                       // bug 97625, bug 97908.
                       "_KOMODO_VERUSERDATADIR",


                       "_XRE_USERAPPDATADIR",
                       "MOZ_APP_RESTART", "MOZ_CRASHREPORTER_DATA_DIRECTORY",
                       "MOZ_CRASHREPORTER_DISABLE", "MOZ_CRASHREPORTER_NO_REPORT",
                       "MOZ_CRASHREPORTER_RESTART_ARG_0", "MOZ_LAUNCHED_CHILD",
                       "MOZ_NO_REMOTE", "NO_EM_RESTART",
                       "VERSIONER_PYTHON_PREFER_32_BIT", "VERSIONER_PYTHON_VERSION",
                       "XRE_BINARY_PATH", "XRE_PROFILE_LOCAL_PATH",
                       "XRE_PROFILE_NAME", "XRE_PROFILE_PATH",
                       "XRE_START_OFFLINE", "XUL_APP_FILE"];
    let pyenv = Cc["@activestate.com/koEnviron;1"].getService(Ci.koIEnviron);
    for (let name of kVarNames) {
      if (pyenv.has(name)) {
        pyenv.remove(name);
      }
    }
    // Wipe out PYTHONHOME too; see bug 83693.  Note that we don't touch what
    // Python sees here
    let environ = Cc["@mozilla.org/process/environment;1"]
                    .getService(Ci.nsIEnvironment);
    let koOS = Cc["@activestate.com/koOs;1"].getService(Ci.koIOs);
    let koDirs = Cc["@activestate.com/koDirs;1"].getService(Ci.koIDirs);
    let installDir = Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);
    installDir.initWithPath(koDirs.installDir);









    for (let key of ["LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH", "PYTHONPATH",
                     "PYTHONHOME", "LIBRARY_PATH", "LIBPATH"])
    {
      if (!environ.exists(key)) {
        continue;
      }
      let vals = environ.get(key).split(koOS.pathsep);
      vals = vals.filter(function(path) {
        try {
          let file = Cc["@mozilla.org/file/local;1"].createInstance(Ci.nsIFile);
          file.initWithPath(path);
          return !installDir.contains(file, true);
        } catch (ex) { /* ignore exception, keep the path */ }
        return true;
      });
      let value = vals.join(koOS.pathsep) || null;
      environ.set(key, value);
      if (!value) {
        // On Unix, setting they key to null does not remove it - bug 96589, so
        // we must remove it using a specific unsetenv call. Note that
        // os.unsetenv() will not affect os.environ, it's just a wrapper around
        // C's unsetenv (if it's available).
        koOS.unsetenv(key);
      }
    }
  },

  // XXX localize me... how?
  helpInfo : "Usage: komodo [-flags] [<url>]\n",

  classDescription: "komodoCmdLineHandler",
  classID: Components.ID("{07DCEAC7-31F6-11DA-BC61-000D935D3368}"),
  contractID: "@activestate.com/komodo/final-clh;1",
  QueryInterface: XPCOMUtils.generateQI([Ci.nsICommandLineHandler]),
  _xpcom_categories: [{category: "command-line-handler", entry: "m-komodo"}]
};

if ("generateNSGetFactory" in XPCOMUtils) {
    var NSGetFactory = XPCOMUtils.generateNSGetFactory([komodoCmdLineHandler]);
} else if ("generateNSGetModule" in XPCOMUtils) {
    var NSGetModule = XPCOMUtils.generateNSGetModule([komodoCmdLineHandler]);
}
