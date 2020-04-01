# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Version: 
#  @Author: RunningMan
#  @File: __init__.py
#  @Create Time: 2019/12/31 14:14
# ==============================================================
import os
import functools

import utilities
import _api
reload(_api)

DATA_PATH = os.path.join(os.environ.get('XSYH_ROOT_PATH'), "data")


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
    # get the env data
    kwargs = utilities.load_json(os.path.join(DATA_PATH, "maya_env.json"))
    # ../../../data/shelves/{proj}/{sw}/{version}.yaml
    shelve_yaml_path = os.path.join(
        kwargs.get("data_path"),
        "shelves",
        kwargs.get("project"),
        kwargs.get("software"),
        "{0}.yaml".format(kwargs.get("sw_version"))
    )
    _api.build_shelf(shelve_yaml_path)


def build_houdini_shelf():
    '''Builds Houdini shelf set from system env.'''
    return _api.build_houdini_shelf()


def supportedApps():
    '''Gets supported apps for the shelf system.'''
    return _api.supportedApps()
