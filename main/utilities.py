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
sys.path.append(r"E:\LongGong\XXYH\test\pltk\thirdparty")
import yaml


def handle_error(func):
    def run():
        try:
            func()
        except:
            return "error"
    return run


# @handle_error
def load_yaml(path):
    '''
    Return data of the yaml file.
    '''
    if os.path.exists(path) and os.path.splitext(path)[-1] == ".yaml":
        with open(path) as f:
            data = yaml.load(f)
        return data
    else:
        return False


if __name__ == '__main__':
    print load_yaml(r"E:\LongGong\XXYH\packages\maya\2016.5\info.yaml")
