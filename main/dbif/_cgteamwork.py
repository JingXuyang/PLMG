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

sys.path.append("C:/cgteamwork/bin/base")
import engine
import cgtw
import cgtw2

# ================================= Global variable =================================
config_data = engine.getConfigs()


# ================================= Class =================================
class CGT(object):

    def __init__(self, proj_name=os.environ.get('XSYH_PROJECT')):
        self.tw = cgtw.tw()
        self.tw2 = cgtw2.tw()
        self.proj_name = proj_name
        self.database = self.getDataBase(self.proj_name)

    def islogind(self):
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

    def getInfoId(self, seq, shot, model="shot"):
        if model == "shot":
            t_id_list = self.tw2.info.get_id(
                self.database, model, [['shot.eps_name', '=', seq], 'and', ["shot.shot", "=", shot]]
            )
        else:
            t_id_list = self.tw2.info.get_id(
                self.database, "asset", [['asset.type_name', '=', seq], 'and', ["asset.asset_name", "=", shot]]
            )
        if t_id_list:
            return t_id_list[0]

    def getTaskId(self, seq='', shot='', step='', task='', model="shot"):
        if model == "shot":
            t_id_list = self.tw2.task.get_id(
                self.database, model,
                [['shot.eps_name', '=', seq], 'and', ["shot.shot", "=", shot], 'and', ["task.task_name", "=", task]]
            )
        else:
            t_id_list = self.tw2.task.get_id(
                self.database, "asset", [['asset.type_name', '=', seq], 'and', ["asset.asset_name", "=", shot], 'and',
                                         ["task.task_name", "=", task], 'and', ["task.pipeline", "=", step]]
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

    def getAssetTask(self, asset_type, asset_name, load_label=False):
        '''
        [{'asset.asset_name': u'charHei',
          'asset.type_name': u'char',
          'id': u'75A4620D-1CED-7013-1C86-CFD252F5E541',
          'task.artist': u'\u674e\u5a67',},
          ...
          ]
        '''
        extend_filters = ['task.pipeline', 'task.task_name', 'asset.type_name', 'asset.asset_name', 'task.artist',
                          'task.account']
        filters = [i.get("sign") for i in config_data.get("global").get("asset_load")]
        filters.extend(extend_filters)
        t_id_list = self.tw2.task.get_id(
            self.database, 'asset', [['asset.type_name', '=', asset_type], 'and', ["asset.asset_name", "=", asset_name]]
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
                    asset_load = config_data.get("global").get("asset_load")
                    for i in asset_load:
                        if i.get("sign") == sign:
                            task_dic[sign] = (task_dic.get(sign), i.get("label"))
                task_data.append(task_dic)

            return task_data

    def getSeqs(self):
        '''
        得到所有的场次：[u'Mrk000', u'Seq001', u'Seq040']
        @return:
        '''
        t_id_list = self.tw2.info.get_id(self.database, 'eps', [["eps.eps_name", "has", "%"]])
        t_data = self.tw2.info.get(self.database, "eps", t_id_list, ['eps.eps_name'])

        return sorted([i['eps.eps_name'] for i in t_data])

    def getShots(self, seq):
        '''
        得到场次的所有镜头号：[u'Shot010', u'Shot020', u'Shot030']
        @param seq: 场次
        @return: list
        '''
        if seq:
            t_id_list = self.tw2.info.get_id(self.database, 'shot', [["eps.eps_name", "=", seq]])
            shot_list = self.tw2.info.get(self.database, 'shot', t_id_list, ['shot.shot'])
            return sorted([i["shot.shot"] for i in shot_list])
        else:
            return False

    def getShotTask(self, seq, shot, load_label=False):
        extend_filters = ['task.pipeline', 'task.task_name', 'shot.eps_name', 'shot.shot', 'task.artist',
                          'task.account']
        filters = [i.get("sign") for i in config_data.get("global").get("shot_load")]
        filters.extend(extend_filters)
        t_id_list = self.tw2.task.get_id(
            self.database, 'shot', [['shot.eps_name', '=', seq], 'and', ["shot.shot", "=", shot]]
        )
        task_data = self.tw2.task.get(self.database, "shot", t_id_list, filters)

        if not load_label:
            return task_data

        else:
            new_task_data = task_data[:]
            task_data = []
            for task_dic in new_task_data:
                for sign in task_dic.keys():
                    shot_load = config_data.get("global").get("shot_load")
                    for i in shot_load:
                        if i.get("sign") == sign:
                            task_dic[sign] = (task_dic.get(sign), i.get("label"))
                task_data.append(task_dic)
            return task_data


if __name__ == '__main__':
    from pprint import pprint

    cgt = CGT("LongGong")
    # pprint(cgt.getShotTask("Seq001", "Shot010", load_label=True))
    # pprint(cgt.getAssetTask("char", "charHei"))
