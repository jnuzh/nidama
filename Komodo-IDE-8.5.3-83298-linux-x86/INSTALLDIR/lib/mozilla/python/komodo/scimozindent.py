# Copyright (c) 2004-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

# Utility functions for dealing with scimoz & indentation
# that are used both by koLanguageServiceBase and koLanguageCommandHandler

import re


# ---- Globals

_commentRegex = re.compile('<!--.*?-->')
_multiStartTagsRegex = re.compile('<.*<')
_multiEndTagsRegex = re.compile('>.*[<>]')



def makeIndentFromWidth(scimoz, width):
    """ returns a string consisting of however many tabs and spaces
    are needed to make a width of `width`, using the useTabs pref
    and the scimoz tabWidth
    """
    if scimoz.useTabs:
        tabWidth = scimoz.tabWidth
        # guard against a misconfigured scimoz with a tabWidth
        # of 0, which would cause a divide by zero error
        if tabWidth == 0: tabWidth = 8
        numtabs, numspaces = divmod(width, scimoz.tabWidth)
        return '\t'*numtabs + ' '*numspaces
    else:
        return ' '*width

def findMatchingTagPosition(scimoz, caretPos, languageObj, constrainSearchInViewPort=False):
    """
    Gives information to clients on where the matching start- and end-tags are.
    @param scimoz {Scimoz}
    @param caretPos {int} The current position
    @param languageObj {koILanguage} - unwrapped Python object
    @param constrainSearchInViewPort {bool} - Search only in the visible portion of the document.
    
    @returns:
      On failure: None
      Otherwise: 5-tuple: ({bool}: onStartTag
                           {int}: start-tag-start-pos,
                           {int}: start-tag-end-pos,
                           {int}: end-tag-start-pos,
                           {int}: end-tag-end-pos)
    """
    textLength = scimoz.textLength
    if caretPos >= textLength:
        caretPos = scimoz.positionBefore(textLength)
        
    # If we're on a start- or end-tag, go find the matcher.
    isHTML = languageObj.isHTMLLanguage
    tagStartPos = caretPos
    tagStartPrevPos = scimoz.positionBefore(tagStartPos)
    matchingTagInfo = None
    onStartTagAtLeft = languageObj.onStartTag(scimoz, tagStartPrevPos)
    onStartTagAtRight = (tagStartPos < textLength
                         and languageObj.onStartTag(scimoz, tagStartPos))
    onEndTagAtLeft = languageObj.onEndTag(scimoz, tagStartPrevPos)
    onEndTagAtRight = (tagStartPos < textLength
                       and languageObj.onEndTag(scimoz, tagStartPos))
    
    # Break ties when we're between two tags.
    if onEndTagAtLeft and scimoz.getStyleAt(tagStartPrevPos) == scimoz.SCE_UDL_M_ETAGC:
        if onStartTagAtRight or onEndTagAtRight:
            # Favor left.  This means moving forward on '<a...'
            # will always return back to the start of '<a...'
            # </a>|<b> : show <a>
            # </a>|</b> : show <a>
            onStartTagAtRight = onEndTagAtRight = False
            tagStartPos -= 1
    elif onStartTagAtLeft and scimoz.getStyleAt(tagStartPrevPos) == scimoz.SCE_UDL_M_STAGC:
        if onEndTagAtRight:
            # There's nothing to do, so return a nil result
            # <a>|</b> : If we did a search, we'd end up walking
            # through the full doc and find either nothing,
            # or a false positive
            return None
        elif onStartTagAtRight:
            # Favor right: consistent with onEndTagAtLeft
            # <a>|<b> : show </b>
            onStartTagAtLeft = False
            tagStartPos += 1
    
    if constrainSearchInViewPort:   
        firstLine = scimoz.docLineFromVisible(scimoz.firstVisibleLine)
        lastLine = scimoz.docLineFromVisible(scimoz.firstVisibleLine + scimoz.linesOnScreen)
        firstVisiblePos = scimoz.positionFromLine(firstLine)
        lastVisiblePos = scimoz.getLineEndPosition(lastLine) + 1
    else:
        firstVisiblePos = lastVisiblePos = None
        
    if onStartTagAtLeft or onStartTagAtRight:
        res = endTagInfo_from_startTagPos(scimoz, tagStartPos, isHTML, lastVisiblePos)
        if res:
            return (True,) + (res)
        return res
    elif onEndTagAtLeft or onEndTagAtRight:
        res = startTagInfo_from_endTagPos(scimoz, tagStartPos, isHTML, firstVisiblePos)
        if res:
            return (False,) + (res)
        return res
    else:
        return None
    
