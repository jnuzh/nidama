"""Language package for HTML"""

from xpcom import components, ServerException

from koLanguageServiceBase import *
from koXMLLanguageBase import koHTMLLanguageBase

def registerLanguage(registery):
    registery.registerLanguage(KoHTMLLanguage())
    registery.registerLanguage(KoHTML5Language())

class KoHTMLLanguage(koHTMLLanguageBase):
    name = "HTML"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" \
                       % (name)
    _reg_clsid_ = "{7FDF82EB-7E8E-40f4-BD39-563FD2B7E94A}"
    _reg_categories_ = [("komodo-language", name)]

    lexresLangName = "HTML"
    lang_from_udl_family = {'CSL': 'JavaScript', 'M': 'HTML', 'CSS': 'CSS'}

    searchURL = "http://www.google.com/search?q=site%3Ahttp%3A%2F%2Fwww.w3schools.com%2Ftags+%W"

    accessKey = 'm'
    defaultExtension = ".html" # XXX how do we deal w/ .htm vs. html?
    #XXX Boy it would be nice to have this be 6 so we could get green
    #    squigglies for linting.
    _lineup_chars = '' # don't indent ()'s and the like in HTML!
    _lineup_open_chars = "" # don't indent ()'s and the like in HTML!

    # The set of elements which do not have a close tag. See
    # http://www.w3.org/TR/html401/index/elements.html
    # (with some sensible additions from HTML5 where tags are not standardized)
    _void_elements = set(("area", "base", "basefont", "br", "col", "embed",
                          "frame", "hr", "img", "input", "isindex", "keygen",
                          "link", "meta", "param", "wbr"))

    sample = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en" dir="ltr">
  <head lang="en" xml:lang="en" dir="ltr" profile="profile">
    <!-- base href="http://www.w3.org/People/mimasa/test/xhtml/media-types/test" /-->
    <meta http-equiv="Content-Language" content="en" />
    <title lang="en" xml:lang="en" dir="ltr">Sample XHTML 1.0 document</title>
    <link rev="made" href="mailto:mimasa@w3.org" />
    <style type="text/css" media="screen">
      .title { color: #FF3333 }
    </style>
    <meta scheme="Dublin Core" name="DC.CREATOR" content="ISHIKAWA, Masayasu" />
    <style type="text/css" media="aural">
      .title { volume: loud }
    </style>
    <link id="help.link" class="help.link" title="For more information, see HTML 4 Specification." lang="en" xml:lang="en" dir="ltr" charset="ISO-8859-1" href="http://www.w3.org/TR/html4" rel="Help" />
  </head>
  <body id="body" class="body" title="body" lang="en" xml:lang="en" dir="ltr">

    <h1 id="title" class="title" title="document title" lang="en"
    xml:lang="en" dir="ltr" style="color: maroon">Sample XHTML 1.0 document</h1>

    <h2 id="ToC">Contents</h2>

    <ul>
      <li><a href="#grouping.heading">Grouping elements: <code>div</code> and <code>span</code></a></li>
      <li><a href="#bidi.heading">Bidrectionality</a>
        <ul>
	  <li><a href="#ltr.heading">Base directionality: left to right</a></li>
	  <li><a href="#rtl.heading">Base directionality: right to left</a></li>
	  <li><a href="#bdo.heading">Bidirectionality override: <code>bdo</code></a></li>
	</ul>
      </li>

"""


class KoHTML5Language(KoHTMLLanguage):
    name = "HTML5"
    accessKey = '5'
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" \
                       % (name)
    _reg_clsid_ = "{f662cc4c-4f86-194e-83a8-35f2f0097121}"
    _reg_categories_ = [("komodo-language", name)]
    
    lang_from_udl_family = {'CSL': 'JavaScript', 'M': 'HTML5', 'CSS': 'CSS'}

    # The set of elements which do not have a close tag. See
    # http://www.whatwg.org/specs/web-apps/current-work/multipage/syntax.html#void-elements
    _void_elements = set(("area", "base", "br", "col", "command", "embed", "hr",
                          "img", "input", "keygen", "link", "meta", "param",
                          "source", "track", "wbr"))

    sample = """<!DOCTYPE html>
<html lang-en>
  <head>
    <meta charset=UTF-8 />
    <title>Sample HTML 5 document</title>
    <style>
      .title { color: #FF3333 }
    </style>
  </head>
  <body id="body" class="body">
    <header>
      <h1>Sample HTML 5 document</h1>
      <p>This is a <cite>HTML 5 document</cite></p>
    </header>
  </body>
</html>
"""
