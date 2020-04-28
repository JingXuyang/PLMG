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

from Qt import QtGui
from Qt import QtWidgets
from Qt import QtCore


class MyTreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, parent=None):
        super(MyTreeWidget, self).__init__(parent)
        self.customStyle()

    def customStyle(self, size=9, item_h=15):
        '''设置字体样式'''
        font = QtGui.QFont()
        font.setPointSize(size)
        self.setFont(font)
        self.setStyleSheet("QTreeWidget::item{height:%spx;}" % (item_h))

    def setHeaderLabs(self, labels):
        '''设置表头'''
        self.setHeaderLabels(labels)

    def setHeaderStyle(self):
        self.header().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.setSortingEnabled(True)
        self.sortItems(0, QtCore.Qt.AscendingOrder)

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
                root = QtWidgets.QTreeWidgetItem(parent_item)
                if isinstance(each, dict):
                    index = 1
                    for sign, text in each.items():
                        root.setTextAlignment(index, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                        if isinstance(text, tuple):
                            header_index = self.getHeaderIndex(text[1])
                            if header_index >= 0:
                                root.setText(header_index, text[0])
                        else:
                            header_index = self.getHeaderIndex(sign)
                            if header_index >= 0:
                                root.setText(header_index, text)
                        index += 1
                else:
                    root.setText(0, each)
                    if expand:
                        QtWidgets.QTreeWidgetItem(root)
            return root

        else:
            for each in data:
                root = QtWidgets.QTreeWidgetItem(self)
                if isinstance(each, dict):
                    index = 1
                    for sign, text in each.items():
                        root.setTextAlignment(index, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                        if isinstance(text, tuple):
                            header_index = self.getHeaderIndex(text[1])
                            if header_index >= 0:
                                root.setText(header_index, text[0])
                        else:
                            header_index = self.getHeaderIndex(sign)
                            if header_index >= 0:
                                root.setText(header_index, text)
                        index += 1
                else:
                    root.setText(0, each)
                    if expand:
                        QtWidgets.QTreeWidgetItem(root)
            return root

    def getItemLevel(self, item):
        '''
        得到item所在的层级
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
        返回 header_name 在表头的序号
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

    def getCheckedItems(self):
        child_root = []
        it = QtWidgets.QTreeWidgetItemIterator(self)
        while it:
            item = it.value()
            if not item:
                break
            if not item.childCount() and item.checkState(0).name == 'Checked':
                child_root.append(item)
            it += 1
        return child_root

    def getParentList(self, child_root, result):
        '''
        根据子节点查找父节点
        '''
        result.append(child_root.text(0))
        par_root = child_root.parent()
        if par_root:
            self.getParentList(par_root, result)

    def getRootLevel(self):
        '''
        得到所有子节点的全部层级:
        例如树：
            a
            |__b
               |__c
               |__b
        返回：
            [
                ['a', 'b', 'c'],
                ['a, 'b', 'b']
            ]
        @return: list
        '''
        child_root = []
        it = QtWidgets.QTreeWidgetItemIterator(self)
        while it:
            item = it.value()
            if not item:
                break
            if not item.childCount():
                child_root.append(item)
            it += 1

        result = []
        for i in child_root:
            temp = []
            self.getParentList(i, temp)
            result.append(temp[::-1])
        return result


class MyTableWidget(QtWidgets.QTableWidget):

    def __init__(self, parent=None):
        super(MyTableWidget, self).__init__(parent)

        self.customStyle()

    def customStyle(self):
        '''
        自定义窗口风格化
        '''
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)  # 设置只可以单选，可以使用ExtendedSelection进行多选
        self.setSortingEnabled(True)  # 设置表头可以自动排序
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.setAlternatingRowColors(True)
        self.setFrameStyle(QtWidgets.QFrame.NoFrame)

    def getItem(self, row='', column=0):
        '''
        返回指定的 行和列的item
        @param row: 行数
        @param column: 列数
        @return: QTableWidgetItem
        '''
        row_count = self.rowCount()
        for _row in range(row_count):
            if _row == row:
                return self.item(_row, column)

    def getAllRows(self, column):
        '''
        返回指定列数的所有item
        @param column: 列数
        @return: QTableWidgetItem
        '''
        result = list()
        row_count = self.rowCount()
        for _row in range(row_count):
            result.append(self.item(_row, column))
        return result

    def getRowState(self):
        '''
        范湖第一列单元格的所有勾选状态
        @return: QTableWidgetItem
        '''
        result = list()
        row_count = self.rowCount()
        for _row in range(row_count):
            result.append((self.item(_row, 0), self.item(_row, 0).checkState().name))
        return result


def test():
    data = {
        "header_label": ["Seq", "Shot", "Step", "Task", "User"],
        "proj_name": "LongGong",
        "sequence": ["Seq110", "Shot1201"],

    }

    app = QtWidgets.QApplication(sys.argv)
    win = MyTreeWidget(data)
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
