# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Author: RunningMan
#  @File: deploy.py
#  @Create Time: 2019/12/30 15:15
# ==============================================================
import sys
from functools import partial

import engine
from PySide import QtGui
from PySide import QtCore


class MyTreeWidget(QtGui.QTreeWidget):

    def __init__(self, parent=None):
        super(MyTreeWidget, self).__init__(parent)
        # self.setStyleSheet("QTreeWidget::item{height:40px;}")

    def setHeaderLabs(self, labels):
        self.setHeaderLabels(labels)

    def createItem(self, parent_item="", data="", expand=False):
        '''
        1. 如果指定了parent_item, 以该 parent 为根节点创建 “子” item
            --parent
               |_ _ item
               |_ _ item
        2. 如果没有指定parent_item, 则创建 item
            -- item
        如果 expand 是 True, 则添加一个空的item使其可以展开。

        @param parent_item: class item
        @param data: [{'':''}, {'':''}, ...]
        @param expand: bool
        @return: class item
        '''
        data = data if isinstance(data, list) else [data]
        if parent_item:
            parent_item.takeChildren()
            for each in data:
                if isinstance(each, dict):
                    root = QtGui.QTreeWidgetItem(parent_item)
                    for sign, text in each.items():
                        if isinstance(text, tuple):
                            root.setText(self.getHeaderIndex(text[1]), text[0])
                        else:
                            if self.getHeaderIndex(text):
                                root.setText(self.getHeaderIndex(text), text)
                else:
                    root = QtGui.QTreeWidgetItem(parent_item)
                    root.setText(0, each)
                    if expand:
                        QtGui.QTreeWidgetItem(root)
            return root
        else:
            for text in data:
                root = QtGui.QTreeWidgetItem(self)
                root.setText(0, text)
                if expand:
                    QtGui.QTreeWidgetItem(root)
            return root

    def getItemLevel(self, item):
        '''
        得到item的层级
        @param item: item object
        @return: int
        '''
        level = 0
        index = self.indexFromItem(item, 0)

        while index.parent().isValid():
            index = index.parent()
            level += 1

        return level

    def getHeaderIndex(self, header_name):
        '''
        返回 header_name 在表头的位置
        @param header_name: text
        @return: int
        '''
        count = self.columnCount()
        for i in range(count):
            if self.headerItem().text(i) == header_name:
                return i

        return None

    def selectionInfo(self):
        '''
        得到选择的信息。
        '''
        item = self.currentItem()
        if item:
            result = {}
            for i in range(self.columnCount()):
                header_label = self.headerItem().text(i)
                result[header_label] = item.text(i)
            return result
        else:
            return False


if __name__ == '__main__':
    data = {
        "header_label": ["Seq", "Shot", "Step", "Task", "User"],
        "proj_name": "LongGong",
        "sequence": ["Seq110", "Shot1201"],

    }

    app = QtGui.QApplication(sys.argv)
    win = MyTreeWidget(data)
    win.show()
    sys.exit(app.exec_())
