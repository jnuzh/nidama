#!python
# Copyright (c) 2004-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

"""Komodo Code Browser (the "Code" tab in the left side pane) tree view 
implementation using codeintel.
"""

import os
from os.path import abspath, basename, dirname, normcase, normpath
import threading
import logging
import re
from pprint import pprint, pformat
import weakref
from bisect import bisect_left
import operator

from xpcom import components, nsError, ServerException, COMException
from xpcom.components import classes as Cc, interfaces as Ci
from xpcom.server import UnwrapObject, WrapObject
from xpcom.server.enumerator import SimpleEnumerator
from koTreeView import TreeView, ObjectTreeView, ObjectTreeViewItem

from codeintel2.common import *
import contextlib


#---- globals

log = logging.getLogger("koCodeBrowser")
#log.setLevel(logging.DEBUG)



#---- Code Browser impl

class KoCodeBrowserElementItem(ObjectTreeViewItem):

    _com_interfaces_ = [components.interfaces.koICodeBrowserTreeItem]

    """A tree view item for an element"""
    def __init__(self, **kwargs):
        """Create a tree node for an eleement
            @param buf {koICodeIntelBuffer} the buffer for the text
            @param detail {str} Tooltip to show for the item
            @param parent_scope {tuple} The scope of the parent element
            @param lang_data {object} Data for the language
            @param name {str} The name of the element
            @param img {str} The image to use
            """
        ObjectTreeViewItem.__init__(self, log=kwargs.get("log", None))
        self.debug = self.log.debug if self.log else lambda *args: None
        self.data = kwargs
        self.lang_data = kwargs["lang_data"]
        self.buf = kwargs["buf"]
        self.text = kwargs["name"]
        self.tooltip = kwargs.get("detail", None)
        self.image = kwargs.get("img", None)
        self._children = None
        self._sorted = False
        self._open = False
        self.scope = kwargs["parent_scope"] + (kwargs["name"],)

    @property
    def detail(self):
        return self.data.get("detail", getattr(self, "text", None))

    @property
    def children(self):
        # lazy getter for children
        if self._children is not None:
            if not self._sorted:
                # needs re-sorting
                if not hasattr(self, "_sortKeyFunc"):
                    self.sortKey # sets _sortKeyFunc as side effect
                with self._dataLock:
                    self._children = sorted(self._children, key=self._sortKeyFunc)
                    self._sorted = True
                self.invalidate(recurse=False)
                index = self.rowIndex
                if index is not None:
                    self._invalidate(index, index + self.rowCount)
            return self._children

        is_module_scope = len(self.scope) == 2
        group_global_vars = is_module_scope \
                            and self.lang_data["group_global_vars"]
        children_args = {"buf":          self.buf,
                         "parent_scope": self.scope,
                         "log":          self.log,
                         "lang_data":    self.lang_data,
                        }
        section_args = dict(artificial=True, **children_args)

        # These are ObjectTreeViewItems of each type
        imports = []
        global_vars = []
        instance_vars = []
        symbols = []

        with contextlib.nested(self._invalidater, self._dataLock):
            self._children = []
            for data in self.data.get("children", []):

                # skip hidden and fabricated elements
                attrs = data.get("attributes", "").split()
                for attr in ("__hidden__", "__fabricated__"):
                    if attr in attrs:
                        continue

                args = children_args.copy()
                args.update(data)
                if  data["tag"] == "import":
                    imports.append(KoCodeBrowserElementItem(**args))
                elif group_global_vars and data["tag"] == "variable":
                    global_vars.append(KoCodeBrowserElementItem(**args))
                elif data["tag"] == "variable" and "__instancevar__" in attrs:
                    instance_vars.append(KoCodeBrowserElementItem(**args))
                else:
                    symbols.append(KoCodeBrowserElementItem(**args))
            del self.data["children"] # no longer needed

            if imports:
                child = KoCodeBrowserSectionItem(children=imports,
                                                 name=self.lang_data["import_group_title"],
                                                 img="import",
                                                 scope=self.scope + ("[imports]",),
                                                 **section_args)
                self._insertChildInternal(child, self._children)
                child.open = self.view.is_open_from_scope(child.scope)

            if global_vars:
                child = KoCodeBrowserSectionItem(children=global_vars,
                                                 name=self.lang_data["globalvar_group_title"],
                                                 img="variable",
                                                 scope=self.scope + ("[globalvars]",),
                                                 **section_args)
                self._insertChildInternal(child, self._children)
                child.open = self.view.is_open_from_scope(child.scope)

            if instance_vars:
                child = KoCodeBrowserSectionItem(children=instance_vars,
                                                 name="Instance Variables",
                                                 img="instance-variable",
                                                 scope=self.scope + ("[instancevars]",),
                                                 **section_args)
                self._insertChildInternal(child, self._children)
                child.open = self.view.is_open_from_scope(child.scope)

            if not hasattr(self, "_sortKeyFunc"):
                self.sortKey # side effect sets the sort function
            for child in sorted(symbols, key=self._sortKeyFunc):
                self._insertChildInternal(child, self._children)
                child.open = self.view.is_open_from_scope(child.scope)

            self._sorted = True
            return self._children
    @children.setter
    def children(self, val):
        # make setting children be a no-op
        pass

    @property
    def sortKey(self):
        if getattr(self, "_sortKeyFunc", None) is None:
            # initialize the sort key
            if self.parent:
                self.sortKey = self.parent.sortKey
            else:
                # no sort key known, use the default
                self.sortKey = "name"
        return getattr(self, "_sortKeyName", None)
    @sortKey.setter
    def sortKey(self, val):
        oldSort = getattr(self, "_sortKeyName", None)
        if oldSort == val:
            # didn't change the sort?
            return

        scopes = ("[imports]", "[globalvars]", "[instancevars]")

        if val == "file-order":
            def keyByFileOrder(item):
                if isinstance(item, KoCodeBrowserSectionItem):
                    return (0, scopes.index(item.data['scope'][-1]))
                line = item.data.get("line", 0)
                return (1, line, item.text.lower())
            key = keyByFileOrder
        elif val == "name":
            def keyByName(item):
                if isinstance(item, KoCodeBrowserSectionItem):
                    return (0, scopes.index(item.data['scope'][-1]))
                return (1, item.text.lower())
            key = keyByName
        else:
            raise ValueError("unknown sort order name: %r" % (val,))
        with self._invalidater:
            self._sorted = False
            setattr(self, "_sortKeyFunc", key)
            setattr(self, "_sortKeyName", val)
            index = self.rowIndex
            if index is not None:
                self._invalidater.invalidate(index, index + self.rowCount,
                                             "re-sorting %r" % (self,))
            # set the sort of the children _without_ generating anything
            for child in self._children or []:
                child.sortKey = val

    @property
    def _dataLock(self):
        view = self.view
        if view is not None:
            return view._dataLock
        @contextlib.contextmanager
        def f():
            yield
        return f()

    def __repr__(self):
        return "<%r (%r)>" % (self.__class__, getattr(self, "text", "<unnamed>"))

    def enumerate(self):
        return SimpleEnumerator(self.children)

