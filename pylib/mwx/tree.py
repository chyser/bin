#!/usr/bin/env python
"""
Library:

"""

from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import

import wx


#-------------------------------------------------------------------------------
class Tree(wx.TreeCtrl):
#-------------------------------------------------------------------------------
    """ Class for a tree control
    """
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, style=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        wx.TreeCtrl.__init__(self, parent, -1, style=style | wx.TR_HAS_BUTTONS)
        self.rootTid = None
        self.tidMap = {}

        self.CreateImageList()

        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self._onRightDown)
        self.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self.OnGetToolTip)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._onSelect)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def reset(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.tidMap = {}
        self.DeleteAllItems()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CreateImageList(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ create the imagelist needed for nodes and leaves of the tree. default
            is for a file manager.
        """
        size = (16, 16)
        self.imageList = wx.ImageList(*size)
        for art in wx.ART_FOLDER, wx.ART_FILE_OPEN, wx.ART_NORMAL_FILE:
            self.imageList.Add(wx.ArtProvider.GetBitmap(art, wx.ART_OTHER, size))
        self.AssignImageList(self.imageList)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnCompareItems(self, tid1, tid2):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.cmp(self.GetItemPyData(tid1), self.GetItemPyData(tid2))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def cmp(self, node1, node2):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print('cmp() called', node1, node2)
        if node1.teLabel == node2.teLabel:
            return 0
        if node1.teLabel < node2.teLabel:
            return -1
        return 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getNode(self, event):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        tid = event.GetItem()
        if not tid.IsOk():
            return None
        return self.GetItemPyData(event.GetItem())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _onRightDown(self, event):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.OnRightDown(self.getNode(event))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _onSelect(self, event):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ called in response to 'selection' (dclick)
        """
        node = self.getNode(event)
        parentTid = self.GetItemParent(self.tidMap[node])
        res = self.OnSelect(node)
        self.expand(parentTid)
        return res

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnGetToolTip(self, event):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        node = self.getNode(event)
        tt = self.nodeGetToolTip(node)
        if tt is not None:
            event.SetToolTip(tt)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def sort(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.SortChildren(self.rootTid)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddRoot(self, rootNode):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ make rootNode the root node.
            return rootNode on success else None
        """
        self.reset()
        self.rootTid = wx.TreeCtrl.AddRoot(self, self.nodeGetLabel(rootNode))
        nIdx, eIdx = self.nodeGetImageListIdx(rootNode)
        if nIdx is not None:
            self.SetItemImage(self.rootTid, nIdx, wx.TreeItemIcon_Normal)
        if eIdx is not None:
            self.SetItemImage(self.rootTid, eIdx, wx.TreeItemIcon_Expanded)
        self.SetItemPyData(self.rootTid, rootNode)
        self.tidMap[rootNode] = self.rootTid

        for childNode in self.nodeGetChildren(rootNode):
            self.AddNode(childNode, self.rootTid)

        return rootNode

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddNode(self, node, subRoot=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ add node to root is subRoot is None else to subRoot. subRoot can be
            a previosuly added node or the node's Tid.
            returns the node on success else None
        """
        rtid = self.getTid(subRoot)

        tid = self.AppendItem(rtid, self.nodeGetLabel(node))
        nIdx, eIdx = self.nodeGetImageListIdx(node)
        if nIdx is not None:
            self.SetItemImage(tid, nIdx, wx.TreeItemIcon_Normal)
        if eIdx is not None:
            self.SetItemImage(tid, eIdx, wx.TreeItemIcon_Expanded)
        self.SetItemPyData(tid, node)
        self.tidMap[node] = tid

        for childNode in self.nodeGetChildren(node):
            self.AddNode(childNode, tid)

        return node

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getTid(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ given a node, tid or None return the node's tid, the tid or root's tid
        """
        if node is None:
            assert self.rootTid is not None
            return self.rootTid
        if node in self.tidMap:
            return self.tidMap[node]
        return node

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getRootChildrenTids(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if self.rootTid is None:
            return []

        child, token = self.GetFirstChild(self.rootTid)
        if not child.IsOk():
            return []

        ary = [child]

        while 1:
            child, token = self.GetNextChild(self.rootTid, token)
            if not child.IsOk():
                break
            ary.append(child)

        return ary

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getExpanded(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        aset = set()
        for tid in self.getRootChildrenTids():
            if self.IsExpanded(tid):
                aset.add(self.GetItemText(tid))
        return aset

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expand(self, node=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ expand the tree below node. If node is None, expand entire tree.
        """
        self.Expand(self.getTid(node))

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def expandLabels(self, lbls):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if isinstance(lbls, unicode):
            lbls = set([lbls])

        for tid in self.getRootChildrenTids():
            if self.GetItemText(tid) in lbls:
                self.Expand(tid)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnSelect(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ called when tree node is double clicked
        """
        return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnRightDown(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ called when right button is pressed on a tree node
        """
        return

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nodeGetLabel(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return the label from the node
            override if node class is not a TreeElem
        """
        return node.teLabel

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nodeGetToolTip(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return the tooltip from the node
            override if node class is not a TreeElem
        """
        return node.teToolTip

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nodeGetChildren(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return the list of children of the parent node
            override if node class is not a TreeElem
        """
        return node.teGetChildren()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nodeGetImageListIdx(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ return a tuple of the imagelist indexes for this node. The first
            element is the index for non-expanded, the second is for expanded
        """
        return node.teGetImgLstIdx()


#-------------------------------------------------------------------------------
class DragTree(Tree):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, style=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        Tree.__init__(self, parent, style)
        self.dragTid = None

        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self._onBeginDrag)
        self.Bind(wx.EVT_TREE_END_DRAG, self._onEndDrag)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _onBeginDrag(self, event):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        event.Allow()
        self.dragTid = event.GetItem()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _onEndDrag(self, event):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        newParentTid = event.GetItem()

        if not newParentTid.IsOk() or newParentTid == self.dragTid:
            return

        newParent = self.GetItemPyData(newParentTid)

        oldParentTid = self.GetItemParent(self.dragTid)
        oldParent = self.GetItemPyData(oldParentTid)

        dragNode = self.GetItemPyData(self.dragTid)

        if self.nodeAddChild(newParent, dragNode):
            self.nodeDelChild(oldParent, dragNode)
            self.Delete(self.dragTid)
            self.AddNode(dragNode, newParentTid)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nodeDelChild(self, parentNode, childNode):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ delete the child node from the parent node
            override if node class is not a TreeElem
        """
        parentNode.teDelChild(childNode)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nodeAddChild(self, parentNode, childNode):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """ if allowed, add the child node to the parent node else return None
            override if node class is not a TreeElem
        """
        return parentNode.teAddChild(childNode)



#-------------------------------------------------------------------------------
class EditLabelTree(DragTree):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, style=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        DragTree.__init__(self, parent, style | wx.TR_EDIT_LABELS | wx.TR_FULL_ROW_HIGHLIGHT | wx.TR_NO_LINES)

        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self._onEndLabelEdit)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _onEndLabelEdit(self, event):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        node = self.getNode(event)
        self.nodeSetLabel(node, event.GetLabel())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnRightDown(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.EditLabel(self.tidMap[node])

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def nodeSetLabel(self, node, label):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print('nodeSetLabel: ' + label)
        node.teLabel = label


#-------------------------------------------------------------------------------
class TreeElem(object):
#-------------------------------------------------------------------------------
    """ Optional class that works with default Tree and DragTree
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, label, tooltip=None, nIdx=0, eIdx=1, cxt=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.teLabel = str(label)
        self.teToolTip = tooltip
        self.teCxt = cxt
        self.teChildren = []
        self.teNormalImageIdx = nIdx
        self.teExpandedImageIdx = eIdx

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.teLabel + ' ' + str(self.teToolTip)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def teGetImgLstIdx(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.teNormalImageIdx, self.teExpandedImageIdx

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def teDelChild(self, child):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        try:
            self.teChildren.remove(child)
        except ValueError:
            pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def teAddChild(self, child):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.teChildren.append(child)
        return child

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def teGetChildren(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.teChildren

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def teDump(self, indent=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = []
        s.append(('    ' * indent) + self.teLabel)

        for c in self.teChildren:
            s.append(c.teDump(indent+1))

        return '\n'.join(s)

#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """ used for automated module testing. see L{tester}
    """

    #import pylib.tester as tester
    return 0


#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss
    import pylib.mx as mx
    import random

    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)

    app = mx.SimpleTestApp('test app')

    t = EditLabelTree(app.win, wx.TR_MULTIPLE)

    root = TreeElem('root')
    for i in range(9, -1, -1):
        te = TreeElem('tag_%d' % i, 'toolTip_%d' % i)
        if random.random() < 0.4:
            te.teAddChild(TreeElem('test_%d' % i, 'test_tip_%d' % i))

        #t.AddNode(te)

        #if random.random() < 0.3:
        #    child = te.teAddChild(TreeElem('cool_%d' % i, 'cool_tip_%d' % i))
        #    t.AddNode(child, te)

        root.teAddChild(te)


    t.AddRoot(root)
    t.expand()
    t.sort()

    print(t.getRootChildrenTids())
    print(t.getExpanded())

    app.run()

    print(root.teDump())
    print(t.getExpanded())

    res = not __test__()
    oss.exit(res)


