#!python
# Copyright (c) 2000-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

"""Language package for PHP"""

import os
import re
import logging

import process
import koprocessutils

from koLanguageServiceBase import *
from koUDLLanguageBase import KoUDLLanguage
from xpcom import components, ServerException
import xpcom.server

sci_constants = components.interfaces.ISciMoz



def registerLanguage(registry):
    registry.registerLanguage(KoPHPLanguage())
    

class KoPHPLanguage(KoUDLLanguage, KoLanguageBaseDedentMixin):
    name = "PHP"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" \
                       % (name)
    _reg_clsid_ = "{F472CC39-0902-4d92-8A5B-7DD0F612F119}"
    _reg_categories_ = [("komodo-language", name)]
    _com_interfaces_ = [components.interfaces.koILanguage,
                        components.interfaces.nsIObserver]

    lexresLangName = "PHP"
    lang_from_udl_family = {'CSL': 'JavaScript', 'M': 'HTML', 'CSS': 'CSS',
                            'SSL': 'PHP'}

    accessKey = 'h'
    primary = 1
    shebangPatterns = [
        re.compile(ur'\A#!.*php.*$', re.IGNORECASE | re.MULTILINE),
    ]
    namedBlockRE = r'^(.*?function\s+[&]*?\s*[\w_]*)|(^.*?(?<=\s)(?:class|interface)\s+[\w_]*)'
    namedBlockDescription = 'PHP functions and classes'
    defaultExtension = ".php"
    variableIndicators = '$'
    downloadURL = 'http://php.net/'
    commentDelimiterInfo = {
        "line": [ "//", "#" ],
        "block": [ ("/*", "*/") ],
        "markup": "*",
    }
    _dedenting_statements = [u'throw', u'return', u'break', u'continue']
    supportsSmartIndent = "brace"
    sample = """<?php
class foo {
    // a comment
    var $a;
    var $b;
    function display() {
        echo "This is class foo";
        echo "a = ".$this->a."";
        echo "b = {$this->b}";
    }
    function mul() {
        return $this->a*$this->b;
    }
};

$foo1 = new foo;
$foo1->a = 2;
$foo1->b = 5;
$foo1->display();
echo $foo1->mul()."";
?>"""    
        
    def __init__(self):
        KoUDLLanguage.__init__(self)
        KoLanguageBaseDedentMixin.__init__(self)
        
        # get the comment prefs and set that, then observe for pref changes
        self.__prefs = components.classes["@activestate.com/koPrefService;1"].\
            getService(components.interfaces.koIPrefService).prefs
        self.commentDelimiterInfo['line'] = self.__prefs.getStringPref("phpCommentStyle").split(",")

        self._observer = xpcom.server.WrapObject(self,
                                      components.interfaces.nsIObserver)
        self.__prefs.prefObserverService.addObserver(self._observer, "phpCommentStyle", 0)
        self._setupIndentCheckSoftChar()
        self._fastCharData = \
            FastCharData(trigger_char=";",
                         style_list=(sci_constants.SCE_UDL_SSL_OPERATOR,),
                         skippable_chars_by_style={ sci_constants.SCE_UDL_SSL_OPERATOR : "])",},
                         
                         for_check=True)
    
    def observe(self, subject, topic, data):
        if topic == "phpCommentStyle":
            self.commentDelimiterInfo['line'] = self.__prefs.getStringPref("phpCommentStyle").split(",")
            self._commenter = None
	else:
	    KoUDLLanguage.observe(self, subject, topic, data)

    def get_interpreter(self):
        if self._interpreter is None:
            self._interpreter = components.classes["@activestate.com/koAppInfoEx?app=PHP;1"].getService()
        return self._interpreter

