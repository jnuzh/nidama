const EXPORTED_SYMBOLS = ['FilesRecord']

Components.utils.import("resource://services-sync/util.js");
Components.utils.import("resource://services-sync/base_records/crypto.js");

function FilesRecord(collection, id) {
    CryptoWrapper.call(this, collection, id);
}

FilesRecord.prototype = {
    __proto__: CryptoWrapper.prototype,
    _logName: "Record.File"
}

Utils.deferGetSet(FilesRecord, "cleartext", ["fileName", "fileContent", "isDirectory"])