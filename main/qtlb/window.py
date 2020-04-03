# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Author: RunningMan
#  @File: deploy.py
#  @Create Time: 2019/12/30 15:15
#  @Description: 调用widget.py中的基本部件，创建最终显示的窗口。
# ==============================================================
import os

import widget

reload(widget)
from widget import *

sys.path.append(r"E:\LongGong\XSYH\main")
import utilities
import engine
import nodes
import dbif
import swif
reload(utilities)
reload(engine)
reload(nodes)
reload(dbif)
reload(swif)

# ================================= Global variable =================================
config_data = engine.getConfigs()
database = dbif.CGT(config_data=config_data)
prj_name = os.environ["XSYH_PROJECT"]
sw = swif.software()


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
        self._init_wgt()

        # -------------------------- layout --------------------------
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.task_widget)

        # -------------------------- single --------------------------
        self.task_widget.itemExpanded.connect(self._update_items)
        self.task_widget.itemClicked.connect(self.__set_task_env)

    def _init_wgt(self):
        '''
        初始化 tree widget
        '''
        self.task_widget.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.task_widget.setSortingEnabled(True)
        self.task_widget.sortItems(0, QtCore.Qt.AscendingOrder)

        # 设置header label
        labels = [i.get("label") for i in self.data.get("data") if i.get("show")]
        self.task_widget.setHeaderLabs(labels)

        # 创建根节点为项目名
        root = self.task_widget.createItem(data=self.data.get("project"))
        root.setExpanded(True)
        self.task_widget.createItem(parent_item=root, data=self.data.get("sequence"), expand=True)

    def __set_task_env(self):
        '''
        set the task environment
        '''
        _data = self.getSelection()
        kwargs = {
            "XSYH_PROJECT": os.environ.get("XSYH_PROJECT") or "",
            "XSYH_SEQUENCE": _data.get("sequence") or "",
            "XSYH_SHOT": _data.get("shot") or "",
            "XSYH_TYPE": _data.get("type") or "",
            "XSYH_STEP": _data.get("step") or "",
            "XSYH_TASK": _data.get("task_name") or "",
            "XSYH_TASK_STATUS": _data.get("status") or "",
            "XSYH_ARTIST": _data.get("account") or "",
            "XSYH_TASK_ID": _data.get("task_id") or "",
        }
        utilities.setEnv(kwargs)

    def _update_items(self, item):
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
                sequence = item.parent().text(0)
                shot_task = database.getShotTask(sequence=sequence, shot=shot, load_label=True)
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
            result = self.task_widget.selectionInfo()
            result[u'sequence'] = item.parent().parent().text(0)
            result[u'shot'] = item.parent().text(0)
            task_kwargs = {
                'sequence': result[u'sequence'],
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
        self._init_wgt()

        # -------------------------- layout --------------------------
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.file_widget)

        # -------------------------- single --------------------------
        # self.file_widget.itemClicked.connect(self.__set_task_env)

    def _init_wgt(self):
        self.file_widget.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.file_widget.setSortingEnabled(True)
        self.file_widget.sortItems(0, QtCore.Qt.AscendingOrder)

        config = config_data.get("global").get("workfile_fields")

        # 创建头部名称
        self.header_labs = [i.get("label") for i in config if i.get("show")]
        self.file_widget.setHeaderLabs(self.header_labs)

    def _update_items(self, item_data):
        '''
        添加item
        @param item_data:
        '''
        self.file_widget.clear()
        file_data = engine.toShowFileMsg(item_data)
        for file_dic in file_data:
            root = QtGui.QTreeWidgetItem(self.file_widget)
            for index in range(self.file_widget.columnCount()):
                header_label = self.file_widget.headerItem().text(index)
                root.setText(index, file_dic.get(header_label, ""))

    def getSelection(self):
        '''
        得到选择的任务信息。
        @return:
        '''
        sl_info = self.file_widget.selectionInfo()
        sl_info['full_path'] = "{0}/{1}.{2}".format(sl_info['path'], sl_info['file_name'], sl_info['file_type'])
        return sl_info


