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
import getpass
import yaml
import time
import shutil


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


def setEnv(dicts):
    '''
    设置环境变量
    @param dicts: 环境变量字典
    '''
    for key, val in dicts.iteritems():
        os.environ[key] = val


def filterType(path, file_typ=""):
    '''
    :param path: 路径
    :return: file_typ，返回扩展名, 否则为Folse
    '''
    if os.path.isfile(path):
        ext = os.path.splitext(path)[1]
        if ext in file_typ:
            return ext
        else:
            return False


def getUser():
    '''
    返回当前系统的用户名
    '''
    return getpass.getuser()


def getFoldersInPath(path):
    '''
    返回path下边所有的文件夹列表
    '''
    if os.path.exists(path):
        folder = []
        lst = os.listdir(path)  # 列出文件夹下所有的目录
        for i in range(0, len(lst)):
            temp = os.path.join(path, lst[i])
            if os.path.isdir(temp):
                folder.append(lst[i])
        return folder
    else:
        return []


def getFilesInFolder(path):
    '''
    返回 path下边所有的文件列表
    '''
    if os.path.exists(path):
        files = []
        list = os.listdir(path)  # 列出文件夹下所有的文件
        for i in range(0, len(list)):
            temp = os.path.join(path, list[i])
            if os.path.isfile(temp):
                files.append(list[i])
        return files
    else:
        return []


def getBaseName(path):
    '''
    得到文件名字
    '''
    if os.path.exists(path):
        return os.path.basename(path)
    else:
        return ""


def makeFolder(path):
    '''
    创建文件夹
    '''
    folder = os.path.dirname(path)
    if not os.path.isdir(folder):
        os.makedirs(folder)


def copyFile(src, dst):
    '''
    拷贝文件
    '''
    src = src.replace('\\', '/')
    dst = dst.replace('\\', '/')
    if os.path.exists(src) and src != dst:
        shutil.copyfile(src, dst)


def timeStampToTime(timestamp):
    '''
    把时间戳转化为时间: 1479264792 to 2016-11-16 10:53:12
    '''
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


def getFileSize(path):
    '''
    获取文件的大小,结果保留两位小数，单位为MB
    '''
    fsize = os.path.getsize(path)
    fsize1 = fsize / float(1024 * 1024)
    if fsize1 > 1:
        return str(round(fsize1, 1)) + "MB"
    else:
        fsize1 = fsize / float(1024)
        return str(round(fsize1, 1)) + "KB"


def getFileModifyTime(path):
    '''
    获取文件的修改时间
    '''
    t = os.path.getmtime(path)
    return timeStampToTime(t)


if __name__ == '__main__':
    print(load_json(r"E:\LongGong\XXYH\data\maya_env.json"))
