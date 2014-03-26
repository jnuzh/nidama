#!/usr/bin/env python
# Copyright (c) 2000-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

import sys, os
import tempfile
from xpcom import components, ServerException, nsError


#---- internal support functions

def _mkdir(newdir):
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)


def _copy(src, dst):
    """works the way a good copy should :)
        - no source, raise an exception
        - destination directory, make a file in that dir named after src
        - source directory, recursively copy the directory to the destination
        - filename wildcarding allowed
    """
    import string, glob, shutil

    # determine if filename wildcarding is being used
    # (only raise error if non-wildcarded source file does not exist)
    if string.find(src, '*') != -1 or \
       string.find(src, '?') != -1 or \
       string.find(src, '[') != -1:
        usingWildcards = 1
        srcFiles = glob.glob(src)
    else:
        usingWildcards = 0
        srcFiles = [src]

    for srcFile in srcFiles:
        if os.path.isfile(srcFile):
            if usingWildcards:
                srcFileHead, srcFileTail = os.path.split(srcFile)
                srcHead, srcTail = os.path.split(src)
                dstHead, dstTail = os.path.split(dst)
                if dstTail == srcTail:
                    dstFile = os.path.join(dstHead, srcFileTail)
                else:
                    dstFile = os.path.join(dst, srcFileTail)
            else:
                dstFile = dst
            dstFileHead, dstFileTail = os.path.split(dstFile)
            if dstFileHead and not os.path.isdir(dstFileHead):
                _mkdir(dstFileHead)
            #print "copy %s to %s" % (repr(srcFile), repr(dstFile))
            if os.path.isfile(dstFile):
                # make sure 'dstFile' is writeable
                os.chmod(dstFile, 0755)
            shutil.copy(srcFile, dstFile)
            # make the new 'dstFile' writeable
            os.chmod(dstFile, 0755)
        elif os.path.isdir(srcFile):
            srcFiles = os.listdir(srcFile)
            if not os.path.exists(dst):
                _mkdir(dst)
            for f in srcFiles:
                s = os.path.join(srcFile, f)
                d = os.path.join(dst, f)
                try:
                    _copy(s, d)
                except (IOError, os.error), why:
                    raise OSError("Can't copy %s to %s: %s"\
                          % (repr(s), repr(d), str(why)))
        elif not usingWildcards:
            raise OSError("Source file %s does not exist" % repr(srcFile))


#---- components

class KoTutorialService:
    """Virtual application info base class."""
    def __init__(self, language, projectCacheDir, projectFileName):
        self.language = language
        self.projectCacheDir = projectCacheDir
        self.projectFileName = projectFileName
    
    def GetWorkingDir(self):
        # base tutorial dir should be:
        #  Linux: ~
        #  Windows: My Documents
        if sys.platform.startswith("win"):
            from win32com.shell import shellcon, shell
            base = shell.SHGetFolderPath(0, shellcon.CSIDL_PERSONAL,
                                         0, 0)
        else:
            base = os.environ.get("HOME")
        # fallback to a temp directory
        if not base or not os.path.isdir(base):
            base = os.path.dirname(tempfile.mktemp())
        # just try <base>/<lang>_tutorial first
        potential = os.path.join(base, self.language.lower()+"_tutorial")
        if not os.path.exists(potential):
            return potential
        # otherwise try <base>/<lang>_tutorial<index>
        base = potential
        for i in range(2, 1000):  # 1000 == ridiculously high sentinel
            potential = base+str(i)
            if not os.path.exists(potential):
                return potential
        # otherwise fallback to an ugly random tempfile name
        return tempfile.mktemp()

    def PrepareWorkingDir(self, workingDir):
        """Create the working directory and copy over the files.
        Make the files writeable. Abort if the directory already exists and
        is non-empty.
        """
        # create the working directory
        if os.path.exists(workingDir) and not os.path.isdir(workingDir):
            return "Error: '%s' is an already existing file. You must "\
                   "select a new or empty directory."\
                   % workingDir
        elif os.path.exists(workingDir) and os.listdir(workingDir):
            return "Error: '%s' is a non-empty directory. You must "\
                   "select a new or empty directory."\
                   % workingDir
        elif os.path.exists(workingDir):
            # an empty existing directory
            pass
        else:
            # The directory does not yet exist.
            _mkdir(workingDir)

        # copy over the files (making them writeable)
        _copy(os.path.join(self.projectCacheDir, "*"), workingDir) 
        return None
        


class KoPerlTutorialService(KoTutorialService):
    """Perl Tutorial support"""
    _com_interfaces_ = [components.interfaces.koITutorialService]
    _reg_clsid_ = "549e16aa-e885-4965-aa46-7ff648584807"
    _reg_contractid_ = "@activestate.com/koPerlTutorialService;1"
    _reg_desc_ = "Perl Tutorial Service"

    def __init__(self):
        koDirs = components.classes["@activestate.com/koDirs;1"]\
                 .getService(components.interfaces.koIDirs)
        projectCacheDir = os.path.join(koDirs.supportDir, "samples",
                                       "perl_tutorials")
        KoTutorialService.__init__(self, "Perl", projectCacheDir,
                                   "perl_tutorial.komodoproject")


