/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

const Cc = Components.classes;
const Ci = Components.interfaces;
const CC = Components.Constructor;
const Cu = Components.utils;

Cu.import("resource://gre/modules/Services.jsm");

this.EXPORTED_SYMBOLS = ["WebappOSUtils"];

this.WebappOSUtils = {
  launch: function(aData) {
//@line 59 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/webapps/WebappOSUtils.jsm"
    let origin = Services.io.newURI(aData.origin, null, null);
    let installDir = "." + origin.scheme + ";" +
                     origin.host +
                     (origin.port != -1 ? ";" + origin.port : "");

    let exeFile = Services.dirsvc.get("Home", Ci.nsIFile);
    exeFile.append(installDir);
    exeFile.append("webapprt-stub");

    try {
      if (exeFile.exists()) {
        let process = Cc["@mozilla.org/process/util;1"]
                        .createInstance(Ci.nsIProcess);
        process.init(exeFile);
        process.runAsync([], 0);
        return true;
      }
    } catch (e) {}

    return false;
//@line 80 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/webapps/WebappOSUtils.jsm"
  },

  uninstall: function(aData) {
//@line 85 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/webapps/WebappOSUtils.jsm"
    let origin = Services.io.newURI(aData.origin, null, null);
    let installDir = "." + origin.scheme + ";" +
                     origin.host +
                     (origin.port != -1 ? ";" + origin.port : "");

    let exeFile = Services.dirsvc.get("Home", Ci.nsIFile);
    exeFile.append(installDir);
    exeFile.append("webapprt-stub");

    try {
      if (exeFile.exists()) {
        var process = Cc["@mozilla.org/process/util;1"].createInstance(Ci.nsIProcess);
        process.init(exeFile);
        process.runAsync(["-remove"], 1);
        return true;
      }
    } catch(e) {}

    return false;
//@line 106 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/webapps/WebappOSUtils.jsm"
  }
}
