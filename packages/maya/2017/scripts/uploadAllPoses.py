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
        
        super(Window, self).__init__(parent)
        
        self.setWindowTitle(u"Upload poses to CGT")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(310,100)
        
        self.tip = QtGui.QLabel("Please click 'Start' button.")
        
        lay1 = QtGui.QVBoxLayout()
        lay1.addWidget(self.tip)
        
        self.progress = QtGui.QProgressBar()
        self.progress.setMaximumWidth(200)
        self.startButton = QtGui.QPushButton('Start')
        self.startButton.setMaximumWidth(80)
        hlay = QtGui.QHBoxLayout()
        hlay.addWidget(self.progress)
        hlay.addWidget(self.startButton)
        
        lay1.addLayout(hlay)

        self.setLayout(lay1)
        
        self.startButton.clicked.connect(self.run2) 

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
        self.tip.setText("Searching data from CGT...")        
        self.progress.setMinimum(0)
        self.progress.setMaximum(len(allIdList()))
        
        # 搜索本地所有文件
        AllFiles = []
        for path, dirname, filename in os.walk(PATH):
            for j in filename:
                if os.path.splitext(j)[1] == ".jpg":
                    A = (path+"/"+j).replace("\\","/")
                    if A.split("/")[5] not in FloderFilter:
                        AllFiles.append(A)
        # 设置进度条
        dataList = []
        t_tw = self._cgtw.tw()
        t_shot = t_tw.info_module("proj_longgong_0", "poselibrary")
        for num, id in enumerate(allIdList()):
            self.progress.setValue(num+1)
            t_shot.init_with_id([id])
            type = t_shot.get(["poselibrary.type"])
            name = t_shot.get(["poselibrary.entity_name"])
            charname = t_shot.get(["poselibrary.charname"])
            dataList.append( PATH+"/" + charname[0]["poselibrary.charname"] + "/" + type[0]["poselibrary.type"] + "/" + name[0]["poselibrary.entity_name"])

        # 得到需要上传的文件    
        self.uploadList = []    
        for local in AllFiles:
            if len(os.path.dirname(local).split("/")) == 8:
                if os.path.dirname(local) not in dataList:
                    self.uploadList.append(local)
    
    def finishWin(self):
        end_win = QtGui.QListWidget()
        end_win.addItems(self.uploadList)
        end_win.show()
    
    def run2(self):
        self.run1()
        time.sleep(0.5)
        print u"Need to upload: ", self.uploadList
        if len(self.uploadList) > 1:
            self.progress.setMinimum(0)
            self.progress.setMaximum(len(self.uploadList))
            for num, value in enumerate(self.uploadList): 
                path = value
                if path: 
                    char = path.split("/")[5]
                    type = path.split("/")[6]
                    name = path.split("/")[7]
                    charname = self.getID(char) 
                    
                    self.tip.setText("Create and uploding '%s' ..." % (char+"/"+type+"/"+name))
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
                    
                    print "image is ", path
                    t_info.set_image('poselibrary.image', path)
                    
                    # # 复制文件夹到文件框
                    a_sou_file_path = path
                    t_sou_file_name = self._os.path.basename(a_sou_file_path)
                    t_des_file_name = t_sou_file_name
                    t_module_class = t_tw.info_module("proj_longgong_0", "poselibrary")
                    t_module_class.init_with_filter(filters)
                    t_id_list = t_module_class.get_id_list()
                    # t_module_class = t_tw.info_module("proj_longgong_0", "poselibrary", t_id_list)
                    # t_des_dir = t_module_class.get_dir(["AnimLib_folder"])[0]["AnimLib_folder"]
                    # t_des_file_path = unicode(t_des_dir + t_des_file_name).replace("\\", "/")
                    # t_sou_path_list = []
                    # if self._os.path.isdir(a_sou_file_path):
                    #     t_sou_path_list = self._ct.file().get_file_with_walk_folder(a_sou_file_path)
                    # try:
                    #     for i in t_sou_path_list:
                    #         des_path = unicode(i).replace("\\", "/").replace(a_sou_file_path, t_des_file_path)
                    #         self._ct.file().copy_file(i, des_path)        
                    # except Exception, e:
                    #     print "Copy Fail" + a_sou_file_path + " --> " + t_des_file_path + "\n"
                    
                    # print os.path.dirname(path)
                    uploadFile(os.path.dirname(path), t_id_list[0])
                        
                self.progress.setValue(num+1)
         
        else:
            pass
            
        # self.finishWin()
        QtGui.QMessageBox.information(self, "Information", "Upload pose successfully !!!\n For this time, we have upload {} poses.\n {}".format(len(self.uploadList), self.uploadList))
        
        self.close()
