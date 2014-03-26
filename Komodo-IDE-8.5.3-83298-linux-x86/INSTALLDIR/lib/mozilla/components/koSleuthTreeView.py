#!python
# Copyright (c) 2000-2008 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

# The implementation of the Komodo Find and Replace service

import logging
import os
#from os.path import join, isabs, expanduser, normpath
#import pprint
import re
# import string
import sys
import types

from xpcom import components
from koTreeView import TreeView



#---- globals

log = logging.getLogger("koSleuthTreeView")
#log.setLevel(logging.DEBUG)



#---- Sleuth backend

class KoSleuthResultsView(TreeView):
    _com_interfaces_ = [components.interfaces.koISleuthResultsView,
                        components.interfaces.nsITreeView]
    _reg_desc_  = "Sleuth Results View"
    _reg_clsid_ = "{29da8a82-849f-4117-a260-bcf4bb209a74}"
    _reg_contractid_ = "@activestate.com/koSleuthResultsView;1"

    _status_icons = {
        "P" : "chrome://famfamfamsilk/skin/icons/accept.png",
        "E" : "chrome://famfamfamsilk/skin/icons/error.png",
        "F" : "chrome://famfamfamsilk/skin/icons/exclamation.png"
        }
    _unknown_status_icon = "chrome://famfamfamsilk/skin/icons/information.png"

    def __init__(self):
        TreeView.__init__(self, debug=0)
        #global lastErrorSvc
        #lastErrorSvc = components.classes["@activestate.com/koLastErrorService;1"]\
        #               .getService(components.interfaces.koILastErrorService)
        self._data = []
        self._tree = None
        self._updated_point = 0;
        
    def Clear(self):
        # Same as find results
        length = len(self._data)
        self._data = []
        self._tree.beginUpdateBatch()
        self._tree.rowCountChanged(0, -length)
        self._tree.invalidate()
        self._tree.endUpdateBatch()
    
    def AddDetails(self, description, outcome, details):
        """
        See code in koSleuth.py for structure of data
        It's an array of triples, but second and third values
        could be None or an array
        """
        datum = {
            "projectUnitTestsResults-filename": description,
            "projectUnitTestsResults-linenum": outcome,
            "projectUnitTestsResults-context": details,
            }
        self._data.append(datum)
            
    def UpdateTree(self):
        new_len = len(self._data)
        self._tree.beginUpdateBatch()
        self._tree.rowCountChanged(self._updated_point, new_len - self._updated_point)
        self._tree.invalidate()  #XXX invalidating too much here?
        self._tree.endUpdateBatch()
        self._updated_point = new_len
    
    # Implement everything else we need. This is similar to the
    # find-results view.

    def get_rowCount(self):
        return len(self._data)

    def getCellText(self, row, column):
        col = column.id
        try:
            datum = self._data[row][col]
        except IndexError:
            # Silence this, it is too annoying.
            # c.f. http://bugs.activestate.com/show_bug.cgi?id=27487
            #log.error("no %sth find result" % row)
            return ""
        except KeyError:
            log.error("unknown find result column id: '%s'" % col)
            return ""
        if type(datum) not in (types.StringType, types.UnicodeType):
            datum = str(datum)
        return datum

    def getImageSrc(self, row, column):
        if column.id != "projectUnitTestsResults-filename":
            return ""
        try:
            datum = self._data[row]["projectUnitTestsResults-linenum"]
            url = self._status_icons.get(datum, self._unknown_status_icon)
            #log.debug("getImageSrc: datum = %s, url = %s", datum, url)
            return url
        except IndexError:
            # Silence this, it is too annoying.
            # c.f. http://bugs.activestate.com/show_bug.cgi?id=27487
            #log.error("no %sth find result" % row)
            return ""
