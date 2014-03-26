#!python
# Copyright (c) 2000-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

from xpcom import components
from koLanguageServiceBase import *
from koXMLLanguageBase import koXMLLanguageBase, KoGenericXMLLinter

import os
import logging

log = logging.getLogger("koXSLTLanguage")

def registerLanguage(registery):
    registery.registerLanguage(koXSLTLanguage())
    
class koXSLTLanguage(koXMLLanguageBase):
    name = "XSLT"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" \
                       % (name)
    _reg_clsid_ = "{7F76A3CE-7FE1-4363-99EB-4AAAFA79BC88}"
    _reg_categories_ = [("komodo-language", name)]

    lexresLangName = name
    lang_from_udl_family = {'M': 'XML'}

    accessKey = 's'
    primary = 1
    defaultExtension = ".xsl"

    systemIdList = ["http://www.w3.org/1999/XSL/Transform"]
    namespaces = ["http://www.w3.org/1999/XSL/Transform"]
    
    namedBlockRE = r'(\<xsl:template.*?\>)'
    namedBlockDescription = 'XSL Templates'

    sample = """<?xml version="1.0"?> 

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="xml" indent="yes"/>

<!-- Syntax Coloring:
    Komodo detects keywords and applies syntax coloring.  In the code
    below, note how "template" is a different color from "match",
    which is a different color from ""Class"". -->

<xsl:template match="Class">
    <html>
            <xsl:apply-templates select="Order"/>
    </html>
</xsl:template>

"""


class KoXSLTCompileLinter(KoGenericXMLLinter):
    _reg_desc_ = "Komodo XSLT Compile Linter"
    _reg_clsid_ = "{390b2ce2-9df8-41a7-8e35-d2a4d76618d6}"
    _reg_contractid_ = "@activestate.com/koLinter?language=XSLT;1"
    _com_interfaces_ = [components.interfaces.koILinter]
    _reg_categories_ = [
         ("category-komodo-linter", 'XSLT'),
         ]
