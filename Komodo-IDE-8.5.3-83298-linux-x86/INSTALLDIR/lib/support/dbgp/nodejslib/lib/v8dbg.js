// Copyright (c) 2011 - 2012 ActiveState Software Inc.
// See the LICENSE file for licensing information.

var _debugger = require('_debugger'),
  Log = require("log"),
  util = require('util');

var log = new Log('error');

/**
 * This extends node's implementation of the v8 debugger protocol (_debugger.js)
 */
function Client() {
  _debugger.Client.apply(this);
}

util.inherits(Client, _debugger.Client);

exports.port = _debugger.port;
exports.Client = Client;

/**
 * Inlines the value of a given object reference by doing a reqLookup.
 */
Client.prototype.inlineObjectRef = function(object, cb) {
  cb = cb || function() {};
  this.reqLookup([object.ref], function(err, res) {
    if (err || !res) {
      log.debug('problem with reqLookup');
      cb(object);
      return;
    }
    
    object.value = res[object.ref];
    cb(object);
  });
};

/*
DON'T use this. The inlined properties are *not* complete.
Client.prototype.reqScopeInline = function(scopeNumber, frameNumber, cb) {
  var req = {
    'command': 'scope',
    'arguments': {
      'number': scopeNumber,
      'inlineRefs': true
    }
  };
  if (typeof frameNumber !== 'undefined' && frameNumber != null)
    req.arguments.frameNumber = frameNumber;
  console.log(scopeNumber + JSON.stringify(req));
  this.req(req, function(res) {
    if (cb) cb(res);
  });
};
*/

Client.prototype.reqScopes = function(frameNumber, cb) {
  var req = {
    'command': 'scopes',
    'arguments': {}
  };
  if (typeof frameNumber !== 'undefined' && frameNumber != null)
    req.arguments.frameNumber = frameNumber;
  this.req(req, function(res) {
    if (cb) cb(res);
  });
};

Client.prototype.reqScopesInline = function(frameNumber, cb) {
  var req = {
    'command': 'scopes',
    'arguments': {
      'inlineRefs': true
    }
  };
  if (typeof frameNumber !== 'undefined' && frameNumber != null)
    req.arguments.frameNumber = frameNumber;
  this.req(req, function(res) {
    if (cb) cb(res);
  });
};

Client.prototype.reqScopeHandles = function(frameNumber, scopeType, cb) {
  // Get all scopes
  this.reqScopes(frameNumber, function(resp) {
    if (!resp || !resp.success){
      console.error('Failed to get scopes');
      return [];
    }
    
    // Build a list of scopes by comparing type with the given contextId and
    // fetching the handle of matching scopes from the refs section
    var scopes = [];
    resp.body.scopes.forEach(function(scope) {
      if (typeof scopeType == 'number' && scope.type != scopeType)
        return;
      
      var handleId = scope.object.ref;
      var scopeObject;
      for (var i = 0; i < resp.refs.length; i++) {
        scopeObject = resp.refs[i];
        if (scopeObject.handle == handleId)
          break;
      }
      if (!scopeObject)
        return;
      scopes.push(scopeObject);
    }, this);
    
    if (cb) cb(scopes);
  });
};

Client.prototype.evaluateExpression = function(expression, frameNo, isGlobal, cb) {
  var req = {
    'command': 'evaluate',
    'arguments': {
      "expression": expression,
      "frame": frameNo,
      "global": isGlobal,
      "disable_break": true,
      "inlineRefs": true
    }
  };
  this.req(req, cb);
};

Client.prototype.reqFrameInline = function(number, cb) {
  var req = {
    'command': 'frame',
    'arguments': { 'inlineRefs': true }
  };
  if (typeof number !== 'undefined' && number != null)
    req.arguments.number = number;
  this.req(req, function(res) {
    if (cb) cb(res);
  });
};

Client.prototype.setExceptionBreak = function(type, enabled, cb) {
  var req = {
    'command': 'setexceptionbreak',
    'arguments': {}
  };
  req.arguments.type = type;
  if (typeof enabled == 'boolean')
    req.arguments.enabled = enabled; // toggles otherwise
  this.req(req, function(res) {
    if (cb) cb(res);
  });
};

