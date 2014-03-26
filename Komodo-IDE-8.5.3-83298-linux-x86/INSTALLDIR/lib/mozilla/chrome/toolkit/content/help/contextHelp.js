//@line 4 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"

//@line 7 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
var helpFileURI;

//@line 12 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
function openHelp(topic, contentPack)
{
//@line 16 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
  helpFileURI = contentPack || helpFileURI;

//@line 19 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
  var topWindow = locateHelpWindow(helpFileURI);

  if ( topWindow ) {
//@line 23 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
    topWindow.focus();
    topWindow.displayTopic(topic);
  } else {
//@line 27 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
    const params = Components.classes["@mozilla.org/embedcomp/dialogparam;1"]
                             .createInstance(Components.interfaces.nsIDialogParamBlock);
    params.SetNumberStrings(2);
    params.SetString(0, helpFileURI);
    params.SetString(1, topic);
    const ww = Components.classes["@mozilla.org/embedcomp/window-watcher;1"]
                         .getService(Components.interfaces.nsIWindowWatcher);
//@line 40 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
    ww.openWindow(null, "chrome://help/content/help.xul", "_blank", "chrome,all,dialog=no", params);
//@line 42 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
  }
}

//@line 46 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
function setHelpFileURI(rdfURI)
{
  helpFileURI = rdfURI;
}

//@line 52 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
function locateHelpWindow(contentPack) {
    const windowManagerInterface = Components
        .classes['@mozilla.org/appshell/window-mediator;1'].getService()
        .QueryInterface(Components.interfaces.nsIWindowMediator);
    const iterator = windowManagerInterface.getEnumerator("mozilla:help");
    var topWindow = null;
    var aWindow;

//@line 62 "/home/komodo-build/mozbuilds/release/ide-8.5/hg-ff-24.0.0/mozilla/toolkit/components/help/content/contextHelp.js"
    while (iterator.hasMoreElements()) {
        aWindow = iterator.getNext();
        if (aWindow.getHelpFileURI() == contentPack) {
            topWindow = aWindow;
        }
    }
    return topWindow;
}
