# -*- coding:utf-8 -*-
# ==============================================================

# !/usr/bin/env python
#
# @Author: RunningMan
# @File: _cgteamwork.py.py
# @Create Time: 2019/12/30 0030 20:41
# ==============================================================

import sys

sys.path.append("C:/cgteamwork/bin/base")
import cgtw
import cgtw2


# ------------------------------- Class -------------------------------
class CGT(object):

    def __init__(self, proj_name):
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

    def getDataBase(self, proj_name=""):
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
        return result

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

    def getAssetTask(self, asset_type, asset_name):
        pass

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

    def getShotTask(self, seq, shot):
        filter = ['task.pipeline', 'task.task_name', 'shot.eps_name', 'shot.shot', 'task.artist', 'task.account']
        t_id_list = self.tw2.task.get_id(
            self.database, 'shot', [['shot.eps_name', '=', seq], 'and', ["shot.shot", "=", shot]]
        )
        task_data = self.tw2.task.get(self.database, "shot", t_id_list, filter)
        return task_data


if __name__ == '__main__':
    from pprint import pprint
    cgt = CGT("LongGong")
    pprint(cgt.getShotTask("Seq001", "Shot010"))
