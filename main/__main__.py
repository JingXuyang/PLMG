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

        PACKAGE_PATH = os.path.join(os.environ["XSYH_ROOT_PATH"], "packages", sw, sw_version)

        info_data = utilities.load_yaml(PACKAGE_PATH + "/info.yaml")
        kwargs = dict()
        kwargs["software"] = sw
        kwargs["sw_version"] = sw_version
        kwargs["sw_path"] = info_data["exe"]
        kwargs["sw_tools"] = info_data["tools"]
        kwargs["extra_envs"] = info_data["env"]
        kwargs["package"] = PACKAGE_PATH
        kwargs["project"] = project
        kwargs["global_config"] = ""
        kwargs["pack_path"] = ""
        kwargs["data_path"] = os.path.join(os.environ["XSYH_ROOT_PATH"], "data")

        # pass the sys argv to the deploy
        deploy.launch(**kwargs)

    else:
        print("参数有误")


if __name__ == '__main__':
    main()