/**
 * (Komodo extension method)
 * Fetch the given scripts by id
 * @param types {Number} The types of scripts to fetch; should be a mix of
 *    the _ko_SCRIPT_TYPES constants
 * @param ids {Array or null} The script IDs to fetch; if not given, all scripts
 *    are fetched
 * @param includeSource {Boolean} Whether to fetch script source
 * @param filter {Number or String} If a number, only the script with the given
 *    id will be fetched.  If a script, only scripts whose name contains the
 *    filter string will be fetched.
 * @params sortKey {String} Determines how to index the object given to the
 *    callback; can be any property name of the script objects (e.g. "id"), or
 *    null to use an array in undefined order
 * @param cb {Function} Callback for completion; takes two arguments:
 *    err {Object} Whether an error occurred
 *    result {Object or Array} If sortKey is given, an object with the keys
 *        being the requested property
 *        If sortKey is not given, an array in arbitrary order.
 */
Client.prototype._ko_reqScripts = function(types, ids, includeSource, filter, sortKey, cb) {
  var self = this;
  log.info("requesting scripts...");
  var foundScripts = {}; // indexed by script id
  // If no types are given, assume everything
  types = types || this._ko_SCRIPT_TYPES.ALL;
  /**
   * Fetch basic script information for all relevant scripts (by id); this does
   * not include sources.
   */
  var FetchScriptInfo = function() {
    log.info("FetchScriptInfo");
    if (ids) {
      ids = ids.filter(function(id) {
        if (id in self.scripts) {
          foundScripts[id] = self.scripts[id];
          return false; // No need to fetch the script
        }
        return true; // this id is missing, try fetching it
      });
      if (ids.length) {
        var FetchScriptInfoCallback = function(err, scripts) {
          if (err) {
            cb(err); // Failure
            return;
          }
          scripts.forEach(function(script) {
            self._addHandle(script);
            foundScripts[script.id] = script;
          });
          FilterScripts();
        };
        self.req({command: 'scripts',
                  arguments: {
                    types: types,
                    ids: ids,
                    includeSource: includeSource,
                    filter: filter,
                  }
                 }, FetchScriptInfoCallback);
      } else {
        // We already have everything we need
        FilterScripts();
      }
    } else {
      // Need to fetch everything
      self.reqScripts(function(res) {
        if (res) {
          cb(res); // Failure
        } else {
          Object.keys(self.scripts).forEach(function(scriptId) {
            foundScripts[scriptId] = self.scripts[scriptId];
          });
          FilterScripts();
        }
      })
    }
  };
  var FilterScripts = function() {
    log.info("FilterScripts");
    // Need to manually filter again becuase we might have extra scripts from
    // being cached or we're not given any ids
    if ((typeof filter) == "number") {
      Object.keys(foundScripts).forEach(function(scriptId) {
        if (scriptId != filter) {
          delete foundScripts[scriptId];
        }
      });
    } else if ((typeof filter) == "string") {
      Object.keys(foundScripts).forEach(function(scriptId) {
        if (foundScripts[scriptId].name.indexOf(filter) < 0) {
          delete foundScripts[scriptId];
        }
      });
    }
    GetScriptSources();
  };
  var GetScriptSources = function() {
    log.info("GetScriptSources");
    // Filter scripts by wanted script types
    Object.keys(foundScripts).forEach(function(scriptId) {
      if (!(types & foundScripts[scriptId].scriptType)) {
        delete foundScripts[scriptId]; // Unwanted script type
      }
    });
    if (includeSource) {
      // Try to find the sources for scripts
      var missingSources =
        Object.keys(foundScripts)
              .map(function(scriptId) {return foundScripts[scriptId];})
              .filter(function(script) {return !("source" in script)})
              .map(function(script) {return script.id});
      if (missingSources.length > 0) {
        var GetScriptSourcesCallback = function(err, scripts) {
          if (err) {
            cb(res); // Failure
          } else {
            scripts.forEach(function(script) {
              self._addHandle(script);
              foundScripts[script.id] = script;
            });
            InvokeCallback();
          }
        };
        self.req({command: 'scripts',
                  arguments: {
                    types: types,
                    ids: missingSources,
                    includeSource: true,
                  }
                 }, GetScriptSourcesCallback);
      } else {
        InvokeCallback();
      }
    } else {
      InvokeCallback();
    }
  };
  var InvokeCallback = function() {
    log.info("InvokeCallback");
    var scripts = {};
    if (sortKey) {
      Object.keys(foundScripts).forEach(function(scriptId) {
        scripts[foundScripts[scriptId][sortKey]] = foundScripts[scriptId];
      });
    } else {
      scripts = Object.keys(foundScripts).map(function(scriptId) {
        return foundScripts[scriptId];
      });
    }
    cb(null, scripts);
  };
  FetchScriptInfo();
};
Client.prototype._ko_SCRIPT_TYPES = {NATIVE: 1, EXTENSION: 2, NORMAL: 4,
                                     ALL: 1|2|4};
