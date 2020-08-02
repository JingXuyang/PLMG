# coding: utf-8
from pymel.core import *
def BlendEditWin():
    if window("blendTool", exists=1):
        deleteUI('blendTool')
    windows = window('blendTool',wh = (320,480))
    columnLayout(adj=True)
    rowLayout(numberOfColumns=3, columnWidth3=(200,45,325), columnAttach=[(1, 'both', 10), (2, 'both', 4), (3, 'both', 5)])
    button(l = 'blend_weight_k',h=35,c = 'import lcaCfxBlendtool.BlendEditTool as bl;bl.setk()' )
    checkBox('check1',l='Key')
    floatSliderGrp('blend_number',field=True, minValue=0, maxValue=1,fieldMinValue=-100.0, fieldMaxValue=100.0, value=0,pre=2)
    setParent('..')
    rowLayout(numberOfColumns=2, columnWidth2=(200,360), columnAttach=[(1, 'both', 10), (2, 'both', 4)])
    button(l = 'Curves.CV_Weight_Edit',h=35,c = 'import lcaCfxBlendtool.BlendEditTool as bl;bl.blen_flo()' )
    intSliderGrp('all_cv_count',field=True, minValue=1, maxValue=20,fieldMaxValue=100.0, value=1)
    showWindow(windows)

def setk():
    de= selected()
    weight = floatSliderGrp('blend_number',q = 1,v=True)
    all = []
    for i in de:
        if i.type() == 'transform':
            name = listConnections(i.getShape(),t='blendShape')
            all.append(name[0])
    for i in all:
        Key = checkBox('check1',q = 1,v=True)
        if Key == True:
            setKeyframe(i,attribute='weight[0]',v=weight)
            i.setAttr('weight[0]',weight)
        else:
            i.setAttr('weight[0]',weight)
            
                
            

def getNurbsCurve():
    AllCurves = []
    for i in selected():
        if i.type() == 'nurbsCurve':
            AllCurves.append(i)
        elif i.type() == 'transform':
            shape= listRelatives(i,c=True,ad=True)
            if len(shape) >0:
                for il in shape:
                    if  il.type() == "nurbsCurve":
                        AllCurves.append(il)
    FinCurves = [a for a in selected()  if 'Orig' not in a]  
    return FinCurves

        
def blen_flo():
    all_cv = intSliderGrp('all_cv_count',q =1 ,value = True)
    CurvesShape = getNurbsCurve()
    print CurvesShape
    cv_list = range(all_cv)
    for i in CurvesShape:
        ble = listConnections(i+'.create')
        if len(ble) > 0:
            if not all_cv > i.numCVs():
                for cv_num in cv_list:
                    final_num = cv_num/float(all_cv)
                    str_cv_num = str(cv_num)
                    setAttr(ble[0]+'.inputTarget[0].baseWeights['+str_cv_num+']',final_num)
            else:
                for cv_num in range(i.numCVs()):
                    final_num = cv_num/float(i.numCVs())
                    str_cv_num = str(cv_num)
                    setAttr(ble[0]+'.inputTarget[0].baseWeights['+str_cv_num+']',final_num)
                

