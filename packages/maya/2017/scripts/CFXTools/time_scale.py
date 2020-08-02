# coding=utf-8
from pymel.core import *
if window("TimeScale", exists=1):
    deleteUI('TimeScale')
windows = window('TimeScale',title = "CFX_TimeScale",wh = (300,500))
columnLayout( columnAttach=('both', 5), rowSpacing=10, columnWidth=500)
setParent('..')
rowLayout( numberOfColumns=6, columnWidth6=(10,5,10,10,10,10), adjustableColumn=2, columnAlign=(1, 'right') )
text(l =u'起始帧',h = 25,w=50)
floatField('start_Attr',h = 22,w=60,v=998)
text(l =u'缩放倍数',h = 25,w=60)
floatField('num_Attr',h =20,w=80,v=0.1)
text(l =u'创建',h = 25,w=50)
button(l = u'身体缩放',h = 25,w=60 , c = 'creat()')
setParent('..')
rowLayout( numberOfColumns=7, columnWidth6=(10,5,10,10,10,10), adjustableColumn=2, columnAlign=(1, 'right') )
text(l =u'获取',h = 25,w=60)
button(l = u'缩放参数',h = 25,w=60 , c = 'get_attr()')
text(l =u'获取',h = 25,w=40)
button(l = u'对应帧数',h = 25,w=60 , c = 'get_zhenshu()')
text(l =u'名称',h = 25,w=50)
textField('name_add_body')
button(l = u'添加修形',h = 25,w=60 , c = 'add_xiuxing()')
setParent('..')
rowLayout( numberOfColumns=7, columnWidth6=(10,5,10,10,10,10), adjustableColumn=2, columnAlign=(1, 'right') )
text(l =u'名称',h = 25,w=50)
textField('name_cloth')
text(l =u'起始帧',h = 25,w=50)
floatField('start_cloth',h = 22,w=60,v=998)
text(l =u'缩放倍数',h = 25,w=60)
floatField('num_cloth',h =20,w=80,v=10)
button(l = u'布料完成',h = 25,w=60 , c = 'cloth()')
setParent('..')
rowLayout( numberOfColumns=7, columnWidth6=(10,5,10,10,10,10), adjustableColumn=2, columnAlign=(1, 'right') )
text(l =u'布料',h = 25,w=60)
button(l = u'检测并删除',h = 25,w=60 , c = 'chek_cloth()')
text(l =u'名称',h = 25,w=50)
textField('name_add_cloth')
button(l = u'添加布料',h = 25,w=60 , c = 'add_yifu()')


showWindow(windows)
def creat():
    start = floatField('start_Attr',q =1 ,value = True)
    num = floatField('num_Attr',q =1 ,value = True)   
    sel=selected()
    
    
    if objExists("aver_creat_01") or objExists("mult_creat_01") or objExists("aver_creat_02") or objExists("com_creat_01"):
     
        setAttr('aver_creat_01.input1D[1]',start)
        setAttr('mult_creat_01.input2X', num)
        setAttr('aver_creat_02.input1D[1]',start)
        setAttr('com_creat_01.secondTerm',start)
    else:
        
        AlembicNode=ls(type="AlembicNode")
        
        b=shadingNode('plusMinusAverage', asUtility=True,n='aver_creat_01')
        b.addAttr('body')
        setAttr(b+'.operation', 2 )
        setAttr(b+'.input1D[1]', start)
        connectAttr( 'time1.outTime',b+'.input1D[0]' ,f=True)
        c=shadingNode('multiplyDivide', asUtility=True,n='mult_creat_01')
        c.addAttr('body')
        setAttr(c+'.input2X', num )
        connectAttr( b+'.output1D', c+'.input1X' ,f=True)
        b2=shadingNode('plusMinusAverage', asUtility=True,n='aver_creat_02')
        b2.addAttr('body')
        setAttr(b2+'.input1D[1]',start)
        connectAttr( c+'.outputX', b2+'.input1D[0]',f=True )
        com=shadingNode('condition', asUtility=True,n='com_creat_01')
        com.addAttr('body')
        setAttr(com+'.secondTerm',start)
        setAttr(com+'.operation', 4)
        connectAttr( 'time1.outTime',com+'.firstTerm',f=True )
        connectAttr( 'time1.outTime',com+'.colorIfTrueR',f=True )
        connectAttr( b2+'.output1D',com+'.colorIfFalseR',f=True)
        for alem in AlembicNode:
            connectAttr( com+'.outColorR',alem+'.time',f=True)
      
      
