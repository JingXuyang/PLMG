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
import utilities


env_config = ""


def save_env():
    env_path = os.path.join(
        env_config.get("data_path"),
        "{sw}_env.json".format(sw=env_config.get("software"))
    )
    utilities.write_json(env_path, env_config)


def getenv():
    env_path = os.path.join(
        env_config.get("data_path"),
        "{sw}_env.json".format(sw=env_config.get("software"))
    )
    return utilities.load_json(env_path, env_config)


def set_env(kwargs):
    '''
    From "../packages/{software}/{version}"
    @param env_ls:
    @return:
    '''
    if kwargs["software"] == "maya":
        env_ls = kwargs.get("extra_envs")
        if isinstance(env_ls, list):
            new_envs = os.environ.copy()
            for env in env_ls:
                value = env.get("value", "").format(
                    ROOT=os.environ["XSYH_ROOT_PATH"],
                    XSYH_ROOT_PATH=os.environ["XSYH_ROOT_PATH"],
                    XSYH_PACKAGE_PATH=kwargs.get("package")
                )
                name = env.get("name")
                if env["mode"] == "over":
                    new_envs[name] = value

                elif env["mode"] == "prefix":
                    new_envs[name] = "{0};{1}".format(new_envs.get(name, ""), value)

                elif env["mode"] == "suffix":
                    new_envs[name] = "{0};{1}".format(value, new_envs.get(name, ""))

            # 添加 ../scripts到 "PYTHONPATH", 能够自动运行userSetup.py
            new_envs["PYTHONPATH"] = new_envs.get("PYTHONPATH")+";"+os.path.join(kwargs["package"], "scripts")

            return new_envs
        else:
            return None
    else:
        return {}


def launch_software(software, new_env=""):
    '''
    Launch software by subprocess.
    @param software: software path
    @param new_env: env to set
    '''
    if not new_env:
        new_env = dict()
    subprocess.Popen(software, env=new_env)


def launch(**kwargs):
    '''
    Start the software.
    '''
    global env_config
    env_config = kwargs

    # launch the software
    new_env = set_env(kwargs)
    sf_path = kwargs.get("sw_path")
    launch_software('"{0}"'.format(sf_path), new_env)
    # save the global environment
    save_env()


# if __name__ == '__main__':
#     launch_software(r"C:\Program Files\Autodesk\Maya2016.5\bin\maya.exe", {})
