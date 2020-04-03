# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Author: RunningMan
#  @File: actions.py
#  @Create Time: 2020/3/30 15:15
# ==============================================================
import os
import copy
import shutil
import glob
import json
import re
import time
import traceback
import sys
from engine import ActionEngine as Action
sys.path.append("C:/cgteamwork/bin/base")

import dbif
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om


def _reference(sw, info, createSets=True, configs={}, groupOption=None,
               displayMode=None):
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
            #print 'sets:',info.get('sets')
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
            info = self._defaultParms['input']

            create_sets = self._defaultParms['create_sets']
            kwargs = {
                'sw': sw,
                'info': info,
                'createSets': create_sets
            }

            group_option = self._defaultParms['group_option']
            if group_option is not None:
                kwargs['groupOption'] = group_option

            display_mode = self._defaultParms['display_mode']
            if display_mode is not None:
                kwargs['displayMode'] = display_mode

            print kwargs
            return _reference(**kwargs)


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
        kwargs['tag'] = task.get('tag')
        self.database.getTaskFromTag(**kwargs)
