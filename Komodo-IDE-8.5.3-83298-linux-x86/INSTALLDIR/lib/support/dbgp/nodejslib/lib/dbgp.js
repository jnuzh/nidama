// Copyright (c) 2011 - 2012 ActiveState Software Inc.
// See the LICENSE file for licensing information.

var v8dbg = require('./v8dbg'),
    cmdln = require('./cmdln'),
    util = require('util'),
    events = require('events'),
    net = require('net'),
    path = require('path'),
    url = require('url'),
    os = require('os'),
    assert = require('assert'),
    Log = require('log');

var log = new Log('error');

var DBGP_ERROR_CODES = {
  'INVALID_OPTIONS': 3,
  'BREAKPOINT_COULD_NOT_BE_SET': 200,
  'BREAKPOINT_TYPE_NOT_SUPPORTED': 201,
  'BREAKPOINT_INVALID': 202,
  'NO_CODE_ON_BREAKPOINT_LINE': 203,
  'INVALID_BREAKPOINT_STATE': 204,
  'NO_SUCH_BREAKPOINT': 205,
  'ERROR_EVALUATING_CODE': 206,
  'INVALID_EXPRESSION': 207,
  'CANNOT_GET_PROPERTY': 300,
  'STACK_DEPTH_INVALID': 301,
  'CONTEXT_INVALID': 302,
  'INTERNAL_ERROR': 998,
  'UNKNOWN_ERROR': 999
};

var V8_SCOPE_TYPES = {
  0: 'Global',
  1: 'Local',
  2: 'With',
  3: 'Closure',
  4: 'Catch'
};

var DBGP_CONTEXT_IDS = {
  // Map DBGP context IDs to V8 scope types, so we can use 0 for locals.
  0: 1, // Local
  1: 2, // With
  2: 3, // Closure
  3: 4, // Catch
  4: 0  // Global
};

var DBGP_TYPEMAP = {
  'undefined': 'undefined',
  'null': 'object',
  'boolean': 'bool',
  'number': 'float',
  'string': 'string',
  'object': 'object',
  'function': 'function'
}

var INTERNAL_GLOBAL_NAMES = [
  "Array", "Boolean", "Buffer", "clearInterval", "clearTimeout", "console",
  "Date", "decodeURI", "decodeURIComponent", "encodeURI",
  "encodeURIComponent", "Error", "escape", "eval", "EvalError", "execScript",
  "Function", "GLOBAL", "global", "Infinity", "isFinite", "isNaN", "JSON",
  "Math", "NaN", "Number", "Object", "parseFloat", "parseInt", "process",
  "RangeError", "ReferenceError", "RegExp", "root", "setInterval",
  "setTimeout", "String", "SyntaxError", "TypeError", "undefined", "unescape",
  "URIError", "v8debug"
];

var INTERNAL_LOCAL_NAMES = [
    "__dirname", "__filename", "exports", "module", "require"
];

//function ts(o) {
//    var s = JSON.stringify(o);
//    var lim = 100;
//    if (s.length > lim) {
//        s = s.substr(0, lim) + "...";
//    }
//    return s;
//}

function Client(engine) {
  net.Socket.call(this);
  this.engine = engine;
  this.setEncoding('ascii');

  this._messageChunk = '';
  this.on('data', function(data) {
    log.info('Got a chunk: ' + data);
    this._messageChunk += data;
    var eom, messages = [];
    while ((eom = this._messageChunk.indexOf('\x00')) != -1) {
        messages.push(this._messageChunk.slice(0, eom));
        this._messageChunk = this._messageChunk.slice(eom+1);
    }
    messages.forEach(function(msg) {
        this.engine.handleMessage(msg);
    }.bind(this));
  });

  this.on('closed', function() {
    this.engine.emit('dbgpClosed');
  });
}

util.inherits(Client, net.Socket);

Client.prototype.sendPacket = function(xml) {
  var packet = '';
  packet += xml.length + '\x00' + xml + '\x00';
  this.write(packet);
  log.info("Message packet sent: " + packet);
};

exports.Client = Client;

function Engine(debuggee, fileUri, port, host) {
  events.EventEmitter.apply(this);

  this.init(debuggee, fileUri, port, host);

  // Wait a bit before connecting, so that v8 has a chance to open a socket.
  // This will emit the 'ready' event when successful.
  setTimeout(function() {
    this.v8Client.connect(v8dbg.port);
  }.bind(this), 100);
}

util.inherits(Engine, events.EventEmitter);

