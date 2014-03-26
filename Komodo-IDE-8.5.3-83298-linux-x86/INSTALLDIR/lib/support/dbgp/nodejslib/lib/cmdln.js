// Copyright (c) 2011 ActiveState Software Inc.
// See the LICENSE file for licensing information.

/**
 * Port of trentm's cmdln.py
 * (http://code.google.com/p/cmdln/source/browse/trunk/lib/cmdln.py)
 */
exports.parseArgv = function parseArgv(line) {
    var WHITESPACE = '\t\n\x0b\x0c\r ';
    var QUOTES = "\"'";
    var i = -1;
    var ch, arg = null, argv = [];
    var state = 'default';
    line = line.trim();
    while (true) {
          i += 1;
          if (i >= line.length)
            break;
          ch = line[i];

          if (ch == "\\" && i+1 < line.length) {
              // escaped char always added to arg, regardless of state
              if (arg == null) arg = "";
              if ((state == "double-quoted" || state == "single-quoted")
                  && QUOTES.indexOf(line[i+1]) == -1) {
                  arg += ch;
              }
              i += 1;
              arg += line[i];
              continue;
          }
          if (state == "single-quoted") {
              if (ch == "'")
                  state = "default";
              else
                  arg += ch;
          } else if (state == "double-quoted") {
              if (ch == '"')
                  state = "default";
              else
                  arg += ch;
          } else if (state == "default") {
              if (ch == '"') {
                  if (arg == null) arg = "";
                  state = "double-quoted";
              } else if (ch == "'") {
                  if (arg == null) arg = "";
                  state = "single-quoted";
              } else if (WHITESPACE.indexOf(ch) >= 0) {
                  if (arg != null)
                      argv.push(arg);
                  arg = null;
              } else {
                  if (arg == null) arg = "";
                  arg += ch;
              }
          }
      }
      if (arg != null)
          argv.push(arg);
      if (state != "default")
          throw "line is not terminated: unfinished " + state + "segment";
      return argv;
};
