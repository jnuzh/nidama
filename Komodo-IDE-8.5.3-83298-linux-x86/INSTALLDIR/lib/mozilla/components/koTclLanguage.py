"""Language package for Tcl"""

from xpcom import components, ServerException
from xpcom.server import WrapObject, UnwrapObject
from koLanguageServiceBase import *
import os, re

from codeintel2 import lang_tcl

import logging


log = logging.getLogger("TclLanguage")

class koTclLanguage(KoLanguageBase):
    name = "Tcl"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" \
                       % (name)
    _reg_clsid_ = "{491A0CE5-7180-425b-A27A-9EA36BCBA50F}"
    _reg_categories_ = [("komodo-language", name)]

    accessKey = 't'
    shebangPatterns = [
        re.compile(ur'\A#!.*tclsh.*$', re.IGNORECASE | re.MULTILINE),
        re.compile(ur'\A#!.*wish.*$', re.IGNORECASE | re.MULTILINE),
        re.compile(ur'\A#!.*expect.*$', re.IGNORECASE | re.MULTILINE),
        # As suggested here: http://www.tcl.tk/man/tcl8.4/UserCmd/tclsh.htm
        # Make sure we properly catch shebang lines like this:
        #   #!/bin/sh
        #   # the next line restarts using tclsh \
        #   exec tclsh "$0" "$@"
        re.compile(ur'\A#!.*^exec [^\r\n|\n|\r]*?tclsh', re.IGNORECASE | re.MULTILINE | re.DOTALL),
        re.compile(ur'\A#!.*^exec [^\r\n|\n|\r]*?wish', re.IGNORECASE | re.MULTILINE | re.DOTALL),
        re.compile(ur'\A#!.*^exec [^\r\n|\n|\r]*?expect', re.IGNORECASE | re.MULTILINE | re.DOTALL),
    ]
    primary = 1
    namedBlockRE = "^[ \t;]*(proc|class|method)\s+[\w:]+(.*\{\n)?"
    namedBlockDescription = 'Tcl procedures and [incr Tcl] classes'
    defaultExtension = ".tcl"

    # XXX read from config somewhere, download from ActiveState?
    downloadURL = 'http://www.ActiveState.com/Products/ActiveTcl'
    commentDelimiterInfo = { "line": [ "#" ]  }
    variableIndicators = '$'
    supportsSmartIndent = "brace"
    _dedenting_statements = [u'error', u'return', u'break', u'continue']

    sample = """proc loadFile { } {
    # a simple comment
    global f
    global f2
    global fileToOpen
    global fileOpened
    if [file exists $fileToOpen] {
        $f2.text delete 1.0 end
        set ff [open $fileToOpen]
        while {![eof $ff]} {
            $f2.text insert end [read $ff 1000]
        }
        close $ff
        set fileOpened $fileToOpen
    } else {
        $f.entry insert end " does not exist"
    }
}
"""

    styleStdin = components.interfaces.ISciMoz.SCE_TCL_STDIN
    styleStdout = components.interfaces.ISciMoz.SCE_TCL_STDOUT
    styleStderr = components.interfaces.ISciMoz.SCE_TCL_STDERR

    def __init__(self):
        KoLanguageBase.__init__(self)
        del self.matchingSoftChars["'"]

        self.dbgpObserver = koTclDBGPInitHandler()


    def getVariableStyles(self):
        # Bug 95389 - support variable highlighting for Tcl regardless of
        # whether a variable def'n or use is clicked.
        return self._style_info._variable_styles + [components.interfaces.ISciMoz.SCE_TCL_IDENTIFIER]
    
    def get_lexer(self):
        if self._lexer is None:
            self._lexer = KoLexerLanguageService()
            self._lexer.setLexer(components.interfaces.ISciMoz.SCLEX_TCL)
            keywords = lang_tcl.keywords
            try:
                version = components.classes["@activestate.com/koAppInfoEx?app=Tcl;1"].createInstance().version.split(".", 2)
                versionNum = tuple([int(x) for x in version])
                if versionNum >= (8, 6):
                    keywords = sorted(keywords + lang_tcl.v8_6_keywords)
            except:
                log.exception("Couldn't get the version")
            self._lexer.setKeywords(0, keywords)
            self._lexer.supportsFolding = 1
        return self._lexer

    def get_completer(self):
        if self._completer is None:
            self._completer = components.classes["@activestate.com/koTclCompletionLanguageService;1"].getService(components.interfaces.koICompletionLanguageService)
        return self._completer

    def get_interpreter(self):
        if self._interpreter is None:
            self._interpreter = components.classes["@activestate.com/koAppInfoEx?app=Tcl;1"].getService()
        return self._interpreter
    
    def softchar_accept_matching_double_quote(self, scimoz, pos, style_info, candidate):
        if pos == 0:
            return candidate
        prevPos = scimoz.positionBefore(pos)
        if scimoz.getStyleAt(prevPos) == scimoz.SCE_TCL_DEFAULT:
            return candidate
        return None

    # XXX later these need to be centralized.


class koTclDBGPInitHandler:
    _com_interfaces_ = [components.interfaces.nsIObserver]
    
    def __init__(self):
        self._wrapped = WrapObject(self, components.interfaces.nsIObserver)
        self._observerSvc = components.classes["@mozilla.org/observer-service;1"].\
            getService(components.interfaces.nsIObserverService)
        self._observerSvc.addObserver(self._wrapped, 'debugger_startup', 1)

        self._prefsSvc = components.classes["@activestate.com/koPrefService;1"].\
            getService(components.interfaces.koIPrefService)

    def _parse(self, instrument):
        result = {}
        for item in instrument.split(':'):
            v,k = item.split(',')
            result[k]=v
        return result
        
    def observe(self, session, event, data):
        try:
            if event == 'debugger_startup' and session.languageName == 'Tcl':
                # do our own additional debugger init work
                tclInstrument = self._prefsSvc.prefs.getStringPref('tclInstrument')
                if not tclInstrument:
                    return
    
                try:
                    session.featureGet('instrument_set')
                except Exception, e:
                    # not supported, dont bother
                    return
                
                modules = self._parse(tclInstrument)
                for module, enabled in modules.items():
                    if enabled.lower() == 'true':
                        enabled='1'
                    else:
                        enabled='0'
                    command = ['instrument_set', '-d', module, '-e', enabled]
                    session.sendCommand(command, None)
        except Exception, e:
            log.exception(e)