def _verifyLoneStartTag(scimoz, tagPos):
    """
    When we match tags according to Scintilla fold information,
    we need to make sure the start-tag's closing '>' is part
    of the only tag on the line.  The reason for this is when
    multiple opening or closing tags are on the same line, we
    can't use just folding info to figure out which tag matches
    the starting tag.  In that case it's more straightforward to
    simply match by tagname.
    
    If the tag isn't alone, return None.  If it is,
    return a 4-tuple of useful information.
    
    @param scimoz {Scimoz}
    @param tagPos {int} -- a position somewhere on the start-tag
    @returns None or (startTagStartPos, startTagEndPos, lineNo, tagName)
    """
    # Watch out for being outside a tag
    if (tagPos > 0
        and scimoz.getStyleAt(tagPos - 1) == scimoz.SCE_UDL_M_STAGC
        and tagPos < scimoz.textLength
        and scimoz.getStyleAt(tagPos) != scimoz.SCE_UDL_M_STAGO):
        # We're to the immediate right of the end-tag of interest,
        # but not to the left of another tag
        tagPos -= 1
    startTagEndPos = _tagEndPosFromPos(scimoz, tagPos, scimoz.SCE_UDL_M_STAGC)
    if startTagEndPos <= 0:
        return None
    lineNo = scimoz.lineFromPosition(startTagEndPos)
    lineStartPos = scimoz.positionFromLine(lineNo)
    lineEndPos = scimoz.getLineEndPosition(lineNo)
    lineStartText = scimoz.getTextRange(lineStartPos, lineEndPos)
    lineStartText = re.sub(_commentRegex, "", lineStartText)
    if (_multiStartTagsRegex.search(lineStartText)
        or _multiEndTagsRegex.search(lineStartText)):
        return None
    startTagStartPos = _tagStartPosFromPos(scimoz, tagPos, scimoz.SCE_UDL_M_STAGO)
    if startTagStartPos <= 0:
        return None
    tagName = _getCurrTagName(scimoz, startTagStartPos + 1)
    return startTagStartPos, startTagEndPos, lineNo, tagName

def _verifyLoneEndTag(scimoz, tagPos):
    """ See _verifyLoneStartTag for details
    @param scimoz {Scimoz}
    @param tagPos {int} -- a position somewhere on the end-tag
    @returns None or (endTagStartPos, endTagEndPos, lineNo, tagName)
    """
    
    # Watch out for being outside a tag
    if (tagPos > 0
        and scimoz.getStyleAt(tagPos - 1) == scimoz.SCE_UDL_M_ETAGC
        and tagPos < scimoz.textLength
        and scimoz.getStyleAt(tagPos) != scimoz.SCE_UDL_M_ETAGO):
        # We're to the immediate right of the end-tag of interest,
        # but not to the left of another tag
        tagPos -= 1
    endTagEndPos = _tagEndPosFromPos(scimoz, tagPos, scimoz.SCE_UDL_M_ETAGC)
    if endTagEndPos <= 0:
        return None
    lineNo = scimoz.lineFromPosition(endTagEndPos)
    lineStartPos = scimoz.positionFromLine(lineNo)
    lineEndPos = scimoz.getLineEndPosition(lineNo)
    lineStartText = scimoz.getStyledText(lineStartPos, lineEndPos)[0::2]
    lineStartText = re.sub(_commentRegex, "", lineStartText)
    if (_multiStartTagsRegex.search(lineStartText)
        or _multiEndTagsRegex.search(lineStartText)):
        return None
    endTagStartPos = _tagStartPosFromPos(scimoz, tagPos, scimoz.SCE_UDL_M_ETAGO)
    if endTagStartPos <= 0:
        return None
    if scimoz.getCharAt(endTagStartPos) == ord('/'):
        endTagStartPos -= 1
    tagName = _getCurrTagName(scimoz, endTagStartPos + 2)
    return endTagStartPos, endTagEndPos, lineNo, tagName

