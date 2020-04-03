# coding: utf-8
from pymel.core import *
def RTNAGBG():
    AG=[]
    BG=[]
    if len(selected()) == 2:
        driver = selected()[0]
        driven = selected()[1]
        ag = listRelatives(driver,ad =True,typ ='mesh') + listRelatives(driver,ad =True,typ ='nurbsCurve')
        for i in ag:
            agt = i.getParent()
            AG.append(agt)
        bg = listRelatives(driven,ad =True ,typ ='mesh') + listRelatives(driven,ad =True,typ ='nurbsCurve')
        drivered_new = [i for i in bg if i[-4:] != 'Orig' ]
        for i in drivered_new:
            bgt = i.getParent()
            BG.append(bgt)
    else:
        confirmDialog( title='Confirm', message='Are you select two mod or group ?', dismissString='No' )
    
    return  AG,BG

def makeBlend(driver, driven):
    return blendShape(driver,driven,tc=False,bf=True,origin ='world',n="vegaBlend")[0].w[0].set(1)

def Blend_name(AG,BG):    
    for eachB in BG :
        for eachA in AG :
            if eachB.getShape().type() ==eachA.getShape().type():
                if eachB.name().split('|')[-1].split(':')[-1] == eachA.name().split('|')[-1].split(':')[-1]  or  eachB.name().split('|')[-1].split(':')[-1] == eachA.name().split('|')[-1].split(':')[-1] +"_driver":
                        lo = PyNode(eachA.getShape())
                        lb = PyNode(eachB.getShape())
                        try:
                            makeBlend(lo, lb)
                        except RuntimeError or AttributeError:
                            print  lo, lb
                            confirmDialog(m="检查模型是否一样。或许有些模型smooth了一个级别.", t='!!!!!', b=['好的'])
def Blend_name_run():
    ag,bg = RTNAGBG()
    DR = list(set(ag))
    RD = list(set(bg))
    Blend_name(DR,RD)
def Blend_Index():
    if len(selected()) == 2:
        driver = selected()[0].getChildren()
        driven = selected()[1].getChildren()
        for i in range(len(driver)):
            print driver[i],driven[i]
            makeBlend(driver[i],driven[i])
    else:
        confirmDialog( title='Confirm', message='Are you select two mod ?', dismissString='No' )
def Blend():
    driver = ls(sl = 1)
    if len(driver) == 2:
        makeBlend(driver, driver[1])
    else:
        confirmDialog( title='Confirm', message='Are you select two mod ?', dismissString='No' )
    
    
def blend_delete():
    all = []
    for i in selected():
        if i.type() == 'transform':
            name = listConnections(i.getShape(),t='blendShape')
            if name !=[]:
                all.append(name[0])
        elif i.type() == 'mesh' or 'nurbsCurve':
            name = listConnections(i,t='blendShape')
            if name !=[]:
                all.append(name[0])
    delete(all)
