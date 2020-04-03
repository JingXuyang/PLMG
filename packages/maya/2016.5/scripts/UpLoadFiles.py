# -*- coding: utf-8 -*-
import os
import maya.cmds as cmds
import plcr
import sys
import dbif
sys.path.append("C:/cgteamwork/bin/base")
import cgtw

def run(*args):
    t_tw = cgtw.tw()
    data_task = plcr.getTaskFromEnv()
    a = dbif._cgteamwork.CGTeamwork()
    data_base = a.getProjectDatabase(data_task['project'])

    t_module      = data_task["pipeline_type"]  #模块
    t_module_type = "task"  #模块类型
    t_db          = data_base  #数据库
    t_local_path = cmds.file(location=1,q=1)  #要上传文件.mb路径
    
    # sorceimage文件
    image_path = os.path.dirname( cmds.file(location=1,q=1) )+"/"+"sourceimages"
    image_ls = []
    if os.path.exists(image_path):
        for i in os.listdir(image_path):
            if os.path.splitext(i)[-1] != ".db":
                image_ls.append(image_path+"/"+i)

    #获取文件框数据
    filename=os.path.basename( t_local_path )
    task_id_list = data_task["task_id"]
    print task_id_list
                                      
    try:
        result = []
        #上传.mb文件
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
        
        # 上传sorceimage文件
        if len(image_ls) > 0:
            for image in image_ls:
                filename=os.path.basename( image )
                t_path=os.path.dirname( image )
                t_upload_list = [ {"sou":image, "des":unicode(os.path.splitdrive(t_path)[1]+"/"+filename).replace("\\", "/")} ]
                #通过客户端进行上传到在线文件
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

        if "False" not in result:
            window = cmds.window( title="Tip", iconName='Short Name', widthHeight=(180, 80), rtf=True)
            cmds.columnLayout( adjustableColumn=True )
            cmds.text( label='' )
            cmds.text( label='Upload successful !!!' )
            cmds.text( label='' )
            cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 60), (2, 60), (3, 60)])
            cmds.text( label='' )
            cmds.button( label='Close', command=('cmds.deleteUI(\"' + window + '\", window=True)') )
            cmds.setParent( '..' )
            cmds.showWindow( window ) 

    except Exception, e:
        print e.message
        window = cmds.window( title="Tip", iconName='Short Name', widthHeight=(180, 60), rtf=True)
        cmds.columnLayout( adjustableColumn=True )
        cmds.text( label='' )
        cmds.text( label='Failed, please click script editer and check !!!' )
        cmds.setParent( '..' )
        cmds.showWindow( window )

def A():

    window = cmds.window( title="Tip", iconName='Short Name', widthHeight=(200, 80), rtf=True)
    cmds.columnLayout( adjustableColumn=True )
    cmds.text( label='' )
    cmds.text( label='Do you want to upload current files ?' )
    cmds.text( label='' )
    cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 60), (2, 60), (3, 60)])
    cmds.text( label='' )
    cmds.button( label='upload', command=run)
    cmds.text( label='' )
    cmds.setParent( '..' )
    cmds.showWindow( window )

