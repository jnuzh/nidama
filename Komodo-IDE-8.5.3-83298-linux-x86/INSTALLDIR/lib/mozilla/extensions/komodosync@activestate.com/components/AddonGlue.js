/* ***** BEGIN LICENSE BLOCK *****
 * Version: MPL 1.1/GPL 2.0/LGPL 2.1
 *
 * The contents of this file are subject to the Mozilla Public License Version
 * 1.1 (the "License"); you may not use this file except in compliance with
 * the License. You may obtain a copy of the License at
 * http://www.mozilla.org/MPL/
 *
 * Software distributed under the License is distributed on an "AS IS" basis,
 * WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
 * for the specific language governing rights and limitations under the
 * License.
 *
 * The Original Code is Weave.
 *
 * The Initial Developer of the Original Code is
 * the Mozilla Foundation.
 * Portions created by the Initial Developer are Copyright (C) 2010
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *
 * Alternatively, the contents of this file may be used under the terms of
 * either the GNU General Public License Version 2 or later (the "GPL"), or
 * the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
 * in which case the provisions of the GPL or the LGPL are applicable instead
 * of those above. If you wish to allow use of your version of this file only
 * under the terms of either the GPL or the LGPL, and not to allow others to
 * use your version of this file under the terms of the MPL, indicate your
 * decision by deleting the provisions above and replace them with the notice
 * and other provisions required by the GPL or the LGPL. If you do not delete
 * the provisions above, a recipient may use your version of this file under
 * the terms of any one of the MPL, the GPL or the LGPL.
 *
 * ***** END LICENSE BLOCK ***** */

const Ci = Components.interfaces;
const Cu = Components.utils;

Cu.import("resource://gre/modules/XPCOMUtils.jsm");

function AddonGlue() {}
AddonGlue.prototype = {
  classDescription: "Sync Add-on Glue",
  contractID: "@mozilla.org/weave/addon-glue;1",
  classID: Components.ID("{f9fa50ae-f78f-4f8c-beba-91a5cff28f1a}"),
  _xpcom_categories: [{category: "app-startup", service: true}],

  QueryInterface: XPCOMUtils.generateQI([Ci.nsIObserver,
                                         Ci.nsISupportsWeakReference]),

  observe: function BSS__observe(subject, topic, data) {
    Cu.import("resource://services-sync/util.js");
    Cu.import("resource://services-sync/constants.js");

    let engines = [];
    switch (Svc.AppInfo.ID) {
      case FIREFOX_ID:
        // The overlay code should connect us earlier, but if it fails to
        // do that for some reason, make sure we autoconnect after 30 secs.
        Svc.DefaultPrefs.set("autoconnectDelay", 30);
        engines = ["Bookmarks", "Form", "History", "Password", "Prefs", "Tab"];
        break;

      case SEAMONKEY_ID:
        Svc.DefaultPrefs.set("autoconnectDelay", 30);
        engines = ["Bookmarks", "Form", "History", "Password", "Tab"];
        break;

      case FENNEC_ID:
        Svc.DefaultPrefs.set("client.type", "mobile");
        Svc.DefaultPrefs.set("autoconnectDelay", 5);
        engines = ["Tab", "Bookmarks", "Form", "History", "Password"];
        break;
    }
    Svc.DefaultPrefs.set("registerEngines", engines.join(","));
    Svc.DefaultPrefs.set("log.appender.debugLog.enabled", true);
  }
};

// Gecko <2.0
function NSGetModule(compMgr, fileSpec) {
  return XPCOMUtils.generateModule([AddonGlue]);
}

// Gecko >=2.0
if (typeof XPCOMUtils.generateNSGetFactory == "function")
  const NSGetFactory = XPCOMUtils.generateNSGetFactory([AddonGlue]);
