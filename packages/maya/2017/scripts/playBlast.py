# -*- coding:utf-8 -*-

import pymel.core as pm
import maya.cmds as cmds
import json
import os
import getpass
# from collection import 
import plcr
import dbif
import time
import re

import sys
sys.path.append("C:/cgteamwork/bin/base")

import cgtw
import cgtw2
import swif
sw = swif._maya.Maya()

mask="spiderhuds"
PLUG_IN_NAME="spiderhuds.py"
TRANSFORM_NODE_NAME = "spiderhuds"
NODE_NAME="spiderhuds"
SHAPE_NODE_NAME="spiderhuds_shape"

Action = plcr.Action

camera = cmds.lookThru(q=True)

class MayaShuiYin(Action):

    def hideLocator(self):
        all_locator=cmds.ls(type="locator")
        for locator in all_locator:
            locator=locator.replace("Shape","")
            if locator!="spiderhuds_shape":
                try:
                    cmds.setAttr("{}.visibility".format(locator),0)
                except:
                    print "{}.visibility".format(locator)
                
    def showLocator(self):
        all_locator=cmds.ls(type="locator")
        for locator in all_locator:
            locator=locator.replace("Shape","")
            if locator!="spiderhuds_shape":
                cmds.setAttr("{}.visibility".format(locator),1)
    
    def reslution(self):
        width = cmds.getAttr('defaultResolution.width')
        height = cmds.getAttr('defaultResolution.height')
        reslu = str(width) + 'x' + str(height)
        return reslu
        
    def setRenderRes(self, name):
        
        # cmds.setAttr('defaultResolution.height', 1240)
        # cmds.setAttr("defaultResolution.deviceAspectRatio", 1.611)
        cmds.setAttr('defaultResolution.height', 948)
        cmds.setAttr("defaultResolution.deviceAspectRatio", 2.106)
        cmds.setAttr(name+".displayFilmGate", 0)
        cmds.setAttr(name+".displayResolution", 1)
        cmds.setAttr(name+".displayGateMask", 1)
        cmds.setAttr(name+".filmFit", 1)
        cmds.setAttr(name+".overscan", 1)
        cmds.setAttr(name+".displayGateMaskOpacity", 1)
        cmds.setAttr(name+".displayGateMaskColor", 0, 0, 0, type="double3")
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
        
    def setLabelSize(self, size):
        cmds.setAttr("spiderhuds_shape.borderColor", 0,0,0,type="double3")
        
        cmds.setAttr("spiderhuds_shape.font1Scale", size)
        cmds.setAttr("spiderhuds_shape.font1Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font2Scale", size)
        cmds.setAttr("spiderhuds_shape.font2Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font3Scale", size)
        cmds.setAttr("spiderhuds_shape.font3Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font4Scale", size)
        cmds.setAttr("spiderhuds_shape.font4Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font5Scale", size)
        cmds.setAttr("spiderhuds_shape.font5Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font6Scale", size)
        cmds.setAttr("spiderhuds_shape.font6Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font7Scale", size)
        cmds.setAttr("spiderhuds_shape.font7Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font8Scale", size)
        cmds.setAttr("spiderhuds_shape.font8Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font9Scale", size)
        cmds.setAttr("spiderhuds_shape.font9Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font10Scale", size)
        cmds.setAttr("spiderhuds_shape.font10Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font11Scale", size)
        cmds.setAttr("spiderhuds_shape.font11Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font12Scale", size)
        cmds.setAttr("spiderhuds_shape.font12Color", 1, 0.8342, 0.0188, type="double3")

        cmds.setAttr("spiderhuds_shape.font4hpos", 41)
        cmds.setAttr("spiderhuds_shape.font5hpos", 100)
        cmds.setAttr("spiderhuds_shape.font6hpos", -33)
        cmds.setAttr("spiderhuds_shape.font10hpos", 28)
        cmds.setAttr("spiderhuds_shape.font11hpos", 72)

    def setHudNode(self, PLUG_IN_NAME, TRANSFORM_NODE_NAME, NODE_NAME, SHAPE_NODE_NAME,frameRange=[],filename=''):
    
        t_tw = cgtw.tw()
        data = plcr.getTaskFromEnv()
        if not filename:
            filename = os.path.basename(cmds.file(location=1, q=1)).split(".")[0]
            
        author = data['artist']
        if not author:
            author = t_tw.sys().get_account()
        
        
        if not frameRange:
            frame_list = sw.frameRange()
        else:
            frame_list = frameRange
        
        startEndFrame = str(frame_list[0]) + "--" + str(frame_list[1])
        
        
        a = dbif._cgteamwork.CGTeamwork()
        data_base = a.getProjectDatabase(data['project'])
        if data_base:
            model = data.get('pipeline_type')
            if not model or not data.get('task_id'):
                priority = 'None'
            else:
                t_task_module = t_tw.task_module(str(data_base), str(model),[data['task_id']])
                inf = t_task_module.get(['shot.priority_shot'])
                if inf:
                    priority = inf[0]['shot.priority_shot']
                else:
                    priority = "None"
        else:
            priority = "None"
            
        
        camreaName = camera.split("|")[-1]
        
        start_f = cmds.playbackOptions(q=1, ast=1)
        end_f = cmds.playbackOptions(q=1, aet=1)
        ani_time = end_f-start_f+1
        
        self.label_text = [filename,
         time.strftime("%d/%m/%y %H:%M:%S", time.localtime(time.time())),
         # "reslution: " + "1998x1080",
         "reslution: " + "1920*818",
         "FocalLength: " + str(cmds.getAttr(camera + '.focalLength')),
         'Author: '+ author,
         'Time Unit: '+str(sw.fps()),
         'Start/End: '+ startEndFrame,
         'Priority: '+ priority,
         camreaName,
         'Sequence: '+ '{frame.4}' +"/"+str(int(end_f)),
         'frame: '+ '{frame.4}',
         "",
         ]
        
        if not cmds.pluginInfo(PLUG_IN_NAME, q=True, loaded=True):
            try:
                cmds.loadPlugin(PLUG_IN_NAME)
            except:
                om.MGlobal.displayError("Failed to load ZShotMask plug-in: {0}".format(PLUG_IN_NAME))
                return
        if cmds.objExists(NODE_NAME) != True:
            transform_node = cmds.createNode("transform", name=TRANSFORM_NODE_NAME)
            cmds.createNode(NODE_NAME, name=SHAPE_NODE_NAME, parent=transform_node)
            cmds.setAttr("{0}.topLeftText1".format(mask), self.label_text[0], type="string")
            cmds.setAttr("{0}.topLeftText2".format(mask), self.label_text[1], type="string")
            cmds.setAttr("{0}.topLeftText3".format(mask), self.label_text[2], type="string")
  
            cmds.setAttr("{0}.topRightText1".format(mask), self.label_text[3], type="string")
            cmds.setAttr("{0}.topRightText2".format(mask), self.label_text[4], type="string")
            cmds.setAttr("{0}.topRightText3".format(mask), self.label_text[5], type="string")
             
            cmds.setAttr("{0}.bottomLeftText1".format(mask), self.label_text[6], type="string")
            cmds.setAttr("{0}.bottomLeftText2".format(mask), self.label_text[7], type="string")
            cmds.setAttr("{0}.bottomLeftText3".format(mask), self.label_text[8], type="string")
            
            cmds.setAttr("{0}.bottomRightText1".format(mask), self.label_text[9], type="string")
            cmds.setAttr("{0}.bottomRightText2".format(mask), self.label_text[10], type="string")
            cmds.setAttr("{0}.bottomRightText3".format(mask), self.label_text[11], type="string")
            
            cmds.setAttr("{0}.borderColor".format(mask), 0.1, 0.6, 0, type="double3")
            return True

    # delete display HUD of node
    def delHeadsUpDisplay(self, node):
        """
        :param node: nodename
        :return:
        """
        if cmds.objExists(node) == True:
            cmds.delete(node)
        else:
            cmds.inViewMessage(amg='Node no exists!', pos='midCenter', fade=True)

    def setLabelText(self, mask):
        """
        :param mask: nodename
        :param label_text: label content ; list
        :return:
        """
        cmds.setAttr("{0}.topLeftText1".format(mask), self.label_text[0], type="string")
        cmds.setAttr("{0}.topLeftText2".format(mask), self.label_text[1], type="string")
        cmds.setAttr("{0}.topLeftText3".format(mask), self.label_text[2], type="string")
  
        cmds.setAttr("{0}.topRightText1".format(mask), self.label_text[3], type="string")
        cmds.setAttr("{0}.topRightText2".format(mask), self.label_text[4], type="string")
        cmds.setAttr("{0}.topRightText3".format(mask), self.label_text[5], type="string")
             
        cmds.setAttr("{0}.bottomLeftText1".format(mask), self.label_text[6], type="string")
        cmds.setAttr("{0}.bottomLeftText2".format(mask), self.label_text[7], type="string")
        cmds.setAttr("{0}.bottomLeftText3".format(mask), self.label_text[8], type="string")
            
        cmds.setAttr("{0}.bottomRightText1".format(mask), self.label_text[9], type="string")
        cmds.setAttr("{0}.bottomRightText2".format(mask), self.label_text[10], type="string")
        cmds.setAttr("{0}.bottomRightText3".format(mask), self.label_text[11], type="string")
        
    def run(self,frameRange=[],filename=''):
        
        print 0
        # 时间滑块设置到一帧
        #cmds.currentTime(cmds.playbackOptions(q=1, ast=1))
        print 1
        if "spiderhuds" in cmds.ls(assemblies=1):
            cmds.delete("spiderhuds")
        print "camera name:",camera
        # close camera shape's panZoomEnabled attr
        cameraShape = cmds.listRelatives(camera)[0]
        cmds.setAttr("%s.panZoomEnabled"%cameraShape,0)
        print 2
        # load plugin
        cmds.loadPlugin(r"Z:\bin\pltk\packages\maya\2016.5\plug-ins\spiderhud\spiderhuds.py")
        # set resolution and camera's Gate
        #print camera
        print 3
        self.setRenderRes(camera)
        # add HUD
        print 4
        self.setHudNode(PLUG_IN_NAME,TRANSFORM_NODE_NAME,NODE_NAME,SHAPE_NODE_NAME,frameRange=frameRange,filename=filename)
        # set HUD  pos,size
        print 5
        self.setLabelText(mask)
        self.setLabelSize(20)
        # 回到第一帧
        print 6
        #cmds.currentTime(cmds.playbackOptions(q=1, ast=1))
        print 7
        # display locater
        #cmds.modelEditor(cmds.getPanel( visiblePanels=1 )[0], e=True, allObjects=False)
        print 7.5
        cmds.modelEditor(cmds.getPanel( visiblePanels=1 )[0], e=True, locators=True, polymeshes=True, nurbsSurfaces=True, strokes=True)
        self.hideLocator()
        print 8
        # open gpu display
        panel = cmds.getPanel( visiblePanels=1 )[0]
        pm.mel.eval('modelEditor -e -pluginObjects gpuCacheDisplayFilter true %s;'%panel)
        print 9
        # display spiderhuds Locater
        cmds.setAttr("spiderhuds_shape.visibility",1)
        # cmds.ogs( reset=True )

