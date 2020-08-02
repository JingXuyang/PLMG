# -*- coding: utf-8 -*-
import maya.cmds as mc
from pymel.core import *
def jointChain( Prefix = 'joint',Num=10, inputCurve = 'curve1', orientation = 'xyz' ):
    mc.undoInfo(ock=True)
    Jnts=[]
    mc.select (cl=1)
    News = mc.duplicate (inputCurve,rr=1)
    mel.eval('rebuildCurve -ch 0 -rpo 1 -rt 0 -end 1 -kr 0 -kcp 0 -kep 1 -kt 0 -s 100 -d 3 -tol 0.01 %s;'%(News[0]))
    for i in range(Num):
        max = mc.getAttr( '%s.maxValue'%(mc.listRelatives(News[0],s=1)[0]))
        min = mc.getAttr('%s.minValue'%(mc.listRelatives(News[0],s=1)[0]))
        Pos = mc.pointOnCurve(News[0],pr=(i*(max-min)/(Num-1)),p=1)
        jnt = mc.joint (n='%s_jnt_#'%(Prefix),p=(Pos[0],Pos[1],Pos[2]))
        Jnts.append(jnt)
        mc.select (cl=1)
    mc.delete(News)
    aimDict = {}
    aimDict[orientation[0]] = 1
    aimDict[orientation[1]] = 0
    aimDict[orientation[2]] = 0
    aimVec = ( aimDict['x'], aimDict['y'], aimDict['z'] )
    orientDict = {}
    orientDict[orientation[0]] = 0
    orientDict[orientation[1]] = 0
    orientDict[orientation[2]] = 1
    orientVec = ( orientDict['x'], orientDict['y'], orientDict['z'] )
    JntAimConstrain = mc.aimConstraint( Jnts[1], Jnts[0], aimVector = aimVec, upVector = (0,1,0), worldUpType = "scene" )
    mc.delete( JntAimConstrain )
    getro = mc.getAttr (Jnts[0]+".r")[0]
    ro = mc.setAttr (Jnts[0]+".jointOrient",getro[0],getro[1],getro[2],type="double3")
    mc.setAttr (Jnts[0]+".r",0,0,0)
    for i in range( 1, len( Jnts ) - 1 ):
        JntAimConstrain = mc.aimConstraint( Jnts[i+1], Jnts[i], aimVector = aimVec, upVector = orientVec, worldUpType = "objectrotation", worldUpVector = orientVec, worldUpObject = Jnts[i-1] )
        mc.delete( JntAimConstrain )
        getro = mc.getAttr (Jnts[i]+".r")[0]
        ro = mc.setAttr (Jnts[i]+".jointOrient",getro[0],getro[1],getro[2],type="double3")
        mc.setAttr (Jnts[i]+".r",0,0,0)
    for i in range( 1, len( Jnts ) ):
     mc.parent( Jnts[i], Jnts[i-1], absolute = True)
    mc.joint (Jnts[-1],e=1,zso=1,oj='none',sao='zup',roo='zyx' )
    mc.select (cl=1)
    mc.undoInfo(cck=True)
    return inputCurve,Jnts


def create_stretch_ik( Prefix ='hair',Num = 6, inputCurve ='spine_curve'):
    ikchain = jointChain( Prefix,Num, inputCurve, orientation = 'xyz' )[1]
    ikhand = mc.ikHandle(c=inputCurve,n=Prefix+'_ikHandle#',roc=1,sj=ikchain[0],ee=ikchain[-1],ccv=0,sol='ikSplineSolver') 
    if not mc.objExists(inputCurve+".autoStretch"):
        mc.addAttr(inputCurve,k=1 ,ln= "autoStretch",min=0.0 ,max=1.0  ,at="double",dv=0.0 )
    arc = mc.arclen(inputCurve,ch=1)
    newdis = mc.createNode('multiplyDivide',n=(Prefix+"_newDis_MpD#"))
    mc.setAttr (newdis+".operation" ,2)
    mc.connectAttr ( arc+'.arcLength', newdis+'.input1X',f=1)
    newpma = mc.createNode('plusMinusAverage',n=(Prefix+"_newDis_PmA#"))
    mc.setAttr (newpma+".operation" ,2)
    mc.connectAttr ( newdis+'.outputX', newpma+'.input1D[0]',f=1)
    mc.setAttr (newpma+".input1D[1]" ,mc.getAttr (arc+".arcLength"))
    switch = mc.createNode('multiplyDivide',n=(Prefix+"_switch_MpD#"))
    mc.connectAttr (inputCurve+'.autoStretch', switch+'.input1X',f=1) 
    mc.connectAttr ( newpma+'.output1D',switch+'.input2X',f=1)
    trans = mc.createNode('multiplyDivide',n=(Prefix+"_trans_MpD#"))
    mc.setAttr (trans+".operation" ,2)
    mc.setAttr (trans+".input2X" ,len(ikchain)-1)
    mc.connectAttr ( switch+'.outputX',trans+'.input1X',f=1)
    for a in ikchain[1:]:
        lens = mc.createNode('plusMinusAverage',n=(Prefix+"_len_PmA#"))
        mc.setAttr (lens+".input1D[0]" ,mc.getAttr (a+".tx"))
        mc.connectAttr ( trans+'.outputX', lens+'.input1D[1]',f=1)
        mc.connectAttr ( lens+'.output1D',a+'.tx',f=1)
def createIK():
    SL=selected()
    for i in SL:
        num=i.getShape().numCVs()
        create_stretch_ik( Prefix ='hair',Num = num, inputCurve =i.name())
