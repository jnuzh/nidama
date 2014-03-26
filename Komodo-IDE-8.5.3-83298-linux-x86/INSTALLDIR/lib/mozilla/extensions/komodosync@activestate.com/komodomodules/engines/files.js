const EXPORTED_SYMBOLS = ['FilesEngine', 'FilesStore', 'FilesTracker'];

Components.utils.import("resource://services-sync/engines.js");
Components.utils.import("resource://services-sync/notifications.js");
Components.utils.import("resource://services-sync/stores.js");
Components.utils.import("resource://services-sync/trackers.js");
Components.utils.import("resource://services-sync/util.js");
Components.utils.import("resource://services-sync/base_records/crypto.js");
Components.utils.import("resource://komodosync/type_records/files.js");

/**
 * FilesEngine synchronizes the content of the base directory `baseDir` with
 * Weave. In order to detect changes inside the base directory it stores a
 * snapshot file in the base directory. The snapshot file contains the name
 * of each file and the md5 hash of its content.
 */
function FilesEngine(name, baseDir) {
    SyncEngine.call(this, name);

    this._store.baseDir = baseDir;    
    this._log.debug("FilesEngine created: " + name);
}

FilesEngine.prototype = {
    // TODO implement Engine reset (delete fileNames file)
    // FIXME resetLastSync if _store._snapshotFile is missing
    __proto__: SyncEngine.prototype,
    
    _storeObj: FilesStore,
    _trackerObj: FilesTracker,
    _recordObj: FilesRecord,
    
    _resetClient: function FilesEngine__resetClient() {
        this._log.debug('resetting ' + this.name);
        SyncEngine.prototype._resetClient.apply(this, arguments);
        this._store.resetSnapshot(); // FIXME use notification instead
        this._store._fileNames = null;
    },
    
    _syncStartup: function FilesEngine__syncStartup() {
        this._log.debug('syncying ' + this.name);
        if (this.lastSync
            && !FilesUtils.checkPermissions(this._store._snapshotFile)) {
            // Snapshot file went missing, we have to fetch everything from the server
            this._log.debug('snapshot missing for ' + this.name);
            this.resetClient();
        }
        if (this.lastSync) {
            // If this engine has been synced before, look at what's changed
            // and manually add all changes to the tracker. Otherwise,
            // SyncEngine will mark all files as changed anyway.
            this._trackChangedFiles();
        }
        var ret = SyncEngine.prototype._syncStartup.apply(this, arguments);
        return ret;
    },

    _syncFinish: function FilesEngine__syncFinish() {
        var ret = SyncEngine.prototype._syncFinish.apply(this, arguments);
        this._store.saveSnapshot();
        return ret;
    },
    
    _trackChangedFiles: function FilesEngine__trackChangedFiles() {
        for each (let id in this._store.getChangedIDs()) {
            this._tracker.addChangedID(id);
        }
    }
}

function FilesStore(name) {
    Store.call(this, name);
    this._log.debug("FilesStore created: " + name);
}

