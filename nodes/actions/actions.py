# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Author: RunningMan
#  @File: actions.py
#  @Create Time: 2020/3/30 15:15
# ==============================================================
import copy
import glob
import json
import os
import pprint
import re
import shutil
import sys
import time
from PySide import QtGui

sys.path.append("C:/cgteamwork/bin/base")

import cgtw
import cgtw2
import dbif
import swif
from nodes import engine
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om

Action = engine.ActionEngine
mask = "spiderhuds"
PLUG_IN_NAME = "spiderhuds.py"
TRANSFORM_NODE_NAME = "spiderhuds"
NODE_NAME = "spiderhuds"
SHAPE_NODE_NAME = "spiderhuds_shape"


def makeFolder(path):
    if os.path.exists(path) or os.path.exists(os.path.dirname(path)):
        return

    if not os.path.splitext(path)[1]:
        os.makedirs(path)
    else:
        os.makedirs(os.path.dirname(path))


def copyFile(src, dst):
    src = src.replace('\\', '/')
    dst = dst.replace('\\', '/')
    if os.path.exists(src) and src != dst:
        shutil.copyfile(src, dst)


def getFileMd5(path):
    import md5

    if os.path.isfile(path):
        f = open(path, 'rb')
        txt = f.read()
        f.close()

        result = md5.new(txt)
        return result.hexdigest()


def unloadPlugin():
    '''
    load eyeBallNode.py plugin ,
    when playblast is beging,
    the maya will be stuck
    '''
    allPlugin = cmds.pluginInfo(q=True, listPlugins=True)
    if 'eyeBallNode' in allPlugin:
        cmds.unloadPlugin('eyeBallNode.py', force=True)


def loadPlugin():
    cmds.loadPlugin('eyeBallNode.py')


def current_file():
    '''Z:/char_test_v001.mb'''
    return swif.software().filepath()


def current_filename():
    '''char_test_v001.mb'''
    return os.path.basename(swif.software().filepath())


def current_file_basename():
    '''char_test_v001'''
    return os.path.basename(swif.software().filepath()).split('.')[0]


class Tip(QtGui.QWidget):
    def __init__(self, message, parent=None):
        super(Tip, self).__init__(parent)

        QtGui.QMessageBox.information(self, "Tip", message, QtGui.QMessageBox.Yes)


class IsSceneUntitled(Action):

    def run(self):
        sw = self.software()
        if sw:
            if sw.isUntitled():
                text = 'Please save the sence first!'
                text = u'请先保存文件!'

                return text


