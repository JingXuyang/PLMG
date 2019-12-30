# ==============================================================
# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: RunningMan
#  @File: deploy.py
#  @Create Time: 2019/12/30 15:15
# ==============================================================

import copy


PROJECT = ""


def launch(package, version='', tool='', project=PROJECT,
           args=[], wait=True, extraEnvs={}):
    '''
    Launches the package with subprocess module.

    Arguments:
        package
            Package name.
        version
            Package version number.
        tool
            The tool of the package you want to launch.
            There might be more than one sub package. We call it tool.
            A tool is usually in the same folder as the main execute file.
            For instance there are lots of tools for Houdini, like hython, hserver.
            We can treat them as a tool of Houdini.
        project
            Project name. Default value is studio.
        args
            Arguments which will pass to the package exe file.
        wait
            Whether to wait the process of the package until it is closed.
            Default value is True which means the main process will wait the package process.
        extraEnvs
            Extra variables put to the env. It's a dictionary.
    '''
    kwargs = copy.deepcopy(vars())
    print kwargs
