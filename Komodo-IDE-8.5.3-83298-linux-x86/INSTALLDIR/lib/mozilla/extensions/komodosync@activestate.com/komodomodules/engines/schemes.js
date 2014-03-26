Components.utils.import("resource://komodosync/engines/files.js");

const EXPORTED_SYMBOLS = ['SchemesEngine'];

function SchemesEngine() {
    var osSvc = Components.classes['@activestate.com/koOs;1'].
                    getService(Components.interfaces.koIOs);
    var userDataDir = Components.classes['@activestate.com/koDirs;1']
                        .getService(Components.interfaces.koIDirs).userDataDir;
    var enginePath = osSvc.path.join(userDataDir, "schemes");
    var engineDir = Components.classes["@mozilla.org/file/local;1"].
                     createInstance(Components.interfaces.nsILocalFile);
    engineDir.initWithPath(enginePath);
    FilesEngine.call(this, "schemes", engineDir);
    
    // ignore all keyboard scheme files from sync:
    this._store._ignoreFileReStrings.push("\\.kkf$");
}

SchemesEngine.prototype = {
    __proto__: FilesEngine.prototype,

    _syncFinish: function SchemesEngine__syncFinish() {
        var ret = FilesEngine.prototype._syncFinish.apply(this, arguments);
        this.reloadSchemes();
        return ret;
    },
    
    reloadSchemes: function() {
        try {
            var schemesSvc = Components.classes['@activestate.com/koScintillaSchemeService;1'].getService();
            schemesSvc.reloadAvailableSchemes();
        } catch(ex) {
            this._log.exception("Unable to reload schemes: " + ex);
        }
    }
}