class KoXSLTTutorialService(KoTutorialService):
    """XSLT Tutorial support"""
    _com_interfaces_ = [components.interfaces.koITutorialService]
    _reg_clsid_ = "27a32a55-53fe-4ff6-b5fb-fb54f8655633"
    _reg_contractid_ = "@activestate.com/koXSLTTutorialService;1"
    _reg_desc_ = "XSLT Tutorial Service"

    def __init__(self):
        koDirs = components.classes["@activestate.com/koDirs;1"]\
                 .getService(components.interfaces.koIDirs)
        projectCacheDir = os.path.join(koDirs.supportDir, "samples",
                                       "xslt_tutorials")
        KoTutorialService.__init__(self, "XSLT", projectCacheDir,
                                   "xslt_tutorial.komodoproject")


class KoPythonTutorialService(KoTutorialService):
    """Python Tutorial support"""
    _com_interfaces_ = [components.interfaces.koITutorialService]
    _reg_clsid_ = "1fa3edd4-c533-4edc-b681-7e460c78faf1"
    _reg_contractid_ = "@activestate.com/koPythonTutorialService;1"
    _reg_desc_ = "Python Tutorial Service"

    def __init__(self):
        koDirs = components.classes["@activestate.com/koDirs;1"]\
                 .getService(components.interfaces.koIDirs)
        projectCacheDir = os.path.join(koDirs.supportDir, "samples",
                                       "python_tutorials")
        KoTutorialService.__init__(self, "Python", projectCacheDir,
                                   "python_tutorial.komodoproject")


class KoPHPTutorialService(KoTutorialService):
    """PHP Tutorial support"""
    _com_interfaces_ = [components.interfaces.koITutorialService]
    _reg_clsid_ = "8b0adb7b-ed4a-4715-9496-29b8057641bf"
    _reg_contractid_ = "@activestate.com/koPHPTutorialService;1"
    _reg_desc_ = "PHP Tutorial Service"

    def __init__(self):
        koDirs = components.classes["@activestate.com/koDirs;1"]\
                 .getService(components.interfaces.koIDirs)
        projectCacheDir = os.path.join(koDirs.supportDir, "samples",
                                       "php_tutorials")
        KoTutorialService.__init__(self, "PHP", projectCacheDir,
                                   "php_tutorial.komodoproject")


class KoRunCommandTutorialService(KoTutorialService):
    """Run Command Tutorial support"""
    _com_interfaces_ = [components.interfaces.koITutorialService]
    _reg_clsid_ = "6FF2926B-6481-4105-A4D1-8C09FD4D3F9B"
    _reg_contractid_ = "@activestate.com/koRunCommandTutorialService;1"
    _reg_desc_ = "RunCommand Tutorial Service"

    def __init__(self):
        koDirs = components.classes["@activestate.com/koDirs;1"]\
                 .getService(components.interfaces.koIDirs)
        projectCacheDir = os.path.join(koDirs.supportDir, "samples",
                                       "runcmd_tutorials")
        KoTutorialService.__init__(self, "RunCommand", projectCacheDir,
                                   "runcmd_tutorial.komodoproject")

class KoTourTutorialService(KoTutorialService):
    """Tour Tutorial support"""
    _com_interfaces_ = [components.interfaces.koITutorialService]
    _reg_clsid_ = "4BFA5549-B656-476A-AAD1-C227930ACB08"
    _reg_contractid_ = "@activestate.com/koTourTutorialService;1"
    _reg_desc_ = "Tour Tutorial Service"

    def __init__(self):
        koDirs = components.classes["@activestate.com/koDirs;1"]\
                 .getService(components.interfaces.koIDirs)
        projectCacheDir = os.path.join(koDirs.supportDir, "samples",
                                       "tour_tutorials")
        KoTutorialService.__init__(self, "Tour", projectCacheDir,
                                   "komodo_tour.komodoproject")

class KoTclTutorialService(KoTutorialService):
    """Tcl Tutorial support"""
    _com_interfaces_ = [components.interfaces.koITutorialService]
    _reg_clsid_ = "60A60390-A723-473D-BF72-5F1D60F2D726"
    _reg_contractid_ = "@activestate.com/koTclTutorialService;1"
    _reg_desc_ = "Tcl Tutorial Service"

    def __init__(self):
        koDirs = components.classes["@activestate.com/koDirs;1"]\
                 .getService(components.interfaces.koIDirs)
        projectCacheDir = os.path.join(koDirs.supportDir, "samples",
                                       "tcl_tutorials")
        KoTutorialService.__init__(self, "Tcl", projectCacheDir,
                                   "tcl_tutorial.komodoproject")



#---- self test code

if __name__ == "__main__":
    for tutname in ["Perl", "XSLT", "Python", "PHP", "RunCommand", "Tour",
                    "Tcl"]:
        tutSvc = components.classes["@activestate.com/ko"+tutname+"TutorialService;1"]\
                 .getService(components.interfaces.koITutorialService)
        workingDir = tutSvc.GetWorkingDir()
        answer = raw_input("template working directory? [%s] " % workingDir)
        if answer:
            workingDir = answer
        print "Preparing the working directory...", workingDir
        errorStr = tutSvc.PrepareWorkingDir(workingDir)
        if errorStr:
            print "errorStr: '%s'" % errorStr
        else:
            if sys.platform.startswith("win"):
                os.system("dir %s" % workingDir)
            else:
                os.system("ls %s" % workingDir)
        print "project file name:", tutSvc.projectFileName
        print "project file path:", os.path.join(workingDir,
                                                 tutSvc.projectFileName)

