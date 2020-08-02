# coding=utf-8
from pymel.core import *
if window("blend", exists=1):
    deleteUI('blend')
windows = window('blend',title='blend_following')
columnLayout()
floatSliderButtonGrp( 'all_cv_count',label=u'不跟随点数', field=True, buttonLabel='blend',buttonCommand='blen_flo()',minValue=0, maxValue=50, value=0 )
showWindow( windows )
def blen_flo():
    all_cv = floatSliderButtonGrp('all_cv_count',q =1 ,value = True)
    cv_list = range(int(all_cv))
    belend_both = selected()
    blendShape(origin='world',before=1)[0].w[0].set(1)
    judge = type(selected()[0].getShape()) == nt.NurbsCurve
    if judge == True:
        ble = listConnections(belend_both[1].getShape()+'.create')
        for cv_num in cv_list:
            final_num = cv_num/float(all_cv)
            str_cv_num = str(cv_num)
            setAttr(ble[0]+'.inputTarget[0].baseWeights['+str_cv_num+']',final_num)
        
    else:
        
        curs = belend_both[1].getChildren()
        select(curs)
        cur_shape = curs[0].getShape()
        ble = listConnections(cur_shape+'.create')
        cur_num = range(len(selected()))
        for cn in cur_num:
            str_cn=str(cn)
            for cv_num in cv_list:
                final_num = cv_num/float(all_cv)
                str_cv_num = str(cv_num)
                setAttr(ble[0]+'.inputTarget['+str_cn+'].baseWeights['+str_cv_num+']',final_num)

