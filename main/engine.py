# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Version:
#  @Author: RunningMan
#  @File: engine.py
#  @Create Time: 2020/2/4 19:51
# ==============================================================

import os
import utilities

# ================================= Global Values =================================
CONFIG_PATH = os.path.join(os.environ.get('XSYH_ROOT_PATH'), "data/config.yaml")
task_env = dict()


# ================================= Functions =================================
def getConfigs():
    '''
        得到 configs 的内容
        @return:
        '''
    config_data = utilities.load_yaml(CONFIG_PATH)
    return config_data


def getTaskFromEnv(task_tree_item):
    '''
        得到当前的任务环境
        @param task_tree_item:
        @return:
        '''
    task_env = task_tree_item


def relaodConfigs():
    '''
        重新读取 configs
        @return:
        '''
    return getConfigs()


def stepConfigs(step=""):
    return getConfigs().get(step)


def setEnv(dicts):
    '''
        设置环境变量
        @param dicts: 环境变量字典
        '''
    for key, val in dicts.iteritems():
        os.environ[key] = val


# ================================= Class =================================
class ActionEngine(object):
    '''
    此类用来获取 nodes.action中的子类
    '''

    def __init__(self):
        pass


class CheckEngine(object):
    '''
    此类用来获取 nodes.checking中的子类
    '''
    def __init__(self):
        pass




if __name__ == '__main__':
    # print getConfigs()
    pass
