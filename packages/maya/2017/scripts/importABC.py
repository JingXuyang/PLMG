# -*- coding: utf-8 -*-
import maya.mel as mel
import maya.cmds as cmds
import plcr
import dbif
from PySide import QtCore
from PySide import QtGui
import sys
sys.path.append("C:/cgteamwork/bin/base")
import cgtw

def Arnold():
    a = dbif._cgteamwork.CGTeamwork()
    data_task = plcr.getTaskFromEnv()
    data_base = a.getProjectDatabase(data_task['project'])
    t_tw = cgtw.tw()
    if data_base:
        model = data_task['pipeline_type']
        t_task_module = t_tw.task_module(str(data_base), str(model), [data_task['task_id']])
        cg_time = t_task_module.get(['shot.frame'])[0]["shot.frame"]
    start_f = cmds.playbackOptions(q=1, ast=1)
    end_f = cmds.playbackOptions(q=1, aet=1)
    firstFrame = 1001
    lastFrame = firstFrame+int(cg_time)-1
    
    cmds.loadPlugin("mtoa")
    cmds.setAttr("defaultRenderGlobals.currentRenderer",'arnold',type="string")
    
    cmds.setAttr("defaultRenderGlobals.imageFilePrefix", "<Scene>/<RenderLayer>/<RenderLayer>", type='string')
    cmds.setAttr('defaultRenderGlobals.animation',1)
    allCamera = cmds.ls(type='camera') 
    for cm in allCamera:
        if "cam" not in cm:
            camName = cmds.listRelatives(cm, ap=True)[0]
            cmds.setAttr("%s.renderable" % cm, 0)
        else:
            cmds.setAttr("%s.renderable" % cm, 1)
    
    cmds.setAttr("defaultResolution.width",1998)
    cmds.setAttr("defaultResolution.height",1080)
    cmds.setAttr("defaultResolution.imageSizeUnits",0)
    
    cmds.setAttr('defaultRenderGlobals.startFrame',int(firstFrame))
    cmds.setAttr('defaultRenderGlobals.endFrame',int(lastFrame))

class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        import maya.cmds as cmds
        import os
        
        super(Window,self).__init__(parent)
        self.resize(350,100)
        
        self.label1 = QtGui.QLabel(u"导入ABC: ")
        self.abcPath = QtGui.QLineEdit()
        self.abcPath.setMinimumWidth(100)
        self.open = QtGui.QPushButton(u"...")
        self.export_but = QtGui.QPushButton(u"导入")
        self.export_but.setMaximumWidth(90)
        
        self.lay = QtGui.QGridLayout(self)
        self.lay.addWidget(self.label1,0,0)
        self.lay.addWidget(self.abcPath,0,1)
        self.lay.addWidget(self.open,0,2)
        self.lay.addWidget(self.export_but,1,1)
        self.setLayout(self.lay)
        
        t_tw = cgtw.tw()
        data_task = plcr.getTaskFromEnv()
        self.par_path = "Z:/LongGong/sequences/"+data_task['sequence']+"/"+data_task['shot']+"/shotFinaling/outputCache"

        
        self.open.clicked.connect(self.openfile)
        self.export_but.clicked.connect(self.run)
        
    def openfile(self):
        # data_task = plcr.getTaskFromEnv()
        # path = "Z:/LongGong/sequences/"+data_task['sequence']+"/"+data_task['shot']+"/shotFinaling/approved/scenes"
        if "Shot" in self.par_path:
            file_path = QtGui.QFileDialog.getOpenFileName(self,"Import ABC",self.par_path,"ABC Files (*.abc)")
        else:
            file_path = QtGui.QFileDialog.getOpenFileName(self,"Import ABC","./","ABC Files (*.abc)")
        self.abcPath.setText(file_path[0])
        
    def run(self):
        path = self.abcPath.text()
        print path
        print 'AbcImport -mode import "%s";' % path
        mel.eval('AbcImport -mode import "%s";' % path)
        
        a = dbif._cgteamwork.CGTeamwork()
        data_task = plcr.getTaskFromEnv()
        data_base = a.getProjectDatabase(data_task['project'])
        t_tw = cgtw.tw()
        if data_base:
            model = data_task['pipeline_type']
            t_task_module = t_tw.task_module(str(data_base), str(model), [data_task['task_id']])
            cg_time = t_task_module.get(['shot.frame'])[0]["shot.frame"]
        start_f = cmds.playbackOptions(q=1, ast=1)
        end_f = cmds.playbackOptions(q=1, aet=1)
        firstFrame = 1001
        lastFrame = firstFrame+int(cg_time)-1
        cmds.playbackOptions(minTime=firstFrame, maxTime=lastFrame,animationStartTime=firstFrame,animationEndTime=lastFrame)
        
        Arnold()
        
        cmds.inViewMessage(amg=u'导 入 成 功', pos='midCenter', fts=20, bkc=0x00FF1010, fade=True)
        