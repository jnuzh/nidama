Components.utils.import("resource://komodosync/engines/files.js");

const EXPORTED_SYMBOLS = ['SubDirsEngine'];

/** Like a FilesEngine, but does not track non-directory files in the base
 *  directory.
 */
function SubDirsEngine(name, baseDir) {
    FilesEngine.call(this, name, baseDir);
}

SubDirsEngine.prototype = {
    __proto__: FilesEngine.prototype,
    _storeObj: SubDirsStore
}

function SubDirsStore(name) {
    FilesStore.call(this, name);
}

SubDirsStore.prototype = {
    __proto__: FilesStore.prototype,
    
    // Non-directory files in the base dir must not be tracked.
    getAllIDs: function FilesStore_getAllIDs() {
        this._log.debug("getAllIDs called");
        var dirEntries = this.baseDir.directoryEntries;
        while (dirEntries.hasMoreElements()) {
            let entry = dirEntries.getNext();
            entry.QueryInterface(Components.interfaces.nsILocalFile);
            if (entry.isDirectory()) {
                this._getAllIDsForFile(entry);
            }
        }
        return this._fileNames;
    }
}