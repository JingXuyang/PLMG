import maya.cmds as cmds

obg_list = cmds.ls(sl=1,dag=1,o=1,s=1)
for obg in obg_list:
    cmds.setAttr (obg+".aiSubdivType", 1)
    cmds.setAttr (obg+".aiSubdivIterations", 1)

for i in cmds.ls("*eyeBall_Shape", r=1):
    cmds.setAttr(i+".osdFvarBoundary", 0)