# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Version: 
#  @Author: RunningMan
#  @File: utilities.py
#  @Create Time: 2019/12/30 17:29
# ==============================================================

import os
import sys
import json
import yaml


def handle_error(func):
    def run():
        try:
            func()
        except:
            return "error"
    return run


def write_json(path, data):
    if os.path.splitext(path)[-1] == ".json":
        with open(path, "w") as f:
            f.write(json.dumps(data, indent=4))
        return True


def load_json(path):
    if os.path.exists(path) and os.path.splitext(path)[-1] == ".json":
        with open(path, "r") as f:
            data = json.load(f)
        return data

    return False


def write_yaml(path, data):
    if os.path.exists(path):
        with open(path, "w") as f:
            f.write(yaml.dumps(data))
        return True


# @handle_error
def load_yaml(path):
    '''
    Return data of the yaml file.
    '''
    if os.path.exists(path) and os.path.splitext(path)[-1] == ".yaml":
        with open(path, "r") as f:
            data = yaml.load(f)
        return data

    return False


def get_inherit(cls):
    '''
    返回所有继承cls的子类
    @param cls: 父类
    @return: dict
    {
        'B': <class '__main__.B'>,
        'C': <class '__main__.C'>
    }
    '''
    sub_cls = {sub_cls.__name__: sub_cls for sub_cls in cls.__subclasses__()}
    return sub_cls


if __name__ == '__main__':
    print(load_json(r"E:\LongGong\XXYH\data\maya_env.json"))
