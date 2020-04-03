# -*- coding: utf-8 -*-
import sys,os
import yaml
import inspect
import qtlb
import nodes
import huds_widgets
reload(huds_widgets)
#app = qtlb.Application(sys.argv)

currentFile = inspect.getfile(inspect.currentframe())
transparentImg = r'%s/1920_1080.png'%(os.path.dirname(currentFile))
transparentImg = transparentImg.replace('\\','/')


dafaultData = '''
labels: 
  - {text: Seq001_Shot010_Ani_BLO_v006, color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: 8}
  - {text: '05/06/19 11:06:44', color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: 84}
  - {text: 'resolution: 1920*818', color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: 60}
  - {text: 'FocalLength: 35.0', color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: 27}
  - {text: 'Author: wuxingcan', color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: -56}
  - {text: 'Time Unit: 24', color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: -40}
  
  - {text: 'Start/End: 1001--1005', color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: 8}
  - {text: 'Priority: P1', color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: 54}
  - {text: cam_001_010, color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: 33}
  - {text: 'Sequence: {frame.4}/1005', color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: 4}
  - {text: 'frame: {frame.4}', color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: -50}
  - {text: '', color: '#FCE344', font: Arial,
     alpha: 1, scale: 20, hpos: 0}

mask: 
  color: '#000000'
  alpha: 1
  scale: 131
  top: true
  bottom: true
'''
'#FFD505'

def main(data='',
        srcPath='',
        dstPath='',
        frameRange='',
        bgImg=''):
    
    if not data:
        data = dafaultData
    
    if not os.path.exists(bgImg):
        bgImg = transparentImg
    wgt = huds_widgets.SceneHUDsPrefsWidget(backgroundImage=bgImg)
        
    dat = yaml.load(data)
    wgt.setValue(dat)
    # refresh first label text font
    #wgt.show()
    #wgt.close()

    srcPath = srcPath
    dstPath = dstPath
    frameRange = frameRange
    wgt.saveSequence(srcPath, dstPath, frameRange,transparentImg=transparentImg)

    #sys.exit(app.exec_())

