# -*- coding: utf-8 -*-
from PySide import QtCore
from PySide import QtGui
import os
import sys
import time
sys.path.append("C:/cgteamwork/bin/base")
sys.path.append("C:/cgteamwork/bin/cgtw")
import cgtw

PATH = r"Z:/LongGong/common/animation/studiolibrary"
FloderFilter = ["Temp","temp", "Trash", "trash"]


# 获取所有动作库的ID号    
def allIdList():
    t_tw=cgtw.tw()
    t_shot = t_tw.info_module("proj_longgong_0", "poselibrary")
    id_list = t_shot.get_distinct_with_filter("poselibrary.id", [["poselibrary.id", "has", "%"]])
    return id_list        

# 上传动作库
def uploadFile(path, ID):
    t_tw = cgtw.tw()
    t_module  = "poselibrary" #模块
    t_module_type = "poselibrary"  #模块类型
    t_db  = "proj_longgong_0"  #数据库
    t_local_path = path #要上传文件路径

    try:
        #获取文件框数据
        filename = os.path.basename(t_local_path)
        task_id_list = ID
        t_path = os.path.dirname( t_local_path )
        t_upload_list = [ {"sou":t_local_path, "des":unicode(os.path.splitdrive(t_path)[1]+"/"+filename).replace("\\", "/")} ]
        
        #通过客户端进行上传到在线文件
        t_dic={'name':filename, 'task': [{"action":"upload", 
                                           "is_contine":True, 
                                           "data_list":t_upload_list, 
                                           "db":t_db, 
                                           "module":t_module, 
                                           "module_type":t_module_type, 
                                           "task_id":task_id_list, 
                                           "version_id":""}
                                          ]}
        print t_tw.local_con._send("queue_widget","add_task", {"task_data":t_dic}, "send")       
    except Exception, e:
        print e.message

class MyListWidget(QtGui.QListWidget):
    def __init__(self, parent = None):
        super(MyListWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        
    def dragEnterEvent(self, event):
        self.information = []
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        data = event.mimeData()
        urls = data.urls()
        if (urls and urls[0].scheme() == 'file'):
            urls[0].setScheme("")
            for uu in urls:
                self.information.append(uu)
        self.Add()
        
    def Add(self):
        for i in self.information:
            path = i.toString()
            if "///" in path:
                self.addItem(path.split("///")[1])
            else:
                self.addItem(path[1:])  
        return self.information
        

class Window(QtGui.QDialog):
    def __init__(self, parent=None):
        import maya.cmds as cmds
        import os
        import cgtw
        import ct 
        
        self._cmds = cmds
        self._cgtw = cgtw
        self._ct = ct
        self._os = os
        
        self.dir = {}
        
        super(Window,self).__init__(parent)
        
        self.setWindowTitle(u"Upload poses to CGT")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(430,300)
        
        self.tip = QtGui.QLabel(u"Drag&drop pose thumbnail")
        self.h1 = QtGui.QHBoxLayout()
        self.h1.addWidget(self.tip)
        self.sel = MyListWidget()
        
        self.but3 = QtGui.QPushButton(u"Del Selection")
        self.but3.setMaximumWidth(100)
        self.but2 = QtGui.QPushButton(u"Upload")
        self.but2.setMaximumWidth(100)
        self.h2 = QtGui.QHBoxLayout()
        self.h2.addWidget(self.but3)
        self.h2.addStretch()
        self.h2.addWidget(self.but2)
        lay = QtGui.QVBoxLayout()
        lay.addLayout(self.h1)
        lay.addWidget(self.sel)
        lay.addLayout(self.h2)
        
        self.setLayout(lay)
        
        self.but3.clicked.connect(self.run1)
        self.but2.clicked.connect(self.run)
    
    def getID(self, asset_name):
        t_tw1 = self._cgtw.tw()
        t_info = t_tw1.info_module("proj_longgong_0", "asset")
        filters = [
        ["asset.asset_name", "=", asset_name], 
        "and", 
        ["asset.type_name", "=", "char"]
        ]
        t_info.init_with_filter(filters) 
        asset_id = t_info.get(['asset.id'])[0]["asset.id"]
        return asset_id

    def run1(self):
        for i in self.sel.selectedItems():
            self.sel.takeItem(self.sel.row(i))
    
    def run(self):
        
        # 进度条弹窗
        progress = QtGui.QProgressDialog(self)
        progress.resize(400,200)
        progress.setWindowTitle("Please Wait")
        progress.setLabelText("Upload poses to CGT...")
        progress.setRange(0, self.sel.count())
        progress.show()
        
        for i in range(self.sel.count()):
            progress.setValue(i+1)
            path = self.sel.item(i).text()
            print path
            if path:
                char = path.split("/")[5]
                type = path.split("/")[6]
                name = path.split("/")[7]
                charname = self.getID(char) 
                t_tw = self._cgtw.tw()
                t_info = t_tw.info_module("proj_longgong_0", "poselibrary")
                t_create_dict = {'poselibrary.type':type, "poselibrary.entity_name":name, "poselibrary.charname":charname}
                filters = [
                ["poselibrary.entity_name", "=", name], 
                "and", 
                ["poselibrary.type", "=", type],
                "and",
                ["poselibrary.charname", "=", char]
                ]
                t_count = t_info.get_count_with_filter(filters)
                if t_count == "0":
                    print t_info.create(t_create_dict)
                t_info.init_with_filter(filters)
                print "jxy", char
                
                t_info.set({'poselibrary.charname':charname})
                t_info.set_image('poselibrary.image', path)
                
                a_sou_file_path = path
                t_sou_file_name = self._os.path.basename(a_sou_file_path)
                t_des_file_name = t_sou_file_name
                t_module_class = t_tw.info_module("proj_longgong_0", "poselibrary")
                t_module_class.init_with_filter(filters)
                t_id_list = t_module_class.get_id_list()
                t_module_class = t_tw.info_module("proj_longgong_0", "poselibrary", t_id_list)
                t_des_dir = t_module_class.get_dir(["AnimLib_folder"])[0]["AnimLib_folder"]
                t_des_file_path = unicode(t_des_dir + t_des_file_name).replace("\\", "/")
                t_sou_path_list = []
                if self._os.path.isdir(a_sou_file_path):
                    t_sou_path_list = self._ct.file().get_file_with_walk_folder(a_sou_file_path)
                try:
                    for i in t_sou_path_list:
                        des_path = unicode(i).replace("\\", "/").replace(a_sou_file_path, t_des_file_path)
                        self._ct.file().copy_file(i, des_path)        
                except Exception, e:
                    print u"Copy file fali " + a_sou_file_path + " --> " + t_des_file_path + "\n"

                print os.path.dirname(path)
                uploadFile(os.path.dirname(path), t_id_list[0])
                
        temp = []
        for i in range(self.sel.count()):
            temp.append(self.sel.item(i).text())
        progress.close()
        QtGui.QMessageBox.information(self, "Information", "Upload pose successfully !!!\n For this time, we have upload {} poses.\n {}".format(self.sel.count(), temp))
        
        self.sel.clear()
        

