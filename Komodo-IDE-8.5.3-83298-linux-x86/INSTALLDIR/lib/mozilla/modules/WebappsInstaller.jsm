/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

this.EXPORTED_SYMBOLS = ["WebappsInstaller"];

const Cc = Components.classes;
const Ci = Components.interfaces;
const Cu = Components.utils;
const Cr = Components.results;

Cu.import("resource://gre/modules/Services.jsm");
Cu.import("resource://gre/modules/FileUtils.jsm");
Cu.import("resource://gre/modules/NetUtil.jsm");
Cu.import("resource://gre/modules/osfile.jsm");

this.WebappsInstaller = {
  /**
   * Creates a native installation of the web app in the OS
   *
   * @param aData the manifest data provided by the web app
   *
   * @returns bool true on success, false if an error was thrown
   */
  install: function(aData) {

    try {
      if (Services.prefs.getBoolPref("browser.mozApps.installer.dry_run")) {
        return true;
      }
    } catch (ex) {}

//@line 38 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/webapps/WebappsInstaller.jsm"
    let shell = new LinuxNativeApp(aData);
//@line 42 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/webapps/WebappsInstaller.jsm"

    try {
      shell.install();
    } catch (ex) {
      Cu.reportError("Error installing app: " + ex);
      return null;
    }

    let data = {
      "installDir": shell.installDir.path,
      "app": aData.app
    };
    Services.obs.notifyObservers(null, "webapp-installed", JSON.stringify(data));

    return shell;
  }
}

/**
 * This function implements the common constructor for
 * the Windows, Mac and Linux native app shells. It reads and parses
 * the data from the app manifest and stores it in the NativeApp
 * object. It's meant to be called as NativeApp.call(this, aData)
 * from the platform-specific constructor.
 *
 * @param aData the data object provided by the web app with
 *              all the app settings and specifications.
 *
 */
function NativeApp(aData) {
  let app = this.app = aData.app;

  let origin = Services.io.newURI(app.origin, null, null);

  if (app.manifest.launch_path) {
    this.launchURI = Services.io.newURI(origin.resolve(app.manifest.launch_path),
                                        null, null);
  } else {
    this.launchURI = origin.clone();
  }

  let biggestIcon = getBiggestIconURL(app.manifest.icons);
  try {
    let iconURI = Services.io.newURI(biggestIcon, null, null);
    if (iconURI.scheme == "data") {
      this.iconURI = iconURI;
    }
  } catch (ex) {}

  if (!this.iconURI) {
    try {
      this.iconURI = Services.io.newURI(origin.resolve(biggestIcon), null, null);
    }
    catch (ex) {}
  }

  this.appName = sanitize(app.manifest.name);
  this.appNameAsFilename = stripStringForFilename(this.appName);

  if(app.manifest.developer && app.manifest.developer.name) {
    let devName = app.manifest.developer.name.substr(0, 128);
    devName = sanitize(devName);
    if (devName) {
      this.developerName = devName;
    }
  }

  let shortDesc = this.appName;
  if (app.manifest.description) {
    let firstLine = app.manifest.description.split("\n")[0];
    shortDesc = firstLine.length <= 256
                ? firstLine
                : firstLine.substr(0, 253) + "...";
  }
  this.shortDescription = sanitize(shortDesc);

  // The app registry is the Firefox profile from which the app
  // was installed.
  this.registryFolder = Services.dirsvc.get("ProfD", Ci.nsIFile);

  this.webappJson = {
    "registryDir": this.registryFolder.path,
    "app": app
  };

  this.runtimeFolder = Services.dirsvc.get("GreD", Ci.nsIFile);
}

//@line 661 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/webapps/WebappsInstaller.jsm"

function LinuxNativeApp(aData) {
  NativeApp.call(this, aData);
  this._init();
}

