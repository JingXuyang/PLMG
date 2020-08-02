import sys
import os
import re
import glob
import shutil
import dbif
import maya.cmds as cmds
import pymel.core as pm
db = dbif._cgteamwork.CGTeamwork()
import swif
sw = swif._maya.Maya()

camModulePath = "Z:/LongGong/sequences/{sequence}/{shot}/camera/approved/{sequence}_{shot}_camera.abc"
#"Z:/LongGong/sequences/{sequence}/{shot}/camera/approved/{sequence}_{shot}_Ani_camera.mb"

def getSequences(project='LongGong'):
    seqInfo = db.getSequences(project)
    seqList = [inf['code'] for inf in seqInfo]
    
    seqList = sorted(seqList)
    return seqList
    
    
def getShots(project='LongGong',seq=''):
    shotList = []
    if seq:
        shotInfo = db.getShots(project,seq)
        shotList = [inf['code'] for inf in shotInfo]
        
        shotList = sorted(shotList)
        
    return shotList
        
def getSelectCam():
    s = cmds.ls(sl=True,type='camera',r=True,dag=True,long=True)
    allSelCam = cmds.listRelatives(s,p=True,fullPath=True)
    return allSelCam
    
def replaceRefCamToImport(refCam,newCamName,removeNamespace=True):
    cam = refCam
    reference = False
    if cmds.referenceQuery(cam,isNodeReferenced=True):
        rfn = cmds.referenceQuery(cam,rfn=True)
        # 
        cmds.file(importReference=True,referenceNode=rfn)
        
        # delete ':' namespace
        #newName = re.findall('cam_\d{3}_\d{3}',cam)
        reference = True
        
    cam = cmds.rename(cam,newCamName)

    return cam,reference

def versionUp(camPath,format='mb'):
    #camPath = r"Z:\LongGong\sequences\Seq050\Shot075\camera\approved\Seq050_Shot075_camera.mb"
    historyFolder = "%s/history"%(os.path.dirname(camPath))
    fileName = os.path.basename(camPath).split('.')[0]

    historyModulePath = "%s/%s_v???.%s"%(historyFolder,fileName,format)

    his = glob.glob(historyModulePath)

    if his:
        maxFile = max(his)
        version =  re.findall('v\d{3}(?=.%s)'%format,maxFile)

        newVersion = int(version[0][1:])+1
        newVersion = "v"+"%03.f"%newVersion
        versionFile = historyModulePath.replace('v???.%s'%format,"%s.%s"%(newVersion,format))
    else:
        versionFile = "%s/%s_v001.%s"%(historyFolder,fileName,format)

    versionFile = versionFile.replace('\\','/')
    
    if not os.path.exists(historyFolder):
        os.makedirs(historyFolder)
    
    shutil.copyfile(camPath,versionFile)
    
    return versionFile
    
    
def bakeCmd(obj,frameRange=[1,1]):
    mel  = 'bakeResults -simulation true -t "%s:%s" -sampleBy 1 '%(frameRange[0],frameRange[1])
    mel += "-disableImplicitControl true -preserveOutsideKeys true "
    mel += "-sparseAnimCurveBake false -removeBakedAttributeFromLayer false "
    mel += "-removeBakedAnimFromLayer false -bakeOnOverrideLayer false "
    mel += '-minimizeRotation true -controlPoints false -shape true {"%s"};'%(obj)
    pm.mel.eval(mel)
    


def publishCam(seq,shot,camera=[],bake=False):


    #print seq,shot
    camera =camera[0]
    
    
    camPath = camModulePath.format(sequence=seq,
                                   shot=shot)
                                   
    print "camPath:",camPath
    
    newCamName = "cam_%s_%s"%(seq[-3:],shot[-3:])
    reference = False
    if newCamName != camera:
        camera,reference = replaceRefCamToImport(camera,newCamName)
        
    if bake:
        frameRange = sw.frameRange()
        bakeCmd(camera,frameRange=frameRange)
    
    cmds.select(camera)
    
    kwargs = {
    'path': camPath,
    'singleFrame': False,
    'objects': [camera],
    'first_frame': 1000
     }
     
    sw.exportAbc(**kwargs)
    
    #sw.exportSelected(camPath)
    # version camera
    versionFileAbc = versionUp(camPath,format='abc')
    
    # export mb file
    camMbPath = camPath.replace('.abc','.mb')
    cmds.select(camera)
    sw.exportSelected(camMbPath)
    versionFileMb = versionUp(camMbPath,format='mb')
    
    #print "versionFile:",versionFile
    #print "reference:",reference
    
    #if reference:
    #    sw.reference(camPath,removeNamespace=False)
    
    
    
    
    
    
    