# !/usr/bin/env python
# -*- coding: utf-8 -*-# 
# ============================================================== 
#  @Version: 
#  @Author: RunningMan
#  @File: engine.py
#  @Create Time: 2020/4/13 16:16
# ==============================================================

import os
import re
import main.utilities as utilities
import main.dbif
import main.swif as swif

# ================================= Global Values =================================
CONFIG_PATH = os.path.join(os.environ.get('XSYH_ROOT_PATH'), "data/config.yaml")
task_env = dict()
sw = swif.software()


def getConfigs():
    '''
    得到 configs 的内容
    @return:
    '''
    config_data = main.utilities.load_yaml(CONFIG_PATH)
    return config_data


def getTaskFromEnv():
    '''
    得到当前的任务环境
    '''
    kwargs = {
        "sequence": os.environ.get("XSYH_SEQUENCE"),
        "shot": os.environ.get("XSYH_SHOT"),
        "shot_id": os.environ.get("XSYH_SHOT_ID"),
        "type": os.environ.get("XSYH_TYPE"),
        "step": os.environ.get("XSYH_STEP"),
        "task_name": os.environ.get("XSYH_TASK_NAME"),
        "status": os.environ.get("XSYH_TASK_STATUS"),
        "artist": os.environ.get("XSYH_ARTIST"),
        "task_id": os.environ.get("XSYH_TASK_ID"),
    }
    return kwargs


def relaodConfigs():
    '''
    重新读取 configs
    @return:
    '''
    return getConfigs()


def setEnv(dicts):
    '''
    设置环境变量
    @param dicts: 环境变量字典
    '''
    for key, val in dicts.iteritems():
        os.environ[key] = val


def setTaskEnv(data_dic):
    '''
    设置任务环境
    @param dicts: 环境变量字典
    '''
    kwargs = {
        "XSYH_PROJECT": os.environ.get("XSYH_PROJECT") or "",
        "XSYH_SEQUENCE": data_dic.get("sequence") or "",
        "XSYH_SHOT": data_dic.get("shot") or "",
        "XSYH_TYPE": data_dic.get("type") or "",
        "XSYH_STEP": data_dic.get("step") or "",
        "XSYH_TASK_NAME": data_dic.get("task_name") or "",
        "XSYH_TASK_STATUS": data_dic.get("status") or "",
        "XSYH_ARTIST": data_dic.get("account") or "",
        "XSYH_TASK_ID": data_dic.get("task_id") or "",
        "XSYH_SHOT_ID": data_dic.get("shot_id") or "",
    }
    setEnv(kwargs)


def getStepConfig(step, level, project=''):
    return getConfigs().get(step).get(level)


def _localSettingsPath():
    user_path = user_path = '{0}/{1}'.format(os.path.dirname(os.path.expanduser('~')), '.pltk.')
    if not os.path.exists(user_path):
        main.utilities.makeFolder(user_path)
    return user_path


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
    return main.dbif.CGT().getPathFromTag(**kwargs)


def taskFileInfo(path):
    '''
    得到文件夹下边多有符合改格式的文件信息列表
    @param path: 文件夹路径
    @return: list
    '''
    file_extension = getConfigs().get("global").get("workfile_format").get("maya")
    file_ls = main.utilities.getFilesInFolder(path)
    result = list()
    for f in file_ls:
        f = os.path.join(path, f)
        file_type = main.utilities.getBaseName(f).split(".")[1]
        if file_type in file_extension:
            kwargs = dict()
            kwargs['file_name'] = main.utilities.getBaseName(f).split(".")[0]
            kwargs['file_type'] = file_type
            kwargs['modified_Time'] = main.utilities.getFileModifyTime(f)
            kwargs['size'] = main.utilities.getFileSize(f)
            kwargs['path'] = path
            kwargs['description'] = ''
            # kwargs['artist']
            result.append(kwargs)
    return result


def toShowFileMsg(item_data, work=True):
    '''
    返回所有需要显示的文件信息列表。
    @param item_data:
    @param work: 如果是True则找work_path，不是则找publish_path
    @return:
    '''
    if work:
        work_path = getTaskPath(item_data, "work_path")
    else:
        work_path = getTaskPath(item_data, "publish_path")
    file_info_ls = taskFileInfo(work_path)

    if file_info_ls:
        return file_info_ls

    return ''


def descriptionItem(data):
    '''
    处理环节的文件描述
    @param data: 配置数据
    @return: list
    '''
    result = list()
    if data.get("workfile_filename_description_items"):
        for item in data.get("workfile_filename_description_items"):
            if item.get("short_name"):
                result.append(item.get("short_name"))
            else:
                result.append(item.get("name"))
        return result
    else:
        return list()


def applyMaterials(info):
    if info.get('file_type') == 'ma':
        mapping_path = info['full_path'].replace('.ma', '_mapping.json')
        mapping = utilities.load_json(mapping_path)
        matNamespace = sw.isAlreadyReferenced(info['full_path'])
        if not matNamespace:
            matNamespace = sw.reference(info['full_path'])['namespace']

        sw.assignMaterials(mapping, matNamespace=matNamespace)