class KoCodeBrowserSectionItem(KoCodeBrowserElementItem):
    """A tree view item for a section header, e.g. "Imports", "Global Variables" """
    def __init__(self, children=[], **kwargs):
        """Initialize a section
            @param children {iterable of ObjectTreeViewItem} The child nodes"""
        KoCodeBrowserElementItem.__init__(self, **kwargs)
        for child in children:
            child.parent = self
        self._children = children

    @property
    def children(self):
        # override the KoCodeBrowserElementItem children getter
        if not self._sorted:
            # needs re-sorting
            if not hasattr(self, "_sortKeyFunc"):
                self.sortKey # sets _sortKeyFunc as side effect
            with self._dataLock:
                self._children = sorted(self._children, key=self._sortKeyFunc)
                self._sorted = True
            self.invalidate(recurse=False)
            index = self.rowIndex
            if index is not None:
                self._invalidate(index, index + self.rowCount)
        return self._children
    @children.setter
    def children(self, val):
        pass

class KoCodeBrowserBufItem(KoCodeBrowserElementItem):
    """A tree item for a buffer
        @param buf {koICodeIntelBuffer} The buffer this item corresponds to
        @param send_fn {callable} Reference to koCodeIntelService.send
        @param log {logging.Log} Log
    """
    def __init__(self, buf=None, send_fn=None, log=None):
        KoCodeBrowserElementItem.__init__(self,
                                          buf=buf,
                                          name=basename(buf.path),
                                          parent_scope=(),
                                          log=log,
                                          lang_data={})
        self.scope = (buf.path,)
        self._children = []
        self.send = send_fn
        self._open = True

    def update(self):
        self.debug("updating %s", self.buf.path)
        self.send(command="codebrowser-get-buffer",
                  path=self.buf.path,
                  language=self.buf.lang,
                  callback=self._update)

    def _update(self, request, response):
        if not response.get("success"):
            self.debug("Failed to get tree for %s: %r",
                       self.text, response)
            return # XXX marky FIXME: do error handling
        if not self.view:
            return # This buffer is already dead
        self.debug("update buf %r view %r: %r", self.text, self.view,
                   response.get("tree"))
        buf = self.buf
        base = basename(buf.path)
        root = response.get("tree")

        with self._invalidater:
            for child in self._children[:]:
                self.removeChild(child)

            self.data = root.copy()
            del self.data["children"]

            for lang, data in root["children"].items():
                lang_data = {
                    "import_group_title": data.get("import_group_title"),
                    "globalvar_group_title": data.get("globalvar_group_title"),
                    "group_global_vars": data.get("group_global_vars", False),
                }
                child = KoCodeBrowserElementItem(buf=self.buf,
                                                 parent_scope=self.scope,
                                                 log=self.log,
                                                 lang_data=lang_data,
                                                 **data)
                assert child.parent is None
                assert child.view is None
                assert not child.open

                self._insertChildInternal(child, self._children)
                child.open = self.view.is_open_from_scope(child.scope)

                if self.view:
                    self.view.invalidater.check()
                    assert self.view.rowCount == self.view.invalidater._count, \
                        "after inserting blob %s, real row count %r should match invalidater row count %r\nchildren: %r" % (
                            child.text, self.view.rowCount, self.view.invalidater._count, self.view._visibleSubtree)

            if len(root["children"]) == 1:
                # only one language, hide the language node
                if self.view:
                    self.view.invalidater.check()
                child = self._children[0]

                self.data["img"] = child.data["img"]
                child.invisible = True
                child.open = True # otherwise you can't open it!
                child.data["invisible"] = True # for do_filter
                if self.view:
                    self.view.invalidater.check()

        self.debug("buf %s update complete, view %r, rows %r",
                   self.text, self.view, self.rowCount)

    @property
    def children(self):
        # override the KoCodeBrowserElementItem children getter
        return self._children
    @children.setter
    def children(self, val):
        pass
    def __repr__(self):
        return "<KoCodeBrowserBufItem (%r)>" % (self.buf,)