FilesStore.prototype = {
    __proto__: Store.prototype,
    __baseDir: null,
    __fileNames: null, // ID <> file name mapping
    _snapshot: null,  // ID <> md5 mapping

    get _ignoreFileReStrings() {
        let strings = [
            "^(.*\\/)*\\." // ignore all files and directories that start with a dot
        ];
        this.__defineGetter__("_ignoreFileReStrings", function() strings);
        return strings;
    },

    
    /**
     * This returns a regular expression that matches all files that have to
     * be ignored from sync.
     */
    get _ignoreFileRe() {
        if (!this.__ignoreFileRe) {
            let reString = "";
            for each (let str in this._ignoreFileReStrings) {
                reString += str + "|"
            }
            reString = reString.slice(0,-1); // remove the last '|'
            this.__ignoreFileRe = new RegExp(reString);
            this.__defineGetter__("_ignoreFileRe", function() this.__ignoreFileRe);
        }
        return this.__ignoreFileRe;
    },
    
    /**
     * _fileNames maps the IDs of all files that are currently tracked by this
     * engine to their path names (relative to baseDir). The IDs from this
     * object are used to create the snapshot after the engine finished
     * syncing. It is updated before sync by getAllIDs and during sync by all
     * functions that manipulate files, such as create and remove.
     */
    get _fileNames() {
        if (!this.__fileNames) {
            this.__fileNames = {};
        }
        return this.__fileNames;
    },
    
    set _fileNames(value) {
        return this.__fileNames = value;
    },
    
    get baseDir() {
        if (!this.__baseDir) {
            throw "base directory has not been set for engine " + this.name;
        }
        if (!this.__baseDir.exists()) {
            try {
                this.__baseDir.create(
                    Components.interfaces.nsIFile.DIRECTORY_TYPE, 0700
                );
            } catch(e) {
                this._log.error(e.message);
                throw "cannot create base directory of " + this.name;
            }
        }
        return this.__baseDir.clone().QueryInterface(Components.interfaces.nsILocalFile);
    },
    
    set baseDir(dir) {
        dir.QueryInterface(Components.interfaces.nsILocalFile);
        if (this.__baseDir) {
            throw "Base dir has already been set for engine " + this.name;
        }
        return this.__baseDir = dir;
    },
    
    get _snapshotFile() {
        var file = this.baseDir;
        file.append("." + this.name + ".komodosync");
        return file;
    },
    
    /**
     * Returns a new file initialized with relPath relative to this.baseDir.
     * If the file is not readible and writeable or should be, ignored, null
     * is returned instead.
     */
    _newFile: function FilesStore__newFile(relPath) {
        var file = Components.classes["@mozilla.org/file/local;1"].
                             createInstance(Components.interfaces.nsILocalFile);
        file.setRelativeDescriptor(this.baseDir, relPath);
        if (FilesUtils.checkPermissions(file) && !this._shouldIgnore(file)) {
            return file;
        } else {
            return null;
        }
    },
    
    _getFileFromID: function FilesStore__getFileFromID(id) {
        var fileName = this._fileNames[id];
        var file = null;
        if (typeof fileName == "string") {
            file = this._newFile(fileName);
        }
        return file;
    },
    
    _getFileFromRecord: function FilesStore__getFileFromRecord(record) {
        if (typeof record.fileName !== "string") {
            return null;
        }
        var file = this._newFile(record.fileName);
        return file;
    },

    itemExists: function FilesStore_itemExists(id) {
        this._log.debug("Checking if " + id + " exists...");
        var exists = id in this._fileNames;
        this._log.debug("Exists? " + exists + " : " + this._fileNames[id]);
        return exists;
    },
    
    create: function FilesStore_create(record) {
        this._log.debug("Creating file " + record.fileName + "(" + record.id + ")");
        let file = this._getFileFromRecord(record);
        if (file) {
            let type = record.isDirectory ?
                Components.interfaces.nsIFile.DIRECTORY_TYPE :
                Components.interfaces.nsIFile.NORMAL_FILE_TYPE;
            let permissions = record.isDirectory ? 0700 : 0600;
            if (!file.exists()) {
                file.create(type, permissions);
            } else {
                this._log.debug("File " + record.fileName + " already exists");
            }
            this._fileNames[record.id] = record.fileName;
            this.update(record);
        } else {
            this._log.error("Invalid record to create: " + record.id)
        }
    },
    
    remove: function FilesStore_remove(record) {
        this._log.debug("Removing " + record.id);
        // _record_ is the incoming record, which has no data attached to it.
        // Thus we have to retrieve the file by ID.
        let file = this._getFileFromID(record.id);
        if (file && file.exists() && this._checkPermissions(file)) {
            this._log.debug("File name is " + file.path);
            let recursive = file.isDirectory();
            // TODO We need error handling here. nsiFile.remove occasionally
            // fails w/ NS_ERROR_FAILURE (open file e.g.)
            file.remove(recursive);
        }
        delete this._fileNames[record.id];
        delete this._snapshot[record.id]; // XXX Do we have to manipulate _snapshot??? 
    },
    
    /**
     * Deletes everything this engine tracks. Note that this might also remove
     * files that are ignored by this engine.
     */
    wipe: function FilesStore_wipe() {
        for each (let fileName in this.getAllIDs()) {
            let file = this._newFile(fileName);
            if (file.exists()) {
                try {
                    file.remove(true);
                } catch(e) {
                    this._log.debug("Cannot delete file " + file.path);
                    this._log.debug(e);
                }
            }
        }
        this._log.debug("Wiped local store.");
    },
    
    /**
     * Update a local file with the data from record.
     */
    update: function FilesStore_update(record) {
        this._log.debug("Updating file " + record.fileName + "(" + record.id + ")");
        let file = this._getFileFromRecord(record);
        if (file.isFile() && this._checkPermissions(file)
                            && typeof record.fileContent === "string"
                            && record.fileContent.length > 0) {
            let foStream = Components.classes["@mozilla.org/network/file-output-stream;1"]
                        .createInstance(Components.interfaces.nsIFileOutputStream);
            foStream.init(file, 0x02 | 0x08 | 0x20, 0644, 0);
            foStream.write(record.fileContent, record.fileContent.length);
            foStream.close();
        }
        this._snapshot[record.id] = FilesUtils.md5(record.fileContent);
    },
    
    /**
     * Initializes record with the file contents for the id given in record.
     */
    _initRecord: function FilesStore__initRecord(record) {
        let id = record.id;
        var file = this._getFileFromID(id);
        if (file && file.exists() && this._checkPermissions(file)) {
            record.fileName = this._getRelDescFromFile(file);
            var data = "";
            record.isDirectory = file.isDirectory()
            if (!record.isDirectory) {
                try {
                    let fstream =
                        Components.classes["@mozilla.org/network/file-input-stream;1"].
                            createInstance(Components.interfaces.nsIFileInputStream);
                    let bstream =
                        Components.classes["@mozilla.org/binaryinputstream;1"].
                            createInstance(Components.interfaces.nsIBinaryInputStream);
                    fstream.init(file, -1, 0, 0);
                    bstream.setInputStream(fstream);
                    data = bstream.readBytes(bstream.available());
                    bstream.close();
                    fstream.close();
                } catch(e) { 
                    this._log.error("Cannot access " + id + " " + file.path);
                    this._log.error(e.message);
                    this._showFileNotification(file);
                    data = "";
                    record.deleted = true;
                }
            }
            record.fileContent = data;
        } else {
            record.deleted = true;
        }
        return record;
    },
    
    createRecord: function FilesStore_createRecord(id, collection) {
        this._log.debug("Creating new record for file " + id);
        var record = new FilesRecord(collection, id);
        this._initRecord(record);
        if (!record.deleted) {
            this._snapshot[id] = FilesUtils.md5(record.fileContent);
        } else {
            this._log.debug("File has been deleted"); // or couldn't be accessed
            delete this._fileNames[id];
            delete this._snapshot[id];
        }
        return record;
    },

    _getIDAndRelDescFromFile: function FilesStore__getIDAndRelDescFromFile(file) {
        var relativeDesc = this._getRelDescFromFile(file);
        var id = Utils.sha1(relativeDesc);
        return [id, relativeDesc];
    },
    
    _getRelDescFromFile: function FilesStore__getRelDescFromFile(file) {
        file.QueryInterface(Components.interfaces.nsILocalFile);
        return file.getRelativeDescriptor(this.baseDir);
    },
    
    _shouldIgnore: function FilesStore__shouldIgnore(file) {
        let path = this._getRelDescFromFile(file);
        let matchesRegEx = this._ignoreFileRe.test(path);
        return matchesRegEx || !this._checkPermissions(file);
    },
    
    _getAllIDsForFile: function FilesStore__getAllIDsForFile(file) {
        file.QueryInterface(Components.interfaces.nsILocalFile);
        if (!this._shouldIgnore(file)) {
            let [id, fileName] = this._getIDAndRelDescFromFile(file);
            this._fileNames[id] = fileName;
            if (file.isDirectory()) {
                var dirEntries = file.directoryEntries;
                while (dirEntries.hasMoreElements()) {
                    let entry = dirEntries.getNext();
                    this._getAllIDsForFile(entry);
                }
            }
        }
    },
    
    getAllIDs: function FilesStore_getAllIDs() {
        this._log.debug("getAllIDs called");
        var dirEntries = this.baseDir.directoryEntries;
        while (dirEntries.hasMoreElements()) {
            let entry = dirEntries.getNext();
            this._getAllIDsForFile(entry);
        }
        return this._fileNames;
    },
    
    _fileHasChanged: function FilesStore__fileHasChanged(id) {
        var fileName = this._fileNames[id]
        var file = this._newFile(fileName);
        if (!(file && file.exists()) || this._shouldIgnore(file)) {
            return true;
        } else if (file.isDirectory() || !this._checkPermissions(file)) {
            return false;
        } else {
            // Check if its content has been modified
            var newMd5 = FilesUtils.md5(file);
            var oldMd5 = this._snapshot[id];
            return (newMd5 !== oldMd5);
        }
    },

    /**
     * This returns the IDs of all files that have been added, removed,
     * modified, made inaccessible since the last sync.
     */
    getChangedIDs: function FilesStore_getChangedIDs() {
        this.loadSnapshot();
        var newIDs = [id for (id in this.getAllIDs())
                        if (!(id in this._snapshot))];
        var modifiedIDs = [id for (id in this._snapshot) 
                            if (this._fileHasChanged(id))];
        return newIDs.concat(modifiedIDs);
    },
    
    loadSnapshot: function FilesStore_loadSnapshot() {
        // Loads a directory snapshot from last sync for comparison
        try {
            var json = FilesUtils.jsonLoad(this._snapshotFile);
        } catch(e) {}
        var snapshot = json || {};
        this._snapshot = snapshot;
        return this._snapshot;
    },
    
    saveSnapshot: function FileStore_saveSnapshot() {
        // Invoked right after this Engine has been synced, to store a snapshot
        // of IDs and md5s to the disk. 
        FilesUtils.jsonSave(this._snapshotFile, this._snapshot);
    },
    
    resetSnapshot: function FilesStore_resetSnapshot() {
        FilesUtils.jsonSave(this._snapshotFile, {})
        this._snapshot = {};
    },
    
    _notifications: {},

    _showFileNotification: function FilesStore__showFileNotification(file) {
        file.QueryInterface(Components.interfaces.nsILocalFile);
        if (!(file.path in this._notifications)) {
            let title = "Could not sync file";
            let description = file.path + " from your " + this.name + " could "
                + "not be synced. Please make sure it is readable and writable.";
            let button = new NotificationButton("Show file", null, function() {
                try {
                    file.reveal()
                } catch(e) { /* not every OS supports this */ }
            });
            Notifications.add(
                new Notification(title, description, null, null, [button],
                                 ["sync"])
            );
            this._notifications[file.path] = null;
        }
    },
    
    _checkPermissions: function FilesStore__checkPermissions(file) {
        var permitted = FilesUtils.checkPermissions(file);
        if (!permitted) {
            this._showFileNotification(file);
        }
        return permitted;
    }
}

