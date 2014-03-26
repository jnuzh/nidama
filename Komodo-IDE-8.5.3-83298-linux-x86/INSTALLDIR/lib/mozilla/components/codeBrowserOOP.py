"""CodeIntel-side command extensions for code browser support"""

from codeintel2.oop.driver import CommandHandler, Driver, RequestFailure
from collections import defaultdict
from os.path import dirname, basename, splitext
from pprint import pformat
import logging
log = logging.getLogger("codeintel.oop.codebrowser")

class CodeBrowserCommandHandler(CommandHandler):
    supportedCommands = ["codebrowser-get-buffer",
                         "codebrowser-locate-scope",
                        ]

    def canHandleRequest(self, request):
        return request.command in self.supportedCommands

    def handleRequest(self, request, driver):
        if not request.command.startswith("codebrowser-"):
            raise RequestFailure(message="Unexpected command %s" % (request.command,))
        meth_name = "do_" + request.command[len("codebrowser-"):].replace("-", "_")
        meth = getattr(self, meth_name, None)
        if not meth:
            raise RequestFailure(message="Unexpected command %s" % (request.command,))
        return meth(request, driver)

    def do_get_buffer(self, request, driver):
        """Get the full buffer tree for code browser"""
        buf = driver.get_buffer(request=request)
        base = basename(buf.path)
        tree = {"name": base,
                "detail": "%s (%s)" % (base, dirname(buf.path)),
                "children": {}}

        if buf.scan_time is None and not buf.accessor.content:
            # The buffer has never been scanned before.
            # Special case empty buffers:
            # If the buffer is empty, it's likely that we just haven't finished
            # loading the file.  To avoid blob_from_lang implicitly scanning the
            # file and marking it as up to date (when it clearly isn't), force a
            # scan now with mtime=0 so it will be re-scanned once we have the
            # contents.  See bug 99498.
            log.debug("%s: Empty buffer", buf.path)
            buf.scan(mtime=0)

        blobs = buf.blob_from_lang
        if blobs is None:
            # wtf, the getter is supposed to fix this
            buf.scan()
            blobs = buf.blob_from_lang or dict()

        if buf.scan_error:
            tree.update({"img": "error",
                         "detail": "error scanning '%s': %s" %
                              (base, buf.scan_error)})

        have_blob_data = any(len(b) for b in blobs.values())
        for lang, blob in blobs.items():
            langintel = driver.mgr.langintel_from_lang(lang)
            data = self._get_children(blob, buf, langintel)
            tree["children"][lang] = data

        if not have_blob_data and buf.scan_error:
            # I.e. there was an error scanning the thing.
            detail = "error scanning '%s'" % base
            if buf.scan_error:
                detail += ": "+str(buf.scan_error)
            tree.update({"detail": detail,
                         "img": "error",
                         "artificial": True})

        log.debug("%s:\n%s", buf.path, pformat(tree, indent=2))

        driver.send(path=buf.path,
                    scan_error=buf.scan_error,
                    tree=tree)

    def _get_children(self, elem, buf, langintel):
        """Helper to get the children of a given CI element"""
        data = langintel.cb_data_from_elem_and_buf(elem, buf)
        data = self._fixParams(elem, data, buf, langintel)
        data["children"] = []
        for child in elem:
            data["children"].append(self._get_children(child, buf, langintel))
        return data

    def _fixParams(self, elem, data, buf, langintel):
        """Helper to fixup an element's data"""
        ilk = elem.get("ilk")
        if ilk:
            data["ilk"] = ilk
        if ilk == "blob": # and level == 1
            # This is one of many blobs under a file row
            data["name"] = "%s Code" % (elem.get("lang"),)
            data["detail"] = "%s Code in '%s'" % (elem.get("lang"),
                                                  buf.path)
            data["import_group_title"] = langintel.cb_import_group_title
            data["globalvar_group_title"] = langintel.cb_globalvar_group_title
            data["group_global_vars"] = langintel.cb_group_global_vars
        elif "name" not in data:
            data["name"] = repr(elem)
        if ilk == "blob" and elem.tag == "scope" and buf.scan_error:
            data["detail"] = "error scanning '%s': %s" % (
                basename(buf.path), buf.scan_error)
            data["img"] = "error"
        if data.get("detail") == data["name"]:
            del data["detail"] # useless
        try:
            data["line"] = int(elem.get("line", "0"), 10)
        except ValueError:
            data["line"] = 0
        data["tag"] = elem.tag
        attrs = elem.get("attributes")
        if attrs:
            data["attributes"] = attrs

        return data

    def do_locate_scope(self, request, driver):
        """Locate the scope for a position
        Returns a list, starting from the root of the tree"""
        buf = driver.get_buffer(request=request)
        pos = int(request.get("pos"))
        log.debug("locating scope: pos %i of %r", pos, buf)
        blob, lpath = buf.scoperef_from_pos(pos) or (None, None)
        if not blob:
            raise RequestFailure(message="Failed to find position %s" % (pos,))
        langintel = driver.mgr.langintel_from_lang(blob.get("lang"))
        blob_data = langintel.cb_data_from_elem_and_buf(blob, buf)
        blob_data = self._fixParams(blob, blob_data, buf, langintel)
        lpath.insert(0, blob_data["name"])
        log.debug("got lpath: %r", lpath)
        driver.send(path=lpath)


# NOTE that codeintel may have issues loading XPCOM; if we need that, we'll need
# to manually add things to sys.path.
class CommandExtensionRegistrationHelper(object):
    _com_interfaces_ = []
    _reg_clsid_ = "{8dc474bd-7654-43f2-b5f1-48ba0e533cc1}"
    _reg_contractid_ = "@activestate.com/koCodeBrowser/registrationHelper;1"
    _reg_desc_ = "Komodo Code Browser Out-of-process Registration Helper"
    _reg_categories_ = [
        ("codeintel-command-extension", "@activestate.com/koCodeBrowser/registrationHelper;1"),
    ]

    data = [(dirname(__file__), splitext(basename(__file__))[0]),]
    def __init__(self):
        self.data = self.data[:]
    def __iter__(self):
        return self
    def next(self):
        try:
            return self.data.pop(0)
        except IndexError:
            raise StopIteration

def registerExtension():
    """Code Browser command extension registration"""
    log.debug("Registering code browser extension")
    Driver.registerCommandHandler(CodeBrowserCommandHandler())
