# ==============================================================
# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Version: 
#  @Author: RunningMan
#  @File: _maya.py
#  @Create Time: 2019/12/31 14:13
# ==============================================================


class Maya(object):

    def __init__(self):
        import maya.cmds as cmds
        import maya.mel as mel
        import pymel.core as pm
        self._pm = pm
        self._mel = mel
        self._cmds = cmds


class Render(object):

    def __init__(self):
        import maya.cmds as cmds
        import maya.app.renderSetup.model.override as override
        import maya.app.renderSetup.model.selector as selector
        import maya.app.renderSetup.model.collection as collection
        import maya.app.renderSetup.model.renderLayer as renderLayer
        import maya.app.renderSetup.model.renderSetup as renderSetup

        self._cmds = cmds
        self.render_setup = renderSetup.instance()
        # self.render_setup.initialize()
        self.override = override
        self.collection = collection
        self.selector = selector
        self.render_layer = renderLayer

    def create_render_layer(self, layer_name):
        '''
        create render layer
        @return: render layer
        '''
        layer_obj = self.render_setup.createRenderLayer(layer_name)
        return layer_obj

    @staticmethod
    def create_collection(render_layer, col_name):
        '''
        create collection of the render layer
        @return: collection
        '''
        col_obj = render_layer.createCollection(col_name)
        return col_obj

    def create_abs_override(self, col_name, over_name):
        '''
        create override of the collection.
        @return: override
        '''
        over_obj = col_name.createOverride(over_name, self.override.AbsOverride.kTypeId)
        return over_obj