LinuxNativeApp.prototype = {
  _init: function() {
    // The ${InstallDir} and desktop entry filename format is as follows:
    // host of the app origin + ";" +
    // protocol
    // + ";" + port (only if port is not default)

    this.uniqueName = this.launchURI.scheme + ";" + this.launchURI.host;
    if (this.launchURI.port != -1)
      this.uniqueName += ";" + this.launchURI.port;

    this.installDir = Services.dirsvc.get("Home", Ci.nsIFile);
    this.installDir.append("." + this.uniqueName);

    this.iconFile = this.installDir.clone();
    this.iconFile.append("icon.png");

    this.webapprt = this.installDir.clone();
    this.webapprt.append("webapprt-stub");

    this.configJson = this.installDir.clone();
    this.configJson.append("webapp.json");

    this.webappINI = this.installDir.clone();
    this.webappINI.append("webapp.ini");

    let env = Cc["@mozilla.org/process/environment;1"]
                .getService(Ci.nsIEnvironment);
    let xdg_data_home_env = env.get("XDG_DATA_HOME");
    if (xdg_data_home_env != "") {
      this.desktopINI = Cc["@mozilla.org/file/local;1"]
                          .createInstance(Ci.nsILocalFile);
      this.desktopINI.initWithPath(xdg_data_home_env);
    }
    else {
      this.desktopINI = Services.dirsvc.get("Home", Ci.nsIFile);
      this.desktopINI.append(".local");
      this.desktopINI.append("share");
    }

    this.desktopINI.append("applications");
    this.desktopINI.append("owa-" + this.uniqueName + ".desktop");
  },

  install: function() {
    this._removeInstallation(true);

    try {
      this._createDirectoryStructure();
      this._copyPrebuiltFiles();
      this._createConfigFiles();
      this._createAppProfile();
    } catch (ex) {
      this._removeInstallation(false);
      throw(ex);
    }

    getIconForApp(this, function() {});
  },

  _removeInstallation: function(keepProfile) {
    let filesToRemove = [this.desktopINI];

    if (keepProfile) {
      filesToRemove.push(this.iconFile);
      filesToRemove.push(this.webapprt);
      filesToRemove.push(this.configJson);
      filesToRemove.push(this.webappINI);
    } else {
      filesToRemove.push(this.installDir);
    }

    removeFiles(filesToRemove);
  },

  _createDirectoryStructure: function() {
    if (!this.installDir.exists())
      this.installDir.create(Ci.nsIFile.DIRECTORY_TYPE, 0755);
  },

  _copyPrebuiltFiles: function() {
    let webapprtPre = this.runtimeFolder.clone();
    webapprtPre.append(this.webapprt.leafName);
    webapprtPre.copyTo(this.installDir, this.webapprt.leafName);
  },

  _createAppProfile: function() {
    let profSvc = Cc["@mozilla.org/toolkit/profile-service;1"]
                    .getService(Ci.nsIToolkitProfileService);

    try {
      this.appProfile = profSvc.createDefaultProfileForApp(this.installDir.leafName,
                                                           null, null);
    } catch (ex if ex.result == Cr.NS_ERROR_ALREADY_INITIALIZED) {}
  },

  /**
   * Translate marketplace categories to freedesktop.org categories.
   *
   * @link http://standards.freedesktop.org/menu-spec/menu-spec-latest.html#category-registry
   *
   * @return an array of categories
   */
  _translateCategories: function() {
    let translations = {
      "books-reference": "Education;Literature",
      "business": "Finance",
      "education": "Education",
      "entertainment-sports": "Amusement;Sports",
      "games": "Game",
      "health-fitness": "MedicalSoftware",
      "lifestyle": "Amusement",
      "music": "Audio;Music",
      "news-weather": "News",
      "photos-media": "AudioVideo",
      "productivity": "Office",
      "shopping": "Amusement",
      "social": "Chat",
      "travel": "Amusement",
      "utilities": "Utility"
    };

    // The trailing semicolon is needed as written in the freedesktop specification
    let categories = "";
    for (let category of this.app.categories) {
      let catLower = category.toLowerCase();
      if (catLower in translations) {
        categories += translations[catLower] + ";";
      }
    }

    return categories;
  },

  _createConfigFiles: function() {
    // ${InstallDir}/webapp.json
    writeToFile(this.configJson, JSON.stringify(this.webappJson));

    let factory = Cc["@mozilla.org/xpcom/ini-processor-factory;1"]
                    .getService(Ci.nsIINIParserFactory);

    let webappsBundle = Services.strings.createBundle("chrome://global/locale/webapps.properties");

    // ${InstallDir}/webapp.ini
    let writer = factory.createINIParser(this.webappINI).QueryInterface(Ci.nsIINIParserWriter);
    writer.setString("Webapp", "Name", this.appName);
    writer.setString("Webapp", "Profile", this.uniqueName);
    writer.setString("Webapp", "UninstallMsg", webappsBundle.formatStringFromName("uninstall.notification", [this.appName], 1));
    writer.setString("WebappRT", "InstallDir", this.runtimeFolder.path);
    writer.writeFile();

    // $XDG_DATA_HOME/applications/owa-<webappuniquename>.desktop
    this.desktopINI.create(Ci.nsIFile.NORMAL_FILE_TYPE, 0755);

    writer = factory.createINIParser(this.desktopINI).QueryInterface(Ci.nsIINIParserWriter);
    writer.setString("Desktop Entry", "Name", this.appName);
    writer.setString("Desktop Entry", "Comment", this.shortDescription);
    writer.setString("Desktop Entry", "Exec", '"'+this.webapprt.path+'"');
    writer.setString("Desktop Entry", "Icon", this.iconFile.path);
    writer.setString("Desktop Entry", "Type", "Application");
    writer.setString("Desktop Entry", "Terminal", "false");

    let categories = this._translateCategories();
    if (categories)
      writer.setString("Desktop Entry", "Categories", categories);

    writer.setString("Desktop Entry", "Actions", "Uninstall;");
    writer.setString("Desktop Action Uninstall", "Name", webappsBundle.GetStringFromName("uninstall.label"));
    writer.setString("Desktop Action Uninstall", "Exec", this.webapprt.path + " -remove");

    writer.writeFile();
  },

  /**
   * This variable specifies if the icon retrieval process should
   * use a temporary file in the system or a binary stream. This
   * is accessed by a common function in WebappsIconHelpers.js and
   * is different for each platform.
   */
  useTmpForIcon: false,

  /**
   * Process the icon from the imageStream as retrieved from
   * the URL by getIconForApp().
   *
   * @param aMimeType     ahe icon mimetype
   * @param aImageStream  the stream for the image data
   * @param aCallback     a callback function to be called
   *                      after the process finishes
   */
  processIcon: function(aMimeType, aImageStream, aCallback) {
    let iconStream;
    try {
      let imgTools = Cc["@mozilla.org/image/tools;1"]
                       .createInstance(Ci.imgITools);
      let imgContainer = { value: null };

      imgTools.decodeImageData(aImageStream, aMimeType, imgContainer);
      iconStream = imgTools.encodeImage(imgContainer.value, "image/png");
    } catch (e) {
      throw("processIcon - Failure converting icon (" + e + ")");
    }

    let outputStream = FileUtils.openSafeFileOutputStream(this.iconFile);
    NetUtil.asyncCopy(iconStream, outputStream);
  }
}

