# -*- coding:utf-8 -*-
# ==============================================================

# !/usr/bin/env python
#
# @Author: RunningMan
# @File: _cgteamwork.py.py
# @Create Time: 2019/12/30 0030 20:41
# ==============================================================

import os
import sys
import logging

sys.path.append("C:/cgteamwork/bin/base")
import cgtw
import cgtw2


# ----------------------------------------------------------------------
# 在使用requests包发送http请求的时候，都会默认在日志文件里生成一条建立连接的记录。
# 使用logging模块，取消requests的http请求，能够取消打印日志
# ----------------------------------------------------------------------
logging.getLogger("requests").setLevel(logging.WARNING)


# ================================= Class =================================

class CGT(object):

    def __init__(self, proj_name=os.environ.get('XSYH_PROJECT'), config_data=""):
        self.tw = cgtw.tw()
        self.tw2 = cgtw2.tw()
        self.proj_name = proj_name
        self.config_data = config_data
        self.database = self.getDataBase(self.proj_name)

    @classmethod
    def islogind(cls):
        '''
        检查是否打开了cgteamwork客户端，成功返回True, 否则返回False
        @return: bool
        '''
        try:
            cgtw2.tw()
            return True
        except:
            return False

    def getDataBase(self, proj_name=os.environ.get('XSYH_PROJECT')):
        '''
        得到项目的数据库名称
        @param proj_name: 项目名称
        @return: string
        '''
        t_id_list = self.tw2.info.get_id(
            'public', 'project', [["project.status", "!=", "Lost"], "and", ["project.status", "!=", "Close"]]
        )
        t_data = self.tw2.info.get(
            'public', 'project', t_id_list, ['project.database', 'project.code']
        )
        for index, dic in enumerate(t_data):
            if dic.get('project.code') == proj_name:
                return dic.get('project.database')

        return False

    def user(self):
        '''获取当前登录的账号'''
        return self.tw2.login.account()

    def userTaskInfo(self):
        '''
        [
            {'id': u'91927D66-4AB4-0137-8FE3-0EA5B5F441CB',
              'shot.eps_name': u'Seq001',
              'shot.shot': u'Shot010',
              'task.account': u'jingxuyang',
              'task.artist': u'\u666f\u65ed\u9633',
              'task.assign_time': u'2020-04-08 16:27:25',
              'task.pipeline': u'Animation',
              'task.status': u'Published',
              'task.task_name': u'Animation'},
             {'asset.asset': u'',
              'asset.asset_name': u'TestCharDog',
              'asset.cn_name': u'',
              'asset.type_name': u'char',
              'id': u'62240A29-F3C9-8547-61C1-60E1B0919512',
              'task.account': u'jingxuyang',
              'task.artist': u'\u666f\u65ed\u9633',
              'task.assign_time': u'2020-04-14 11:13:03',
              'task.pipeline': u'Texture',
              'task.status': u'Wait',
              'task.task_name': u'Texture'}
        ]
        '''
        result = list()

        # 查找用户的镜头任务
        seq_ls = self.getSeqs()
        shot_id_list = list()  # 存储用户的镜头任务ID
        for seq in seq_ls:
            shot_ls = self.getShots(seq)
            _id_list = self.tw2.task.get_id(self.database, 'shot',
                                            [['shot.eps_name', '=', seq], 'and', ["shot.shot", "in", shot_ls], 'and',
                                             ["task.account", "=", self.user()]])
            shot_id_list.extend(_id_list)
        shot_info = self.getShotTask(task_id_ls=shot_id_list, load_label=True)
        # 添加额外的信息
        for info in shot_info:
            info['project'] = os.environ.get('XSYH_PROJECT')
            info['type'] = 'shot'
        result.extend(shot_info)

        # 查找用户的资产任务
        asset_typ = self.assetTypes()
        asset_id_list = list()  # 存储用户的资产任务ID
        for typ in asset_typ:
            _id_list = self.tw2.task.get_id(self.database, 'asset',
                                            [['asset.type_name', '=', typ], 'and', ["task.account", "=", self.user()]])
            asset_id_list.extend(_id_list)
        asset_info = self.getAssetTask(task_id_ls=asset_id_list, load_label=True)
        # 资产信息中的 asset_name 和 type_name， 替换为shot_name 和 sequence。
        # 在庄口中显示任务信息时，减少列数。
        for info in asset_info:
            info['project'] = os.environ.get('XSYH_PROJECT')
            info['type'] = 'asset'
            info['asset.asset_name'] = (info.get('asset.asset_name')[0], 'shot')
            info['asset.type_name'] = (info.get('asset.type_name')[0], 'sequence')
        result.extend(asset_info)

        return result

    def submit(self, project='', type='', taskId='', files='', description='', state=''):
        '''
        提交检查文件，创建一个 状态为submit状态的note
        '''
        db = self.getDataBase(project)
        # self.tw2.task.submit(db, type, taskId, file, description)
        self.tw2.send_web("c_note", "create",
                          {"db": db, "cc_acount_id": "",
                           "field_data_array": {"status": state, "module": type, "module_type": "task",
                                                "#task_id": taskId,
                                                "text": {
                                                    "data": "<a class='cgtw-open-file-css' href='file:///{0}'>{1}</a> <br><br>{2}".format(
                                                        files, os.path.basename(files), description),
                                                    "image": ""
                                                },
                                                "#from_account_id": ''
                                                }
                           }
                          )

    def doesFieldsExist(self, entity, project, name_ls):
        '''查看字段是否存在'''
        db = self.getDataBase(project)
        result = []
        for name in name_ls:
            if not '{0}.{1}'.format(entity, name) in self.tw2.info.fields(db, entity):
                result.append(name)
        if result:
            return result
        else:
            return True

    def createField(self, entity='', project='', cnLabel='', label='', name='', type=''):
        '''创建字段'''
        db = self.getDataBase(project)
        if cnLabel:
            self.tw2.field.create(db, entity, "info", cnLabel, name, name, type)
        else:
            self.tw2.field.create(db, entity, "info", name, name, name, type)

    def getPipelineData(self):
        id_list = self.tw2.pipeline.get_id(self.database, [['entity_name', 'has', '%']])
        t_pipeline_data = self.tw2.pipeline.get(self.database, id_list, ['module', 'entity_name'])
        for i in t_pipeline_data:
            print i

    def assetTypes(self):
        '''
        得到所有资产类型：["prop", "set", "char"]
        @return: list
        '''
        t_asset_id_list = self.tw2.info.get_id(
            self.database, 'asset', [['asset.asset_name', 'has', '%']]
        )
        asset_types = self.tw2.info.get(
            self.database, 'asset', t_asset_id_list, ["asset.type_name"]
        )
        result = set()
        for i in asset_types:
            result.add(i["asset.type_name"])

        return list(result)

    def getInfoId(self, sequence, shot, model="shot"):
        '''获取信息模块的ID'''
        if model == "shot":
            t_id_list = self.tw2.info.get_id(
                self.database, model, [['shot.eps_name', '=', sequence], 'and', ["shot.shot", "=", shot]]
            )
        else:
            t_id_list = self.tw2.info.get_id(
                self.database, "asset", [['asset.type_name', '=', sequence], 'and', ["asset.asset_name", "=", shot]]
            )
        if t_id_list:
            return t_id_list[0]

    def getTaskId(self, sequence='', shot='', step='', task_name='', model="shot"):
        '''获取任务模块的ID'''
        if model == "shot":
            t_id_list = self.tw2.task.get_id(
                self.database, model,
                [['shot.eps_name', '=', sequence], 'and', ["shot.shot", "=", shot], 'and',
                 ["task.task_name", "=", task_name]]
            )
        else:
            t_id_list = self.tw2.task.get_id(
                self.database, "asset",
                [['asset.type_name', '=', sequence], 'and', ["asset.asset_name", "=", shot], 'and',
                 ["task.task_name", "=", task_name], 'and', ["task.pipeline", "=", step]]
            )

        if t_id_list:
            return t_id_list[0]

    def getAssets(self):
        '''
        得到所有的资产，并以资产类型进行分类：
        {u'char': [u'TestCharDog', u'charFishC'],
         u'prop': [u'propProduceBag', u'propCartShellB'],
         u'set': [u'setStreetBuildingA', u'setMarketStreet']}
        @return: dict
        '''
        t_asset_id_list = self.tw2.info.get_id(
            self.database, 'asset', [['asset.asset_name', 'has', '%']]
        )
        t_asset_list = self.tw2.info.get(
            self.database, 'asset', t_asset_id_list, ['asset.asset_name', "asset.type_name"]
        )
        asset_types = self.assetTypes()
        result = {i: [] for i in asset_types}
        if t_asset_list:
            for asset in t_asset_list:
                result[asset["asset.type_name"]].append(asset["asset.asset_name"])

        return result

    def getAssetTask(self, asset_type='', asset_name='', task_id_ls='', load_label=False):
        '''
        [{'asset.asset_name': u'charHei',
          'asset.type_name': u'char',
          'id': u'75A4620D-1CED-7013-1C86-CFD252F5E541',
          'task.artist': u'\u674e\u5a67',},
          ...
          ]
        '''
        filters = [i.get("sign") for i in self.config_data.get("global").get("asset_load")]
        filters.append('asset.type_name')

        if task_id_ls:
            task_data = self.tw2.task.get(self.database, "asset", task_id_ls, filters)
        else:
            t_id_list = self.tw2.task.get_id(
                self.database, 'asset',
                [['asset.type_name', '=', asset_type], 'and', ["asset.asset_name", "=", asset_name]]
            )
            task_data = self.tw2.task.get(self.database, "asset", t_id_list, filters)

        if not load_label:
            return task_data

        else:
            new_task_data = task_data[:]
            task_data = []
            # task_dic: {'asset.asset': None, 'asset.cn_name': None, 'asset.type_name': u'char', ...}
            for task_dic in new_task_data:
                for sign in task_dic.keys():
                    # asset_load: [{label: asset name, sign: "asset.asset_name", show: true}, {...}]
                    asset_load = self.config_data.get("global").get("asset_load")
                    for i in asset_load:
                        if i.get("sign") == sign:
                            task_dic[sign] = (task_dic.get(sign), i.get("label"))
                task_data.append(task_dic)

            return task_data

    def getSeqs(self):
        '''
        得到所有的场次
        @return: lsit
        '''
        t_id_list = self.tw2.info.get_id(self.database, 'eps', [["eps.eps_name", "has", "%"]])
        t_data = self.tw2.info.get(self.database, "eps", t_id_list, ['eps.eps_name'])

        return sorted([i['eps.eps_name'] for i in t_data])

    def getShots(self, sequence):
        '''
        得到场次的所有镜头号：[u'Shot010', u'Shot020', u'Shot030']
        @param sequence: 场次
        @return: list
        '''
        if sequence:
            t_id_list = self.tw2.info.get_id(self.database, 'shot', [["eps.eps_name", "=", sequence]])
            shot_list = self.tw2.info.get(self.database, 'shot', t_id_list, ['shot.shot'])
            return sorted([i["shot.shot"] for i in shot_list])
        else:
            return False

    def getShotTask(self, sequence='', shot='', task_id_ls='', load_label=''):
        filters = [i.get("sign") for i in self.config_data.get("global").get("shot_load")]
        filters.append('task.pipeline')
        if task_id_ls:
            task_data = self.tw2.task.get(self.database, "shot", task_id_ls, filters)
        else:
            t_id_list = self.tw2.task.get_id(
                self.database, 'shot', [['shot.eps_name', '=', sequence], 'and', ["shot.shot", "=", shot]]
            )
            task_data = self.tw2.task.get(self.database, "shot", t_id_list, filters)

        if not load_label:
            return task_data

        else:
            new_task_data = task_data[:]
            task_data = []
            for task_dic in new_task_data:
                for sign in task_dic.keys():
                    shot_load = self.config_data.get("global").get("shot_load")
                    for i in shot_load:
                        if i.get("sign") == sign:
                            task_dic[sign] = (task_dic.get(sign), i.get("label"))
                task_data.append(task_dic)
            return task_data

    def getPathFromTag(self, type="", sequence="", shot="", tag=""):
        '''
        根据目录标签，得到对应的完整路径
        '''
        if type == "shot":
            id_list = self.tw2.info.get_id(self.database, type,
                                           [["shot.shot", "=", shot], 'and', ['shot.eps_name', '=', sequence]])
        else:
            id_list = self.tw2.info.get_id(self.database, type,
                                           [["asset.asset_name", "=", shot], 'and', ['asset.type_name', '=', sequence]])
        if id_list:
            return self.tw2.info.get_dir(self.database, type, id_list, [tag])[0][tag]
        else:
            return None

    def getTaskFromTag(self, type="", sequence="", shot="", tag="", step=''):
        '''
        根据目录标签，获取CGT项目目录的路径
        '''
        if type == "shot":
            id_list = self.tw2.info.get_id(self.database, type,
                                           [["shot.shot", "=", shot], 'and', ['shot.eps_name', '=', sequence]])
        else:
            id_list = self.tw2.info.get_id(self.database, type,
                                           [["asset.asset_name", "=", shot], 'and', ['asset.type_name', '=', sequence]])
        if id_list:
            return self.tw2.info.get_dir(self.database, type, id_list, [tag])[0][tag]
        else:
            return None

    def getShotFrameRange(self, project, shotId=''):
        data = self.tw2.info.get(self.getDataBase(project), 'shot', [shotId], ['shot.first_frame', 'shot.last_frame'])
        if data:
            frm1, frm2 = data[0]['shot.first_frame'], data[0]['shot.last_frame']
            return frm1, frm2
        else:
            return '', ''

    def doesVersionExist(self, info, project=os.environ.get('XSYH_PROJECT')):
        '''
        检查version模块中是否存在该信息，存在返回信息ID，不存在返回False
        '''
        id_list = self.tw2.info.get_id(self.database, 'version', [['version.sequence', "=", info['sequence']],
                                                                  ['version.shot', "=", info['shot']],
                                                                  ['version.step', "=", info['step']],
                                                                  ['version.task_name', "=", info['task_name']],
                                                                  ['version.name', "=", info['name']],
                                                                  ['version.version_type', "=", info['version_type']]]
                                       )
        if id_list:
            data = self.tw2.info.get(self.getDataBase(project), 'version', id_list, ['version.id'])
            return data[0]['version.id']
        else:
            return False

    def updateVersionInfo(self, version_id, info, project=os.environ.get('XSYH_PROJECT')):
        '''
        更新version模块中的字段数据，
        '''
        exist_filters = self.tw2.info.fields(self.getDataBase(project), "version")
        new_info = dict()
        for key, val in info.iteritems():
            if 'version.' + key in exist_filters:
                new_info['version.' + key] = val
        self.tw2.info.set(self.getDataBase(project), 'version', [version_id], new_info)

    def createVersion(self, info, project=os.environ.get('XSYH_PROJECT')):
        '''
        在version模块创建信息
        '''
        exist_filters = self.tw2.info.fields(self.getDataBase(project), "version")
        new_info = dict()
        for key, val in info.iteritems():
            if 'version.' + key in exist_filters:
                new_info['version.' + key] = val
        self.tw2.info.create(self.getDataBase(project), 'version', new_info, True)

    def getVersion(self, info, sign, project=os.environ.get('XSYH_PROJECT')):
        '''
        检查version模块中是否存在该信息，存在返回信息ID，不存在返回False
        @param project:
        @return:
        '''
        id_list = self.tw2.info.get_id(self.database, 'version', [['version.sequence', "=", info['sequence']],
                                                                  ['version.shot', "=", info['shot']],
                                                                  ['version.step', "=", info['step']],
                                                                  ['version.task_name', "=", info['task_name']],
                                                                  ['version.name', "=", info['name']]]
                                       )
        if id_list:
            data = self.tw2.info.get(self.getDataBase(project), 'version', id_list, ['version.{}'.format(sign)])
            return data[0]['version.{}'.format(sign)]
        else:
            return False


if __name__ == '__main__':
    cgt = CGT("LongGong")
    # pprint(cgt.getShotTask("Seq001", "Shot010", load_label=True))
    # pprint(cgt.getAssetTask("char", "charHei"))
    # print cgt.getTaskFromTag("shot", "Seq001", "Shot010", "Animation_publish")
    print cgt.getShotFrameRange('LongGongTest', 'A72FCEBF-FA63-2DF1-4279-57A87EBE3ABB')
