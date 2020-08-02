import os
import shutil
import subprocess
import time
import re
import sys
sys.path.append(r'C:\cgteamwork\bin\base')

import cgtw
import cgtw2
import maya.cmds as cmds
import swif

import hud_func
reload(hud_func)

tw1 = cgtw.tw()
t_tw = cgtw2.tw()
sw = swif._maya.Maya()

inputFolder = "%s/hudTempFolder/input" % (os.environ['TEMP'])
outFolder = "%s/hudTempFolder/output" % (os.environ['TEMP'])
data_base = "proj_longgong_0"


class HudWatermark:

    def __init__(self, path, cam):
        self.path = path.replace('\\', '/')
        self.camera = cam

    def getShotPriority(self):
        seq_split = re.search(r'(Seq\w+)', sw.filepath())
        shot_split = re.search(r'(Shot\w+)', sw.filepath())
        if seq_split and shot_split:
            t_id_list = t_tw.task.get_id(
                data_base, 'shot', [['shot.eps_name', '=', seq_split.group()], 'and', ["shot.shot", "=", shot_split.group()]]
            )
            priority = t_tw.task.get(data_base, "shot", [t_id_list[0]], ['shot.priority_shot'])
            return priority[0]['shot.priority_shot']
        else:
            return False

    def setHudData(self):
        fileName = os.path.basename(self.path)
        timeStr = time.strftime("%d/%m/%y %H:%M:%S", time.localtime(time.time()))
        res = "reslution: 1920x818"
        focal = "FocalLength: %s" % (cmds.getAttr(self.camera + '.focalLength'))
        author = tw1.sys().get_account()
        author = 'Author: %s' % author
        fps = 'Time Unit: %s' % (sw.fps())
        frame_list = sw.frameRange()
        frameRange = "%s--%s" % (frame_list[0], frame_list[1])
        frameRange = 'Start/End: ' + frameRange
        inf = self.getShotPriority()
        if inf:
            priority = inf
        else:
            priority = "None"

        priority = 'Priority: ' + priority
        #
        camera = self.camera
        #
        seqFrameStr = "Sequence: {frame.4}/%s" % (frame_list[1])
        #
        frame = 'frame: {frame.4}'

        data = '''
        labels: 
          - {text: %s, color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: 8}
          - {text: '%s', color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: 111}
          - {text: '%s', color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: 60}
          - {text: '%s', color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: 27}
          - {text: '%s', color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: -56}
          - {text: '%s', color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: -40}
          
          - {text: '%s', color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: 8}
          - {text: '%s', color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: 54}
          - {text: %s, color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: 33}
          - {text: '%s', color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: 4}
          - {text: '%s', color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: -50}
          - {text: '', color: '#FCE344', font: Arial,
             alpha: 1, scale: 20, hpos: 0}
        
        mask: 
          color: '#000000'
          alpha: 1
          scale: 131
          top: true
          bottom: true
        ''' % (fileName, timeStr, res, focal, author, fps, frameRange, priority, camera, seqFrameStr, frame)
        return data

    def getCameraAttr(self):

        attrList = ['defaultResolution.width',
                    'defaultResolution.height',
                    "defaultResolution.deviceAspectRatio",
                    self.camera + ".displayFilmGate",
                    self.camera + ".displayResolution",
                    self.camera + ".displayGateMask",
                    self.camera + ".filmFit",
                    self.camera + ".overscan",
                    "hardwareRenderingGlobals.multiSampleEnable",
                    "hardwareRenderingGlobals.ssaoEnable"
                    ]
        r = {}

        for atr in attrList:
            v = cmds.getAttr(atr)
            r[atr] = v
        return r

    def setCameraAttr(self):
        self.oldAttr = self.getCameraAttr()

        # unlock attr
        s = cmds.getAttr(self.camera + ".displayFilmGate", l=True)
        if s:
            cmds.setAttr(self.camera + ".displayFilmGate", l=False)

        sfd = cmds.connectionInfo(self.camera + ".displayFilmGate", sfd=True)
        if sfd:
            cmds.disconnectAttr(sfd, self.camera + ".displayFilmGate")

        #
        s = cmds.getAttr(self.camera + ".displayResolution", l=True)
        if s:
            cmds.setAttr(self.camera + ".displayResolution", l=False)
        #
        s = cmds.getAttr(self.camera + ".displayGateMask", l=True)
        if s:
            cmds.setAttr(self.camera + ".displayGateMask", l=False)

        s = cmds.getAttr(self.camera + ".filmFit", l=True)
        if s:
            cmds.setAttr(self.camera + ".filmFit", l=False)

        s = cmds.getAttr(self.camera + ".overscan", l=True)
        if s:
            cmds.setAttr(self.camera + ".overscan", l=False)

            # ------------
        cmds.setAttr('defaultResolution.width', 1920)
        cmds.setAttr('defaultResolution.height', 1080)
        cmds.setAttr("defaultResolution.deviceAspectRatio", 2.106)
        cmds.setAttr(self.camera + ".displayFilmGate", 0)
        cmds.setAttr(self.camera + ".displayResolution", 1)
        cmds.setAttr(self.camera + ".displayGateMask", 1)
        cmds.setAttr(self.camera + ".filmFit", 1)
        cmds.setAttr(self.camera + ".overscan", 1)
        # cmds.setAttr(self.camera+".displayGateMaskOpacity", 1)
        # cmds.setAttr(self.camera+".displayGateMaskColor", 0, 0, 0, type="double3")
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
        cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)

    def playblast(self):
        # remove images file
        if os.path.exists(inputFolder):
            shutil.rmtree(inputFolder)
        if os.path.exists(outFolder):
            shutil.rmtree(outFolder)

        if not os.path.exists(inputFolder):
            os.makedirs(inputFolder)
        if not os.path.exists(outFolder):
            os.makedirs(outFolder)
        # inputFolder = inputFolder.replace('\\','/')
        # outFolder = outFolder.replace('\\','/')

        file = inputFolder + '/test'
        v = {"format": "image",
             "filename": file,
             "sequenceTime": 0,
             "clearCache": 1,
             "viewer": 0,
             "showOrnaments": 1,
             "fp": 4,
             "percent": 100,
             "compression": "jpg",
             "quality": 100,
             "widthHeight": [1920, 1080]}

        cmds.lookThru(self.camera)
        print "playblast: ", v
        cmds.playblast(**v)
        cmds.ogs(reset=True)

    def addHudWatermark(self):
        data = self.setHudData()
        self.srcPath = "%s/test.####.jpg" % (inputFolder)
        self.dstPath = "%s/test.####.png" % (outFolder)
        self.frameRange = sw.frameRange()
        frameRangeStr = "%s-%s" % (self.frameRange[0], self.frameRange[1])
        hud_func.main(data=data,
                      srcPath=self.srcPath,
                      dstPath=self.dstPath,
                      frameRange=frameRangeStr)

    def killProcess(self, processName=''):
        '''
        processName: quicktimeShim.exe
        '''
        cmd = 'taskkill /F /IM "%s"' % processName
        os.popen(cmd)

    def outputMov(self):

        self.killProcess(processName='quicktimeShim.exe')
        try:
            audio = cmds.ls(type="audio")[0]
            audio = cmds.getAttr("%s.filename" % audio)
            if not os.path.isfile(audio):
                audio = None
        except:
            audio = None

        temp_path = os.path.dirname(self.dstPath) + "aaa.mov"
        cmd = '"{ffmpeg}" -y -start_number {startFrame} -r 24 -i "{inputImgs}" '
        cmd += '-start_number {startFrame} -r 24 -i "{inputImgs2}" -filter_complex "[0:v][1:v]overlay=0:0" '
        cmd += '-c:v libx264 -pix_fmt yuv420p -b:v 20000k -f mov "{output}"'
        cmd = cmd.format(ffmpeg="Z:/bin/pltk/thirdparty/ffmpeg/win/20160711/bin/ffmpeg.exe",
                         startFrame=self.frameRange[0],
                         inputImgs=self.srcPath.replace('####', '%04d'),
                         inputImgs2=self.dstPath.replace('####', '%04d'),
                         audio=audio,
                         output=temp_path,
                         )
        print "cmd1: ", cmd
        folderPath = os.path.dirname(self.path)
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)

        subprocess.call(cmd, shell=True)

        if audio:
            cmd = '"{ffmpeg}" -y -i "{no_audio}" -i "{audiofile}" -c:v copy -c:a aac -strict experimental -map 0:v:0 -map 1:a:0 -shortest "{output}"'
            cmd = cmd.format(ffmpeg="Z:/bin/pltk/thirdparty/ffmpeg/win/20160711/bin/ffmpeg.exe",
                             no_audio=temp_path,
                             audiofile=audio,
                             output=self.path
                             )
            print "cmd2: ", cmd
            subprocess.call(cmd, shell=True)
        else:
            shutil.copy2(temp_path, self.path)

        os.startfile(self.path)

        # setAttr old attr

        for atr, v in self.oldAttr.iteritems():
            cmds.setAttr(atr, v)
