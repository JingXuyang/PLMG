import maya.cmds as cmds

obg_list = cmds.ls(sl=1,dag=1,o=1,s=1)
for obg in obg_list:
    cmds.setAttr (obg+".aiOpaque", 0)