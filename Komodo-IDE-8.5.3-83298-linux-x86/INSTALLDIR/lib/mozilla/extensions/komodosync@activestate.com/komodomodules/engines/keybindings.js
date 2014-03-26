Components.utils.import("resource://komodosync/engines/files.js");

const EXPORTED_SYMBOLS = ['KeybindingsEngine'];

/**
 * The KeybindingsEngine only syncs records between machines of the same
 * platform, so e.g. Mac keybindings (Cmd+...) won't overwrite Windows
 * keybindings (Ctrl+...).
 */
function KeybindingsEngine() {
    var osSvc = Components.classes['@activestate.com/koOs;1'].
                    getService(Components.interfaces.koIOs);
    var userDataDir = Components.classes['@activestate.com/koDirs;1']
                        .getService(Components.interfaces.koIDirs).userDataDir;
    var enginePath = osSvc.path.join(userDataDir, "schemes");
    var engineDir = Components.classes["@mozilla.org/file/local;1"].
                     createInstance(Components.interfaces.nsILocalFile);
    engineDir.initWithPath(enginePath);
    var name = "keybindings";
    this._name = name;
    name += "_" + this._platform;
    FilesEngine.call(this, name, engineDir);
}

KeybindingsEngine.prototype = {
    __proto__: FilesEngine.prototype,
    _storeObj: KeybindingStore,
    
    __platform: null,
    get _platform() {
        if (!this.__platform) {
            let platformStr = Components.
                classes["@mozilla.org/appshell/window-mediator;1"].
                getService(Components.interfaces.nsIWindowMediator).
                getMostRecentWindow("Komodo").
                navigator.platform.toLowerCase();
            if (platformStr.indexOf("win") != -1)
                this.__platform = "win";
            else if (platformStr.indexOf("linux") != -1)
                this.__platform = "linux";
            else if (platformStr.indexOf("mac") != -1)
                this.__platform = "mac";
            else
                this.__platform = "other"
        }
        return this.__platform;
    },
    
    get prefName() this._name, // Note that the current weave implementation only uses this for this.enabled
}

/**
 * The KeybindingStore only tracks .kkf files in the schemes directory.
 * The SchemesEngine _MUST_ make sure to exclude those.
 */
function KeybindingStore(name) {
    FilesStore.call(this, name);
}

KeybindingStore.prototype = {
    __proto__: FilesStore.prototype,
    
    getAllIDs: function FilesStore_getAllIDs() {
        this._log.debug("getAllIDs called");
        var dirEntries = this.baseDir.directoryEntries;
        while (dirEntries.hasMoreElements()) {
            let file = dirEntries.getNext();
            file.QueryInterface(Components.interfaces.nsILocalFile);
            let regexp = /.+\.kkf$/; // only match .kkf files
            if (file.isFile() && regexp.test(file.leafName)) {
                let [id, fileName] = this._getIDAndRelDescFromFile(file);
                this._fileNames[id] = fileName;
            }
        }
        return this._fileNames;
    }
}