(function() {
  this.init  = function(child, fileUri, port, host) {
    this.fileUri = fileUri;
    this.port = port;
    this.host = host; // may be undefined; that's okay.
    this.status = 'starting';
    this.reason = 'ok';
    this.stdout = 0; // 0-disable, 1-copy data, 2-redirect

    this._initV8Client();
    this._initDBGPClient();
    this._initChild(child);
    assert.ok(this.child);
  };

  this._initV8Client = function() {
    this.v8Client = new v8dbg.Client();

    this.v8Client.once('ready', function(resp) {
      this.v8Client.req({command: 'setexceptionbreak',
                         arguments: {type: 'uncaught', enabled: true}},
                        function(err, resp) {
        if (err) {
          log.error("Failed to initialize v8 debugger, aborting.");
          this.terminate();
        } else {
          // Some times the initial breakpoint hasn't been reached yet; wait a
          // bit to make sure that happens.  Mostly happens on Windows, but this
          // has been observed on OSX too.
          setTimeout(function() {
            log.info('dbgp ready');
            this.emit('ready');
          }.bind(this), 100);
        }
      }.bind(this))
    }.bind(this));

    this.v8Client.on('break', function(resp) {
      resp = resp.body;
      log.info('V8 Debugger Client ran into breakpoint:\n\t' +
        resp.sourceLine + ':' + resp.sourceColumn + ' ' + resp.sourceLineText);
      for (var p in resp) {
        log.info(p + ": " + String(resp[p]).split(/\r\n?|\n/)[0]);
      }
      log.info("resp.script: " );
      for (var p in resp.script) {
        log.info("  " + p + ": " + resp.script[p]);
      }
      this.status = 'break';
      this.reason = 'ok';
      this.emit('v8ExecutionStopped');
    }.bind(this));

    this.v8Client.on('exception', function(resp) {
      // Note that this only works for uncaught exceptions.
      // TODO This doesn't fire on my machine. Looks like a v8 bug to me.
      resp = resp.body;
      log.error('Debuggee process ran into uncaught exception:\n\t' +
        resp.script.name + ':' + resp.sourceLine + ':' + resp.sourceColumn +
        ' ' + resp.sourceLineText);
      this.status = 'break';
      this.reason = 'exception';
      this.emit('v8ExecutionStopped');
    }.bind(this));

    this.v8Client.on('error', function(e) {
      log.debug("V8 Debugger Client error: " + e.message);
      this.status = 'stopped';
      this.reason = 'error';
      this.emit('v8ExecutionStopped');
    }.bind(this));

    this.v8Client.on('close', function() {
      log.info('V8 Debugger Client closed');
      this.status = 'stopped';
      this.reason = 'ok';
      this.emit('v8ExecutionStopped');
    }.bind(this));

  };

  this._initDBGPClient = function() {
    this.dbgpClient = new Client(this);

    this.dbgpClient.on('connect', function() {
      log.info('DBGP client connected');

      this.dbgpClient.sendPacket(this.makeInit());
    }.bind(this));

    this.dbgpClient.on('close', function() {
      log.info('DBGP client disconnected');
      this.emit('exit');
    }.bind(this));
  };

  this._initChild = function(childProcess) {
    this.child = childProcess; // the debuggee child process

    this.child.on('exit', function() {
      this.status = 'stopping';
      log.info('Child process exited');
      this.emit('v8ExecutionStopped');
    }.bind(this));

    this.child.stdout.on('data', function(data) {
      if (this.stdout== 0)
        process.stdout.write(data);
      else if (this.stdout == 1)
        this.stdoutCopy(data);
      else if (this.stdout == 2)
        this.stdoutRedirect(data);
    }.bind(this));

    this.child.stderr.on('data', function(data) {
      if (this.stderr == 0)
        process.stderr.write(data);
      else if (this.stderr == 1)
        this.stderrCopy(data);
      else if (this.stderr == 2)
        this.stderrRedirect(data);
    }.bind(this));
  };


  /**
   * Features that are supported in feature_get
   */
  this._readOnlyFeatures = {
    'breakpoint_types': 'line', // TODO implement more breakpoint_types
    'data_encoding': 'base64',
    'encoding': 'utf-8',
    'language_supports_threads': '0',
    'language_name': 'Node.js',
    'language_version': '' + process.version,
    'multiple_sessions': '0',
    'protocol_version': '1',
    'supports_async': '1',
    'supports_postmortem': '1',
    // TODO make writable.
    // must either be limited or we should stop printing function definitions
    'max_data': 30000
  };

  /**
   * Features that are supported in feature_get and feature_set
   */
  this._writableFeatures = {
    'max_children': 25,
    'max_depth': 0,
    'show_hidden': 0
  };

  this.getFeature = function(name) {
    if (this._readOnlyFeatures.hasOwnProperty(name)) {
      return this._readOnlyFeatures[name];
    } else if (this._writableFeatures.hasOwnProperty(name)) {
      return this._writableFeatures[name];
    } else {
      return undefined;
    }
  };

  this.setFeature = function(name, value) {
    if (this._writableFeatures.hasOwnProperty(name)) {
      this._writableFeatures[name] = value;
      return true;
    } else {
      return false;
    }
  };


  /**
   * ----- DBGP procotol message handlers
   */

  this.on('feature_get', function(args) {
    if (!("n" in args)) {
      this.sendUnsuccessfulResponse('feature_get', args['i'], null,
                                    this.makeError(DBGP_ERROR_CODES.INVALID_OPTIONS,
                                                   "No feature name given"),
                                    true);
      return;
    }
    var featureName = '' + args['n'];
    var response = {feature_name: featureName};
    var featureValue, message = "";
    if (!featureName) {
      message = this.makeError(DBGP_ERROR_CODES['INVALID_OPTIONS'],
                               'missing parameter');
    } else {
      featureValue = this.getFeature(featureName);
      if (typeof featureValue !== 'undefined') {
        message = featureValue;
        response['supported'] = '1';
      } else if (featureName in this._events) {
        response['supported'] = '1';
      } else {
        response['supported'] = '0';
      }
    }
    this.sendResponse('feature_get', args['i'], response, '' + message);
  });

  this.on('feature_set', function(args) {
    if (!("n" in args)) {
      this.sendUnsuccessfulResponse('feature_get', args['i'], null,
                                    this.makeError(DBGP_ERROR_CODES.INVALID_OPTIONS,
                                                   "No feature name given"),
                                    true);
      return;
    }
    if (!("v" in args)) {
      this.sendUnsuccessfulResponse('feature_get', args['i'], null,
                                    this.makeError(DBGP_ERROR_CODES.INVALID_OPTIONS,
                                                   "No feature value given"),
                                    true);
      return;
    }
    var featureName = '' + args['n'];
    var newValue = args['v'];
    var message = null;
    var response = { featureName: featureName, success: 0 };
    var errorCode, status = 0, success = 0;
    if (!featureName) {
      errorCode = 'INVALID_OPTIONS';
      message = 'missing parameter';
    } else if (this._readOnlyFeatures.hasOwnProperty(featureName)) {
      message = 'Command ' + featureName + ' not modifiable';
      // This is not an error condition -- just let the client know the feature wasn't changed.
    } else if (isNaN(newValue = parseInt(newValue, 10))) {
      // only numerical features at this point
      errorCode = 'INVALID_OPTIONS';
      message = 'invalid value';
    } else if (!this.setFeature(featureName, newValue)) {
      errorCode = 'INVALID_OPTIONS';
      message = 'Unknown feature name';
    } else {
      response['success'] = '1';
    }
    if (errorCode) {
      log.info("feature_set: got message:"
                  + message
                  + ", errorCode:"
                  + errorCode);
      message = this.makeError(DBGP_ERROR_CODES[errorCode],
                               message);
      this.sendUnsuccessfulResponse('feature_set', args['i'],
                                    {'feature_name': args['n']}, message, true);
    } else {
      log.info("feature_set: "
                  + featureName
                  + " succeeded");
      this.sendResponse('feature_set', args['i'], response);
    }
  });

  this.on('status', function(args) {
    this.sendStatusResponse('status', args['i']);
  });

  this.on('run', function(args) {
    log.info('Starting debuggee...');
    this.v8Client.reqContinue(function(err, resp) {
      if (!err && resp.running) {
        log.info('debuggee running!');
        this.status = 'running';
        this.reason = 'ok';
        this.once('v8ExecutionStopped', function() {
          this.sendStatusResponse('run', args['i']);
        }.bind(this));
      } else {
        this.status = 'stopped';
        this.reason = 'error';
        this.sendStatusResponse('run', args['i'], null,
          this.makeError(DBGP_ERROR_CODES.UNKNOWN_ERROR, err || JSON.stringify(resp)), true);
      }
    }.bind(this));
  });

  this.on('step_into', function(args) {
    this._firstBreak = true;
    this.v8Client.step('in', 1, function(err, resp) {
      if (!err && resp.success&& resp.running) {
        log.info('debuggee running!');
        this.status = 'running';
        this.reason = 'ok';
        this.once('v8ExecutionStopped', function() {
          this.sendStatusResponse('step_into', args['i']);
        }.bind(this));
      } else {
        this.status = 'stopped';
        this.reason = 'error';
        this.sendStatusResponse('step_into', args['i']);
      }
    }.bind(this));
  });

  this.on('step_over', function(args) {
    this.v8Client.step('next', 1, function(err, resp) {
      if (!err && resp.success && resp.running) {
        this.status = 'running';
        this.reason = 'ok';
        this.once('v8ExecutionStopped', function() {
          this.sendStatusResponse('step_over', args['i']);
        }.bind(this));
      } else {
        this.status = 'stopped';
        this.reason = 'error';
        this.sendStatusResponse('step_over', args['i']);
      }
    }.bind(this));
  });

  this.on('step_out', function(args) {
    this.v8Client.step('out', 1, function(err, resp) {
      if (!err && resp.success&& resp.running) {
        this.status = 'running';
        this.reason = 'ok';
        this.once('v8ExecutionStopped', function() {
          this.sendStatusResponse('step_out', args['i']);
        }.bind(this));
      } else {
        this.status = 'stopped';
        this.reason = 'error';
        this.sendStatusResponse('step_out', args['i']);
      }
    }.bind(this));
  });

  this.on('stop', function(args) {
    log.info('Stopping debuggee...');
    if (this.child) {
      // Kill the debuggee process, tell the IDE that the session stopped.
      this.once('v8ExecutionStopped', function() {
	this.status = 'stopped';
	this.reason = 'ok';
        this.sendStatusResponse('stop', args['i']);
        this.dbgpClient.end();
      }.bind(this));
      this.child.kill();
      this.child = null;
    } else {
      this.sendStatusResponse('stop', args['i']);
    }
  });

  this.on('stack_get', function stack_get(args) {
    var stackDepth = args['d'];

    // XXX marky: Avoid using this.v8Client.fullTrace, it tries to look up
    // things like the receiver, which we don't care about.
    this.v8Client.reqBacktrace(function(err, trace) {
      if (err) {
        this.sendUnsuccessfulResponse('stack_get', args['i'], null,
          this.makeError(DBGP_ERROR_CODES.INTERNAL_ERROR, err), true);
        return;
      }
      if (!trace.frames || !trace.frames.length) {
        this.sendUnsuccessfulResponse('stack_get', args['i'], null,
          this.makeError(DBGP_ERROR_CODES.CANNOT_GET_PROPERTY), true)
      }
      var frames = [];
      var scripts = {};

      this.v8Client._ko_reqScripts(
        this.v8Client._ko_SCRIPT_TYPES.ALL,
        trace.frames.map(function(frame) {return frame.func.scriptId;}),
        /* source? */ false, /* filter */ null, /* key */ "id",
        function (err, scripts) {
          if (err || !scripts) {
            this.sendUnsuccessfulResponse('stack_get', args['i'], null,
              this.makeError(DBGP_ERROR_CODES.INTERNAL_ERROR, err), true);
            return;
          }

          // Collect requested frames
          if (stackDepth >= 0) {
            // Requested a single frame
            for (var i = 0; i < trace.frames.length; i++) {
              var frame = trace.frames[i];
              frame.script = scripts[frame.func.scriptId];
              if (!frame.script || frame.script.isNative) {
                // Note that we currently don't expose node-internal stuff.
                // This might change.
                continue;
              } else if (frame.index == stackDepth) {
                frames.push(frame);
                break;
              }
            }
            if (frames.length != 1) {
              // Requested stack depth is invalid.
              this.sendUnsuccessfulResponse('stack_get', args['i'], null,
                this.makeError(DBGP_ERROR_CODES.STACK_DEPTH_INVALID), true);
              return;
            }
          } else {
            // Requested a full stack trace
            for (var i = 0; i < trace.frames.length; i++) {
              var frame = trace.frames[i];
              frame.script = scripts[frame.func.scriptId];
              if (!frame.script || frame.script.isNative)
                continue;
              else
                frames.push(frame);
            }
          }

          // Make a DBGP stack trace and send as reponse
          var framesStr = '';
          for (var i = 0; i < frames.length; i++) {
            var frame = frames[i];
            frame.line += 1; // V8 starts indexing at 0
            framesStr += this.makeFrame(frame.index, 'file', frame.script.name,
                                        frame.line, frame.func.inferredName);
          }
          this.sendResponse('stack_get', args['i'], {
            'success': '1'
          }, framesStr, true);

        }.bind(this));
    }.bind(this));
  });


  this.on('breakpoint_set', function(args) {
    // Only partially implemented.
    var type = args['t'],
        state = (args['s'] != 'disabled'),
        uri = args['f'],
        lineno = parseInt(args['n'], 10);

    var target = this._filepathFromUri(uri);
    // V8 starts indexing lines at 0:
    lineno -= 1;
    var func = args['m'];
    switch (type) {
      case 'line':
        this.v8Client.setBreakpoint({
            'type': 'script',
            'target': target,
            'line': lineno,
            'column': 0,
            'enabled': state,
          }, function(err, res) {
            if (!err && res) {
              this.sendResponse('breakpoint_set', args['i'],
                                { 'id': res.breakpoint,
                                  'state': state ? 'enabled' : 'disabled' });
            } else {
              var error = this.makeError(DBGP_ERROR_CODES.BREAKPOINT_COULD_NOT_BE_SET,
                                         err);
              this.sendResponse('breakpoint_set', args['i'], { 'status': 'disabled' },
                                error, true);
            }
          }.bind(this));
        break;
      default:
        var error = this.makeError(DBGP_ERROR_CODES['BREAKPOINT_TYPE_NOT_SUPPORTED']);
        this.sendResponse('breakpoint_set', args['i'], { 'status': 'disabled' },
                          error, true);
    }
  });

  /*
  this.on('breakpoint_get', function(args) {

  });
  */

  this.on('breakpoint_update', function(args) {
    if (!('d' in args)) {
      sendError.call(this, DBGP_ERROR_CODES.INVALID_OPTIONS,
                     "No breakpoint to update");
      return;
    }
    var breakpointId = parseInt(args['d'], 10),
        state = args['s'],
        hitValue = parseInt(args['h'], 10);

    if (('n' in args) || ('o' in args && args.o != '>=')) {
      // Unsupported arguments
      sendError.call(this,
                     DBGP_ERROR_CODES['BREAKPOINT_TYPE_NOT_SUPPORTED'],
                     "V8 debugger does not support the specified operation");
      return;
    }

    var bpArgs = {
      command: 'changebreakpoint',
        arguments: {
        breakpoint: breakpointId,
        enabled: state != 'disabled',
        ignoreCount: (hitValue >= 0) ? hitValue : 0,
      },
    };

    this.v8Client.req(bpArgs, function cb(err, resp) {
      if (!err && resp && resp.success) {
        this.sendResponse('breakpoint_update', args['i'], {success: 1}, null, true);
      } else {
        sendError.call(this, DBGP_ERROR_CODES.BREAKPOINT_COULD_NOT_BE_SET);
      }
    }.bind(this));

    function sendError(errorCode, message) {
      var error = this.makeError(errorCode, message);
      this.sendUnsuccessfulResponse('breakpoint_update', args['i'], null, error, true);
    }
  });

  this.on('breakpoint_remove', function(args) {
    var id = args['d'];
    this.v8Client.clearBreakpoint({
      'breakpoint': id
    }, function(res) {
      if (res && res.success && res.body) {
        this.sendResponse('breakpoint_remove', args['i']);
      } else {
        var error = this.makeError(DBGP_ERROR_CODES['BREAKPOINT_COULD_NOT_BE_SET']);
        this.sendResponse('breakpoint_set', args['i'], { 'status': 'disabled' },
                          error, true);
      }
    }.bind(this));
  });

  this.on('breakpoint_list', function(args) {
    var id = args['d'];
    this.v8Client.listbreakpoints(function(err, res) {
      if (err || !res || !res.breakpoints) {
        var error = this.makeError(DBGP_ERROR_CODES.UNKNOWN_ERROR, err);
        this.sendResponse('breakpoint_list', args['i'], null, error, true);
        return;
      }
      var resultStrings = [];
      res.breakpoints.forEach(function(bp) {
        resultStrings.push(this.makeBreakpoint(bp.number, {
          type: 'line',
          state: bp.active ? "enabled" : "disabled",
          filename: bp.script_name,
          lineno: bp.line + 1, // V8 is 0-based, dbgp is 1-based
          hit_count: bp.hit_count,
        }));
      }.bind(this));
      this.sendResponse('breakpoint_list', args['i'], {},
                        resultStrings.join("\n"), true);
    }.bind(this));
  });

  this.on('stdout', function(args) {
    var target = parseInt(args['c'], 10);
    if ([0,1,2].indexOf(target) != -1) {
      this.stdout = target;
      this.sendResponse('stdout', args['i'], { 'success': 1 });
    } else {
      this.sendUnsuccessfulResponse('stdout', args['i']);
    }
  });

  this.on('stderr', function(args) {
    var target = parseInt(args['c'], 10);
    if ([0,1,2].indexOf(target) != -1) {
      this.stderr = target;
      this.sendResponse('stderr', args['i'], { 'success': 1 });
    } else {
      this.sendUnsuccessfulResponse('stderr', args['i']);
    }
  });

  this.on('property_get', function(args) {
    // TODO respect other parameters such as max_children/pages
    // TODO use frameReceiver when asked for `this`
    var propertyName = args['n'];
    var contextId = parseInt(args['c'], 10) || 0;
    var scopeId = this._scopeForContext(contextId);
    var stackDepth = parseInt(args['d'], 10) || 0;
    this.pageIndex = parseInt(args['p']) || 0;
    this.pageSize = this.getFeature('max_children') || 25;

    if (!propertyName || !(scopeId >= 0) || !(stackDepth >= 0)) {
      sendError.call(this, DBGP_ERROR_CODES.INVALID_OPTIONS, 'invalid options');
      return;
    }

    var isGlobal = scopeId == 0;
    var sendPropertyGetResponse = function(propertiesStr) {
      this.sendResponse('property_get', args['i'], null, propertiesStr, true);
    }.bind(this);
    var sendPropertyGetError = function(code, message) {
      var error = this.makeError(code, message);
      this.sendUnsuccessfulResponse('property_get', args['i'], null, error, true);
    }.bind(this);
    var callbacks = {
      onSuccess: sendPropertyGetResponse,
      onFailure: sendPropertyGetError
    };
    this.v8Client.reqFrameEval(propertyName, isGlobal ? -1 : stackDepth,
      function(err, res) {
        if (err || !res) {
          var reason;
          if (err) {
            reason = err;
          } else if (!res) {
            reason = 'invalid stack depth';
          } else {
            reason = ("can't evaluate " + propertyName + " at stack " + stackDepth);
          }
          sendPropertyGetError.call(this, DBGP_ERROR_CODES.INVALID_EXPRESSION, reason);
          return;
        }
        if (!res.name) res.name = propertyName;
        this.makeProperty(res, propertyName,
                          this.getFeature('max_depth') || 1, callbacks);
      }.bind(this));

    function sendError(errorCode) {
      var error = this.makeError(errorCode);
      this.sendResponse('property_get', args['i'], null, errorCode, true);
    }
  });

  this.on('property_value', function(args) {
    var propertyName = args['n'];
    var contextId = parseInt(args['c'], 10) || 0;
    var scopeId = this._scopeForContext(contextId);
    var stackDepth = parseInt(args['d'], 10);

    if (!propertyName || !(scopeId >= 0) || !(stackDepth >= 0)) {
      sendError.call(this, DBGP_ERROR_CODES.INVALID_OPTIONS, 'invalid options');
      return;
    }

    var isGlobal = scopeId == 0;
    var jsonExpression = "JSON.stringify(" + propertyName + ")";
    this.v8Client.evaluateExpression(jsonExpression, stackDepth, isGlobal,
      function(resp) {
        var resValue;
        if (!resp) {
          sendError.call(this, DBGP_ERROR_CODES.ERROR_EVALUATING_CODE, "Can't evaluate " + propertyName);
          return;
        } else if ((!resp.body || !resp.success) && resp.message) {
          resValue = propertyName + ": " + resp.message;
        } else {
          resValue = resp.body.text.toString();
        }
        resValue = this.makeSafeCdataMarkedSection(resValue);
        this.sendResponse('property_value', args['i'], null, resValue, false);
      }.bind(this));
    function sendError(errorCode, message) {
      var error = this.makeError(errorCode, message);
      this.sendUnsuccessfulResponse('property_value', args['i'], null, error, true);
    }
  });
    
  this.builtinTypes = ["undefined", "null", "boolean", "number", "string", "function"];

  this.on('context_names', function(args) {
    // Hard-wired to always send all of V8's scope names
    var contexts = '';
    for (var id in DBGP_CONTEXT_IDS) {
      var v8Id = DBGP_CONTEXT_IDS[id];
      var name = V8_SCOPE_TYPES[v8Id];
      if (typeof name !== 'string') {
        log.error("DBGP context with id " + id + " is not a V8 scope.")
      }
      contexts += this.makeContext(id, name);
    }
    this.sendResponse('context_names', args['i'], null, contexts, true);
  });

  this.on('context_get', function(args) {
    var contextId = parseInt(args['c'], 10) || 0;
    var scopeId = this._scopeForContext(contextId);
    var stackDepth = parseInt(args['d'], 10);

    this.v8Client.req({command: 'frame',
                       arguments: {number: stackDepth}},
                      function(err, frame) {
      var sendContextGetResponse = function(propertiesStr) {
        this.sendResponse('context_get', args['i'], null, propertiesStr, true);
      }.bind(this);
      
      var sendContextGetError = function(code, message) {
        var error = this.makeError(code, message);
        this.sendUnsuccessfulResponse('context_get', args['i'], null, error, true);
      }.bind(this);
      
      if (err || !frame) {
        sendContextGetError(DBGP_ERROR_CODES.INVALID_OPTIONS,
                            err || 'stack depth invalid');
        return;
      }

      var scopes = frame.scopes || [];
      var scopeNumber;
      scopes.forEach(function(scope) {
        if (scope.type == scopeId) {
          scopeNumber = scope.index;
          log.debug("Found scope, number " + scopeNumber);
        }
      }.bind(this));

      if (typeof scopeNumber === "undefined") {
        // Probably temporarily not applicable, like "with" or "catch" scopes
        this.sendResponse('context_get', args['i'], null, '', false);
        return;
      }

      this.v8Client.req({command: 'scope',
                         arguments: {number: scopeNumber,
                                     framenumber: stackDepth}},
                        function(err, resp) {
        if (err || !resp) {
          log.debug("Failed to get scope");
          sendContextGetError(DBGP_ERROR_CODES.INVALID_OPTIONS,
                              err || 'context id invalid');
          return;
        }

        this.v8Client.reqLookup([resp.object.ref], function(err, scopes){
          if (err || !scopes) {
            log.debug("Failed to lookup scope");
            sendContextGetError(DBGP_ERROR_CODES.INVALID_OPTIONS,
                                err || 'failed to lookup scope');
          }
          var scope = scopes[resp.object.ref];
          log.debug("got scope #" + scopeId + ": " + util.inspect(scope, {colors: true}));

          // If the local scope was requested, include a reference to the frame's
          // receiver object as `this`.
          if (scopeId == 1) { // local
            var thisRef = {
              "name": "this",
              "ref": frame.receiver.ref,
            };
            scope.properties.push(thisRef);
          }

          if (scopeId == 0) { // global
            this._filterGlobalScope(scope);
          } else if (scopeId == 1) { // local
            this._filterLocalScope(scope);
          }

          var maxDepth = this.getFeature('max_depth') || 1;

          var ContextGetResponse = function() {
            var callbacks = {
              onFailure: sendContextGetError
            };
            var contextProperties = scope.properties;
            if (/[v ]0\.6\./.test(process.version)) {
              // For Node 0.6 on Darwin, sometimes we get a crazy empty-name property...
              contextProperties = contextProperties.filter(function(n) { return n.name} );
            }
            log.debug("contextProperties: " + util.inspect(contextProperties, {colors: true}));
            var contextPropertyStrings = []; // tuple of (property, string)
            var wrapPropertyStrings = function wrapPropertyStrings() {
              sendContextGetResponse(contextPropertyStrings
                .sort(function(a, b) { return a[0].name.localeCompare(b[0].name); })
                .map(function(a) { return a[1]; })
                .join("\n"));
            }.bind(this);

            var cpsCallbacks = {
              onFailure: sendContextGetError
            };
            var collectPropertyStrings = function(ix) {
              var cb = function(propertyStr) {
                if (propertyStr) {
                  contextPropertyStrings.push([contextProperty, propertyStr]);
                } else {
                  log.debug("Failed to get property string for " +
                            contextProperty.name);
                }
                ix += 1;
                if (ix < contextProperties.length) {
                  collectPropertyStrings(ix);
                } else {
                  wrapPropertyStrings();
                }
              }.bind(this);
              cpsCallbacks.onSuccess = cb;
              var contextProperty = contextProperties[ix];
              if (contextProperty.name == "this"
                  && contextProperty.value
                  && contextProperty.value.type =="object"
                  && contextProperty.value.className =="global") {
                // skip the global 'this'
                cb(null, null);
                return;
              }
              this.pageIndex = 0;
              this.pageSize = this.getFeature('max_children') || 25;
              if (!contextProperty.value) {
                cb = function(inlinedProperty) {
                  this.makeProperty(inlinedProperty.value, contextProperty.name, 0,
                                    cpsCallbacks);
                }.bind(this);
                this.v8Client.inlineObjectRef(contextProperty, cb);
              } else {
                this.makeProperty(contextProperty.value, contextProperty.name, 0,
                                  cpsCallbacks);
              }

            }.bind(this);
            if (contextProperties.length) {
              collectPropertyStrings(0);
            } else {
              wrapPropertyStrings();
            }
          }.bind(this);

          this.v8Client.reqLookup(scope.properties.map(function(p) {return p.ref}),
            function(err, props) {
              scope.properties.forEach(function(property) {
                if ((property.ref in props) && !("value" in property)) {
                  property.value = props[property.ref]
                }
              });
              ContextGetResponse();
            });
        }.bind(this));
      }.bind(this));
    }.bind(this));
  });

  this.on('source', function(args) {
    var uri = args['f'];
    try {
      var filename = this._filepathFromUri(uri);
    } catch(e) {
      // Might fail if, for example, this is from eval()
      this.sendUnsuccessfulResponse('source', args['i']);
      return;
    }
    this.v8Client._ko_reqScripts(0, null, true, filename, null, function(err, scripts) {
      if (err) {
        this.sendUnsuccessfulResponse('source', args['i'], null,
          this.makeError(DBGP_ERROR_CODES.UNKNOWN_ERROR, err), true);
        return;
      }
      scripts = scripts.filter(function(script) {return script.name == filename;});
      if (scripts.length) {
        this.sendResponse('source', args['i'], {success: 1}, scripts[0].source, false);
      } else {
        this.sendUnsuccessfulResponse('source', args['i']);
      }
    }.bind(this));
  });

  this.on('typemap_get', function(args) {
    var response = '';
    for (var typeName in DBGP_TYPEMAP) {
      var typeValue = DBGP_TYPEMAP[typeName];
      response += this.makeType(typeName, typeValue);
    }
    this.sendResponse('typemap_get', args['i'], null, response, true);
  });


  /**
   * ----- Helper functions
   */

  /**
   * Make a <response> message that contains the given command and transaction
   * id, as well as the other given parameters, and message (which can be an
   * xml string or data for a CDATA entity). Then send it.
   */
  this.sendResponse = function(cmd, transactionId, parameters, message, xml) {
    var response = this.makeResponse(cmd, transactionId, parameters, message, xml);
    this.dbgpClient.sendPacket(response);
  };

  /**
   * `sendResponse()` with success="0".
   */
  this.sendUnsuccessfulResponse = function(cmd, transactionId, parameters, message, xml) {
    if (!parameters)
      parameters = {};
    parameters['success'] = 0;
    this.sendResponse(cmd, transactionId, parameters, message, xml);
  };

  /**
   * `sendResponse()` with status=`this.status` and reason=`this.reason`.
   */
  this.sendStatusResponse = function(cmd, transactionId, parameters, message, xml) {
    if (!parameters)
      parameters = {};
    parameters.status = this.status;
    parameters.reason = this.reason;
    this.sendResponse(cmd, transactionId, parameters, message, xml);
  };

  /**
   * Make a <response> message with the given parameters and message. The
   * message can be an xml string or data, which will be base64-encoded.
   */
  this.makeResponse = function(cmd, transactionId, parameters, message, xml) {
    if (!parameters)
      parameters = {};
    parameters['command'] = cmd;
    parameters['transaction_id'] = transactionId;
    if (this.getFeature('data_encoding') == 'base64')
      parameters['encoding'] = 'base64';
    message = message || '';
    var response = '<?xml version="1.0" encoding="UTF-8"?>';
    response += '<response xmlns="urn:debugger_protocol_v1" ';
    for (var name in parameters) {
      // FIXME needs escaping
      var value = parameters[name];
      response += name + '="' + value + '" ';
    }
    response = response.trimRight();
    if (message) {
      response += ">";
      if (xml) {
        response += message;
      } else {
        response += this._encodeData(message);
      }
      response += '</response>';
    } else {
      response += " />";
    }
    return response;
  };

  /**
   * Encodes data according to the current 'data_encoding' feature value.
   */
  this._encodeData = function(data) {
    var dataEncoding = this.getFeature('data_encoding');
    if (dataEncoding == 'none')
      return data;
    else if (dataEncoding == 'base64')
        return (new Buffer('' + data)).toString('base64');
    else
      throw 'Feature data_encoding has an unsupported value!';
  };

  /**
   * Generate an <init> message.
   */
  this.makeInit = function() {
    var ideKey = process.env['IDE_KEY'] || '';
    var dbgpCookie = process.env['DBGP_COOKIE'] || '';
    var appId = process.env['APPID'] || '';
    var init = '<?xml version="1.0" encoding="UTF-8"?>';
    init += '<init xmlns="urn:debugger_protocol_v1" appid="dbgp.js" ' +
               'idekey="'+ ideKey + '" ' +
               'session="'+ dbgpCookie + '" ' +
               'thread="1" ' + // ?
               'parent="' + appId + '" ' + // ?
               'language="node.js" ' +
               'protocol_version="1.0" ' +
               'fileuri="' + this.fileUri + '"/>'; // TODO
    return init;
  };

  /**
   * Wrap the supplied text in <![CDATA[...]]>, but handle any
   * internal occurrences of "]]>" that would prematurely terminate the
   * cdata section and cause a parsing error. For each "]]>" we find in
   * the text, we end the previous cdata section, write in "]]&gt;" as
   * plain text, and then start a new cdata section.
   *
   * On the IDE side the server always allows for more than one child
   * element where it's processing text.
   * 
   * Ref bug 90063
   */
  this.makeSafeCdataMarkedSection = function(value) {
    if (/[\<\>\&]/.test(value)) {
      return "<![CDATA[" + value.replace(/\]\]>/g, "]]>]]&gt;<![CDATA[") + "]]>";
    } else {
      return value;
    }
  };

  /**
   * Generate an <error> message with the given error code message text.
   */
  this.makeError = function(code, message) {
    if (typeof(message) == "undefined") {
      message = "";
    }
    var error = ('<error code="' + code + '">' + '<message>'
                 + this.makeSafeCdataMarkedSection(message)
                 + '</message>' + '</error>');
    return error;
  };

  /**
   * Generate a (misnamed) <stack> element for stacktraces.
   */
  this.makeFrame = function(level, type, filename, lineno, where, cmdbegin,
                            cmdend, extra) {
    var params = { 'level': level, 'type': type, 'filename': filename,
      'lineno': lineno};
    if (where)
      params['where'] = where;
    if (cmdbegin)
      params['cmdbegin'] = cmdbegin;
    if (where)
      params['where'] = where;
    if (extra) {
      Object.keys(extra).forEach(function(prop) {params[prop] = extra[prop];});
    }
    // Why is <stack> not called <frame>?
    var frame = this._makeXmlTag('stack', params, true);
    return frame;
  };

  this._isBlank = function(s) {
      return !s && s !== 0;
  };
  
  /** makeProperty - transform info about a variable into a dbgp property
   */
  this.makeProperty = function(property, fullName, maxDepth, finalCallbacks) {
    var propArgs = {
      'name': property.name,
      fullname: fullName,
      'type': property.type
    };
    if (this._isBlank(propArgs.name)) {
      propArgs.name = fullName;
    }
    if (this.builtinTypes.indexOf(propArgs.type) >= 0) {
      this.makeScalarProperty(propArgs, fullName, property, finalCallbacks);
    } else {
      this.makeCompoundProperty(propArgs, fullName, property, maxDepth, finalCallbacks);
    }
  };

  /** makeInnerProperty - similar to makeProperty, but if the property is
   * compound we need to call inlineObjectRef to get the properties field
   * on the property object.
   */
  this.makeInnerProperty = function(property, fullName, maxDepth, callbacks) {
    if (!property.value) {
      var cb = function(inlinedProperty) {
        if (!('value' in inlinedProperty)) {
          callbacks.onFailure(DBGP_ERROR_CODES['CANNOT_GET_PROPERTY'],
                              ("Failed to find a ref for " + fullName));
        } else {
          property.value = inlinedProperty.value;
          this.makeInnerProperty(property, fullName, maxDepth, callbacks);
        }
      }.bind(this);
      this.v8Client.inlineObjectRef(property, cb);
      return;
    }
    var propArgs = {
      'name': property.name,
      fullname: fullName,
      'type': property.value.type
    };
    if (this._isBlank(propArgs.name)) {
      propArgs.name = fullName;
    }
    if (this.builtinTypes.indexOf(propArgs.type) >= 0) {
      this.makeScalarProperty(propArgs, fullName, property.value, callbacks);
    } else {
      this.makeCompoundProperty(propArgs, fullName, property.value, maxDepth, callbacks);
    }
  };

  this.makeScalarProperty = function(propArgs, propName, property, finalCallbacks) {
    propArgs.children = '0';
    var cb;
    if (['undefined', 'null', 'function'].indexOf(propArgs.type) >= 0) {
      finalCallbacks.onSuccess(this.wrapInPropertyTag(propArgs, ''));
      return;
    }
    else if (!('value' in property)
             && !('text' in property)) {
      // We can use both property.text and property.value, so don't refresh
      // if one of them is present.
      cb = function(inlinedProperty) {
        if (!('value' in inlinedProperty)) {
          finalCallbacks.onFailure(DBGP_ERROR_CODES['CANNOT_GET_PROPERTY'],
                                   ("Failed to find an object for " + propName));
        } else {
          this.makeScalarProperty(propArgs, propName, inlinedProperty.value, finalCallbacks);
        }
      }.bind(this);
      this.v8Client.inlineObjectRef(property, cb);
    } else {
      var value;
      switch (property.type) {
        case 'boolean':
        case 'number':
          value = property.text || property.value;
          break;
        case 'string':
          value = property.text || property.value;
          var maxData = this.getFeature('max_data') || -1;
          // Actually, we want to track the total size of a packet.
          if (value.length > maxData) {
            value = value.slice(0, maxData) + "...";
          }
          break;
        default:
          log.error("unexpected type: " + propType);
          value = '';
      }
      if (typeof(value) == 'undefined') {
        value = '';
      }
      finalCallbacks.onSuccess(
          this.wrapInPropertyTag(propArgs,
                                 this.makeSafeCdataMarkedSection(value)));
    }
  };
  
  var compareStrings = function(aname, bname) {
    if (aname < bname) return -1;
    else if (aname > bname) return 1;
    else return 0;
  }

  var sortByName = function(a, b) {
    var aname = a.name;
    var bname = b.name;
    if (typeof(aname) == "number" && typeof(bname) == "number") {
      return aname - bname;
    } else if (typeof(aname) == "string" && typeof(bname) == "string") {
      // If two strings match ignoring case, do a case-sensitive comparison
      return (compareStrings(aname.toLowerCase(), bname.toLowerCase())
              || compareStrings(aname, bname));
    } else if (typeof(aname) == "number") {
      // Favor putting numbers first
      return -1;
    } else if (typeof(bname) == "number") {
      return 1;
    } else {
      return compareStrings(String(aname), String(bname));
    }
  };

  this.makeCompoundProperty = function(propArgs, propertyName, resp, maxDepth, finalCallbacks) {
    if (!('properties' in resp)) {
      var cb = function(inlinedProperty) {
        if (!('value' in inlinedProperty) || !('properties' in inlinedProperty.value)) {
          finalCallbacks.onFailure(DBGP_ERROR_CODES['CANNOT_GET_PROPERTY'],
                                   ("Failed to find value for " + propertyName));
        } else {
          this.makeCompoundProperty(propArgs, propertyName, inlinedProperty.value,
                                    maxDepth, finalCallbacks);
        }
      }.bind(this);
      this.v8Client.inlineObjectRef(resp, cb);
      return;
    }
    var respProperties = resp.properties;
    if (!respProperties) {
      finalCallbacks.onFailure(DBGP_ERROR_CODES['CANNOT_GET_PROPERTY'],
                               ("Failed to find properties for " + propertyName));
    }
    propArgs.type = resp.className;
    var isArray;
    if ((propArgs.type == "object" || propArgs.type == "Array")
        && resp.className == "Array") {
      isArray = true;
      var respPropertiesByNumber = [];
      var respPropertiesByName = [];
      respProperties.forEach(function(prop) {
        var name = prop.name;
        if (/^\d+$/.test(name)) {
          respPropertiesByNumber.push(prop);
        } else if (name != "length" && !this._shouldIgnoreProperty(prop)) {
          respPropertiesByName.push(prop);
        }
      }, this);
      respPropertiesByName.sort(sortByName);
      respProperties = respPropertiesByNumber.concat(respPropertiesByName);
    } else {
      isArray = false;
      respProperties = respProperties.filter(function(property) {
        return !this._shouldIgnoreProperty(property);
      }, this);
      respProperties.sort(sortByName);
    }
    if (respProperties.length) {
      propArgs.children = 1;
      propArgs.numchildren = respProperties.length;
      // Keep only the properties we were asked to show
      var startIdx = this.pageIndex * this.pageSize;
      var endIdx = startIdx + this.pageSize;
      respProperties = respProperties.slice(startIdx, endIdx);
    } else {
      propArgs.children = 0;
    }
    var propertyStrings = [];
    var wrapPropertyStrings = function() {
      var childString;
      if (propertyStrings.length) {
        childString = propertyStrings.join("");
      } else {
        childString = '';
      }
      finalCallbacks.onSuccess(
          this.wrapInPropertyTag(propArgs, childString));
    }.bind(this);

    if (maxDepth <= 0) {
      wrapPropertyStrings();
      return;
    }

    var buildCompoundPropertyStrings = function(i) {
      if (i >= respProperties.length) {
        wrapPropertyStrings();
        return;
      }
      var innerProperty = respProperties[i];
      if (!innerProperty) {
        wrapPropertyStrings();
        return;
      }
      var key;
      var name = innerProperty.name;
      if (/^\d+$/.test(name)) {
        key = '[' + name + ']';
      } else if (/^\w+$/.test(name)) {
        key = '.' + name;
      } else {
        key = '[' + JSON.stringify(String(name)) + ']';
      }
      var cb = function(propertyStr) {
        propertyStrings.push(propertyStr);
        buildCompoundPropertyStrings(i + 1);
      }.bind(this);
      var innerCallbacks = {
        onSuccess: cb,
        onFailure: finalCallbacks.onFailure
      };
      this.makeInnerProperty(innerProperty, propertyName + key, maxDepth - 1, innerCallbacks);
    }.bind(this);

    buildCompoundPropertyStrings(0);
  };

  this.wrapInPropertyTag = function(propArgs, s) {
    var propXml = (this._makeXmlTag('property', propArgs, false)
                   + s
                   + '</property>');
    return propXml;
 };

  /**
   * Generate a <breakpoint> element.
   */
  this.makeBreakpoint = function(id, params, expression) {
    params['id'] = id;
    var bp = this._makeXmlTag('breakpoint', params, false);
    if (expression) {
      bp += this._makeXmlTag('expression');
      bp += this.makeSafeCdataMarkedSection(expression);
      bp += '</expression>';
    }
    bp += '</breakpoint>';
    return bp;
  };

  this.makeContext = function(id, name) {
    return this._makeXmlTag('context', {
      'id': id,
      'name': name
    }, true);
  };

  this.makeType = function(name, type) {
    return this._makeXmlTag('map', {
      'name': name,
      'type': type
    }, true);
  };

  /**
   * Send data as a dbgp stdout message and to our stdout file.
   */
  this.stdoutCopy = function(data) {
    assert.equal(this.stdout, 1);
    var msg = this._makeStreamMessage('stdout', data);
    this.dbgpClient.sendPacket(msg);
    process.stdout.write(data);
  };

  /**
   * Send data as a dbgp message.
   */
  this.stdoutRedirect = function(data) {
    assert.equal(this.stdout, 2);
    var msg = this._makeStreamMessage('stdout', data);
    this.dbgpClient.sendPacket(msg);
  };

  /**
   * Send data as a dbgp stderr message and to our stderr file.
   */
  this.stderrCopy = function(data) {
    assert.equal(this.stderr, 1);
    var msg = this._makeStreamMessage('stderr', data);
    this.dbgpClient.sendPacket(msg);
    process.stderr.write(data);
  };

  /**
   * Send data as a dbgp stderr message.
   */
  this.stderrRedirect = function(data) {
    assert.equal(this.stderr, 2);
    var msg = this._makeStreamMessage('stderr', data);
    this.dbgpClient.sendPacket(msg);
  };

  this._makeStreamMessage = function(type, data) {
    var msg = '<?xml version="1.0" encoding="UTF-8"?>';
    msg += this._makeXmlTag('stream', { 'type': type }, false);
    msg += this._encodeData(data);
    msg += '</stream>';
    return msg;
  };

  this._makeXmlTag = function(tagName, params, closing) {
    var tag = '<' + tagName + ' ';
    for (var name in params) {
      var value = params[name];
      tag += name + '="' + this._xmlEscape(value) + '" ';
    }
    tag.trimRight();
    tag += closing ? '/>' : '>';
    return tag;
  };

  var _escapes = {
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;",
    "'": "&apos;",
    '"': "&quot;"
  };
  var _escapableChars_re = /([<>&\'\"])/g;
  var _xmlEscapeReplFunc = function(c) {
    return _escapes[c];
  };
  this._xmlEscape = function(s) {
    try {
      return s.replace(_escapableChars_re, _xmlEscapeReplFunc)
    } catch(ex) {
      return s;
    }
  };

  
  this._filterGlobalScope = function(scope) {
    // Node and JS internals in the global scope are usually not that
    // interesting, but displaying them with every context_get can slow things
    // down a lot. So we hide them if the Server doesn't tell us otherwise.
    if (this.getFeature('show_hidden'))
      return;

    scope.properties = scope.properties.filter(function(property) {
      return INTERNAL_GLOBAL_NAMES.indexOf(property.name) == -1;
    });
  };

  this._filterLocalScope = function(scope) {
    if (this.getFeature('show_hidden')) 
      return;
    scope.properties = scope.properties.filter(function(property) {
      return INTERNAL_LOCAL_NAMES.indexOf(property.name) == -1;
    });
  };

  this._shouldIgnoreProperty = function(property) {
    return !this.getFeature('show_hidden') && property.name[0] == "_";
  };

  this._scopeForContext = function(contextId) {
    // Return a V8 scope ID for a DBGP context ID.
    return DBGP_CONTEXT_IDS[contextId];
  };

  /**
   * Retrieves the file path from the given uri.
   */
  this._filepathFromUri = function(uri) {
    var isWindows = /^win/i.test(os.platform());
    uri = url.parse(uri);
    var filepath = uri.pathname;
    if (isWindows) {
      if (!uri.protocol) {
        // No protocol, it was a MSYS-style path, /c/my/file.js
        if (/^\/.\//.test(url.pathname)) {
          filepath = url.pathname[1] + ":" + url.pathname.substr(2);
        }
      } else if (uri.protocol.length == 2) {
        // Drive letter, "X:"
        filepath = uri.protocol + uri.pathname;
      } else if (uri.protocol == "file:") {
        var match = /^\/*(.)[:|](.*)/.exec(uri.pathname);
        if (match) {
          // file:///X:/Blah, pathname was /X:/Blah
          filepath = match[1] + ":" + unescape(match[2]);
        }
      }
    } else if (uri.protocol) {
      // There waas a protocol, this was a URI (probably file:///something)
      filepath = unescape(uri.pathname);
    }
    return path.normalize(filepath);
  };

  this._parseArgs = function(args) {
    if (args.length % 2 != 0)
      throw "Invalid arguments format!";
    var parsedArgs = {};
    for (var i=0; i < args.length; i += 2) {
      var name = args[i];
      if (name[0] != '-')
        throw "Invalid argument name: " + name;
      name = name.slice(1);
      var value = args[i+1];
      parsedArgs[name] = value;
    }
    return parsedArgs;
  };

  this.handleMessage = function(msg) {
    log.info("Got message: " + msg);
    var args = cmdln.parseArgv(msg); // TODO try-catch
    var cmd = args.shift();
    this.handleCommand(cmd, args);
  };

  this.handleCommand = function(cmd, args) {
    log.info("Got command: " + cmd);
    args = this._parseArgs(args);
    if (this.listeners(cmd).length > 0) {
      // TODO Potentially bad because we also have other event listeners.
      // It's probably a good idea to separate protocol implementation from the
      // rest of the Enine.
      this.emit(cmd, args);
    } else {
      log.warning("Unsupported command " + cmd);
      this.sendUnsuccessfulResponse(cmd, args['i']);
    }
  };

  /**
   * Initiates the debugging session. Call this, once the Engine emits 'ready'.
   * The dbgp client will connect to the dbgp server (Komodo) to initiate the
   * session for the user.
   */
  this.connect = function() {
    this.dbgpClient.connect(this.port, this.host);
  };

  /**
   * Terminates the debugging session by closing the connection to the dbgp
   * server (Komodo).
   */
  this.terminate = function() {
    this.dbgpClient.end();
  };
}).apply(Engine.prototype);

exports.Engine = Engine;

function capitalize(str) {
  str = str.toLowerCase();
  str[0] = str[0].toUpperCase();
  return str;
}