class ActionEngine(object):
    '''
    此类用来获取 nodes.action中的子类
    '''

    def _initAttr(self):
        '''
        绑定全局设置的属性
        @return:
        '''
        self._match_class(self.getGlobalConfigs())

    @staticmethod
    def project():
        '''
        得到当前的项目名称
        '''
        return os.environ.get("XSYH_PROJECT")

    @staticmethod
    def task():
        '''
        得到当前的任务信息
        '''
        kwargs = {
            "sequence": os.environ.get("XSYH_SEQUENCE"),
            "shot": os.environ.get("XSYH_SHOT"),
            "shot_id": os.environ.get("XSYH_SHOT_ID"),
            "type": os.environ.get("XSYH_TYPE"),
            "step": os.environ.get("XSYH_STEP"),
            "task_name": os.environ.get("XSYH_TASK_NAME"),
            "status": os.environ.get("XSYH_TASK_STATUS"),
            "artist": os.environ.get("XSYH_ARTIST"),
            "task_id": os.environ.get("XSYH_TASK_ID"),
        }
        return kwargs

    @staticmethod
    def database():
        return main.dbif.CGT()

    @classmethod
    def step(cls):
        return os.environ.get("XSYH_STEP")

    @classmethod
    def user(cls):
        return cls.database().user()

    @staticmethod
    def software():
        '''
        返回当前软件名称
        '''
        return main.swif.software()

    @staticmethod
    def getGlobalConfigs():
        '''
        '''
        return getConfigs().get('global')

    @staticmethod
    def getStepConfig():
        '''
        '''
        return getConfigs().get(os.environ.get("XSYH_STEP"))

    def parm(self, parm):
        return getattr(self, parm)

    @classmethod
    def setParm(cls, variable, val):
        setattr(cls, variable, val)

    def runAction(self, config_str, actions=''):
        self._match_class(config_str, actions)

    @staticmethod
    def getVersion():
        pass

    @classmethod
    def workfile_format(cls):
        return getStepConfig('global', 'workfile_format').get('maya')

    def formatVariable(self, config_str, actions=''):
        '''
        格式化字符串，如果有{},将{}中的变量替换后，返回正确的结果。
        如果没有，返回原值。
        @param config_str: 配置文件
        '''
        result = config_str
        # 如果字符串有{}，则需要替换其中的变量
        if isinstance(config_str, str) and '{' in config_str:
            cls_ls = re.findall(r'[{](.*?)[}]', config_str)
            for cls in cls_ls:
                # 查找 action 是否有该属性
                if hasattr(actions, cls):
                    # 当变量是 类 时，执行run函数，把结果替换变量
                    if hasattr(getattr(actions, cls), 'software'):
                        temp = getattr(actions, cls)()
                        a = temp.run()
                        if isinstance(a, (list, dict, tuple)):
                            result = a
                        else:
                            result = result.replace('{%s}' % cls, a)
                    else:
                        temp = getattr(actions, cls)
                        # 未找到函数和类，使用变量本身替换
                        if not hasattr(temp, '__call__'):
                            result = result.replace('{%s}' % cls, temp)
                        # 变量是 函数 时，直接执行替换变量
                        else:
                            a = temp()
                            if isinstance(a, (list, dict, tuple)):
                                result = a
                            else:
                                result = result.replace('{%s}' % cls, a or temp.__name__)

                # 查找 ActionEngine 是否有该属性
                elif hasattr(self, cls):
                    # 当变量是 类 时，执行run函数，把结果替换变量
                    if hasattr(getattr(self, cls), 'software'):
                        temp = getattr(self, cls)()
                        result = result.replace('{%s}' % cls, temp.run())
                    # 变量是 函数或者字符串时，直接执行替换变量
                    else:
                        temp = getattr(self, cls)
                        if not hasattr(temp, '__call__'):
                            if isinstance(temp, (list, dict, tuple)):
                                result = temp
                            else:
                                result = result.replace('{%s}' % cls, temp)
                        else:
                            a = temp()
                            if isinstance(a, (list, dict, tuple)):
                                result = a
                            else:
                                result = result.replace('{%s}' % cls, a or temp.__name__)

                # 去环境变量里查找
                elif self.task().get(cls):
                    result = result.replace('{%s}' % cls, self.task().get(cls))

                # 没有找到就返回本身
                else:
                    result = result.replace('{%s}' % cls, cls)

            return result

        else:
            return result

    def _match_class(self, config_data, actions=''):
        '''
        匹配 action.py 中对应配置文件里的类，找到则运行类中的run函数。
        如果没有找到报错。
        @return: bool
        '''
        if isinstance(config_data, list):
            for element in config_data:
                action_type = element.get("type")
                action_name = element.get("name")
                action_cls = getattr(actions, action_type)
                parms_dic = element.get('parms')
                subs_list = element.get('subs')

                # 如果有'_defaultParms'属性，把所有的字典都绑定到action_cls
                if hasattr(action_cls, '_defaultParms'):
                    for parms, val in action_cls._defaultParms.iteritems():
                        val = self.formatVariable(val, actions)
                        setattr(action_cls, parms, val)

                # 把所有的配置文件里的属性都绑定到action_cls，如果属性重复则覆盖
                if parms_dic:
                    for parms, val in parms_dic.iteritems():
                        if not isinstance(val, list):
                            val = self.formatVariable(val, actions)
                            setattr(action_cls, parms, val)
                        else:
                            if not hasattr(action_cls, parms):
                                temp = list()
                                for i in val:
                                    val = self.formatVariable(i, actions)
                                    temp.append(val)
                                setattr(action_cls, parms, temp)

                if subs_list:
                    setattr(action_cls, 'subs', subs_list)

                # 运行类的run函数得到结果
                # 如果有name, 把结果绑定到name对应的属性上。否则，把结果绑定到type对应的属性上
                if action_name:
                    setattr(self, action_name, action_cls().run())
                else:
                    setattr(self, action_type, action_cls().run())

        if isinstance(config_data, dict):
            for key, val in config_data.iteritems():
                setattr(self, key, val)

        return True
