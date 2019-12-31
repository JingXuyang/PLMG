# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Author: RunningMan
#  @File: deploy.py
#  @Create Time: 2019/12/30 15:15
# ==============================================================

__version__ = '1.0'

import os
import subprocess

import sfmg


def set_env(env_ls):
    if isinstance(env_ls, list):
        new_envs = os.environ.copy()
        for env in env_ls:
            if env["mode"] == "over":
                new_envs[env.get("name")] = env.get("value")
            elif env["mode"] == "prefix":
                new_envs[env.get("name")] = new_envs.get(env.get("name"))+";"+env.get("value")
            elif env["mode"] == "suffix":
                new_envs[env.get("name")] = env.get("value")+";"+new_envs.get(env.get("name"))
        return new_envs
    else:
        return None


def launch_software(software, new_env):
    '''
    Launch software bu subprocess.
    '''
    if not new_env:
        new_env = dict()
    subprocess.Popen(software, env=new_env)


def launch(**kwargs):
    '''
    Launch software bu subprocess.
    '''
    new_env = set_env(kwargs.get("extra_envs"))
    sf_path = kwargs.get("sw_path")
    commands = '"{0}"'.format(sf_path)
    launch_software(commands, new_env)


if __name__ == '__main__':
    launch_software(r"C:\Program Files\Autodesk\Maya2016.5\bin\maya.exe")
