Components.utils.import("resource://services-sync/engines/prefs.js");
Components.utils.import("resource://services-sync/util.js");

const EXPORTED_SYMBOLS = ['KoPrefsEngine'];
const KOMODO_SYNC_PREFS = "services.sync.koprefs.sync.";
const WEAVE_PREFS_GUID = "komodoprefs";
const MAJOR_VERSION = Svc.AppInfo.version.split(".")[0];

function KoPrefsEngine() {
    PrefsEngine.call(this);
    this.name = "koprefs";
}

KoPrefsEngine.prototype = {
    __proto__: PrefsEngine.prototype,
    _storeObj: KoPrefStore,
    _trackerObj: KoPrefTracker,
    // We use a different storage collection in Komodo 8, to avoid conflicts
    // with Komodo 7 prefs - bug 96567.
    get engineURL() this.storageURL + this.name + MAJOR_VERSION,
}

function KoPrefStore() {
    PrefsEngine.prototype._storeObj.call(this);
    // TODO add prefs changed observer 
}

KoPrefStore.prototype = {
    __proto__: PrefsEngine.prototype._storeObj.prototype,

    get _prefs() {
        if (!this.__prefs) {
            this.__prefs = Components.classes["@activestate.com/koPrefService;1"].
                            getService(Components.interfaces.koIPrefService).
                            prefs;
        }
        return this.__prefs;
    },
    
    __mozPrefs: null,
    get _mozPrefs() {
        // FIXME Is this a (self-updating) view or a cache?
        if (!this.__mozPrefs) {
            this.__mozPrefs = Components.classes["@mozilla.org/preferences-service;1"].
                                getService(Components.interfaces.nsIPrefService).
                                getBranch(KOMODO_SYNC_PREFS);
        }
        return this.__mozPrefs;
    },

    get _syncPrefs() {
        if (!this.__syncPrefs) {
            this.__syncPrefs = this._mozPrefs.getChildList("", {});
        }
        return this.__syncPrefs;
    },
    
    get _prefsGUID() {
        if (!this.__prefsGUID) {
            // TODO We could make a distinction between IDE and Edit here, but
            // for now let's just sync everything into the same record.
            this.__prefsGUID = WEAVE_PREFS_GUID;
        }
        return this.__prefsGUID;
    },
    
    _getAllPrefs: function PrefStore__getAllPrefs() {
        let values = [];
        let toSync = this._syncPrefs;

        let pref;
        for (let i = 0; i < toSync.length; i++) {
            if (!this._mozPrefs.getBoolPref(toSync[i]))
                continue;

            pref = {};
            pref["name"] = toSync[i];

            switch (this._prefs.getPrefType(toSync[i])) {
            case "long":
                pref["type"] = "long";
                pref["value"] = this._prefs.getLongPref(toSync[i]);
                break;
            case "double":
                pref["type"] = "double";
                pref["value"] = this._prefs.getDoublePref(toSync[i]);
                break;
            case "string":
                pref["type"] = "string";
                pref["value"] = this._prefs.getStringPref(toSync[i]);
                break;
            case "boolean":
                pref["type"] = "boolean";
                pref["value"] = this._prefs.getBooleanPref(toSync[i]);
                break;
            // FIXME What about object type prefs?
            default:
                this._log.trace("Unsupported pref type for " + toSync[i]);
            }
            if ("value" in pref) values[values.length] = pref;
        }

        return values;
    },
    
    _setAllPrefs: function PrefStore__setAllPrefs(values) {
        // cache 
        let enabledBefore = false;
        for (let i = 0; i < values.length; i++) {
            switch (values[i]["type"]) {
            case "long":
                this._prefs.setLongPref(values[i]["name"], values[i]["value"]);
                break;
            case "double":
                this._prefs.setDoublePref(values[i]["name"], values[i]["value"]);
                break;
            case "string":
                this._prefs.setStringPref(values[i]["name"], values[i]["value"]);
                break;
            case "boolean":
                this._prefs.setBooleanPref(values[i]["name"], values[i]["value"]);
                break;
            // FIXME what about object type prefs?
            default:
                this._log.trace("Unexpected preference type: " + values[i]["type"]);
            }
        }
        // TODO Anyone we should notify here?
    }
}

function KoPrefTracker(name) {
    PrefsEngine.prototype._trackerObj.call(this, name);
    Svc.Obs.add("weave:engine:start-tracking", this);
    Svc.Obs.add("weave:engine:stop-tracking", this);
}

KoPrefTracker.prototype = {
    __proto__: PrefsEngine.prototype._trackerObj.prototype,

    get _prefs() {
        if (!this.__prefs) {
            this.__prefs = Components.classes["@activestate.com/koPrefService;1"].
                            getService(Components.interfaces.koIPrefService).
                            prefs;
        }
        return this.__prefs;
    },
    
    __mozPrefs: null,
    get _mozPrefs() {
        // FIXME Is this a (self-updating) view or a cache?
        if (!this.__mozPrefs) {
            this.__mozPrefs = Components.classes["@mozilla.org/preferences-service;1"].
                                getService(Components.interfaces.nsIPrefService).
                                getBranch(KOMODO_SYNC_PREFS);
        }
        return this.__mozPrefs;
    },

    get _syncPrefs() {
        if (!this.__syncPrefs) {
            this.__syncPrefs = this._mozPrefs.getChildList("", {});
        }
        return this.__syncPrefs;
    },

    observe: function(aSubject, aTopic, aData) {
        switch (aTopic) {
        case "weave:engine:start-tracking":
            if (!this._enabled) {
                this._prefs.prefObserverService.addObserverForTopics(this,
                                                                     this._syncPrefs.length,
                                                                     this._syncPrefs,
                                                                     false);
                this._enabled = true;
            }
            break;
        case "weave:engine:stop-tracking":
            if (this._enabled) {
                this._prefs.prefObserverService.removeObserverForTopics(this,
                                                                        this._syncPrefs.length,
                                                                        this._syncPrefs);
                this._enabled = false;
            }
            break;
        default:
            this.score += 10;
            this.modified = true;
            this.addChangedID(WEAVE_PREFS_GUID);
            this._log.trace("Preference " + aData + " changed");
            break;
        }
    }
}