class KoCodeBrowserTreeView(ObjectTreeView):
    _com_interfaces_ = [components.interfaces.koICodeBrowserTreeView,
                        components.interfaces.nsITreeView,
                        components.interfaces.nsIObserver,
                        components.interfaces.koICodeBrowserTreeItem]
    _reg_clsid_ = "{E9E7E7EB-2DED-479B-AA1C-D8AF0E1347EA}"
    _reg_contractid_ = "@activestate.com/koCodeBrowserTreeView;1"
    _reg_desc_ = "Komodo Code Browser Tree View"

    def __init__(self):
        ObjectTreeView.__init__(self) # for debugging: , debug="cb")
        self._svc = Cc["@activestate.com/koCodeIntelService;1"]\
                      .getService(Ci.koICodeIntelService)
        self.send = UnwrapObject(self._svc).send

        self._buf_data_from_id = {}
        """The set of bufs to show in the tree. Need a ref-count because
            of split-view.
            (<lang>, <path>) -> {"buf": <weakref to buf>,
                                 "refcnt": <ref count>,
                                 "item": <KoCodeBrowserBufItem>}
            Note that the path needs to go through normcase/normpath
            """

        self._ignoreNextToggleOpenState = False

        self._num_top_nodes_open_by_default = 2
        self._is_open_from_scope = {}
        self._dataLock = threading.RLock()
        self._sortedBy = "name"
        self._filter = None
        self._filter_re = None

        # Data for controlling the display of node detail when the mouse is
        # hovering over that row's icon.
        self._showDetailForRow = -1  # -1 means don't show for any row
        atomSvc = components.classes["@mozilla.org/atom-service;1"].\
                  getService(components.interfaces.nsIAtomService)
        self._showDetailAtom = atomSvc.getAtom("showDetail")
        self._notMatchResultAtom = atomSvc.getAtom("notMatchResult")
        
        obsSvc = components.classes["@mozilla.org/observer-service;1"]\
            .getService(components.interfaces.nsIObserverService)
        self._wrappedSelf = WrapObject(self, components.interfaces.nsIObserver)
        obsSvc.addObserver(self._wrappedSelf, "codeintel_buffer_scanned", True)

        # Mozilla 22 changed the way tree properties work.
        nsXulAppInfo = components.classes["@mozilla.org/xre/app-info;1"].getService(components.interfaces.nsIXULAppInfo)
        try:
            mozMajorVer = int(nsXulAppInfo.platformVersion.split(".")[0])
        except:
            log.warn("Unable to parse nsXulAppInfo.platformVersion")
        if mozMajorVer < 22:
            # Older mozilla versions used a different properties mechanism.
            self.getCellProperties = self.getCellPropertiesMoz21AndOlder

    def _get_buf_id(self, buf):
        """Get the buffer id for a given buffer
        @returns {tuple} See definition of _buf_data_from_id
        """
        path = buf.path
        if abspath(path) == path:
            # this is an actual file path, not a URL or whatever
            path = normcase(normpath(path))
        return (buf.lang, path)

    def finalize(self):
        obsSvc = components.classes["@mozilla.org/observer-service;1"]\
            .getService(components.interfaces.nsIObserverService)
        obsSvc.removeObserver(self, "codeintel_buffer_scanned")
        del self._wrappedSelf
        setattr(self, "_prefSvc", None)

    def setCodeBrowserMgr(self, codeBrowserMgr):
        self._codeBrowserMgr = codeBrowserMgr

    @property
    def prefSvc(self):
        """Get the app-wide default preferences"""
        if not getattr(self, "_prefSvc", None):
            prefSvc = components.classes["@activestate.com/koPrefService;1"]\
                                .getService().prefs
            setattr(self, "_prefSvc", prefSvc)
        return self._prefSvc

    is_open_pref_name = "codeintel_open_codebrowser_nodes"
    def restorePrefs(self):
        #TODO Put a timestamp into this datastruct and time out
        #     things after a week or so (to keep it small).
        #     A lighter (but not perfect) soln would be to just drop
        #     half the keys when they reach a certain limit.
        if self.prefSvc.hasStringPref(self.is_open_pref_name):
            pref_str = self.prefSvc.getStringPref(self.is_open_pref_name)
            try:
                pref_val = eval(pref_str)
            except SyntaxError, ex:
                log.debug("drop '%s' pref value: %s",
                          self.is_open_pref_name, ex)
            else:
                if pref_val and not isinstance(pref_val.keys()[0], tuple):
                    # This is the old format for this pref (strings
                    # as keys). Drop it.
                    pass
                else:
                    self._is_open_from_scope = pref_val

    def savePrefs(self):
        self.prefSvc.setStringPref(self.is_open_pref_name,
                                   repr(self._is_open_from_scope))

    def observe(self, subject, topic, path):
        assert topic == "codeintel_buffer_scanned", \
            "Unexpected topic %s" % (topic,)
        if topic != "codeintel_buffer_scanned":
            return
        # Look for matching buffers
        with contextlib.nested(self._dataLock, self.invalidater):
            for (buf_lang, buf_path), buf_data in self._buf_data_from_id.items():
                if buf_path == path:
                    log.debug("Updating buffer %s", path)
                    try:
                        item = buf_data["item"]
                        assert item.parent == self
                        assert item.view == self
                        # This is a little silly - asking for the tree again
                        # instead of just having it sent down with the
                        # notification - but it works well enough (since it
                        # won't actually be rescanned again)
                        item.update()
                        if self._filter:
                            self.do_filter(item=item)
                    except:
                        log.exception("Failed to update %s", path)
                    else:
                        log.debug("successfully updated %s", path)
                else:
                    log.debug("buf.path %s is not target path %s",
                              buf_path, path)

    # Mapping of which container nodes are open/closed.
    #   {<scope>: <is-open>, ...}
    # where <scope> is a full scope path tuple to the node in the
    # tree.
    def is_open_from_scope(self, scope):
        try:
            return self._is_open_from_scope[scope]
        except KeyError:
            return len(scope) <= self._num_top_nodes_open_by_default

    def add_buf(self, buf):
        buf = UnwrapObject(buf)
        log.debug("Adding buffer %r", buf)
        if buf is None:
            return # guard against buffer already having been closed
        if not self._svc.is_citadel_lang(buf.lang):
            return

        buf_id = self._get_buf_id(buf)
        if buf_id in self._buf_data_from_id:
            # Split view: increment ref count for this buffer.
            self._buf_data_from_id[buf_id]["refcnt"] += 1
            return

        self._dataLock.acquire()
        try:
            adding_first_file = len(self._buf_data_from_id) == 0
            if adding_first_file:
                self._codeBrowserMgr.haveFilesInWS(True)

            item = KoCodeBrowserBufItem(buf, self.send, log=self.log)
            self.insertChild(item)
            item.update()
            self._buf_data_from_id[buf_id] = {"buf": weakref.ref(buf),
                                              "refcnt": 1,
                                              "item": item}

            if self._filter:
                self.do_filter(item=item)

        finally:
            self._dataLock.release()

    def change_buf_lang(self, buf):
        # The way the 'switched_current_language' IDE event current
        # works in Komodo we don't know what the old language was.
        buf_lang, buf_path = self._get_buf_id(buf)
        for existing_lang, existing_path in self._buf_data_from_id:
            if buf_path == existing_path:
                self._remove_buf_id((existing_lang, existing_path))
                break
        if buf:
            self.add_buf(buf)

    def remove_buf(self, buf):
        buf_id = self._get_buf_id(buf)
        data = self._buf_data_from_id.get(buf_id)
        if data:
            data["refcnt"] -= 1
            if data["refcnt"] == 0:
                self._remove_buf_id(buf_id)

    def _remove_buf_id(self, buf_id):
        item = None # used to remove things outside the lock
        self._dataLock.acquire()
        try:
            try:
                item = self._buf_data_from_id[buf_id].get("item", None)
                del self._buf_data_from_id[buf_id]
            except KeyError:
                pass
            if not self._buf_data_from_id:
                self._codeBrowserMgr.haveFilesInWS(False)

        finally:
            self._dataLock.release()

        if item and item.parent:
            item.parent.removeChild(item)

    def mouseOverNode(self, row, element):
        invalids = [] # rows that need redrawing
        if element == "image" and self._showDetailForRow != row:
            # The mouse is now over a new node's image: show details for
            # that node.
            invalids = [i for i in (self._showDetailForRow, row)
                        if i != -1]
            self._showDetailForRow = row
        elif (self._showDetailForRow != -1 and element != "image"
              and self._showDetailForRow != row):
            # The mouse is over a row for which we are not showing detail:
            # we should remove any special detail UI for other rows.
            invalids = [self._showDetailForRow]
            self._showDetailForRow = -1

        if invalids:
            self._tree.beginUpdateBatch()
            for invalid in invalids:
                column = self._tree.columns.getNamedColumn("codebrowser-tree-node")
                self._tree.invalidateCell(invalid, column)
            self._tree.endUpdateBatch()

    def do_filter(self, refine=False, item=None):
        """Apply filtering to the items.
            @param refine {bool} If true, this is a refinement and currently
                hidden items will not be unhidden
            @param item {ObjectTreeViewItem} The subtree to filter; if None,
                the whole tree is filtered.
            """
        def check(item, refine):
            """
            Check an item to see if it should be displayed
            @param item {ObjectTreeViewItem} The subtree to check
            @param refine {bool} Whether this is a refinement
            @returns {bool} whether this item or any descendants are visible
            """

            has_children = False

            for child in item.children:
                if refine and child.invisible and not child.data.get("invisible", False):
                    # this is already invisible, no need to check it (or its
                    # children) when refining
                    continue
                has_children |= check(child, refine)

            if item.data.get("invisible", False) and not has_children:
                # this needs to be invisible
                item.invisible = True
                return has_children

            if self._matches_filter(item):
                # item matches the filter
                item.invisible = False
                if item.rowIndex is not None and not item.data.get("match"):
                    self.invalidater.invalidate(item.rowIndex)
                item.data["match"] = True
                return True

            # this item does not itself match; show it if it has matched
            # children
            item.invisible = not has_children
            if has_children and not item.open:
                item.data["forced_open"] = True
                item.open = True
            if item.rowIndex is not None and item.data.get("match"):
                self.invalidater.invalidate(item.rowIndex)
            item.data["match"] = False
            return has_children

        def clear(item):
            """
            Clear any filtering applied
            @param item {ObjectTreeViewItem} The subtree to clear
            """
            for child in item.children:
                clear(child)
            if item.data.get("invisible", False) != item.invisible:
                item.invisible = item.data.get("invisible")
            if item.data.get("forced_open", False):
                item.open = False
                del item.data["forced_open"]

        with self.invalidater:
            self._dataLock.acquire()
            try:
                if self._filter:
                    check(item or self, refine)
                else:
                    clear(item or self)
            finally:
                self._dataLock.release()

    def _matches_filter(self, item):
        # Note: If this changes to anything more fancy that
        # string-contains comparison then revisit whether
        # do_filter() optimization in .setFilter() is possible.
        if item.data.get("artificial"):
            # Artificial rows (i.e. those that don't represent
            # actual data, but are just there for grouping) should
            # never match.
            return False
        return self._filter_re.search(item.text)

    def _filtered(self, gen):
        """Filter tree rows generated by 'gen' against the current
        match filter.
        """
        on_deck = {}
        for row in gen:
            level = row["level"]
            on_deck[level] = row
            if self._matches_filter(row):
                row["match"] = True
                for i in range(level+1):
                    if on_deck[i] is not None:
                        yield on_deck[i]
                        on_deck[i] = None
            else:
                row["match"] = False

    def sortBy(self, key):
        self._dataLock.acquire()
        try:
            with self.invalidater:
                changed = False
                for child in self.children:
                    if child.sortKey != key:
                        changed = True
                        child.sortKey = key
                if changed:
                    self.children # refresh
                    if self._filter:
                        self.do_filter()
            self._sortedBy = key
        finally:
            self._dataLock.release()

    @property
    def sortKey(self):
        return self._sortedBy

    def setFilter(self, filter_text):
        self._dataLock.acquire()
        try:
            if self._filter != filter_text:
                try:
                    filter_re = re.compile(filter_text, re.I)
                except re.error, ex:
                    raise ServerException(nsError.NS_ERROR_FAILURE, str(ex))

                refine = self._filter and self._filter in filter_text \
                        and re.escape(filter_text) == filter_text
                        # As long as our filtering is a simple string-contains
                        # check, then we need only refine the current hits.
                self._filter = filter_text
                self._filter_re = filter_re
                self.do_filter(refine=refine)
        finally:
            self._dataLock.release()
    
    def locateScope(self, buf, pos, closestOnly=False, callback=None):
        buf = UnwrapObject(buf)
        RESULT_SUCCESSFUL = Ci.koIAsyncCallback.RESULT_SUCCESSFUL
        RESULT_ERROR = Ci.koIAsyncCallback.RESULT_ERROR

        if callback:
            try:
                callback = callback.koIAsyncCallback.callback
            except AttributeError:
                pass
        else:
            callback = lambda result, data: None

        if self._filter:
            self._filter = None
            self.do_filter()

        if not self._tree:
            log.info("locateScope(%r, %r) called with no tree, avoiding work",
                     buf, pos)
            callback(RESULT_ERROR, None)
            return

        buf_id = self._get_buf_id(buf)
        if not buf_id in self._buf_data_from_id:
            log.info("Couldn't find Code Browser row for buffer %r language %r",
                     buf.path, buf.lang)
            callback(RESULT_ERROR, None)
            return

        def on_have_path(request, response):
            if not response.get("success", False):
                callback(RESULT_ERROR, None)
                return
            path = response.get("path", [])
            if not path:
                callback(RESULT_ERROR, None)
                return

            log.debug("locateScope: have path %s",
                      " -> ".join(map(str, path)))

            try:
                item = self._buf_data_from_id[buf_id]["item"]
            except KeyError:
                # Buf is already gone... nothing to do.
                return

            self._dataLock.acquire()
            try:
                # - For each element in the scope stack walk forward to the
                #   appropriate child item
                seen_path = []
                while path:
                    if not item.open:
                        if closestOnly:
                            # don't open anything
                            break
                        log.debug("open container %s (index %r)",
                                  item.text, item.rowIndex)
                        item.open = True
                    name = path.pop(0)
                    seen_path.append(name)
                    children = filter(lambda child: child.text == name, item.children)
                    if not children:
                        seen_path.reverse()
                        log.info("Coudn't find Code Browser row for %r scope in %r",
                                 seen_path, buf)
                        break
                    item = children.pop()
                    log.debug("located '%s' row at idx %d: %r",
                              name, item.rowIndex, item)

                result = self.selectRowByItem(item)
                callback(RESULT_SUCCESSFUL if result else RESULT_ERROR, None)
            except:
                callback(RESULT_ERROR, None)
            finally:
                self._dataLock.release()

        self.send(command="codebrowser-locate-scope",
                  path=buf.path,
                  language=buf.lang,
                  pos=pos,
                  callback=on_have_path)

    #---- nsITreeView methods

    def getCellText(self, row_idx, col):
        assert col.id == "codebrowser-tree-node"
        item = self.item_from_index(row_idx)
        assert item is not None, "getting cell text for row %r of %r" % (
            row_idx, self.rowCount)
        if item is None:
            # We're busted, try to invalidate...
            self._tree.invalidate()
            raise COMException(nsError.NS_ERROR_INVALID_ARG,
                               "getCellText: row %r not found" % (row_idx,))
        if row_idx == self._showDetailForRow and hasattr(item, "detail"):
            return item.detail
        else:
            return item.text

    def getCellProperties(self, row_idx, col):
        #assert col.id == "codebrowser-tree-node"
        properties = ""
        if row_idx == self._showDetailForRow:
            properties += " showDetail"
        item = self.item_from_index(row_idx)
        if self._filter and item is not None and not item.data.get("match"):
            properties += " notMatchResult"
        return properties.lstrip()

    def getCellPropertiesMoz21AndOlder(self, row_idx, col, properties):
        #assert col.id == "codebrowser-tree-node"
        if row_idx == self._showDetailForRow:
            properties.AppendElement(self._showDetailAtom)
        item = self.item_from_index(row_idx)
        if self._filter and item is not None and not item.data.get("match"):
            properties.AppendElement(self._notMatchResultAtom)

    img_url_from_img_name = {
        "Python" : "chrome://komodo/skin/images/languages/python/python_16x16.png",
        "Python3" : "chrome://komodo/skin/images/languages/python/python3_16x16.png",
        "Perl": "chrome://komodo/skin/images/languages/perl/perl_16x16.png",
        "PHP": "chrome://komodo/skin/images/languages/php/php_16x16.png",
        "Tcl": "chrome://komodo/skin/images/languages/tcl/tcl_16x16.png",
        "JavaScript": "chrome://komodo/skin/images/languages/javascript/javascript_16x16.png",
        "Node.js": "chrome://komodo/skin/images/languages/nodejs/nodejs_16x16.png",
        "HTML": "chrome://komodo/skin/images/languages/html/html_16x16.png",
        "HTML5": "chrome://komodo/skin/images/languages/html/html5_16x16.png",
        "XML": "chrome://komodo/skin/images/languages/xml/xml_16x16.png",
        "Ruby": "chrome://komodo/skin/images/languages/ruby/ruby_16x16.png",
        "CSS" : "chrome://komodo/skin/images/languages/css/css_16x16.png",
        "Less" : "chrome://komodo/skin/images/languages/css/less_16x16.png",
        "SCSS" : "chrome://komodo/skin/images/languages/css/scss_16x16.png",
        "function-private": "chrome://komodo/skin/images/cb_function_private.png",
        "function-protected": "chrome://komodo/skin/images/cb_function_protected.png",
        "function": "chrome://komodo/skin/images/cb_function.png",
        "interface-private": "chrome://komodo/skin/images/cb_interface_private.png",
        "interface-protected": "chrome://komodo/skin/images/cb_interface_protected.png",
        "interface": "chrome://komodo/skin/images/cb_interface.png",
        "namespace": "chrome://komodo/skin/images/cb_namespace.png",
        "class-private": "chrome://komodo/skin/images/cb_class_private.png",
        "class-protected": "chrome://komodo/skin/images/cb_class_protected.png",
        "class": "chrome://komodo/skin/images/cb_class.png",
        "trait": "chrome://komodo/skin/images/cb_trait.png",
        "instance-variable-private": "chrome://komodo/skin/images/cb_instance_variable_private.png",
        "instance-variable-protected": "chrome://komodo/skin/images/cb_instance_variable_protected.png",
        "instance-variable": "chrome://komodo/skin/images/cb_instance_variable.png",
        "variable-private": "chrome://komodo/skin/images/cb_variable_private.png",
        "variable-protected": "chrome://komodo/skin/images/cb_variable_protected.png",
        "variable": "chrome://komodo/skin/images/cb_variable.png",
        "argument-private": "chrome://komodo/skin/images/cb_argument_private.png",
        "argument-protected": "chrome://komodo/skin/images/cb_argument_protected.png",
        "argument": "chrome://komodo/skin/images/cb_argument.png",
        "import": "chrome://komodo/skin/images/cb_import.png",
        "scanning": "chrome://komodo/skin/images/cb_scanning.png",
        "error": "chrome://komodo/skin/images/cb_error.png",
        "container": "chrome://komodo/content/icons/open.png",
        "constant": "chrome://komodo/skin/images/cb_constant.png",
    }
    default_img_url = "chrome://komodo/skin/images/cb_variable.png"

    def getImageSrc(self, row, col):
        if col.id != "codebrowser-tree-node":
            return ""
        item = self.item_from_index(row)
        if item is None:
            return ""
        img_name = item.data.get("img")
        img_url = self.img_url_from_img_name.get(
            img_name, self.default_img_url)
        return img_url

    def ignoreNextToggleOpenState(self):
        self._ignoreNextToggleOpenState = True

    def toggleOpenState(self, row_idx):
        if self._ignoreNextToggleOpenState:
            log.debug("ignoring this toggleOpenState(row_idx=%r)", row_idx)
            self._ignoreNextToggleOpenState = False
            return

        if self._filter:
            return

        with self._dataLock:
            item = self.item_from_index(row_idx)
            item.open = not item.open
            self._is_open_from_scope[item.scope] = item.open

    def rememberOpenState(self, item):
        item = UnwrapObject(item)
        if hasattr(item, "scope"):
            with self._dataLock:
                self._is_open_from_scope[item.scope] = item.open

    #XXX handle canDropOn(), canDropBeforeAfter(), drop()
    #XXX What about the performAction[on{Row|Cell}]() methods?
    if True:
        # Turn this on to silence TreeView logging, if enabled,
        # for these specific methods.
        def isSorted(self):
            return 0
        def getRowProperties(self, row, properties=None):
            pass
        def getColumnProperties(self, column, properties=None):
            pass

    def enumerate(self):
        return SimpleEnumerator(self.children)

    @property
    def buf(self):
        return None

    #---- current node accessor attributes
    @property
    def _currentItem(self):
        """Get the KoCodeBrowserElementItem for the current selection"""
        idx = self._tree.view.selection.currentIndex
        return self.item_from_index(idx)

    @property
    def currentNodeFilePath(self):
        """Get the file path of the buffer for the current item"""
        item = self._currentItem
        if item is None:
            return None
        return item.buf.path

    @property
    def currentNodeLine(self):
        """The 1-based index of the starting line of the currently selected item;
            will be 0 if the line number is unknown or is not meaningful
            """
        # Special case: if this is a module node and the line is 1,
        # then don't specify to jump to line 1, this might be
        # changing the current line if the module is already open. A
        # module line of 1 usually indicates that this is a language
        # where file===module, i.e. the line number is essentially
        # meaningless.
        item = self._currentItem
        if not item.data:
            return 0 # broken item? should always have data...
        line = item.data.get("line")
        if line is not None:
            return line
        if item.data.get("ilk") == "argument":
            # for arguments, jump to the line indicated by the parent function
            try:
                return item.parent.data.get("line", 0)
            except AttributeError:
                return 0
        return 0

    @property
    def currentNodeLanguage(self):
        item = self._currentItem
        if item:
            return item.buf.lang
        return None

    @property
    def currentNodeSymbolPattern(self):
        item = self._currentItem
        if not item:
            return None
        if item.elem.type == "import":
            if item.elem.symbol in ("*", "**"): # special signifiers
                symbol = None
            else:
                symbol = item.elem.symbol
        else:
            symbol = item.elem.name
        return symbol

    @property
    def currentNodeModulePattern(self):
        item = self._currentItem
        if item is None:
            return None
        if item.elem.type == "import":
            return item.elem.module
        else:
            return None
