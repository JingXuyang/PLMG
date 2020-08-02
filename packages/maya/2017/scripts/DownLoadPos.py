# -*- coding: utf-8 -*-
from PySide import QtCore
from PySide import QtGui
import maya.cmds as cmds
import os
import time
import sys
sys.path.append("C:/cgteamwork/bin/base")
import cgtw
import cgtw2
from pprint import pprint

PATH = r"Z:/LongGong/common/animation/studiolibrary"

# 获取所有动作库的ID号    
def allIdList():
    t_tw=cgtw.tw()
    t_shot = t_tw.info_module("proj_longgong_0", "poselibrary")
    id_list = t_shot.get_distinct_with_filter("poselibrary.id", [["poselibrary.id", "has", "%"]])
    return id_list   

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        
        import maya.cmds as cmds
        import os
        import cgtw
        
        self._cmds = cmds
        self._cgtw = cgtw
        self._cgtw2 = cgtw2
        self._os = os
        
        self.dir = {}

        super(Window,self).__init__(parent)
        
        self.setWindowTitle(u"Download poses from CGT")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(500,370)
        
        self.but1 = QtGui.QPushButton(u"Refresh")
        self.but1.setMinimumWidth(100)
        self.h1 = QtGui.QHBoxLayout()
        self.h1.addWidget(self.but1)
        self.h1.addStretch()
        self.tree = QtGui.QTreeWidget()
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background, QtCore.Qt.white)
        self.tree.setPalette(palette)
        
        self.tree.setSortingEnabled(True)
        self.tree.setHeaderLabels(['charname', 'type', 'name'])
        
        self.tip = QtGui.QLabel(u"Download poses")
        self.but3 = QtGui.QPushButton(u"Seleted")
        self.but3.setMinimumWidth(100)
        self.but2 = QtGui.QPushButton(u"All")
        self.but2.setMinimumWidth(100)
        self.h2 = QtGui.QHBoxLayout()
        self.h2.addWidget(self.tip)
        self.h2.addStretch()
        self.h2.addWidget(self.but3)
        self.h2.addWidget(self.but2)
        
        lay = QtGui.QVBoxLayout()
        lay.addLayout(self.h1)
        lay.addWidget(self.tree)
        lay.addLayout(self.h2)
        
        self.setLayout(lay)
        
        self.but1.clicked.connect(self.refresh)
        self.but3.clicked.connect(self.start)
        self.but2.clicked.connect(self.download_all)
        self.tree.itemClicked.connect(self.handleChanged)
    
    
    def sel_all(self):
        item = QtGui.QTreeWidgetItemIterator(self.tree)
        while item.value():
            if item.value().checkState(0) == QtCore.Qt.Unchecked:
                item.value().setCheckState(0, QtCore.Qt.Checked)
                item += 1
        
        return "suc"
        
    def download_all(self):
        a = self.sel_all()
        if a == "suc":
            self.start()
        
    def getData(self):
        progress = QtGui.QProgressDialog(self)
        progress.resize(400,200)
        progress.setWindowTitle("Please Wait")
        progress.setLabelText("Searching data from CGT...")
        progress.setRange(0, len(allIdList()))
        progress.show()
        
        # 得到所有anim 类型(type)
        t_shot = self._cgtw.tw.info_module("proj_longgong_0", "poselibrary")
        ls = t_shot.get_with_filter( ["poselibrary.type"], [["poselibrary.type", "has", "%"]])
        pos_type = []
        for type in ls:
            pos_type.append(type["poselibrary.type"])
            
        pos_type = list(set(pos_type))
            
        # 搜索本地所有文件
        AllFiles = []
        for path, dirname, filename in os.walk(PATH):
            for j in filename:
                if os.path.splitext(j)[1] == ".jpg":
                    A = path
                    AllFiles.append(A.replace("\\","/"))
        dataList = []
        
        # 设置进度条         
        t_tw = self._cgtw.tw()
        t_shot = t_tw.info_module("proj_longgong_0", "poselibrary")
        for num, id in enumerate(allIdList()):
            progress.setValue(num+1)
            t_shot.init_with_id([id])
            type = t_shot.get(["poselibrary.type"])
            name = t_shot.get(["poselibrary.entity_name"])
            charname = t_shot.get(["poselibrary.charname"])
            dataList.append( PATH+"/" + charname[0]["poselibrary.charname"] + "/" + type[0]["poselibrary.type"] + "/" + name[0]["poselibrary.entity_name"])

        # 得到需要下载的文件    
        self.downloadList = []    
        for cloud in dataList:
            if cloud not in AllFiles:
                self.downloadList.append(cloud)
                
        # 得到需要下载的文件的 type    
        type = []    
        for i in self.downloadList:
            type.append(self.getFilters(i)['charname'])
        
        self.charname = list(set(type))
        
        return self.downloadList
        pprint(self.downloadList)
        
    def deal_path(self, path = []):
        temp = {}
        for i in path:
            temp1 = []
            type = i.split("/")[-2]
            name = i.split("/")[-1]
            charname = i.split("/")[-3]
            temp1.append(type)
            temp1.append(name)
            temp1.append(charname)
            temp[type] = temp1
             
        return temp
    
    def handleChanged(self, item, column):
        count = item.childCount()
        # 根节点勾选, 导出所有子节点
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

    def getFilters(self, path):
        '''过滤条件'''
        dir = {}
        pathLs = path.replace("//","/").split("/")
        dir['charname'] = pathLs[5]
        dir['type'] = pathLs[6]
        dir['entity_name'] = pathLs[7]
        return dir
    
    def refresh(self):
        self.tree.clear()
        downloadList = self.getData()
        print "jxy", self.charname
        for i in self.charname:
            root = QtGui.QTreeWidgetItem(self.tree)
            for j in downloadList:
                if j.split("/")[-3] == i:
                    root.setText(0, i)
                    root.setCheckState(0, QtCore.Qt.Unchecked)
                    child = QtGui.QTreeWidgetItem(root)
                    child.setCheckState(0, QtCore.Qt.Unchecked)
                    type = j.split("/")[-2]
                    name = j.split("/")[-1]
                    charname = j.split("/")[-3]
                    child.setText(0, charname)
                    child.setText(1, type)
                    child.setText(2, name)
        
    def start(self):
        self.t_tw1 = self._cgtw.tw()
        self.t_tw2 = self._cgtw2.tw()
        
        # 存储需要导出的长名
        dow_ls = []
        # 遍历TreeWidet
        iterator = QtGui.QTreeWidgetItemIterator(self.tree)
        while iterator.value():
            # 根节点勾选, 导出所有子节点
            if iterator.value().childCount() and iterator.value().checkState(0) == QtCore.Qt.Checked:
                for i in range(iterator.value().childCount()):
                    parent = iterator.value().child(i).parent().text(0)
                    charname = iterator.value().child(i).text(0)
                    type = iterator.value().child(i).text(1)
                    name = iterator.value().child(i).text(2)
                    new = (PATH, charname, type, name)
                    dow_ls.append( "/".join(new))
                    
            # 根节点未勾选，导出已经勾上的子节点
            if iterator.value().childCount() and iterator.value().checkState(0) == QtCore.Qt.Unchecked:
                for i in range(iterator.value().childCount()):
                    if iterator.value().child(i).checkState(0) == QtCore.Qt.Checked:
                        parent = iterator.value().child(i).parent().text(0)
                        charname = iterator.value().child(i).text(0)
                        type = iterator.value().child(i).text(1)
                        name = iterator.value().child(i).text(2)
                        new = (PATH, charname, type, name)
                        dow_ls.append( "/".join(new))
            iterator += 1
        
        # 进度条弹窗
        progress = QtGui.QProgressDialog(self)
        progress.resize(400,200)
        progress.setWindowTitle("Please Wait")
        progress.setLabelText("Download poses from CGT...")
        progress.setRange(0, len(dow_ls))
        progress.show()
        
        pprint (dow_ls)
        self.fail = []
        if len(dow_ls) >= 1:
            for num, value in enumerate(dow_ls):
                progress.setValue(num+1)
                self.dir = self.getFilters(value)
                progress.setLabelText("Downloading '{0}/{1}/{2}'".format(self.dir['charname'], self.dir['type'], self.dir['entity_name']))
                # self.tip.setText("Downloading '%s' ..." % (self.dir['charname']+"/"+self.dir['type']+"/"+self.dir['entity_name']))
                filters = [
                ["poselibrary.type", "=", self.dir['type']],
                'and',
                ["poselibrary.entity_name", "=", self.dir['entity_name']],
                'and', 
                ["poselibrary.charname", "=", self.dir['charname']],
                ]
                
                t_id_list  = self.t_tw2.info.get_id('proj_longgong_0','poselibrary', filters)
                t_filebox_data = self.t_tw2.info.get_sign_filebox("proj_longgong_0",'poselibrary',t_id_list[0], "pos_work") 
                print t_filebox_data
                t_filebox_id = t_filebox_data['#id']
                filebox = self.t_tw2.info.get_sign_filebox("proj_longgong_0",'poselibrary',t_id_list[0], "pos_work")['title']
                print t_id_list[0],"   ", t_filebox_id
                try:
                    a = self.t_tw1.media_file().download("proj_longgong_0", 'poselibrary', "info", t_id_list[0], t_filebox_id)
                    if len(a) == 0:
                        temp = (PATH, value.split("/")[-3], value.split("/")[-2], value.split("/")[-1])
                        self.fail.append("/".join(temp))
                except:
                    print u'"%s" do not upload!!!'%(i)
        else:
            pass
        suc = len(dow_ls)-len(self.fail)
        fail = len(self.fail)
        suc_ls = list(set(dow_ls).difference(set(self.fail)))
        split = "**************************************************************************"
        QtGui.QMessageBox.information(self, "Information", "\nFor this time, we have downloaded {1} poses.\n {2}\n{3}\nBut {4} poses download fail, please check them !\n{5}".format(split, suc, suc_ls, split, fail, self.fail))