# 获取文件夹下最新的文件的版本号，升级一个版本号
class FakeVersionUp(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        path = self.parm('input')
        # print "path:",path
        lists = os.listdir(path)
        lists.sort(key=lambda fn: os.path.getmtime(path + "\\" + fn))
        for i in lists:
            if ".mb" not in i:
                lists.remove(i)
        # print "lists:",lists
        if not lists:

            Tip('The Work File is not submit !\n Plesae Sumbmit workfile as first.')

            return
        else:
            name_ls = lists[-1].split(".")[0].split("_")
            latest_file = lists[-1].split(".")[0].split("_")[-1]
            version = latest_file
            # version = "v"+str(int(version)+1).zfill(3)
            name_ls[-1] = version

            fileName = "_".join(name_ls) + ".mb"
            return fileName


class CurrenrFilename(Action):
    def run(self):
        return cmds.file(q=1, location=1)


class DelTweakNode(Action):
    def run(self):
        for i in cmds.ls(type="mesh", long=True):
            if "|model_GRP" in i:
                tweak_node = cmds.listConnections(i, type="tweak")
                if tweak_node:
                    cmds.delete(tweak_node)
        return "OK"


# 返回没有版本号的文件名
class cutVersion(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        import os
        name_ls = os.path.splitext(self.parm('input'))[0].split("_")
        new_ls = name_ls[:3]
        new_name = "_".join(new_ls) + os.path.splitext(self.parm('input'))[1]
        return new_name


# 拷贝文件
class copyMovies(Action):
    _defaultParms = {
        'root': '',
        'current': '',
        'target': '',
    }

    def run(self):
        # print self.parm('root'),self.parm('current'),self.parm('target')
        root = self.parm('root')
        for dirpath, dienames, filenames in os.walk(root):
            for i in filenames:
                if self.parm('current') not in i:
                    # print "sorce:",os.path.join(dirpath, i).replace("\\","/")
                    # print "target:",self.parm('target')
                    try:
                        os.rename(os.path.join(dirpath, i).replace("\\", "/"), self.parm('target') + "/" + i)
                    except:
                        pass
        return "OK"


# 拷贝到target文件夹之前， 先把文件夹里的所有文件删除掉再拷贝
class ClearMoviesBeforeCopy(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        target = self.parm('target')

        # 不存在approved movies文件夹， 创建文件夹返回
        if not os.path.exists(target):
            makeFolder(target)
            return

        to_remove_file = list()
        for filenames in os.listdir(target):
            files = os.path.join(target, filenames)
            if os.path.isfile(files) and os.path.splitext(files)[-1] == ".mov":
                try:
                    os.remove(target + "/" + filenames)
                except:
                    to_remove_file.append(files)
        if to_remove_file:
            Tip(u"请让生成该文件%s的人删除这个文件" % (','.join(to_remove_file)))
            return


class DoesVersionExisted(Action):
    _defaultParms = {
        'version': '{workfile_version}',
        'version_type': 'publish',
        'other_filters': []
    }

    def run(self):
        vn = self.parm('version')
        # print
        # print 'version:',vn

        versionType = self.parm('version_type')

        filters = [
            ['project', '=', self.database().getDataBase()],
            ['pipeline_type', '=', self.task().get('type')],
            ['type', '=', self.task().get('type')],
            ['sequence', '=', self.task().get('sequence')],
            ['shot', '=', self.task().get('shot')],
            ['asset_type', '=', self.task().get('asset_type')],
            ['asset', '=', self.task().get('asset')],
            ['task', '=', self.task().get('code')],
            ['version_type', '=', versionType],
            ['version', '=', vn]
        ]

        other = self.parm('other_filters')
        if not other:
            other = []
        filters += other

        # print
        # print 'filters:'
        # print filters

        r = self.database().doesVersionExist(self.database().getDataBase(), filters)

        if r:
            txt = u'版本 %s 已经提交过了，请升级版本再提交' % vn
            return txt


class DoesAnimationVersionExisted(Action):
    _defaultParms = {
        'version': '{workfile_version}',
        'version_type': 'publish',
    }

    def run(self):
        vn = self.parm('version')
        versionType = self.parm('version_type')

        filters = [
            ['project', '=', self.database().getDataBase()],
            ['pipeline_type', '=', self.task().get('type')],
            ['type', '=', self.task().get('type')],
            ['sequence', '=', self.task().get('sequence')],
            ['shot', '=', self.task().get('shot')],
            # ['asset_type', '=', self.task().get('asset_type')],
            ['task', '=', self.task().get('code')],
            ['version_type', '=', versionType],
            ['version', '=', vn]
        ]

        result = []
        for info in self.engine().getInputData():
            group = info['instance']

            theFilters = copy.deepcopy(filters)
            theFilters.append(['part', '=', group])
            theFilters.append(['asset', '=', info['asset']])

            # print 'filters:',theFilters

            r = self.database().doesVersionExist(self.database().getDataBase(), theFilters)

            if r:
                t = '    %s_%s' % (group, vn)
                if t not in result:
                    result.append(t)

        if result:
            txt = u'以下资产已经提交过了，请升级版本再提交:\n'
            txt += '\n'.join(result)
            return txt


class Condition(Action):

    def run(self):
        key = self.parm('key')
        condition = self.parm('condition')
        value = self.parm('value')

        if condition == 'in':
            return key in value


class CheckTaskStatus(Action):

    def run(self):
        kwargs = {
            'project': self.database().getDataBase(),
            'type': self.task().get('type'),
            'taskId': self.task().get('task_id')
        }
        status = self.database().getTaskStatus(**kwargs)
        value = self.parm('value')

        if not value:
            value = []

        if value:
            if status not in value:
                text = u'该任务状态为 %s , 不能提交任务\n' % status
                text += u'可以提交文件的任务状态为:\n'
                text += '\n'.join(value)

                return text


class Boolean(Action):
    _defaultParms = {
        'input': ''
    }

    def run(self):
        if self.parm('input'):
            return 1
        else:
            return 0


class WorkfileException(Exception):
    pass


def showWorkfileError(sw):
    try:
        msg = sys.exc_value.message
    except:
        msg = 'file error'
    raise WorkfileException(msg)


class NewScene(Action):
    progressText = 'Creating a new scene...'

    def run(self):
        sw = self.software()
        if sw:
            try:
                sw.new(force=True)
            except:
                showWorkfileError(sw)


class OpenScene(Action):
    progressText = 'Opening a scene...'

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('input')
            # print 'path:',path
            try:
                sw.open(path, force=True)
            except:
                showWorkfileError(sw)

            return path


class ImportScene(Action):

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('input')
            # print 'path:',path

            try:
                sw.import_(path, removeNamespace=True)
            except:
                showWorkfileError(sw)

            return path


def _reference(sw, info, createSets=True, configs={}, groupOption=None,
               displayMode=None):
    # print
    # print 'info:',info

    if info:
        if type(info) == dict:
            path = info['path']

            if not os.path.isfile(path):
                return

            if info.get('part') == 'camera':
                res = info.get('resolution')
                ref = sw.referenceCamera(path, resolution=res)

            elif info.get('part') == 'material':
                ref = sw.importMaterials(path, configs=configs)

            else:
                if info['filetype'] == 'gpu':
                    ref = sw.importGpuCache(path)
                elif info['filetype'] == 'ass':
                    ref = sw.referenceAssembly(path)
                else:
                    ref = sw.reference(path, groupOption=groupOption,
                                       displayMode=displayMode)

            # Create sets for a model
            # print 'sets:',info.get('sets')
            if createSets:
                sw.createSets(info.get('sets'), namespace=ref['namespace'])

            return ref

        elif type(info) in (str, unicode):
            if not os.path.isfile(info):
                return

            ref = sw.reference(info)
            return ref


class ReferenceScene(Action):
    '''
    References the input file in the current scene.
    group_option is for the group info of Houdini alembic node.
        0: No Group
        1: Shape Node Full Path
        2: Transform Node Full Path
        3: Shape Node Name
        4: Transform Node Name

    display_mode is for display mode of Houdini alembic node:
        0: Full Geometry
        1: Point Cloud
        2: Bounding Box
        3: Centroid
        4: Hidden
    '''

    _defaultParms = {
        'input': '',
        'create_sets': False,
        'group_option': None,
        'display_mode': None
    }

    def run(self):
        sw = self.software()
        if sw:
            info = self.parm('input')
            key = self.parm('returned_key')
            res = self.parm('resolution')

            createSets = self.parm('create_sets')
            kwargs = {
                'sw': sw,
                'info': info,
                'createSets': createSets
            }
            groupOption = self.parm('group_option')
            if groupOption != None:
                kwargs['groupOption'] = groupOption

            displayMode = self.parm('display_mode')

            if displayMode != None:
                kwargs['displayMode'] = displayMode
                # print kwargs+"!!!!!!!!!!!!!!!"
            # print kwargs
            return _reference(**kwargs)


def _reference2(sw, info, createSets=True, configs={}, groupOption=None,
                displayMode=None):
    # print
    # print 'info:',info

    if info:
        if type(info) == dict:
            path = info['path']

            if not os.path.isfile(path):
                return

            if info.get('part') == 'camera':
                res = info.get('resolution')
                # ref = sw.referenceCamera(path, resolution=res,)
                ref = sw.reference(path, getTopObj=False)

            elif info.get('part') == 'material':
                if info['asset_type'] == 'set':
                    folder = os.path.dirname(path)
                    newPath = "%s/%s_tex_ENVIR.ma" % (folder, info['asset'])
                    if os.path.isfile(newPath):
                        path = newPath

                ref = sw.reference(path, getTopObj=False)

            else:
                if info['filetype'] == 'gpu':
                    ref = sw.importGpuCache(path)
                elif info['filetype'] == 'ass':
                    ref = sw.referenceAssembly(path)
                else:
                    # print "info:",info
                    if info['asset_type'] == 'set':
                        # print "info:",info
                        folder = os.path.dirname(path)
                        newPath = "%s/%s_model_ENVIR.abc" % (folder, info['asset'])

                        if os.path.isfile(newPath):
                            path = newPath

                    ref = sw.reference(path, groupOption=groupOption,
                                       displayMode=displayMode, getTopObj=False)

            # Create sets for a model
            # print 'sets:',info.get('sets')
            if createSets:
                sw.createSets(info.get('sets'), namespace=ref['namespace'])

            return ref

        elif type(info) in (str, unicode):
            if not os.path.isfile(info):
                return

            ref = sw.reference(info)
            return ref


class ReferenceScene2(Action):
    '''
    References the input file in the current scene.
    group_option is for the group info of Houdini alembic node.
        0: No Group
        1: Shape Node Full Path
        2: Transform Node Full Path
        3: Shape Node Name
        4: Transform Node Name

    display_mode is for display mode of Houdini alembic node:
        0: Full Geometry
        1: Point Cloud
        2: Bounding Box
        3: Centroid
        4: Hidden
    '''

    _defaultParms = {
        'input': '',
        'create_sets': False,
        'group_option': None,
        'display_mode': None
    }

    def run(self):
        sw = self.software()
        if sw:
            info = self.parm('input')
            key = self.parm('returned_key')
            res = self.parm('resolution')

            createSets = self.parm('create_sets')
            kwargs = {
                'sw': sw,
                'info': info,
                'createSets': createSets
            }
            groupOption = self.parm('group_option')
            if groupOption != None:
                kwargs['groupOption'] = groupOption

            displayMode = self.parm('display_mode')

            if displayMode != None:
                kwargs['displayMode'] = displayMode
                # print kwargs+"!!!!!!!!!!!!!!!"
            # print kwargs
            return _reference2(**kwargs)


# 获取重复的reference文件
class getExtraRF(Action):
    def run(self):
        import os
        import maya.cmds as cmds
        A = {}
        rf = cmds.ls(rf=1)
        if len(rf) >= 2:
            # print rf[1]
            path = os.path.dirname(cmds.referenceQuery(rf[1], filename=True))
            # print path,"!!!!!!!!!!!!!!"
            # list all the files in the dir
            file_list = []
            for j in os.listdir(path):
                file_list.append(j.split(".")[0])
                # reanme rf
            rf_ls = []
            for i in rf:
                rf_ls.append(i.split(".")[0].replace("RN", ""))
            # difference of files and rf
            file_rf = [i for i in file_list if i not in rf_ls]
            # need to rf
            B = []
            for i in rf_ls:
                for j in file_rf:
                    if i in j:
                        B.append(j)
                        A[j.split("_")[-1][:-1]] = B
                B = []
        else:
            pass
        return A


# reference文件夹下重复的带有数字的文件
class ReferenceExtra(Action):

    def run(self):
        import os
        import maya.cmds as cmds
        ge = getExtraRF(self)
        a = ge.run()
        if len(a) != 0:
            for i in a:
                for j in a[i]:
                    rf = cmds.ls(rf=1)
                    path = os.path.dirname(cmds.referenceQuery(rf[1], filename=True))
                    cmds.file(path + "/" + j + ".abc", r=1, type="Alembic", ignoreVersion=1, gl=1,
                              mergeNamespacesOnClash=0, namespace=":")
        else:
            pass
        return a


class RemoveReference(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        sw = self.software()
        if sw:
            refPath = self.parm('input')
            sw.removeReference(refPath)

            return refPath


class RemoveSceneObject(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        sw = self.software()
        if sw:
            obj = self.parm('input')
            sw.delete(obj)

            return obj


class AssignMaterials(Action):
    _defaultParms = {
        'input': '',
        'geo': '',
        'create_sets': False,
        'configs': {},
        'extra_RF': ''
    }

    def run(self):
        sw = self.software()
        if sw:
            materials = self.parm('input')
            if type(materials) == dict and materials:
                # Reference materials
                # print 'materials:',materials
                geoNamespace = self.parm('geo').get('namespace')
                createSets = self.parm('create_sets')
                key = self.parm('returned_key')

                info = _reference(sw, materials, createSets=False,
                                  configs=self.parm('configs'))
                if info:
                    matNamespace = info['namespace']
                    # print 'matNamespace:',matNamespace

                    # Assign materials
                    # print
                    # print 'Mapping:'
                    # print materials['mapping']
                    # print geoNamespace, matNamespace, 2222222
                    matNode = sw.assignMaterials(materials.get('mapping'),
                                                 self.parm('extra_RF'),
                                                 geoNamespace=geoNamespace,
                                                 matNamespace=matNamespace)
                    info['material_node'] = matNode

                if createSets:
                    sw.createSets(materials.get('sets'), namespace=geoNamespace)

                return info


def assignMaterials2(
        mapping,
        geoNamespace='',
        matNamespace='',
        useShortName=False):
    '''
    mapping is a dictionary or a file with geometry and materials mapping.

    Example of mapping:
        {
            "blinn1SG": {
                "|dog|base|box|boxShape": [
                    "|box.f[0:5]",
                    "|box.f[7:9]"
                ]
            },
            "blinn2SG": {
                "|dog|base|pCone1|pConeShape1": []
            }
        }

        {
            "blinn1SG": {
                "|dog|base|body|bodyShape": [
                    "|body.f[200:359]",
                    "|body.f[380:399]"
                ]
            },
            "blinn2SG": {
                "|dog|base|body|bodyShape": [
                    "|body.f[0:199]",
                    "|body.f[360:379]"
                ]
            }
        }
    '''

    errorLog = []
    for SG, meshInfo in mapping.iteritems():

        refSG = "%s:%s" % (matNamespace, SG)
        for shape, faces in meshInfo.iteritems():
            if faces:
                faceList = []
                for f in faces:

                    f = f[1:]  # remove first "|"
                    if useShortName:
                        if geoNamespace:
                            f = f.replace('|', '|%s:' % geoNamespace)
                        f = f.rsplit('|', 1)[-1]
                    else:
                        sp = shape.rsplit('|', 1)[0]
                        parent = sp.rsplit('|', 1)[0]
                        f = parent + '|' + f

                        if geoNamespace:
                            f = f.replace('|', '|%s:' % geoNamespace)
                        f = f.rsplit('|', 1)[-1]

                    faceList.append(f)
                obj = faceList
            else:

                obj = shape.rsplit('|', 1)[0]
                if geoNamespace:
                    obj = obj.replace('|', '|%s:' % geoNamespace)
                obj = obj[1:]  # remove first "|"

                if useShortName:
                    obj = obj.rsplit('|', 1)[-1]

            try:
                cmds.sets(obj, e=True, forceElement=refSG)
            except:
                r = '----------------------------------------------' + '\n'
                r += "refSG:  " + refSG + '\n'
                r += "  obj:  " + str(obj) + '\n'
                r += 'refSG ,obj, assign materials failed!!!'
                errorLog.append(r)
    return errorLog


class AssignMaterials2(Action):
    _defaultParms = {
        'input': '',
        'geo': '',
        'create_sets': False,
        'configs': {},
        'extra_RF': ''
    }

    def run(self):
        sw = self.software()
        if sw:
            materials = self.parm('input')
            if type(materials) == dict and materials:
                # Reference materials
                # print 'materials:',materials
                geoNamespace = self.parm('geo').get('namespace')
                createSets = self.parm('create_sets')
                key = self.parm('returned_key')
                # print 'materials:',materials
                info = _reference2(sw, materials, createSets=False)
                if info:
                    matNamespace = info['namespace']
                    # print 'matNamespace:',matNamespace

                    # Assign materials
                    # print
                    # print 'Mapping:'
                    # print materials['mapping']
                    # print geoNamespace, matNamespace, 2222222
                    mapping = materials.get('mapping')

                    if materials['asset_type'] == 'set':
                        matPath = info['path']

                        pathList = os.path.splitext(matPath)

                        mapPath = "%s_mapping.json" % (pathList[0])
                        # print "mapPath:",mapPath
                        if os.path.isfile(mapPath):
                            with open(mapPath, 'r') as f:
                                read = f.read()
                                mapping = json.loads(read)

                    # print "info['path']:",info['path']

                    # print "self.parm('extra_RF'):",self.parm('extra_RF')
                    errotInfo = assignMaterials2(mapping,
                                                 geoNamespace=geoNamespace,
                                                 matNamespace=matNamespace)
                    # info['material_node'] = matNode

                if createSets:
                    sw.createSets(materials.get('sets'), namespace=geoNamespace)

                return info


class AssignOtherCacheMaterials(Action):
    _defaultParms = {'input': []}

    def getShotLinkedAssets(self, assetType=[]):

        shotInfo = {'id': self.task()['shot_id'],
                    'project': self.task()['project']}

        assetInfo = self.database().getShotLinkedAssets(shotInfo)
        # [{'cn_name': u'\u5c0f\u9ed1\u5bb6',
        # 'code': 'setHeiHouse',
        # 'entity_type': 'asset',
        # 'id': '92FC939F-936E-3563-E681-DB90AE8D1BA7',
        # 'image': '{"min":["/upload/image/proj_longgong_0/min/145ead746ea535ab3c4cad6a37301c61.jpg"],"max":["/upload/image/proj_longgong_0/max/145ead746ea535ab3c4cad6a37301c61.jpg"]}',
        # 'project': 'LongGong',
        # 'sequence': 'set',
        # 'type': 'asset'}] #

        if assetType:
            lis = []
            for astInfo in assetInfo:
                if astInfo['sequence'] in assetType:
                    lis.append(astInfo)

            return lis
        return assetInfo

    def assemblyFileError(self, filePath, des='FilePath'):
        r = "---------------- %s ----------------" % des + '\n'
        r += "%s not find!!!,please check filePath or fileName is right" % (filePath) + '\n'
        r += "---------------- %s ----------------" % des + '\n'
        return r

    def run(self):
        import swif
        sw = swif._maya.Maya()
        errorLog = []

        allData = self.parm('input')

        # print "data:",data
        setInfo = {}

        # assembly camera,nCloth,shotFinal
        for data in allData:
            abcPath = data['abc_path']
            # camera
            if data['type'] == 'Camera':
                if abcPath:
                    sw.reference(abcPath, getTopObj=False)
            # set
            elif data['type'] == 'LightingRig':
                if abcPath:
                    if not setInfo.get(abcPath):
                        setInfo[abcPath] = [data]
                    else:
                        setInfo[abcPath].append(data)

            else:
                if abcPath:
                    info = sw.reference(data['abc_path'], getTopObj=False)
                    geoNamespace = info['namespace']

                    matPath = data['mat_path']
                    if matPath:
                        matInfo = sw.reference(matPath, getTopObj=False)
                        matNamespace = matInfo['namespace']

                        mapPath = data['map_path']
                        if mapPath:
                            with open(mapPath, 'r') as f:
                                read = f.read()

                                mapping = json.loads(read)

                                errorInfo = assignMaterials2(mapping,
                                                             geoNamespace=geoNamespace,
                                                             matNamespace=matNamespace)
                                if errorInfo:
                                    errorLog += errorInfo

        # assembly set
        # one abc, more set materials

        for abcPath, inf in setInfo.iteritems():
            info = sw.reference(abcPath, getTopObj=False)
        '''
            geoNamespace = info['namespace']
        
            for m in inf:
                matPath = m['mat_path']
                mapPath = m['map_path']
                
                if matPath:
                    matInfo = sw.reference(matPath,getTopObj=False)
                    matNamespace = matInfo['namespace']
                    
                    if mapPath:
                        with open(mapPath,'r') as f:
                            read = f.read()
                            
                            mapping = json.loads(read)
                            
                            errorInfo2 = assignMaterials2(  mapping,
                                                            geoNamespace=geoNamespace,
                                                            matNamespace=matNamespace)
                            if errorInfo2:
                                errorLog += errorInfo2
        '''
        if errorLog:
            errorLog = '\n'.join(errorLog)

            print errorLog

    def run_bak(self):
        errorLog = []

        import swif
        sw = swif._maya.Maya()

        shot = self.task()['shot']
        seq = self.task()['sequence']

        # camera abc
        cameraPath = 'Z:/LongGong/sequences/{seq}/{shot}/animation/approved/scenes/{seq}_{shot}_Ani_camera.abc'.format(
            seq=seq, shot=shot)
        # cameraPath = glob.glob(cameraPath)
        if not os.path.exists(cameraPath):
            errorLog.append(self.assemblyFileError(cameraPath, "cameraPath"))
        else:
            sw.reference(cameraPath, getTopObj=False)

        #####################################################################################################
        # nCloth abc

        modulePath = 'Z:/LongGong/sequences/{seq}/{shot}/Cache/nCloth/approved/*.abc'.format(seq=seq, shot=shot)

        refs = sw.getReferences()
        abcPaths = [r['path'] for r in refs if r['path'].endswith('.abc')]

        allAbc = glob.glob(modulePath)

        for cache in allAbc:
            cache = cache.replace('\\', '/')
            if cache not in abcPaths:
                # print "cache:",cache
                abcInfo = sw.reference(cache, getTopObj=False)
                # geoNamespace
                geoNamespace = abcInfo['namespace']

                fileName = os.path.basename(cache).split('.')[0]
                assetName = fileName.split('_')[-1]
                num = re.findall('\d+$', assetName)
                if num:
                    l = len(num[0])
                    assetName = assetName[:-l]

                if assetName.startswith('char'):
                    assetType = 'char'
                elif assetName.startswith('set'):
                    assetType = 'set'
                elif assetName.startswith('prop'):
                    assetType = 'prop'
                #
                mappingPath = "Z:/LongGong/assets/{asset_type}/{asset_name}/surface/approved/"
                mappingPath += "{asset_name}_tex_highTex_mapping.json"
                mappingPath = mappingPath.format(asset_type=assetType, asset_name=assetName)

                if not os.path.exists(mappingPath):
                    errorLog.append(self.assemblyFileError(mappingPath, "mappingPath"))
                else:

                    with open(mappingPath, 'r') as f:
                        read = f.read()
                    # mapping
                    mapping = json.loads(read)

                    matPath = mappingPath.replace('_mapping.json', '.ma')
                    if not os.path.exists(matPath):
                        errorLog.append(self.assemblyFileError(matPath, "matPath"))
                    else:
                        info = sw.reference(matPath, getTopObj=False)

                        # matNamespace
                        matNamespace = info['namespace']

                        errorInfo = assignMaterials2(mapping,
                                                     geoNamespace=geoNamespace,
                                                     matNamespace=matNamespace)
                        if errorInfo:
                            errorLog += errorInfo
        #####################################################################################################
        # shotfinal abc
        SFModulePath = 'Z:/LongGong/sequences/{seq}/{shot}/Cache/shotFinaling/approved/*.abc'.format(seq=seq, shot=shot)

        allAbc2 = glob.glob(SFModulePath)

        for cache in allAbc2:
            cache = cache.replace('\\', '/')
            if cache not in abcPaths:
                # print "cache:",cache
                SFAbcInfo = sw.reference(cache, getTopObj=False)
                # geoNamespace
                SFGeoNamespace = SFAbcInfo['namespace']

                fileName = os.path.basename(cache).split('.')[0]
                assetName = fileName.split('_')[-1]
                num = re.findall('\d+$', assetName)
                if num:
                    l = len(num[0])
                    assetName = assetName[:-l]

                if assetName.startswith('char'):
                    assetType = 'char'
                elif assetName.startswith('set'):
                    assetType = 'set'
                elif assetName.startswith('prop'):
                    assetType = 'prop'
                #
                SFMappingPath = "Z:/LongGong/assets/{asset_type}/{asset_name}/surface/approved/"
                SFMappingPath += "{asset_name}_tex_highTex_mapping.json"
                SFMappingPath = SFMappingPath.format(asset_type=assetType, asset_name=assetName)

                if not os.path.exists(SFMappingPath):
                    errorLog.append(self.assemblyFileError(SFMappingPath, "SFMappingPath"))
                else:

                    with open(SFMappingPath, 'r') as f:
                        SFRead = f.read()
                    # mapping
                    SFMapping = json.loads(SFRead)

                    SFMatPath = SFMappingPath.replace('_mapping.json', '.ma')
                    if not os.path.exists(SFMatPath):
                        errorLog.append(self.assemblyFileError(SFMatPath, "SFMatPath"))
                    else:
                        SFInfo = sw.reference(SFMatPath, getTopObj=False)

                        # matNamespace
                        SFMatNamespace = SFInfo['namespace']

                        errorInfo3 = assignMaterials2(SFMapping,
                                                      geoNamespace=SFGeoNamespace,
                                                      matNamespace=SFMatNamespace)
                        if errorInfo3:
                            errorLog += errorInfo3

        #####################################################################################################
        # set abc
        lightSetPath = 'Z:/LongGong/sequences/{sequence}/lightingRig/approved/scenes/{sequence}_master_lighting_rig.mb'.format(
            sequence=seq)

        if not os.path.exists(lightSetPath):
            errorLog.append(self.assemblyFileError(lightSetPath, 'lightSetPath'))
        else:
            # geoNamespace
            setInfo = sw.reference(lightSetPath, getTopObj=False)
            setGeoNamespace = setInfo['namespace']

            # get link set assets
            setAssets = self.getShotLinkedAssets(assetType=['set'])
            setMapPath = "Z:/LongGong/assets/{asset_type}/{asset_name}/surface/approved/"
            setMapPath += "{asset_name}_tex_ENVIR_mapping.json"

            for setInfo in setAssets:
                setMappingPath = setMapPath.format(asset_type='set', asset_name=setInfo['code'])

                if not os.path.exists(setMappingPath):

                    errorLog.append(self.assemblyFileError(setMappingPath, 'setMappingPath'))
                else:
                    with open(setMappingPath, 'r') as f:
                        setRead = f.read()
                    setMapping = json.loads(read)
                    setMatPath = setMappingPath.replace('_mapping.json', '.ma')

                    if not os.path.exists(setMatPath):

                        errorLog.append(self.assemblyFileError(setMatPath, 'setMatPath'))
                    else:
                        setMatInfo = sw.reference(matPath, getTopObj=False)

                        # matNamespace
                        setMatNamespace = setMatInfo['namespace']

                        errorInfo2 = assignMaterials2(setMapping,
                                                      geoNamespace=setGeoNamespace,
                                                      matNamespace=setMatNamespace)
                        if errorInfo2:
                            errorLog += errorInfo2

        if errorLog:
            errorLog = '\n'.join(errorLog)

            print errorLog


class SetTransform(Action):
    _defaultParms = {
        'input': '',
        'transform': '',
        'subs': []
    }

    def run(self):
        sw = self.software()
        if sw:
            info = self.parm('input')
            transformInfo = self.parm('transform')

            # print
            # print 'input:',info
            # print 'transformInfo:',transformInfo

            if info and transformInfo:
                topObjs = info.get('top_objects')
                if topObjs:
                    obj = topObjs[0]
                else:
                    obj = info['node']
                # print '%s: %s' % (obj, transformInfo)

                try:
                    sw.setTransform(obj, transformInfo)
                except:
                    pass

                subs = self.parm('subs')
                inputNode = self.parm('input_node')
                if type(subs) == list:
                    sw.setSubsTransform(obj, inputNode, subs)


# 添加更改相机的属性， 锁定相机
class SetView(Action):
    '''Sets the view to the given camera or one of the scene cameras.'''

    _defaultParms = {
        'camera': '',
    }

    def run(self):
        import maya.cmds as cmds
        cam = cmds.ls(type="camera")
        for i in cam:
            if cmds.referenceQuery(i, isNodeReferenced=True):
                cmds.setAttr(i + ".displayResolution", 1)
                cmds.setAttr(i + ".displayGateMaskOpacity", 1.000)
                cmds.setAttr(i + ".displayGateMaskColor", 0, 0, 0, type="double3")
        rf = cmds.ls(rf=1)
        for i in rf:
            if "camera" in i:
                cmds.file(unloadReference=i)
                cmds.setAttr("%s.locked" % (i), 1)
                cmds.file(loadReference=i)

        sw = self.software()
        if sw:
            camera = self.parm('camera')
            if camera:
                sw.setView(camera)
            else:
                cams = sw.getCameras()
                if cams:
                    sw.setView(cams[0]['full_path'])


# 除了rig环节， 保存的时候选中所有层架按1， 然后显示线框模式， 关闭抗锯齿
# previs ,layout环节保存时，去除1 显示
class SetLowViwer(Action):
    '''
    Set low viwer mode
    '''

    defaultParms = {
        'wireframe': True,
    }

    def run(self):
        filePath = cmds.file(query=True, location=True)
        if "rig" not in filePath:
            all = cmds.ls(assemblies=True)
            cmds.select(all)

            md = cmds.getPanel(visiblePanels=1)[0]

            if 'previs' not in filePath and 'layout' not in filePath and 'shotFinaling' not in filePath:
                mel.eval(
                    'displaySmoothness -divisionsU 0 -divisionsV 0 -pointsWire 4 -pointsShaded 1 -polygonObject 1;')
            if self.parm('wireframe'):
                cmds.modelEditor(md, edit=True, displayAppearance="wireframe", displayLights="default")
            else:
                cmds.modelEditor(md, edit=True, displayAppearance="smoothShaded")

            # hidden ""

            cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 0)
            cmds.select(clear=True)
        else:
            pass


class CreateCamera(Action):
    '''Imports the camera from the template file or create a new one.'''

    _defaultParms = {
        'template': '',
        'camera_name': '',
    }

    progressText = 'Creating camera from template...'

    def run(self):
        sw = self.software()
        if sw:
            template = self.parm('template')
            cameraName = self.parm('camera_name')

            if os.path.isfile(template):
                sw.import_(template, removeNamespace=True)
                cams = sw.getCameras()
                if cams:
                    cam = cams[0]['full_path']
                    return sw.rename(cam, cameraName)

            else:
                return sw.createCamera(cameraName)[0]


class SaveScene(Action):
    progressText = 'Saving current scene...'

    def run(self):
        format_ = self.parm('format')
        sw = self.software()
        if sw:
            if not sw.isUntitled():
                if format_:
                    # If the format is different with current format
                    # Then save as to target format
                    currentPath = sw.filepath()
                    currentExt = os.path.splitext(currentPath)[1].replace('.', '')
                    if currentExt.lower() == format_.lower():
                        try:
                            sw.save(force=True)
                        except:
                            showWorkfileError(sw)

                    else:
                        currentBasename = os.path.splitext(currentPath)[0]
                        newPath = '%s.%s' % (currentBasename, format_)
                        try:
                            sw.saveAs(newPath, force=True)
                        except:
                            showWorkfileError(sw)

                else:
                    try:
                        sw.save(force=True)
                    except:
                        showWorkfileError(sw)

                return sw.filepath()


class SaveAsScene(Action):
    progressText = 'Saving the scene...'

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('input')
            makeFolder(path)

            try:
                sw.saveAs(path, force=True)

            except:
                showWorkfileError(sw)

            return path


class GetSceneReferences(Action):

    def run(self):
        sw = self.software()
        if sw:
            return sw.getReferenceObjects()

        else:
            return []


class FindSceneObjects(Action):
    _defaultParms = {
        'name': '',
        'namespace': '',
        'type': '',
        'attributes': {},
        'returned_index': None
    }

    def run(self):
        sw = self.software()
        if sw:
            name = self.parm('name')
            namespace = self.parm('namespace')
            type = self.parm('type')
            attris = self.parm('attributes')

            kwargs = {}
            if name:
                kwargs['name'] = name
            if namespace:
                kwargs['namespace'] = namespace
            if type:
                kwargs['type'] = type
            if attris:
                kwargs['attributes'] = attris

            result = sw.find(**kwargs)

        else:
            result = []

        returnedIndex = self.parm('returned_index')
        if returnedIndex == None:
            return result
        else:
            try:
                return result[returnedIndex]
            except:
                return


class HasWriteNode(Action):
    _defaultParms = {
        'name': '',
        'attributes': {},
    }

    def run(self):
        sw = self.software()
        if sw:
            name = self.parm('name')
            type = 'Write'
            attris = self.parm('attributes')

            kwargs = {'type': type}
            if name:
                kwargs['name'] = name
            if attris:
                kwargs['attributes'] = attris

            result = sw.find(**kwargs)

            if not result:
                return 'Can not find Write node!'


class RenameChildren(Action):
    _defaultParms = {
        'input': '',
        'replace': '',
        'to': ''
    }

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('input')
            replace = self.parm('replace')
            replace = replace.replace('/', '\\')
            to = self.parm('to')
            sw.renameChildren(path, replace, to)


class GroupChildrenByNetworkBox(Action):
    '''
    Groups the node children into net work boxes.
    We get the group key by split the node name.
    '''

    _defaultParms = {
        'input': '',
        'splitter': '_',
        'index': 0
    }

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('input')
            splitter = self.parm('splitter')
            index = self.parm('index')

            nodes = sw.getChildren(path)

            temp = {}
            for n in nodes:
                key = n.name().split(splitter)[index]
                if not temp.has_key(key):
                    temp[key] = []
                temp[key].append(n.path())

            for key in temp.keys():
                sw.createNetworkBox(path, name=key, items=temp[key])


class GetSceneObjectChildren(Action):
    _defaultParms = {
        'input': '',
        'type': '',
        'all_subs': False
    }

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('input')
            typ = self.parm('type')
            allSubs = self.parm('all_subs')

            if path:
                if allSubs:
                    return sw.getAllSubChildren(path, type=typ)

                else:
                    temp = sw.getChildren(path, type=typ)

                    return [t.fullPath() for t in temp]

        return []


class CreateSceneHierachy(Action):
    progressText = 'Creating scene hierachy...'

    def run(self):
        sw = self.software()
        if sw:
            # data = self.parm('hierachy')
            data = engine.getStepConfig(self.task()['step'], 'hierachy')
            if data:
                task_name = engine.getTaskFromEnv()['task']
                name_list = ["model", "Model", "Texture", "Rig", "rig", "charEffects"]
                if task_name in name_list:
                    data[0]['name'] = data[0]['name'].format(shot=self.task()['shot'])
                    sw.createHierachy(data)
                    return data


class SetSceneFrameRange(Action):
    _defaultParms = {
        'shot': '',
    }

    progressText = 'Setting scene frame range...'

    def run(self):
        sw = self.software()
        if sw:
            shot = self.parm('shot')
            if shot:
                shotId = shot.get('id')
            else:
                shotId = self.task().get('shot_id')

            kwargs = {
                'project': self.database().getDataBase(),
                'shotId': shotId,
            }
            firstFrame, lastFrame = self.database().getShotFrameRange(**kwargs)

            if firstFrame and lastFrame:
                sw.setFrameRange(firstFrame, lastFrame)


# 根据teamwork的帧数来改变maya的帧数
class SetSceneFrameRange1(Action):

    def run(self):
        import maya.cmds as cmds

        import cgtw
        import dbif

        t_tw = cgtw.tw()
        data_task = engine.getTaskFromEnv()
        data_base = dbif.CGT().getDataBase()
        if data_base:
            model = data_task['type']
            t_task_module = t_tw.task_module(str(data_base), str(model), [data_task['task_id']])
            cg_time = t_task_module.get(['shot.frame'])[0]["shot.frame"]
            firstFrame = 1001
            lastFrame = firstFrame + int(cg_time) - 1
            # print firstFrame, lastFrame
            cmds.playbackOptions(minTime=firstFrame, maxTime=lastFrame, animationStartTime=firstFrame,
                                 animationEndTime=lastFrame)


class GetSceneResolution(Action):

    def run(self):
        sw = self.software()
        if sw:
            return sw.resolution()
        else:
            return [None, None]


class SetSceneResolution(Action):
    _defaultParms = {
        'resolution': None,
    }

    progressText = 'Setting scene resolution...'

    def run(self):
        sw = self.software()
        if sw:
            res = self.parm('resolution')
            if not res:
                step = 'global'
                pro = self.database().getDataBase()
                res = engine.getStepConfig(step, 'resolution', project=pro)

            if type(res) in (tuple, list):
                if len(res) == 2:
                    sw.setResolution(*res)


class SetSceneFps(Action):
    progressText = 'Setting scene fps...'

    def run(self):
        sw = self.software()
        if sw:
            step = 'global'
            pro = self.database().getDataBase()
            fps = engine.getStepConfig(step, 'fps', project=pro)
            if type(fps) in (int, float):
                sw.setFps(fps)


class SetMayaProject(Action):

    def run(self):
        sw = self.software()
        if sw:
            proFolder = self.parm('input')

            try:
                os.makedirs(proFolder)
            except OSError:
                if not os.path.isdir(proFolder):
                    raise

            sw.setProject(proFolder)

            return proFolder


class SetSceneHUDs(Action):

    def run(self):
        sw = self.software()
        if sw:
            data = self.parm('input')
            if data:
                sw.removeAllHUDs()
                # Parse the data
                info = self.task().copy()
                info['date'] = time.strftime('%Y-%m-%d')
                for d in data:
                    # print 'd:',d
                    key = 'label'
                    value = d.get(key)
                    d[key] = info.get(value, value)

                sw.setHUDs(data)

                return data


class SetSceneActiveViewAttributes(Action):

    def run(self):
        sw = self.software()
        if sw:
            attribs = self.parm('input')
            if attribs:
                sw.setActiveCameraAttributes(**attribs)
                return attribs


class MakeScenePlayblast(Action):
    _defaultParms = {
        'output': '',
        'frame_range': '{scene_frame_range}',
        'resolution': [1998, 1080],
        'scale': 100,
        'quality': 100,
        'movie_codec': ''
    }

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('output')
            frameRange = self.parm('frame_range')
            scale = self.parm('scale')
            quality = self.parm('quality')
            resolution = self.parm('resolution')
            camera = self.parm('camera')
            movieCodec = self.parm('movie_codec')

            makeFolder(path)

            sw.playblast(path, scale, quality,
                         resolution=resolution,
                         override=True, camera=camera,
                         firstFrame=frameRange[0],
                         lastFrame=frameRange[-1],
                         movieCodec=movieCodec)

            return path


class MakeSceneTurntablePlayblast(Action):
    _defaultParms = {
        'frame_range': [1, 180],
        'resolution': [1920, 1080],
        'scale': 100,
        'quality': 100,
    }

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('output')
            scale = self.parm('scale')
            quality = self.parm('quality')
            frameRange = self.parm('frame_range')
            resolution = self.parm('resolution')

            tops = sw.getTopLevelObjectsOfMeshes()
            if tops:
                asset = tops[0]
            else:
                return

            # If user reference asset, then there's a namespace in the node name
            objs = sw.findObjects(asset)
            if objs:
                asset = objs[0]

            makeFolder(path)

            try:
                firstFrame = frameRange[0]
                lastFrame = frameRange[1]
            except:
                firstFrame = None
                lastFrame = None

            sw.makeTurntablePlayblast(path, asset,
                                      firstFrame=firstFrame,
                                      lastFrame=lastFrame,
                                      scale=scale,
                                      quality=quality,
                                      resolution=resolution,
                                      override=True)

            return path


class MakeSceneTurntableRenderPreview(Action):
    _defaultParms = {
        'renderer': 'arnold',
        'template_path': '',
        'hdrPath': '',
        'frame_range': [1, 180],
        'frame_step': 1,
        'resolution': [1920, 1080],
        'output': '',
    }

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('output')
            renderer = self.parm('renderer')
            frameRange = self.parm('frame_range')
            resolution = self.parm('resolution')
            hdrPath = self.parm('hdrPath')
            templatePath = self.parm('template_path')
            step = self.parm('frame_step')

            tops = sw.getTopLevelObjectsOfMeshes()
            if tops:
                asset = tops[0]
            else:
                return

            # If user reference asset, then there's a namespace in the node name
            objs = sw.findObjects(asset)
            if objs:
                asset = objs[0]

            makeFolder(path)

            # print 'templatePath:',templatePath
            # print 'hdrPath:',hdrPath

            try:
                firstFrame = frameRange[0]
                lastFrame = frameRange[1]
            except:
                firstFrame = None
                lastFrame = None

            sw.makeTurntableRenderPreview(path, asset,
                                          renderer=renderer,
                                          firstFrame=firstFrame,
                                          lastFrame=lastFrame,
                                          resolution=resolution,
                                          hdrPath=hdrPath,
                                          templatePath=templatePath,
                                          frameStep=step)

            return path


class RenderScene(Action):
    _defaultParms = {
        'renderer': 'arnold',
        'frame_range': None,
        'frame_step': 1,
        'resolution': None,
        'output': '',
        'enable_aovs': False,
        'camera': '',
        'aov_output_path': '<BeautyPath>/<RenderPass>/<BeautyFile>.<RenderPass>',
        'render_settings': {},
        'return_one': False,
        'silence': False
    }

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('output')
            renderer = self.parm('renderer')
            frameRange = self.parm('frame_range')
            resolution = self.parm('resolution')
            step = self.parm('frame_step')
            enableAOVs = self.parm('enable_aovs')
            camera = self.parm('camera')

            if not camera:
                camera = sw.getCurrentView()

            # print
            # print 'frameRange:'
            # print frameRange

            if not frameRange:
                frameRange = sw.frameRange()

            # print
            # print 'frameRange1:'
            # print frameRange

            try:
                firstFrame = frameRange[0]
                lastFrame = frameRange[1]
            except:
                firstFrame = None
                lastFrame = None

            makeFolder(path)

            # print 'templatePath:',templatePath
            # print 'hdrPath:',hdrPath

            kwargs = {
                'path': path,
                'renderer': renderer,
                'firstFrame': firstFrame,
                'lastFrame': lastFrame,
                'resolution': resolution,
                'camera': camera,
                'enableAOVs': enableAOVs,
                'frameStep': step,
                'renderSettings': self.parm('render_settings'),
                'aovOutputPath': self.parm('aov_output_path'),
                'silence': self.parm('silence')
            }

            r = sw.render(**kwargs)

            if self.parm('return_one'):
                return r[0]
            else:
                return r


class CreateRenderNode(Action):
    '''
    Creates a render node in the scene.

    Right now it supports software below:

    Nuke:
        It creates a Write node.
        custom_attributes is a list of dictionaries which has keys:
            type: type of Knob in Nuke
            name: parameter name of the attribute
            label: label of the parameter
            readonly: if it's true, set it to readonly status
    '''

    _defaultParms = {
        'renderer': 'arnold',
        'frame_range': None,
        'frame_step': 1,
        'resolution': None,
        'output': '',
        'enable_aovs': False,
        'camera': '',
        'aov_output_path': '<BeautyPath>/<RenderPass>/<BeautyFile>.<RenderPass>',
        'render_settings': {},
        'custom_attributes': []
    }

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('output')
            renderer = self.parm('renderer')
            frameRange = self.parm('frame_range')
            resolution = self.parm('resolution')
            step = self.parm('frame_step')
            enableAOVs = self.parm('enable_aovs')
            camera = self.parm('camera')

            if not camera:
                camera = sw.getCurrentView()

            # print
            # print 'frameRange:'
            # print frameRange

            if not frameRange:
                frameRange = sw.frameRange()

            # print
            # print 'frameRange1:'
            # print frameRange

            try:
                firstFrame = frameRange[0]
                lastFrame = frameRange[1]
            except:
                firstFrame = None
                lastFrame = None

            makeFolder(path)

            # print 'templatePath:',templatePath
            # print 'hdrPath:',hdrPath

            kwargs = {
                'path': path,
                'renderer': renderer,
                'firstFrame': firstFrame,
                'lastFrame': lastFrame,
                'resolution': resolution,
                'camera': camera,
                'enableAOVs': enableAOVs,
                'frameStep': step,
                'renderSettings': self.parm('render_settings'),
                'aovOutputPath': self.parm('aov_output_path'),
                'customAttributes': self.parm('custom_attributes')
            }

            r = sw.createRenderNode(**kwargs)
            return r


class ReplaceReadNodesPaths(Action):
    _defaultParms = {
        'option': 'node_name',
        'input': ''
    }

    def run(self):
        sw = self.software()
        if sw:
            option = self.parm('option')

            if option == 'node_name':
                nodes = sw.find(type='Read')
                for name in nodes:
                    n = sw._nuke.toNode(name)
                    kwargs = {'pass': n.name()}
                    self.setFormatKeys(kwargs)
                    path = self.parm('input')
                    n['file'].setValue(path)


class RunExpression(Action):
    _defaultParms = {
        'expression': '',
    }

    def run(self):
        ex = self.parm('expression')
        r = {}
        a = {}
        exec (ex, r, a)
        return a


class EvalString(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        ex = self.parm('input')
        ex = str(ex)
        return eval(ex)


class GetDictValue(Action):
    _defaultParms = {
        'input': '',
        'key': '',
    }

    def run(self):
        d = self.parm('input')
        key = self.parm('key')

        if type(d) == dict:
            return d.get(key)


class GetListValue(Action):
    _defaultParms = {
        'input': '',
        'index': '',
    }

    def run(self):
        d = self.parm('input')
        i = self.parm('index')

        if type(d) in (list, tuple) and type(i) == int:
            if len(d) > i:
                return d[i]


class MakeMovie(Action):
    _defaultParms = {
        'input': '',
        'output': '',
        'engine': 'ffmpeg',
        'fps': 24,
        'quality': 1,
        'first_frame': 1001,
    }

    def run(self):
        inputPath = self.parm('input')
        outputPath = self.parm('output')
        ext = os.path.splitext(inputPath)[-1].replace('.', '')

        kwargs = {
            'inputPath': inputPath,
            'outputPath': outputPath,
            'fps': self.parm('fps'),
            'quality': self.parm('quality')
        }

        first = self.parm('first_frame')
        if type(first) == int:
            kwargs['firstFrame'] = first

        engine = self.parm('engine').lower()
        if engine == 'rvio':
            if ext == 'exr':
                kwargs['outsrgb'] = True

            engine = rdlb.RVIO()

        elif engine == 'ffmpeg':
            engine = rdlb.FFmpeg()

        else:
            engine = None

        if engine:
            makeFolder(outputPath)
            engine.renderPhotoJPEGMov(**kwargs)

        return outputPath


class MakeThumbnail(Action):

    def run(self):
        inputPath = self.parm('input')
        outputPath = self.parm('output')

        makeFolder(inputPath)

        engine = rdlb.FFmpeg()
        engine.makeJPGSnapshot(inputPath, outputPath)

        return outputPath


class SetEnvContext(Action):
    '''Sets current context to system env.'''

    progressText = 'Setting working context...'

    def run(self):
        print 'self._task:', self.task()
        engine.setEnv(self.task())


def _getFileOpenRecordFilename(currentFile):
    root = engine._localSettingsPath()
    filename = os.path.basename(currentFile)
    path = '%s/file_open_%s.json' % (root, filename)
    return path


def top_level_meshes():
    cam_ls = [u'persp', u'top', u'front', u'side']
    top_ls = [i for i in cmds.ls(assemblies=True) if i not in cam_ls]
    return top_ls


class MakeFileOpenRecord(Action):
    '''Makes a record after openning the file.'''

    _defaultParms = {
        'input': '{current_file}',
    }

    progressText = 'Making file open record...'

    def run(self):
        currentFile = self.parm('input')
        currentFile = currentFile.replace('\\', '/')

        path = _getFileOpenRecordFilename(currentFile)

        info = {
            'file': currentFile,
            'task': self.task()
        }
        info = json.dumps(info, indent=4)

        f = open(path, 'w')
        f.write(info)
        f.close()

        return path


class CheckFileOpen(Action):
    '''Checks whether the user open the file through the tool.'''

    _defaultParms = {
        'input': '{current_file}',
    }

    def run(self):
        result = False

        currentFile = self.parm('input')
        currentFile = currentFile.replace('\\', '/')

        path = _getFileOpenRecordFilename(currentFile)

        if os.path.isfile(path):
            f = open(path, 'r')
            t = f.read()
            f.close()

            info = json.loads(t)

            # print
            # print 'info:'
            # print info
            #
            # print
            # print 'task:',
            # print self.task()

            if type(info) == dict:
                task = info.get('task')
                if type(task) == dict:
                    openedTaskId = str(task.get('id'))
                    currentTaskId = str(self.task().get('id'))
                    if info.get('file') == currentFile and openedTaskId == currentTaskId:
                        result = True

        if not result:
            txt = u'请使用Open工具打开文件!'
            return txt


class CGTeamworkTagException(Exception):
    pass


class GetPathFromTag(Action):
    progressText = 'Getting path from tag...'

    _defaultParms = {
        'input': '',
    }

    def run(self):
        task = self.task()
        kwargs = dict()
        kwargs['type'] = task.get('type')
        kwargs['sequence'] = task.get('sequence')
        kwargs['shot'] = task.get('shot')
        kwargs['step'] = task.get('step')
        kwargs['tag'] = self.parm('input')
        r = self.database().getTaskFromTag(**kwargs)
        if r:
            return r
        else:
            return "find nothing"


# 获取charEffect环节的nCloth任务路径
class charEffectsNclothTag(Action):
    progressText = 'Getting path from tag...'

    def run(self):
        tag = 'charEffects_cloth_work'
        task = self.task()

        kwargs = {}
        typ = task.get('type')
        kwargs['type'] = typ
        kwargs['sequence'] = task.get('sequence')
        kwargs['shot'] = task.get('shot')
        kwargs['step'] = self.step()
        kwargs['tag'] = 'charEffects_cloth_work'

        r = self.database().getTaskFromTag(**kwargs)

        if r:
            return r
        else:
            msg = '%s' % tag
            raise CGTeamworkTagException(msg)


# 获取charEffect环节的nHair任务路径
class charEffectsNhairTag(Action):
    progressText = 'Getting path from tag...'

    def run(self):
        tag = 'charEffects_hair_work'
        task = self.task()

        kwargs = {}
        typ = task.get('type')
        kwargs['type'] = typ
        kwargs['sequence'] = task.get('sequence')
        kwargs['shot'] = task.get('shot')
        kwargs['step'] = self.step()
        kwargs['tag'] = 'charEffects_hair_work'

        r = self.database().getTaskFromTag(**kwargs)

        if r:
            return r
        else:
            msg = '%s' % tag
            raise CGTeamworkTagException(msg)


class GetFolder(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        path = self.parm('input')
        return os.path.dirname(path)


class GetFilename(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        path = self.parm('input')
        return os.path.basename(path)


class GetTaskName(Action):

    def run(self):
        task_name = engine.getTaskFromEnv()['task_name']
        return task_name


class GetFileBaseName(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        path = self.parm('input')
        temp = os.path.basename(path)
        return os.path.splitext(temp)[0]


# 获取文件名
class GetFileBaseName1(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        path = self.parm('input')
        temp = os.path.basename(path)
        return os.path.splitext(temp)[0]


# 返回没有版本号的文件名
class GetIniBaseName(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        path = self.parm('input')
        temp = os.path.basename(path)
        basename = os.path.splitext(temp)[0]
        temp = basename.split("_")
        temp.pop()
        ini_list = "_".join(tuple(temp))
        return ini_list


class ReplaceString(Action):
    '''Replaces the string for the from and to values.'''

    _defaultParms = {
        'input': '',
        'replace': '',
        'to': ''
    }

    def run(self):
        s = self.parm('input')
        fromS = self.parm('replace')
        fromS = fromS.replace('/', '\\')
        toS = self.parm('to')

        rePat = re.compile(fromS)
        return rePat.sub(toS, s)


_vnPattern = re.compile('([a-zA-Z]+)?(#+)')


def parseVersionPattern(s):
    result = _vnPattern.findall(s)
    if result:
        # s: tst_lgt_v###.ma
        # result: [('v', '###')]
        # prefix: v
        # padPat: ###
        # vnPat: v###
        # vnFormat: v%03d
        # rePat: tst_lgt_v(\d{3}).ma
        # formatS: tst_lgt_v%03d.ma
        prefix, padPat = result[-1]
        vnPat = prefix + padPat
        count = len(padPat)
        rePat = s.replace(padPat, '(\d{%s})' % count)
        rePat = re.compile(rePat)
        theF = '%0' + str(count) + 'd'
        formatS = s.replace(padPat, theF)
        vnFormat = prefix + theF
        return rePat, formatS, vnPat, vnFormat
    else:
        return s, s, '', ''


_digitsPattern = re.compile('([a-zA-Z]+)?(\d+)')


def toVersionPattern(string):
    '''
    Converts the string to a version pattern.

    Example:
        string: tst_lgt_v002.ma
        return: tst_lgt_v###.ma
    '''
    result = _digitsPattern.findall(string)
    if result:
        # s: tst_lgt_v002.ma
        # result: [('v', '002')]
        # prefix: v
        # digits: 002
        # digitsPat: v002
        # vnPat: v###
        # pattern: tst_lgt_v###.ma
        prefix, digits = result[-1]
        digitsPat = prefix + digits
        vnPat = prefix + len(digits) * '#'
        pattern = string.replace(digitsPat, vnPat)
        return pattern


def toVersionWildcard(string):
    '''
    Converts the string to a version wildcard pattern.

    Example:
        string: tst_lgt_v002.ma
        return: tst_lgt_*.ma
    '''
    result = _digitsPattern.findall(string)
    if result:
        # s: tst_lgt_v002.ma
        # result: [('v', '002')]
        # prefix: v
        # digits: 002
        # digitsPat: v002
        # vnPat: v???
        # pattern: tst_lgt_v###.ma
        prefix, digits = result[-1]
        digitsPat = prefix + digits
        vnPat = prefix + len(digits) * '?'
        pattern = string.replace(digitsPat, vnPat)
        return pattern


def getLatestVersion(files, filenamePattern):
    '''
    Gets latest version file of the files.
    files is a list of string of filenames,
    filenamePattern is a string for filtering the files.

    Example:
        files:
            tst_lgt_v001.ma
            tst_lgt_v002.ma
        filenamePattern:
            tst_lgt_v###.ma or tst_lgt_v001.ma
        return:
            {version_pattern: v###
             version_format: v%03d
             file_format: tst_lgt_v%03d.ma
             latest_version: v002
             latest_version_number: 2
             latest_file: tst_lgt_v002.ma
             current_version: v003
             current_version_number: 3
             current_file: tst_lgt_v003.ma
            }
    '''
    # Parse patterns
    # filenamePattern: tst_lgt_v###.ma
    # filenameRePattern: tst_lgt_v(\d{3}).ma
    # filenameFormat: tst_lgt_v%03d.ma
    # versionPattern: v###
    # versionRePattern: v(\d{3})
    # versionFormat: v%03d
    filenameRePattern, filenameFormat, versionPattern, versionFormat = parseVersionPattern(filenamePattern)
    # print 'filenameRePattern:',filenameRePattern
    # print 'filenameFormat:', filenameFormat
    # print 'versionPattern:',versionPattern
    # print 'versionFormat:', versionFormat

    if filenameRePattern == filenamePattern:
        # filenameRePattern: tst_lgt_v001.ma
        # filenameRePattern: tst_lgt_v###.ma
        filenamePattern = toVersionPattern(filenamePattern)
        if filenamePattern:
            filenameRePattern, filenameFormat, versionPattern, versionFormat = parseVersionPattern(filenamePattern)
        else:
            return

    # Filter the files
    okFiles = {}
    for f in files:
        r = filenameRePattern.findall(f)
        # print 'r:',r
        if r:
            vn = int(r[0])
            if not okFiles.has_key(vn):
                okFiles[vn] = []
            okFiles[vn].append(f)

    if okFiles:
        lastVersionNumber = sorted(okFiles.keys())[-1]
        latestVersion = versionFormat % lastVersionNumber
        latestFile = okFiles[lastVersionNumber][0]
    else:
        lastVersionNumber = 0
        latestVersion = ''
        latestFile = ''

    currentVersionNumber = lastVersionNumber + 1
    currentVersion = versionFormat % currentVersionNumber
    currentFile = filenameFormat % currentVersionNumber

    result = {
        'version_pattern': versionPattern,
        'version_format': versionFormat,
        'latest_version': latestVersion,
        'latest_version_number': lastVersionNumber,
        'latest_file': latestFile,
        'current_version': currentVersion,
        'current_version_number': currentVersionNumber,
        'current_file': currentFile,
    }
    return result


def getLatestVersion1(files, filenamePattern):
    '''
    Gets latest version file of the files.
    files is a list of string of filenames,
    filenamePattern is a string for filtering the files.

    Example:
        files:
            tst_lgt_v001.ma
            tst_lgt_v002.ma
        filenamePattern:
            tst_lgt_v###.ma or tst_lgt_v001.ma
        return:
            {version_pattern: v###
             version_format: v%03d
             file_format: tst_lgt_v%03d.ma
             latest_version: v002
             latest_version_number: 2
             latest_file: tst_lgt_v002.ma
             current_version: v003
             current_version_number: 3
             current_file: tst_lgt_v003.ma
            }
    '''
    # Parse patterns
    # filenamePattern: tst_lgt_v###.ma
    # filenameRePattern: tst_lgt_v(\d{3}).ma
    # filenameFormat: tst_lgt_v%03d.ma
    # versionPattern: v###
    # versionRePattern: v(\d{3})
    # versionFormat: v%03d
    filenameRePattern, filenameFormat, versionPattern, versionFormat = parseVersionPattern(filenamePattern)
    # print 'filenameRePattern:',filenameRePattern
    # print 'filenameFormat:', filenameFormat
    # print 'versionPattern:',versionPattern
    # print 'versionFormat:', versionFormat

    if filenameRePattern == filenamePattern:
        # filenameRePattern: tst_lgt_v001.ma
        # filenameRePattern: tst_lgt_v###.ma
        filenamePattern = toVersionPattern(filenamePattern)
        if filenamePattern:
            filenameRePattern, filenameFormat, versionPattern, versionFormat = parseVersionPattern(filenamePattern)
        else:
            return

    # Filter the files
    okFiles = {}
    for f in files:
        r = filenameRePattern.findall(f)
        # print 'r:',r
        if r:
            vn = int(r[0])
            if not okFiles.has_key(vn):
                okFiles[vn] = []
            okFiles[vn].append(f)

    if okFiles:
        lastVersionNumber = sorted(okFiles.keys())[-1]
        latestVersion = versionFormat % lastVersionNumber
        latestFile = okFiles[lastVersionNumber][0]
    else:
        lastVersionNumber = 0
        latestVersion = ''
        latestFile = ''

    currentVersionNumber = lastVersionNumber
    currentVersion = versionFormat % currentVersionNumber
    currentFile = filenameFormat % currentVersionNumber

    result = {
        'version_pattern': versionPattern,
        'version_format': versionFormat,
        'latest_version': latestVersion,
        'latest_version_number': lastVersionNumber,
        'latest_file': latestFile,
        'current_version': currentVersion,
        'current_version_number': currentVersionNumber,
        'current_file': currentFile,
    }
    return result


class VersionUpBaseName(Action):
    def run(self):
        sw = self.software()
        if sw:
            # filename:
            path = self.parm('input')
            # print 'action:',self.name
            # print 'path:',[path]
            folder = os.path.dirname(path)
            if os.path.exists(folder):
                pass
            else:
                os.makedirs(folder)
            filename = os.path.basename(path)
            filename = filename.replace('_______', '_')
            filename = filename.replace('______', '_')
            filename = filename.replace('_____', '_')
            filename = filename.replace('____', '_')
            filename = filename.replace('___', '_')
            filename = filename.replace('__', '_')

            if os.path.exists(folder):
                files = os.listdir(folder)
            else:
                files = []
            r = getLatestVersion(files, filename)

            # result = '%s/%s' % (folder, r['current_file'])
            result = r['current_file']
            return result


class VersionUp(Action):
    '''
    Folder structure of the work files:
        001_01_model_v002.ma
        versions:
            001_01_model_v001.ma
            001_01_model_v002.ma
            001_01_model_v003.ma
    '''

    def run(self):
        sw = self.software()
        if sw:
            # filename:
            path = self.parm('input')
            folder = os.path.dirname(path)
            if not os.path.exists(folder):
                os.makedirs(folder)

            filename = os.path.basename(path)
            if os.path.exists(folder):
                files = os.listdir(folder)
            else:
                files = []
            r = getLatestVersion(files, filename)

            result = '%s/%s' % (folder, r['current_file'])

            return result


class KeepName(Action):

    def run(self):
        path = self.parm('input')
        return path


class ModelVersionUp(Action):
    '''
    Folder structure of the work files:
        001_01_model_v002.ma
        versions:
            001_01_model_v001.ma
            001_01_model_v002.ma
            001_01_model_v003.ma
    '''

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('input')
            folder = os.path.dirname(path)
            if not os.path.exists(folder):
                os.makedirs(folder)
            filename = os.path.basename(path)
            in_name = filename.split('_')
            in_name[2] = in_name[2].lower()
            if in_name[2] in ['texture']:
                in_name[2] = 'tex'
            if in_name[1] in ["model", 'rig', 'Model', 'Rig', 'Texture']:
                in_name.remove(in_name[1])

            filename = "_".join(in_name)
            if os.path.exists(folder):
                files = os.listdir(folder)
            else:
                files = []
            r = getLatestVersion(files, filename)

            # result = '%s/%s' % (folder, r['current_file'])
            result = '%s/%s' % (folder, r['current_file'])

            return result


class GetAutoVersion(Action):
    _defaultParms = {
        'input': '',
        'pattern': 'v###',
    }

    def run(self):
        folder = self.parm('input')
        pattern = self.parm('pattern')

        if os.path.exists(folder):
            files = os.listdir(folder)
        else:
            files = []

        r = getLatestVersion(files, pattern)

        return r['current_version']


class GetVersionNumber(Action):
    '''Gets version number in the string.'''

    _defaultParms = {
        'input': '',
        'pattern': 'v###',
    }

    progressText = 'Getting version number from input...'

    def run(self):
        s = self.parm('input')
        pat = self.parm('pattern')

        # Get re pattern
        result = _vnPattern.findall(pat)
        if result:
            # prefix: v
            # padPat: ###
            prefix, padPat = result[-1]
            count = len(padPat)
            rePat = pat.replace(padPat, '\d{%s}' % count)
            rePat = re.compile(rePat)
            token = rePat.findall(s)
            if token:
                return token[-1]

        return ''


class FindString(Action):
    _defaultParms = {
        'input': '',
        'pattern': '',
        'returned_index': -1
    }

    def run(self):
        s = self.parm('input')
        pat = self.parm('pattern')
        pat = pat.replace('/', '\\')
        pat = re.compile(pat)
        temp = pat.findall(s)
        if temp:
            i = self.parm('returned_index')
            if type(i) == int:
                try:
                    r = temp[i]
                except:
                    r = temp[-1]
            else:
                r = temp[-1]

        else:
            r = ''

        return r


class CopyFile(Action):
    _defaultParms = {
        'input': '',
        'output': '',
        'force': True
    }

    def run(self):
        inputPath = self.parm('input')
        path = self.parm('output')
        makeFolder(path)

        if os.path.isfile(inputPath):
            if os.path.isdir(path):
                filename = os.path.basename(inputPath)
                path = '%s/%s' % (path, filename)

            copyFile(inputPath, path)

        elif os.path.isdir(inputPath):
            if os.path.exists(path):
                if self.parm('force'):
                    shutil.rmtree(path)
                else:
                    return path

            shutil.copytree(inputPath, path)

        return path


class CopyXgenFile(Action):
    _defaultParms = {
        'input': '',
        'seq': '',
        'shot': '',
        'nHair_abc': ''
    }

    def run(self):
        seq = self.parm('seq')
        shot = self.parm('shot')
        nHair_abc = self.parm('nHair_abc')
        tgt_basename = os.path.basename(self.parm('input')).split(".")[0]
        tgt_ls = glob.glob(nHair_abc)
        if tgt_ls:
            for f in tgt_ls:
                targetPath = "{dir}/{basename}{nHair_abc}".format(dir=os.path.dirname(self.parm('input')),
                                                                  basename=tgt_basename,
                                                                  nHair_abc=re.findall(r"__.*", f)[0])
                copyFile(f, targetPath)


class RemoveFiles(Action):

    def run(self):
        path = self.parm('input')
        files = glob.glob(path)
        for f in files:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)


class CombineData(Action):
    _defaultParms = {
        'inputs': [],
    }

    def run(self):
        inputs = self.parm('inputs')
        if not inputs:
            inputs = []

        result = []
        for i in inputs:
            result += i

        return result


'''
groupKey = 'namespace'
newKey, newKeySource = 'objects', 'full_path'

data = [{'asset': u'laserwave',
  'full_path': u'|laserwave:world_gp|laserwave:renderMesh_gp|laserwave:laserwave_GRP',
  'namespace': u'laserwave',
  'object': u'laserwave:laserwave_GRP'},
 {'asset': u'laserwave',
  'full_path': u'|laserwave:world_gp|laserwave:renderMesh_gp|mask',
  'namespace': u'laserwave',
  'object': u'mask'},
 {'asset': u'laserwave',
  'full_path': u'|laserwave1:world_gp|laserwave1:renderMesh_gp|laserwave1:laserwave_GRP',
  'namespace': u'laserwave1',
  'object': u'laserwave1:laserwave_GRP'},
 {'asset': u'laserwave',
  'full_path': u'|laserwave2:world_gp|laserwave2:renderMesh_gp|laserwave2:laserwave_GRP',
  'namespace': u'laserwave2',
  'object': u'laserwave2:laserwave_GRP'}]

run(groupKey, newKey, newKeySource, data)
'''


class GroupData(Action):
    _defaultParms = {
        'group_key': '',
        'collapse_key': '',
        'new_key': '',
        'data': []
    }

    def run(self):
        groupKey = self.parm('group_key')
        newKeySource = self.parm('collapse_key')
        newKey = self.parm('new_key')
        data = self.parm('data')

        groups = []
        temp = {}
        for d in data:
            group = d.get(groupKey)
            if not temp.has_key(group):
                temp[group] = []
                groups.append(d)
            temp[group].append(d)

        result = []
        for d in groups:
            group = d.get(groupKey)

            lst = []
            for info in temp[group]:
                lst.append(info.get(newKeySource))

            d[newKey] = lst

            if d.has_key(newKeySource):
                del d[newKeySource]
            else:
                pass

            result.append(d)

        return result


class DataTable(Action):
    _defaultParms = {
        'input': [],
    }

    # def __init__(self, engine):
    #    Action.__init__(self, engine)
    #
    #    self._items = []
    #
    # def addItem(self, item):
    #    self._items.append(item)

    def run(self):
        return self.parm('input')


class FilterDataTable(Action):
    '''
    '''

    _defaultParms = {
        'input': '',
        'filters': {}
    }

    def run(self):
        result = []

        data = self.parm('input')
        filters = self.parm('filters')
        # print "filters:",filters
        for d in data:
            tem = []
            for f in filters.keys():
                if type(filters[f]) == list:
                    if d.get(f) in filters[f]:
                        tem.append(0)
                elif d.get(f) == filters[f]:
                    tem.append(0)

            if len(tem) == len(filters):
                result.append(d)
        return result


class AddData(Action):
    _defaultParms = {
        'input': [],
        # ''
    }

    # def __init__(self, engine):
    #    Action.__init__(self, engine)
    #
    #    self._items = []
    #
    # def addItem(self, item):
    #    self._items.append(item)

    def run(self):
        return self.parm('input')


class SetShotFrameRange(Action):
    _defaultParms = {
        'frame_range': '{scene_frame_range}',
    }

    def run(self):
        kwargs = {
            'project': self.database().getDataBase(),
            'shotId': self.task().get('shot_id'),
            'value': self.parm('frame_range')
        }
        self.database().updateShotFrameRange(**kwargs)


class SetShotLinkedAssets(Action):
    '''
    Sets linked assets of the shot on database based on
    assets in the scene.
    '''

    def run(self):
        sw = self.software()
        if sw:
            # Get referenced scene assets
            refs = sw.getReferenceObjects()
            refs += sw.getGpuCaches()
            refs += sw.getAssemblyReferences()

            paths = []
            for i in refs:
                path = i['path']
                if path not in paths:
                    paths.append(path)

            assetIds = []
            for path in paths:
                info = self.engine().getInfoFromPath(path, enableCache=True)

                if info:
                    kwargs = {
                        'project': info.get('project'),
                        'assetType': info.get('sequence'),
                        'asset': info.get('shot')
                    }
                    id_ = self.database().getAssetId(**kwargs)
                    if id_:
                        assetIds.append(id_)

            if assetIds:
                project = self.database().getDataBase()
                shotId = self.task().get('shot_id')
                self.database().updateShotLinkedAssets(project, shotId, assetIds)


class SetShotLinkedAssets2(Action):
    '''
    Sets linked assets of the shot on database based on
    assets in the scene. We search the assets by the group name pattern.
    '''

    _defaultParms = {
        'type': 'transform',
        'name_pattern': '',
        'index': 0,
    }

    def run(self):
        sw = self.software()
        if sw:
            typ = self.parm('type')
            pattern = self.parm('name_pattern')
            pat = re.compile(pattern)
            index = self.parm('index')

            assets = []
            temp = sw._cmds.ls(type=typ)
            # temp = sw.find(name=key, type=typ, fullPath=True)
            for t in temp:
                token = pat.findall(t)
                if token:
                    asset = token[0]
                    if asset not in assets:
                        assets.append(asset)

            assetIds = []
            for asset in assets:
                kwargs = {
                    'project': self.database().getDataBase(),
                    'asset': asset
                }
                id_ = self.database().getAssetId(**kwargs)
                if id_:
                    assetIds.append(id_)

            # print
            # print 'assetIds:'
            # print assetIds

            if assetIds:
                project = self.database().getDataBase()
                shotId = self.task().get('shot_id')
                self.database().updateShotLinkedAssets(project, shotId, assetIds)


class GetSceneCameras(Action):
    _defaultParms = {
        'name_pattern': '',
        'include_hidden': False
    }

    def run(self):
        result = []

        sw = self.software()
        if sw:
            camPattern = self.parm('name_pattern')
            includeHidden = self.parm('include_hidden')

            if camPattern:
                camPattern = camPattern.replace('/', '\\')
                camPattern = re.compile(camPattern)

            cams = sw.getCameras(includeHidden=includeHidden)

            # print
            # print 'cameras:'
            # pprint.pprint(cams)
            # print

            for c in cams:
                go = False
                if camPattern:
                    if camPattern.findall(c['full_path']):
                        go = True
                else:
                    go = True

                if go:
                    d = {}
                    # if c['namespace']:
                    #    d['namespace'] = c['namespace']
                    # else:
                    # d['namespace'] = 'camera'

                    d['instance'] = 'camera'
                    d['namespace'] = 'camera'
                    d['asset'] = 'camera'
                    d['object'] = c['name']
                    d['full_path'] = c['full_path']
                    d['node_type'] = 'transform'
                    d['node'] = c['full_path']

                    result.append(d)

        return result


def _addAssetInstance(data):
    '''
    Puts a new key called instance for the asset number
    where is more than one instance for the asset.
    '''
    result = []

    for asset in data.keys():
        i = 0
        for d in data[asset]:
            if i:
                d['instance'] = '%s%s' % (d['asset'], i)
            else:
                d['instance'] = d['asset']
            result.append(d)

            i += 1

    return result


class GetAnimationPublishedObjects(Action):
    _defaultParms = {
        'keyword': '',
    }

    def run(self):
        import pymel.core as pm
        key = self.parm('keyword')

        alll = {}

        sw = self.software()
        if sw:
            refs = sw.getReferenceObjects()
            # temp = self._software.getReferences()
            # print refs
            for ref in refs:
                # print
                # print 'ref:',ref
                # ref: {name:'', code:'', full_name:'', namespace:'', path:''}
                # print ref['path']
                info = self.engine().getInfoFromPath(ref['path'], enableCache=True)
                # print 'info:',
                # pprint.pprint(info)
                # print
                # print 'info:',info

                if not info:
                    continue
                # print ref['namespace'], 222222222222222
                if key:
                    kwargs = {
                        'name': key,
                        'namespace': ref['namespace'],
                    }
                    # print 'kwargs:',kwargs
                    objs = sw.find(**kwargs)
                    if objs:
                        obj = objs[0]

                        # print 'obj:',obj

                        d = {}
                        d['namespace'] = ref['namespace']
                        d['asset_type'] = info.get('sequence')
                        d['asset'] = info['shot']
                        d['object'] = obj
                        d['full_path'] = pm.PyNode(obj).fullPath()
                        d['ref_node'] = ref['ref_node']
                        d['ref_path'] = ref['ref_path']

                        if not alll.has_key(info['shot']):
                            alll[info['shot']] = []
                        alll[info['shot']].append(d)

                else:
                    d = {}
                    d['namespace'] = ref['namespace']
                    d['asset_type'] = info.get('sequence')
                    d['asset'] = info['shot']
                    d['object'] = ref['full_name']
                    d['full_path'] = ref['full_name']
                    d['ref_node'] = ref['ref_node']
                    d['ref_path'] = ref['ref_path']

                    if not alll.has_key(info['shot']):
                        alll[info['shot']] = []
                    alll[info['shot']].append(d)

        result = _addAssetInstance(alll)
        # print 'result:',result

        return result


class GetAnimationPublishedObjects2(Action):
    '''
    Gets object under the root group, then check which one match the
    name pattern.
    Example:
        aaa_rig:
            renderMesh
                dog_Model_GRP
                cat_Model_GRP

        keyword: renderMesh
        name_pattern: [a-zA-Z]_Model_GRP
        index: 0
        return:[
                {'asset':'dog', 'object':'',
                'full_path':'', 'instance':'dog'}
            ]
    '''

    _defaultParms = {
        'keyword': '',
        'type': 'transform',
        'name_pattern': '',
        'index': 0,
    }

    def run(self):
        sw = self.software()
        if sw:
            alll = {}

            key = self.parm('keyword')
            typ = self.parm('type')
            pattern = self.parm('name_pattern')
            pat = re.compile(pattern)
            index = self.parm('index')
            newKey = 'asset'

            temp = sw.find(name=key, type=typ, fullPath=True)
            for t in temp:
                for c in sw.getChildren(t, type=typ):
                    token = pat.findall(c.name())
                    if token:
                        value = token[0]

                        info = {
                            'namespace': c.namespace(),
                            'asset_type': '',
                            newKey: value,
                            'object': c.name(),
                            'full_path': c.fullPath(),
                            'ref_node': '',
                            'ref_path': ''
                        }

                        if not alll.has_key(value):
                            alll[value] = []
                        alll[value].append(info)

            result = _addAssetInstance(alll)
            # print result, 789789798798798798798
            return result

        return []


class GetShotLinkedAssets(Action):
    _defaultParms = {
        'shot': ''
    }

    def run(self):
        shot = self.parm('shot')
        return self.database().getShotLinkedAssets(shot)


class GetPublishedFiles(Action):
    _defaultParms = {
        'project': '',
        'type': '',
        'sequence': '',
        'shot': '',
        # 'episode': '',
        'steps': [],
        'latest': False,
        'enableCache': False,
        'parts': [],
        'filetypes': []
    }

    def run(self):
        keys = self._parms.keys()
        kwargs = self.parms(keys)
        if not kwargs['project']:
            kwargs['project'] = self.database().getDataBase()
        kwargs['database'] = self.database()

        # print
        # print 'filters:'
        # print kwargs

        temp = plcr.getPublishedFiles(**kwargs)

        # print
        # print 'result:'
        # print temp

        return temp


class GetPublishedFiles(Action):
    _defaultParms = {
        'project': '',
        'type': '',
        'sequence': '',
        'shot': '',
        # 'episode': '',
        'steps': [],
        'latest': False,
        'enableCache': False,
        'parts': [],
        'filetypes': []
    }

    def run(self):
        keys = self._parms.keys()
        kwargs = self.parms(keys)
        if not kwargs['project']:
            kwargs['project'] = self.database().getDataBase()
        kwargs['database'] = self.database()

        # print
        # print 'filters:'
        # print kwargs

        temp = plcr.getPublishedFiles(**kwargs)

        # print
        # print 'result:'
        # print temp

        return temp


class GetWorkfileId(Action):
    _defaultParms = {
        'project': '',
        'name': ''
    }

    def run(self):
        project = self.parm('project')
        if not project:
            project = self.database().getDataBase()

        name = self.parm('name')
        entity = 'version'
        filters = [
            ['project', '=', project],
            ['version.version_type', '=', 'workfile'],
            ['version.name', '=', name]
        ]
        fields = ['version.id']
        temp = self.database().find(entity, filters, fields)
        if temp:
            return temp[0]['version.id']


class GetAssemblyElements(Action):
    '''
    Finds the assembly elements for the shot.

    If layout is an empty list, get assets from shot links.

    Example of layout data:
    [
        {
            "name": "world_gp",
            "namespace": "laserwave1",
            "transform": {
                "translateX": 0.0,
                "translateY": 0.0,
                "translateZ": 0.0,
                "scaleX": 1.0,
                "scaleY": 1.0,
                "scaleZ": 1.0,
                "rotateX": 0.0,
                "rotateY": 0.0,
                "rotateZ": 0.0
            },
            "node_type": "transform",
            "asset": "laserwave",
            "full_name": "laserwave1:world_gp"
        }
    ]

    Returns a list of dictionaries:
    [
        {
            'asset': 'camera',
            'asset_type': '',
            'transform': {},
            'elements_order': ['shape']
            'elements': {
                'shape': [
                    {'name': 'shape', 'step':'animation', 'filetype':'abc', 'path': ''},
                    {'name': 'material', 'step':'', 'path': ''},
                    {'name': 'transform', 'step':'', 'path': ''},
                ]
            }
        },
        {
            'asset': 'buildingA',
            'asset_type': 'sets',
            'transform': {},
            'elements': {
                'shape': [
                    {'name': 'shape', 'step':'rig', 'filetype':'gpu', 'path': ''},
                    {'name': 'material', 'step':'', 'path': ''},
                    {'name': 'transform', 'step':'', 'path': ''},
                ]
            }
        },
        {
            'asset': 'dog',
            'asset_type': 'chr',
            'transform': {},
            'elements': {
                'shape': [
                    {'name': 'shape', 'step':'', 'path': ''},
                    {'name': 'material', 'step':'', 'path': ''},
                    {'name': 'transform', 'step':'', 'path': ''},
                ]
            }
        }
    ]
    '''

    _defaultParms = {
        'shot': '',
        'layout': [],
        'camera': {
            'shape': {
                'type': 'shot',
                'steps': 'Animation',
                'parts': 'camera',
                'filetypes': 'abc'
            }
        },
        'elements_order': ['shape'],
        'default_asset_type': 'DEFAULT',
        'elements': {
            'sets': {
                'shape': [
                    {
                        'type': 'asset',
                        'steps': 'rig',
                        'parts': 'model',
                        'filetypes': 'gpu'
                    },
                    {
                        'type': 'asset',
                        'steps': 'mod',
                        'parts': 'model',
                        'filetypes': 'gpu'
                    }
                ],
                'material': []
            },
            'chars': {
                'shape': [
                    {
                        'type': 'shot',
                        'steps': 'Animation',
                        'filetypes': 'abc'
                    }
                ]
            }
        }
    }

    def run(self):
        plcr.clearConfigCache()

        # print
        result = []

        shot = self.parm('shot')
        elementsOrder = self.parm('elements_order')
        if not elementsOrder:
            elementsOrder = []
        elementsInfo = self.parm('elements')
        cameraInfo = self.parm('camera')
        layoutInfo = self.parm('layout')
        pro = shot.get('project')
        defaultAType = self.parm('default_asset_type')

        # print
        # print 'shot:',shot
        # print

        if type(layoutInfo) in (str, unicode):
            f = open(layoutInfo, 'r')
            t = f.read()
            f.close()
            layoutInfo = json.loads(t)

        # Get layout info
        if not layoutInfo:
            layoutInfo = []

            assets = self.database().getShotLinkedAssets(shot)

            for asset in assets:
                info = {
                    "name": asset['code'],
                    "namespace": '',
                    "node_type": "transform",
                    "asset": asset['code'],
                    'asset_type': asset['sequence'],
                    "full_name": asset['code'],
                    'instance': asset['code']
                }
                layoutInfo.append(info)

        result = []

        # Get camera
        if not cameraInfo:
            cameraInfo = {}

        if cameraInfo:
            elements = {}
            for key in cameraInfo.keys():
                temp = []
                for unit in cameraInfo[key]:
                    kwargs = {
                        'database': self.database(),
                        'project': pro,
                        'sequence': shot.get('sequence'),
                        'shot': shot.get('code'),
                        'latest': True,
                        'enableCache': True
                    }
                    kwargs.update(unit)

                    # print
                    # print 'Getting published cameras'
                    temp1 = plcr.getPublishedFiles(**kwargs)
                    # print 'Done'

                    temp += temp1

                if temp:
                    elements[key] = temp

            if elements:
                unit = {
                    'asset': 'camera',
                    'asset_type': '',
                    'elements_order': elementsOrder,
                    'elements': elements
                }
                result.append(unit)

        # Get normal assets
        # print "layoutInfo:",layoutInfo
        if not layoutInfo:
            return result

        for lay in layoutInfo:
            # print
            # print 'lay:',lay

            asset = lay['asset']
            assetType = lay['asset_type']
            part = lay['instance']
            trans = lay.get('transform')
            if not trans:
                trans = {}
            # print 'part:',part

            subs = lay.get('subs')
            if not subs:
                subs = []

            setup = elementsInfo.get(assetType)
            if not setup:
                setup = elementsInfo.get(defaultAType)

            if setup:
                elements = {}

                for key in setup.keys():
                    # print "Key:",key
                    # shape
                    # material

                    temp = []
                    for unit in setup[key]:
                        # print "unit:",unit
                        # {'type': 'shot', 'steps': 'nCloth', 'filetypes': 'abc'} unit:
                        # {'type': 'shot', 'steps': 'nHair', 'filetypes': 'ma'}
                        # {'type': 'asset', 'parts': 'material', 'steps': 'Texture', 'filetypes': 'ma'}
                        typ = unit.get('type')

                        if typ == 'shot':
                            kwargs = {
                                'database': self.database(),
                                'project': pro,
                                'sequence': shot.get('sequence'),
                                'shot': shot.get('code'),
                                'latest': True,
                                'enableCache': True
                            }
                            kwargs['parts'] = [part]
                            kwargs.update(unit)

                        else:
                            kwargs = {
                                'database': self.database(),
                                'project': pro,
                                'sequence': assetType,
                                'shot': asset,
                                'latest': True,
                                'enableCache': True
                            }
                            kwargs.update(unit)

                        # import pprint
                        # outputLog( 'Getting published files...')
                        # outputLog('kwargs:')
                        # outputLog(pprint.pformat(kwargs))

                        temp1 = plcr.getPublishedFiles(**kwargs)
                        # outputLog( 'result:')
                        # outputLog(pprint.pformat( temp1))
                        # outputLog( 'Done')

                        temp += temp1

                    elements[key] = temp

                if elements:
                    unit = {
                        'asset': asset,
                        'asset_type': assetType,
                        'elements_order': elementsOrder,
                        'elements': elements
                    }

                    if trans:
                        unit['transform'] = trans
                    if subs:
                        unit['subs'] = subs

                    result.append(unit)

        plcr.clearConfigCache()

        return result


def outputLog(msg):
    # print msg
    path = r'C:\Users\cgt\Desktop\test.txt'
    f = open(path, 'a')
    f.write(msg + '\n')
    f.close()


class TranslateAssemblyElements(Action):
    '''
    Translates assembly elements data to a list of versions.
    input data is the result of GetAssemblyElements action.

    Example:
    [
        {'shape': {}, 'material': {}},
        {},
    ]
    '''

    _defaultParms = {
        'input': '',
    }

    def run(self):
        data = self.parm('input')
        if not data:
            data = []

        result = []

        for d in data:
            info = {}
            trans = d.get('transform')
            if not trans:
                trans = {}
            if trans:
                info['transform'] = trans

            elements = d.get('elements')
            if not elements:
                elements = {}

            for key in elements.keys():
                if elements[key]:
                    info[key] = elements[key][0]

            if info:
                result.append(info)

        return result


class CreateVar(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        return self.parm('input')


class CreateDict(Action):
    _defaultParms = {}

    def run(self):
        result = {}
        for key in self._parms.keys():
            value = self.parm(key)
            result[key] = value

        return result


class SplitString(Action):
    _defaultParms = {
        'input': '',
        'splitter': '',
        'index': 0
    }

    def run(self):
        s = self.parm('input').split(".")[0]
        splitter = self.parm('splitter')
        index = self.parm('index')
        return s.split(splitter)[index]


class If(Action):
    _defaultParms = {}

    def run(self):
        go = []
        keys = self._parms.keys()
        for key in keys:
            key1 = '{%s}' % key
            caseValue = self.parseValue(key1, extraArgs=self._formatKeys)
            value = self.parm(key)
            if type(value) in (tuple, list):
                if caseValue in value:
                    go.append(1)
            else:
                if caseValue == value:
                    go.append(1)
        print "self._subs:", self._subs
        if len(go) == len(keys):
            action = self._subs[0]
        else:
            action = self._subs[1]

        # print
        # print 'If.parms:',self._parms
        # print 'action:',action

        action.setFormatKeys(self._formatKeys)
        r = self.engine().runAction(action)

        return r


# class ForLoop(Action):
#     _defaultParms = {
#         'input': '',
#     }
#
#     def count(self):
#         '''Count of the sub items.'''
#         n1 = len(self.parm('input'))
#         n2 = len(self.subs())
#         return n1 * n2
#
#     def run(self):
#         result = []
#
#         inputs = self.parm('input')
#         for info in inputs:
#             # print
#             # print 'ForLoop.info:'
#             # pprint.pprint(info)
#             # print
#
#             r = {}
#             for sub in self._subs:
#                 # print
#                 # print 'sub:',sub
#                 # print
#                 sub.setFormatKeys(info)
#                 r = self.engine().runAction(sub)
#
#             result.append(r)
#
#         return result
class ForLoop(Action):

    def run(self):
        result = []

        inputs = self.parm('input')
        for info in inputs:
            instance = info.split('_')[0]
            self.setParm('each_objects', info)
            self.setParm('instance', instance)
            r = self.runAction(self.parm('subs'), sys.modules[__name__])
            result.append(r)

        return result


class Boolean(Action):
    '''
    A boolean action.
    True to run sub node1, else to run sub node2.
    '''

    _defaultParms = {
        'input': '',
    }

    def run(self):
        node1, node2 = None, None
        n = len(self._subs)
        if n == 1:
            node1 = self._subs[0]
        elif n > 1:
            node1, node2 = self._subs[:2]

        r = self.parm('input')
        self.engine().setActionValue(self.name, r)

        # print 'result:',[r]

        if r:
            if node1:
                node1.run()
        else:
            if node2:
                node2.run()

        return r


class ExportScene(Action):
    _defaultParms = {
        'object': '',
        'output': '',
    }

    progressText = 'Exporting scene objects...'

    def run(self):
        sw = self.software()
        if sw:
            obj = self.parm('object')
            path = self.parm('output')
            makeFolder(path)

            if obj:
                try:
                    sw.clearSelection()
                    sw.select(obj)
                    sw.exportSelected(path)
                except:
                    showWorkfileError(sw)

            else:
                try:
                    sw.exportAll(path)
                except:
                    showWorkfileError(sw)

            return path


class HidObject(Action):
    _defaultParms = {
        'input': '',
    }

    progressText = 'Hid object rig_GRP group...'

    def run(self):
        # sw = self.software()
        objs = self.parm('input')
        # print 'objs:',[objs]
        import maya.cmds as cmds
        if type(objs) != list:
            objs = [objs]
        for sw in objs:
            if sw:
                name_space_list = sw.split(":")
                name_space_list.pop()
                name_space = ':'.join(name_space_list)
                hid_name = name_space + ':' + 'rig_GRP.visibility'
                try:
                    cmds.setAttr(hid_name, 0)
                except:
                    print u"error:没有发现这个对象请找绑定确认下", hid_name


# 输出abc时勾选 eulerFilter
class ExportAbc(Action):
    _defaultParms = {
        'input': '',
        'output': '',
        'single_frame': True,
        'options': [
            '-uvWrite',
            '-worldSpace',
            '-eulerFilter',
            '-dataFormat ogawa',
            '-ro',
            '-writeVisibility',
        ],
        'deleteArnoldAttr': False,
    }

    progressText = 'Exporting abc cache...'

    def frameRange(self):
        minT = cmds.playbackOptions(query=True, minTime=True)
        maxT = cmds.playbackOptions(query=True, maxTime=True)
        return [int(minT) - 1, int(maxT)]

    def run(self):
        cmds.select(clear=True)
        sw = self.software()
        objs = self.parm('input')
        if sw and objs:
            if type(objs) != list:
                objs = [objs]
            path = self.parm('output')
            options = self.parm('options')

            makeFolder(path)

            kwargs = {
                'path': path,
                'singleFrame': self.parm('single_frame'),
                'objects': objs
            }
            if options:
                kwargs['options'] = options

            deleteArnoldAttr = self.parm('deleteArnoldAttr')
            if deleteArnoldAttr:
                kwargs['deleteArnoldAttr'] = True

            kwargs['frameRange'] = self.frameRange()

            # hidden show type
            typeDic = hiddenShowType()

            # print "kwargs:", kwargs
            sw.exportAbc(**kwargs)

            # display show type
            displayShowType(typeDic=typeDic)
            return path


class ExportAbc2(Action):
    _defaultParms = {
        'input': '',
        'output': '',
        'single_frame': True,
        'options': [
            '-uvWrite',
            '-worldSpace',
            '-eulerFilter',
            '-dataFormat ogawa',
            '-ro',
            '-writeVisibility',
        ],
        'deleteArnoldAttr': False,
    }

    progressText = 'Exporting abc cache...'

    def frameRange(self):
        minT = cmds.playbackOptions(query=True, minTime=True)
        maxT = cmds.playbackOptions(query=True, maxTime=True)
        return [int(minT) - 1, int(maxT) + 1]

    def run(self):
        import maya.cmds as cmds
        cmds.select(clear=True)
        sw = self.software()
        objs = self.parm('input')
        if sw and objs:
            if type(objs) != list:
                objs = [objs]
            path = self.parm('output')
            options = self.parm('options')

            makeFolder(path)

            kwargs = {
                'path': path,
                'singleFrame': self.parm('single_frame'),
                'objects': objs
            }
            if options:
                kwargs['options'] = options

            deleteArnoldAttr = self.parm('deleteArnoldAttr')
            if deleteArnoldAttr:
                kwargs['deleteArnoldAttr'] = True

            kwargs['frameRange'] = self.frameRange()

            print "kwargs:", kwargs

            # hidden show type
            typeDic = hiddenShowType()
            #
            sw.exportAbc(**kwargs)

            # display show type
            showTyp = displayShowType(typeDic=typeDic)


# class ExportAbc2(Action):

# _defaultParms = {
# 'input': '',
# 'output': '',
# 'single_frame': True
# }

# def run(self):
# import maya.cmds as cmds
# cmds.select(clear=True)
# sw = self.software()
# tops = self.parm('input')
# if sw and tops:
# path = self.parm('output')
# sw.exportAbc(path, singleFrame=self.parm('single_frame'),
# objects=tops)
# return path

class ExportGpu(Action):
    _defaultParms = {
        'input': '',
        'output': '',
        'single_frame': True
    }

    progressText = 'Exporting gpu cache...'

    def run(self):
        sw = self.software()
        tops = self.parm('input')
        if sw and tops:
            path = self.parm('output')
            makeFolder(path)
            sw.exportGpuCache(path, singleFrame=self.parm('single_frame'),
                              objects=tops)
            return path


class ExportRedshiftProxy(Action):
    _defaultParms = {
        'single_frame': True,
        'frame_range': None,
        'input': [],
        'output': '',
    }

    def run(self):
        sw = self.software()
        tops = self.parm('input')
        if sw and tops:
            singleFrame = self.parm('single_frame')
            frameRange = self.parm('frame_range')
            path = self.parm('output')
            makeFolder(path)
            sw.exportRedshiftProxy(path, singleFrame=singleFrame,
                                   frameRange=frameRange,
                                   objects=tops)
            return path


class ExportRedshiftProxyScene(Action):
    _defaultParms = {
        'single_frame': True,
        'frame_range': None,
        'input': [],
        'output': '',
    }

    progressText = 'Exporting Redshift proxy...'

    def run(self):
        sw = self.software()
        tops = self.parm('input')
        if sw and tops:
            singleFrame = self.parm('single_frame')
            frameRange = self.parm('frame_range')
            path = self.parm('output')
            makeFolder(path)
            sw.exportRedshiftProxyScene(path, singleFrame=singleFrame,
                                        frameRange=frameRange,
                                        objects=tops)
            return path


class ExportBoundingbox(Action):
    _defaultParms = {
        'input': '',
        'output': '',
    }

    progressText = 'Exporting bounding box...'

    def run(self):
        sw = self.software()
        tops = self.parm('input')
        if sw and tops:
            path = self.parm('output')
            makeFolder(path)
            sw.exportBoundingbox(path, tops[0])
            return path


class CreateAssemblyDefinitionScene(Action):
    _defaultParms = {
        'output': '',
        'name': '',
        'files': [],
        'actived': ''
    }

    progressText = 'Creating assembly scene...'

    def run(self):
        sw = self.software()
        files = self.parm('files')
        if sw and files:
            name = self.parm('name')
            path = self.parm('output')
            actived = self.parm('actived')
            sw.createAssemblyDefinitionScene(path, name=name,
                                             files=files,
                                             actived=actived)
            return path


class CreateAssemblyReferenceScene(Action):
    _defaultParms = {
        'input': '',
        'output': '',
        'name': '',
        'actived': ''
    }

    def run(self):
        sw = self.software()
        if sw:
            name = self.parm('name')
            adPath = self.parm('input')
            path = self.parm('output')
            actived = self.parm('actived')
            sw.createAssemblyReferenceScene(path, adPath=adPath,
                                            name=name,
                                            actived=actived)
            return path


class GetSceneMaterials(Action):
    _defaultParms = {
        'remove_namespace': False
    }

    def run(self):
        sw = self.software()
        if sw:
            removeNamespace = self.parm('remove_namespace')
            return sw.getMaterials(removeNamespace=removeNamespace)

        return {}


class ExportMaterials(Action):
    _defaultParms = {
        'export_textures': False,
        'textures_root': '',
        'output': '',
        'mapping_filename': 'mapping',
        'generate_mapping': True,
        'materials': {}
    }

    progressText = 'Exporting scene materials...'

    def run(self):
        sw = self.software()
        if sw:
            output = self.parm('output')
            makeFolder(output)
            mappingFilename = self.parm('mapping_filename')
            generateMapping = self.parm('generate_mapping')
            materials = self.parm('materials')

            sw.exportMaterials(output, generateMapping=generateMapping,
                               mappingFilename=mappingFilename,
                               removeNamespace=True,
                               materials=materials)
            return output


class ExportMaterials2(Action):
    '''Exports all materials and objects materials mapping to a json file.'''

    _defaultParms = {
        'export_textures': False,
        'textures_root': '',
        'output': '',
        'configs': {},
        'objects': []
    }

    def run(self):
        sw = self.software()
        if sw:
            output = self.parm('output')
            configs = self.parm('configs')
            objs = self.parm('objects')
            makeFolder(output)

            # print
            # print 'output:',output

            sw.exportMaterials2(output, removeNamespace=True,
                                configs=configs, objects=objs)
            return output


def getFileMd5(path):
    import md5

    if os.path.isfile(path):
        f = open(path, 'rb')
        txt = f.read()
        f.close()

        result = md5.new(txt)
        return result.hexdigest()


class ExportTextures(Action):
    '''
    Copy textures to the target folder, version up each time copying the file.
    Check md5 of the latest version file to make sure only copy different files.

    Example:
        filepath:
            TST\assets\chr\dog\srf\work\textures\body_dif.1001.tif
        targetPath:
            TST\assets\chr\dog\srf\publish\textures
        files in targetPath:
            body_dif.1001
                body_dif.1001_v001.tif
                body_dif.1001_v002.tif
    '''

    _defaultParms = {
        'material_path': '',
        'output': '',
        'version_pattern': '_v###',
    }

    def run(self):
        sw = self.software()
        if sw:
            matPath = self.parm('material_path')
            output = self.parm('output')
            pattern = self.parm('version_pattern')

            textures = sw.getTexturePaths()

            pathInfo = {}
            for texPath in textures.values():
                if os.path.isfile(texPath):

                    filename = os.path.basename(texPath)
                    baseName, ext = os.path.splitext(filename)
                    folder = '%s/%s' % (output, baseName)
                    if os.path.exists(folder):
                        files = os.listdir(folder)
                    else:
                        os.makedirs(folder)
                        files = []

                    filePattern = '%s%s%s' % (baseName, pattern, ext)
                    r = getLatestVersion(files, filePattern)

                    # Check md5
                    latestPath = '%s/%s' % (folder, r['latest_file'])
                    latestMd5 = getFileMd5(latestPath)
                    fileMd5 = getFileMd5(texPath)
                    # print '%s: %s' % (latestPath, latestMd5)
                    # print '%s: %s' % (texPath, fileMd5)
                    if fileMd5 == latestMd5:
                        targetPath = latestPath
                    else:
                        # Copy the target file to versions folder
                        targetPath = '%s/%s' % (folder, r['current_file'])
                        copyFile(texPath, targetPath)

                    pathInfo[texPath] = targetPath

            if matPath:
                sw.replaceTexturePaths(matPath, pathInfo)


class ExportTextures2(Action):
    '''Copy textures to the target folder, override the existing files.'''

    _defaultParms = {
        'textures': [],
        'material_path': '',
        'output': '',
    }

    def judgeUpdate(self, chian_file, usa_file):
        """
        judge file whether newest
        :param chian_file: server file
        :param usa_file: local file
        :return: bool
        """
        import time
        if os.path.exists(usa_file):

            # get file change time
            chian_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.stat(chian_file).st_mtime))
            usa_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.stat(usa_file).st_mtime))
            # judge file change time
            if chian_time != usa_time:
                # print chian_time, usa_time
                return True
            else:
                return False
        else:
            # print 222222222
            return True

    def judgeUpdateSize(self, chian_file, usa_file):
        """
        judge file whether newest
        :param chian_file: server file
        :param usa_file: local file
        :return: bool
        """
        if os.path.exists(usa_file):

            # get file change time
            chian_time = os.path.getsize(chian_file)
            usa_time = os.path.getsize(usa_file)
            # judge file change time
            if chian_time != usa_time:
                return True
            else:
                return False
        else:
            return True

    def run(self):
        sw = self.software()
        import shutil
        if sw:
            matPath = self.parm('material_path')
            output = self.parm('output')
            textures = self.parm('textures')

            if not textures:
                textures = sw.getTexturePaths().values()

            pathInfo = {}
            num = 0
            for texPath in textures:
                if os.path.isfile(texPath):
                    filename = os.path.basename(texPath)
                    targetPath = '%s/%s' % (output, filename)

                    # Check md5
                    ##texPathMd5 = getFileMd5(texPath)
                    ##targetPathMd5 = getFileMd5(targetPath)
                    # print '%s: %s' % (latestPath, latestMd5)
                    # print '%s: %s' % (texPath, fileMd5)
                    ##if texPathMd5 != targetPathMd5:
                    if self.judgeUpdateSize(texPath, targetPath):
                        makeFolder(targetPath)
                        shutil.copy2(texPath, targetPath)
                    pathInfo[texPath] = targetPath

            if matPath:
                sw.replaceTexturePaths(matPath, pathInfo)


class ExportTextures3(Action):
    '''Copy textures to the target folder, override the existing files.'''

    _defaultParms = {
        'output': '',
        'replaceOutput': '',
        'rsNormalMap': False,
    }

    def run(self):
        sw = self.software()

        if sw:
            output = self.parm('output')
            replaceOutput = self.parm('replaceOutput')
            rsNormalMap = self.parm('rsNormalMap')

            # print "rsNormalMap:",rsNormalMap
            textures = sw.getTexturePaths2(rsNormalMap=rsNormalMap)
            pathInfo = []
            # textures: {'file':{'fileNodes':[],}}

            for typ in textures.keys():
                texDic = textures[typ]
                for fn in texDic.keys():
                    texPathList = texDic[fn]
                    for texPath in texPathList:
                        if os.path.isfile(texPath):
                            texPath = texPath.replace('\\', '/')
                            filename = os.path.basename(texPath)
                            # if filename.split(".")[-1] == "tx":
                            # continue
                            # b = filename.split(".")
                            # b[-1] = "tif"
                            # filename = ".".join(b)
                            targetPath = '%s/%s' % (output, filename)

                            # Check md5
                            texPathMd5 = getFileMd5(texPath)
                            targetPathMd5 = getFileMd5(targetPath)
                            # print '%s: %s' % (latestPath, latestMd5)
                            # print '%s: %s' % (texPath, fileMd5)
                            if texPathMd5 != targetPathMd5:
                                makeFolder(targetPath)
                                # if not os.path.exists(targetPath):
                                # print 'source', texPath
                                # print 'target', targetPath
                                copyFile(texPath, targetPath)
                            else:
                                print "copy", texPathMd5

                            if replaceOutput:
                                targetPath = '%s/%s' % (replaceOutput, filename)
                            #      ['file','fileNodes','path1','path2']
                            pathInfo.append([typ, fn, texPath, targetPath])

            return pathInfo


class replaceTexturePath(Action):
    _defaultParms = {
        'input': [],
        'replaceTo': '',
    }

    def run(self):
        '''
        replaceTo is only "new" or "old"
        '''
        sw = self.software()
        if sw:
            pathInfo = self.parm('input')
            replaceTo = self.parm('replaceTo')

            sw.replaceTexturePaths2(pathInfo, replaceTo=replaceTo)


class ExportSets(Action):
    _defaultParms = {
        'set_types': [],
    }

    progressText = 'Exporting scene sets...'

    def run(self):
        sw = self.software()
        if sw:
            step = self.task().get('step')
            allTypes = engine.getStepConfig(step, 'set_types')
            types = self.parm('set_types')

            if not types:
                types = []
            if not allTypes:
                allTypes = []

            parms = []
            for t in types:
                for t1 in allTypes:
                    name = t1.get('name')
                    if name and t == name:
                        ps = t1.get('parms')
                        if not ps:
                            ps = []
                        parms.extend(ps)
                        break

            # print 'set types:',types
            # print 'set parms:',parms

            info = sw.getSets(types=types, parms=parms)

            infoPath = self.parm('output')
            if info:
                makeFolder(infoPath)
                txt = json.dumps(info, indent=4)
                f = open(infoPath, 'w')
                f.write(txt)
                f.close()

            return infoPath


class ExportSceneLayout(Action):
    _defaultParms = {
        'asset_types': ['env'],
        'extra_group': '',
        'extra_group_asset_type': 'other',
        'extra_group_asset': 'other',
        'input': '{top_level_meshes}',
        'output': '{version_root}/layout.json',
        'all_subs_asset_types': [],
        'all_subs': False,
        'default_transform': {
            "translateX": 0.0,
            "translateY": 0.0,
            "translateZ": 0.0,
            "scaleX": 1.0,
            "scaleY": 1.0,
            "scaleZ": 1.0,
            "rotateX": 0.0,
            "rotateY": 0.0,
            "rotateZ": 0.0
        },
    }

    def getTransform(self, obj):
        sw = self.software()
        defaultTransform = self.parm('default_transform')
        r = sw.getTransform(obj)
        if defaultTransform:
            if r != defaultTransform:
                return r
        else:
            return r

        return r

    def run(self):
        sw = self.software()
        if sw:
            assetTypes = self.parm('asset_types')
            allSubsATypes = self.parm('all_subs_asset_types')

            # Get scene output assets
            refs = sw.getReferenceObjects()
            refs += sw.getGpuCaches()
            refs += sw.getAssemblyReferences()

            alll = {}
            for i in refs:
                info = self.engine().getInfoFromPath(i['path'], enableCache=True)
                asset = info.get('shot')
                assetType = info.get('sequence')

                go = False
                if assetTypes:
                    if assetType in assetTypes:
                        go = True
                else:
                    go = True

                if go:
                    d = {
                        'asset': asset,
                        'asset_type': assetType,
                        'name': i['name'],
                        'full_name': i['full_name'],
                        'namespace': i['namespace'],
                        'node_type': i['node_type'],
                        'transform': self.getTransform(i['transform_node'])
                    }
                    # Get transform of all sub nodes
                    if assetType in allSubsATypes:
                        if self.parm('all_subs'):
                            subTransforms = []
                            subs = sw.getAllSubChildren(i['transform_node'], type='transform')
                            for sub in subs:
                                t = self.getTransform(sub)
                                if t:
                                    info = {
                                        'name': sub.split('|')[-1],
                                        'full_name': sub,
                                        'transform': t
                                    }
                                    subTransforms.append(info)

                            d['subs'] = subTransforms

                    if not alll.has_key(asset):
                        alll[asset] = []
                    alll[asset].append(d)

            result = _addAssetInstance(alll)
            extraGroup = self.parm('extra_group')
            if sw.exists(extraGroup):
                extraGroupAssetType = self.parm('extra_group_asset_type')
                extraGroupAsset = self.parm('extra_group_asset')
                info = {
                    'instance': extraGroupAsset,
                    'asset': extraGroupAsset,
                    'asset_type': extraGroupAssetType,
                    'name': extraGroup,
                    'full_name': extraGroup,
                    'namespace': '',
                    'node_type': 'transform',
                    'transform': self.getTransform(extraGroup)
                }
                result.append(info)

            # Make the json file
            path = self.parm('output')
            makeFolder(path)
            txt = json.dumps(result, indent=4)
            f = open(path, 'w')
            f.write(txt)
            f.close()

            return path


# 返回当前相机名
class CameraName(Action):
    def run(self):
        sw = self.software()
        if sw:
            cams = sw.getCameras()
            cams = [c['full_path'] for c in cams if "cam" in c['name']]

            return cams


class ExportCameras(Action):
    _defaultParms = {
        'input': '{current_file}',
        'output': '{version_root}/cameras.abc',
        'cam_name': '',
    }

    def run(self):
        sw = self.software()
        if sw:
            cams = sw.getCameras()

            cam_name = self.parm('cam_name')
            cams = [c['full_path'] for c in cams if "cam" in c['name']]
            # print cams

            path = self.parm('output')

            makeFolder(path)

            sw.exportAbc(path, objects=cams)

            return path


class MakeSceneThumbnail(Action):
    _defaultParms = {
        'input': '{current_file}',
        'output': '{version_root}/thumbnail.jpg',
    }

    progressText = 'Making scene thumbnail...'

    def run(self):
        sw = self.software()
        if sw:
            path = self.parm('output')
            makeFolder(path)
            sw.makeSceneThumbnail(path)
            return path


class GetRenderFiles(Action):

    def run(self):
        files = self.parm('input')

        if not files:
            files = []

        for f in files:
            # f['path'] = f['full_path']
            f['part'] = f['pass']

        return files


class NewMakePublishInfoFile(Action):
    progressText = 'Creating a version to database...'

    def run(self):
        info = {
            'artist': self.user(),
            'description': self.parm('description'),
            'version_type': self.parm('version_type'),
            'name': self.parm('name'),
            'part': self.parm('part'),
            'version': self.parm('version'),
            'thumbnail': self.parm('thumbnail'),
            'path': os.path.dirname(self.parm('output')),
        }
        task_info = engine.getTaskFromEnv()
        if task_info['type'] == 'asset':
            info['asset_type'] = task_info['sequence']

        info.update(task_info)

        filters = [
            'type', 'sequence', 'shot', 'asset_type', 'description',
            'asset', 'step', 'task_name', 'part', 'thumbnail', 'version_type',
            'pipeline_type', 'name', 'path', 'version'
        ]

        update_info = dict()
        for sign in filters:
            update_info[sign] = info.get(sign)

        # print 'update_info'
        # pprint.pprint(update_info)

        version_id = self.database().doesVersionExist(update_info)
        if version_id:
            self.database().updateVersionInfo(version_id, info)
        else:
            self.database().createVersion(info)


class MakePublishInfoFile(Action):
    _defaultParms = {
        'input': '',
        'output': '{version_root}/info.json',
        'thumbnail': '{scene_thumbnail}',
        'version_type': 'publish',
        'part': '{step}',
        'level': '',
        'version': '{workfile_version}',
        'name': '{shot}_{step}_{workfile_version}',
        'description': '{description}',
        'entity_type': 'version',
        'asset': '',
        'files': [],
        'create_json_file': False,
        'only_include_existing_files': False
    }

    progressText = 'Creating a version to database...'

    def run(self):
        # Get parms
        name = self.parm('name')
        part = self.parm('part')
        thumbnail = self.parm('thumbnail')
        version = self.parm('version')
        infoPath = self.parm('output')
        folder = os.path.dirname(infoPath)
        files = self.parm('files')
        eType = self.parm('entity_type')
        comments = self.parm('description')
        versionType = self.parm('version_type')
        asset = self.parm('asset')
        level = self.parm('level')
        onlyIncludeExistingFiles = self.parm('only_include_existing_files')

        # Default parm value
        if not name:
            name = os.path.basename(folder)

        if not version:
            version = self.getVersion(folder)

        thumbnail = {
            'entity_type': 'image',
            'path': self.parsePath(thumbnail, root=folder),
        }

        # print 'files:',files

        files1 = []
        for f in files:
            if f:
                if type(f) == dict:
                    path = f.get('path')

                    go = False
                    if onlyIncludeExistingFiles:
                        if os.path.exists(path):
                            go = True
                    else:
                        go = True

                    if go:
                        f['path'] = self.parsePath(path, root=folder)
                        f['entity_type'] = 'published_file'
                        files1.append(f)

                elif type(f) in (str, unicode):
                    go = False
                    if onlyIncludeExistingFiles:
                        if os.path.exists(f):
                            go = True
                    else:
                        go = True

                    if go:
                        ext = os.path.splitext(f)[-1]
                        ext = ext.replace('.', '')
                        d = {
                            'filetype': ext,
                            'path': self.parsePath(f, root=folder)
                        }
                        files1.append(d)

        # Get info
        info = plcr.getEnvContext(self.task())
        info = plcr.getTaskFromEnv(info)
        info['task'] = info.get('code')
        try:
            del info['code']
        except:
            pass

        info1 = {
            'entity_type': eType,
            'artist': self.user(),
            'description': comments,
            'files': files1,
            'version_type': versionType,
            'name': name,
            'part': part,
            'version': version,
            'thumbnail': thumbnail,
            'path': folder,
            'level': level
        }

        if asset:
            info1['asset'] = asset

        info.update(info1)

        # Make the json file
        if self.parm('create_json_file'):
            makeFolder(infoPath)
            txt = json.dumps(info, indent=4)
            f = open(infoPath, 'w')
            f.write(txt)
            f.close()

        # Create a version on CGTeamwork
        VersionInfo = info.copy()  # jxy
        # Find existing version
        filterKeys = [
            'project', 'type', 'sequence', 'shot', 'asset_type',
            'asset', 'step', 'task', 'part', 'entity_type',
            'version_type', 'pipeline_type', 'name'
        ]
        filters = []
        for k in filterKeys:
            v = VersionInfo.get(k)
            if v not in ('', None):
                f = [k, '=', v]
                filters.append(f)

        r = self.database().doesVersionExist(self.database().getDataBase(), filters=filters)  # jxy
        # print 'result:',r

        if r:
            self.database().updateVersionInfo(self.database().getDataBase(), r['id'], info)

        else:
            # Create a new one
            self.database().createVersion(self.database().getDataBase(), info)  # jxy

        # Create a latest version
        if self.parm('create_latest_version'):
            latestInfo = info.copy()

            # Find existing version
            filterKeys = [
                'project', 'type', 'sequence', 'shot', 'asset_type',
                'asset', 'step', 'task', 'part', 'entity_type',
                'version_type', 'pipeline_type'
            ]
            filters = []
            for k in filterKeys:
                v = latestInfo.get(k)
                if v not in ('', None):
                    f = [k, '=', v]
                    filters.append(f)

            r = self.database().doesLatestVersionExist(self.database().getDataBase(), filters=filters)

            if r:
                self.database().updateLatestVersionInfo(self.database().getDataBase(), r['id'], latestInfo)

            else:
                # Create a new one
                self.database().createLatestVersion(self.database().getDataBase(), latestInfo)

        return info


class CreateLatestVersion(Action):
    _defaultParms = {
        'path': '{version_root}',
        'thumbnail': '{scene_thumbnail}',
        'version_type': 'publish',
        'part': '{step}',
        'level': '',
        'version': 'latest',
        'name': '{shot}_{step}_{workfile_version}',
        'description': '{description}',
        'entity_type': 'version',
        'asset': '',
        'files': []
    }

    def run(self):
        # Get parms
        name = self.parm('name')
        part = self.parm('part')
        thumbnail = self.parm('thumbnail')
        version = self.parm('version')
        folder = self.parm('path')
        files = self.parm('files')
        eType = self.parm('entity_type')
        comments = self.parm('description')
        versionType = self.parm('version_type')
        asset = self.parm('asset')
        level = self.parm('level')
        # Default parm value
        if not name:
            name = os.path.basename(folder)

        if not version:
            version = 'latest'

        thumbnail = {
            'entity_type': 'image',
            'path': self.parsePath(thumbnail, root=folder),
        }

        # print 'files:',files

        files1 = []
        for f in files:
            if f:
                if type(f) == dict:
                    f['path'] = self.parsePath(f.get('path'), root=folder)
                    files1.append(f)

                elif type(f) in (str, unicode):
                    ext = os.path.splitext(f)[-1]
                    ext = ext.replace('.', '')
                    d = {
                        'filetype': ext,
                        'path': self.parsePath(f, root=folder)
                    }
                    files1.append(d)

        # Get info
        info = copy.deepcopy(self.task())
        info['task'] = info.get('code')
        try:
            del info['code']
        except:
            pass

        info1 = {
            'entity_type': eType,
            'artist': self.user(),
            'description': comments,
            'files': files1,
            'version_type': versionType,
            'name': name,
            'part': part,
            'version': version,
            'thumbnail': thumbnail,
            'path': folder,
            'level': level
        }

        if asset:
            info1['asset'] = asset
        info.update(info1)

        # Find existing version
        filterKeys = [
            'project', 'type', 'sequence', 'shot', 'asset_type',
            'asset', 'step', 'task', 'part',  # 'entity_type',
            'version_type', 'pipeline_type', 'version'
        ]
        if level:
            filterKeys.append('level')

        filters = []
        for k in filterKeys:
            v = info.get(k)
            if v not in ('', None):
                f = [k, '=', v]
                filters.append(f)

        r = self.database().doesVersionExist(self.database().getDataBase(), filters=filters)

        # print 'result:',r

        if r:
            self.database().updateVersionInfo(self.database().getDataBase(), r['id'], info)

        else:
            # Create a new one
            self.database().createVersion(self.database().getDataBase(), info)

        return info


class UpdateVersionInfo(Action):
    _defaultParms = {
        'project': '',
        'id': '',
        'data': {}
    }

    def run(self):
        project = self.parm('project')
        id_ = self.parm('id')
        data = self.parm('data')

        if not project:
            project = self.database().getDataBase()

        self.database().updateVersionInfo(project, id_, data)


class CreateVersionNote(Action):
    _defaultParms = {
        'input': {},
    }

    progressText = 'Creating a note to database...'

    def run(self):
        project = self.database().getDataBase()
        entity = self.task().get('type') + '_task'
        taskId = self.task().get('task_id')

        # Get note body
        info = self.parm('input')
        keys = [
            'type', 'sequence', 'shot', 'asset_type',
            'asset', 'step', 'task', 'part',
            'version_type', 'version', 'description'
        ]

        text = u'%(artist)s 提交了一个新版本 %(version_type)s %(name)s'
        text += '<br>'
        text += u'%(description)s'
        text = text % info
        # lines = [title]
        # lines.append('')
        # for key in keys:
        #    v = info.get(key)
        #    if not v:
        #        v = ''
        #    line = '%s: %s' % (key, v)
        #    lines.append(line)

        # text = '<br>'.join(lines)

        self.database().createNote(project, entity, taskId, text)


class MakePreviewInfoFile(Action):
    _defaultParms = {
        'input': '',
        'output': '{version_root}/info.json',
        'thumbnail': '{scene_thumbnail}',
        'version_type': 'publish',
        'version': '{workfile_version}',
        'name': '{shot}_{step}_{workfile_version}',
        'description': '{description}',
        'entity_type': 'version',
        'asset': '',
        'file': []
    }

    def run(self):
        ''


class MakeWorkfileInfoFile(Action):
    _defaultParms = {
        'input': '{current_file}',
        'description': '{description}',
    }

    def run(self):
        # Get parms
        path = self.parm('input')

        infoPath = '%s.json' % path
        info = {
            'entity_type': 'workfile',
            'artist': self.user(),
            'description': self.parm('description'),
        }

        makeFolder(infoPath)
        txt = json.dumps(info, indent=4)
        f = open(infoPath, 'w')
        f.write(txt)
        f.close()

        return info

class SubmitToDatabase(Action):
    _defaultParms = {
        'input': '{VersionRoot}',
        'description': '{description}',
    }

    progressText = 'Submitting to database...'

    def run(self):
        path = self.parm('input')
        comments = self.parm('description')

        if type(path) == list:
            files = path
        else:
            files = [path]

        # Connect to CGTeamwork
        kwargs = {
            'project': self.task().get('project'),
            'type': self.task().get('type'),
            'taskId': self.task().get('task_id'),
            'files': files,
            'description': comments,
            'state': self.parm('state') or 'Submit'
        }
        # print
        # print 'kwargs:'
        # print kwargs
        if self.task().get('pipeline_type') == "asset":
            self.database().submit(**kwargs)


# 镜头提交信息的时候，在note里添加文件中角色资产的版本号， 音频文件名 和 文件的帧范围
class SubmitCharVersionDatabase(Action):
    _defaultParms = {
        'input': '{VersionRoot}',
        'description': '{description}',
    }

    progressText = 'Submitting to database...'

    def getCharAsset(self):

        data = engine.getTaskFromEnv()
        list = []
        t_tw = cgtw2.tw()
        task_id_list = t_tw.task.get_id(self.database().getDataBase(), "shot", [["shot.shot", "=", data["shot"]]])
        i = task_id_list[0]
        link_id_list = t_tw.link.get_asset(self.database().getDataBase(), 'shot', 'task', i)
        if len(link_id_list) > 0:
            t_asset_list = t_tw.info.get(self.database().getDataBase(), 'asset', link_id_list, ['asset.asset_name'])
            for n in t_asset_list:
                # print u"资产信息:",n
                list.append(n["asset.asset_name"])

        temp = []
        for i in list:
            if "char" in i:
                temp.append(i)
        return temp

    def get_audio_rig(self):
        # 获取reference文件的绑定版本号，如果不带版本号就返回approve/history文件夹下版本号最高的文件，如果有版本号就返回本身
        data = engine.getTaskFromEnv()

        if data['type'] == 'shot':
            if cmds.ls(type="audio"):
                node = cmds.ls(type="audio")[0]
                audio_path = cmds.getAttr(node + ".filename")
                audio = os.path.basename(audio_path).split(".")[0]
            else:
                audio = "None"

            RFfiles = []
            for i in cmds.ls(rf=1):
                if "_UNKNOWN_REF_NODE_" not in i:
                    try:
                        path = cmds.referenceQuery(i, filename=True)
                        if "{" not in path:
                            RFfiles.append(path)
                    except:
                        pass
            RFfiles = list(set(RFfiles))

            char = self.getCharAsset()

            charfile = {}
            message = ''
            for file in RFfiles:
                file = file.replace("//", "/")
                if file.split("/")[3] == "char":
                    charname = file.split("/")[4]
                    charname = charname[0].lower() + charname[1:]
                    t_tw = cgtw.tw()
                    t_shot = t_tw.info_module(self.database().getDataBase(), "version")
                    filters = ([
                        ["version.step", "=", "Rig"],
                        "and",
                        ["version.version_type", "=", "publish"],
                        "and",
                        ["version.shot", "=", charname]
                    ]
                    )
                    t_shot.init_with_filter(filters)
                    version = []
                    for i in t_shot.get(["version.version"]):
                        version.append(i['version.version'])
                    version.sort()

                    mes = {}
                    ver = "".join([x for x in os.path.basename(file) if x.isdigit()])
                    if ver:
                        mes['version'] = "v" + ver
                    else:
                        mes['version'] = version[-1]
                    if version:
                        mes['last_version'] = version[-1]
                        charfile[charname] = mes
                    else:
                        message += "Asset '%s' is not publish <br> " % charname
                else:
                    pass

            if charfile:
                for num, ch in enumerate(charfile):
                    if charfile[ch]['version'] != charfile[ch]['last_version']:
                        message += str(
                            num + 1) + ". '%s' current version is '%s', but the lasted version is '%s' <br>" % (
                                       ch, charfile[ch]['version'], charfile[ch]['last_version'])
                    else:
                        message += str(num + 1) + ". '%s' current version is the latest version '%s' <br>" % (
                            ch, charfile[ch]['version'])
                self.rigNotes = message.replace('<br>', '\n')
            message = "<br>Audio file is {}. ".format(audio) + message

            start_f = int(cmds.playbackOptions(q=1, ast=1))
            end_f = int(cmds.playbackOptions(q=1, aet=1))

            t_tw = cgtw.tw()
            data_task = engine.getTaskFromEnv()
            data_base = dbif.CGT().getDataBase()
            t_shot = t_tw.info_module(data_base, "shot")
            t_shot.init_with_id([data_task['shot_id']])

            start_f1 = t_shot.get(['shot.first_frame'])[0]['shot.first_frame']
            end_f1 = t_shot.get(['shot.last_frame'])[0]['shot.last_frame']
            message += "<br> Frame range: Before(%s to %s)  After(%s to %s)" % (
                str(start_f1), str(end_f1), str(start_f), str(end_f))

            return message

        else:
            return ''

    def model_note(self):
        # 获取绑定版本m_all_CTL上的"modelVersion"信息
        add = ["modelVersion", "rigVersion"]
        message = ''
        for i in add:
            try:
                if i in cmds.listAttr("m_all_CTL"):
                    rigv = cmds.getAttr('m_all_CTL.modelVersion')
                    message += "<br> '%s' is %s" % (i, rigv)
            except:
                message += ''
        return message

    def setTaskDescription(self, des, data_base, model, taskId):
        tw2 = cgtw2.tw()

        dic = {'shot.desc_shot': des,
               }

        tw2.info.set(str(data_base), str(model), [taskId], dic)

    def run(self):
        files = self.parm('input')
        comments = self.parm('description')
        self.rigNotes = ''

        # Connect to CGTeamwork
        # 如果是绑定环节需要发送"self.model_note()"当前模型版本号的note
        if engine.getTaskFromEnv()['step'] == 'Rig':
            extra = self.model_note()
            kwargs = {
                'project': self.project(),
                'type': self.task().get('type'),
                'taskId': self.task().get('task_id'),
                'files': files,
                'description': comments + extra,
                'state': self.parm('state')
            }
        # 如果是动画环节需要发送"self.get_audio_rig()"当前模型版本号的note
        else:
            extra = self.get_audio_rig()
            kwargs = {
                'project': self.project(),
                'type': self.task().get('type'),
                'taskId': self.task().get('task_id'),
                'files': files,
                'description': comments + extra,
                'state': self.parm('state')
            }
        self.database().submit(**kwargs)

        # set shot description
        typ = self.task().get('type')
        model = typ
        shotId = self.task().get('shot_id')
        data_base = dbif.CGT().getDataBase()

        if typ == 'shot':
            if self.rigNotes:
                # print "self.rigNotes:",self.rigNotes
                ##############
                motion_frame = cmds.getAttr("defaultArnoldRenderOptions.motion_frames")
                notes = "MotionBlur(%s)" % (str(round(motion_frame, 3)))
                notes += self.rigNotes
                ##############
                self.setTaskDescription(notes, data_base, model, shotId)


# 发送状态是Approved的note
class SubmitApprovedDatabase(Action):
    _defaultParms = {
        'input': '{VersionRoot}',
        'description': '{description}',
        'version_path': '',
    }

    progressText = 'Submitting to database...'

    def getCharAsset(self):
        data = engine.getTaskFromEnv()
        list = []
        t_tw = cgtw2.tw()
        task_id_list = t_tw.task.get_id(self.database().getDataBase(), "shot", [["shot.shot", "=", data["shot"]]])
        i = task_id_list[0]
        link_id_list = t_tw.link.get_asset(self.database().getDataBase(), 'shot', 'task', i)
        if len(link_id_list) > 0:
            t_asset_list = t_tw.info.get(self.database().getDataBase(), 'asset', link_id_list, ['asset.asset_name'])
            for n in t_asset_list:
                # print u"资产信息:",n
                list.append(n["asset.asset_name"])

        temp = []
        for i in list:
            if "char" in i or "prop" in i:
                temp.append(i)
        return temp

    def get_audio_rig(self):
        # 获取reference文件的绑定版本号，如果不带版本号就返回approve/history文件夹下版本号最高的文件，如果有版本号就返回本身
        data = engine.getTaskFromEnv()

        if data['type'] == 'shot':
            if cmds.ls(type="audio"):
                node = cmds.ls(type="audio")[0]
                audio_path = cmds.getAttr(node + ".filename")
                audio = os.path.basename(audio_path).split(".")[0]
            else:
                audio = "None"

            RFfiles = []
            for i in cmds.ls(rf=1):
                if "_UNKNOWN_REF_NODE_" not in i:
                    try:
                        path = cmds.referenceQuery(i, filename=True)
                        if "{" not in path:
                            RFfiles.append(path)
                    except:
                        pass
            RFfiles = list(set(RFfiles))

            char = self.getCharAsset()

            charfile = {}
            message = ''
            for file in RFfiles:
                file = file.replace("//", "/")
                if file.split("/")[3] == "char" or (file.split("/")[3] == "prop" and "history" in file):
                    charname = file.split("/")[4]
                    charname = charname[0].lower() + charname[1:]
                    t_tw = cgtw.tw()
                    t_shot = t_tw.info_module(self.database().getDataBase(), "version")
                    filters = ([
                        ["version.step", "=", "Rig"],
                        "and",
                        ["version.version_type", "=", "publish"],
                        "and",
                        ["version.shot", "=", charname]
                    ]
                    )
                    t_shot.init_with_filter(filters)
                    version = []
                    for i in t_shot.get(["version.version"]):
                        version.append(i['version.version'])
                    version.sort()

                    mes = {}
                    ver = "".join([x for x in os.path.basename(file) if x.isdigit()])
                    if ver:
                        mes['version'] = "v" + ver
                    if version:
                        mes['last_version'] = version[-1]
                        charfile[charname] = mes
                    else:
                        message += "<br>Asset '%s' is not publish." % charname
                else:
                    pass

            if charfile:
                for num, ch in enumerate(charfile):
                    if charfile[ch]['version'] != charfile[ch]['last_version']:
                        message += str(
                            num + 1) + ". '%s' current version is '%s', but the lasted version is '%s' <br>" % (
                                       ch, charfile[ch]['version'], charfile[ch]['last_version'])
                    else:
                        message += str(num + 1) + ". '%s' current version is the latest version '%s' <br>" % (
                            ch, charfile[ch]['version'])
                rigNotes = message.replace('<br>', '\n')
            else:
                rigNotes = ""
            message = "<br>Audio file is {}.".format(audio) + message

            start_f = int(cmds.playbackOptions(q=1, ast=1))
            end_f = int(cmds.playbackOptions(q=1, aet=1))

            t_tw = cgtw.tw()
            data_task = engine.getTaskFromEnv()
            data_base = dbif.CGT().getDataBase()
            t_shot = t_tw.info_module(data_base, "shot")
            t_shot.init_with_id([data_task['shot_id']])

            start_f1 = t_shot.get(['shot.first_frame'])[0]['shot.first_frame']
            end_f1 = t_shot.get(['shot.last_frame'])[0]['shot.last_frame']
            message += "<br>Frame range: Before(%s to %s).  After(%s to %s)" % (
                str(start_f1), str(end_f1), str(start_f), str(end_f))

            return message, rigNotes

        else:
            return '', ''

    def model_note(self):
        add = ["modelVersion", "rigVersion"]
        message = ''
        for i in add:
            try:
                if i in cmds.listAttr("m_all_CTL"):
                    rigv = cmds.getAttr('m_all_CTL.%s' % (i))
                    message += "<br> '%s' is %s" % (i, rigv)
            except:
                message = ''
        return message

    def setTaskApprovePath(self, path, data_base, model, taskId):
        tw2 = cgtw2.tw()

        fileName = os.path.basename(os.path.splitext(path)[0])
        folder = os.path.dirname(path)
        dic = {'task.submit_file': fileName,
               'task.submit_file_path': {'path': [folder], 'file_path': [path]}}

        tw2.task.set(str(data_base), str(model), [taskId], dic)

    def setTaskDescription(self, des, data_base, model, taskId):
        tw2 = cgtw2.tw()

        dic = {'shot.desc_shot': des,
               }
        # print  str(data_base),str(model),[taskId],dic
        tw2.info.set(str(data_base), str(model), [taskId], dic)

    def run(self):
        path = self.parm('input')
        comments = self.parm('description')
        self.rigNotes = ''
        # Connect to CGTeamwork
        if engine.getTaskFromEnv()['step'] == 'Rig':
            extra = self.model_note()
            kwargs = {
                'project': self.project(),
                'type': self.task().get('type'),
                'taskId': self.task().get('task_id'),
                'files': path,
                'description': comments + extra,
                'state': 'Published'
            }
        else:
            extra = self.get_audio_rig()[0]
            kwargs = {
                'project': self.project(),
                'type': self.task().get('type'),
                'taskId': self.task().get('task_id'),
                'files': path,
                'description': comments + extra,
                'state': 'Published'
            }

        # set task's file_path and file_name, then the ChangePublish command (tw2.task.update_flow)
        # can send note include current file path.
        # print 'kwargs', kwargs
        self.database().submit(**kwargs)

        # asset step ,display approve .mb
        data_base = dbif.CGT().getDataBase()
        typ = self.task().get('type')
        model = typ
        taskId = self.task().get('task_id')
        shotId = self.task().get('shot_id')
        if typ == 'asset':
            if path.endswith('.mb'):
                self.setTaskApprovePath(path, data_base, model, taskId)
        else:
            # set rig version notes,write to CGT description
            # if self.rigNotes:
            try:
                motion_frame = cmds.getAttr("defaultArnoldRenderOptions.motion_frames")
                notes = "MotionBlur(%s)" % (str(round(motion_frame, 3)))
            except:
                notes = ""
            # notes += self.rigNotes
            notes += self.get_audio_rig()[1]
            self.setTaskDescription(notes, data_base, model, shotId)


class GetUserTasks(Action):
    _defaultParms = {
        'user': '{artist}',
    }

    def run(self):
        user = self.parm('user')
        return self.database().getUserTasks(user)


class Print(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        i = self.parm('input')

        if type(i) in (tuple, list, dict):
            pprint.pprint(i)

        else:
            print i


class SaveToFile(Action):
    _defaultParms = {
        'input': '',
        'output': '',
    }

    def run(self):
        i = self.parm('input')
        t = pprint.pformat(i)
        path = self.parm('output')
        f = open(path, 'w')
        f.write(t)
        f.close()


# 给绑定资产的“m_all_CTL”上添加信息
class SetRigNotes(Action):

    def run(self):
        import maya.cmds as cmds
        import datetime
        try:
            cmds.deleteAttr("m_all_CTL.RigDate")
            cmds.deleteAttr("m_all_CTL.AssetName")
            cmds.deleteAttr("m_all_CTL.RigVersion")
        except:
            pass

        now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = cmds.file(query=True, location=True)
        asset_name = 'longgong' + '.' + file_name.split("/")[3] + "." + file_name.split('/')[4]

        try:
            if file_name.split("/")[5] == "rig":
                add = ["rigDate", "assetName", "rigVersion"]
                for i in add:
                    if i not in cmds.listAttr("m_all_CTL"):
                        cmds.addAttr('m_all_CTL', ln=i, dt="string")
                name_list = file_name.split('.')[0].split('_')
                version = name_list[-2]
                cmds.setAttr("m_all_CTL.assetName", l=False)
                cmds.setAttr("m_all_CTL.rigDate", l=False)
                cmds.setAttr("m_all_CTL.rigVersion", l=False)
                cmds.setAttr("m_all_CTL.assetName", asset_name, type="string")
                cmds.setAttr("m_all_CTL.rigDate", now_time, type="string")
                cmds.setAttr("m_all_CTL.rigVersion", version, type="string")
                cmds.setAttr("m_all_CTL.assetName", l=True)
                cmds.setAttr("m_all_CTL.rigDate", l=True)
                cmds.setAttr("m_all_CTL.rigVersion", l=True)
            else:
                pass
        except:
            print "no creat attr or "


# 给模型资产的“model_GRP”上添加信息
class SetModelNotes(Action):

    def run(self):
        try:
            import maya.cmds as cmds

            import datetime
            import os
            file_name = os.path.basename(cmds.file(query=1, location=1))
            if "model" in file_name:
                try:
                    cmds.deleteAttr("model_GRP.ModelVersion")
                except:
                    print "pass"
                try:
                    add = ["modelDate", "assetName", "modelVersion"]
                    for i in add:
                        if i not in cmds.listAttr("model_GRP"):
                            cmds.addAttr('model_GRP', ln=i, dt="string")
                except:
                    pass

                data = engine.getTaskFromEnv()
                now_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                file_name = cmds.file(query=True, location=True)
                asset_name = 'longgong' + '.' + file_name.split("/")[3] + "." + file_name.split('/')[4]

                name_list = file_name.split('.')[0].split('_')
                version = name_list[-2]
                cmds.setAttr("model_GRP.assetName", l=False)
                cmds.setAttr("model_GRP.modelDate", l=False)
                cmds.setAttr("model_GRP.modelVersion", l=False)
                cmds.setAttr("model_GRP.assetName", asset_name, type="string")
                cmds.setAttr("model_GRP.modelDate", now_time, type="string")
                cmds.setAttr("model_GRP.modelVersion", version, type="string")
                cmds.setAttr("model_GRP.assetName", l=True)
                cmds.setAttr("model_GRP.modelDate", l=True)
                cmds.setAttr("model_GRP.modelVersion", l=True)
        except:
            pass


class SendMessage(Action):
    _defaultParms = {
        'file_path': '',
        'description': '{description}'
    }

    def run(self):
        t_tw = cgtw.tw()
        file_path = self.parm('file_path')
        comments = self.parm('description')
        data_task = engine.getTaskFromEnv()
        data_base = dbif.CGT().getDataBase()
        if data_base:
            model = data_task['type']
            if model:
                t_task_module = t_tw.task_module(str(data_base), str(model), [data_task['task_id']])
                pipeline_id = t_task_module.get(['task.set_pipeline_id'])[0]['task.set_pipeline_id']

                t_filebox = t_tw.filebox(data_base)
                file_box_list = t_filebox.get_with_pipeline_id(pipeline_id, model)

                for dict_id in file_box_list:
                    if data_task['step'] == 'Animation':
                        if dict_id['title'] == 'approved-movies':
                            try:
                                file_box_dict = t_task_module.get_filebox_with_filebox_id(dict_id['id'])
                                account_id_list = file_box_dict['drag_in'][2]['account_id'].split(',')
                                if os.path.isfile(file_path):
                                    message = str(comments) + u"<a href=" + "\'" + str(
                                        file_path) + "\'" + u">点击打开文件位置</a>" + u"approved"
                                else:
                                    message = str(comments) + u"<a href=" + "\'" + str(
                                        file_path) + "\'" + u">点击打开文件夹位置</a>" + u"approved"
                                t_tw.msg.send_messsage(data_base, model, "task", data_task['task_id'],
                                                       account_id_list, "Python",
                                                       message)
                            except:
                                pass
                    else:
                        if 'approved' in dict_id['title']:
                            try:
                                file_box_dict = t_task_module.get_filebox_with_filebox_id(dict_id['id'])
                                account_id_list = file_box_dict['drag_in'][2]['account_id'].split(',')
                                if os.path.isfile(file_path):
                                    message = str(comments) + u"，<a href=" + "\'" + str(
                                        file_path) + "\'" + u">点击打开文件位置</a>" + u"approved"
                                else:
                                    message = str(comments) + u"，<a href=" + "\'" + str(
                                        file_path) + "\'" + u">点击打开文件夹位置</a>" + u"approved"
                                t_tw.msg.send_messsage(data_base, model, "task", data_task['task_id'],
                                                       account_id_list, "Python", message)
                            except:
                                pass

            else:
                t_tw.sys().message_error(u"no get model")
        else:
            t_tw.sys().message_error(u"no get database")


class ChangeStateAni(Action):
    _defaultParms = {
        'file_path': ''
    }

    def run(self):

        t_tw = cgtw.tw()
        data_task = engine.getTaskFromEnv()
        data_base = dbif.CGT().getDataBase()
        if data_base:
            model = data_task['type']
            file_path = self.parm('file_path')
            list_name = file_path.split('_')
            t_task_module = t_tw.task_module(str(data_base), str(model), [data_task['task_id']])
            t_task_module.set({"task.shot_step": list_name[-2]})

        else:
            t_tw.sys().message_error(u"no get database")


# 提交文件时更改状态为"Check"
class CheangeSubmit(Action):
    def run(self):
        t_tw = cgtw.tw()
        data_task = engine.getTaskFromEnv()
        data_base = dbif.CGT().getDataBase()
        if data_base:
            model = data_task['type']
            t_task_module = t_tw.task_module(str(data_base), str(model), [data_task['task_id']])
            t_task_module.set({"task.status": "Check"})
            t_task_module.set({"task.leader_status": "submit"})
            t_task_module.set({"task.sup_review": "Check"})


# publish文件时，如果总监审核是"Approved"状态时， 把所有的任务状态都改为"Published"。如果不是，则不更改状态
# previs 环节提交时，附带修改layout任务状态，copy previs通过文件到layout（wait）
class ChangePublish(Action):
    _defaultParms = {
        'publishLayout': False,
        'approve_path': '',
        'approve_mov': ''
    }

    def run(self):
        tw2 = cgtw2.tw()
        data_task = engine.getTaskFromEnv()
        data_base = dbif.CGT().getDataBase()

        '''
        if data_base:
            model = data_task['type']
            t_task_module = t_tw.task_module(str(data_base), str(model), [data_task['task_id']])
            for i in t_task_module.get(["task.sup_review"]):
                if i["task.sup_review"] == "Approved":	
                    # t_task_module.update_flow("task.status", 'Published')
                    t_task_module.update_flow("task.leader_status", 'Published')
                    t_task_module.update_flow("task.sup_review", 'Published')
                    
                    if self.parm('publishLayout'):
                        self.publishLayout(data_task,a)
                    
                    
            t_tw.sys().logout()
        '''
        if data_base:
            model = data_task['type']
            tw2.task.update_flow(str(data_base), str(model), data_task['task_id'], 'task.leader_status', 'Published')
            # tw2.task.update_flow(str(data_base),str(model), data_task['task_id'], 'task.sup_review', 'Published')

        else:
            # tw2.sys().message_error(u"no get database")
            print "no get database"


class MakeSceneTurntablePlayblast1(Action):
    _defaultParms = {
        'frame_range': [1, 100],
        'resolution': [1998, 1080],
        'format': "qt",
        'output': '',
        'camera_name': '',
        'scale': 100,
        'movie_codec': 'H.264',
        'quality': 100
    }

    def run(self):
        import maya.cmds as cmds

        '''得到所有物体的位置信息'''
        Listx = []
        Listy = []
        Listz = []
        # 列出场景中的物体除了摄像机
        a = cmds.listCameras()
        del_cam = ['front', 'persp', 'side', 'top']
        came = [i for i in a if i not in del_cam]
        if len(a) != 0:
            aa = cmds.ls(tr=True, dag=True, v=True)
            selection = [i for i in aa if i not in came]

        sel_length = len(selection)
        for each in range(0, sel_length, 1):
            sel_pos_tx = cmds.getAttr(selection[each] + ".translateX")
            Listx.append(sel_pos_tx)
            sel_pos_ty = cmds.getAttr(selection[each] + ".translateY")
            Listy.append(sel_pos_ty)
            sel_pos_tz = cmds.getAttr(selection[each] + ".translateZ")
            Listz.append(sel_pos_tz)
        getGeoPose = (Listx, Listy, Listz)

        ''' 得到所有物体位置的平均值'''
        geoPose = getGeoPose
        Listx_length = len(geoPose[0])
        sumx = 0
        for eachx in geoPose[0]:
            sumx += eachx
        average_x = sumx / Listx_length
        Listy_length = len(geoPose[1])
        sumy = 0
        for eachy in geoPose[1]:
            sumy += eachy
        average_y = sumy / Listy_length
        Listz_length = len(geoPose[2])
        sumz = 0
        for eachz in geoPose[2]:
            sumz += eachz
        average_z = sumz / Listz_length
        countPose = (average_x, average_y, average_z)
        camera_na = self.parm('camera_name')
        out_file_name = self.parm('output')
        currentPose = countPose
        Start_Frame = self.parm('frame_range')[0]
        End_Frame = self.parm('frame_range')[1]
        format_name = self.parm('format')
        print 'resolution', self.parm('resolution')
        resolution_value = self.parm("resolution")[0]
        resolution_value1 = self.parm("resolution")[1]
        width_value = int(resolution_value)
        higth_value = int(resolution_value1)

        if camera_na != "":
            new_camera = camera_na
            cmds.lookThru(new_camera)
            cmds.move(currentPose[0], currentPose[1], currentPose[2], new_camera + ".scalePivot",
                      new_camera + ".rotatePivot")
        else:
            camera_name = cmds.camera(p=(currentPose[0] * 2 + 5, currentPose[1] * 2 + 5, currentPose[2] * 2 + 5),
                                      wci=(0, 0, 0))
            new_camera = camera_name[0]
            cmds.lookThru(camera_name[0])
            cmds.viewFit(camera_name[1], all=1)
            cmds.move(currentPose[0], currentPose[1], currentPose[2], new_camera + ".scalePivot",
                      new_camera + ".rotatePivot")

        cmds.playbackOptions(min=int(Start_Frame), max=int(End_Frame))
        cmds.rotate(0, '0', 0, new_camera, pivot=(currentPose[0], currentPose[1], currentPose[2]))
        cmds.setKeyframe(new_camera, at='rotateY', t=int(Start_Frame))
        cmds.rotate(0, '360', 0, new_camera, pivot=(currentPose[0], currentPose[1], currentPose[2]))
        cmds.setKeyframe(new_camera, at='rotateY', t=int(End_Frame))
        cmds.rotate("-17", 0, 0, new_camera, pivot=(currentPose[0], currentPose[1], currentPose[2]), ws=1)
        cmds.playblast(p=60, wh=(width_value, higth_value), v=False, format=format_name, viewer=False,
                       forceOverwrite=True,
                       f=out_file_name, cc=1, percent=self.parm("scale"), compression=self.parm("movie_codec"),
                       quality=self.parm("quality"), st=int(Start_Frame), et=int(End_Frame))
        if camera_na == "":
            cmds.cutKey(cmds.ls(sl=1)[0], time=(1, 11), attribute='rotateY', option="keys")
            cmds.delete(camera_name[0])
            cmds.lookThru('persp')
        else:
            cmds.cutKey(camera_na, time=(1, 11), attribute='rotateY', option="keys")


class GetLayer(Action):
    _defaultParms = {
        'layer_name': '',
        'json_path': ''
    }

    def run(self):
        import pymel.core as pm
        import maya.cmds as cmds
        import json

        list = pm.ls(geometry=1, v=1, shapes=1, type="mesh")
        del_camera = pm.ls(type='camera')
        list1 = [i for i in list if i not in del_camera]
        all_list = []
        new_all_list = []
        for i in list1:
            all_list.append(i.longName())
        for i in all_list:
            if self.parm('layer_name') in i:
                new_all_list.append(i)

        f_name = cmds.file(loc=1, q=1)
        key = os.path.basename(f_name).split(".")[0]
        name_split_list = key.split("_")
        name_split_list.remove(name_split_list[-2])
        file_name = '_'.join(name_split_list)
        json_name = '_'.join(name_split_list[:2])
        json_path = os.path.dirname(f_name) + '/' + json_name + '.json'
        new_key = file_name
        data = {}
        data[new_key] = new_all_list
        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)
        return json_path


class AutoPlay(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        import sys
        sys.path.append("Z:/bin/key_frame")
        try:
            import star_code
            a = []
            a.append(self.parm("input"))

            star_code.impoet_mov(a)
        except:
            pass


class DeleteUnknown(Action):

    def run(self):
        import maya.cmds as cmds
        try:
            for i in cmds.ls(type=["unknown", "unknownDag", "unknownTransform"]):
                cmds.delete(i)
            print "Delete Unknow Nodes !"
        except:
            pass


# 添加水印
class MayaShuiYin_bak(Action):

    def hideLocator(self):
        all_locator = cmds.ls(type="locator")
        for locator in all_locator:
            locator = locator.replace("Shape", "")
            if locator != "spiderhuds_shape":
                try:
                    cmds.setAttr("{}.visibility".format(locator), 0)
                except:
                    print "{}.visibility".format(locator)

    def showLocator(self):
        all_locator = cmds.ls(type="locator")
        for locator in all_locator:
            locator = locator.replace("Shape", "")
            if locator != "spiderhuds_shape":
                cmds.setAttr("{}.visibility".format(locator), 1)

    def reslution(self):
        width = cmds.getAttr('defaultResolution.width')
        height = cmds.getAttr('defaultResolution.height')
        reslu = str(width) + 'x' + str(height)
        return reslu

    def setRenderRes(self, name):
        '''设置相机分辨率 和 相机Gate'''
        # cmds.setAttr('defaultResolution.height', 1240)
        # cmds.setAttr("defaultResolution.deviceAspectRatio", 1.611)
        cmds.setAttr('defaultResolution.height', 948)
        cmds.setAttr("defaultResolution.deviceAspectRatio", 2.106)
        cmds.setAttr(name + ".displayFilmGate", 0)
        cmds.setAttr(name + ".displayResolution", 1)
        cmds.setAttr(name + ".displayGateMask", 1)
        cmds.setAttr(name + ".filmFit", 1)
        cmds.setAttr(name + ".overscan", 1)
        cmds.setAttr(name + ".displayGateMaskOpacity", 1)
        cmds.setAttr(name + ".displayGateMaskColor", 0, 0, 0, type="double3")
        # 开启圆滑显示
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 1)
        # 开启阴影
        cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
        # 开启抗锯齿
        cmds.modelEditor(cmds.getPanel(visiblePanels=1)[0], edit=True, displayAppearance="smoothShaded",
                         displayLights="default")

    def setLabelSize(self, size):
        cmds.setAttr("spiderhuds_shape.borderColor", 0, 0, 0, type="double3")

        cmds.setAttr("spiderhuds_shape.font1Scale", size)
        cmds.setAttr("spiderhuds_shape.font1Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font2Scale", size)
        cmds.setAttr("spiderhuds_shape.font2Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font3Scale", size)
        cmds.setAttr("spiderhuds_shape.font3Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font4Scale", size)
        cmds.setAttr("spiderhuds_shape.font4Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font5Scale", size)
        cmds.setAttr("spiderhuds_shape.font5Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font6Scale", size)
        cmds.setAttr("spiderhuds_shape.font6Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font7Scale", size)
        cmds.setAttr("spiderhuds_shape.font7Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font8Scale", size)
        cmds.setAttr("spiderhuds_shape.font8Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font9Scale", size)
        cmds.setAttr("spiderhuds_shape.font9Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font10Scale", size)
        cmds.setAttr("spiderhuds_shape.font10Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font11Scale", size)
        cmds.setAttr("spiderhuds_shape.font11Color", 1, 0.8342, 0.0188, type="double3")
        cmds.setAttr("spiderhuds_shape.font12Scale", size)
        cmds.setAttr("spiderhuds_shape.font12Color", 1, 0.8342, 0.0188, type="double3")

        cmds.setAttr("spiderhuds_shape.font4hpos", 41)
        cmds.setAttr("spiderhuds_shape.font5hpos", 100)
        cmds.setAttr("spiderhuds_shape.font6hpos", -33)
        cmds.setAttr("spiderhuds_shape.font10hpos", 28)
        cmds.setAttr("spiderhuds_shape.font11hpos", 72)

    def setHudNode(self, PLUG_IN_NAME, TRANSFORM_NODE_NAME, NODE_NAME, SHAPE_NODE_NAME):
        sw = self.software()
        data = engine.getTaskFromEnv()
        filename = os.path.basename(cmds.file(location=1, q=1)).split(".")[0]

        # patn_json = r'D:/name/name.json'
        # if os.path.exists(patn_json):
        # with open(patn_json) as file:
        # name_dict = json.loads(file.read())
        # if name_dict["name"] == "":
        # author = data['artist']
        # else:
        # author = name_dict['name']
        # else:
        # author = data['artist']
        author = data['artist']
        frame_list = sw.frameRange()
        startEndFrame = str(frame_list[0]) + "--" + str(frame_list[1])

        t_tw = cgtw.tw()
        data_base = dbif.CGT().getDataBase()
        if data_base:
            model = data['type']
            t_task_module = t_tw.task_module(str(data_base), str(model), [data['task_id']])
            if t_task_module.get(['shot.priority_shot'])[0]['shot.priority_shot']:
                priority = t_task_module.get(['shot.priority_shot'])[0]['shot.priority_shot']
            else:
                priority = "None"

        camreaName = sw.getActiveCamera().split("|")[-1]

        start_f = cmds.playbackOptions(q=1, ast=1)
        end_f = cmds.playbackOptions(q=1, aet=1)
        ani_time = end_f - start_f + 1

        self.label_text = [filename,
                           time.strftime("%d/%m/%y %H:%M:%S", time.localtime(time.time())),
                           # "reslution: " + "1998x1080",
                           "reslution: " + "1920*818",
                           "FocalLength: " + str(cmds.getAttr(sw.getActiveCamera() + '.focalLength')),
                           'Author: ' + author,
                           'Time Unit: ' + str(sw.fps()),
                           'Start/End: ' + startEndFrame,
                           'Priority: ' + priority,
                           camreaName,
                           'Sequence: ' + '{frame.4}' + "/" + str(int(end_f)),
                           'frame: ' + '{frame.4}',
                           "",
                           ]

        if not cmds.pluginInfo(PLUG_IN_NAME, q=True, loaded=True):
            try:
                cmds.loadPlugin(PLUG_IN_NAME)
            except:
                om.MGlobal.displayError("Failed to load ZShotMask plug-in: {0}".format(PLUG_IN_NAME))
                return
        if cmds.objExists(NODE_NAME) != True:
            transform_node = cmds.createNode("transform", name=TRANSFORM_NODE_NAME)
            cmds.createNode(NODE_NAME, name=SHAPE_NODE_NAME, parent=transform_node)
            cmds.setAttr("{0}.topLeftText1".format(mask), self.label_text[0], type="string")
            cmds.setAttr("{0}.topLeftText2".format(mask), self.label_text[1], type="string")
            cmds.setAttr("{0}.topLeftText3".format(mask), self.label_text[2], type="string")

            cmds.setAttr("{0}.topRightText1".format(mask), self.label_text[3], type="string")
            cmds.setAttr("{0}.topRightText2".format(mask), self.label_text[4], type="string")
            cmds.setAttr("{0}.topRightText3".format(mask), self.label_text[5], type="string")

            cmds.setAttr("{0}.bottomLeftText1".format(mask), self.label_text[6], type="string")
            cmds.setAttr("{0}.bottomLeftText2".format(mask), self.label_text[7], type="string")
            cmds.setAttr("{0}.bottomLeftText3".format(mask), self.label_text[8], type="string")

            cmds.setAttr("{0}.bottomRightText1".format(mask), self.label_text[9], type="string")
            cmds.setAttr("{0}.bottomRightText2".format(mask), self.label_text[10], type="string")
            cmds.setAttr("{0}.bottomRightText3".format(mask), self.label_text[11], type="string")

            cmds.setAttr("{0}.borderColor".format(mask), 0.1, 0.6, 0, type="double3")
            return True

    # delete display HUD of node
    def delHeadsUpDisplay(self, node):
        """
        :param node: nodename
        :return:
        """
        if cmds.objExists(node) == True:
            cmds.delete(node)
        else:
            cmds.inViewMessage(amg='Node no exists!', pos='midCenter', fade=True)

    def setLabelText(self, mask):
        """
        :param mask: nodename
        :param label_text: label content ; list
        :return:
        """
        cmds.setAttr("{0}.topLeftText1".format(mask), self.label_text[0], type="string")
        cmds.setAttr("{0}.topLeftText2".format(mask), self.label_text[1], type="string")
        cmds.setAttr("{0}.topLeftText3".format(mask), self.label_text[2], type="string")

        cmds.setAttr("{0}.topRightText1".format(mask), self.label_text[3], type="string")
        cmds.setAttr("{0}.topRightText2".format(mask), self.label_text[4], type="string")
        cmds.setAttr("{0}.topRightText3".format(mask), self.label_text[5], type="string")

        cmds.setAttr("{0}.bottomLeftText1".format(mask), self.label_text[6], type="string")
        cmds.setAttr("{0}.bottomLeftText2".format(mask), self.label_text[7], type="string")
        cmds.setAttr("{0}.bottomLeftText3".format(mask), self.label_text[8], type="string")

        cmds.setAttr("{0}.bottomRightText1".format(mask), self.label_text[9], type="string")
        cmds.setAttr("{0}.bottomRightText2".format(mask), self.label_text[10], type="string")
        cmds.setAttr("{0}.bottomRightText3".format(mask), self.label_text[11], type="string")

    def run(self):
        cam = self.software().getActiveCamera()

        # close camera shape's panZoomEnabled attr
        cameraShape = cmds.listRelatives(cam)[0]
        cmds.setAttr("%s.panZoomEnabled" % cameraShape, 0)

        # 时间滑块设置到一帧
        cmds.currentTime(cmds.playbackOptions(q=1, ast=1))
        if "spiderhuds" in cmds.ls(assemblies=1):
            cmds.delete("spiderhuds")
            # 加载插件
        cmds.loadPlugin(os.path.dirname(
            os.path.dirname(os.path.dirname((__file__)))) + r"\packages\maya\2016.5\plug-ins\spiderhud\spiderhuds.py")
        # 设置分辨率和相机Gate
        # print self.software().getActiveCamera()
        self.setRenderRes(cam)
        # 加水印
        self.setHudNode(PLUG_IN_NAME, TRANSFORM_NODE_NAME, NODE_NAME, SHAPE_NODE_NAME)
        # 微调水印位置,大小
        self.setLabelText(mask)
        self.setLabelSize(20)
        # 回到第一帧
        cmds.currentTime(cmds.playbackOptions(q=1, ast=1))
        # 显示locater
        cmds.modelEditor(cmds.getPanel(visiblePanels=1)[0], e=True, allObjects=False)
        cmds.modelEditor(cmds.getPanel(visiblePanels=1)[0], e=True, locators=True, polymeshes=True, nurbsSurfaces=True,
                         strokes=True)
        self.hideLocator()
        # 显示spiderhuds Locater
        cmds.setAttr("spiderhuds_shape.visibility", 1)
        cmds.refresh(force=True)

        # maya.mel.eval('modelEditor -e -locators false modelPanel1')


# 删除水印恢复相机分辨率
class DelShuiYin_bak(Action):

    def run(self):
        camera = "cam" + "_" + engine.getTaskFromEnv()["sequence"][-3:] + "_" + engine.getTaskFromEnv()["shot"][-3:]
        '''恢复相机分辨率 和 相机Gate'''
        # cmds.setAttr('defaultResolution.height', 1080)
        # cmds.setAttr("defaultResolution.deviceAspectRatio", 1.850)
        cmds.setAttr('defaultResolution.height', 818)
        cmds.setAttr("defaultResolution.deviceAspectRatio", 2.35)
        cmds.setAttr(self.software().getActiveCamera() + ".filmFit", 0)
        cmds.setAttr(self.software().getActiveCamera() + ".overscan", 1.1)
        cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", 0)
        cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 0)

        # 删除水印节点
        cmds.delete("spiderhuds")


class FakePlayBlast_bak(Action):
    _defaultParms = {
        'output': '',
        'displayLights': True,
        'displayTextures': True,
    }

    def killProcess(self, processName=''):
        '''
        processName: quicktimeShim.exe
        '''
        cmd = 'taskkill /F /IM "%s"' % processName
        os.popen(cmd)

    def run(self):
        # Kill "quicktimeShim" before playblast
        self.killProcess(processName='quicktimeShim.exe')

        try:
            audio = cmds.ls(type="audio")[0]
        except:
            audio = "None"
        key = {'format': 'qt', 'viewer': 1, 'quality': 100, 'compression': 'H.264',
               'sound': audio, 'clearCache': 1, 'framePadding': 0, 'showOrnaments': 1,
               'sequenceTime': 0, 'percent': 100, 'filename': self.parm("output"),
               'forceOverwrite': True, 'widthHeight': [1920, 1080]}

        cam_name = "cam" + '_' + filter(str.isdigit, str(engine.getTaskFromEnv()["sequence"])) + '_' + filter(
            str.isdigit,
            str(
                engine.getTaskFromEnv()[
                    "shot"]))

        if "previs" not in cmds.file(location=1, q=1):
            cmds.lookThru(cam_name)
        else:
            cmds.lookThru(cam_name)

        cmds.currentTime(cmds.playbackOptions(q=1, ast=1) - 1)
        cmds.refresh(force=True)
        cmds.currentTime(cmds.playbackOptions(q=1, ast=1))

        # displayLights = self.parm('displayLights')

        # if displayLights:
        #    allLight = cmds.ls(lights=True,type=['aiAreaLight','aiSkyDomeLight','aiMeshLight','aiPhotometricLight','aiLightPortal','aiPhysicalSky'],dag=True)
        #    if allLight:
        #        cmds.modelEditor('modelPanel4',edit=True,displayLights="all")

        # displayTextures = self.parm('displayTextures')

        # if displayTextures:
        #    cmds.modelEditor('modelPanel4',edit=True,displayTextures=True)

        # print "play cmd:",key
        cmds.playblast(**key)
        # cmds.ogs( reset=True )

        return self.parm("output")


class PlayBlastFunc2(Action):
    _defaultParms = {
        'movPath': '',
    }

    def shotCamera(self):
        for cam in swif.software().getCameras(includeHidden=True):
            if re.search(r'\d{2}', self.task().get('shot')).group() in cam:
                return cam

        return cmds.lookThru(q=True)

    def run(self):
        import playBlast2
        reload(playBlast2)

        path = self.parm('movPath')

        # hidden "nurbscurve","joints"
        md = cmds.getPanel(visiblePanels=1)[0]
        cmds.modelEditor(md, e=True, nurbsCurves=False, joints=False)

        # play blast with banner
        playBlast2.run(path, self.shotCamera())
        return path


# class MayaShuiYin(Action):
#     _defaultParms = {
#         'input': '',
#     }
#
#     def run(self):
#         sys.path.append("Z:/bin/pltk/packages/maya/2016.5/scripts")
#         import playBlast
#         reload(playBlast)
#         en = plcr.Engine()
#
#         MS = playBlast.MayaShuiYin(en)
#         f = self.parm("input")
#
#         if not f.endswith('.mov'):
#             f = f + '.mov'
#         MS.run(filename=f)
#
#
# class FakePlayBlast(Action):
#     _defaultParms = {
#         'output': '',
#     }
#
#     def run(self):
#         sys.path.append("Z:/bin/pltk/packages/maya/2016.5/scripts")
#         import playBlast
#         reload(playBlast)
#         en = plcr.Engine()
#
#         FP = playBlast.FakePlayBlast(en)
#         fn = self.parm("output")
#         if not fn.endswith('.mov'):
#             fn += '.mov'
#         FP.run(fn)
#
#
# class DelShuiYin(Action):
#     def run(self):
#         sys.path.append("Z:/bin/pltk/packages/maya/2016.5/scripts")
#         import playBlast
#         reload(playBlast)
#         en = plcr.Engine()
#
#         DY = playBlast.DelShuiYin(en)
#         DY.run()


class ImagePlayBlast(Action):
    _defaultParms = {
        'output': '',
    }

    def run(self):
        try:
            audio = cmds.ls(type="audio")[0]
        except:
            audio = "None"

        cam_name = "cam" + '_' + filter(str.isdigit, str(engine.getTaskFromEnv()["sequence"])) + '_' + filter(
            str.isdigit,
            str(
                engine.getTaskFromEnv()[
                    "shot"]))
        if "previs" not in cmds.file(location=1, q=1):
            cmds.lookThru(cam_name)
        else:
            cmds.lookThru(cam_name)

        cmds.playblast(format='image', viewer=0, quality=100, compression='jpg',
                       clearCache=1, showOrnaments=1, fp=4, sequenceTime=0, percent=100,
                       filename=self.parm("output"), forceOverwrite=True, widthHeight=[1920, 1080])

        cmds.ogs(reset=True)

        return self.parm("output")


class changeFrame(Action):

    def run(self):
        if "animation" in cmds.file(location=1, q=1):
            t_tw = cgtw.tw()
            data_task = engine.getTaskFromEnv()
            data_base = dbif.CGT().getDataBase()
            t_shot = t_tw.info_module(data_base, "shot")
            t_shot.init_with_id([data_task['shot_id']])

            start_f = cmds.playbackOptions(q=1, ast=1)
            end_f = cmds.playbackOptions(q=1, aet=1)
            ani_time = end_f - start_f + 1

            print t_shot.set({'shot.frame': ani_time})
            print t_shot.set({'shot.first_frame': start_f})
            print t_shot.set({'shot.last_frame': end_f})
        else:
            pass


# 上传当前文件
class UploadFiles(Action):

    def run(self):
        t_tw = cgtw.tw()
        data_task = engine.getTaskFromEnv()
        data_base = dbif.CGT().getDataBase()

        t_module = data_task["type"]  # 模块
        t_module_type = "task"  # 模块类型
        t_db = data_base  # 数据库
        t_local_path = cmds.file(location=1, q=1)  # 要上传文件.mb路径

        # sorceimage文件
        image_path = os.path.dirname(cmds.file(location=1, q=1)) + "/" + "sourceimages"
        image_ls = []
        if os.path.exists(image_path):
            for i in os.listdir(image_path):
                if os.path.splitext(i)[-1] == ".jpg":
                    image_ls.append(image_path + "/" + i)

        # 获取文件框数据
        filename = os.path.basename(t_local_path)
        task_id_list = data_task["task_id"]
        print task_id_list

        try:
            result = []

            # 上传.mb文件
            t_path = os.path.dirname(t_local_path)
            t_upload_list = [{"sou": t_local_path,
                              "des": unicode(os.path.splitdrive(t_path)[1] + "/" + filename).replace("\\", "/")}]

            t_dic = {'name': filename, 'task': [{"action": "upload",
                                                 "is_contine": True,
                                                 "data_list": t_upload_list,
                                                 "db": t_db,
                                                 "module": t_module,
                                                 "module_type": t_module_type,
                                                 "task_id": task_id_list[0],
                                                 "version_id": ""}
                                                ]}
            a = t_tw.local_con._send("queue_widget", "add_task", {"task_data": t_dic}, "send")
            result.append(a)

            # 上传mov文件
            movie_path = os.path.dirname(os.path.dirname(t_local_path)) + "/movies/" + filename.split(".")[0] + ".mov"
            if os.path.exists(movie_path):  # 存在视频的话就上传
                t_path = os.path.dirname(self.parm("movie_path"))
                t_upload_list = [{"sou": self.parm("movie_path"),
                                  "des": unicode(os.path.splitdrive(t_path)[1] + "/" + filename).replace("\\", "/")}]
                # 通过客户端进行上传到在线文件
                t_dic = {'name': filename, 'task': [{"action": "upload",
                                                     "is_contine": True,
                                                     "data_list": t_upload_list,
                                                     "db": t_db,
                                                     "module": t_module,
                                                     "module_type": t_module_type,
                                                     "task_id": task_id_list[0],
                                                     "version_id": ""}
                                                    ]}
                a = t_tw.local_con._send("queue_widget", "add_task", {"task_data": t_dic}, "send")
                result.append(a)

            # 上传sorceimage文件
            if len(image_ls) > 0:
                for image in image_ls:
                    filename = os.path.basename(image)
                    t_path = os.path.dirname(image)
                    t_upload_list = [{"sou": image,
                                      "des": unicode(os.path.splitdrive(t_path)[1] + "/" + filename).replace("\\",
                                                                                                             "/")}]
                    # 通过客户端进行上传到在线文件
                    t_dic = {'name': filename, 'task': [{"action": "upload",
                                                         "is_contine": True,
                                                         "data_list": t_upload_list,
                                                         "db": t_db,
                                                         "module": t_module,
                                                         "module_type": t_module_type,
                                                         "task_id": task_id_list[0],
                                                         "version_id": ""}
                                                        ]}
                    a = t_tw.local_con._send("queue_widget", "add_task", {"task_data": t_dic}, "send")
                    result.append(a)

            if "False" not in result:
                print "Upload Successfully !"

        except Exception, e:
            print e.message


# 上传指定的文件
class UploadFiles1(Action):
    _defaultParms = {
        'hist_abc_path': '',
        'appr_abc_path': '',
        'hist_path': '',
        'appr_path': '',
        'hist_movie': '',
        'movie_path': '',
        'camera_history': '',
        'camera_approve': '',
        'camera_abc_his': '',
        'camera_abc_app': '',
        'sequence': ''
    }

    def run(self):
        upload_ls = []

        hist_path = self.parm("hist_path")
        if hist_path:
            upload_ls.append(hist_path)

        appr_path = self.parm("appr_path")
        if appr_path:
            upload_ls.append(appr_path)

        hist_abc_path = self.parm("hist_abc_path")
        if hist_abc_path:
            upload_ls.append(hist_abc_path)

        appr_abc_path = self.parm("appr_abc_path")
        if appr_abc_path:
            upload_ls.append(appr_abc_path)

        hist_movie = self.parm("hist_movie")
        if hist_movie:
            upload_ls.append(hist_movie)

        movie_path = self.parm("movie_path")
        if movie_path:
            upload_ls.append(movie_path)

        camera_history = self.parm("camera_history")
        if camera_history:
            upload_ls.append(camera_history)

        camera_approve = self.parm("camera_approve")
        if camera_approve:
            upload_ls.append(camera_approve)

        camera_abc_his = self.parm("camera_abc_his")
        if camera_abc_his:
            upload_ls.append(camera_abc_his)

        camera_abc_app = self.parm("camera_abc_app")
        if camera_abc_app:
            upload_ls.append(camera_abc_app)

        t_tw = cgtw.tw()
        data_task = engine.getTaskFromEnv()
        if self.parm("sequence") != "":
            if not data_task["sequence"] in self.parm("sequence"):
                return None
        else:
            pass
        data_base = dbif.CGT().getDataBase()

        t_module = data_task["type"]  # 模块
        t_module_type = "task"  # 模块类型
        t_db = data_base  # 数据库
        pprint.pprint(upload_ls)

        try:
            for file in upload_ls:

                t_local_path = file  # 要上传文件.mb路径

                # 获取文件框数据
                filename = os.path.basename(t_local_path)
                task_id_list = data_task["task_id"]

                result = []
                # 上传.mb文件
                if os.path.exists(file):
                    t_path = os.path.dirname(t_local_path)
                    t_upload_list = [{"sou": t_local_path,
                                      "des": unicode(os.path.splitdrive(t_path)[1] + "/" + filename).replace("\\",
                                                                                                             "/")}]

                    t_dic = {'name': filename, 'task': [{"action": "upload",
                                                         "is_contine": True,
                                                         "data_list": t_upload_list,
                                                         "db": t_db,
                                                         "module": t_module,
                                                         "module_type": t_module_type,
                                                         "task_id": task_id_list[0],
                                                         "version_id": ""}
                                                        ]}

                    a = t_tw.local_con._send("queue_widget", "add_task", {"task_data": t_dic}, "send")
                    # print "t_dic:",t_dic
                    result.append(a)

                # 上传sorceimage文件
                image_path = os.path.dirname(file) + "/" + "sourceimages"
                image_ls = []
                if os.path.exists(image_path):
                    for i in os.listdir(image_path):
                        if os.path.splitext(i)[-1] == ".jpg":
                            image_ls.append(image_path + "/" + i)

                if len(image_ls) > 0:
                    for image in image_ls:
                        filename = os.path.basename(image)
                        t_path = os.path.dirname(image)
                        t_upload_list = [{"sou": image,
                                          "des": unicode(os.path.splitdrive(t_path)[1] + "/" + filename).replace("\\",
                                                                                                                 "/")}]
                        # 通过客户端进行上传到在线文件
                        t_dic = {'name': filename, 'task': [{"action": "upload",
                                                             "is_contine": True,
                                                             "data_list": t_upload_list,
                                                             "db": t_db,
                                                             "module": t_module,
                                                             "module_type": t_module_type,
                                                             "task_id": task_id_list[0],
                                                             "version_id": ""}
                                                            ]}
                        a = t_tw.local_con._send("queue_widget", "add_task", {"task_data": t_dic}, "send")
                        result.append(a)

        except Exception, e:
            print '-------- upload field! --------------'
            print e.message


# 导出RoughRender的ABC
class ExportRRAbc(Action):
    _defaultParms = {
        'input': '',
    }

    def getAni(self):
        con = cmds.ls(rf=1)
        int_pos = {}
        fin_pos = {}
        start_f = cmds.playbackOptions(q=1, ast=1)
        cmds.currentTime(start_f)
        for i in con:
            try:
                ref_node = cmds.referenceQuery(i, nodes=True)
                if ref_node != None and "SG" not in ref_node[0]:
                    # print i, ":", ref_node
                    int_pos[ref_node[0]] = cmds.objectCenter(ref_node[0], gl=1)
            except:
                pass
        end_f = cmds.playbackOptions(q=1, aet=1)
        cmds.currentTime(end_f)
        for i in con:
            try:
                ref_node = cmds.referenceQuery(i, nodes=True)
                if ref_node != None and "SG" not in ref_node[0]:
                    fin_pos[ref_node[0]] = cmds.objectCenter(ref_node[0], gl=1)
            except:
                pass
        dic = {}
        for k in int_pos:
            for j in fin_pos:
                if k == j and int_pos[k] != fin_pos[j]:
                    dic[k] = int_pos[k]
        getObj = []
        for key in dic:
            getObj.append(key)

        cameraLis = self.cameraList()
        for c in cameraLis:
            if c not in getObj:
                getObj.append(c)

            # remove repeat grp
            grp = c.split('|')[1]
            if grp in getObj:
                getObj.remove(grp)

        print "getObj:", getObj
        return getObj

    def cameraList(self):
        allCamera = cmds.ls(cameras=True, long=True)
        defaultCamera = ['|persp', '|front', '|side', '|top', '|back', '|left', '|right', '|bottom']
        cameraList = []
        for i in allCamera:
            cameraName = cmds.listRelatives(i, allParents=True, fullPath=True)[0]
            if cameraName not in defaultCamera:
                cameraList.append(cameraName)
        return cameraList

    def versionUp(self, path):
        dir = os.path.dirname(path)
        basename = os.path.basename(path).split(".")[0]
        all = []
        for i in os.listdir(dir):
            if ".abc" in i:
                if basename.split("_")[3] in i:
                    all.append(i)
        newname = os.path.basename(cmds.file(q=1, sceneName=1)).split(".")[0].split("_")
        newname.pop()
        new_name = "_".join(set(newname))
        return new_name + "_" + str(len(all) + 1).zfill(3) + ".abc"

    def run(self):
        # print "self.parm('input'):",self.parm("input")
        if self.parm("input") == "Yes":
            start_f = cmds.playbackOptions(q=1, ast=1)
            end_f = cmds.playbackOptions(q=1, aet=1)
            args = '-frameRange %s %s ' % (start_f - 1, end_f)
            args = args + ' -ro -uvWrite -writeColorSets -worldSpace -writeVisibility -writeUVSets -eulerFilter -dataFormat ogawa '
            for i in self.getAni():
                args += '-root %s ' % i

            data_task = engine.getTaskFromEnv()

            folder_name = os.path.basename(cmds.file(q=1, sceneName=1)).split(".")[0]

            # fileName = os.path.basename(cmds.file(q=1,sceneName=1)).split(".")[0]+".abc"
            fileName = "%s_%s_SF.abc" % (data_task['sequence'], data_task['shot'])

            target_path = 'Z:/LongGong/sequences/{seq}/{shot}/Cache/shotFinaling/work'.format(seq=data_task['sequence'],
                                                                                              shot=data_task['shot'])
            target_file = 'Z:/LongGong/sequences/{seq}/{shot}/Cache/shotFinaling/work/{fileName}'.format(
                seq=data_task['sequence'],
                shot=data_task['shot'],
                fileName=fileName)

            if os.path.exists(target_path):
                pass
            else:
                os.makedirs(target_path)
            # name = self.versionUp(target_file)
            # path = os.path.dirname(target_file)+"/"+name
            path = target_file
            args += '-file %s' % (path)
            plugin_list = cmds.pluginInfo(query=True, listPlugins=True)
            if 'mtoa' in plugin_list:
                args += ' -attr aiSubdivType -attr aiSubdivIterations'
            if 'AbcExport' not in plugin_list:
                cmds.loadPlugin("AbcExport")
            cmd = 'AbcExport -j "%s";' % args
            print "ExportRRAbc Cmd:", cmd
            try:
                pm.mel.eval(cmd)
                # cmds.inViewMessage(amg=u'Export ABC successful !', pos='midCenter', fts=20, bkc=0x00FF1010, fade=True)
            except:
                pass
                # cmds.inViewMessage(amg=u"Please check camera's name, may be there are the same camera", pos='midCenter', fts=30, bkc=0x00FF1010, fade=True)

            return path

        else:
            pass


class TransferUV(Action):
    _defaultParms = {
        'uv_path': ''
    }

    def targetPath(self, foldername):
        path = r"Z:\LongGong\users\srf_wrong"
        target = os.path.join(path, time.strftime("%y_%m_%d", time.localtime(time.time())), foldername)
        return target

    def run(self):
        import sys
        import os
        sys.path.append(r'Z:\bin\pltk\packages\maya\2016.5\scripts\transf\_maya')
        import testB
        reload(testB)

        if self.task().get('sequence') == 'set':
            return

        uvPath = self.parm('uv_path')
        rig_folder = os.path.dirname(uvPath).replace("surface", "rig")
        rig_name = os.path.basename(uvPath)
        rig_name = rig_name.replace("highTex", "high")
        rig_name = rig_name.replace("highUV", "high")
        rig_name = rig_name.replace("abc", "mb")
        rig_name = rig_name.replace('_tex_', '_rig_')

        maPath = os.path.join(rig_folder, rig_name)

        folder_name = self.targetPath(os.path.basename(os.path.splitext(uvPath)[0]))

        logPath = '%s/%s_uvLog.txt' % (folder_name, os.path.basename(os.path.splitext(maPath)[0]))
        openLog = True
        mayabatchPath = "%s/bin/mayabatch.exe" % (os.environ['MAYA_LOCATION'])
        melPath = r'Z:\bin\pltk\packages\maya\2016.5\scripts\transf\melPath\transmit.mel'
        block = False

        if os.path.exists(maPath):
            cmd = testB.transmitFileUVBackStage(maPath, uvPath,
                                                logPath=logPath,
                                                openLog=openLog,
                                                mayabatchPath=mayabatchPath,
                                                melPath=melPath,
                                                block=block)

            print cmd
        else:
            Tip("%s\nPlease check if rig is published." % maPath)


class BreakHiddenObjectConnect(Action):
    def run(self):
        import maya.cmds as cmds
        allTransform = cmds.ls(type='transform')

        connectInfo = {}

        for t in allTransform:
            visAttr = "%s.visibility" % t
            if cmds.getAttr(visAttr) == 0:
                connectNode = cmds.listConnections(visAttr)
                if connectNode:
                    type = cmds.nodeType(connectNode)
                    if type and not type.startswith('animCurveT'):
                        linkAttr = cmds.connectionInfo(visAttr, sfd=True)
                        locked = cmds.getAttr(visAttr, lock=True)

                        if not locked and connectNode[0] != 'defaultRenderLayer':
                            try:
                                connectInfo[visAttr] = linkAttr
                                cmds.disconnectAttr(linkAttr, visAttr)
                            except:
                                pass

        return connectInfo


class LinkHiddenObjectConnect(Action):
    _defaultParms = {'connectInfo': {}}

    def run(self):
        import maya.cmds as cmds
        connectInfo = self.parm('connectInfo')

        for source, des in connectInfo.iteritems():
            try:
                cmds.connectAttr(des, source)
            except:
                pass


class DisplayTexture(Action):
    def run(self):
        import maya.cmds as cmds
        cmds.modelEditor('modelPanel4', edit=True, displayTextures=True)


class FindMaxVersionWorkFileBasename(Action):
    def run(self):
        root = 'Z:/LongGong/sequences'
        # print 'root:',root
        workPath = '{root}/{seq}/{shot}/{step}/work/scenes'

        task = engine.getTaskFromEnv()
        seq = task['sequence']
        shot = task['shot']
        step = task['step']

        info = {
            'root': root,
            'seq': seq,
            'shot': shot,
            'step': step,
        }

        filename = ''

        if step == 'Previs':
            workPath = workPath.format(**info)
            filename = "{seq}_{shot}_Previs_v???.mb".format(**info)

        elif step == 'Layout':
            workPath = workPath.format(**info)
            filename = "{seq}_{shot}_Layout_v???.mb".format(**info)

        elif step == 'Animation':
            workPath = workPath.format(**info)
            filename = "{seq}_{shot}_Ani_BLO_v???.mb".format(**info)

            stepList = ['POL', 'SPL', 'BLO']
            for s in stepList:
                info['ani_step'] = s
                filename = "{seq}_{shot}_Ani_{ani_step}_v???.mb".format(**info)

                filePath = "%s/%s" % (workPath, filename)
                allFile = glob.glob(filePath)
                if allFile:
                    break
        elif step == 'shotFinaling':
            workPath = workPath.format(**info)
            filename = "{seq}_{shot}_SF_v???.mb".format(**info)

        elif step == 'Assembling':
            workPath = workPath.format(**info)
            filename = "{seq}_{shot}_Assembling_v???.mb".format(**info)

        elif step == 'BG_Characters':
            workPath = workPath.format(**info)
            filename = "{seq}_{shot}_BG_BLO_v???.mb".format(**info)

            stepList = ['POL', 'SPL', 'BLO']
            for s in stepList:
                info['ani_step'] = s
                filename = "{seq}_{shot}_BG_{ani_step}_v???.mb".format(**info)

                filePath = "%s/%s" % (workPath, filename)
                allFile = glob.glob(filePath)
                if allFile:
                    break

        filePath = "%s/%s" % (workPath, filename)
        allFile = glob.glob(filePath)
        if allFile:

            maxFile = max(allFile)
        else:
            maxFile = filePath.replace('v???', 'v001')

        basename = os.path.basename(os.path.splitext(maxFile)[0])
        return basename


class SetCGTPublishedFileInfo(Action):
    defaultParms = {
        "path": '',
    }

    def setTaskApprovePath(self, path, data_base, model, taskId):
        tw2 = cgtw2.tw()

        fileName = os.path.basename(path)
        folder = os.path.dirname(path)
        dic = {'task.submit_file': fileName,
               'task.submit_file_path': {'path': [folder], 'file_path': [path]}}
        tw2.task.set(str(data_base), str(model), [taskId], dic)

    def run(self):
        path = self.parm('path')

        if os.path.isfile(path):

            data_base = dbif.CGT().getDataBase()
            taskId = self.task().get('task_id')
            typ = self.task().get('type')

            self.setTaskApprovePath(path, data_base, typ, taskId)
        else:
            print "----------SetCGTPublishedFileInfo----------"
            print "path:", path


class TextureExportArchive(Action):

    def run(self):
        file = self.parm('path')
        exportArchive = self.parm('exportArchive')

        if not exportArchive:
            return

        # switch to arnold render
        cmds.setAttr("defaultRenderGlobals.currentRenderer", 'arnold', type="string")

        # open motion blur
        cmds.setAttr("defaultArnoldRenderOptions.motion_blur_enable", 1)
        cmds.file(save=True, force=True)
        #
        folder = os.path.dirname(os.path.dirname(os.path.dirname(file)))
        basename = os.path.basename(file)
        assetName = basename.split('_tex_')[0]
        path = "%s/archive/%s/" % (folder, assetName)
        currentFile = cmds.file(query=True, location=True)
        groupName = cmds.ls("|*_GRP", long=True)[0]
        currentFrame = cmds.currentTime(q=True)
        # create archive folder
        if not os.path.exists(path):
            os.makedirs(path)

        # export archive
        oldH = cmds.ls(assemblies=True)
        import xgenm
        hlp = xgenm.xmaya.xgmArchiveExport.xgmArchiveExport()
        # next command will open maya backstage , set render Setting need to save file,then run command.
        hlp.processDir(assetName, path, [currentFile], [groupName], 0, '0.0', '0.0', currentFrame, currentFrame)
        newH = cmds.ls(assemblies=True)
        otherH = list(set(newH) - set(oldH))
        cmds.delete(otherH)

        # copy local file to archive floder
        newFile = "%s/%s.mb" % (path, assetName)
        shutil.copy2(currentFile, newFile)

        # save thumbnail
        imageSnapshot = "%s/%s.png" % (path, assetName)
        imageSnapshot2 = "%s/%s_copy.png" % (path, assetName)
        cmds.refresh(cv=True, fe="png", fn=imageSnapshot2)

        # replace "thumb.png" to ".../thumb.png"
        xarcFile = imageSnapshot.replace('.png', '.xarc')
        imageSnapshot = imageSnapshot.replace('\\', '/')
        imageSnapshot = imageSnapshot.replace('//', '/')

        if os.path.exists(xarcFile):
            with open(xarcFile, 'r') as f:
                read = f.read()

            text = read.replace('"%s"' % (os.path.basename(imageSnapshot)), '"%s"' % (imageSnapshot2))
            with open(xarcFile, 'w') as f:
                f.write(text)
        print '"%s"' % (imageSnapshot2)
        # print '--------------------------------------------------------------------'
        # print "switch to arnold render"
        # print cmds.getAttr("defaultRenderGlobals.currentRenderer")
        # print "motion_blur_enable"
        # print cmds.getAttr("defaultArnoldRenderOptions.motion_blur_enable")
        # print '---------------------------------------------------------------------'


# ------------------------- shot type ------------------------------------
showType = ["nurbsCurves",
            "nurbsSurfaces",
            "cv",
            "hulls",
            "polymeshes",
            "subdivSurfaces",
            "planes",
            "lights",
            "cameras",
            "imagePlane",
            "joints",
            "ikHandles",
            "deformers",
            "dynamics",
            "particleInstancers",
            "fluids",
            "hairSystems",
            "follicles",
            "nCloths",
            "nParticles",
            "nRigids",
            "dynamicConstraints",
            "locators",
            "dimensions",
            "pivots",
            "handles",
            "textures",
            "strokes",
            "motionTrails",
            "pluginShapes",
            "clipGhosts",
            "greasePencils",
            "gpuCacheDisplayFilter"]


def hiddenShowType():
    result = {}
    mp = cmds.getPanel(visiblePanels=1)[0]
    for typ in showType:
        if typ == 'gpuCacheDisplayFilter':
            mel = 'modelEditor -q -queryPluginObjects %s %s;' % (typ, mp)
        else:
            mel = 'modelEditor -q -%s %s;' % (typ, mp)
        v = pm.mel.eval(mel)

        if v:
            result[typ] = v
    # show none
    m = 'modelEditor -e -allObjects 0 %s;' % mp
    pm.mel.eval(m)
    return result


def displayShowType(typeDic={}):
    if not typeDic:
        return
    mp = cmds.getPanel(visiblePanels=1)[0]
    for typ, v in typeDic.iteritems():
        if typ == 'gpuCacheDisplayFilter':
            mel = 'modelEditor -e -pluginObjects %s %s %s;' % (typ, v, mp)
        else:
            mel = 'modelEditor -e -%s %s %s;' % (typ, v, mp)

        pm.mel.eval(mel)


class UploadFilesToCgtwQueue(Action):
    "upload to cgtw's queue widget"

    def run(self):

        path = self.parm('path')
        import cgtw
        t_tw = cgtw.tw()
        files = []

        if type(path) == list:
            files = path

        if type(path) == str:

            if os.path.isdir(path):
                filename = os.listdir(path)

                for n in filename:
                    filepath = "%s/%s" % (path, n)
                    # filepath = filepath.replace('\\','/')
                    files.append(filepath)

            if os.path.isfile(path):
                files = [path]

        data_task = engine.getTaskFromEnv()
        db = dbif.CGT().getDataBase()
        module = data_task["pipeline_type"]
        module_type = "task"
        task_id_list = data_task["task_id"]

        for f in files:
            if not os.path.isfile(f):
                continue

            filename = os.path.basename(f)
            networkPath = os.path.splitdrive(f)[-1].replace('\\', '/')

            upload_list = [{"sou": f, "des": networkPath}]

            taskInfo = [
                {"action": "upload",
                 "is_contine": True,
                 "data_list": upload_list,
                 "db": db,
                 "module": module,
                 "module_type": module_type,
                 "task_id": task_id_list,
                 "version_id": ""}
            ]

            info = {'name': filename,
                    'task': taskInfo}

            t_tw.local_con._send("queue_widget", "add_task", {"task_data": info}, "send")


class SetXgen(Action):

    # data = engine.getTaskFromEnv()
    # seq = data["sequence"]
    # shot = data["shot"]
    # xgn_path = r"Z:/LongGong/sequences/{0}/{1}/nHair/work/render/*.xgen"
    # abc_cache_path = r"Z:/LongGong/sequences/{0}/{1}/Cache/nHair/approved/*.abc"

    def hiddenHair(self):
        char_as = [i for i in cmds.ls(assemblies=True) if "char" in i]
        for i in char_as:
            modle_grp = cmds.listRelatives(i, children=True)
            for j in cmds.listRelatives(modle_grp, children=True):
                if "m_hair_GRP" in j:
                    cmds.setAttr(j + ".visibility", 0)

    def run(self):
        data = engine.getTaskFromEnv()
        seq = data["sequence"]
        shot = data["shot"]
        sys.path.append(r"Z:\bin\script\work\maya\setXgenFiles")
        import script
        reload(script)
        from script import SetXgen
        set_sgn = SetXgen(seq, shot)

        set_sgn.loadXgenPlugin()
        set_sgn.imptScalp()
        set_sgn.setXgenFile()
        set_sgn.setAniAbc()
        set_sgn.refreshXgen()
        # self.hiddenHair()


class AssignHairSystem(Action):

    def run(self):
        import maya.mel as mel
        mel.eval('source "Z:/bin/script/syf_nHair_Assign_peBrush_tool.mel"')
        mel.eval('if(`window -exists "syf_texture_random"`) deleteUI -window syf_texture_random;')
        transform_ls = cmds.ls(type="transform")
        for i in transform_ls:
            try:
                if "charQian_hair_Long" in i:
                    cmds.select(i, r=True)
                    mel.eval('charQian_hairSystem_Long_Assign()')
                elif "charQian_hair_Short" in i:
                    cmds.select(i, r=True)
                    mel.eval('charQian_hairSystem_Short_Assign()')
                elif "charBossPi_hair_Long" in i:
                    cmds.select(i, r=True)
                    mel.eval('charBossPi_hairSystem_long_Assign')
                elif "charBossPi_hair_ShortA" in i:
                    cmds.select(i, r=True)
                    mel.eval('charBossPi_hairSystem_shortA_Assign')
                elif "charBossPi_hair_ShortB" in i:
                    cmds.select(i, r=True)
                    mel.eval('charBossPi_hairSystem_shortB_Assign')
                elif "charAnglerFishHair_Desc" in i:
                    cmds.select(i, r=True)
                    mel.eval('charAnglerFish_Head_Assign')
            except:
                pass


class ExportAssembleJson(Action):
    _defaultParms = {
        'cache_path': '',
        'grp_name': "",
        "output_path": ""
    }

    def run(self):
        sys.path.append(r"Z:\bin\script\work\maya\AssignBackgroundRole")
        import action
        reload(action)
        from action import Maya
        my = Maya()
        objs = self.parm('grp_name')
        if type(objs) == list:
            objs = objs[0]
        kwargs = {
            'cache_path': self.parm('cache_path'),
            'grp_name': objs,
            'output_path': self.parm('output_path')
        }
        my.exportAssembleJson(**kwargs)


class AssembleJson(Action):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        import sys
        sys.path.append(r"Z:\bin\script\work\maya\AssignBackgroundRole")
        import action
        reload(action)
        from action import Maya
        my = Maya()

        data = engine.getTaskFromEnv()
        seq = data["sequence"]
        shot = data["shot"]

        material_json_path = "Z:/LongGong/sequences/{0}/{1}/Cache/nCloth/approved/MaterialMessage.json".format(seq,
                                                                                                               shot)
        my.run(material_json_path)

        material_json_path1 = "Z:/LongGong/sequences/{0}/{1}/Cache/shotFinaling/approved/MaterialMessage.json".format(
            seq, shot)
        my.run(material_json_path1)

        return material_json_path


class ShowHairCurve(Action):

    def run(self):
        [cmds.setAttr(i + ".visibility", 1) for i in cmds.ls(type="transform", long=True) if
         "nhair_Grp" in i and "model" in i]
