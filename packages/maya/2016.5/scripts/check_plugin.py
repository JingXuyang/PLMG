# -*- coding: utf-8 -*-

import sys
sys.path.append(r"Z:/bin/pltk/plugins/checking")
sys.path.append(r"Z:/bin/老外的PLTK/pltk/plugins/checking")

from qtlb import QtGui

import maya.cmds as cmds

class Tip(QtGui.QWidget):
    def __init__(self, message, parent=None):
        super(Tip, self).__init__(parent)

        QtGui.QMessageBox.information(self, "Tip", message, QtGui.QMessageBox.Yes)

def CheckUnknownPlugin():
    all_unknownPlug = cmds.unknownPlugin(q=True, l=True)
    if all_unknownPlug:
        for i in all_unknownPlug:
            try:
                cmds.unknownPlugin(i, r=1)
            except:
                pass
    cmds.dataStructure(removeAll=True)

def CheckAovs():
    if cmds.ls(type = "aiAOV"):
        for i in cmds.ls(type = "aiAOV"):
            cmds.delete(i)
        return 'OK'

def CheckUnknown():
    try:
        for i in cmds.ls(type=["unknown","unknownDag","unknownTransform"]):
            cmds.delete(i)
    except:
        pass

def CleanScene():
    del_exp = []
    for i in cmds.ls(type='expression'):
        if "xgm" in i:
            del_exp.append(i)
    comp = cmds.ls(type='deleteComponent')
    script_ls = cmds.ls(type='script')
    render_ls = cmds.ls(type="renderLayer")
    render_ls.remove("defaultRenderLayer")

    try:
        cmds.delete(comp)
        cmds.delete(del_exp) 
        cmds.delete(script_ls)
        cmds.delete(render_ls)
        cmds.dataStructure(removeAll=True)
    except:
        pass
        

def main():
    CheckUnknownPlugin()

    CheckAovs()

    CheckUnknown()

    CleanScene()

    a = Tip(u"Clean scene successful!")
    