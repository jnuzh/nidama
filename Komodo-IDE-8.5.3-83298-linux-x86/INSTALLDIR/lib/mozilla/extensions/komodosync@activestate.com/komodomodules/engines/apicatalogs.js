Components.utils.import("resource://komodosync/engines/files.js");

const EXPORTED_SYMBOLS = ['ApiCatalogsEngine'];

function ApiCatalogsEngine() {
    var osSvc = Components.classes['@activestate.com/koOs;1'].
                    getService(Components.interfaces.koIOs);
    var userDataDir = Components.classes['@activestate.com/koDirs;1']
                        .getService(Components.interfaces.koIDirs).userDataDir;
    var enginePath = osSvc.path.join(userDataDir, "apicatalogs");
    var engineDir = Components.classes["@mozilla.org/file/local;1"].
                     createInstance(Components.interfaces.nsILocalFile);
    engineDir.initWithPath(enginePath);
    FilesEngine.call(this, "apicatalogs", engineDir);
}

ApiCatalogsEngine.prototype = {
    __proto__: FilesEngine.prototype
}