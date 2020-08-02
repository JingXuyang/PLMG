# -*- coding: utf-8 -*-
import sys
sys.path.append("C:/cgteamwork/bin/base")
import os
import plcr
import cgtw


def transmitRigUV(source,target):
    import maya.cmds as cmds
    allShape = cmds.listRelatives(target,shapes=True,path=True)

    origShape = [s for s in allShape if 'Orig' in s and cmds.connectionInfo("%s.worldMesh[0]"%s,destinationFromSource=True)]
    if len(origShape) >= 1:
        shapeName = origShape[0]
        cmds.setAttr("%s.intermediateObject"%shapeName,0)
        cmds.polyTransfer(shapeName,uv=1,ch=0,ao=source)
        # 有多个Orig节点，删除是导致失败, 先跳过
        cmds.delete(shapeName,constructionHistory=True)
        cmds.setAttr("%s.intermediateObject"%shapeName,1)
    else:
        cmds.polyTransfer(target,uv=1,ch=0,ao=source)
        cmds.delete(target,constructionHistory=True)


def transmitFileUVCmd(maPath,uvPath,logPath,openLog=False,longName=True):
    '''
    after used 'transmitFileUVBackStage'
    '''
    import maya.cmds as cmds
    # open  ma file
    print "0"
    print maPath
    print uvPath
    cmds.file(maPath, force=True, open=True, prompt=False,ignoreVersion=True)
    print "1"
    # reference UV
    filename = os.path.basename(uvPath)
    ns = os.path.splitext(filename)[0]
    cmds.loadPlugin("AbcImport.mll")
    cmds.loadPlugin("AbcExport.mll")
    refPath = cmds.file(uvPath, reference=True, ignoreVersion=True,
                        groupLocator=True, mergeNamespacesOnClash=False,
                        options="v=0;",namespace=ns, type="Alembic")
    allReferenceMesh = cmds.ls(type="mesh",referencedNodes=True,dag=True)
    allRefObj = [cmds.listRelatives(m,p=True,fullPath=True)[0] for m in allReferenceMesh if not cmds.getAttr("%s.intermediateObject"%m)]

    namespace = cmds.referenceQuery(refPath, namespace=True)
    namespace = namespace.lstrip(':')
    # passing data
    objList = []

    asset = plcr.getTaskFromEnv()["asset"]
    t_tw=cgtw.tw()
    asset_ls = t_tw.info_module("proj_longgong_0", "asset").get_distinct_with_filter("asset.asset_name", [["asset.asset_name", "has", "%"], ["asset.type_name", "=", "char"]])
    
    for uvObj in allRefObj:
        obj = uvObj.replace('|%s:'%namespace,'|')
        # obj:  "|mesh"
        obj = obj[1:]
        if not longName:
            obj = obj.rsplit('|',1)[0]
        
        if cmds.objExists(obj):
            transmit=uvObj
            receive=obj
            
            print [transmit,receive]
            # transmit uv
            # if cmds.listRelatives(receive): # judge the object if is None
            #     transmitRigUV(transmit,receive)

            # ------------------------jxy----------------------------
            # l_eye_GRP组下边不能执行transmitRigUV，防止删除eyeBall_node
            if asset in asset_ls:
                if asset in receive and "r_eye_GRP" in receive:
                    pass
                elif asset in receive and "l_eye_GRP" in receive:
                    pass
                else:
                    if cmds.listRelatives(receive): # judge the object if is None
                        transmitRigUV(transmit,receive)
            else:
                if cmds.listRelatives(receive): # judge the object if is None
                    transmitRigUV(transmit,receive)
            # ----------------------------------------------------------------

        else:
            objList.append(obj)
            
    
    # remove reference
    cmds.file(refPath, removeReference=True)
    # save       
    cmds.file(force=True, save=True, prompt=False)
    return objList


def main(argv):
    
    #print "argv:",argv
    #['D:/project/THHJ/assets/Ch/Jiaolong/rig/publish/v002/Jiaolong.ma',
    # 'D:/project/THHJ/assets/Ch/Jiaolong/tex/publish/v001/Jiaolong.abc',
    # 'C:/Users/wuxingcan/Desktop/Jiaolong_uvLog.txt',
    # 'True'
    # 'True']
    
    maPath,uvPath,logPath,openLog,longName = argv

    if openLog == 'True':
        openLog = True
    else:
        openLog = False
    
    if longName == 'True':
        longName = True
    else:
        longName = False
        
    if logPath:
        import traceback
        
        logDir = os.path.dirname(logPath)
        if not os.path.exists(logDir):
            os.makedirs(logDir)
        
        try:
            
            result = transmitFileUVCmd(maPath,uvPath,logPath,openLog,longName)
            
            info = 'Transmit UV Success!!!\n'
            info += '\n'
            
            
            if result:
                info += '-------------- Object Not Found --------------------'
                info += '\n'
                result = '\n'.join(result)
                info += result
                info += '\n'
                info += '----------------------------------------------------'

            info += maPath

            with open(logPath,'w') as f:
                f.write(info)
        
            if openLog:
                os.startfile(logPath)
            
            
        except Exception, e:
            error = traceback.format_exc()
            error += '\n'
            error += '\n'
            error += maPath
            
            with open(logPath,'w') as f:
                f.write(error)
        
            if openLog:
                os.startfile(logPath)
        
    else:
        transmitFileUVCmd(maPath,uvPath,logPath,openLog,longName)
    
    
