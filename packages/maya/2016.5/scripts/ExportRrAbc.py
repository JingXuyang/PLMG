# -*- coding:utf-8 -*-

from PySide import QtCore
from PySide import QtGui
import pymel.core as pm
import maya.cmds as cmds
import json
import os
# from collection import 
import plcr
import dbif
import sys
sys.path.append("C:/cgteamwork/bin/base")
import cgtw


def getCamera():
    import re
    import maya.cmds as cmds
    
    allCam = cmds.listCameras()
    
    camList = []
    for cam in allCam:
        c = re.findall('cam_\d{3}_\d{3}',cam)
        if c:
            cam = c[0]
            longname= cmds.ls(cam+'*',long=True)
            camGroup = longname[0].split('|')[1]
            if camGroup not in camList:
                camList.append(camGroup)
            
    return camList
    
def cameraList():
    allCamera = cmds.ls(cameras=True, long=True)
    defaultCamera = ['|persp','|front','|side','|top','|back', '|left', '|right', '|bottom']
    cameraList = []
    for i in allCamera:
        cameraName = cmds.listRelatives(i, allParents=True, fullPath=True)[0]
        if cameraName not in defaultCamera:
            cameraList.append(cameraName)
    return cameraList
    
def getAni():
    con = cmds.ls(rf=1)
    int_pos = {}
    fin_pos = {}
    start_f = cmds.playbackOptions(q=1, ast=1)
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
    #print "getObj:",getObj
    camList = cameraList()
    for c in camList:
        if c not in getObj:
            getObj.append(c)
            
        # remove repeat grp
        grp = c.split('|')[1]
        if grp in getObj:
            getObj.remove(grp)
            
    print "getObj:",getObj
    return getObj

    
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
    new_name = "_".join(set(newname))
    return new_name+"_v"+str(len(all)+1).zfill(3)+".abc"

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        import maya.cmds as cmds
        import os
        super(Window, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(400,500)

        self.but1 = QtGui.QPushButton(u"Load Outliner")
        self.but1.setMaximumWidth(80)
        self.but2 = QtGui.QPushButton(u"Export selection")
        self.but2.setMaximumWidth(85)
        self.but3 = QtGui.QPushButton(u"Del selection")
        self.but3.setMaximumWidth(85)
        self.sel = QtGui.QTreeWidget()
        self.sel.setHeaderHidden(True)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
        self.sel.setPalette(palette)
        self.all = QtGui.QTreeWidgetItem(self.sel)
        self.all.setText(0, "All")
        self.all.setCheckState(0, QtCore.Qt.Unchecked)
        self.sel.expandAll()
        
        self.ani_ls = getAni()
        # Ìí¼ÓÈËÎï
        for i in self.ani_ls:
            root = QtGui.QTreeWidgetItem(self.all)
            root.setText(0, i)
            root.setCheckState(0, QtCore.Qt.Unchecked)
        # self.sel.addItems(self.ani_ls)
        temp = []
        
        # Ìí¼ÓÏà»ú
        for i in temp:
            root = QtGui.QTreeWidgetItem(self.all)
            root.setText(0, i)
            root.setCheckState(0, QtCore.Qt.Unchecked)
        
        
        # add select shot widget
        import selectShotWidget
        reload(selectShotWidget)
        shotWgt = selectShotWidget.SelectShotStepWidget()
        
        
        self.checkBox = QtGui.QCheckBox('Other')
        #self.checkBox.setCheckState(QtCore.Qt.Checked)
        
        
        lay1 = QtGui.QHBoxLayout()
        lay1.addWidget(self.but1)
        lay1.addStretch(1)
        #lay1.addWidget(self.checkBox)
        lay1.addWidget(self.but2)
        
        lay = QtGui.QVBoxLayout()
        lay.addWidget(shotWgt)
        lay.addWidget(self.but3)
        lay.addWidget(self.sel)
        lay.addLayout(lay1)

        H_lay = QtGui.QHBoxLayout()
        H_lay.addLayout(lay)

        self.setLayout(H_lay)
        
        self.but1.clicked.connect(self.addSel)
        self.but2.clicked.connect(self.export)
        self.but3.clicked.connect(self.delSel)
        self.sel.itemClicked.connect(self.handleChanged)
        
    def addSel(self):
        old = []
        for j in range(self.all.childCount()):
            old.append(self.all.child(j).text(0))
        
        list = cmds.ls(sl=1)
        for i in list:
            if i not in old:
                root = QtGui.QTreeWidgetItem(self.all)
                root.setText(0, i)
                root.setCheckState(0, QtCore.Qt.Unchecked)
    
    def delSel(self):
        self.all.removeChild(self.sel.currentItem())
    
    def handleChanged(self, item, column):
        count = item.childCount()
        # ¸ù½Úµã¹´Ñ¡, µ¼³öËùÓÐ×Ó½Úµã
        if count:
            if item.checkState(column) == QtCore.Qt.Checked:
                for i in range(count):
                    item.child(i).setCheckState(0, QtCore.Qt.Checked)
            if item.checkState(column) == QtCore.Qt.Unchecked:
                for i in range(count):
                    item.child(i).setCheckState(0, QtCore.Qt.Unchecked)
        else:
            if item.checkState(column) == QtCore.Qt.Unchecked:
                item.parent().setCheckState(0, QtCore.Qt.Unchecked)
    
    def run(self, path):
        t_tw = cgtw.tw()
        data_task = plcr.getTaskFromEnv()
        a = dbif._cgteamwork.CGTeamwork()
        data_base = a.getProjectDatabase(data_task['project'])

        t_module      = data_task["pipeline_type"]  #Ä£¿é
        t_module_type = "task"  #Ä£¿éÀàÐÍ
        t_db          = data_base  #Êý¾Ý¿â
        t_local_path = path  #ÒªÉÏ´«ÎÄ¼þ.mbÂ·¾¶

        #»ñÈ¡ÎÄ¼þ¿òÊý¾Ý
        filename=os.path.basename( t_local_path )
        task_id_list = data_task["task_id"]
        print task_id_list
                                          
        try:
            result = []
            #ÉÏ´«.mbÎÄ¼þ
            t_path=os.path.dirname( t_local_path )
            t_upload_list = [ {"sou":t_local_path, "des":unicode(os.path.splitdrive(t_path)[1]+"/"+filename).replace("\\", "/")} ]
            
            t_dic={'name':filename, 'task': [{"action":"upload", 
                                               "is_contine":True, 
                                               "data_list":t_upload_list, 
                                               "db":t_db, 
                                               "module":t_module, 
                                               "module_type":t_module_type, 
                                               "task_id":task_id_list[0], 
                                               "version_id":""}
                                              ]}
            a = t_tw.local_con._send("queue_widget","add_task", {"task_data":t_dic}, "send")
            result.append(a)
        except:
            pass
        
        print "Upload Successful !"
    
    def export(self):
        print "Start ..."
        
        start_f = cmds.playbackOptions(q=1, ast=1)
        end_f = cmds.playbackOptions(q=1, aet=1)
        #print [start_f,end_f]
        
        args = '-frameRange %s %s ' % (start_f-1, end_f)
        args = args+' -ro -uvWrite -writeColorSets -worldSpace -writeVisibility -eulerFilter -writeUVSets -dataFormat ogawa '
        #print "000"
        # ´æ´¢ÐèÒªµ¼³öµÄ³¤Ãû
        dow_ls = []
        # ±éÀúTreeWidet
        iterator = QtGui.QTreeWidgetItemIterator(self.sel)
        #print 111
        while iterator.value():
            # ¸ù½Úµã¹´Ñ¡, µ¼³öËùÓÐ×Ó½Úµã
            if iterator.value().childCount() and iterator.value().checkState(0) == QtCore.Qt.Checked:
                for i in range(iterator.value().childCount()):
                    name = iterator.value().child(i).text(0)
                    dow_ls.append(name)
                    
            # ¸ù½ÚµãÎ´¹´Ñ¡£¬µ¼³öÒÑ¾­¹´ÉÏµÄ×Ó½Úµã
            if iterator.value().childCount() and iterator.value().checkState(0) == QtCore.Qt.Unchecked:
                for i in range(iterator.value().childCount()):
                    if iterator.value().child(i).checkState(0) == QtCore.Qt.Checked:
                        name = iterator.value().child(i).text(0)
                        dow_ls.append(name)
            iterator += 1
        
        #print 222
        for i in dow_ls:
            args += '-root %s ' % i
        #print 333
        data_task = plcr.getTaskFromEnv()

        folder_name = os.path.basename(cmds.file(q=1,sceneName=1)).split(".")[0]
        
        fileName = "%s_%s_SF.abc"%(data_task['sequence'],data_task['shot'])

        path1 = 'Z:/LongGong/sequences/{seq}/{shot}/Cache/shotFinaling/work/{fileName}'.format( seq=data_task['sequence'],
                                                                                                shot=data_task['shot'],
                                                                                                fileName=fileName)
        
        #path1 = "Z:/LongGong/sequences/"+data_task['sequence']+"/"+data_task['shot']+"/animation/outputCache/"+folder_name+"/"+os.path.basename(cmds.file(q=1,sceneName=1)).split(".")[0]+".abc"
        #print "path100:",path1
        if os.path.exists(os.path.dirname(path1)):
            pass
        else:
            os.makedirs(os.path.dirname(path1))
        # name = versionUp(path1)
        path = path1
        
        if self.checkBox.isChecked():
            pass
            #l = os.path.splitext(path)
            #path = "%s_other%s"%(l[0],l[1])
            
        
        args += '-file %s' % (path)
        plugin_list = cmds.pluginInfo(query=True, listPlugins=True)
        if 'mtoa' in plugin_list:
            args += ' -attr aiSubdivType -attr aiSubdivIterations'
        if 'AbcExport' not in plugin_list:
            cmds.loadPlugin("AbcExport")
        cmd = 'AbcExport -j "%s";' % args
        print "cmd:",cmd
        #return 
        try:
            pm.mel.eval(cmd)
        except:
            pass
            # cmds.inViewMessage(amg=u"Please check camera's name, may be there are the same camera", pos='midCenter', fts=30, bkc=0x00FF1010, fade=True)
        
        self.run(path)
        
        QtGui.QMessageBox.information(self, "Information", 'Export ABC successful !')


# win = Window()
# win.show()
        