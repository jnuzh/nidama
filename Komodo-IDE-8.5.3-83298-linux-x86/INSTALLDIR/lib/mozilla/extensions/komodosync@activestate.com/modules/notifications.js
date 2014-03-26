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
 * The Original Code is Bookmarks Sync.
 *
 * The Initial Developer of the Original Code is Mozilla.
 * Portions created by the Initial Developer are Copyright (C) 2007
 * the Initial Developer. All Rights Reserved.
 *
 * Contributor(s):
 *  Myk Melez <myk@mozilla.org>
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

const EXPORTED_SYMBOLS = ["Notifications", "Notification", "NotificationButton"];

const Cc = Components.classes;
const Ci = Components.interfaces;
const Cr = Components.results;
const Cu = Components.utils;

Cu.import("resource://gre/modules/XPCOMUtils.jsm");
Cu.import("resource://services-sync/ext/Observers.js");
Cu.import("resource://services-sync/log4moz.js");
Cu.import("resource://services-sync/util.js");

var {logging} = Cu.import("chrome://komodo/content/library/logging.js", {});
var log = logging.getLogger("sync.notifications");

/**
 * This is an override of the Weave Notification Service.  It's a wrapper around
 * Komodo's koINotifactionService (which was based off the old Weave version).
 */

XPCOMUtils.defineLazyGetter(Cu.getGlobalForObject({}), "Notifications", () => {
    const {KoNotificationManagerWrapper} =
        Cu.import("resource://gre/modules/notifications.js", {});

    return {
        manager: new KoNotificationManagerWrapper(null),
        get Notification() Notification,
        get NotificationButton() NotificationButton,

        // Match the referenced values in toolkit/content/widgets/notification.xml.
        get PRIORITY_INFO() 1, // PRIORITY_INFO_LOW
        get PRIORITY_WARNING() 4, // PRIORITY_WARNING_LOW
        get PRIORITY_ERROR() 7, // PRIORITY_CRITICAL_LOW

        get notifications() Array.slice(this.manager),

        /**
         * Shorthand method to create and add a simple notification.
         */
        notify: function Notifications_notify(title, description, iconURL, priority) {
            var notification = Notification(title, description, iconURL, priority);
            notification = this.manager.add(notification);
            notification.wrappedJSObject = notification;
            return notification;
        },

        add: function Notifications_add(notification) {
            this.manager.addNotification(notification);
            Services.obs.notifyObservers(notification,
                "komodo:notification:added", null);
        },

        remove: function Notifications_remove(notification) {
            if (this.manager.removeNotification(notification)) {
                Services.obs.notifyObservers(notification,
                    "komodo:notification:removed", null);
            }
        },

        /**
         * Replace an existing notification.
         */
        replace: function Notifications_replace(oldNotification, newNotification) {
            this.manager.removeNotification(oldNotification);
            this.manager.addNotification(newNotification);
        },

        /**
         * Remove all notifications that match a title. If no title is provided, all
         * notifications are removed.
         *
         * @param title [optional]
         *        Title of notifications to remove; falsy value means remove all
         */
        removeAll: function Notifications_removeAll(title) {
            for each(let notification in Array.slice(this.manager)) {
                if (!title || notification.summary == title) {
                    this.manager.remove(notification);
                }
            }
        },

         // replaces all existing notifications with the same title as the new one
        replaceTitle: function Notifications_replaceTitle(notification) {
            this.removeAll(notification.summary);
            this.add(notification);
        }
}});

// Compat wrapper
XPCOMUtils.defineLazyGetter(Cu.getGlobalForObject({}),
                            "NotificationSvc",
                            Notifications);

function Notification(title, description, iconURL, priority, buttons=[], tags=[]) {
    var severity = ({ // map to koINotification severity levels
        "1": Ci.koINotification.SEVERITY_INFO,
        "4": Ci.koINotification.SEVERITY_WARNING,
        "7": Ci.koINotification.SEVERITY_ERROR,
    })[priority];
    var params = {
        description: description,
        iconURL: iconURL,
        severity: severity
    };

    if (buttons) {
        params.actions = buttons;
    }

    return Notifications.manager.add(title, tags, title, params);
}

/**
 * A button to display in a notification.
 */
function NotificationButton(label, accessKey, callback) {
  var action = Cc["@activestate.com/koNotification/action;1"]
                 .createInstance(Ci.koINotificationAction);
  function callbackWrapper(aNotification, aActionId) {
    try {
      callback.apply(this, arguments);
    } catch (e) {
      Cu.reportError(e);
      try {
        log.exception("Exception while handling button callback: " +
                      Utils.exceptionStr(e));
      } catch(ex) {
      }
      throw e;
    }
  }
  action.identifier = label || "anonymous-action-" + Date.now() + "." + Math.random();
  action.label = label;
  action.accessKey = accessKey;
  action.handler = callbackWrapper;
  action.visible = action.enabled = true;

  return action;
};

/**
 * Helper functions
 */
let Utils = {
  exceptionStr: function(e) {
    let message = e.message ? e.message : e;
    return message + " " + Utils.stackTrace(e);
  },

  stackTrace: function(e) {
    // Wrapped nsIException
    if (e.location)
      return "Stack trace: " + Utils.stackTraceFromFrame(e.location);

    // Standard JS exception
    if (e.stack)
      return "JS Stack trace: " + e.stack.trim().replace(/\n/g, " < ").
        replace(/@[^@]*?([^\/\.]+\.\w+:)/g, "@$1");

    return "No traceback available";
  },

  stackTraceFromFrame: function(frame) {
    let output = [];
    while (frame) {
      let str = Utils.formatFrame(frame);
      if (str)
        output.push(str);
      frame = frame.caller;
    }
    return output.join(" < ");
  },

  // Works on frames or exceptions, munges file:// URIs to shorten the paths
  // FIXME: filename munging is sort of hackish, might be confusing if
  // there are multiple extensions with similar filenames
  formatFrame: function(frame) {
    let tmp = "<file:unknown>";

    let file = frame.filename || frame.fileName;
    if (file)
      tmp = file.replace(/^(?:chrome|file):.*?([^\/\.]+\.\w+)$/, "$1");

    if (frame.lineNumber)
      tmp += ":" + frame.lineNumber;
    if (frame.name)
      tmp = frame.name + "()@" + tmp;

    return tmp;
  }
};
