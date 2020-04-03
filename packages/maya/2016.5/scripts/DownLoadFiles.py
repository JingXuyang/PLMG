# -*- coding: utf-8 -*-
from PySide import QtCore
from PySide import QtGui
import maya.cmds as cmds
import os
import sys
sys.path.append("C:/cgteamwork/bin/base")
sys.path.append('C:/cgteamwork/bin/cgtw')
sys.path.append('C:/cgteamwork/bin/base/com_lib/')

import traceback
import ct
from   com_message_box   import *
import cgtw
import cgtw2
from pprint import pprint

class DownloadFiles(QtGui.QDialog):
    def __init__(self, parent=None):
        
        super(DownloadFiles,self).__init__(parent)
        
        self.setWindowTitle(u"Download Files")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(320,100)

        self.t_tw1 = cgtw.tw()
        self.t_tw2 = cgtw2.tw()
        self.cmds = cmds
        
        self._UI()
        
    def _UI(self):
        self.tip = QtGui.QLabel("Donwload reference files .",self)
        lay2 = QtGui.QHBoxLayout()
        lay2.addStretch()
        self.but = QtGui.QPushButton('Download')
        self.but.setMaximumWidth(80)
        lay2.addWidget(self.but)
        
        lay1 = QtGui.QVBoxLayout()
        lay1.addWidget(self.tip)
        lay1.addLayout(lay2)
        
        self.setLayout(lay1)
        
        self.but.clicked.connect(self.run) 

    def getAllRFs(self):
        '''获取不存在的RF文件'''
        RFfiles = []
        for i in cmds.ls(rf=1):
            if i == "_UNKNOWN_REF_NODE_":
                pass
            else:
                try:
                    path = cmds.referenceQuery(i, filename=True)
                except:
                    print i
                if "{" not in path:
                    if not os.path.exists(path):
                        RFfiles.append(path)
        RFfiles = list(set(RFfiles))
        return RFfiles
        
        
    def getFilters(self, path):
        '''过滤资产条件'''
        dir = {}
        pathLs = path.replace("//","/").split("/")
        if pathLs[2] == "assets":
            dir["two"] = 'asset'
        dir["type"] = pathLs[3]
        if pathLs[5]=="model":
            dir["stage"] = "Model"
        elif pathLs[5]=="rig":
            dir["stage"] = "Rig"
        elif pathLs[5]=="surface":
            dir["stage"] = "Texture"
        else:
            dir["stage"] = pathLs[5]

        dir["asestname"] = pathLs[4]
        if pathLs[5]=="charEffects":
            dir["state"] = pathLs[7]
            dir['chareffect'] = pathLs[6]
        else:
            dir['state'] = pathLs[6]
            dir['his'] = pathLs[7]
        return dir
        
    def getFilters1(self, path):
        '''过滤镜头条件'''
        dir = {}
        pathLs = path.replace("//","/").split("/")
        if pathLs[2] == "sequences":
            dir["two"] = 'shot'
            dir["eps"] = pathLs[3]
            dir["shot"] = pathLs[4]
            if pathLs[5] == "animation":
                dir['stage'] = 'Animation'
            else: 
                dir['stage'] = pathLs[5]
            dir['state'] = pathLs[6]
            return dir
                
    def file_path_sign(self, step, state, his):
        # chareffect = self.dir['chareffect']
        print step, state, his
        "通过环节名和状态来获取目录标识"
        dir = {
               "Model": {"work":"Model_work", "approved":"Model_publish"},
               "Rig": {"work":"Rig_work", "approved":"Rig_publish", "history":"Rig_publish_versions"},
               "Texture": {"work":"Texture_work", "approved":"Texture_publish"},
               "charEffects": {"work":["charEffects_work", "charEffects_nhair_work"], 
                               "approved":["charEffects_publish", "charEffects_nhair_publish"]},
               "Previs": {"work":"Previs_work", "approved":"Previs_publish"},
               "Layout": {"work":"Layout_work", "approved":"Layout_publish"},
               "Animation": {"work":"Animation_work", "approved":"Animation_publish"},
               "shotFinaling": {"work":"shotFinaling_work", "approved":"shotFinaling_publish"},
               "FX": {"work":"FX_work", "approved":"FX_publish"},
               }
        
        temp = ""
        for i in dir:
            if step == i:
                for ii in dir[i]:
                    if state == ii:
                        if self.dir.has_key('chareffect'):
                            if self.dir['chareffect'] == 'nCloth':
                                temp = dir[i][ii][0]
                            else:
                                temp = dir[i][ii][0]
                            
                        else:
                            if his == "history":
                                temp = dir[i]["history"]
                            else:
                                temp = dir[i][ii]
        return temp
        
                
    # def reloadRF(self):
        # Reload files
      #  for i in self.list:
       #     self.tip.setText("Reload files -- %s" %("/".join(i.split("/")[-4:])))
        #    self.cmds.file(i, loadReferenceDepth="asPrefs", loadReference=self.list[i])
    
    def run(self):
        self.list = self.getAllRFs()
        
        not_upload = []
        not_rig = []
        
        for i in self.getAllRFs():
            self.tip.clear()
            self.tip.setText('Dolwnloading "%s" ...' %("/".join(i.split("/")[-4:])))

            if "assets" in i:
                try:
                    self.dir = self.getFilters(i)
                    filters = [
                    ["asset.type_name", "=", self.dir["type"]],
                    'and',
                    ["task.pipeline", "=", self.dir["stage"]],
                    'and',
                    ["asset.asset_name", "=", self.dir["asestname"]],
                    ]
                    
                    t_info = self.t_tw2.task.get_id("proj_longgong_0", "asset", filters)
                    
                    id = self.t_tw2.task.get('proj_longgong_0', self.dir["two"], t_info, ['task.set_pipeline_id'])[0]['id']
                    
                    try:
                        # 下载资产文件
                        file_sign = self.file_path_sign(self.dir["stage"], self.dir["state"], self.dir['his'])
                        res = self.t_tw1.con._send("c_media_file","get_bulk_download_data_with_folder_sign",
                                                   {"db":"proj_longgong_0", 
                                                    "module":"asset", 
                                                    "module_type":"task", 
                                                    "os":ct.com().get_os(), 
                                                    "task_id_array": [id],
                                                    "folder_sign": file_sign,
                                                    })
                        for dic in res:
                            t_current_folder_id=dic["current_folder_id"]
                            t_folder_data_list=dic["folder_data_list"]
                            pprint (t_folder_data_list)
    
                            t_des_dir=dic["des_dir"]
                            if isinstance(t_folder_data_list, list):
                                for t_dict_data in t_folder_data_list:
                                    if isinstance(t_dict_data, dict) and t_dict_data.has_key("id") and t_dict_data.has_key("name") and t_dict_data.has_key("is_folder") and t_dict_data["name"] == os.path.basename(i):
                                        print t_dict_data["name"]
                                        t_task_data={'name':t_dict_data["name"], 'task': 
                                            [{"action":"download", 
                                              "is_contine":True, 
                                              "data_list":[t_dict_data], 
                                              "db":"proj_longgong_0", 
                                              "des_dir":t_des_dir, 
                                              "current_folder_id":t_current_folder_id}
                                            ]} 
                                        
                                        reslut = self.t_tw1.local_con._send("queue_widget","add_task", {"task_data":t_task_data},"send")
                                        if not result:
                                            not_upload.append(reslut)
                        # 下载资产文件
                        # print self.t_tw1.media_file().download("proj_longgong_0", self.dir["two"], "task", id, fileboxID)
                        
                        # 下载贴图文件
                        # if self.dir["stage"] == "Texture":
                        #     filebox_tex = self.getfileboxName2(set_pipeline_id)
                        #     fileboxID_tex = self.getfileboxID(filebox_tex, set_pipeline_id) 
                        #     print self.t_tw1.media_file().download("proj_longgong_0", self.dir["two"], "task", id, fileboxID_tex)
                    except:
                        print u'"%s" do not upload!!!'%(i)
                except:
                    not_rig.append(i )
                
            else:
                self.dir = self.getFilters1(i)
                filters = [
                ["shot.shot", "=", self.dir["shot"]],
                'and',
                ["shot.eps_name", "=", self.dir["eps"]],
                'and',
                ["task.pipeline", "=", self.dir["stage"]],
                ]
                
                t_info = self.t_tw2.task.get_id("proj_longgong_0", "shot", filters)
                
                id = self.t_tw2.task.get('proj_longgong_0', self.dir["two"], t_info, ['task.set_pipeline_id'])[0]['id']
                try:
                    # 下载镜头文件
                    file_sign = self.file_path_sign(self.dir["stage"], self.dir["state"])
                    print "file_sign: ",file_sign, "id:", id
                    
                    res = self.t_tw1.con._send("c_media_file","get_bulk_download_data_with_folder_sign",
                                               {"db":"proj_longgong_0", 
                                                "module":"shot", 
                                                "module_type":"task", 
                                                "os":ct.com().get_os(), 
                                                "task_id_array": [id],
                                                "folder_sign": file_sign,
                                                })
                    for dic in res:
                        t_current_folder_id=dic["current_folder_id"]
                        t_folder_data_list=dic["folder_data_list"]

                        t_des_dir=dic["des_dir"]
                        if isinstance(t_folder_data_list, list):
                            for t_dict_data in t_folder_data_list:
                                if isinstance(t_dict_data, dict) and t_dict_data.has_key("id") and t_dict_data.has_key("name") and t_dict_data.has_key("is_folder") and t_dict_data["name"] == os.path.basename(i):
                                    t_task_data={'name':t_dict_data["name"], 'task': 
                                        [{"action":"download", 
                                          "is_contine":True, 
                                          "data_list":[t_dict_data], 
                                          "db":"proj_longgong_0", 
                                          "des_dir":t_des_dir, 
                                          "current_folder_id":t_current_folder_id}
                                        ]} 
                                    reslut = self.t_tw1.local_con._send("queue_widget","add_task", {"task_data":t_task_data},"send")
                                    if not result:
                                        not_upload.append(reslut)
                   
                except:
                    print u'"%s" do not upload!!!'%(i)
        
        #self.reloadRF()
        
        split = "**************************************************************************\n" 
        mes = "Please view the download process in CGTeamWork !! \n\n"

        if  len( not_rig ) > 0:
            mes += split+"These files may doesn't exist in CGTeamWork\n"
            for i in not_rig:
                mes += i+"\n"
                
        if  len( not_upload ) > 0:
            mes += "\n"+split+"These files doesn't upload !"
            for i in not_upload:
                mes += i+"\n"
                
        self.tip.setText("Finish...")
        
        QtGui.QMessageBox.information(self, "Information", mes)
