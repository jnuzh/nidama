# Copyright (c) 2000-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

import sys

from xpcom import components, COMException, ServerException
from xpcom.server import UnwrapObject
import logging
import eollib

from zope.cachedescriptors.property import LazyClassAttribute

log = logging.getLogger('koDocumentSettingsManager')
#log.setLevel(logging.DEBUG)

def RGB(r,g,b): return r+g*256+b*256*256

# Must keep this marker constants in sync with markers.js MARKNUM_*
#XXX Should create a module for that because koScintillaSchemeService.py
#    has the same issue.
MARKNUM_BOOKMARK = 6

MARKNUM_BREAKPOINT_ENABLED = 2


import string
_letters = string.ascii_letters + string.digits + '_'

class koDocumentSettingsManager:
    _com_interfaces_ = [components.interfaces.koIDocumentSettingsManager,
                        components.interfaces.nsIObserver]
    _reg_desc_ = "Komodo Document Settings Manager"
    _reg_contractid_ = "@activestate.com/koDocumentSettingsManager;1"
    _reg_clsid_ = "{5ECD8F3B-4118-43F4-82AA-DB7AC60F9A6D}"

    # A list of view-related preferences.
    _viewPrefList = ['showWhitespace', 'showIndentationGuides', 'showEOL',
                     'editUseAlternateFaceType', 'showLineNumbers',
                     'editWrapType', 'editAutoWrapColumn', 'editUseEdge',
                     'encoding', 'editFoldStyle', 'anchor', 'currentPos',
                     'editFoldLines', 'indentWidth', 'caretStyle', 'caretWidth',
                     'editor_font_quality',
                     # Code Intelligence stuff:
                     'codeintel_completion_triggering_enabled',
                     'codeintel_rescan_while_typing_enabled',
                ]

    def __init__(self):
        self.koDoc = None
        self._observed_prefs = None
        self._foldFlags = 0
        self._scintillas = []
        self._useAlternateFaceType = None

    @LazyClassAttribute
    def _globalPrefs(self):
        return components.classes["@activestate.com/koPrefService;1"].\
                            getService(components.interfaces.koIPrefService).prefs


    @LazyClassAttribute
    def _breakpointMgr(self):
        return components.classes["@activestate.com/koDBGPBreakpointManager;1"].\
            getService(components.interfaces.koIDBGPBreakpointManager)


    def register(self, koDoc, scintilla):
        self.koDoc = koDoc
        if scintilla in self._scintillas:
            log.error("Already have scimoz %r for koDoc %s",scintilla, koDoc)
            raise ServerException
        self._scintillas.append(scintilla)
        # Two cases-- either this is the first scintilla
        # for this document, or it's not.  In the first
        # case, then the buffer needs to be gotten from
        # the document.  In the other it's just a matter of
        # sharing docpointers
        scimoz = scintilla.scimoz
        if len(self._scintillas) == 1:
            scimoz.undoCollection = 0
            scimoz.emptyUndoBuffer()
            scimoz.readOnly = 0
            buffer = koDoc.buffer
            scimoz.text = buffer
            scimoz.undoCollection = 1
            scimoz.setSavePoint()
            scimoz.emptyUndoBuffer()

            self._breakpointMgr.addMarkersForDocument(koDoc, scintilla)

        else:
            scimoz.docPointer = self._scintillas[0].scimoz.docPointer
            
        scimoz.eOLMode = eollib.eol2scimozEOL[koDoc.new_line_endings]
        self.applyDocumentSettingsToView(scintilla)
        # Watch for preference set changes from these pref sets.
        if self._observed_prefs is None:
            pref_topics = []
            for name in dir(self):
                if name.startswith("_apply_"):
                    pref_topics.append(name[len("_apply_"):])
            #print 'pref_topics: %r' % (pref_topics, )
            if pref_topics:
                globalPrefObserverSvc = self._globalPrefs.prefObserverService
                globalPrefObserverSvc.addObserverForTopics(self, pref_topics, True)
                docPrefObserverSvc = self.koDoc.prefs.prefObserverService
                docPrefObserverSvc.addObserverForTopics(self, pref_topics, True)
            self._observed_prefs = pref_topics

    def unregister(self, scintilla):
        if scintilla not in self._scintillas:
            log.error("can't unregister unknown scimoz: %r", scintilla)
            raise ServerException
        self._scintillas.remove(scintilla)
        if not self._scintillas:
            # We just got rid of the last view for this document
            # We should save the state of that last view
            self.applyViewSettingsToDocument(scintilla)
            if self._observed_prefs:
                # remove observers
                # XXX these cause exceptions regarding weakref/null pointer, but
                # NOT doing this we continue to leak editor wrappers.
                globalPrefObserverSvc = self._globalPrefs.prefObserverService
                globalPrefObserverSvc.removeObserverForTopics(self, self._observed_prefs)
                docPrefObserverSvc = self.koDoc.prefs.prefObserverService
                docPrefObserverSvc.removeObserverForTopics(self, self._observed_prefs)
                self._observed_prefs = None
            self.koDoc = None
        
    def applyDocumentSettingsToView(self, scintilla):
        scimoz = scintilla.scimoz
        # assumption: we are given a 'virgin' view, and a fully
        # capable document -- if it doesn't know something, it can figure it out.
        languageOb = self.koDoc.languageObj
        koDoc = self.koDoc
        prefs = koDoc.prefs
        try:
            # Unwrap prefs, as it will be faster to work outside of XPCOM.
            prefs = UnwrapObject(prefs)
        except:
            pass
        lexer = koDoc.lexer
        if lexer is None:
            lexer = languageOb.getLanguageService(components.interfaces.koILexerLanguageService)
        lexer.setCurrent(scimoz)
        self._setIndicators(languageOb, scimoz)
        self._applyPrefs(prefs, scimoz)
        
        if prefs.hasLongPref('anchor'):
            scimoz.currentPos = scimoz.anchor = prefs.getLongPref('anchor')

        if prefs.hasLongPref('currentPos'):
            scimoz.currentPos = prefs.getLongPref('currentPos')

        if prefs.hasPrefHere('indentWidth'):
            scimoz.indent = prefs.getLongPref('indentWidth')
        else:
            scimoz.indent = koDoc.indentWidth

        if prefs.hasPrefHere('editUseAlternateFaceType'):
            useAlternate = prefs.getBooleanPref('editUseAlternateFaceType')
        else:
            useAlternate = 0
        scintilla.alternateFaceType = useAlternate
        self._updateEdge(prefs)
            
        if prefs.hasPrefHere('useTabs'):
            scimoz.useTabs = prefs.getBooleanPref('useTabs')
        else:
            scimoz.useTabs = koDoc.useTabs

        if prefs.hasPrefHere('tabWidth'):
            scimoz.tabWidth = prefs.getLongPref('tabWidth')
        else:
            scimoz.tabWidth = koDoc.tabWidth

        slop = prefs.getLongPref('ySlop')
        scimoz.setYCaretPolicy(scimoz.CARET_SLOP | scimoz.CARET_STRICT | scimoz.CARET_EVEN, slop)
        scimoz.setVisiblePolicy(scimoz.VISIBLE_SLOP | scimoz.VISIBLE_STRICT, slop)

        if prefs.hasLongPref('firstVisibleLine'):
            scimoz.lineScroll(0, prefs.getLongPref('firstVisibleLine'))

        # scrollWidth is disabled on OS X - see bug 88586.
        if sys.platform != "darwin":
            if prefs.hasLongPref('scrollWidth'):
                scimoz.scrollWidth = prefs.getLongPref("scrollWidth")
            else:
                log.warn('should set default scroll width?')

        if prefs.getBooleanPref('scrollWidthTracking'):
            scimoz.scrollWidthTracking = prefs.getBooleanPref("scrollWidthTracking")

        if prefs.hasLongPref('xOffset'):
            scimoz.xOffset = prefs.getLongPref('xOffset')
        else:
            scimoz.xOffset = 0

        if languageOb.variableIndicators:
            scimoz.wordChars = _letters + languageOb.variableIndicators
        else:
            # Do this for cases where we change languages.
            scimoz.setCharsDefault()
        
        # restore fold points if the user has checked that pref off.
        # We don't do it by default because the colourise(.., -1) call below
        # can be quite slow.
        # Bug 93190: prefs are boolean for foldPoints,
        # but get the actual foldPoints off the document prefs
        if prefs.getBooleanPref("editRestoreFoldPoints") and \
                prefs.hasPref('foldPoints') and \
                scimoz.getPropertyInt("fold"):
            foldPoints = prefs.getPref("foldPoints")
            if foldPoints.length:
                # restyle the whole document to get folding right
                # Fixes bug 45621
                scimoz.colourise(0, -1)
                for i in range(foldPoints.length):
                    scimoz.toggleFold(foldPoints.getLongPref(i));

        # restore the bookmarks
        # Bug 93190: use doc prefs, stay away from project prefs here
        if prefs.hasPref("bookmarks"):
            bookmarks = prefs.getPref("bookmarks")
            for i in range(bookmarks.length):
                scimoz.markerAdd(bookmarks.getLongPref(i), MARKNUM_BOOKMARK)

    def applyViewSettingsToDocument(self, scintilla):
        prefs = self.koDoc.prefs
        try:
            # Unwrap prefs, as it will be faster to work outside of XPCOM.
            prefs = UnwrapObject(prefs)
        except:
            pass
        # these should all be conditional on not being the
        # default prefs.
        scimoz = scintilla.scimoz
        prefs.setLongPref('anchor', scimoz.anchor)
        prefs.setLongPref('currentPos', scimoz.currentPos)

        # scrollWidth is disabled on OS X - see bug 88586.
        if sys.platform != "darwin":
            prefs.setLongPref("scrollWidth", scimoz.scrollWidth)

        prefs.setBooleanPref("scrollWidthTracking", scimoz.scrollWidthTracking)
        prefs.setLongPref('xOffset', scimoz.xOffset)
        prefs.setLongPref('firstVisibleLine', scimoz.firstVisibleLine)
        prefs.setBooleanPref('showWhitespace', scimoz.viewWS)
        prefs.setBooleanPref('showLineNumbers', scimoz.getMarginWidthN(0) != 0)
        prefs.setBooleanPref('showIndentationGuides', scimoz.indentationGuides)
        prefs.setBooleanPref('showEOL', scimoz.viewEOL)
        prefs.setBooleanPref('editFoldLines', self._foldFlags)
        #prefs.setStringPref('editFoldStyle', ... )
        #prefs.setStringPref('editUseFixedFont', ... )
        prefs.setLongPref('editWrapType', scimoz.wrapMode)

        # these should be saved only if they were explicitely
        # set, not if they were just computed
        if prefs.hasPrefHere('useTabs'):
            prefs.setBooleanPref('useTabs', scimoz.useTabs)
        if prefs.hasPrefHere('indentWidth'):
            prefs.setLongPref('indentWidth', scimoz.indent)
        if prefs.hasPrefHere('tabWidth'):
            prefs.setLongPref('tabWidth', scimoz.tabWidth)

        if prefs.getBooleanPref("editRestoreFoldPoints"):
            i = scimoz.contractedFoldNext(0)
            if i >= 0:
                foldPoints = components.classes[
                    '@activestate.com/koOrderedPreference;1'].createInstance()
                foldPoints.id = "foldPoints"
                while i != -1:
                    foldPoints.appendLongPref(i)
                    i = scimoz.contractedFoldNext(i+1)
                prefs.setPref("foldPoints", foldPoints)
        else:
            # we don't want to store foldpoints if there are none
            # reloading them is expensive.
            if prefs.hasPref('foldPoints'):
                prefs.deletePref('foldPoints')

        # Get the bookmarks.
        bookmarks = None
        marker_mask = 1 << MARKNUM_BOOKMARK
        lineNo = scimoz.markerNext(0, marker_mask)
        while lineNo >= 0:
            if bookmarks is None:
                bookmarks = components.classes['@activestate.com/koOrderedPreference;1'] \
                                .createInstance()
                bookmarks.id = "bookmarks"
                prefs.setPref("bookmarks", bookmarks)
            bookmarks.appendLongPref(lineNo)
            lineNo = scimoz.markerNext(lineNo+1, marker_mask)
        if bookmarks is None and prefs.hasPrefHere("bookmarks"):
            # Remove old bookmarks.
            prefs.deletePref("bookmarks")

        #XXX Breakpoint restoring is now done elsewhere. Note that taking this
        #    out of the view prefs here breaks the transfer of breakpoints
        #    via a "Save As..." operation. See:
        #       views-editor.xml::saveAsURI(), line 609

    def _setIndicators(self, languageOb, scimoz):
        styleBits = languageOb.styleBits
        scimoz.styleBits = styleBits
        # Determine how many indicators we can have.
        indicBits = languageOb.indicatorBits

        #XXX Scintilla renames the indicators depending on the number of style bits :-(.
        #XXX Compensate.
        indicOffset = 8 - styleBits - indicBits
        if indicBits == 2:
            scimoz.indicSetStyle(indicOffset + 1, scimoz.INDIC_SQUIGGLE);
            scimoz.indicSetFore(indicOffset + 1, RGB(0xff,0,0));
            scimoz.indicSetStyle(indicOffset, scimoz.INDIC_SQUIGGLE);
            scimoz.indicSetFore(indicOffset, RGB(0,0x80,0));
        else:
            scimoz.indicSetStyle(indicOffset, scimoz.INDIC_SQUIGGLE);
            scimoz.indicSetFore(indicOffset, RGB(0xff,0,0));

    def _updateLineNumberMargin(self):
        for scintilla in self._scintillas:
            scintilla.scimoz.setMarginWidthN(0,
                scintilla.scimoz.textWidth(0,
                    str(max(1000,scintilla.scimoz.lineCount*2)))+5)

    # nsIObserver interface
    def observe(self, prefSet, topic, data):
        # Dispatch a preference change...
        #print 'topic: %r' % (topic, )
        # Always use the document prefs to lookup pref values.
        self._dispatchPrefChange(self.koDoc.prefs, topic)

    # Probably should make this function table-based to reduce
    # duplication of effort.
    def _dispatchPrefChange(self, prefSet, prefName):
        if hasattr(self, "_apply_" + prefName):
            getattr(self, "_apply_" + prefName)(prefSet)

    def _apply_ySlop(self, prefSet):
        for scintilla in self._scintillas:
            scimoz = scintilla.scimoz
            scimoz.setYCaretPolicy(scimoz.CARET_SLOP | scimoz.CARET_STRICT | scimoz.CARET_EVEN,
                                   prefSet.getLongPref('ySlop'))

    def _apply_useTabs(self, prefSet):
        for scintilla in self._scintillas:
            scintilla.scimoz.useTabs = prefSet.getBooleanPref('useTabs')

    def _apply_indentWidth(self, prefSet):
        #print 'setting indentWidth = ', prefSet.getLongPref('indentWidth')
        for scintilla in self._scintillas:
            scintilla.scimoz.indent = prefSet.getLongPref('indentWidth')

    def _apply_tabWidth(self, prefSet):
        for scintilla in self._scintillas:
            scintilla.scimoz.tabWidth = prefSet.getLongPref('tabWidth')

    def _apply_showWhitespace(self, prefSet):
        for scintilla in self._scintillas:
            scintilla.scimoz.viewWS = prefSet.getBooleanPref('showWhitespace')

    def _apply_editWrapType(self, prefSet):
        editWrapType= prefSet.getLongPref('editWrapType')
        if editWrapType:
            for scintilla in self._scintillas:
                scimoz = scintilla.scimoz
                scimoz.wrapMode = editWrapType
        else:
            for scintilla in self._scintillas:
                scimoz = scintilla.scimoz
                scimoz.wrapMode = scimoz.SC_WRAP_NONE

    def _apply_editWordWrapMarker(self, prefSet):
        editWordWrapMarker= prefSet.getLongPref('editWordWrapMarker')
        for scintilla in self._scintillas:
            scintilla.scimoz.wrapVisualFlags = editWordWrapMarker

    def _apply_editWordWrapIndentation(self, prefSet):
        editWordWrapIndentation= prefSet.getLongPref('editWordWrapIndentation')
        for scintilla in self._scintillas:
            scintilla.scimoz.wrapIndentMode = editWordWrapIndentation

    def _apply_editUseEdge(self, prefSet):
        self._updateEdge(prefSet)

    def _updateEdge(self, prefSet):
        if prefSet.getBooleanPref('editUseEdge'):
            for scintilla in self._scintillas:
                scintilla.scimoz.edgeColumn = prefSet.getLongPref('editAutoWrapColumn')
                if scintilla.scheme.preferFixed and not scintilla.alternateFaceType:
                    scintilla.scimoz.edgeMode = scintilla.scimoz.EDGE_LINE
                else:
                    scintilla.scimoz.edgeMode = scintilla.scimoz.EDGE_BACKGROUND
        else:
            for scintilla in self._scintillas:
                scintilla.scimoz.edgeColumn = prefSet.getLongPref('editAutoWrapColumn')
                scintilla.scimoz.edgeMode = scintilla.scimoz.EDGE_NONE
            
    def _apply_editAutoWrapColumn(self, prefSet):
        self._updateEdge(prefSet)

    def _apply_editUseAlternateFaceType(self, prefSet):
        self._updateEdge(prefSet)

    def _apply_showIndentationGuides(self, prefSet):
        for scintilla in self._scintillas:
            scintilla.scimoz.indentationGuides = prefSet.getBooleanPref('showIndentationGuides')

    def _apply_showEOL(self, prefSet):
        for scintilla in self._scintillas:
            scintilla.scimoz.viewEOL = prefSet.getBooleanPref('showEOL')

    def _apply_showLineNumbers(self, prefSet):
        if prefSet.getBooleanPref('showLineNumbers'):
            self._updateLineNumberMargin()
        else:
            for scintilla in self._scintillas:
                scintilla.scimoz.setMarginWidthN(0, 0)

    def _apply_caretStyle(self, prefSet):
        caretStyle = prefSet.getLongPref('caretStyle')
        for scintilla in self._scintillas:
            scintilla.scimoz.caretStyle = caretStyle

    def _apply_caretWidth(self, prefSet):
        caretWidth = prefSet.getLongPref('caretWidth')
        for scintilla in self._scintillas:
            scintilla.scimoz.caretWidth = caretWidth

    def _apply_editor_font_quality(self, prefSet):
        fontQuality = prefSet.getLongPref('editor_font_quality')
        for scintilla in self._scintillas:
            scintilla.scimoz.fontQuality = fontQuality

    def _apply_editFoldLines(self, prefSet):
        on = prefSet.getBooleanPref('editFoldLines')
        # scintilla doesn't provide an accessor for fold flags
        if on and self._scintillas:
            self._foldFlags = self._scintillas[0].scimoz.SC_FOLDFLAG_LINEAFTER_CONTRACTED
        else:
            self._foldFlags = 0
        for scintilla in self._scintillas:
            scintilla.scimoz.setFoldFlags(self._foldFlags)

    def _apply_editFoldStyle(self, prefSet):
        """
        bug 81961:
        This is an expensive function for UDL documents with very long lines
        (around > 10K).
        """
        # use margin 1 for folding
        if not self.koDoc.languageObj.foldable:
            for scintilla in self._scintillas:
                scintilla.scimoz.setProperty("fold", "0")
                scintilla.scimoz.setMarginWidthN(1, 0)
            return
        foldstyle = prefSet.getStringPref('editFoldStyle')
        if foldstyle != 'none':
            self._enableFolding(1, foldstyle)
            # we'll just work with one of the views
            scimoz = self._scintillas[0].scimoz
            # XXX review logic
            lastLine = min(scimoz.firstVisibleLine + scimoz.linesOnScreen,
                           scimoz.lineCount-1)
            needStyleTo = scimoz.positionFromLine(lastLine)
            if scimoz.endStyled < needStyleTo:
                scimoz.colourise(scimoz.endStyled, needStyleTo)
            for scintilla in self._scintillas:
                scintilla.scimoz.setMarginWidthN(1, 15)
        else:
            for scintilla in self._scintillas:
                scimoz = scintilla.scimoz
                scimoz.showLines(0, scimoz.lineCount-1)
                i = scimoz.contractedFoldNext(0)
                while i != -1:
                    scimoz.setFoldExpanded(i, 1)
                    i = scimoz.contractedFoldNext(i+1)
                # If we don't do this, folding trails off into other buffers.
                scimoz.setProperty("fold", "0")
                scimoz.setMarginWidthN(1, 0)
            
    def _apply_encoding(self, prefSet):
        if prefSet.hasStringPref('encoding'):
            for scintilla in self._scintillas:
                scintilla.encoding = prefSet.getStringPref('encoding')
    
    def _applyPrefs(self, prefs, scimoz):
        for prefName in self._viewPrefList:
            self._dispatchPrefChange(prefs, prefName)
            
    def _apply_Default_fixed(self, prefSet):
        pass
        #self._applyStyles()
            
    def _apply_Default_proportional(self, prefSet):
        pass
        #self._applyStyles()
    
    def _enableFolding(self, whichMargin, foldstyle):
        for scin in self._scintillas:
            scin.setFoldStyle(whichMargin, foldstyle)

