# Komodo Luddite language service.

import logging
from koUDLLanguageBase import KoUDLLanguage


log = logging.getLogger("koLudditeLanguage")
#log.setLevel(logging.DEBUG)


def registerLanguage(registry):
    log.debug("Registering language Luddite")
    registry.registerLanguage(KoLudditeLanguage())


class KoLudditeLanguage(KoUDLLanguage):
    name = "Luddite"
    lexresLangName = "Luddite"
    _reg_desc_ = "%s Language" % name
    _reg_contractid_ = "@activestate.com/koLanguage?language=%s;1" % name
    _reg_clsid_ = "{9B7AA7E1-15DF-443F-9B4C-014047222FBA}"
    _reg_categories_ = [("komodo-language", name)]
    defaultExtension = '.udl'

    lang_from_udl_family = {'CSL': None, 'M': None}

