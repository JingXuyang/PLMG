# ==============================================================
# -*- encoding: utf-8 -*-# 
# !/usr/bin/env python
#
#  @Author: RunningMan
#  @File: userSetup.py.py
#  @Create Time: 2020/1/16 11:37
#  @Description: 改脚本在maya启动的时候，自动运行。前提是把改脚本所在的路径添加到 PYTHON_PATH。
# ==============================================================

import maya.utils as utils


def build_maya_shelf():
    import sfmg
    reload(sfmg)

    sfmg.build_maya_shelf()


utils.executeDeferred(build_maya_shelf)
