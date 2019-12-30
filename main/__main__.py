# ==============================================================
# !/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  @Author: RunningMan
#  @File: deploy.py
#  @Create Time: 2019/12/30 15:15
# ==============================================================

import sys
import os

import deploy
import utilities


def main():
    if len(sys.argv) > 1:
        main_path = sys.argv[0]
        sw = sys.argv[1]
        sw_version = sys.argv[2]
        project = sys.argv[3]
        package_path = os.path.join(os.path.dirname(main_path), "packages", sw, sw_version, "info.yaml")
        info_data = utilities.load_yaml_file(package_path)
        kwargs = dict()
        kwargs["sw_path"] = info_data["exe"]
        kwargs["extra_envs"] = info_data["env"]
        deploy.launch(**kwargs)


if __name__ == '__main__':
    main()
