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
from engine import ActionEngine
sys.path.append("C:/cgteamwork/bin/base")

import cgtw
import cgtw2
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om


class GetPathFromTag(ActionEngine):
    _defaultParms = {
        'input': '',
    }

    def run(self):
        print "run"

