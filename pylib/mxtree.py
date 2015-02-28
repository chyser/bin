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
class AbstractTreeNode(object):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self._tid = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getChildren(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getParent(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rmChild(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        pass

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def getText(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return ""


#-------------------------------------------------------------------------------
class TreeNode(AbstractTreeNode):
#-------------------------------------------------------------------------------
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, text, cxt=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        object.__init__(self)
        self.parent = None
        self.text = text
        self.cxt = cxt
        self.children = []

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddChildren(self, *node_list):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        for n in node_list:
            if n not in self.children:
                n.parent = self
                self.children.append(n)
        return self

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def rmChild(self, c):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.children.remove(c)
        c.parent = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def depthFirst(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = [self]
        for c in self.children:
            s.extend(c.depthFirst())
        return s

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __str__(self, ident=0):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        s = [('    '*ident) + self.text + ' <-- ' + (self.parent.text if self.parent is not None else 'None')]
        for c in self.children:
            s.append(c.__str__(ident+1))
        return '\n'.join(s)


#-------------------------------------------------------------------------------
class TreeCtrlMixin(object):
#-------------------------------------------------------------------------------
    """ A tree control with simplified usage
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, images = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """
            images - a list of image art provider names (see wx.ArtProvider)
        """

        object.__init__(self)
        self.root = None
        self.draggedItem = None

        if images is None:
            self.images = [wx.ART_FOLDER, wx.ART_FILE_OPEN, wx.ART_NORMAL_FILE]
        self.CreateImageList()

        self.Bind(wx.EVT_RIGHT_DOWN, self._OnRightDown)
        #self.Bind(wx.EVT_LEFT_DOWN, self._OnLeftDown)
        self.Bind(wx.EVT_TREE_ITEM_GETTOOLTIP, self._OnGetToolTip)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._OnSelect)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self._OnBeginDrag)
        self.Bind(wx.EVT_TREE_END_DRAG, self._OnEndDrag)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _AddRoot(self, node, nImg = 0, xImg = 1):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.root = node.tid = self.AddRoot(node.getText())
        self.SetItemPyData(self.root, node)

        if self.images is not None:
            self.SetItemImage(self.root, nImg, wx.TreeItemIcon_Normal)
            self.SetItemImage(self.root, xImg, wx.TreeItemIcon_Expanded)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _Add(self, parent, node, nImg=2, xImg=None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        tid = node.tid = self.AppendItem(parent, node.text)
        self.SetItemPyData(tid, node)

        if self.images:
            if xImg is None: xImg = nImg
            self.SetItemImage(tid, nImg, wx.TreeItemIcon_Normal)
            self.SetItemImage(tid, xImg, wx.TreeItemIcon_Expanded)
        return tid

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def AddNode(self, node, parent_tid = None):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if parent_tid == None:
            self._AddRoot(node)

        elif isinstance(parent_tid, TreeNode):
            self._Add(parent_tid._tid, node)
            node.parent.AddChildren(node)

        else:
            self._Add(parent_tid, node)
            self.GetItemPyData(parent_tid).AddChildren(node)

        for n in node.getChildren():
            self.AddNode(n, node)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def RmNode(self, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        parent = node.GetParent()
        if parent is not None:
            parent.rmChild(node)
            self.Delete(node._tid)
            node._tid = None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def CreateImageList(self):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        size = (16, 16)
        self.imageList = wx.ImageList(*size)
        for art in self.images:
            self.imageList.Add(wx.ArtProvider.GetBitmap(art, wx.ART_OTHER, size))
        self.AssignImageList(self.imageList)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _OnSelect(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        node = self.GetItemPyData(e.GetItem())
        self.OnSelect(e, node)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _OnRightDown(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        r, f = self.HitTest(e.GetPosition())
        node = self.GetItemPyData(r)
        self.OnRightDown(e, node)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _OnLeftDown(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        r, f = self.HitTest(e.GetPosition())
        node = self.GetItemPyData(r)
        self.OnLeftDown(e, node)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _OnGetToolTip(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        node = self.GetItemPyData(e.GetItem())
        val = self.OnGetToolTip(e, node)
        if val is not None:
            e.SetToolTip(val)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def Evt2Node(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return self.GetItemPyData(e.GetItem())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _OnBeginDrag(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        item = e.GetItem()
        if item != self.root:
            self.draggedItem = item
            e.Allow()

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def _OnEndDrag(self, e):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        #print "_OnEndDrag"
        if self.draggedItem is None:
            return

        src = self.GetItemPyData(self.draggedItem)
        print(src)

        dst = e.GetItem()
        if dst.IsOk():
            self.DoDrag(dst, src)

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnSelect(self, e, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print("OnSelect:", node.getText())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnRightDown(self, e, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print("RightDown:", node.getText())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnLeftDown(self, e, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        print("LeftDown:", node.getText())

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def OnGetToolTip(self, e, node):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        return None

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def DoDrag(self, dst, src):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        self.RmNode(src)
        self.AddNode(src, dst)


#-------------------------------------------------------------------------------
class TreeCtrl(TreeCtrlMixin, wx.TreeCtrl):
#-------------------------------------------------------------------------------
    """ A tree control with simplified usage
    """

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def __init__(self, parent, images = None, **kwds):
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        """
            images - a list of image art provider names (see wx.ArtProvider)
        """
        if 'id' not in kwds:
            kwds['id'] = -1

        wx.TreeCtrl.__init__(self, parent, **kwds)
        TreeCtrlMixin.__init__(self, parent, images)

        self.root = None



#-------------------------------------------------------------------------------
def __test__():
#-------------------------------------------------------------------------------
    """
    used for automated module testing. see L{tester}
    """
    import pylib.tester as tester
    return 0

#-------------------------------------------------------------------------------
if __name__ == "__main__":
#-------------------------------------------------------------------------------
    import pylib.osscripts as oss

    args, opts = oss.gopt(oss.argv[1:], [], [], __test__.__doc__)



    res = not __test__()
    oss.exit(res)


