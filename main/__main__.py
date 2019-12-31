# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
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
        # main folder path
        main_path = sys.argv[0]

        # software name
        sw = sys.argv[1]

        # software version
        sw_version = sys.argv[2]

        # loading project
        project = sys.argv[3]

        package_path = os.path.join(os.path.dirname(main_path), "packages", sw, sw_version, "info.yaml")
        info_data = utilities.load_yaml(package_path)
        kwargs = dict()
        kwargs["software"] = sw
        kwargs["sw_path"] = info_data["exe"]
        kwargs["extra_envs"] = info_data["env"]
        kwargs["project"] = project
        print kwargs
        # launch software
        # deploy.launch(**kwargs)
    else:
        print("参数有误")


if __name__ == '__main__':
    main()
