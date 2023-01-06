import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
from Log.CoboLoggers import getLogger
logger = getLogger()

class returnObjectUnderMouse():
    def __init__(self):
        self.ctx = 'returnObjectUnderMouse'
        self.object_list = []
        self.run()

    def onRelease(self):
        cmds.setToolTo('selectSuperContext')
        cmds.selectMode(object=True)
        if cmds.draggerContext(self.ctx, exists=True):
            cmds.deleteUI(self.ctx)


    def onPress(self):
        """
        Fancy return option
        :return:
        """
        vpX, vpY, _ = cmds.draggerContext(self.ctx, query=True, anchorPoint=True)
        logger.info(vpX, vpY)

        pos = om.MPoint()
        dir = om.MVector()
        hitpoint = om.MFloatPoint()
        omui.M3dView().active3dView().viewToWorld(int(vpX), int(vpY), pos, dir)
        pos2 = om.MFloatPoint(pos.x, pos.y, pos.z)
        for mesh in cmds.ls():
            selectionList = om.MSelectionList()
            selectionList.add(mesh)
            dagPath = om.MDagPath()
            selectionList.getDagPath(0, dagPath)
            fnMesh = om.MFnMesh(dagPath)
            intersection = fnMesh.closestIntersection(
                om.MFloatPoint(pos2),
                om.MFloatVector(dir),
                None,
                None,
                False,
                om.MSpace.kWorld,
                99999,
                False,
                None,
                hitpoint,
                None,
                None,
                None,
                None,
                None)
            if intersection:
                x = hitpoint.x
                y = hitpoint.y
                z = hitpoint.z
                print(mesh)
                cmds.spaceLocator(p=(x, y, z))

    def simpleHitTest(self):
        """
        Taken from google :)
        def object_under_cursor():
            pos = QtGui.QCursor.pos()
            widget = QtGui.qApp.widgetAt(pos)
            relpos = widget.mapFromGlobal(pos)

            panel = cmds.getPanel(underPointer=True) or ""

            if not "modelPanel" in panel:
                return

            return (cmds.hitTest(panel, relpos.x(), relpos.y()) or [None])[0]
        """
        from PySide2 import QtGui,QtWidgets
        pos = QtGui.QCursor.pos()

        widget = QtWidgets.QApplication.widgetAt(pos)
        relpos = widget.mapFromGlobal(pos)
        panel =  cmds.getPanel(underPointer=True) or ""
        if not "modelPanel" in panel:
            return
        logger.info("selection: %s" % cmds.ls(preSelectHilite=True))
        logger.info("selection: %s" % cmds.ls(hl=True))
        result = cmds.hitTest(panel, relpos.x(), relpos.y())
        if result:
            self.object_list.extend(result)
            print(result)

    def getObjectList(self):
        return self.object_list

    def run(self):
        if cmds.draggerContext(self.ctx, exists=True):
            cmds.deleteUI(self.ctx)
        cmds.draggerContext(self.ctx, pressCommand=self.simpleHitTest, name=self.ctx, cursor='crossHair', releaseCommand=self.onRelease)
        cmds.setToolTo(self.ctx)