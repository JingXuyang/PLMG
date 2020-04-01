# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Author: RunningMan
#  @File: deploy.py
#  @Create Time: 2019/12/30 15:15
# ==============================================================
import os
import widget
reload(widget)
from widget import *
from pprint import pprint

sys.path.append(r"E:\LongGong\XSYH\main")
import engine
import nodes
import dbif

# ================================= Global variable =================================
database = dbif.database
config_data = engine.getConfigs()
prj_name = os.environ["XSYH_PROJECT"]


# ================================= Function =================================
def refreshData():
    global config_data
    config_data = engine.relaodConfigs()


# ================================= Class =================================
class TaskWidget(QtGui.QWidget):
    '''
    选择任务的界面
    '''

    def __init__(self, data, parent=None):
        super(TaskWidget, self).__init__(parent)
        self.data = data

        # -------------------------- widget --------------------------
        self.task_widget = MyTreeWidget()
        self._initWidget()

        # -------------------------- layout --------------------------
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.task_widget)

        # -------------------------- single --------------------------
        self.task_widget.itemExpanded.connect(self.addItem)
        self.task_widget.itemClicked.connect(self.setTaskEnv)

    def _initWidget(self):
        '''
        初始化 tree widget
        '''
        self.task_widget.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.task_widget.setSortingEnabled(True)
        self.task_widget.sortItems(0, QtCore.Qt.AscendingOrder)

        # 设置header label
        labels = [i.get("label") for i in self.data.get("data")]
        self.task_widget.setHeaderLabs(labels)

        # 创建根节点为项目名
        root = self.task_widget.createItem(data=self.data.get("project"))
        root.setExpanded(True)
        self.task_widget.createItem(parent_item=root, data=self.data.get("sequence"), expand=True)

    def addItem(self, item):
        '''
        添加 Item 的子项
        如果是镜头，第一层是集数，第二层是镜头号，第三层是镜头任务。
        如果是资产，第一层是资产类型，第二层是资产名称，第三层是资产任务。
        @param item:
        @return:
        '''
        # shot 模块
        if self.data.get("type") == "shot":
            level = self.task_widget.getItemLevel(item)
            # 第二层是镜头
            if level == 1:
                shot_ls = database.getShots(item.text(0))
                self.task_widget.createItem(parent_item=item, data=shot_ls, expand=True)
            # 第三层是镜头任务
            elif level == 2:
                shot = item.text(0)
                seq = item.parent().text(0)
                shot_task = database.getShotTask(seq=seq, shot=shot, load_label=True)
                self.task_widget.createItem(parent_item=item, data=shot_task, expand=False)

        # asset 模块
        else:
            level = self.task_widget.getItemLevel(item)
            # 第二层是 资产名称
            if level == 1:
                asses_ls = database.getAssets()
                asset_type = item.text(0)
                self.task_widget.createItem(parent_item=item, data=asses_ls.get(asset_type), expand=True)
            # 第三层是 资产任务
            elif level == 2:
                asset_name = item.text(0)
                asset_type = item.parent().text(0)
                asset_task = database.getAssetTask(asset_type, asset_name, load_label=True)
                self.task_widget.createItem(parent_item=item, data=asset_task, expand=False)

    def setTaskEnv(self):
        '''
        set the task environment
        '''
        data = self.getSelection()
        kwargs = {
            "XSYH_PROJECT": os.environ.get("XSYH_PROJECT") or "",
            "XSYH_SEQUENCE": data.get("sequence") or "",
            "XSYH_SHOT": data.get("shot") or "",
            "XSYH_TYPE": data.get("type") or "",
            "XSYH_TASK": data.get("task_name") or "",
            "XSYH_TASK_STATUS": data.get("status") or "",
            "XSYH_ARTIST": data.get("account") or "",
            "XSYH_TASK_ID": data.get("task_id") or "",
        }
        engine.setEnv(kwargs)

    def getSelection(self):
        '''
        得到选择的任务信息。
        {u'artist': u'\u6b66\u661f\u707f',
         u'account': u'wuxingcan',
         u'sequence': u'Seq001',
         u'shot': u'Shot010',
         u'shot_id': u'0168EECA-0AEB-1D9A-0A4A-1FEAD2C742F5',
         u'shot_name': u'Shot010',
         u'start_time': u'2019-04-18 18:07:09',
         u'status': u'Check',
         u'step': u'Lighting',
         u'task_id': u'D035F59B-2F73-F805-009E-79A2629BA3A9',
         u'task_name': u'Lighting',
         u'type': 'shot'}
        @return: dict
        '''
        item = self.task_widget.currentItem()
        if not item.childCount():
            result = {}
            for i in range(self.task_widget.columnCount()):
                header_label = self.task_widget.headerItem().text(i)
                result[header_label] = item.text(i)
            result[u'sequence'] = item.parent().parent().text(0)
            result[u'shot'] = item.parent().text(0)
            task_kwargs = {
                'seq': result[u'sequence'],
                'shot': result[u'shot'],
                'step': result[u'step'],
                'task': result[u'task_name'],
            }

            if self.data.get("type") == "asset":
                result[u'type'] = "asset"
                task_kwargs['model'] = "asset",
                task_id = database.getTaskId(**task_kwargs)
                result[u'task_id'] = task_id
                result[u'asset_type'] = item.parent().parent().text(0)
                result[u'shot_id'] = database.getInfoId(result[u'sequence'], result[u'shot'], model="asset")
            else:
                result[u'type'] = "shot"
                task_id = database.getTaskId(**task_kwargs)
                result[u'task_id'] = task_id
                result[u'shot_id'] = database.getInfoId(result[u'sequence'], result[u'shot'])

            return result

        return dict()

    def updateFileWgt(self):
        pass


class FileWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(FileWidget, self).__init__(parent)

        # -------------------------- widget --------------------------
        self.file_widget = MyTreeWidget()
        self._initWidget()

        # -------------------------- layout --------------------------
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.file_widget)

        # -------------------------- single --------------------------
        # self.task_widget.itemExpanded.connect(self.addItem)
        # self.task_widget.itemClicked.connect(self.setTaskEnv)
        
    def _initWidget(self):
        self.file_widget = MyTreeWidget()


class LoadWindow(QtGui.QDialog):
    '''
    读取界面，包括 选择任务窗口 和 打开文件窗口。
    '''

    def __init__(self, parent=None):
        super(LoadWindow, self).__init__(parent)

        self.setWindowTitle("Load Window")
        self.resize(850, 550)

        # -------------------------------- create widget --------------------------------
        self.task_widget = self.createTaskWidgget()
        self.asset_widget = self.createAssetWidget()
        self.shot_widget = self.createShotWidget()
        self.tab_widget = QtGui.QTabWidget()
        # self.tab_widget.addTab(self.task_widget, "My Task")
        self.tab_widget.addTab(self.asset_widget, "Asset Task")
        self.tab_widget.addTab(self.shot_widget, "Shot Task")
        self.file_widget = FileWidget()
        self.open_btn = QtGui.QPushButton("open")

        # -------------------------------- layout --------------------------------
        main_lay = QtGui.QVBoxLayout()
        main_lay.addWidget(self.tab_widget)
        main_lay.addWidget(self.file_widget)

        bottom_lay = QtGui.QHBoxLayout()
        bottom_lay.addStretch()
        bottom_lay.addWidget(self.open_btn)
        main_lay.addLayout(bottom_lay)

        self.setLayout(main_lay)

        # -------------------------------- layout --------------------------------
        self.task_widget.task_widget.itemClicked.connect(self.task_widget.updateFileWgt)
        self.open_btn.clicked.connect(self.openFile)

    def createTaskWidgget(self):
        data = config_data.get("global").get("task_load")
        kwargs = {
            "sequence": database.assetTypes(),
            'project': prj_name,
            "type": "asset",
            "data": data
        }
        task_widget = TaskWidget(kwargs)
        return task_widget

    def createAssetWidget(self):
        data = config_data.get("global").get("asset_load")
        kwargs = {
            "sequence": database.assetTypes(),
            'project': prj_name,
            "type": "asset",
            "data": data
        }
        asset_widget = TaskWidget(kwargs)
        return asset_widget

    def createShotWidget(self):
        data = config_data.get("global").get("shot_load")
        kwargs = {
            "sequence": database.getSeqs(),
            'project': prj_name,
            "type": "shot",
            "data": data
        }
        shot_widget = TaskWidget(kwargs)
        return shot_widget

    def openFile(self):
        task_win = self.tab_widget.currentWidget()
        pprint(task_win.getSelection())



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = LoadWindow()
    win.show()
    sys.exit(app.exec_())