function FilesTracker(name) {
    Tracker.call(this, name);
    this._log.debug("FilesTracker created: " + name);
}

FilesTracker.prototype = {
    __proto__: Tracker.prototype
}

FilesUtils = {    
    md5: function FilesUtils_md5(input) {
        var md5 = null;
        try {
            var ch = Components.classes["@mozilla.org/security/hash;1"]
                .createInstance(Components.interfaces.nsICryptoHash);
            ch.init(ch.MD5);
            if (typeof input === "string") {
                let bytes = [];
                let i = 0;
                while (i < input.length) {
                    bytes.push(input.charCodeAt(i));
                    i++;
                }
                let result = {};
                ch.update(bytes, bytes.length);
                md5 = ch.finish(true);
            } else {
                let file = input.QueryInterface(Components.interfaces.nsILocalFile);
                if (file.exists() && file.isFile() && this.checkPermissions(file) && file.fileSize > 0) {
                    let fstream = Components.classes["@mozilla.org/network/file-input-stream;1"].
                        createInstance(Components.interfaces.nsIFileInputStream);
                    fstream.init(file, -1, 0, 0);
                    ch.updateFromStream(fstream, 0xffffffff);
                    fstream.close();
                    md5 = ch.finish(true);
                }
            }
        } catch(e) {
            this._log.error("Could not get md5 from file " + file.path);
            this._log.error(e.message);
        } finally {
            return md5;
        }
    },
    
    jsonLoad: function FilesUtils_jsonLoad(file) {
        if (!file.exists()) {
            return null;
        }
        try {
            let [is] = Utils.open(file, "<");
            let json = Utils.readStream(is);
            is.close();
            return JSON.parse(json);
        }
        catch (ex) {
            this._log.debug("Failed to load json: " + Utils.exceptionStr(ex));
            return null;
        }
    },
    
    jsonSave: function FilesUtils_jsonSave(file, json) {
        try {
            let out = JSON.stringify(json);
            let [fos] = Utils.open(file, ">");
            fos.writeString(out);
            fos.close();
        } catch(ex) {
            this._log.debug("Failed to save json: " + Utils.exceptionStr(ex));            
        }
    },
    
    checkPermissions: function FilesUtils_checkPermissions(file) {
        file.QueryInterface(Components.interfaces.nsIFile);
        // XXX Executable for directories?
        if (file.exists())
            return file.isReadable() && file.isWritable();
        else
            return true;
    }
}