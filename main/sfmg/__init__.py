# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Version: 
#  @Author: RunningMan
#  @File: __init__.py
#  @Create Time: 2019/12/31 14:14
# ==============================================================


__version__ = '0.1.0'

import _api

reload(_api)


def get_shelf_set_from_env(package):
    '''
    Gets package shelf set from system env.

    We will use env below:
        PKMG_PACKAGE_VERSION
            Current app version
        PKMG_PROJECT
            Current project
    '''
    return _api.get_shelf_set_from_env(package)


def build_maya_shelf():
    '''
    Builds Maya shelf set from system env.

    Here we don't use Maya shelf to build tools, instead we use menus to build tools.
    Because when Maya is closed, the default Maya shelves data will save to local home
    folder. Next time even if you open Maya without studio env you can still see
    the tools, which causes confusing.

    Call this function like this in Maya scripts/userSetup.py file:
        import maya.utils as utils
        utils.executeDeferred(buildMayaShelf)
    '''
    _api.build_maya_shelf()


def build_houdini_shelf():
    '''Builds Houdini shelf set from system env.'''
    return _api.build_houdini_shelf()


def supportedApps():
    '''Gets supported apps for the shelf system.'''
    return _api.supportedApps()
