Components.utils.import("resource://komodosync/engines/files.js");
Components.utils.import("resource://services-sync/util.js");

const EXPORTED_SYMBOLS = ['ToolsEngine'];

const MAJOR_VERSION = Svc.AppInfo.version.split(".")[0];

function ToolsEngine() {
    var osSvc = Components.classes['@activestate.com/koOs;1'].
                    getService(Components.interfaces.koIOs);
    var userDataDir = Components.classes['@activestate.com/koDirs;1']
                        .getService(Components.interfaces.koIDirs).userDataDir;
    var enginePath = osSvc.path.join(userDataDir, "tools");
    var engineDir = Components.classes["@mozilla.org/file/local;1"].
                     createInstance(Components.interfaces.nsILocalFile);
    engineDir.initWithPath(enginePath);
    FilesEngine.call(this, "tools", engineDir);
    this._store._ignoreFileReStrings.push("^unsynced$");
}

ToolsEngine.prototype = {
    __proto__: FilesEngine.prototype,
    
    // We use a different storage collection in Komodo 8, to avoid conflicts
    // with Komodo 7 tools - bug 96567.
    get engineURL() this.storageURL + this.name + MAJOR_VERSION,

    _syncFinish: function FilesEngine__syncFinish() {
        var ret = FilesEngine.prototype._syncFinish.apply(this, arguments);
        this.reloadToolbox();
        return ret;
    },
    
    get _toolboxSvc() {
        var svc = Components.classes['@activestate.com/koToolbox2Service;1']
                        .getService(Components.interfaces.koIToolbox2Service);
        this.__defineGetter__("toolboxSvc", function() svc);
        return svc;
    },
    
    get _observerSvc() {
        var svc = Components.classes["@mozilla.org/observer-service;1"]
                        .getService(Components.interfaces.nsIObserverService);
        this.__defineGetter__("observerSvc", function() svc);
        return svc;
    },
    
    reloadToolbox: function ToolsEngine_reloadToolbox(path) {
        if (!path)
            path = this._store.baseDir.path;
        this._log.debug("Telling ToolboxService to refresh " + path);
        this._toolboxSvc.reloadToolsDirectory(path);
        this._observerSvc.notifyObservers(null, 'toolbox-tree-changed', path);
    },
    
    _unsyncedFolder: null,
    get unsyncedFolder() {
        if (!this._unsyncedFolder) {
            this._unsyncedFolder = this._store.baseDir;
            this._unsyncedFolder.append("unsynced");
        }
        this._unsyncedFolder.QueryInterface(Components.interfaces.nsILocalFile);
        if (!this._unsyncedFolder.exists()) {
            this._unsyncedFolder.create(
                    Components.interfaces.nsIFile.DIRECTORY_TYPE, 0700
            );
        }
        return this._unsyncedFolder;
    },
    
    ignoreTool: function ToolboxSyncUtils_ignoreTool(file) {
        try {
            if (this._store.baseDir.contains(file, true)) {
                file.moveTo(this.unsyncedFolder, "");
                this.reloadToolbox();
                return true;
            }
        } catch(e) {
            this._log.warn("Ignoring the current tool failed: " + e.message);
        }
        return false;
    }
}