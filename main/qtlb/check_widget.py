# !/usr/bin/env python
# -*- coding: utf-8 -*-
# ==============================================================
#  @Author     : RunningMan
#  @File       : interface.py
#  @Create Time: 2020/03/11 16:15:47
# ==============================================================
import os
from widget import *


# ------------------------- class --------------------------
class TaskThread(QtCore.QThread):

    finished = QtCore.Signal(object)

    def __init__(self, cls, check_table, parent=None):
        super(TaskThread, self).__init__(parent)
        self.cls = cls
        self.check_table = check_table

    def run(self):
        try:
            result = self.cls().run()
        except:
            result = 'no'
        # getattr(self.check_table, self.cls.__name__+"label").setVisible(False)
        self.finished.emit(result)


class ImagePlayer(QtWidgets.QLabel):
    def __init__(self, filename, parent=None):
        super(ImagePlayer, self).__init__(parent)

        self.setImg(filename)
        
    def setImg(self, img):
        # Load the file into a QMovie
        self.movie = QtGui.QMovie(img, QtCore.QByteArray(), self)

        # Set gif zize
        self.movie.setScaledSize(QtCore.QSize(30, 30))

        # Make label fit the gif
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.setAlignment(QtCore.Qt.AlignCenter)

        # Add the QMovie object to the label
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.movie.setSpeed(100)
        
        self.setMovie(self.movie)

    def start(self):
        """sart animnation"""
        self.movie.start()

    def clear(self):
        self.movie.destroyed()


class ResultWidget(QtWidgets.QWidget):

    def __init__(self, data, parent=None):
        super(ResultWidget, self).__init__(parent)
        self.setWindowTitle(r"检查结果")
        self.resize(600, 400)
        self.data = data
        result_wgt = self.buildWgt()

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(result_wgt)
    
    def buildWgt(self):
        tree_wgt = QtWidgets.QTreeWidget(self)
        tree_wgt.setHeaderHidden(True)
        if isinstance(self.data, dict):
            for key, val in self.data.iteritems():
                root = QtWidgets.QTreeWidgetItem(tree_wgt)
                root.setText(0, key)
                root.setExpanded(True)
                for v in val:
                    root = QtWidgets.QTreeWidgetItem(root)
                    root.setText(0, v)
        elif isinstance(self.data, list):
            for root in self.data:
                root = QtWidgets.QTreeWidgetItem(tree_wgt)
                root.setText(0, key)

        return tree_wgt