def startTagInfo_from_endTagPos(scimoz, endTagPos, isHTML=False, firstVisiblePos=None):
    """
    @param scimoz {Scimoz}
    @param endTagPos {int} -- a position somewhere on the end tag
    @param isHTML {bool} -- if False, the match might be determined by looking at Scintilla fold levels
    @param firstVisiblePos {int} - position of the start of the first visible line in the editor
    
    @return either None, or a 4-tuple containing the start and end points
    of the start-tag and end-tag.
    """
    if not isHTML and firstVisiblePos is None:
        res = tagStartFromEndViaFoldLevels(scimoz, endTagPos)
        if res is not None:
            return res
    return tagStartFromEndViaMatchingName(scimoz, endTagPos, firstVisiblePos)
  
def endTagInfo_from_startTagPos(scimoz, startTagPos, isHTML=False, lastVisiblePos=None):
    """
    @param scimoz {Scimoz}
    @param startTagPos {Int} -- a position somewhere on the start tag
    @param isHTML {Boolean} -- if False, the match might be determined by looking at Scintilla fold levels
    @param lastVisiblePos {int} - position of the end of the last visible line in the editor
    
    @return either None or a 4-tuple containing the start and end points
    of the start-tag and end-tag.
    """
    if not isHTML and lastVisiblePos is None:
        res1 = tagEndFromStartViaFoldLevels(scimoz, startTagPos)
        if res1 is not None:
            return res1
    return tagEndFromStartViaMatchingName(scimoz, startTagPos, lastVisiblePos)
   
def tagStartFromEndViaFoldLevels(scimoz, endTagPos):
    """
    Do this only if the closing ">" of the start-tag and end-tag
    don't contain all or part of another tag.  Otherwise matching
    tags are easier to determine by searching through the document.
    
    @return either None, or a 4-tuple containing the start and end points
    of the start-tag and end-tag.
    """
    # Verify the line containing the end-tag close contains nothing else
    res = _verifyLoneEndTag(scimoz, endTagPos)
    if res is None:
        return None
    endTagStartPos, endTagEndPos, lineNo, tagName  = res
    parentLineNo = scimoz.getFoldParent(lineNo)
    if parentLineNo == -1:
        return None

    startTagStartPos = _tagStartOnLine(scimoz, parentLineNo,
                                       (scimoz.SCE_UDL_M_STAGO,
                                        scimoz.SCE_UDL_M_STAGC))
    if startTagStartPos == -1:
        return None
    # Verify that this line contains one ">" and at most one "<" before the ">"
    res = _verifyLoneStartTag(scimoz, startTagStartPos)
    if res is None or tagName != res[3]:
        return None
    return res[0], res[1], endTagStartPos, endTagEndPos

def _getCloseTagPos(scimoz, tagStartPos):
    scimoz.currentPos = scimoz.anchor = tagStartPos + 1
    scimoz.searchAnchor()
    nextTagOpenPos = scimoz.searchNext(0, "<")
    nextTagClosePos = scimoz.searchNext(0, ">")
    if nextTagOpenPos == -1:
        return nextTagClosePos
    elif nextTagOpenPos < nextTagClosePos:
        return -1
    else:
        return nextTagClosePos

