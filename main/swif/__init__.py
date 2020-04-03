# ==============================================================
# -*- encoding: utf-8 -*-# 
# !/usr/bin/env python
# 
#  @Version: 
#  @Author: RunningMan
#  @File: __init__.py
#  @Create Time: 2020/1/15 10:36
# ==============================================================

import _maya
reload(_maya)


class Maya(_maya.Maya):
    '''
    An api class with functions to do things in Maya.
    '''
    pass


# class Houdini(_houdini.Houdini):
#     '''An api class with functions to do things in Houdini.'''
#     pass
#
#
# class Nuke(_nuke.Nuke):
#     '''An api class with functions to do things in Nuke.'''
#     pass


software = None
_app = ''
# for _i in (Maya, Houdini, Nuke):
for _i in (Maya,):
    try:
        _a = _i()
        _app = _a.app()
        software = _i
        break
    except:
        pass


def currentApp():
    return _app
