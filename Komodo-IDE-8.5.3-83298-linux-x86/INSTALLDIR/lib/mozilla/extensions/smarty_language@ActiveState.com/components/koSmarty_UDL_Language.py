# Komodo Smarty language service.

import logging
from koXMLLanguageBase import koHTMLLanguageBase


log = logging.getLogger("koSmartyLanguage")
#log.setLevel(logging.DEBUG)


def registerLanguage(registry):
    log.debug("Registering language Smarty")
    registry.registerLanguage(KoSmartyLanguage())


class KoSmartyLanguage(koHTMLLanguageBase):
    name = "Smarty"
    lexresLangName = "Smarty"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" % name
    _reg_clsid_ = "{2A2886F8-3D8D-4959-9FE1-32BD7FEA8294}"
    _reg_categories_ = [("komodo-language", name)]
    defaultExtension = '.tpl'

    lang_from_udl_family = {'CSL': 'JavaScript', 'TPL': 'Smarty', 'M': 'HTML', 'CSS': 'CSS', 'SSL': 'PHP'}

