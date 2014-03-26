from xpcom import components, ServerException

from koLanguageServiceBase import *

class _koBase_ML_Language(KoLanguageBase):
    commentDelimiterInfo = {
        "block": [ ("(*", "*)") ],
        "markup": "*",
    }
    supportsSmartIndent = "brace"
    sample = """
SAMPLE NOT AVAILABLE
"""

    def __init__(self):
        KoLanguageBase.__init__(self)
        del self.matchingSoftChars["'"]
        
    def get_lexer(self):
        if self._lexer is None:
            self._lexer = KoLexerLanguageService()
            self._lexer.setLexer(self.sciMozLexer)
            self._lexer.setKeywords(0, self._keywords)
            self._lexer.setKeywords(1, self._keywords2)
            self._lexer.supportsFolding = 1
        return self._lexer

    _keywords = [
        "and", "as", "assert", "asr", "begin", "class",
        "constraint", "do", "done", "downto", "else", "end",
        "exception", "external", "false", "for", "fun", "function",
        "functor", "if", "in", "include", "inherit", "initializer",
        "land", "lazy", "let", "lor", "lsl", "lsr",
        "lxor", "match", "method", "mod", "module", "mutable",
        "new", "object", "of", "open", "or", "private",
        "rec", "sig", "struct", "then", "to", "true",
        "try", "type", "val", "virtual", "when", "while",
        "with"]
    
    _keywords2 = ["option", "Some", "None", "ignore", "ref"]

# see http://caml.inria.fr/
class koCamlLanguage(_koBase_ML_Language):
    name = "Objective Caml"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" \
                       % (name)
    _reg_clsid_ = "{23CCAA5C-53E5-11DA-9353-000D935D3368}"
    _reg_categories_ = [("komodo-language", name)]

    defaultExtension = ".ml" # and .mli

    sciMozLexer = components.interfaces.ISciMoz.SCLEX_CAML

    _stateMap = {
        'default': ('SCE_CAML_DEFAULT',),
        'keywords': ('SCE_CAML_KEYWORD', 'SCE_CAML_KEYWORD2',),
        'identifiers': ('SCE_CAML_IDENTIFIER',),
        'comments': ('SCE_CAML_COMMENT','SCE_CAML_COMMENT1',
                     'SCE_CAML_COMMENT2', 'SCE_CAML_COMMENT3',),
        'operators': ('SCE_CAML_OPERATOR',),
        'numbers': ('SCE_CAML_NUMBER',),
        'strings': ('SCE_CAML_STRING', 'SCE_CAML_CHAR',),
        'linenumber': ('SCE_CAML_LINENUM',),
        'tagname': ('SCE_CAML_TAGNAME',),
        }
    
# see 
class koSMLLanguage(_koBase_ML_Language):
    name = "SML" # Standard ML
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" \
                       % (name)
    _reg_clsid_ = "{A8AB7F0E-06DA-4A5E-93AC-8646FA621F47}"
    _reg_categories_ = [("komodo-language", name)]

    defaultExtension = ".sml"

    sciMozLexer = components.interfaces.ISciMoz.SCLEX_SML

    _stateMap = {
        'default': ('SCE_SML_DEFAULT',),
        'keywords': ('SCE_SML_KEYWORD', 'SCE_SML_KEYWORD2',
                     'SCE_SML_KEYWORD3',),
        'identifiers': ('SCE_SML_IDENTIFIER',),
        'comments': ('SCE_SML_COMMENT','SCE_SML_COMMENT1',
                     'SCE_SML_COMMENT2', 'SCE_SML_COMMENT3',),
        'operators': ('SCE_SML_OPERATOR',),
        'numbers': ('SCE_SML_NUMBER',),
        'strings': ('SCE_SML_STRING', 'SCE_SML_CHAR',),
        'linenumber': ('SCE_SML_LINENUM',),
        'tagname': ('SCE_SML_TAGNAME',),
        }
