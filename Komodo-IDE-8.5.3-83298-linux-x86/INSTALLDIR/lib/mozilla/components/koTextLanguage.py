from xpcom import components, ServerException
from koLanguageServiceBase import *

class koTextLanguage(KoLanguageBase):
    name = "Text"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" \
                       % (name)
    _reg_clsid_ = "{CDFF6BC6-C21B-420c-9796-C90C37377FE6}"
    _reg_categories_ = [("komodo-language", name)]

    accessKey = 'e'
    primary = 1
    defaultExtension = ".txt"
    commentDelimiterInfo = { }
    sample = "Text files only have one style."

    def __init__(self):
        """In plain text we can't tell when a quote starts a sentence and
        when it means something else, so we simply never provide a close-quote.
        """
        KoLanguageBase.__init__(self)
        del self.matchingSoftChars["'"]
        del self.matchingSoftChars['"']

    def getEncodingWarning(self, encoding):
            return ''
        
    def guessIndentation(self, scimoz, tabWidth, defaultUsesTabs):
        guess = 0
        usesTabs = 0
        N = min(scimoz.lineCount, 100)
        for lineNo in range(N):
            lineStartPos = scimoz.positionFromLine(lineNo)
            lineEndPos = scimoz.getLineEndPosition(lineNo)
            line = scimoz.getTextRange(lineStartPos, lineEndPos)
            blackPos = len(line) - len(line.lstrip())
            if blackPos:
                guess = scimoz.getColumn(lineStartPos + blackPos)
                break
        if not guess:
            return 0, defaultUsesTabs
        # investigate whether tabs are used
        sawSufficientWhiteSpace = False
        for lineNo in range(lineNo, N):
            lineStartPos = scimoz.positionFromLine(lineNo)
            lineEndPos = scimoz.getLineEndPosition(lineNo)
            line = scimoz.getTextRange(lineStartPos, lineEndPos)
            blackPos = len(line) - len(line.lstrip())
            front = line[:blackPos]
            if '\t' in front or u'\t' in front:
                usesTabs = 1
                break
            elif scimoz.getColumn(lineStartPos + blackPos) >= tabWidth:
                sawSufficientWhiteSpace = True
        return guess, usesTabs or (not sawSufficientWhiteSpace and defaultUsesTabs)

    def get_commenter(self):
        if self._commenter is None:
            self._commenter = KoTextCommenterLanguageService()
        return self._commenter

class KoTextCommenterLanguageService(KoCommenterLanguageService):
    # Bug 90001 - make sure auto-comment on text files does nothing.
    def __init__(self):
        # Don't call the superclass
        pass

    def comment(self, scimoz):
        # Do nothing
        return
    
    def uncomment(self, scimoz):
        # Do nothing
        return
