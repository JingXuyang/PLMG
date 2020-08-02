# -*- coding: utf-8 -*-
from PySide import QtCore
from PySide import QtGui
import pymel.core as pm
import maya.cmds as cmds
import os
import glob
import shutil
import plcr
import dbif
import sys
sys.path.append("C:/cgteamwork/bin/base")
import cgtw

def getAni():        
    con = cmds.ls(rf=1)
    int_pos = {}
    fin_pos = {}
    start_f = '1000'
    cmds.currentTime(start_f)
    for i in con:
        try:
            if cmds.referenceQuery(i,nodes=True) != None:
                int_pos[cmds.referenceQuery(i,nodes=True)[0]] = cmds.objectCenter(cmds.referenceQuery(i,nodes=True)[0],gl=1)
        except:
            pass
    end_f = cmds.playbackOptions(q=1, aet=1)
    cmds.currentTime(end_f)
    for i in con:
        try:
            if cmds.referenceQuery(i,nodes=True) != None:
                fin_pos[cmds.referenceQuery(i,nodes=True)[0]] = cmds.objectCenter(cmds.referenceQuery(i,nodes=True)[0],gl=1)
        except:
            pass
    dic = {}   
    for k in int_pos:    
        for j in fin_pos:
            if k==j and int_pos[k] != fin_pos[j]:
                dic[k] = int_pos[k]
    getObj = []           
    for key in dic:
        getObj.append(key)
    return getObj

def cameraList():
    allCamera = cmds.ls(cameras=True, long=True)
    defaultCamera = ['|persp','|front','|side','|top','|back', '|left', '|right', '|bottom']
    cameraList = []
    for i in allCamera:
        cameraName = cmds.listRelatives(i, allParents=True, fullPath=True)[0]
        if cameraName not in defaultCamera:
            if cameraName.split("|")[0] == "":
                cameraList.append(cameraName.split("|")[1])
            else:
                cameraList.append(cameraName.split("|")[0])
    return cameraList
    
def versionUp(path):
    dir = os.path.dirname(path)
    basename = os.path.basename(path).split(".")[0]
    all = []
    for i in os.listdir(dir):
        if ".abc" in i:
            if basename.split("_")[3] in i:
                all.append(i)
    newname = os.path.basename(cmds.file(q=1,sceneName=1)).split(".")[0].split("_")
    newname.pop()
    new_name = "_".join(newname)
    return new_name+"_v"+str(len(all)+1).zfill(3)+".abc"

class ExportAbc(QtGui.QDialog):
    def __init__(self, parent=None):
        import maya.cmds as cmds
        import os
        super(ExportAbc,self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(500,300)
        
        self.label1 = QtGui.QLabel(u"已选择的动画: ")
        self.sel = QtGui.QListWidget()
        self.sel.addItems(getAni())
        self.sel.addItems(cameraList())
        self.but1 = QtGui.QPushButton(u"载入所选")
        lay = QtGui.QVBoxLayout()
        lay.addWidget(self.label1)
        lay.addWidget(self.sel)
        lay.addWidget(self.but1)
        
        self.label2 = QtGui.QLabel(u"需导出的道具(选中最高层级): ")
        self.un_sel = QtGui.QListWidget()
        self.but2 = QtGui.QPushButton(u"导出所选")
        lay1 = QtGui.QVBoxLayout()
        lay1.addWidget(self.label2)
        lay1.addWidget(self.un_sel)
        lay1.addWidget(self.but2)
        
        H_lay = QtGui.QHBoxLayout()
        H_lay.addLayout(lay)
        H_lay.addLayout(lay1)
        
        self.setLayout(H_lay)
        
        self.but1.clicked.connect(self.addSel)
        self.but2.clicked.connect(self.export)
        
    def addSel(self):
        self.un_sel.clear()
        self.list = cmds.ls(sl=1)
        self.un_sel.addItems(self.list)
        
    def export(self):
        start_f = cmds.playbackOptions(q=1, ast=1)
        end_f = cmds.playbackOptions(q=1, aet=1)
        args = '-frameRange %s %s ' % (start_f, end_f)
        args = args+' -ro -uvWrite -writeColorSets -worldSpace -writeVisibility -writeUVSets -eulerFilter -dataFormat ogawa '
        #print "getAni():",getAni()
        aniList = getAni()
        for i in aniList:
            args += '-root %s ' % i
            
        if len(cmds.ls(sl=1)) != 0:
            for j in cmds.ls(sl=1,long=True):
                if j.split('|')[1] not in aniList:
                    args += '-root %s ' % j
                
        print cameraList()
        if len(cameraList()) != 0:
            for i in cameraList():
                args += '-root %s ' % i
        
        t_tw = cgtw.tw()
        data_task = plcr.getTaskFromEnv()

        # folder_name = os.path.basename(cmds.file(q=1,sceneName=1)).split(".")[0]
        # self.path1 = "Z:/LongGong/sequences/"+data_task['sequence']+"/"+data_task['shot']+"/Cache/shotFinaling/"+folder_name+"/"+os.path.basename(cmds.file(q=1,sceneName=1)).split(".")[0]+".abc"
        # if os.path.exists("Z:/LongGong/sequences/"+data_task['sequence']+"/"+data_task['shot']+"/Cache/shotFinaling/"+folder_name):
            # pass
        # else:
            # os.makedirs("Z:/LongGong/sequences/"+data_task['sequence']+"/"+data_task['shot']+"/Cache/shotFinaling/"+folder_name)
        # name = versionUp(self.path1)
        # path = os.path.dirname(self.path1)+"/"+name
        
        path1 = "Z:/LongGong/sequences/"+data_task['sequence']+"/"+data_task['shot']+"/Cache/shotFinaling/work"
        if os.path.exists(path1):
            pass
        else:
            os.makedirs(path1)
        path = path1+"/"+data_task['sequence']+"_"+data_task['shot']+"_SF.abc"
        
        args += "-file '%s' " % (path)

        plugin_list = cmds.pluginInfo(query=True, listPlugins=True)

        if 'mtoa' in plugin_list:
            args += ' -attr aiSubdivType -attr aiSubdivIterations '
        if 'AbcExport' not in plugin_list:
            cmds.loadPlugin("AbcExport")

        cmd = 'AbcExport -j "%s";' % args
        #print cmd
        
        for i in cmds.ls("*.showProxyEyes", r=1):
            cmds.cutKey(i, clear=True)
            cmds.setAttr(i, 0)
        

        print "cmd:",cmd
        pm.mel.eval(cmd)
        
        # copy to history ,and version up
        historyPath = '%s/history'%(path1)
        if not os.path.exists(historyPath):
            os.makedirs(historyPath)
        
        hisFile = "{path}/{sequence}_{shot}_SF_v???.abc".format( path=historyPath,
                                                                sequence=data_task['sequence'],
                                                                shot = data_task['shot'])
        versionList = glob.glob(hisFile)
        if versionList:
            f = max(versionList)
            f = os.path.basename(f).split('.')[0]
            version = f.split('_')[-1]
            version = 'v'+str(int(version[1:])+1).zfill(3)
            
        else:
            version = 'v001'
        print "version:",version
        hisFilePath = "{path}/{sequence}_{shot}_SF_{version}.abc".format( path=historyPath,
                                                                    sequence=data_task['sequence'],
                                                                    shot = data_task['shot'],
                                                                    version=version)
        shutil.copyfile(path,hisFilePath)
        
        
        cmds.inViewMessage(amg=u'导 出 成 功', pos='midCenter', fts=20, bkc=0x00FF1010, fade=True)
        
        
        
        
        
