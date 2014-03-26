#!python 
# Copyright (c) 2000-2006 ActiveState Software Inc.
# See the file LICENSE.txt for licensing information.

# Implementation of the tree view for displaying a "DOM". 

from xpcom import components
 
import sys, os, re, types, string, threading
import logging
from koTreeView import TreeView
from koXMLTreeService import getService, XMLDocument
import cElementTree as ET
from cElementTree import Element, ElementTree
import elementtree

from zope.cachedescriptors.property import Lazy as LazyProperty

elementType = (type(Element('')), type(elementtree.ElementTree.Element('')))
log = logging.getLogger("KoDOMTreeView")
#log.setLevel(logging.DEBUG)


# detail for attr is name=value
# detail for elem is prefix:localName (id="" | first attr="")

def matchesFilter(elem, filterString):
    """Returns a boolean indicating if this node matches the filter."""
    # XXX FIXME
    return elem.detail.lower().find(filterString.lower()) != -1

def getScopedName(tree, elem, pScopedName=None):
    attr = ""
    if not isinstance(elem, elementType):
        attr = "@%s" % elem[0]
        elem = elem[2]
    # parent.scopedName + node.localName + str(len(parent.children))
    parent = tree.nodemap.get(elem, None)
    if parent is not None:
        if not pScopedName:
            pScopedName = getScopedName(tree, parent)
        return "%s/%s[%d]%s" % (pScopedName, elem.tag, list(parent).index(elem), attr)
    if pScopedName:
        return "%s/%s%s" % (pScopedName, elem.tag, attr)
    return "%s%s" % (elem.tag, attr)

def generateRows(tree, elem, rows, nodeIsOpen, sortBy=None, scopedName=None,
                     filterString=None, showDetails=0):
    # given a tree, a list of open nodes, produce a list of nodes for display
    rows.append(elem)
    scopedName = getScopedName(tree, elem, scopedName)
    if scopedName not in nodeIsOpen:
        nodeIsOpen[scopedName] = 0
    if nodeIsOpen[scopedName]:
        if showDetails:
            # add attributes as rows
            for name, value in elem.attrib.items():
                rows.append((name, value, elem))
        # add children
        if filterString:
            return
        for child in elem:
            generateRows(tree, child, rows, nodeIsOpen, sortBy, scopedName,
                         filterString, showDetails)

