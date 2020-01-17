# ==============================================================
# -*- encoding: utf-8 -*-# 
# !/usr/bin/env python
# 
#  @Version: 
#  @Author: RunningMan
#  @File: userSetup.py.py
#  @Create Time: 2020/1/16 11:37
# ==============================================================

import maya.utils as utils


def build_maya_shelf():
    import sfmg
    reload(sfmg)

    sfmg.build_maya_shelf()


utils.executeDeferred(build_maya_shelf)
