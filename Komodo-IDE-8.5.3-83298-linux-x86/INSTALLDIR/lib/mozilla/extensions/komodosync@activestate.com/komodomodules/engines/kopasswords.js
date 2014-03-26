Components.utils.import("resource://services-sync/engines/passwords.js");

const EXPORTED_SYMBOLS = ['KoPasswordEngine'];

function KoPasswordEngine(name) {
    PasswordEngine.call(this);
    this.name = name;
    this._log.debug("KoPasswordEngine created: " + name);
}

KoPasswordEngine.prototype = {
    __proto__: PasswordEngine.prototype,
    
    __rcService: null,
    get _rcService() {
        if (!this.__rcService) {
            this.__rcService =
                Components.classes["@activestate.com/koRemoteConnectionService;1"].
                getService(Components.interfaces.koIRemoteConnectionService);
        }
        return this.__rcService;
    },
    
    _syncFinish: function FilesEngine__syncFinish() {
        // Tell the Remote Connection Service to reset it's cached accounts
        try {
            this._rcService.clearServerInfoListCache();
        } catch(e) {
            this._log.warn("Couldn't clear ServerInfoList cache. You are " +
                           "probably using an old Komodo build.");
        }
        return PasswordEngine.prototype._syncFinish.apply(this, arguments);
    }
}