class KoDOMTreeView(TreeView):
    _com_interfaces_ = [components.interfaces.koIDOMTreeView,
                        components.interfaces.nsITreeView]
    _reg_clsid_ = "{f3691fa9-210a-400d-b909-7c7684094a1f}"
    _reg_contractid_ = "@activestate.com/KoDOMTreeView;1"
    _reg_desc_ = "Komodo DOM Tree Table View"

    def __init__(self):
        TreeView.__init__(self, debug=0)
        self.ET = None
        self._set = [] # working set of elements found via xpath
        self._rows = []
        self._sortedBy = None

        # Mapping of node "scoped-name" to a boolean indicating if that
        # node is open (or should be) in the Code Browser.
        self._nodeIsOpen = {}
        self._filterString = ''
        self._showDetails = 0

        self._tree = None
        self._document = None
        self._thread = None
        self._dataLock = threading.RLock()

    @LazyProperty
    def atomService(self):
        return components.classes["@mozilla.org/atom-service;1"].\
                          getService(components.interfaces.nsIAtomService)

    @LazyProperty
    def _notMatchResultAtom(self):
        return self.atomService.getAtom("disabled")

    def setDocument(self, doc):
        self._document = doc

    def reset(self):
        # start a thread to parse the document
        if self._thread: # the parse is in progress, so give up on this one
            return False # ideally the domview.js code restarts something later.
        basename = self._document.baseName
        buffer = self._document.buffer
        path = None
        if self._document.file:
            path = self._document.file.path
        else:
            path = basename
        self._thread = threading.Timer(0, self._reset, args=(buffer, path))
        self._thread.start()
        return True

    def getTreeForDocument(self, buffer, uri=None):
        #print "domview get document %s"%uri
        return getService().getTreeForURI(uri, buffer)
        # XXX FIXME post beta 1
        if not uri:
            return getService().getTreeForContent(buffer)
        
        tree = getService().treeFromCache(uri)
        if not tree:
            tree = getService().getTreeForURI(uri, buffer)
        return tree

    def _reset(self, buffer, path):
        try :
            #print "domviewer parsing %s" % path
            tree = self.getTreeForDocument(buffer, path)
            #print "GOT IT"
            if tree is None:
                tree = XMLDocument()
            if tree.root is None:
                tree = None
            self._dataLock.acquire()
            try:
                self._set = []
                self.ET = tree
                if tree is not None and tree.root is not None:
                    self._nodeIsOpen[getScopedName(tree, tree.root)] = 1
                    self._set.append(tree.root)
            finally:
                self._dataLock.release()
            @components.ProxyToMainThread
            def refreshOnMainThread():
                self.refresh()
            refreshOnMainThread()
        except Exception, e:
            log.exception(e)
        self._thread = None

    def refresh(self):
        self._dataLock.acquire()
        try:
            try:
                if self.ET and self.ET.root is not None:
                    self._set = []
                    rows = []
                    set = []
                    filterString = self._filterString
                    if filterString:
                        # fix namespaces
                        prefixes = re.findall("(\w+):", filterString)
                        for prefix in prefixes:
                            if prefix in self.ET.prefixmap:
                                filterString = filterString.replace(prefix+":",
                                                                    "{%s}" % self.ET.prefixmap[prefix])
                        if filterString[0] not in ['.','/','*']:
                            if self.ET.root.ns and filterString[0] is not "{":
                                filterString = "{%s}%s" % (self.ET.root.ns, filterString)
                            self._set = list(self.ET.root.getiterator(filterString))
                        else:
                            try:
                                tree = ElementTree(self.ET.root)
                                self._set = tree.findall(filterString)
                            except SyntaxError, e:
                                # user incorrectly typed an xpath
                                pass
                        if self._set:
                            # generate a set that includes the parents
                            for node in self._set:
                                parents = []
                                parent = self.ET.nodemap[node]
                                while parent and parent not in set:
                                    parents.append(parent)
                                    parent = self.ET.nodemap[parent]
                                if parents:
                                    parents.reverse()
                                    set.extend(parents)
                                set.append(node)
                        
                    if not self._filterString and not set:
                        set = self.ET.getRoots()
                    for elem in set:
                        generateRows(self.ET, elem,
                                    rows, self._nodeIsOpen,
                                    self._sortedBy,
                                    filterString=self._filterString,
                                    showDetails=self._showDetails)
                    self._rows = rows
                else:
                    self._rows = []
            except Exception, e:
                log.exception("Error in KPFTreeView.refresh")
                raise
        finally:
            self._dataLock.release()

        if self._tree:
            self._tree.beginUpdateBatch()
            self._tree.invalidate()
            self._tree.endUpdateBatch()


    def getStartPos(self, index):
        self._dataLock.acquire()
        try:
            if index >=0 and index < len (self._rows):
                node = self._rows[index]
                if isinstance(node, elementType):
                    return node.start
                else:
                    # find the element we belong to
                    return node[2].start
        finally:
            self._dataLock.release()
        return -1

    def getEndPos(self, index):
        self._dataLock.acquire()
        try:
            if index >=0 and index < len (self._rows):
                node = self._rows[index]
                if isinstance(node, elementType):
                    if node.end:
                        return node.end
                elif node[2].end:
                    # find the element we belong to
                    return node[2].end
        finally:
            self._dataLock.release()
        return []

    def get_rowCount(self):
        self._dataLock.acquire()
        try:
            return len(self._rows)
        finally:
            self._dataLock.release()

    def getCellText(self, row, column):
        if row >= len(self._rows): return ""
        col = column.id
        cell = ""
        self._dataLock.acquire()
        try:
            # detail for attr is name=value
            # detail for elem is prefix:localName {namespace}
            node = self._rows[row]
            if col == "domview-name":
                if isinstance(node, elementType):
                    tag = self.ET.qname(node.tag)
                    attr = ('id', node.attrib.get('id', ''))
                    if not attr[1]:
                        attrs = node.attrib.items()
                        if attrs:
                            attr = attrs[0]
                        else:
                            attr = None
                    if attr:
                        cell = "%s (%s='%s')" % (tag, attr[0], attr[1])
                    else:
                        cell = tag
                else:
                    cell = "%s (%s)" % (self.ET.qname(node[0]), node[1])
        finally:
            self._dataLock.release()
        if type(cell) not in types.StringTypes:
            cell = str(cell)
        return cell

    def isContainer(self, row):
        self._dataLock.acquire()
        try:
            if row >=0 and row < len (self._rows):
                return isinstance(self._rows[row], elementType)
        finally:
            self._dataLock.release()
        return 0

    def isContainerEmpty(self, row):
        self._dataLock.acquire()
        try:
            if row >=0 and row < len (self._rows):
                node = self._rows[row]
                return isinstance(node, elementType) and \
                        len(node) == 0 and \
                        (not self._showDetails or not node.attrib)
        finally:
            self._dataLock.release()
        return 1

    def isContainerOpen(self, row):
        self._dataLock.acquire()
        try:
            if row >=0 and row < len (self._rows):
                return self._nodeIsOpen.get(getScopedName(self.ET, self._rows[row]), 0)
        finally:
            self._dataLock.release()
        return 0

    def getParentIndex(self, index):
        try:
            self._dataLock.acquire()
            try:
                node = self._rows[index]
                if not isinstance(node, elementType):
                    parent = node[2]
                else:
                    parent = self.ET.nodemap[node]
                return self._rows.index(parent)
            finally:
                self._dataLock.release()
        except ValueError, e:
            pass
        return -1

    def hasNextSibling(self, index, afterIndex):
        try:
            self._dataLock.acquire()
            try:
                if not isinstance(self._rows[index], elementType):
                    if index+1 < len(self._rows) and \
                       not isinstance(self._rows[index+1], elementType):
                        # another attribute, so use, a sibling
                        return 1
                    # no more attributes, so, if the element has children,
                    # we have a sibling
                    if self._rows[index][2]:
                        return 1
                    return 0
                parent = self.ET.nodemap[self._rows[index]]
                children = list(parent)
                me = children.index(self._rows[index])
                nextSibling = children[me+1]
                if self._rows.index(nextSibling) > afterIndex:
                    return 1
            finally:
                self._dataLock.release()
        except (IndexError, ValueError), e:
            pass
        return 0

    def getLevel(self, index):
        self._dataLock.acquire()
        l = 0
        try:
            if not isinstance(self._rows[index], elementType):
                l = 1
                # an attribute, go back in the rows until we find an element
                while index > 0 and not isinstance(self._rows[index], elementType):
                    index -= 1
                
            node = self._rows[index]
            if node in self.ET.nodemap:
                parent = self.ET.nodemap[node]
                while parent:
                    l += 1
                    parent = self.ET.nodemap[parent]
        finally:
            self._dataLock.release()
        return l

    def setTree(self, tree):
        self._tree = tree


    def set_filterString(self, filterString):
        selectedScopedName = None
        if not filterString:
            # want to keep selection after refresh, as well as make sure that
            # node is open
            self._dataLock.acquire()
            try:
                try:
                    selectedScopedName = getScopedName(self.ET, self._rows[self.selection.currentIndex])
                except IndexError, e:
                    pass
            finally:
                self._dataLock.release()
        self._filterString = filterString
        self.refresh()
        retval = 0
        if selectedScopedName:
            retval = self.locateScopedName(selectedScopedName)
            self._dataLock.acquire()
            try:
                isopen = self._nodeIsOpen.get(getScopedName(self.ET, self._rows[retval]), 0)
            finally:
                self._dataLock.release()
            if not isopen:
                self.toggleOpenState(retval)
        if retval is not None:
            self.selection.select(retval);

    def set_showDetails(self, showDetails):
        # want to keep selection after refresh, as well as make sure that
        # node is open except if there's a filter string, because in that
        # case we want the filter string to override the selection
        if not self._filterString and self.selection.currentIndex < len(self._rows):
            self._dataLock.acquire()
            try:
                selectedScopedName = getScopedName(self.ET, self._rows[self.selection.currentIndex])
            finally:
                self._dataLock.release()
        else:
            selectedScopedName = None
        self._showDetails = showDetails
        retval = 0
        self.refresh()
        if selectedScopedName:
            retval = self.locateScopedName(selectedScopedName)
        if retval != -1:
            self.selection.select(retval);

    def get_showDetails(self):
        return self._showDetails

    def locateNode(self, line, col):
        target = self.ET.locateNode(line, col)
        # we need to expand each row whose node is an ancestor of target
        self._dataLock.acquire()
        try:
            i = 0
            while i < len(self._rows):
                node = self._rows[i]
                if node == target:
                    self.selection.select(i) # done!
                    self._tree.ensureRowIsVisible(i)
                else:
                    if (self.ET.isAncestorOf(node, target) and
                        not self._nodeIsOpen.get(getScopedName(self.ET, self._rows[i]), 0)):
                            self._dataLock.release()
                            self.toggleOpenState(i)
                            self._dataLock.acquire()
                i += 1
        finally:
            self._dataLock.release()
    
    def locateScopedName(self, scopedName):
        i = 0
        self._dataLock.acquire()
        try:
            while 1:
                if i >= len(self._rows):
                    return 0
                currentScopedName = getScopedName(self.ET, self._rows[i])
                if currentScopedName == scopedName:
                    return i
                if scopedName.startswith(currentScopedName):
                    if not self._nodeIsOpen.get(getScopedName(self.ET, self._rows[i]), 0):
                        self._dataLock.release()
                        self.toggleOpenState(i)
                        self._dataLock.acquire()
                i += 1
        finally:
            self._dataLock.release()
    
    def _yield_node_data(self, node, depth):
        if node.start and node.end:
            tag = ""
            if isinstance(node, elementType):
                tag = self.ET.qname(node.tag)
            start_line, start_col = node.start[:2]
            end_line, end_col = node.end[:2]
            yield tag, depth, start_line - 1, start_col - 1, end_line - 1, end_col + len(tag) + 1
        for child in node.getchildren():
            for child_data in self._yield_node_data(child, depth+1):
                yield child_data

    def get_node_regions(self):
        tags = []
        depths = []
        start_linenos = []
        start_cols = []
        end_linenos = []
        end_cols = []
        for node in self.ET.getRoots():
            for hit in self._yield_node_data(node, 0):
                tag, depth, start_line, start_col, end_line, end_col = hit
                tags.append(tag)
                depths.append(depth)
                start_linenos.append(start_line)
                start_cols.append(start_col)
                end_linenos.append(end_line)
                end_cols.append(end_col)
        return tags, depths, start_linenos, start_cols, end_linenos, end_cols

    def toggleOpenState(self, row):
        self._dataLock.acquire()
        try:
            scopedName = getScopedName(self.ET, self._rows[row])
            if scopedName not in self._nodeIsOpen:
                self._nodeIsOpen[scopedName] = 0
            self._nodeIsOpen[scopedName] = not self._nodeIsOpen[scopedName]
        finally:
            self._dataLock.release()

        # Must recalculate the rows.
        oldRowCount = len(self._rows)
        
        # XXX FIXME this is lame, we can just remove the children we want to remove
        rows = []
        self.refresh()

        #for rowF in rows:
        #    print rowF['node']
        self._tree.beginUpdateBatch()
        self._tree.rowCountChanged(0, len(self._rows)-oldRowCount)
        self._tree.invalidate()
        self._tree.endUpdateBatch()
        self.selection.currentIndex = row
        self.selection.select(row);        
        
    def getImageSrc(self, row, column):
        col = column.id
        if col != "domview-name":
            return None
        self._dataLock.acquire()
        try:
            if isinstance(self._rows[row], elementType):
                return "chrome://domviewer/skin/images/xml_element.png"
            else:
                # attribute
                return "chrome://domviewer/skin/images/xml_attribute.png"
        finally:
            self._dataLock.release()

    def getCellProperties(self, index, column, properties=None):
        if column.id != "domview-name":
            return

        # Mozilla 22+ does not have a properties argument.
        if properties is not None:
            return self.getCellPropertiesMoz21AndOlder(index, column, properties)

        properties = "primaryColumn"
        if not self._set:
            return properties
        #assert col.id == "codebrowser-tree-node"
        self._dataLock.acquire()
        try:
                node = self._rows[index]
                if node not in self._set:
                    properties += " disabled"
        finally:
            self._dataLock.release()
        return properties

    def getCellPropertiesMoz21AndOlder(self, index, column, properties):
        properties.AppendElement(self.atomService.getAtom("primaryColumn"));
        if not self._set:
            return
        #assert col.id == "codebrowser-tree-node"
        self._dataLock.acquire()
        try:
                node = self._rows[index]
                if node not in self._set:
                    properties.AppendElement(self._notMatchResultAtom)
        finally:
            self._dataLock.release()
