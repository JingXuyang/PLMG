# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Author: RunningMan
#  @File: deploy.py
#  @Create Time: 2019/12/30 15:15
# ==============================================================

from functools import partial
from PySide import QtGui

HEADER_LABELS = ["Seq", "Shot", "Step", "Task", "User"]


class TaskWidget(QtGui.QTreeWidget):

    def __init__(self, data):
        super(TaskWidget, self).__init__()
        self.data = data

        # -------------------------- 部件 --------------------------
        self.setHeaderLabels(HEADER_LABELS)
        self.createWidget(self.data)

        # -------------------------- 信号 --------------------------
        self.itemExpanded.connect(partial(self.update, "1"))

    def createWidget(self, data):
        if data and isinstance(data, dict):
            for key, val in data.iteritems():
                root = QtGui.QTreeWidgetItem(self)
                root.setText(0, key)

    def update(self, item, data=""):
        if data and isinstance(self.data, dict):
            for key, val in self.data.iteritems():
                root = QtGui.QTreeWidgetItem(self)
                root.setText(0, key)
        else:
            return