def tagStartFromEndViaMatchingName(scimoz, endTagPos, firstVisiblePos):
    """
    Start at the end-point, and search backwards looking at
    <foo and </foo (assuming a starting tag name of "foo",
    make sure that we don't get fooled by tags like "<fool".
    If we find the matching opening "<foo", use its coordinates
    and return the usual 4-tuple.
    
    @return either None, or a 4-tuple containing the start and end points
    of the start-tag and end-tag.
    """
    # On code-completion an element name can be inserted, but we
    # haven't colourised it yet, so do that now.
    lineNo = scimoz.lineFromPosition(endTagPos)
    lineEndPos = scimoz.getLineEndPosition(lineNo)
    scimoz.colourise(endTagPos, lineEndPos)
    
    endTagPos = _tagStartPosFromPos(scimoz, endTagPos, scimoz.SCE_UDL_M_ETAGO)
    if endTagPos == -1:
        return None
    if scimoz.getCharAt(endTagPos) == ord("/"):
       endTagPos -= 1
    tagName = _getCurrTagName(scimoz, endTagPos + 2)

    origPos = scimoz.currentPos
    origAnchor = scimoz.anchor
    tagCount = 1
    startTagSearch = "<" + tagName
    endTagSearch = "</" + tagName
    searchLen = len(tagName) + 1
    scimoz.currentPos = scimoz.anchor = endTagPos - 1
    scimoz.searchAnchor()
    try:
        nextStartTagPos = scimoz.searchPrev(0, startTagSearch)
        if firstVisiblePos is not None and nextStartTagPos < firstVisiblePos:
            return None
        nextEndTagPos = scimoz.searchPrev(0, endTagSearch)
        # Figure out what to do based on what we've seen
        while True:
            if nextStartTagPos == -1:
                return None
            elif nextStartTagPos > nextEndTagPos:
                # Includes no more end-tags
                style = scimoz.getStyleAt(nextStartTagPos)
                if style == scimoz.SCE_UDL_M_STAGO:
                    closeTagPos = _getCloseTagPos(scimoz, nextStartTagPos)
                    if (closeTagPos > 0
                        and (scimoz.getStyleAt(closeTagPos)
                             == scimoz.SCE_UDL_M_STAGC)
                        and (scimoz.getStyleAt(nextStartTagPos + searchLen)
                             != scimoz.SCE_UDL_M_TAGNAME)):
                        if tagCount == 1:
                            tagEndPos = _tagEndPosFromPos(scimoz, nextStartTagPos,
                                                          scimoz.SCE_UDL_M_STAGC)
                            return (nextStartTagPos, tagEndPos,
                                    endTagPos,
                                    _tagEndPosFromPos(scimoz, endTagPos,
                                                      scimoz.SCE_UDL_M_ETAGC))
                        tagCount -= 1
                scimoz.currentPos = scimoz.anchor = nextStartTagPos - 1
                scimoz.searchAnchor()
                nextStartTagPos = scimoz.searchPrev(0, startTagSearch)
                if firstVisiblePos is not None and nextStartTagPos < firstVisiblePos:
                    nextStartTagPos = -1
            else:
                # Found an end-tag
                style = scimoz.getStyleAt(nextEndTagPos)
                if (style == scimoz.SCE_UDL_M_ETAGO
                    and (scimoz.getStyleAt(nextEndTagPos + searchLen + 1)
                         != scimoz.SCE_UDL_M_TAGNAME)):
                    tagCount += 1
                scimoz.currentPos = scimoz.anchor = nextEndTagPos - 1
                scimoz.searchAnchor()
                nextEndTagPos = scimoz.searchPrev(0, endTagSearch)
                if firstVisiblePos is not None and nextEndTagPos < firstVisiblePos:
                    nextEndTagPos = -1
    finally:
        scimoz.currentPos = origPos
        scimoz.anchor = origAnchor

def tagEndFromStartViaFoldLevels(scimoz, startTagPos):
    """
    Do this only if the closing ">" of the start-tag and end-tag
    don't contain all or part of another tag.  Otherwise matching
    tags are easier to determine by searching through the document.
    
    @return either None, or a 4-tuple containing the start and end points
    of the start-tag and end-tag.
    """
    res = _verifyLoneStartTag(scimoz, startTagPos)
    if res is None:
        return None
    startTagStartPos, startTagEndPos, lineNo, tagName = res
    childLineNo = scimoz.getLastChild(lineNo, -1)
    if childLineNo == -1:
        return None
    # Find the last non-empty line before this
    while childLineNo > lineNo:
        if scimoz.positionFromLine(childLineNo) < scimoz.getLineEndPosition(childLineNo):
            break
        childLineNo -= 1
    if childLineNo <= lineNo:
        return None
        
    # Verify that this line contains one ">" and at most one "<" before the ">"
    endTagStartPos = _tagStartOnLine(scimoz, childLineNo,
                                     (scimoz.SCE_UDL_M_ETAGO,
                                      scimoz.SCE_UDL_M_ETAGC))
    if endTagStartPos == -1:
        return None
    res = _verifyLoneEndTag(scimoz, endTagStartPos)
    if res is None or tagName != res[3]:
        return None
    return startTagStartPos, startTagEndPos, res[0], res[1]