class TaskLoadWindow(QtGui.QDialog):
    '''
    读取界面，包括 选择任务窗口 和 打开文件窗口。
    '''

    def __init__(self, parent=None):
        super(TaskLoadWindow, self).__init__(parent)

        self.setWindowTitle("Load Window")
        self.resize(850, 680)

        # -------------------------------- create widget --------------------------------
        self.task_widget = self._create_task_wgt()
        self.asset_widget = self._create_asset_wgt()
        self.shot_widget = self._create_shot_wgt()
        self.tab_widget = QtGui.QTabWidget()
        # self.tab_widget.addTab(self.task_widget, "My Task")
        self.tab_widget.addTab(self.asset_widget, "Asset Task")
        self.tab_widget.addTab(self.shot_widget, "Shot Task")

        self.file_widget = self._create_file_wgt()

        self.rf_comb = QtGui.QComboBox()
        self.load_set_lab = QtGui.QLabel("Loading settings:")
        self.rf_comb.addItems(["all", "none", "topOnly"])
        self.rf_comb.setMaximumWidth(70)
        self.rf_btn = QtGui.QPushButton("reference")
        self.open_btn = QtGui.QPushButton("open")

        # -------------------------------- layout --------------------------------
        main_lay = QtGui.QVBoxLayout()
        main_lay.addWidget(self.tab_widget)
        main_lay.addWidget(self.file_widget)

        bottom_lay = QtGui.QHBoxLayout()
        bottom_lay.addStretch()
        bottom_lay.addWidget(self.load_set_lab)
        bottom_lay.addWidget(self.rf_comb)
        bottom_lay.addWidget(self.rf_btn)
        bottom_lay.addWidget(self.open_btn)
        main_lay.addLayout(bottom_lay)

        self.setLayout(main_lay)

        # -------------------------------- signal --------------------------------
        self.task_widget.task_widget.itemClicked.connect(
            lambda: self.file_widget._update_items(self.tab_widget.currentWidget().getSelection()))
        self.shot_widget.task_widget.itemClicked.connect(
            lambda: self.file_widget._update_items(self.tab_widget.currentWidget().getSelection()))
        self.asset_widget.task_widget.itemClicked.connect(
            lambda: self.file_widget._update_items(self.tab_widget.currentWidget().getSelection()))
        self.rf_btn.clicked.connect(self._reference_file)
        self.open_btn.clicked.connect(self._open_file)

    def _create_task_wgt(self):
        '''
        创建个人任务窗口
        @return:
        '''
        data = config_data.get("global").get("task_load")
        kwargs = {
            "sequence": database.assetTypes(),
            'project': prj_name,
            "type": "asset",
            "data": data
        }
        task_widget = TaskWidget(kwargs)
        return task_widget

    def _create_asset_wgt(self):
        '''
        创建资产任务窗口
        @return:
        '''
        data = config_data.get("global").get("asset_load")
        kwargs = {
            "sequence": database.assetTypes(),
            'project': prj_name,
            "type": "asset",
            "data": data
        }
        asset_widget = TaskWidget(kwargs)
        return asset_widget

    def _create_shot_wgt(self):
        '''
        创建镜头任务窗口
        @return:
        '''
        data = config_data.get("global").get("shot_load")
        kwargs = {
            "sequence": database.getSeqs(),
            'project': prj_name,
            "type": "shot",
            "data": data
        }
        shot_widget = TaskWidget(kwargs)
        return shot_widget

    def _create_file_wgt(self):
        '''
        创建制作文件窗口
        @return:
        '''
        return FileWidget()

    def _open_file(self):
        file_sl = self.file_widget.getSelection()
        if file_sl:
            # print file_sl
            sw.open(file_sl['full_path'])
        else:
            print u"请选择"

    def _reference_file(self):
        file_sl = self.file_widget.getSelection()
        if file_sl:
            # print file_sl
            sw.reference(file_sl['full_path'])
        else:
            print u"请选择"


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    win = TaskLoadWindow()
    win.show()
    sys.exit(app.exec_())
