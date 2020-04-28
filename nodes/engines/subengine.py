# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Version:
#  @Author: RunningMan
#  @File: engine.py
#  @Create Time: 2020/2/4 19:51
# ==============================================================
import engine
reload(engine)
from engine import ActionEngine
from nodes.actions import actions
from nodes.checking import item as check_item
reload(actions)
reload(check_item)


def openDialog(action):
    '''
    返回不同 action的窗口
    @param action:
    @return:
    '''
    import qtlb
    reload(qtlb)
    if action == 'submit':
        return qtlb.SubmitWidget(SubmitEngine)
    elif action == 'checking':
        return qtlb.CheckingWidget(CheckingEngine)
    elif action == 'publish':
        return qtlb.PublishWidget(PublishEngine)
    elif action == 'SelectTask':
        return qtlb.SelectTaskWindow(ActionEngine)


# ================================= Action =================================
class WorkfileManager(ActionEngine):
    '''
    此类用来执行文件管理的功能
    '''
    def __init__(self, engine_name):
        super(WorkfileManager, self).__init__()
        self.engine_name = engine_name
        self.bindAttr()

    def bindAttr(self):
        config = self.getGlobalConfigs().get("{0}_actions".format(self.engine_name))
        self._match_class(config, actions)

    def filterFileName(self, config):
        pass


class SubmitEngine(ActionEngine):
    '''
    处理提交时的功能。
    '''
    def __init__(self):
        super(SubmitEngine, self).__init__()
        self.config = self.getStepConfig().get("workfile_saveas_actions")

    def bindAttr(self):

        # 绑定没有action的属性
        step_config = self.getStepConfig()
        for key, val in step_config.iteritems():
            if 'actions' not in key:
                self._match_class({key: val}, actions)

        self._match_class(self.config, actions)


class PublishEngine(ActionEngine):
    '''
    处理发布时的功能。
    '''
    def __init__(self):
        super(PublishEngine, self).__init__()
        self.config = self.getStepConfig().get("publisher_actions")

    def bindAttr(self):

        # 绑定没有action的属性
        for key, val in self.getStepConfig().iteritems():
            if 'action' not in key or 'description' not in key:
                self._match_class({key: val}, actions)

        self._match_class(self.config, actions)


class CheckingEngine(ActionEngine):
    '''
    此类用来获取 nodes.checking中的子类
    '''
    def __init__(self):
        super(CheckingEngine, self).__init__()

    def getCheckingList(self):
        '''
        首先获取配置文件中 checking_items的列表。
        查找checking/item中的检查类，找到并以元祖的方式添加到列表中。
        第一是类，第二是 是否必须检查。如：
        [
           (<class 'nodes.checking.item.RenameDuplicateShape'>, 0),
           ...
        ]
        @return:
        '''
        self.config = self.getStepConfig().get("checking_items")
        result = list()
        for item in self.config:
            name = item.get('name')
            checkable = item.get('must', 1)
            if hasattr(check_item, name):
                result.append((getattr(check_item, name), checkable))
        return result


if __name__ == '__main__':
    # print getConfigs()
    pass
