# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Version: 
#  @Author: RunningMan
#  @File: __api.py
#  @Create Time: 2019/12/31 14:15
# ==============================================================
import os
import utilities

# ------------------------------- Global Value -------------------------------
IMAGE_PATH = os.path.join(os.environ.get("XSYH_ROOT_PATH"), "data", "images").replace("\\", "/")
PACKAGE_PATH = os.environ.get("XSYH_PACKAGE_PATH")


# ------------------------------- Function -------------------------------
def refreshMenu(shelve_path, name):
    '''
    刷新工具架，先删除，再重新读取添加
    @param shelve_dic:  data of the shelve yaml
    @param name:  menu name
    @return: None
    '''
    from nodes.actions import actions
    reload(actions)
    if cmds.menu(name, exists=True):
        cmds.deleteUI(cmds.menu(name))
        cmds.deleteUI(name)
    cmds.refresh()
    build_shelf(shelve_path)


def itemCommand(name, tool_name):
    '''
    读取../packages/{name}/info.yaml，根据tool_name找到对应的 script
    @param name: publisher/submit
    @param tool_name: aa
    @return: script string
    '''
    if name:
        info_path = "{package_path}/{name}/info.yaml".format(package_path=PACKAGE_PATH, name=name)
        data = utilities.load_yaml(info_path)
        script_string = data.get(tool_name, "")
        return script_string


def createMayaItem(item_dic, parent=""):
    '''
    创建 maya 工具架
    :item_dic: {'tool': 'aa', 'label': 'publish', 'type': 'item', 'name': 'publisher', 'icon': ''}
    '''
    item_type = item_dic.get("type")

    # create item or divider
    if item_type != "subitem":
        kwargs = {
            "divider": True if item_type == "line" else False,
            "label": item_dic.get("label", ""),
            "image": item_dic.get("icon", "").format(IMAGE_PATH=IMAGE_PATH),
            "p": parent,
        }
        # add command if the item is not line
        if item_type != "line":
            kwargs["command"] = itemCommand(item_dic.get("name"), item_dic.get("tool", "None"))
        cmds.menuItem(**kwargs)

    # create submenu item
    else:
        kwargs = {
            "label": item_dic.get("label", ""),
            "image": item_dic.get("icon", "").format(IMAGE_PATH=IMAGE_PATH),
            "subMenu": True,
            "p": parent,
            "command": itemCommand(item_dic.get("name"), item_dic.get("tool", "None"))
        }
        item = cmds.menuItem(**kwargs)
        for sub_item_dic in item_dic.get("items"):
            createMayaItem(sub_item_dic, parent=item)


def build_shelf(shelve_path):
    import maya.cmds as cmds
    import maya.mel as mel
    global cmds
    # main_win = pm.language.melGlobals['gMainWindow']
    # get maya main window
    gMainWindow = mel.eval('$tmpVar=$gMainWindow')
    shelve_data = utilities.load_yaml(shelve_path)

    # create menu
    menu_name = shelve_data.get("menu_name")
    deafult_menu = cmds.menu(menu_name, label=menu_name, tearOff=True, parent=gMainWindow)

    # create refresh item
    cmds.menuItem(label="Refresh",
                  parent=deafult_menu,
                  command=lambda *args: refreshMenu(shelve_path, deafult_menu),
                  image="{IMAGE_PATH}/refresh.png".format(IMAGE_PATH=IMAGE_PATH))

    # create item
    for item_dic in shelve_data.get("items"):
        createMayaItem(item_dic, parent=deafult_menu)