//@line 876 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/webapps/WebappsInstaller.jsm"

/* Helper Functions */

/**
 * Async write a data string into a file
 *
 * @param aFile     the nsIFile to write to
 * @param aData     a string with the data to be written
 */
function writeToFile(aFile, aData) {
  let path = aFile.path;
  let data = new TextEncoder().encode(aData);
  return OS.File.writeAtomic(path, data, { tmpPath: path + ".tmp" });
}

/**
 * Removes unprintable characters from a string.
 */
function sanitize(aStr) {
  let unprintableRE = new RegExp("[\\x00-\\x1F\\x7F]" ,"gi");
  return aStr.replace(unprintableRE, "");
}

/**
 * Strips all non-word characters from the beginning and end of a string
 */
function stripStringForFilename(aPossiblyBadFilenameString) {
  //strip everything from the front up to the first [0-9a-zA-Z]

  let stripFrontRE = new RegExp("^\\W*","gi");
  let stripBackRE = new RegExp("\\s*$","gi");

  let stripped = aPossiblyBadFilenameString.replace(stripFrontRE, "");
  stripped = stripped.replace(stripBackRE, "");
  return stripped;
}

/**
 * Finds a unique name available in a folder (i.e., non-existent file)
 *
 * @param aFolder nsIFile that represents the directory where we want to write
 * @param aName   string with the filename (minus the extension) desired
 * @param aExtension string with the file extension, including the dot

 * @return nsILocalFile or null if folder is unwritable or unique name
 *         was not available
 */
function getAvailableFile(aFolder, aName, aExtension) {
  let folder = aFolder.QueryInterface(Ci.nsILocalFile);
  folder.followLinks = false;
  if (!folder.isDirectory() || !folder.isWritable()) {
    return null;
  }

  let file = folder.clone();
  file.append(aName + aExtension);

  if (!file.exists()) {
    return file;
  }

  for (let i = 2; i < 10; i++) {
    file.leafName = aName + " (" + i + ")" + aExtension;
    if (!file.exists()) {
      return file;
    }
  }

  for (let i = 10; i < 100; i++) {
    file.leafName = aName + "-" + i + aExtension;
    if (!file.exists()) {
      return file;
    }
  }

  return null;
}

