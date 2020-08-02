# -*- coding: utf-8 -*-

from PySide import QtCore
from PySide import QtGui
import pymel.core as pm
import maya.cmds as cmds
import json
import os
# from collection import 
import plcr
# import dbif

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
            if k==j and int_pos[k] != fin_pos[j] and "prop" in k:
                dic[k] = int_pos[k]
    getObj = []           
    for key in dic:
        getObj.append(key)
    return getObj


def cameraList():
    allCamera = cmds.ls(assemblies=True)
    temp = []
    for i in allCamera:
        if "cam" in i or "Cam" in i:
            temp.append(i)
    return temp
        
class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(400,400)

        self.cmds = cmds
        
        self._UI()
    
    def _UI(self):
        self.myTree = QtGui.QTreeWidget(self)
        palette1 = QtGui.QPalette()
        palette1.setColor(self.backgroundRole(), QtGui.QColor(239, 232, 232))
        self.myTree.setPalette(palette1)
        self.myTree.setHeaderLabel("Char")
        temp = []
        for i in self.cmds.ls(assemblies=1):
            if "char" in i and "GRP"in i:
                temp.append(i)
        getSel = temp
        self.char_ls = {}
        self.getItem(getSel, self.char_ls)
        
        # 添加Item
        self.root = []
        for num, obj in enumerate(self.char_ls):
            self.root.append(obj)
            root = QtGui.QTreeWidgetItem(self.myTree)
            root.setText(0, obj)
            root.setCheckState(0, QtCore.Qt.Unchecked)
            for body in self.char_ls[obj]:
                if self.char_ls[obj][body][1] == "True": # 显示层级不隐藏的
                    child = QtGui.QTreeWidgetItem(root) 
                    child.setText(0, body)
                    child.setCheckState(0, QtCore.Qt.Unchecked)
        # self.prop_ls = getAni()
        # for num, obj in enumerate(self.prop_ls ):
        #     root = QtGui.QTreeWidgetItem(self.myTree)
        #     root.setText(0, obj)
        #     root.setCheckState(0, QtCore.Qt.Unchecked)
            
        self.myTree.expandAll()
        
        export_but = QtGui.QPushButton("Export")
        export_but.setMinimumWidth(80)
        h_box = QtGui.QHBoxLayout()
        h_box.addStretch()
        h_box.addWidget(export_but)
        
        V_lay = QtGui.QVBoxLayout()
        V_lay.addWidget(self.myTree)
        V_lay.addLayout(h_box)
        
        self.setLayout(V_lay)
        
        self.myTree.itemClicked.connect(self.handleChanged)
        export_but.clicked.connect(self.exportAbc)
    
    def handleChanged(self, item, column):
        count = item.childCount()
        # 有子节点的时候为根节点，全部都勾�
        if count:
            if item.checkState(column) == QtCore.Qt.Checked:
                for i in range(count):
                    item.child(i).setCheckState(0, QtCore.Qt.Checked)
            if item.checkState(column) == QtCore.Qt.Unchecked:
                for i in range(count):
                    item.child(i).setCheckState(0, QtCore.Qt.Unchecked)
        else:
            try:
                item.parent().setCheckState(0, QtCore.Qt.Unchecked)
            except:
                pass
    
    def getItem(self, input, output):
        for i in input:
            getChild1 = cmds.listRelatives(i, f=1, type="transform", c=1)  # 第一个子层级
            for ii in getChild1:
                if "model_GRP" in ii:
                    if ":" in i:
                        i = i.split(":")[-1]
                    getChild2_short = cmds.listRelatives(ii, f=0, type="transform", c=1)  # 第二个子层级短名
                    getChild2_long = cmds.listRelatives(ii, f=1, type="transform", c=1)  # 第二个子层级长名
                    shot_list = {}
                    for num, key in enumerate(getChild2_short):
                        long_vis_list = []
                        if ":" in key:
                            long_vis_list.append(getChild2_long[num])
                            long_vis_list.append(str(pm.PyNode(getChild2_long[num]).isVisible()))
                            shot_list[key.split(":")[-1]] = long_vis_list
                        else:
                            long_vis_list.append(getChild2_long[num])
                            long_vis_list.append(str(pm.PyNode(getChild2_long[num]).isVisible()))
                            shot_list[key] = long_vis_list
                    output[i] = shot_list
        # 记录层级所有信息在json文件
        #with open(os.path.dirname(cmds.file(location=1, q=1))+"/"+"message.json", "w") as json_file:
         #   json_file.write(json.dumps(output, indent=4))
                        
    def hiddenLayer(self, parent, son):
        '''遍历parent下面的子节点, 除了son之外的隐藏掉'''
        for par in self.char_ls:
            if parent == par:
                for chl in self.char_ls[par]:
                    if son == chl:
                         if not pm.PyNode(self.char_ls[par][chl][0]).isVisible():
                            self.cmds.select(self.char_ls[par][chl][0])
                            try:
                                pm.mel.eval('toggleVisibilityAndKeepSelection `optionVar -query toggleVisibilityAndKeepSelectionBehaviour`')
                            except:
                                pass
                         else:
                             pass
                    else:
                        if pm.PyNode(self.char_ls[par][chl][0]).isVisible():
                            self.cmds.select(self.char_ls[par][chl][0])
                            try:
                                pm.mel.eval('toggleVisibilityAndKeepSelection `optionVar -query toggleVisibilityAndKeepSelectionBehaviour`')
                            except:
                                pass
                        else:
                            pass
    
    def displayLayer(self):
        '''恢复原来层级的显示情�'''
        for par in self.char_ls:
            for chl in self.char_ls[par]:
                # print self.char_ls[par][chl][0],u"now: ",pm.PyNode(self.char_ls[par][chl][0]).isVisible(), u"old: ",self.char_ls[par][chl][1]
                if str(pm.PyNode(self.char_ls[par][chl][0]).isVisible()) != self.char_ls[par][chl][1]:
                    self.cmds.select(self.char_ls[par][chl][0])
                    try:
                        pm.mel.eval('toggleVisibilityAndKeepSelection `optionVar -query toggleVisibilityAndKeepSelectionBehaviour`')
                    except:
                        pass
                else:
                    pass

    def export(self, foldername, target):
        start_f = self.cmds.playbackOptions(q=1, ast=1)
        end_f = self.cmds.playbackOptions(q=1, aet=1)
        args = '-frameRange %s %s ' % (start_f, end_f)
        args = args+' -ro -uvWrite -writeColorSets -worldSpace -writeVisibility -writeUVSets -dataFormat ogawa '
        # 按大纲视图输出abc
        for i in self.cmds.ls(assemblies=1):
            if foldername in i:
                root = i
        args += '-root %s ' %(root)
        
        # for i in range(len(self.prop_ls)):
        #     print self.myTree.topLevelItem(i).text(0)
        
        # 输出相机
        for cam in cameraList():
            args += '-root %s ' %(cam)
            
        data_task = plcr.getTaskFromEnv()
        folder_name = os.path.basename(self.cmds.file(q=1,location=1)).split(".")[0]
        folder_name1 = foldername
        file_name = target
        path = "Z:/LongGong/sequences/"+data_task['sequence']+"/"+data_task['shot']+"/animation/outputCache/"+folder_name+"/"+folder_name1+"/"+file_name+".abc"
        if os.path.exists(os.path.dirname(path)):
            pass
        else:
            os.makedirs(os.path.dirname(path))
        args += '-file %s' % (path)
        plugin_list = self.cmds.pluginInfo(query=True, listPlugins=True)
        if 'mtoa' in plugin_list:
            args += ' -attr aiSubdivType -attr aiSubdivIterations'
        if 'AbcExport' not in plugin_list:
            self.cmds.loadPlugin("AbcExport")
        cmd = 'AbcExport -j "%s";' % args
        print cmd

        try:
            pm.mel.eval(cmd)
        except:
            pass
            # self.cmds.inViewMessage(amg=u"Please check camera's name, may be there are the same camera", pos='midCenter', fts=30, bkc=0x00FF1010, fade=True)
    
    def exportAbc(self):
        # 存储需要导出的长名
        export_ls = []
        # 遍历TreeWidet
        iterator = QtGui.QTreeWidgetItemIterator(self.myTree)
        while iterator.value():
            # 根节点勾� 导出所有子节点
            if iterator.value().childCount() and iterator.value().checkState(0) == QtCore.Qt.Checked:
                for i in range(iterator.value().childCount()):
                    parent = iterator.value().child(i).parent().text(0)
                    son = iterator.value().child(i).text(0)
                    for par in self.char_ls.keys():
                        if parent == par:
                            for chl in self.char_ls[par]:
                                if son == chl:
                                    print "par", par
                                    print "son", son
                                    self.hiddenLayer(par, son)
                                    self.export(par, son)
                                    export_ls.append( self.char_ls[par][son] )
                                    
                                    
            # 根节点未勾选，导出已经勾上的子节点
            if iterator.value().childCount() and iterator.value().checkState(0) == QtCore.Qt.Unchecked:
                for i in range(iterator.value().childCount()):
                    if iterator.value().child(i).checkState(0) == QtCore.Qt.Checked:
                        parent = iterator.value().child(i).parent().text(0)
                        son = iterator.value().child(i).text(0)
                        for par in self.char_ls.keys():
                            if parent == par:
                                for chl in self.char_ls[par]:
                                    if son == chl:
                                        print "par", par
                                        print "son", son
                                        self.hiddenLayer(par, son)
                                        self.export(par, son )
                                        export_ls.append( self.char_ls[par][son])
                                        
            iterator += 1
        
        self.displayLayer()

        QtGui.QMessageBox.information(self, "Information", 'Export ABC successful !')

win = Window()
win.show()
