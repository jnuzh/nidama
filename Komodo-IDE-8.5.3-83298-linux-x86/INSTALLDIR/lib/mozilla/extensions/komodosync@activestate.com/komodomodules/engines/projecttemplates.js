Components.utils.import("resource://komodosync/engines/subdirs.js");

const EXPORTED_SYMBOLS = ['ProjectTemplatesEngine'];

function ProjectTemplatesEngine() {
    var osSvc = Components.classes['@activestate.com/koOs;1'].
                    getService(Components.interfaces.koIOs);
    var userDataDir = Components.classes['@activestate.com/koDirs;1']
                        .getService(Components.interfaces.koIDirs).userDataDir;
    var enginePath = osSvc.path.join(userDataDir, "project-templates");
    var engineDir = Components.classes["@mozilla.org/file/local;1"].
                     createInstance(Components.interfaces.nsILocalFile);
    engineDir.initWithPath(enginePath);
    SubDirsEngine.call(this, "projecttemplates", engineDir);
}

ProjectTemplatesEngine.prototype = {
    __proto__: SubDirsEngine.prototype
}