# Copyright (c) 2000-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

# these classes implement support for the dbgp uri protocol via
# the standard mozilla method of adding new network uri protocols

import urllib
import urlparse
import re
import xpcom
from xpcom import components, ServerException, nsError

from StringIO import StringIO
import logging
import koUnicodeEncoding, types

_scheme = "dbgp"
log = logging.getLogger("dbgp.ProtocolHandler")
#log.setLevel(logging.DEBUG)

class koSimpleStringInputStream:
    _com_interfaces_ = [components.interfaces.nsIInputStream]

    nonBlocking=0

    def __init__(self, data):
        # find out what the proper encoding is for this buffer
        encodingServices = components.classes['@activestate.com/koEncodingServices;1'].\
                 getService(components.interfaces.koIEncodingServices)
        prefs = components.classes["@activestate.com/koPrefService;1"].\
                            getService(components.interfaces.koIPrefService).prefs
        if type(data)==types.UnicodeType:
            data = data.encode('UTF-8')
        encoding_name = prefs.getStringPref('encodingDefault')
        encoding = encodingServices.get_encoding_info(encoding_name).python_encoding_name
        unicodebuffer, encoding, bom =\
            koUnicodeEncoding.autoDetectEncoding(data, 1, 1, 1, defaultEncoding=encoding)
        # we encode to the encoding now, koDocument will handle things
        # from there
        self.data=StringIO(unicodebuffer.encode(encoding))

    def close( self ):
        pass
    def available( self ):
        return self.data.len-self.data.pos

    def readStr( self, amount):
        return self.data.read(amount)

    read=readStr


class koSimpleStringChannel:
    """Note that this class only implements what we need in the short-term.
    Weird stuff like asynch can wait. """
    _com_interfaces_ = [components.interfaces.nsIChannel]

    def __init__(self, url, data):
        self.uri=url
        self.name=url
        self.originalURI=url
        self.data=data

    def open(self):
        return koSimpleStringInputStream(self.data)

    def asyncOpen(self):
        return None

class koDBGPURI:
    _com_interfaces_ = [components.interfaces.koIDBGPURI]
    _reg_clsid_ = "{4A207FA1-A178-48B2-B10D-795C0D863BC3}"
    _reg_contractid_ = "@activestate.com/koDBGPURI;1"

    scheme=_scheme
    
    def init(self, uri):
        if uri.startswith('dbgp:'):
            self.spec= uri
            self.path = uri.split(':',1)[1]
        else:
            self.path = uri
            self.spec= "%s:%s" % (_scheme, uri)
        return 

    def newURI(self, uri):
        "Create a new one based on this one."
        #Unobfuscation: generates dbgp:uri
        newobj = self.__class__()
        if uri.startswith('dbgp:'):
            newobj.init(uri)
        else:
            newobj.init("%s:%s" % (_scheme, uri))
        return newobj

    def getBaseURI(self, uri):
        return uri

class koDBGPProtocolHandler:
    _com_interfaces_ = [components.interfaces.koIDBGPProtocolHandler]
    _reg_clsid_ = "{43441B03-528A-44B8-9D30-957E8BAAA65F}"
    _reg_contractid_ = "@mozilla.org/network/protocol;1?name=%s"%_scheme

    scheme=_scheme

    defaultPort=9000
    instantiated=0
    counter=0
    protocolFlags = 0
    _DBGP_URI_RE = re.compile('dbgp://([-0-9a-fA-F]{36})/(.*)')
    _DBGP_starts_with_scheme = re.compile('(\w+://)')

    def __init__(self):
        assert koDBGPProtocolHandler.instantiated==0, "Should be singleton"
        koDBGPProtocolHandler.instantiated=1

    def newURI(self, newuri, aOriginCharset, base):
        if base is None:
            base = koDBGPURI()
            base.init(newuri)
            return base
        else:
            return base.newURI(newuri)

    def newChannel(self, url):
        # get the current debugger session
        # XXX this may be flaky getting the right uri to the right
        # session
        m = self._DBGP_URI_RE.match(url.spec)
        if m:
            uuid = m.group(1)
            manager = components.classes["@activestate.com/koDBGPManager;1"].\
                      getService(components.interfaces.koIDBGPManager)
            app = manager.getApplicationFromUUID(uuid)
            # See bug 86579: The dbgp scheme is overloaded -- on one hand it's
            # used to indicate that Komodo can't find a remote file,
            # and wants the debugger engine to provide its source.
            # On the other, it's used to identify fabricated buffers internal
            # to the debugger, usually the contents of eval'ed strings.
            # No problem there, but the first kind of URI has to have the
            # "dbgp:///" stripped off, while the second kind needs to have it.
            #
            # In retrospect, we should have created two separate schemes,
            # like "dbgpr" for remote files, "dbgpe" for eval-buffers.
            if app is None:
                # Use the url.spec
                # Remote debugging URIs won't come in with a UUID
                path = url.spec
            else:
                path = m.group(2)
                # Deal with Virtual (eval'd) file paths, which won't be using a
                # uri scheme, example: 'dbgp:///(eval 1)' - bug 86579.
                if not self._DBGP_starts_with_scheme.match(path):
                    path = 'dbgp://' + path
        else:
            path = url.spec
        # if the spec contains a file spec, then we want to return that to
        # the debug engine instead.  We may want to eventually expand this to
        # other specs as well, but for now file is enough for remote debugging
        return koSimpleStringChannel(url, app.currentSession.getSourceCode(path, 0, 0))

