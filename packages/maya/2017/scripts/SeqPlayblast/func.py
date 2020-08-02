import sys
import os
import maya.cmds as cmds

def getAllCamera():
    defaultCam = [ 'front','persp','side','top','bottom']
    allCamera = list(set(cmds.listCameras())-set(defaultCam))
    allCamera = sorted(allCamera)
    return allCamera


def parsingCameraShotInfo():
    allCamera = getAllCamera()
    
    result = []
    for cam in allCamera:
        info = {'camera':cam,
                'firstFrame':'',
                'lastFrame':''}
        result.append(info)
    return result
    
    
def unloadPlugin():
    '''
    load eyeBallNode.py plugin ,
    when playblast is beging,
    the maya will be stuck 
    '''
    allPlugin = cmds.pluginInfo(q=True,listPlugins=True)
    if 'eyeBallNode' in allPlugin:
        cmds.unloadPlugin('eyeBallNode.py',force=True)
    
def loadPlugin():
    cmds.loadPlugin('eyeBallNode.py')

    
def playBlast(path='',
              info=[]):
              
    sys.path.append("Z:/bin/pltk/packages/maya/2016.5/scripts")
    import plcr
    import playBlast
    reload(playBlast)
    en = plcr.Engine()
    
    # unload plugin eyeBallNode.py
    #unloadPlugin()
    
    MS = playBlast.MayaShuiYin(en)
    FP = playBlast.FakePlayBlast(en)
    DY = playBlast.DelShuiYin(en)
    
    if not os.path.exists(path):
        os.makedirs(path)
        
    
    for i in info:
        camera = i[0]
        # set camera zoom 1 ,other value will make hud disappear
        
        cameraShape = cmds.listRelatives(camera)[0]
        try:
            cmds.setAttr("%s.zoom"%cameraShape,1)
        except:
            pass
        
        frameRange = [i[1],i[2]]
        
        #
        print "---- start -------"
        cmds.lookThru(camera)
        MS.run(frameRange=frameRange)
        
        filepath = "%s/%s.mov"%(path,camera)
        
        FP.run(path=filepath,
               frameRange=frameRange,
               camera=camera)
        
    DY.run()
    # load plugin eyeBallNode.py
    #loadPlugin()
    
def playBlast2(path='',
              frameRange=[],
              camera=''):
    sys.path.append("Z:/bin/script")
    import plcr
    import playBlast
    reload(playBlast)

    en = plcr.Engine()

    MS = playBlast.MayaShuiYin(en)
    MS.run(frameRange=frameRange)

    FP = playBlast.FakePlayBlast(en)
    FP.run(path=path,
           frameRange=frameRange,
           camera=camera)

    DY = playBlast.DelShuiYin(en)
    DY.run()
