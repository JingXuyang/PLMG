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
import dbif
import swif
from pprint import pprint

# ================================= Global Values =================================
CONFIG_PATH = os.path.join(os.environ.get('XSYH_ROOT_PATH'), "data/config.yaml")
task_env = dict()
database = dbif.CGT()


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


def getInherit(cls):
    '''
    返回所有继承cls的子类
    @param cls: 父类
    @return: dict
    {
        'B': <class '__main__.B'>,
        'C': <class '__main__.C'>
    }
    '''
    sub_cls = {sub_cls.__name__: sub_cls for sub_cls in cls.__subclasses__()}
    return sub_cls


def getTaskPath(item_data, path_typ="work_path"):
    '''
    根据路径标识，返回路径
    @param item_data: 当前的任务数据
    @param path_typ: work 或 publish
    @return: str
    '''
    tag = getConfigs().get(item_data.get('step')).get(path_typ)
    kwargs = dict()
    kwargs['type'] = item_data.get('type')
    kwargs['sequence'] = item_data.get('sequence')
    kwargs['shot'] = item_data.get('shot')
    kwargs['tag'] = tag.format(step=item_data.get('step'))
    # print kwargs
    return database.getPathFromTag(**kwargs)


def taskFileInfo(path):
    '''
    得到文件夹下边多有符合改格式的文件信息列表
    @param path: 文件夹路径
    @return: list
    '''
    file_extension = getConfigs().get("global").get("workfile_format").get("maya")
    file_ls = utilities.getFilesInFolder(path)
    result = list()
    for f in file_ls:
        f = os.path.join(path, f)
        file_type = utilities.getBaseName(f).split(".")[1]
        if file_type in file_extension:
            kwargs = dict()
            kwargs['file_name'] = utilities.getBaseName(f).split(".")[0]
            kwargs['file_type'] = file_type
            kwargs['modified_Time'] = utilities.getFileModifyTime(f)
            kwargs['size'] = utilities.getFileSize(f)
            kwargs['path'] = path
            kwargs['description'] = ''
            # kwargs['artist']
            result.append(kwargs)
    return result


def toShowFileMsg(item_data, work=True):
    '''
    返回所有需要显示的文件信息列表。
    @param item_data:
    @param submit:
    @return:
    '''
    if work:
        work_path = getTaskPath(item_data, "work_path")
    else:
        work_path = getTaskPath(item_data, "publish_path")
    file_info_ls = taskFileInfo(work_path)
    return file_info_ls


# ================================= Class =================================
class ActionEngine(object):
    '''
    此类用来获取 nodes.action中的子类
    '''

    def __init__(self):
        pass

    @classmethod
    def project(cls):
        return os.environ.get("XSYH_PROJECT")

    @classmethod
    def task(cls):
        kwargs = {
            "sequence": os.environ.get("XSYH_SEQUENCE"),
            "shot": os.environ.get("XSYH_SHOT"),
            "type": os.environ.get("XSYH_TYPE"),
            "step": os.environ.get("XSYH_STEP"),
            "task_name": os.environ.get("XSYH_TASK_NAME"),
            "status": os.environ.get("XSYH_TASK_STATUS"),
            "artist": os.environ.get("XSYH_ARTIST"),
            "task_id": os.environ.get("XSYH_TASK_ID"),
        }
        return kwargs

    @classmethod
    def database(cls):
        return dbif.CGT()

    @classmethod
    def software(cls):
        return swif.software()


class CheckEngine(object):
    '''
    此类用来获取 nodes.checking中的子类
    '''
    def __init__(self):
        pass


class SubmitEngine(object):
    '''
    处理提交时的功能。
    '''

    def __init__(self, engine):
        self.engine = engine
        step = self.engine.get("step")
        self.config = stepConfigs(step).get("workfile_save_actions")

    def __init_config(self):
        '''
        开始匹配配置文件。
        '''
        self._match_class()

    def _match_class(self):
        '''
        匹配 action.py 中对应配置文件里的类，找到则运行类中的run函数。
        如果没有找到报错。
        @return: bool
        '''
        for element in self.config:
            action_type = element.get("type") or "publish"
            try:
                action_cls = getattr(ac, action_type)
                self._run_class(action_cls)

            except AttributeError:
                print u"没有属性", action_type
                return None

        return True

    def _run_class(self, cls):
        '''
        实例化类，并运行类中的run函数。
        @param cls: class
        @return: bool
        '''
        cls_instance = cls()
        try:
            cls_instance.run()
            return True

        except AttributeError:
            print u"没有run函数"
            return None


if __name__ == '__main__':
    # print getConfigs()
    pass