/**
 * Attempts to remove files or directories.
 *
 * @param aFiles An array with nsIFile objects to be removed
 */
function removeFiles(aFiles) {
  for (let file of aFiles) {
    try {
      if (file.exists()) {
        file.followLinks = false;
        file.remove(true);
      }
    } catch(ex) {}
  }
}

function escapeXML(aStr) {
  return aStr.toString()
             .replace(/&/g, "&amp;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&apos;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;");
}

/* More helpers for handling the app icon */
/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

/**
 * This function receives a list of icon sizes
 * and URLs and returns the url string for the biggest icon.
 *
 * @param aIcons An object where the keys are the icon sizes
 *               and the values are URL strings. E.g.:
 *               aIcons = {
 *                 "16": "http://www.example.org/icon16.png",
 *                 "32": "http://www.example.org/icon32.png"
 *               };
 *
 * @returns the URL string for the largest specified icon
 */
function getBiggestIconURL(aIcons) {
  if (!aIcons) {
    return "chrome://browser/skin/webapps-64.png";
  }

  let iconSizes = Object.keys(aIcons);
  if (iconSizes.length == 0) {
    return "chrome://browser/skin/webapps-64.png";
  }
  iconSizes.sort(function(a, b) a - b);
  return aIcons[iconSizes.pop()];
}

/**
 * This function retrieves the icon for an app as specified
 * in the iconURI on the shell object.
 * Upon completion it will call aShell.processIcon()
 *
 * @param aShell The shell that specifies the properties
 *               of the native app. Three properties from this
 *               shell will be used in this function:
 *                 - iconURI
 *                 - useTmpForIcon
 *                 - processIcon()
 */
function getIconForApp(aShell, callback) {
  let iconURI = aShell.iconURI;
  let mimeService = Cc["@mozilla.org/mime;1"]
                      .getService(Ci.nsIMIMEService);

  let mimeType;
  try {
    let tIndex = iconURI.path.indexOf(";");
    if("data" == iconURI.scheme && tIndex != -1) {
      mimeType = iconURI.path.substring(0, tIndex);
    } else {
      mimeType = mimeService.getTypeFromURI(iconURI);
    }
  } catch(e) {
    throw("getIconFromURI - Failed to determine MIME type");
  }

  try {
    let listener;
    if(aShell.useTmpForIcon) {
      let downloadObserver = {
        onDownloadComplete: function(downloader, request, cx, aStatus, file) {
          // pass downloader just to keep reference around
          onIconDownloaded(aShell, mimeType, aStatus, file, callback, downloader);
        }
      };

      let tmpIcon = Services.dirsvc.get("TmpD", Ci.nsIFile);
      tmpIcon.append("tmpicon." + mimeService.getPrimaryExtension(mimeType, ""));
      tmpIcon.createUnique(Ci.nsIFile.NORMAL_FILE_TYPE, 0666);

      listener = Cc["@mozilla.org/network/downloader;1"]
                   .createInstance(Ci.nsIDownloader);
      listener.init(downloadObserver, tmpIcon);
    } else {
      let pipe = Cc["@mozilla.org/pipe;1"]
                   .createInstance(Ci.nsIPipe);
      pipe.init(true, true, 0, 0xffffffff, null);

      listener = Cc["@mozilla.org/network/simple-stream-listener;1"]
                   .createInstance(Ci.nsISimpleStreamListener);
      listener.init(pipe.outputStream, {
          onStartRequest: function() {},
          onStopRequest: function(aRequest, aContext, aStatusCode) {
            pipe.outputStream.close();
            onIconDownloaded(aShell, mimeType, aStatusCode, pipe.inputStream, callback);
         }
      });
    }

    let channel = NetUtil.newChannel(iconURI);
    let CertUtils = { };
    Cu.import("resource://gre/modules/CertUtils.jsm", CertUtils);
    // Pass true to avoid optional redirect-cert-checking behavior.
    channel.notificationCallbacks = new CertUtils.BadCertHandler(true);

    channel.asyncOpen(listener, null);
  } catch(e) {
    throw("getIconFromURI - Failure getting icon (" + e + ")");
  }
}

function onIconDownloaded(aShell, aMimeType, aStatusCode, aIcon, aCallback) {
  if (Components.isSuccessCode(aStatusCode)) {
    aShell.processIcon(aMimeType, aIcon, aCallback);
  } else {
    aCallback.call(aShell);
  }
}
