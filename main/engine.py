# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
# 
#  @Version: 
#  @Author: RunningMan
#  @File: engine.py
#  @Create Time: 2020/2/4 19:51
# ==============================================================

import os

import utilities

# -------------------------- Global Values --------------------------
CONFIG_DATA = utilities.load_yaml(os.path.join(os.environ.get('XSYH_ROOT_PATH'), "data/config.yaml"))

# -------------------------- Functions --------------------------
def main():
    CONFIG_DATA = utilities.load_yaml(os.path.join(os.path.dirname(__file__), "../../data/config.yaml"))
    print CONFIG_DATA


if __name__ == '__main__':
    main()
