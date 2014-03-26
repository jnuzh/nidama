#!python
# Copyright (c) 2004-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

import os
from os.path import dirname, join, abspath, normpath, basename
import sys
import re
import operator
import bisect
from pprint import pprint, pformat
import logging
from cStringIO import StringIO
import traceback
from hashlib import md5
import time

import SilverCity
from SilverCity import ScintillaConstants
#XXX Import only what we need
from SilverCity.ScintillaConstants import *

from codeintel2.common import *
from codeintel2.util import isident, indent, banner, markup_text

if _xpcom_:
    from xpcom import components
    from xpcom.server import UnwrapObject

#XXX We need to have a better mechanism for rationalizing and sharing
#    common lexer style classes. For now we'll just HACKily grab from
#    Komodo's styles.py. Some of this is duplicating logic in
#    KoLanguageServiceBase.py.
_ko_src_dir = normpath(join(dirname(__file__), *([os.pardir]*3)))
sys.path.insert(0, join(_ko_src_dir, "schemes"))
try:
    import styles
finally:
    del sys.path[0]
    del _ko_src_dir


log = logging.getLogger("codeintel.buffer")



#---- module interface

class Buffer(object):
    if _xpcom_:
        _com_interfaces_ = [components.interfaces.koICodeIntelBuffer]

    # Language-specific attributes that subclasses must fill-in.
    lang = None             # language name
    cpln_fillup_chars = ""  # chars on which autocomplete UI will "fillup"
    cpln_stop_chars = ""    # chars on which autocomplete UI will stop

    # Separator btwn completions in a completion list string for the
    # Scintilla API.
    # We don't use the default, ' ', because so of our languages have
    # completions with spaces in them (e.g. Tcl).
    scintilla_cpln_sep = '\n'
    scintilla_cpln_sep_ord = ord(scintilla_cpln_sep) 
    
    # <prefix><stylename>, scintilla style constants prefix for this
    # language. Most languages just have one prefix (e.g. "SCE_P_" for
    # Python), but HTML, for example, has many.
    sce_prefixes = None

    # Code Browser control. (Note: most code browser control is on the
    # relevant LangIntel).
    # 
    # Show a row for this buffer even if empty of code browser data.
    cb_show_if_empty = False

    # Lazily built cache of SCE_* style number (per language) to constant
    # name.
    _style_name_from_style_num_from_lang = {}

    def __init__(self, mgr, accessor, env=None, path=None, encoding=None,
                 lang=None, *args, **kwargs):
        self.mgr = mgr
        self.accessor = accessor # an Accessor instance
        self._env = env
        self.path = path if path is not None else "<Unsaved>"
        self.encoding = encoding
        if lang is not None:
            self.lang = lang

        self.implicit_completion_skip_styles = dict(
            (s, True) for s in self.comment_styles() + self.string_styles())
        self.completion_skip_styles = dict(
            (s, True) for s in self.number_styles())

        super(Buffer, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<%s buf '%s'>" % (self.lang,
                                  basename(self.path) if self.path is not None else "(no file)")

    @property
    def env(self):
        """The runtime Environment instance for this buffer."""
        return self._env or self.mgr.env

    _langintel_cache = None
    @property
    def langintel(self):
        if self._langintel_cache is None:
            self._langintel_cache = self.mgr.langintel_from_lang(self.lang)
        return self._langintel_cache

    _langinfo_cache = None
    @property
    def langinfo(self):
        if self._langinfo_cache is None:
            self._langinfo_cache = self.mgr.lidb.langinfo_from_lang(self.lang)
        return self._langinfo_cache

    def lang_from_pos(self, pos):
        return self.lang

    def set_project(self, project):
        if self.env:
            self.env.set_project(project)

    def trg_from_pos(self, pos, implicit=True):
        """If the given position is a _likely_ trigger point, return a
        relevant Trigger instance. Otherwise return the None.
        
            "pos" is the position at which to check for a trigger point.
            "implicit" (optional) is a boolean indicating if this trigger
                is being implicitly checked (i.e. as a side-effect of
                typing). Defaults to true.

        Implementations of this should be *fast* because editor usage will
        likely call this for most typed characters.

        The default implementation defers to the langintel for this buffer.
        This is generally a better place to implement trg_from_pos if this
        language's content can appear in a multi-language buffer (e.g. CSS).
        """
        return self.langintel.trg_from_pos(self, pos, implicit)

    def preceding_trg_from_pos(self, pos, curr_pos):
        """Look back from the given position for a trigger point within
        range.
        
            "pos" is the position at which to begin backtracking. (I.e. for
                the first Ctrl+J this is the cursor position, for the next
                Ctrl+J it is the position of the current
                autocomplete/calltip UI.)
            "curr_pos" is the current position -- the one to use to
                determine if within range of a found trigger. (I.e. this is
                the cursor position in Komodo.)
        
        Here "within range" depends on the language and the trigger. This
        is the main determinant for the "Ctrl+J" (explicitly trigger
        completion now) functionality in Komodo, for example, and the
        ultimate goal is to not surprisingly move the cursor on the user.
        Here is the algorithm:
        - Only consider a *completion* (i.e. TRG_FORM_CPLN) trigger point
          if `pos' is in range. I.e.:
                sys.pat<|>h         # consider the `sys.' trigger
                os.path.join("<|>   # do not consider the `os.path.' trigger
        - Only consider a calltip trigger point inside the argument
          region.
          
        I.e., "within range" means, we could show the UI for that completion
        in scintilla without having to move the cursor.
        
        The default implementation defers to the langintel for this buffer.

        Returns a Trigger instance or None.
        """
        return self.langintel.preceding_trg_from_pos(self, pos, curr_pos)

    def async_eval_at_trg(self, trg, ctlr):
        """Asynchronously determine completion/calltip info for the given
        trigger.
        
            "trg" is the trigger at which to evaluate (a Trigger instance).
            "ctlr" is the controller (a EvalController instance) used to
                relay results and status and to receive control signals.
        
        Rules for implementation:
        - Must call ctlr.start(buf, trg) at start.
        - Should call ctlr.set_desc(desc) near the start to provide a
          short description of the evaluation. 
        - Should log eval errors via ctlr.error(msg, args...).
        - Should log other events via ctlr.{debug|info|warn}.
        - Should respond to ctlr.abort() in a timely manner.
        - If successful, must report results via one of
          ctlr.set_cplns() or ctlr.set_calltips().
        - Must call ctlr.done(some_reason_string) when done.

        Tips for implementation:
        - The typical structure of an async_eval_at_trg() implementation is:
            ctlr.start(self, trg)  # or 'buf' if implemented on LangIntel
            if trg.id == (<lang>, TRG_FORM_CPLN, <type>):
                # handle this trigger type
            elif trg.id == (<lang>, TRG_FORM_CPLN, <type>):
                # handle this trigger type
            ...
        - If evaluation of a particular trigger type is fast (i.e. just a
          lookup in a hardcoded data structure) then it is okay to process
          asynchronously.

        The default implementation defers to the langintel for this buffer.

        Returns no value. All interaction is on the controller. This may
        raise CodeIntelError on an unexpected error condition.
        """
        #XXX xpcom UnwrapObject here?
        self.langintel.async_eval_at_trg(self, trg, ctlr)

    def cplns_from_trg(self, trg, timeout=None, ctlr=None):
        """Return completions for the given trigger point.

            "trg" is the trigger point at which to eval completions.
            "timeout" (optional) is a number of seconds after which to
                abandon completion. Raises EvalTimeout if the timeout is
                reached.
            "ctlr" (optional) is a EvalController instance to use for
                custom interaction with the evaluation.

        This is a convenience synchronous wrapper around async_eval_at_trg().
        Use the async version for any more interesting interaction.
        
        A "completion" is a 2-tuple -- (<type>, <completion-string>) -- where
        <type> is currently just a string like "variable", "class", etc.
        """
        assert timeout is None or isinstance(timeout, (float, int)),\
            "'timeout' must be None or a number"
        if ctlr is None:
            ctlr = EvalController()
        self.async_eval_at_trg(trg, ctlr)
        ctlr.wait(timeout)
        if not ctlr.is_done():
            ctlr.done("timed out")
            raise EvalTimeout("eval for %s timed-out" % trg)
        return ctlr.cplns

    def calltips_from_trg(self, trg, timeout=None, ctlr=None):
        """Return calltips for the given trigger point.

            "trg" is the trigger point at which to eval completions.
            "timeout" (optional) is a number of seconds after which to
                abandon completion. Raises EvalTimeout if the timeout is
                reached.
            "ctlr" (optional) is a EvalController instance to use for
                custom interaction with the evaluation.

        This is a convenience synchronous wrapper around async_eval_at_trg().
        Use the async version for any more interesting interaction.
        """
        assert timeout is None or isinstance(timeout, (float, int)),\
            "'timeout' must be None or a number"
        if ctlr is None:
            ctlr = EvalController()
        self.async_eval_at_trg(trg, ctlr)
        ctlr.wait(timeout)
        if not ctlr.is_done():
            ctlr.done("timed out")
            raise EvalTimeout("eval for %s timed-out" % trg)
        return ctlr.calltips

    def curr_calltip_arg_range(self, trg_pos, calltip, curr_pos, DEBUG=False):
        """Return that range in the calltip of the "current" arg.
        I.e. what argument is currently being entered.
        
            "trg_pos" is the trigger position.
            "calltip" is the full calltip text.
            "curr_pos" is the current position in the buffer.

        Returns a range: (start, end)
        Set `start == -1` to cancel the calltip, i.e. if the entered text
        has closed the call region.

        The default implementation uses defers to the LangIntel
        singleton for this language.
        """
        return self.langintel.curr_calltip_arg_range(self, trg_pos, calltip,
                                                     curr_pos, DEBUG=DEBUG)

    def text_chunks_from_lang(self, lang):
        """Generate a list of text chunks of the given language content.

        For a single-language buffer this is trivial: 1 chunk of the whole
        buffer. For multi-language buffers, less so.

        Generates 2-tuples:
            (POSITION-OFFSET, TEXT-CHUNK)
        """
        yield 0, self.accessor.text

    @property
    def sections(self):
        """Generate a sequence of sections for this buffer.

        Generates a sequence of `Section` instances.
        """
        for s in self.langintel.sections_from_buf(self):
            yield s

    _sections_cache = None  # (TIME-CACHED, MD5-OF-TEXT, SECTIONS)
    @property
    def cached_sections(self):
        """A version of `self.sections` that does some light and
        independent caching. It also returns a list of sections instead
        of a generator.
        
        Note: It is possible that this doesn't provide that correct
        latest set of sections -- if the document was modified in the
        last 2 seconds and you got unlucky with the timing.
        """
        if self.langintel is None or not self.langintel.sectionsEnabled(self):
            return []
        now = time.time()
        if self._sections_cache is None:
            # text_bytes is just a bag of bytes representing the text (so we can
            # hash it).  It's not actually usable for processing, because we use
            # the unicode_internal encoding if it's Unicode text - that's just a
            # type cast and no real conversion is done, so its format is
            # platform-specific.
            text_bytes = self.accessor.text
            if isinstance(text_bytes, unicode):
                text_bytes = text_bytes.encode("unicode_internal")
            md5sum = md5(text_bytes).hexdigest()
            self._sections_cache = (now, md5sum, list(self.sections))
        else:
            cached_time, cached_md5sum, cached_sections = self._sections_cache
            if now - cached_time < 2:
                # Re-calculate sections every 2 seconds, max.
                # The intention here is to save the time in calculating
                # the md5sum of the file frequently.
                pass
            else:
                # See above on why we're using text_bytes for hexdigest
                text_bytes = self.accessor.text
                if isinstance(text_bytes, unicode):
                    text_bytes = text_bytes.encode("unicode_internal")
                md5sum = md5(text_bytes).hexdigest()
                if md5sum != cached_md5sum:
                    # Need to re-calculate.
                    # WARNING: This effectively gets done synchronously
                    # for adding a new line in Komodo. If `self.sections`
                    # takes a pathologically long time, then editing in
                    # Komodo is crippled!
                    self._sections_cache = (now, md5sum, list(self.sections))
                else:
                    self._sections_cache = (now, cached_md5sum, cached_sections)
        return self._sections_cache[2]

    def curr_section_from_line(self, curr_line, use_cached_sections=True):
        sections = self.get_sections(use_cached_sections)
        curr_idx = self._section_idx_from_line(curr_line, sections)
        if curr_idx == -1:
            return None
        else:
            return sections[curr_idx]

    def prev_section_from_line(self, curr_line, wrap=True,
                               use_cached_sections=True):
        """Return the section preceding the current one.
        
        @param curr_line {int} is the current line number (1-based).
        @param wrap {boolean} indicates whether to return the last
            section if currently at the first section (or above). Default
            true.
        @param use_cached_sections {boolean} indicates whether to use
            `self.cached_sections` rather than `self.sections`. Default
            true.
        """
        sections = self.get_sections(use_cached_sections)
        curr_idx = self._section_idx_from_line(curr_line, sections)
        prev_idx = curr_idx - 1
        if prev_idx < 0:
            if sections and wrap:
                return sections[-1]
            else:
                return None
        else:
            return sections[prev_idx]

    def next_section_from_line(self, curr_line, wrap=True,
                               use_cached_sections=True):
        """Return the section succeeding the current one.
        
        @param curr_line {int} is the current line number (1-based).
        @param wrap {boolean} indicates whether to return the first
            section if currently at the last section. Default true.
        @param use_cached_sections {boolean} indicates whether to use
            `self.cached_sections` rather than `self.sections`. Default
            true.
        """
        sections = self.get_sections(use_cached_sections)
        curr_idx = self._section_idx_from_line(curr_line, sections)
        next_idx = curr_idx + 1
        if next_idx >= len(sections):
            if sections and wrap:
                return sections[0]
            else:
                return None
        else:
            return sections[next_idx]

    def get_sections(self, use_cached_sections=True):
        """Return all sections for the current buffer"""
        if use_cached_sections:
            return self.cached_sections

        return list(self.sections)

    def _section_idx_from_line(self, line, sections=None):
        """Return the section index given a line number
        @param line {int} The line to look up
        """
        if not sections:
            sections = self.get_sections()
        lines = [s.line for s in sections]
        return bisect.bisect_right(lines, line) - 1

    def curr_section_idx_from_line(self, curr_idx,
                                   use_cached_sections=True):
        return self.sections_from_line(curr_idx, use_cached_sections)[1]

    @property
    def libs(self):
        """Return the ordered list libraries in which to search for blob
        imports in this buffer.
        
        Each "library" is an instance of a database *Lib class that
        provides the has_blob()/get_blob() API. See the
        database/database.py module docstring for details.

        Commonly a buffer (for a typical programming language) will have
        some or all of the following libs:
            curdirlib/runtimedirlib
            extradirslib (based on *ExtraPaths prefs in the buffer's env)
            envlib (e.g. from PYTHONPATH, PERL5LIB, ... if set)
            cataloglib
            sitelib
            stdlib
        """
        raise VirtualMethodError("Buffer subclass for lang '%s' should "
                                 "implement the 'libs' property" % self.lang)

    def to_html(self, include_styling=False, include_html=False, title=None,
                do_trg=False, do_eval=False):
        """Return a styled HTML snippet for the current buffer.
        
            "include_styling" (optional, default False) is a boolean
                indicating if the CSS/JS/informational-HTML should be
                included.
            "include_html" (optional, default False) is a boolean indicating
                if the HTML output should be wrapped into a complete HTML
                document.
            "title" is the HTML document title to use if 'include_html' is
                True.
            "do_trg" (optional, default False) indicates that trigger
                handling should be done. This implies do_eval=True.
            "do_eval" (optional, default False) indicates that completion
                eval should be done.
        """
        from cStringIO import StringIO
        html = StringIO()
        
        if include_html:
            html.write('''\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>%s</title>
</head>
<body>
''' % title)

        if include_styling:
            html.write('''
<script type="application/x-javascript">
    function show_class(span) {
        var infobox = document.getElementById("infobox");
        infobox.innerHTML = span.getAttribute("class");
    }
</script>

<style>
#infobox {
    border: 4px solid #e0e0e0;
    background-color: #f0f0f0;
    padding: 10px;
    position: fixed;
    top: 5px;
    right: 5px;
}

/* CSS Tooltips: http://www.communitymx.com/content/article.cfm?cid=4E2C0 */
div.code span.trg {
    font: small-caption;
    vertical-align: bottom;
    color: green;
    position: relative;
    cursor: crosshair;
}
div.code span.trg-info {
    display: none;
    z-index: 25;
    cursor: text;
    min-width: 25em;
    white-space: nowrap;
}
div.code span.trg:hover span.trg-info {
    z-index: 26;
    position: absolute;
    top: 1.0em;
    left: 0.0em;
    display: block;
    padding: 4px;
    background-color: #f0f0f0;
    border: 1px solid #e0e0e0;
}
span.trg-evalerror  { width: 50em; color: red !important; }
span.trg-error      { width: 50em; color: red !important; }
span.trg-notatrg    { color: blue !important; }
span.trg-noresults  { color: orange !important; }
td.trg-evallog {
    color: grey;
    border-left: 1px solid grey;
    padding-left: 5px;
}

/* token highlighting and debugging info */
div.code span:hover {
    background-color: #e0e0e0;
}

div.code span.udl-region:hover {
    background-color: #f0f0f0;
}

/* language-neutral syntax coloring */
div.code {
    font-family: "Courier New", Courier, monospace;
    font-size: small;
}

div.code .comments    { color: grey; }
div.code .keywords    { font-weight: bold; }
div.code .identifiers { color: black; }
div.code .strings     { color: blue; }
div.code .classes,
div.code .functions   { color: green; }
div.code .stderr      { background-color: red; }
div.code .stdout      { background-color: blue; }
div.code .tags        { color: red; }

</style>

<div id="infobox"></div>
''')

        #XXX escape lang name for CSS class
        html.write('<div class="code %s">\n' % self.lang.lower())

        curr_udl_region = None
        ch = last_ch = None
        for token in self.accessor.gen_tokens():
            css_classes = self.style_names_from_style_num(token["style"])
            if css_classes and css_classes[0].startswith("SCE_UDL_"):
                udl_region = css_classes[0].split('_')[2]
                if udl_region == curr_udl_region:
                    pass
                else:
                    if curr_udl_region:
                        html.write('\n</span>\n')
                    html.write('\n<span class="udl-region">\n')
                    curr_udl_region = udl_region
            html.write('<span class="%s" onmouseover="show_class(event.target);">'
                       % ' '.join(css_classes))
            for i, ch in enumerate(token["text"]):
                if ch == "\n" and last_ch == "\r":
                    # Treat '\r\n' as one char.
                    continue
                if do_trg:
                    try:
                        trg = self.trg_from_pos(token["start_index"] + i)
                    except CodeIntelError, ex:
                        html.write(self._html_from_trg_error(ex))
                    else:
                        if trg is not None:
                            html.write(self._html_from_trg(trg,
                                                           do_eval=do_eval))
                #XXX Need to do tab expansion.
                html.write(_htmlescape(ch, quote=True, whitespace=True))
                last_ch = ch
            html.write('</span>')
        if curr_udl_region:
            html.write('\n</span>\n')
        html.write('</div>\n')

        if include_html:
            html.write('''
</body>
</html>
''')

        return html.getvalue()

    def _html_from_trg_error(self, ex):
        marker = "&curren;"
        classes = ["trg"]
        classes.append("trg-error")
        result = _htmlescape(traceback.format_exc(), whitespace=True)
        info_html = '<div>%s</div' % result
        return '<span class="%s">%s<span class="trg-info">%s</span></span>' \
               % (' '.join(classes), marker, info_html)

    def _html_from_trg(self, trg, do_eval=False):
        marker = "&curren;"
        classes = ["trg"]
        
        try:
            eval_log_stream = StringIO()
            hdlr = logging.StreamHandler(eval_log_stream)
            infoFmt = "%(name)s: %(message)s"
            fmtr = logging.Formatter("%(name)s: %(levelname)s: %(message)s")
            hdlr.setFormatter(fmtr)
            codeintel_logger = logging.getLogger("codeintel")
            codeintel_logger.addHandler(hdlr)
            if do_eval:
                ctlr = LogEvalController(codeintel_logger)
                try:
                    if trg.form == TRG_FORM_CPLN:
                        cplns = self.cplns_from_trg(trg, ctlr=ctlr)
                    else:
                        calltips = self.calltips_from_trg(trg, ctlr=ctlr)
                finally:
                    codeintel_logger.removeHandler(hdlr)
        except NotATriggerError:
            classes.append("trg-notatrg")
            result = "(not a trigger point, false alarm by trg_from_pos())"
        except (EvalError, NotImplementedError,
                #XXX Eventually citdl evaluation shouldn't use
                #    codeintel2.CodeIntelError.
                CodeIntelError), ex:
            classes.append("trg-evalerror")
            result = _htmlescape(traceback.format_exc(), whitespace=True)
        else:
            if trg.form == TRG_FORM_CPLN:
                if not do_eval:
                    classes.append("trg-noresults")
                    result = "(eval skipped)"
                elif cplns:
                    result = "<br />".join(["<em>%s</em> %s" % c
                                            for c in cplns])
                else:
                    classes.append("trg-noresults")
                    result = "(no completions)"
            else:
                if not do_eval:
                    classes.append("trg-noresults")
                    result = "(eval skipped)"
                elif calltips:
                    result = _htmlescape(calltips[0], whitespace=True)
                else:
                    classes.append("trg-noresults")
                    result = "(no calltip)"

        eval_log = _htmlescape(str(trg), whitespace=True)
        eval_log += "<hr />"
        eval_log += _htmlescape(eval_log_stream.getvalue(), whitespace=True)
        info_html = ('<table><tr valign="top">'
                     '<td>%s</td>'
                     '<td class="trg-evallog">%s</td>'
                     '</tr></table>'
                     % (result, eval_log))
        return '<span class="%s">%s<span class="trg-info">%s</span></span>' \
               % (' '.join(classes), marker, info_html)


    #---- Scintilla style helpers.
    def style_names_from_style_num(self, style_num):
        #XXX Would like to have python-foo instead of p_foo or SCE_P_FOO, but
        #    that requires a more comprehensive solution for all langs and
        #    multi-langs.
        style_names = []

        # Get the constant name from ScintillaConstants.
        if self.lang not in self._style_name_from_style_num_from_lang:
            name_from_num \
                = self._style_name_from_style_num_from_lang[self.lang] = {}
            sce_prefixes = self.sce_prefixes
            if sce_prefixes is None:
                # Try and guess the prefix then.
                log.warn("Guessing sce_prefix as 'SCE_%s_' - if that's not "
                         "correct then define 'sce_prefixes' on your buffer"
                         "class", self.lang.upper())
                sce_prefixes = ["SCE_%s_" % (self.lang.upper())]
            for attr in dir(ScintillaConstants):
                for sce_prefix in sce_prefixes:
                    if attr.startswith(sce_prefix):
                        name_from_num[getattr(ScintillaConstants, attr)] = attr
        else:
            name_from_num \
                = self._style_name_from_style_num_from_lang[self.lang]
        const_name = self._style_name_from_style_num_from_lang[self.lang].get(style_num, "Unknown style")
        style_names.append("%d - %s" % (style_num, const_name))
        
        # Get a style group from styles.py.
        if self.lang in styles.StateMap:
            for style_group, const_names in styles.StateMap[self.lang].items():
                if const_name in const_names:
                    style_names.append(style_group)
                    break
        else:
            log.warn("lang '%s' not in styles.StateMap: won't have "
                     "common style groups in HTML output" % self.lang)
        
        return style_names

    __string_styles = None
    def string_styles(self):
        if self.__string_styles is None:
            state_map = styles.StateMap[self.lang]
            self.__string_styles = [
                getattr(ScintillaConstants, style_name)
                for style_class in ("strings", "stringeol")
                for style_name in state_map.get(style_class, [])
            ]
        return self.__string_styles

    __comment_styles = None
    def comment_styles(self):
        if self.__comment_styles is None:
            state_map = styles.StateMap[self.lang]
            self.__comment_styles = [
                getattr(ScintillaConstants, style_name)
                for style_class in ("comments", "here documents",
                                    "data sections")
                for style_name in state_map.get(style_class, [])
            ]
        return self.__comment_styles

    __number_styles = None
    def number_styles(self):
        if self.__number_styles is None:
            state_map = styles.StateMap[self.lang]
            self.__number_styles = [
                getattr(ScintillaConstants, style_name)
                for style_class in ("numbers",)
                for style_name in state_map.get(style_class, [])
            ]
        return self.__number_styles


class ImplicitBuffer(Buffer):
    """A buffer for a language that is not explicitly registered as
    a codeintel language.
    """
    def __init__(self, lang, mgr, accessor, env=None, path=None,
                 encoding=None):
        self.lang = lang
        Buffer.__init__(self, mgr, accessor, env=env, path=path,
                        encoding=encoding)

    #TODO: Is there a need/use in possibly determining scintilla styles
    #      for this language?
    def string_styles(self):
        return []
    def comment_styles(self):
        return []
    def number_styles(self):
        return []



#---- internal support stuff

# Recipe: htmlescape (1.0+) in C:\trentm\tm\recipes\cookbook
#         + whitespace option
def _htmlescape(s, quote=False, whitespace=False):
    """Replace special characters '&', '<' and '>' by SGML entities.
    
    Also optionally replace quotes and whitespace with entities and <br/>
    as appropriate.
    """
    s = s.replace("&", "&amp;") # Must be done first!
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    if whitespace:
        s = s.replace(' ', "&nbsp;")
        #XXX Adding that '\n' might be controversial.
        s = re.sub(r"(\r\n|\r|\n)", "<br />\n", s)
    return s



#---- self-test

def _doctest():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _doctest()
