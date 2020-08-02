# coding=utf-8
from pymel.core import *
if window("weiyi", exists=1):
    deleteUI('weiyi')
windows = window('weiyi',title = "CFX_weiyi",wh = (480,320))
form = formLayout()
tabs = tabLayout(innerMarginWidth=10, innerMarginHeight=10)
rowLayout(numberOfColumns=5, columnWidth5=(60,150,30,90,90), columnAttach=[(1, 'both', 0), (2, 'both', 5), (3, 'both',5),(4, 'both', 0),(5,'both',0)])
text(l =u'值',h = 25)
floatField('number_Attr',h = 22,)
text(l =u'起始帧',h = 25,w=50)
floatField('start_w_Attr',h = 22,v=950)
button(l = u'设置',h = 25 , c = 'a()')
showWindow(windows)
def a():
    num = floatField('number_Attr',q =1 ,value = True)
    start_weiyi = floatField('start_w_Attr',q =1 ,value = True)
    lo = selected()
    la = lo.pop(0)    
    
    for i in lo:
        list1 = listConnections(i,t ='multiplyDivide')
        
        if list1==[]:
            a = shadingNode('multiplyDivide', asUtility=True)
            b = shadingNode('plusMinusAverage',asUtility=True)
            connectAttr( la+'.translate', b+'.input3D[0]' )
            
            c1 = getAttr(b+'.input3D[0]',time=start_weiyi)
            list2=[]
            for nu in c1:
                e = nu*-1
                list2.append(e)
            setAttr(b+'.input3D[1]',list2)
            setAttr(a+".input2",(num,num,num))
            connectAttr(a+'.output', i+'.translate',f = True)
            connectAttr(b+'.output3D', a+'.input1' )
            
        else:
            
            setAttr(list1[0]+".input2",(num,num,num))
            list3 = listConnections(la,t ='plusMinusAverage')
            c2 = getAttr(list3[0]+'.input3D[0]',time=start_weiyi)
            list5=[]
            for nu1 in c2:
                e1 = nu1*-1
                list5.append(e1)
            for y in list3:
                    setAttr(y+'.input3D[1]',list5)