def tagEndFromStartViaMatchingName(scimoz, startTagPos, lastVisiblePos):
    """
    Start at the start-tag, and search forwards looking at
    <foo and </foo (assuming a starting tag name of "foo",
    make sure that we don't get fooled by tags like "<fool".
    If we find the matching opening "</foo", use its coordinates
    and return the usual 4-tuple.
    
    @return either None, or a 4-tuple containing the start and end points
    of the start-tag and end-tag.
    """
    startTagPos = _tagStartPosFromPos(scimoz, startTagPos, scimoz.SCE_UDL_M_STAGO)
    if startTagPos == -1:
        return None
    tagName = _getCurrTagName(scimoz, startTagPos + 1)
    
    origPos = scimoz.currentPos
    origAnchor = scimoz.anchor
    tagCount = 1
    searchJump = len(tagName) + 1
    scimoz.currentPos = scimoz.anchor = origPos + searchJump
    scimoz.searchAnchor()

    foundPos = startTagPos
    startTagSearch = "<" + tagName
    endTagSearch = "</" + tagName
    scimoz.currentPos = scimoz.anchor = foundPos + searchJump
    textLength = scimoz.textLength
    scimoz.searchAnchor()
    try:
        nextEndTagPos = scimoz.searchNext(0, endTagSearch)
        if lastVisiblePos is not None and nextEndTagPos > lastVisiblePos:
            return None
        nextStartTagPos = scimoz.searchNext(0, startTagSearch)
        canColourise = True
        while True:
            if nextEndTagPos == -1:
                return None
            elif nextStartTagPos > nextEndTagPos or nextStartTagPos == -1:
                if lastVisiblePos is not None and nextEndTagPos > lastVisiblePos:
                    return None
                style = scimoz.getStyleAt(nextEndTagPos)
                if style == 0 and canColourise:
                    if lastVisiblePos is None:
                        scimoz.colourise(startTagPos, -1)
                    else:
                        scimoz.colourise(startTagPos, lastVisiblePos)
                    canColourise = False
                    style = scimoz.getStyleAt(nextEndTagPos)
                if (style == scimoz.SCE_UDL_M_ETAGO
                    and (nextEndTagPos + searchJump + 1 >= textLength
                         or (scimoz.getStyleAt(nextEndTagPos + searchJump + 1)
                             != scimoz.SCE_UDL_M_TAGNAME))):
                    if tagCount == 1:
                        tagEndPos = _tagEndPosFromPos(scimoz, nextEndTagPos,
                                                      scimoz.SCE_UDL_M_ETAGC)
                        return (startTagPos,
                                _tagEndPosFromPos(scimoz, startTagPos,
                                                  scimoz.SCE_UDL_M_STAGC),
                                nextEndTagPos, tagEndPos)
                    tagCount -= 1
                scimoz.currentPos = scimoz.anchor = nextEndTagPos + searchJump + 1
                scimoz.searchAnchor()
                nextEndTagPos = scimoz.searchNext(0, endTagSearch)
            else:
                if lastVisiblePos is not None and nextStartTagPos > lastVisiblePos:
                    nextStartTagPos = -1
                    continue
                # Start-tag came first
                style = scimoz.getStyleAt(nextStartTagPos)
                if style == 0 and canColourise:
                    if lastVisiblePos is not None and nextStartTagPos > lastVisiblePos:
                        print "searching for end, got start-tag at %d past pos %d" % (nextStartTagPos, lastVisiblePos)
                        return None
                    if lastVisiblePos is None:
                        scimoz.colourise(startTagPos, -1)
                    else:
                        scimoz.colourise(startTagPos, lastVisiblePos)
                    canColourise = False
                    style = scimoz.getStyleAt(nextStartTagPos)
                if style == scimoz.SCE_UDL_M_STAGO:
                    closeTagPos = _getCloseTagPos(scimoz, nextStartTagPos)
                    if closeTagPos == -1:
                        return None
                    nextPos = closeTagPos + 1
                    if (scimoz.getStyleAt(closeTagPos) == scimoz.SCE_UDL_M_STAGC
                        and (nextEndTagPos + searchJump >= textLength
                             or (scimoz.getStyleAt(nextStartTagPos + searchJump)
                                 != scimoz.SCE_UDL_M_TAGNAME))):
                        tagCount += 1
                else:
                    nextPos = nextEndTagPos + searchJump + 1
                scimoz.currentPos = scimoz.anchor = nextPos
                scimoz.searchAnchor()
                nextStartTagPos = scimoz.searchNext(0, startTagSearch)
    finally:
        scimoz.currentPos = origPos
        scimoz.anchor = origAnchor