class CheckWidget(QtWidgets.QWidget):

    def __init__(self, engine='', parent=None):
        super(CheckWidget, self).__init__(parent)

        self._engine = engine()
        self._par = parent
        self._build_data = self._engine.getCheckingList()
        self._init_ui()

    def _init_ui(self):
        # create check widget
        self.check_btn = QtWidgets.QPushButton('Check')
        self.fix_btn = QtWidgets.QPushButton('Fix All')
        self.check_table = MyTableWidget()
        
        # create layout
        lay1 = QtWidgets.QHBoxLayout()
        lay1.addStretch()
        lay1.addWidget(self.check_btn)
        lay1.addWidget(self.fix_btn)
        lay1.addStretch()

        self.lay = QtWidgets.QVBoxLayout(self)
        self.lay.addLayout(lay1)
        self.lay.addWidget(self.check_table)

        # build check widget
        self.buildCheckItem()
        self.setMiddleCenter()

        # create signal
        self.check_btn.clicked.connect(self.start)
        self.check_btn.clicked.connect(self.checkResult)
        self.fix_btn.clicked.connect(self.fixAll)
        self.fix_btn.clicked.connect(self.checkResult)

    def setMiddleCenter(self):
        '''
        设置表格字体居中
        '''
        row = self.check_table.rowCount()
        col = self.check_table.columnCount()
        for x in range(row):
            for y in range(col):
                item = self.check_table.item(x, y)
                if item:
                    item.setTextAlignment(QtCore.Qt.AlignCenter)

    def addWidgetToCell(self, widget_cls, margin=0):
        '''
        控件添加到QTreeWidgetItem 可以居中显示。
        把控件添加到一个新的布局中，然后设置为widget的布局，返回widget。
        '''
        widget = QtWidgets.QWidget()
        lay = QtWidgets.QHBoxLayout()
        # lay.addSpacing(0.1)
        # lay.setMargin(1)
        lay.addWidget(widget_cls)
        widget.setLayout(lay)
        return widget

    def buildCheckItem(self):
        '''
        建立检查项，第一列是名称，第二列检查进度，第三列查看检查结果
        '''
        self.check_table.setColumnCount(5)
        self.check_table.setColumnWidth(0, 230)
        self.check_table.setColumnWidth(1, 300)
        self.check_table.setColumnWidth(2, 60)
        self.check_table.setColumnWidth(3, 60)
        self.check_table.setColumnWidth(4, 60)
        self.check_table.customStyle()
        self.check_table.setHorizontalHeaderLabels(["Check item", u"Result", u"State", 'Fix', 'Select'])
        self.check_table.setRowCount(len(self._build_data))

        for index, item in enumerate(self._build_data):
            checkable = item[1]
            check_cls = item[0]

            # 得到注册类 的名字
            cls_name = check_cls.__name__

            # 创建一个名字为 "'class'name"的属性, 并实例化 QTableWidgetItem
            name = check_cls().cnLabel()
            setattr(self.check_table, cls_name+"name", QtWidgets.QTableWidgetItem(name))
            item = getattr(self.check_table, cls_name+"name")
            # if checkable:
            #     item.setCheckState(QtCore.Qt.Checked)
            # else:
            #     item.setCheckState(QtCore.Qt.Unchecked)
            item.setCheckState(QtCore.Qt.Checked)

            # 用来显示检查结果
            setattr(self.check_table, cls_name+"result", QtWidgets.QTableWidgetItem())
            result_item = getattr(self.check_table, cls_name+"result")

            # 创建一个名字为 "'class'progrss"的属性,实例化一个 ImagePlayer
            img = ImagePlayer("{0}/icons/loading.gif".format(os.path.dirname(__file__)))
            setattr(self.check_table, cls_name+"label", img)
            label = getattr(self.check_table, cls_name+"label")

            # 创建一个名字为 "check_btn"的属性,实例化一个 QPushButton
            setattr(self.check_table, cls_name+"fix_btn", QtWidgets.QPushButton('Fix'))
            fix_btn = getattr(self.check_table, cls_name+"fix_btn")
            fix_btn.setEnabled(False)

            # 创建一个名字为 "fix_btn"的属性,实例化一个 QPushButton
            setattr(self.check_table, cls_name+"sel_btn", QtWidgets.QPushButton('Select'))
            sel_btn = getattr(self.check_table, cls_name+"sel_btn")
            sel_btn.setEnabled(False)

            # 设置单元格值
            self.check_table.setItem(index, 0, item)
            self.check_table.setItem(index, 1, result_item)
            # self.check_table.setCellWidget(index, 2, label)
            self.check_table.setCellWidget(index, 3, fix_btn)
            self.check_table.setCellWidget(index, 4, sel_btn)

    def runCheck(self, cls):
        result = cls().run()
        if not result:
            return 'OK'
        return result

    def runFix(self, cls):
        if hasattr(cls, 'fix'):
            cls().fix()
        return 'OK'

    def getAllCheckItems(self):
        result = list()
        for index, check_item in enumerate(self._build_data):
            for num, state in enumerate(self.check_table.getRowState()):
                if index == num and state[1] == 'Checked':
                    result.append(check_item)

                # 不检查的时候删除图标
                elif index == num and state[1] == 'Unchecked':
                    self.check_table.item(index, 1).setText('')

        return result

    def start(self):
        '''
        开始检查，创建一个包含所有检查项的迭代器， 迭代第一个检查项
        '''
        self.check_btn.setEnabled(False)

        # 得到勾选的检查项
        self._to_check_data = self.getAllCheckItems()

        # 创建迭代器
        self.data_iter = iter(self._to_check_data)

        # 迭代检查项
        self.continueIter()

    def continueIter(self):
        '''
        迭代每个检查项
        '''
        try:
            # 更改当前检查项的图标
            self.check_index = self.data_iter.next()
            check_cls = self.check_index[0]
            getattr(self.check_table, check_cls.__name__+"label").start()
            result = self.runCheck(check_cls)

            # 更新检查项的按钮状态
            self.updateFixBtn(result)

            # 迭代检查项
            self.continueIter()

        except StopIteration:
            # 遇到StopIteration就退出循环
            self.check_btn.setEnabled(True)

    def changeResult(self, item, btn):
        '''
        更改按钮的状态
        '''
        item.setText('OK')
        btn.setEnabled(False)

    def updateFixBtn(self, result):
        '''
        检查完成后更新界面
        '''

        # 更新 状态图片
        img = getattr(self.check_table, self.check_index[0].__name__+"label")
        img.setImg("{0}/icons/successful01.gif".format(os.path.dirname(__file__)))
        img.start()

        check_cls = self.check_index[0]
        result_item = getattr(self.check_table, check_cls.__name__+"result")
        fix_btn = getattr(self.check_table, check_cls.__name__+"fix_btn")
        sel_btn = getattr(self.check_table, check_cls.__name__+"sel_btn")

        if result != 'OK':
            result_item.setText(str(result))
            if hasattr(check_cls, 'fix'):
                fix_btn.setEnabled(True)
                temp = check_cls()
                fix_btn.clicked.connect(lambda: temp.fix())
                fix_btn.clicked.connect(lambda: self.changeResult(result_item, fix_btn))
                fix_btn.clicked.connect(self.checkResult)
            if hasattr(check_cls, 'select'):
                sel_btn.setEnabled(True)
                temp = check_cls()
                sel_btn.clicked.connect(lambda: temp.select())
        else:
            result_item.setText('OK')
            fix_btn.setEnabled(False)
            sel_btn.setEnabled(False)
            self.checkResult()

    def fixAll(self):
        def getAllFixItems():
            result = list()
            for index, check_item in enumerate(self._build_data):
                if self.check_table.getItem(index, 1).text() != 'OK':
                    result.append(check_item)
            return result

        # 得到需要fix的检查项
        self._to_fix_data = getAllFixItems()

        # 创建迭代器
        self.fix_data_iter = iter(self._to_fix_data)

        # 迭代检查项
        self.fixContinueIter()

    def fixContinueIter(self):
        '''
        迭代每个检查项
        '''
        try:
            # 更改当前检查项的图标
            self.check_index = self.fix_data_iter.next()
            check_cls = self.check_index[0]
            getattr(self.check_table, check_cls.__name__+"label").start()
            result = self.runFix(check_cls)

            # 更新检查项的按钮状态
            self.updateFixBtn(result)

            # 迭代检查项
            self.fixContinueIter()

        except StopIteration:
            # 遇到StopIteration就退出循环
            self.check_btn.setEnabled(True)

    def checkResult(self):
        '''
        检查每一项的结果，如果都是‘OK’，下一步按钮启动
        如果存在其他的结果，下一步按钮关闭
        '''
        result_row = self.check_table.getAllRows(0)
        check_error = list()
        for index, item in enumerate(result_row):
            if item.checkState().name == 'Checked' and self.check_table.getItem(index, 1).text() != 'OK':
                check_error.append(item)
        if not check_error:
            self._par.next_btn.setEnabled(True)

    # def showResult(self, data):
    #     '''
    #     弹出检查结果窗口
    #     '''
    #     wgt = ResultWidget(data)
    #     wgt.show()
    #     wgt.exec_()