def cloth():
    start_c= floatField('start_cloth',q =1 ,value = True)
    num_c= floatField('num_cloth',q =1 ,value = True)
    name=textField( 'name_cloth',q=1 ,text = True)
    
    
    if objExists('aver_creat_01_cloth') or objExists("mult_creat_01_cloth") or objExists("aver_creat_02_cloth") or objExists("com_creat_01_cloth"):
        setAttr('aver_creat_01_cloth.input1D[1]',start_c)
        setAttr('mult_creat_01_cloth.input2X', num_c)
        setAttr('aver_creat_02_cloth.input1D[1]',start_c)
        setAttr('com_creat_01_cloth.secondTerm',start_c)
    else:
        b_cloth=shadingNode('plusMinusAverage', asUtility=True,n='aver_creat_01_cloth')
        b_cloth.addAttr('cloth')
        
        setAttr(b_cloth+'.operation', 2 )
        setAttr(b_cloth+'.input1D[1]', start_c)
        connectAttr( 'time1.outTime',b_cloth+'.input1D[0]' ,f=True)
        c_cloth=shadingNode('multiplyDivide', asUtility=True,n='mult_creat_01_cloth')
        c_cloth.addAttr('cloth')
        setAttr(c_cloth+'.input2X',num_c)
        connectAttr( b_cloth+'.output1D', c_cloth+'.input1X' ,f=True)
        b2_cloth=shadingNode('plusMinusAverage', asUtility=True,n='aver_creat_02_cloth')
        b2_cloth.addAttr('cloth')
        setAttr(b2_cloth+'.input1D[1]',start_c)
        connectAttr( c_cloth+'.outputX', b2_cloth+'.input1D[0]',f=True )
        com_cloth=shadingNode('condition', asUtility=True,n='com_creat_01_cloth')
        com_cloth.addAttr('cloth')
        setAttr(com_cloth+'.secondTerm',start_c)
        setAttr(com_cloth+'.operation', 4)
        connectAttr( 'time1.outTime',com_cloth+'.firstTerm',f=True )
        connectAttr( 'time1.outTime',com_cloth+'.colorIfTrueR',f=True )
        connectAttr( b2_cloth+'.output1D',com_cloth+'.colorIfFalseR',f=True)
        connectAttr( com_cloth+'.outColorR',PyNode(name)+'.time',f=True)

def chek_cloth():
    name=textField( 'name_cloth',q=1 ,text = True)
    if objExists('aver_creat_01_cloth') or objExists("mult_creat_01_cloth") or objExists("aver_creat_02_cloth") or objExists("com_creat_01_cloth"):
        chek=confirmDialog( title='Confirm', message=u'已存在缩放节点，是否删除？', button=['Yes','No'])
    
        if chek=='Yes':
            if objExists(name):
                connectAttr( 'time1.outTime',PyNode(name)+'.time',f=True )
                mul_cloth=ls(type='multiplyDivide')
                ave_cloth=ls(type='plusMinusAverage')
                con_cloth=ls(type='condition')
                all_cloth=mul_cloth+ave_cloth+con_cloth
                del_cloth=[]
                for m in all_cloth:
                    if m.hasAttr('cloth'):
                        del_cloth.append(m)
                delete(del_cloth)
            else:
                mul_cloth=ls(type='multiplyDivide')
                ave_cloth=ls(type='plusMinusAverage')
                con_cloth=ls(type='condition')
                all_cloth=mul_cloth+ave_cloth+con_cloth
                del_cloth=[]
                for m in all_cloth:
                    if m.hasAttr('cloth'):
                        del_cloth.append(m)
                delete(del_cloth)
            
def get_attr():
    ave_attr=getAttr('aver_creat_01.input1D[1]')
    mul_attr=getAttr('mult_creat_01.input2X')
    confirmDialog( title='Confirm', message=u'身体缩放倍数            身体起始帧', button=[ave_attr,mul_attr])
def add_xiuxing():
    name_add=textField( 'name_add_body',q=1 ,text = True)
    connectAttr('com_creat_01.outColorR',PyNode(name_add)+'.time',f=True)
def add_yifu():
    name_cloth_add=textField( 'name_add_cloth',q=1 ,text = True)
    connectAttr('com_creat_01_cloth.outColorR',PyNode(name_cloth_add)+'.time',f=True)
def get_zhenshu():
    
    select('com_creat_01')