class DelShuiYin(Action):

    def run(self):
        #camera = "cam"+"_"+plcr.getTaskFromEnv()["sequence"][-3:]+"_"+plcr.getTaskFromEnv()["shot"][-3:]
        '''Gate'''
        cmds.setAttr('defaultResolution.height', 818)
        cmds.setAttr("defaultResolution.deviceAspectRatio", 2.35)
        cmds.setAttr(camera+".filmFit", 0)
        cmds.setAttr(camera+".overscan", 1.1)
        
        # delete HUD Node
        cmds.delete("spiderhuds")

class FakePlayBlast(Action):

    _defaultParms = {
    'output': '', 
    }
    
    def killProcess(self, processName=''):
        '''
        processName: quicktimeShim.exe
        '''
        cmd = 'taskkill /F /IM "%s"'%processName
        os.popen(cmd)
        
    def run(self,path='',frameRange=[],cam=''):
        # print  "JXY:   ", self.parm("output")
        print "--"
        print 0
        # Kill "quicktimeShim" before playblast
        self.killProcess(processName='quicktimeShim.exe')
        print 1
        try:
            audio = cmds.ls(type="audio")[0]
        except:
            audio = "None"
        
        if cam:
            cam_name = cam
        else:
            cam_name = camera
        print "cam_name:",cam_name
        print 2
        if path:
            filename = path
        else:
            seq, shot = re.findall("\d+", cam_name)[0], re.findall("\d+", cam_name)[1]
            filename = 'C:\Users\%s\Desktop\\'%(getpass.getuser())+seq+"_"+shot
        filename = filename.replace('\\','/')
        print "filename:",filename
        
        key = {'format': 'qt', 'viewer': 1, 'quality': 100, 'compression': 'H.264', 
        'sound': audio, 'clearCache': 1, 'framePadding': 0, 'showOrnaments': 1,
        'sequenceTime': 0, 'percent': 100, 'filename': filename, 
        'forceOverwrite': True, 'widthHeight': [1920, 1080]}
        
        if frameRange:
            key['startTime'] = frameRange[0]
            key['endTime'] = frameRange[1]
        print 3
        if "previs" not in cmds.file(location=1, q=1):
            cmds.lookThru(cam_name)
        else:
            cmds.lookThru(cam_name)
        # mel.eval('ogs -reset')
        print 4
        cmds.currentTime(1000)
        #print cmds.playbackOptions(q=1, ast=1)-1
        print 5
        cmds.refresh(force=True)
        print 6
        cmds.currentTime(1001)
        print 7
        print "key:",key
        cmds.playblast(**key)
        
        #cmds.ogs( reset=True )
        
        