def _getCurrTagName(scimoz, pos):
    assert scimoz.getStyleAt(pos) == scimoz.SCE_UDL_M_TAGNAME
    tagNameStartPos = pos
    textLength = scimoz.length
    tagNameEndPos = scimoz.positionAfter(tagNameStartPos)
    while tagNameEndPos < textLength:
        if scimoz.getStyleAt(tagNameEndPos) != scimoz.SCE_UDL_M_TAGNAME:
            break
        tagNameEndPos = scimoz.positionAfter(tagNameEndPos)
    tagName = scimoz.getTextRange(tagNameStartPos, tagNameEndPos)
    return tagName

def _tagEndPosFromPos(scimoz, pos, targetStyle):
    textLength = scimoz.length
    while pos < textLength:
        if scimoz.getStyleAt(pos) == targetStyle:
            return pos
        pos += 1 # UTF8-safe, since we're searching for ASCII
    return -1

def _tagStartPosFromPos(scimoz, pos, targetStyle):
    textLength = scimoz.length
    while pos >= 0:
        if scimoz.getStyleAt(pos) == targetStyle:
            return pos
        pos -= 1
    return -1

def _tagStartOnLine(scimoz, lineNo, styles):
    lineStartPos = scimoz.positionFromLine(lineNo)
    lineEndPos = scimoz.getLineEndPosition(lineNo)
    for pos in range(lineStartPos, lineEndPos):
        if scimoz.getStyleAt(pos) in styles:
            return pos
    return -1

def adjustClosingXMLTag(scimoz, isHTML=False):
    """ This function is called when a ">" from an XML end tag
    is inserted, and it will shift the current line either back
    or forwards so that the tag is aligned with the matching start tag.
    It will only do so if the end tag is the only thing to the left of
    the current position on the current line.
    """
    beforeText = scimoz.getStyledText(0, scimoz.currentPos)[0::2]
    # (for now, assuming no intervening space)
    leftCloseIndex = beforeText.rfind('</')
    if leftCloseIndex == -1:
        # no idea what to do in this case, just bail
        return
    startTagInfo = startTagInfo_from_endTagPos(scimoz, leftCloseIndex, isHTML)
    if startTagInfo is None:
        return
    tagStartPos = startTagInfo[0]
    tagStartLine = scimoz.lineFromPosition(tagStartPos)
    tagStartLinePos = scimoz.positionFromLine(tagStartLine)
    if beforeText[tagStartLinePos:tagStartPos].strip():
        return
    tagStartCol = scimoz.getColumn(tagStartPos)
    indent = scimoz.indent
    if indent == 0:
        indent = 8
    indentLevel, extras = divmod(tagStartCol, indent)
    if indentLevel and not extras:
        indentLevel -= 1
    nextIndentWidth = indentLevel * scimoz.indent
    # The first decrement is safe because scimoz.charAt(scimoz.currentPos - 1) == '<'
    # The second has to go through the API in case it's a multi-byte char
    charPos = scimoz.positionBefore(scimoz.currentPos - 1)
    lineNo = scimoz.lineFromPosition(charPos)
    startOfLine = max(0, scimoz.positionFromLine(lineNo))
    if startOfLine > leftCloseIndex:
        return
    stuffToLeft = scimoz.getTextRange(startOfLine, leftCloseIndex)
    if not stuffToLeft.strip(): # XXX Do we want to pref this?
        # we can align the comment closing before we do the newline
        indent = makeIndentFromWidth(scimoz, tagStartCol)
        scimoz.targetStart = scimoz.positionFromLine(lineNo)
        scimoz.targetEnd = leftCloseIndex
        scimoz.replaceTarget(len(indent), indent)
    scimoz.chooseCaretX()
