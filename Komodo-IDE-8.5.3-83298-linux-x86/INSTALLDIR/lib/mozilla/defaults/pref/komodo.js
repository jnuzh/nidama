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
 * The Original Code is mozilla.org code.
 *
 * The Initial Developer of the Original Code is 
 * Netscape Communications Corporation.
 * Portions created by the Initial Developer are Copyright (C) 1998
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *   ActiveState Software Inc.
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

//@line 39 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"

//@line 42 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"

//@line 48 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"

pref("toolkit.chromeURL","chrome://komodo/content/");
pref("browser.chromeURL","chrome://komodo/content/dialogs/browser.xul");
pref("toolkit.singletonWindowType", "Komodo");
//@line 57 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"

// Less delay for the Add-on install dialog.
pref("security.dialog_enable_delay", 500);

// Preferences for the Get Add-ons pane
pref("extensions.getAddons.showPane", true);
pref("extensions.getAddons.browseAddons", "http://community.activestate.com/addons");
pref("extensions.getAddons.maxResults", 5);
pref("extensions.getAddons.recommended.browseURL", "http://community.activestate.com/addons/recommended");
pref("extensions.getAddons.recommended.url", "http://community.activestate.com/xpi/api/%API_VERSION%/list/featured/all/10");
pref("extensions.getAddons.search.browseURL", "http://community.activestate.com/search/node/%TERMS%+type%3Axpi");
pref("extensions.getAddons.search.url", "http://community.activestate.com/xpi/api/%API_VERSION%/search/%TERMS%");
pref("extensions.webservice.discoverURL", "http://community.activestate.com/addons/recommended8?id=%ID%&version=%VERSION%&os=%OS%&abi=%XPCOMABI%");

// Blocklist preferences
pref("extensions.blocklist.enabled", false);

// App-specific update preferences

// Whether or not app updates are enabled
pref("app.update.enabled", true);

// This preference turns on app.update.mode and allows automatic download and
// install to take place. We use a separate boolean toggle for this to make
// the UI easier to construct.
pref("app.update.auto", false);

// Update service URL:
pref("app.update.url", "https://komodo.activestate.com/update/2/%PRODUCT%/%VERSION%/%BUILD_ID%/linux-x86/%LOCALE%/%CHANNEL%/update.xml?id=%DISTRIBUTION%");
// URL user can browse to manually if for some reason all update installation
// attempts fail.
pref("app.update.url.manual", "http://www.activestate.com/products/komodo_ide/");
// A default value for the "More information about this update" link
// supplied in the "An update is available" page of the update wizard. 
pref("app.update.url.details", "http://www.activestate.com/products/komodo_ide/");

// User-settable override to app.update.url for testing purposes.
//pref("app.update.url.override", "");

// Whether or not we show a dialog box informing the user that the update was
// successfully applied. This is off in Firefox by default since we show a 
// upgrade start page instead! Other apps may wish to show this UI, and supply
// a whatsNewURL field in their brand.properties that contains a link to a page
// which tells users what's new in this new update.
pref("app.update.showInstalledUI", false);

// Symmetric (can be overridden by individual extensions) update preferences.
// e.g.
//  extensions.{GUID}.update.enabled
//  extensions.{GUID}.update.url
//  extensions.{GUID}.update.interval
//  .. etc ..
//
pref("extensions.update.enabled", true);
pref("extensions.update.url", "https://komodo.activestate.com/update/VersionCheck.php?reqVersion=%REQ_VERSION%&id=%ITEM_ID%&version=%ITEM_VERSION%&maxAppVersion=%ITEM_MAXAPPVERSION%&status=%ITEM_STATUS%&appID=%APP_ID%&appVersion=%APP_VERSION%&appOS=%APP_OS%&appABI=%APP_ABI%");
// Non-symmetric (not shared by extensions) extension-specific [update] preferences
pref("extensions.getMoreExtensionsURL", "http://community.activestate.com/addons");
pref("extensions.getMoreThemesURL", "http://community.activestate.com/addons");
// Add-on metadata query (screenshots, description, ratings, downloads, ...)
// Not used by Komodo - and it actually causes our ads to be blocked - bug 97923.
pref("extensions.getAddons.cache.enabled", false);

pref("xpinstall.whitelist.add", "komodo.activestate.com");

pref("keyword.enabled", true);

pref("general.useragent.locale", "en-US");
pref("general.skins.selectedSkin", "classic/1.0");

//@line 127 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"
// Show hidden files in the file picker; bug 81075
pref("filepicker.showHiddenFiles", true);
//@line 130 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"

// Scripts & Windows prefs
pref("dom.disable_open_during_load",              true);
//@line 137 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"
pref("javascript.options.showInConsole",          false);
//@line 139 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"

// Make the status bar reliably present and unaffected by pages
pref("dom.disable_window_open_feature.status",    true);
// This is the pref to control the location bar, change this to true to 
// force this instead of or in addition to the status bar - this makes 
// the origin of popup windows more obvious to avoid spoofing. We would 
// rather not do it by default because it affects UE for web applications, but
// without it there isn't a really good way to prevent chrome spoofing, see bug 337344
pref("dom.disable_window_open_feature.location",  true);
pref("dom.disable_window_status_change",          true);
// allow JS to move and resize existing windows
pref("dom.disable_window_move_resize",            false);
// prevent JS from monkeying with window focus, etc
pref("dom.disable_window_flip",                   false);

pref("profile.allow_automigration", false);   // setting to false bypasses automigration in the profile code

// replace newlines with spaces when pasting into <input type="text"> fields
pref("editor.singleLine.pasteNewlines", 2);

// The breakpad report server to link to in about:crashes
pref("breakpad.reportURL", "http://crash-stats.activestate.com/report/index/");

// base URL for web-based support pages
pref("app.support.baseURL", "http://support.activestate.com/1/%APP%/%VERSION%/%OS%/%LOCALE%/");

// Disable the extension selection UI at startup - as this mostly contains
// ActiveState add-ons included in the base installation - which we don't want
// the user to uninstall.
pref("extensions.shownSelectionUI", true);

// Allow for skin switching during runtime
pref("extensions.dss.enabled", true);

// Used for the Help window
pref("accessibility.typeaheadfind.flashBar", 1);

// Required for "Web & Browser > Proxy" preferences.
//@line 180 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"
pref("browser.preferences.instantApply", true);
//@line 182 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"

//@line 188 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/komodo/app/profile/komodo.js"

// Disable unresponsive script checking - bug 91614.
pref("dom.max_chrome_script_run_time", 0);
