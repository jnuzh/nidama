# Copyright (c) 2000-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

"""utility functions to make using nsIDirectoryService a little easier.
"""

import os
from xpcom import components, COMException
import ConfigParser

nsIDirectoryServiceContractID = "@mozilla.org/file/directory_service;1";
nsIProperties = components.interfaces.nsIProperties;
directoryService =  components.classes[nsIDirectoryServiceContractID].getService(nsIProperties);

def getFiles(key):
    """getFiles
    
    gets a list of nsIFile objects from the directory service.
    """
    enum = directoryService.get(key, components.interfaces.nsISimpleEnumerator);
    files = []
    while enum.hasMoreElements():
        files.append(enum.getNext().QueryInterface(components.interfaces.nsIFile))
    return files

def getFile(key):
    """getFiles
    
    gets a nsIFile object from the directory service.
    """
    return directoryService.get(key, components.interfaces.nsIFile);

_gExtensionDirectoriesCache = None
def getExtensionDirectories():
    """Get extension directories.
    
    @returns A list of full paths to all installed and enabled extension
        directories.
    """
    global _gExtensionDirectoriesCache
    if _gExtensionDirectoriesCache is None:
        dirs = [d.path for d in getFiles("XREExtDL")]
        # Allow a custom directory service to provide additional extension
        # directories using the special "PyxpcomExtDirList" key.
        try:
            dirs += [d.path for d in getFiles("PyxpcomExtDirList")]
        except COMException:
            pass
        if not dirs:
            # Okay, that didn't work; perhaps we're just in early startup.
            # _Hopefully_ this means XREExtDL isn't valid yet; pass an empty
            # list back, but don't update the cache since we might have better
            # luck next time.
            return []
        # Make them unique - ordering does not matter.
        _gExtensionDirectoriesCache = list(set(dirs))
    return _gExtensionDirectoriesCache

_gPylibDirectoriesCache = None
def getPylibDirectories():
    """Get pylib directories.
    
    @returns A list of full paths to all "pylib" directories in all
        installed (and enabled?) extensions.
    """
    global _gPylibDirectoriesCache
    if _gPylibDirectoriesCache is None:
        dirs = set()
        for dir in getExtensionDirectories():
            d = os.path.join(dir, "pylib")
            if os.path.exists(d):
                dirs.add(d)
        _gPylibDirectoriesCache = list(dirs)
    return _gPylibDirectoriesCache
