# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Version: 
#  @Author: RunningMan
#  @File: __api.py
#  @Create Time: 2019/12/31 14:15
# ==============================================================


def get_shelf_set_from_env(**package):
    """
    package = {'software': 'maya',
              'project': 'LongGong',
              'extra_envs': [{'name': 'MAYA_UI_LANGUAGE', 'value': 'en_US', 'mode': 'over'},]
              'sw_path': 'C:/Program Files/Autodesk/Maya2016.5/bin/maya.exe'}
    @return:
    """
    set_sw_env(package["software"])


def set_sw_env(sw):
    if sw == "maya":
        build_maya_shelf()
    elif sw == "houdini":
        pass
    elif sw == "nuke":
        pass


def build_maya_shelf():
    import maya.cmds as cmds
    import pymel.core as pm
    main_win = pm.language.melGlobals['gMainWindow']
    menu_obj = "XSYHToolMenu"
    menu_label = "XSYH Toolkit"

    if cmds.menu(menu_obj, label=menu_label, exists=True, parent=main_win):
        cmds.deleteUI(cmds.menu(menu_obj, e=True, deleteAllItems=True))


if __name__ == '__main__':
    kwargs = {'project': 'LongGong',
              'extra_envs': [{'name': 'MAYA_UI_LANGUAGE', 'value': 'en_US', 'mode': 'over'},
                             {'name': 'MAYA_SCRIPT_PATH', 'value': '{ROOT}/scripts',
                              'mode': 'prefix'},
                             {'name': 'PYTHONPATH', 'value': '{ROOT}/scripts', 'mode': 'prefix'},
                             {'name': 'MAYA_DISABLE_CLIC_IPM', 'value': '1', 'mode': 'over'}],
              'sw_path': 'C:/Program Files/Autodesk/Maya2016.5/bin/maya.exe'}
    get_shelf_set_from_env(**kwargs)
