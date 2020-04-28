# ==============================================================
# -*- coding: utf-8 -*-
# !/usr/bin/env python
#
#  @Author: RunningMan
#  @File: deploy.py
#  @Create Time: 2019/12/30 15:15
#  @Description: 调用widget.py中的基本部件，创建最终显示的窗口。
# ==============================================================
import glob
import os
import re

import widget

reload(widget)
from widget import *

# sys.path.append(r"E:\LongGong\XSYH\main")
import dbif
import swif
from nodes import engine
from nodes.engines import subengine

reload(dbif)
reload(subengine)

# ================================= Global variable =================================
config_data = engine.getConfigs()
database = dbif.CGT(config_data=config_data)
prj_name = os.environ["XSYH_PROJECT"]
sw = swif.software()


# ================================= Function =================================
def refreshData():
    global config_data
    config_data = engine.relaodConfigs()


def createIter(iter_data):
    '''
    创建一个迭代对象
    @param iter_data: 列表
    @return: list iterator
    '''
    return iter(sorted(iter_data))


# ================================= Class =================================
class ActionThread(QtCore.QThread):
    start = QtCore.Signal(object)
    finished = QtCore.Signal(object)

    def __init__(self, cls, parent=None):
        super(ActionThread, self).__init__(parent)
        self.cls = cls

    def run(self):
        show_step = self.cls.progressText
        self.start.emit(show_step)
        self.cls().run()
        self.finished.emit('finished')


class ShotsWidget(QtWidgets.QWidget):
    def __init__(self, engine, parent=None):
        super(ShotsWidget, self).__init__(parent)
        self._engine = engine
        self.data = config_data.get("global").get("shot_load")

        self._init_wgt()

    def _init_wgt(self):
        '''
        初始化 tree widget
        '''
        # -------------------------- widget --------------------------
        self.task_widget = MyTreeWidget()
        self.task_widget.setHeaderStyle()
        labels = ['sequence', 'status']
        self.task_widget.setHeaderLabs(labels)

        # 创建根节点为项目名
        root = self.task_widget.createItem(data=self._engine.project())
        root.setExpanded(True)
        self.task_widget.createItem(parent_item=root, data=database.getSeqs(), expand=True)

        # -------------------------- layout --------------------------
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.task_widget)

        # -------------------------- single --------------------------
        self.task_widget.itemExpanded.connect(self._update_items)

    def _update_items(self, item):
        '''
        添加 Item 的子项
        '''

        level = self.task_widget.getItemLevel(item)
        if level == 1:
            shot_ls = database.getShots(item.text(0))
            self.task_widget.createItem(parent_item=item, data=shot_ls, expand=True)

        elif level == 2:
            shot = item.text(0)
            sequence = item.parent().text(0)
            shot_task = database.getShotTask(sequence=sequence, shot=shot, load_label=True)
            self.task_widget.createItem(parent_item=item, data=shot_task, expand=False)


class TaskWidget(QtWidgets.QWidget):
    '''
    用来显示任务的窗口
    '''

    def __init__(self, data, parent=None):
        super(TaskWidget, self).__init__(parent)
        self.data = data

        # -------------------------- widget --------------------------
        self.task_widget = MyTreeWidget()
        self._init_wgt()

        # -------------------------- layout --------------------------
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.task_widget)

        # -------------------------- single --------------------------
        self.task_widget.itemExpanded.connect(self._update_items)
        self.task_widget.itemClicked.connect(self.__set_task_env)

    def _init_wgt(self):
        '''
        初始化 tree widget
        '''
        self.task_widget.setHeaderStyle()

        # 设置header label
        labels = [i.get("label") for i in self.data.get("data") if i.get("show")]
        self.task_widget.setHeaderLabs(labels)

        # 创建根节点为项目名
        root = self.task_widget.createItem(data=self.data.get("project"))
        root.setExpanded(True)
        self.task_widget.createItem(parent_item=root, data=self.data.get("sequence"), expand=True)

    def __set_task_env(self, item):
        '''
        set the task environment
        '''
        if not item.childCount():
            _data = self.getSelection()
            engine.setTaskEnv(_data)

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
        if item and not item.childCount():
            result = self.task_widget.selectionInfo()
            result[u'sequence'] = item.parent().parent().text(0)
            result[u'shot'] = item.parent().text(0)
            task_kwargs = {
                'sequence': result[u'sequence'],
                'shot': result[u'shot'],
                'step': result[u'step'],
                'task_name': result[u'task_name'],
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


class MyTaskWidget(QtWidgets.QWidget):
    '''
    用来显示任务的窗口
    '''

    def __init__(self, data, parent=None):
        super(MyTaskWidget, self).__init__(parent)
        self.data = data

        # -------------------------- widget --------------------------
        self.task_widget = MyTreeWidget()
        self._init_wgt()

        # -------------------------- layout --------------------------
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.task_widget)

        # -------------------------- single --------------------------
        self.task_widget.itemExpanded.connect(self._update_items)
        self.task_widget.itemClicked.connect(self.__set_task_env)

    def _init_wgt(self):
        '''
        初始化 tree widget
        '''
        self.task_widget.setHeaderStyle()

        # 设置header label
        labels = [i.get("label") for i in self.data.get("data") if i.get("show")]
        self.task_widget.setHeaderLabs(labels)

        self._update_items()

    def _update_items(self):
        '''
        加载任务窗口的信息
        '''
        task_ls = database.userTaskInfo()
        self.task_widget.createItem(data=task_ls)

    def __set_task_env(self, item):
        '''
        set the task environment
        '''
        if not item.childCount():
            _data = self.getSelection()
            engine.setTaskEnv(_data)

    def getSelection(self):
        '''
        @return: dict
        '''
        item = self.task_widget.currentItem()
        if item:
            result = self.task_widget.selectionInfo()

            task_kwargs = {
                'sequence': result.get(u'sequence'),
                'shot': result.get(u'shot'),
                'step': result.get(u'step'),
                'task_name': result.get(u'task_name'),
            }

            if result.get("type") == "asset":
                task_id = database.getTaskId(model="asset", **task_kwargs)
                result[u'task_id'] = task_id
                result[u'asset_type'] = result.get('type')
                result[u'shot_id'] = database.getInfoId(result.get(u'sequence'), result.get(u'shot'), model="asset")
            else:
                task_id = database.getTaskId(**task_kwargs)
                result[u'task_id'] = task_id
                result[u'shot_id'] = database.getInfoId(result.get(u'sequence'), result.get(u'shot'))

            return result

        return dict()


class FileWidget(QtWidgets.QWidget):
    '''
    用来显示文件列表的窗口
    '''

    def __init__(self, parent=None):
        super(FileWidget, self).__init__(parent)

        # -------------------------- widget --------------------------
        self.file_widget = MyTreeWidget()
        self._init_wgt()

        # -------------------------- layout --------------------------
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.file_widget)

        # -------------------------- single --------------------------
        # self.file_widget.itemClicked.connect(self.__set_task_env)

    def _init_wgt(self):
        self.file_widget.setHeaderStyle()

        config = config_data.get("global").get("workfile_fields")

        # 创建头部名称
        self.header_labs = [i.get("label") for i in config if i.get("show")]
        self.file_widget.setHeaderLabs(self.header_labs)

    def _update_items(self, item_data, work=True):
        '''
        添加item
        '''
        if item_data:
            self.file_widget.clear()
            file_data = engine.toShowFileMsg(item_data, work)
            if file_data:
                for file_dic in file_data:
                    root = QtWidgets.QTreeWidgetItem(self.file_widget)
                    for index in range(self.file_widget.columnCount()):
                        header_label = self.file_widget.headerItem().text(index)
                        root.setText(index, file_dic.get(header_label, ""))
                        root.setTextAlignment(index + 1, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
                        if header_label == 'artist':
                            item_data['name'] = file_dic['file_name'] + '.{0}'.format(file_dic['file_type'])
                            root.setText(index, database.getVersion(item_data, 'artist') or '')

    def getSelection(self):
        '''
        得到选择的文件信息。
        @return:
        '''
        sl_info = self.file_widget.selectionInfo()
        if sl_info:
            sl_info['full_path'] = "{0}/{1}.{2}".format(sl_info['path'], sl_info['file_name'], sl_info['file_type'])
            return sl_info
        else:
            return False


class DescriptionWidget(QtWidgets.QComboBox):
    '''
    用来显示文件描述窗口
    '''

    def __init__(self, _engine, parent=None):
        super(DescriptionWidget, self).__init__(parent)
        self._engine = _engine
        self.updateItems()

    def updateItems(self):
        '''更新文件描述的下拉窗口'''
        self.addItems(engine.descriptionItem(self._engine.getStepConfig()))

    def getSelection(self):
        '''得到当前的选择'''
        return self.currentText()


class SelectTaskWindow(QtWidgets.QDialog):
    '''
    读取界面，包括 选择任务窗口 和 打开文件窗口。
    '''

    # if sw.app() == "maya":
    #     parent_win = sw.getMayaWindow()
    # else:
    #     parent_win = None

    def __init__(self, _engine, parent=None):
        super(SelectTaskWindow, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 窗口置顶
        self.setWindowTitle("Select Task Window")
        self.resize(850, 680)

        self._engine = _engine

        # -------------------------------- create widget --------------------------------
        # 任务预览窗口
        self.task_widget = self._createTaskWgt()
        self.asset_widget = self._createAssetWgt()
        self.shot_widget = self._createShotWgt()
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.task_widget, "My Task")
        self.tab_widget.addTab(self.asset_widget, "Asset Task")
        self.tab_widget.addTab(self.shot_widget, "Shot Task")

        # 文件预览窗口
        self.submit_file_widget = self.create_file_wgt()
        self.publish_file_widget = self.create_file_wgt()
        self.tab_widget1 = QtWidgets.QTabWidget()
        self.tab_widget1.addTab(self.submit_file_widget, "Submit File")
        self.tab_widget1.addTab(self.publish_file_widget, "Publish File")

        # 底部控件
        self.new_btn = QtWidgets.QPushButton('New Scene')
        self.apply_btn = QtWidgets.QPushButton('Apply Materials')
        self.apply_btn.setVisible(False)
        self.rf_comb = QtWidgets.QComboBox()
        self.load_set_lab = QtWidgets.QLabel("Loading settings:")
        self.rf_comb.addItems(["all", "none", "topOnly"])
        self.rf_comb.setMaximumWidth(70)
        self.rf_btn = QtWidgets.QPushButton("Reference")
        self.open_btn = QtWidgets.QPushButton("Open")

        # 垂直分割窗口
        ver_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        ver_splitter.addWidget(self.tab_widget)
        ver_splitter.addWidget(self.tab_widget1)
        ver_splitter.setStretchFactor(0, 1)
        ver_splitter.setStretchFactor(1, 1)

        # -------------------------------- layout --------------------------------
        self.main_lay = QtWidgets.QVBoxLayout(self)
        self.main_lay.addWidget(ver_splitter)

        self.bottom_lay = QtWidgets.QHBoxLayout()
        self.bottom_lay.addWidget(self.new_btn)
        self.bottom_lay.addWidget(self.apply_btn)
        self.bottom_lay.addStretch()
        self.bottom_lay.addWidget(self.load_set_lab)
        self.bottom_lay.addWidget(self.rf_comb)
        self.bottom_lay.addWidget(self.rf_btn)
        self.bottom_lay.addWidget(self.open_btn)
        self.main_lay.addLayout(self.bottom_lay)

        # -------------------------------- signal --------------------------------
        self.task_widget.task_widget.itemClicked.connect(
            lambda: self.submit_file_widget._update_items(self.task_widget.getSelection()))
        self.task_widget.task_widget.itemClicked.connect(
            lambda: self.publish_file_widget._update_items(self.task_widget.getSelection(), work=False))

        self.asset_widget.task_widget.itemClicked.connect(
            lambda: self.submit_file_widget._update_items(self.asset_widget.getSelection()))
        self.asset_widget.task_widget.itemClicked.connect(
            lambda: self.publish_file_widget._update_items(self.asset_widget.getSelection(), work=False))

        self.shot_widget.task_widget.itemClicked.connect(
            lambda: self.submit_file_widget._update_items(self.shot_widget.getSelection()))
        self.shot_widget.task_widget.itemClicked.connect(
            lambda: self.publish_file_widget._update_items(self.shot_widget.getSelection(), work=False))

        self.publish_file_widget.file_widget.itemClicked.connect(self.showApplyBtn)

        self.new_btn.clicked.connect(self._new_scene)
        self.apply_btn.clicked.connect(self.applyMaterials)
        self.rf_btn.clicked.connect(self._reference_file)
        self.open_btn.clicked.connect(self._open_file)

    def _createTaskWgt(self):
        '''
        创建个人任务窗口
        @return:
        '''
        data = config_data.get("global").get("task_load")
        kwargs = {
            'project': prj_name,
            "type": "asset",
            "data": data
        }
        task_widget = MyTaskWidget(kwargs)
        return task_widget

    def _createAssetWgt(self):
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

    def _createShotWgt(self):
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

    def create_file_wgt(self):
        '''
        创建制作文件窗口
        @return:
        '''
        return FileWidget()

    def getTaskSelectionInfo(self):
        file_sl = self.tab_widget.currentWidget().getSelection()
        if file_sl:
            return file_sl

        return None

    def getTaskCurrentTab(self):
        return self.tab_widget.currentIndex()

    def getFileSelectionInfo(self):
        file_sl = self.tab_widget1.currentWidget().getSelection()
        if file_sl:
            return file_sl

        return None

    def getFileCurrentTab(self):
        return self.tab_widget1.currentIndex()

    def _new_scene(self):
        '''
        新建场景，初始化一些设置
        '''
        if self.getTaskSelectionInfo():
            engine.WorkfileManager('workfile_new')
        self.close()

    def _open_file(self):
        file_sl = self.getFileSelectionInfo()
        if file_sl:
            # engine.WorkfileManager('workfile_new')
            sw.open(file_sl['full_path'], loadReferenceDepth=self.rf_comb.currentText(), force=True)
            self.close()
        else:
            print u"请选择"

    def _reference_file(self):
        file_sl = self.tab_widget1.currentWidget().getSelection()
        if file_sl:
            sw.reference(file_sl['full_path'], loadReferenceDepth=self.rf_comb.currentText())
            self.close()
        else:
            print u"请选择"

    def showApplyBtn(self):
        if self.getFileCurrentTab() == 1:
            sel_info = self.getTaskSelectionInfo()
            if sel_info.get('step') == 'Texture':
                self.apply_btn.setVisible(True)
        else:
            self.apply_btn.setVisible(False)

    def applyMaterials(self):
        if self.getFileCurrentTab() == 1:
            sel_info = self.getFileSelectionInfo()
            engine.applyMaterials(sel_info)


class CommentWidget(QtWidgets.QDialog):
    '''
    添加描述的窗口
    '''

    def __init__(self, _engine, title, parent=None):
        super(CommentWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 窗口置顶
        self.setWindowTitle('{} File'.format(title))
        self.resize(300, 400)

        self._engine = _engine

        elements_frm = self.createTextWidget()
        self._publishBtn = QtWidgets.QPushButton(title)
        self._publishBtn.setDisabled(True)

        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        self._progressLab = QtWidgets.QLabel('Progress')
        self._progressBar = QtWidgets.QProgressBar()
        self._progressBar.setRange(0, 100)
        self._lay1 = QtWidgets.QHBoxLayout()
        self._lay1.addStretch(1)
        self._lay1.addWidget(self._publishBtn)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(elements_frm)

        self._lay = QtWidgets.QVBoxLayout()
        self._lay.addWidget(splitter)
        self._lay.addLayout(self._lay1)
        self._lay.addWidget(line)
        self._lay.addWidget(self._progressLab)
        self._lay.addWidget(self._progressBar)

        self.setLayout(self._lay)

        self._comments_text.textChanged.connect(lambda: self._publishBtn.setDisabled(False))
        self._publishBtn.clicked.connect(self.publish)

    def createTextWidget(self):
        frm = QtWidgets.QFrame()
        self._step_lab = QtWidgets.QLabel('{0}/{1}/{2}'.format(self._engine.task().get('sequence'),
                                                               self._engine.task().get('shot'),
                                                               self._engine.task().get('step')))
        self._step_lab.setFont(QtGui.QFont("Timers", 15))
        self._comments_lab = QtWidgets.QLabel('Comments:')
        self._comments_text = QtWidgets.QPlainTextEdit()
        lay = QtWidgets.QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._step_lab)
        lay.addWidget(self._comments_lab)
        lay.addWidget(self._comments_text)
        frm.setLayout(lay)
        return frm

    def publish(self):
        comments = self._comments_text.toPlainText()
        self._engine.description = comments  # 添加 description 属性
        self._engine().bindAttr()
        self.close()


class CommentWithSelectAssetWidget(QtWidgets.QDialog):
    '''
    带有可以选择物体的描述窗口
    '''

    def __init__(self, _engine, title, parent=None):
        super(CommentWithSelectAssetWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 窗口置顶
        self.setWindowTitle('{} File'.format(title))
        self.resize(500, 600)

        self._engine = _engine

        elements_lay = self._createTextWidget()
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        self.sel_char_ckb = QtWidgets.QCheckBox("Select Character")
        self.sel_char_ckb.stateChanged.connect(self.selectChar)
        self.sel_none_ckb = QtWidgets.QCheckBox("Deselect")
        self.sel_none_ckb.stateChanged.connect(self.deselect)
        self._publishBtn = QtWidgets.QPushButton(title)
        self._publishBtn.setDisabled(True)
        self._progressLab = QtWidgets.QLabel('Progress')
        self._progressBar = QtWidgets.QProgressBar()
        self._progressBar.setRange(0, 100)

        self._lay1 = QtWidgets.QHBoxLayout()
        self._lay1.addStretch(1)
        self._lay1.addWidget(self._publishBtn)
        check_lay = QtWidgets.QHBoxLayout()
        check_lay.addWidget(self.sel_char_ckb)
        check_lay.addWidget(self.sel_none_ckb)
        check_lay.addStretch(1)
        self._lay = QtWidgets.QVBoxLayout(self)
        self._lay.addLayout(elements_lay)
        self._lay.addLayout(check_lay)
        self._lay.addLayout(self._lay1)
        self._lay.addWidget(line)
        self._lay.addWidget(self._progressLab)
        self._lay.addWidget(self._progressBar)

        self._comments_text.textChanged.connect(lambda: self._publishBtn.setDisabled(False))
        self._publishBtn.clicked.connect(self.publish)

    def _createTextWidget(self):
        self._step_lab = QtWidgets.QLabel('{0}/{1}/{2}'.format(self._engine.task().get('sequence', ''),
                                                               self._engine.task().get('shot', ''),
                                                               self._engine.task().get('step', '')))
        self._step_lab.setFont(QtGui.QFont("Timers", 15))
        self.asset_win = SceneAssetWidget()

        self._comments_lab = QtWidgets.QLabel('Comments:')
        self._comments_text = QtWidgets.QPlainTextEdit()
        _comment_wgt = QtWidgets.QWidget()
        lay1 = QtWidgets.QVBoxLayout()
        lay1.addWidget(self._comments_lab)
        lay1.addWidget(self._comments_text)
        _comment_wgt.setLayout(lay1)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(self.asset_win)
        splitter.addWidget(_comment_wgt)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        lay = QtWidgets.QVBoxLayout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._step_lab)
        lay.addWidget(splitter)
        return lay

    def selectChar(self):
        it = QtWidgets.QTreeWidgetItemIterator(self.asset_win._data_tree)

        while it:
            item = it.value()
            if not item:
                break

            name = item.text(0)
            obj = item.text(1)
            if obj:
                if name.startswith('char'):
                    if self.sel_char_ckb.isChecked():
                        item.setCheckState(0, QtCore.Qt.Checked)
                    else:
                        item.setCheckState(0, QtCore.Qt.Unchecked)
                else:
                    item.setCheckState(0, QtCore.Qt.Unchecked)

            it += 1

    def deselect(self):
        it = QtWidgets.QTreeWidgetItemIterator(self.asset_win._data_tree)

        while it:
            item = it.value()
            if not item:
                break

            name = item.text(0)
            obj = item.text(1)
            if obj:
                item.setCheckState(0, QtCore.Qt.Unchecked)

            it += 1

    def publish(self):
        comments = self._comments_text.toPlainText()
        # self._engine.description = comments  # 添加 description 属性
        self._engine.setParm('description', comments)  # 添加 description 属性
        self._engine.setParm('objects', [i.text(1) for i in self.asset_win.getCheckedItems()])  # 添加选择的物体属性
        self._engine().bindAttr()
        self.close()


class SubmitWidget(QtWidgets.QDialog):
    '''
    提交文件的窗口
    '''

    def __init__(self, engine, parent=None):
        super(SubmitWidget, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 窗口置顶
        self.setWindowTitle("Submit File")
        self.resize(850, 500)

        self._engine = engine

        self.sel_task_wgt = SelectTaskWindow('')
        self.asset_widget = self.sel_task_wgt._createAssetWgt()
        self.shot_widget = self.sel_task_wgt._createShotWgt()
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.asset_widget, "Asset Task")
        self.tab_widget.addTab(self.shot_widget, "Shot Task")

        self.next_btn = QtWidgets.QPushButton('Submit')
        self.btn_lay = QtWidgets.QHBoxLayout()
        self.btn_lay.addStretch()
        self.btn_lay.addWidget(self.next_btn)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.tab_widget)
        lay.addLayout(self.btn_lay)

        self.asset_widget.task_widget.itemClicked.connect(self.changeDesItem)
        self.shot_widget.task_widget.itemClicked.connect(self.changeDesItem)
        self.next_btn.clicked.connect(self.next)

    def changeDesItem(self, item):
        '''
        更新文件描述下拉窗口
        '''
        if engine.descriptionItem(self._engine.getStepConfig()):
            if not hasattr(self, 'des_comp'):
                if not item.childCount():
                    self.des_lab = QtWidgets.QLabel('File description:')
                    self.des_comp = DescriptionWidget(self._engine)
                    self.des_comp.setMinimumWidth(50)
                    self.des_comp.setMinimumHeight(25)
                    self.btn_lay.insertWidget(0, self.des_lab)
                    self.btn_lay.insertWidget(1, self.des_comp)
            else:
                self.des_comp.clear()
                self.des_comp.updateItems()

    def next(self):
        sel_info = self.tab_widget.currentWidget().getSelection()
        if sel_info:
            if hasattr(self, 'des_comp'):
                self._engine.file_description = self.des_comp.currentText()  # 添加 file_description
            self.close()
            # 打开检查窗口
            s = CheckingWidget(subengine.CheckingEngine, self._engine, self)
            s.show()
        else:
            print u'请选择环节'


class PublishWidget(QtWidgets.QDialog):
    '''
    发布文件的窗口
    '''

    def __init__(self, engine, parent=None):
        super(PublishWidget, self).__init__(parent)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)  # 窗口置顶
        self.setWindowTitle("Publish File")
        self.resize(850, 500)
        self._engine = engine

        self.sel_task_wgt = SelectTaskWindow('')
        self.asset_widget = self.sel_task_wgt._createAssetWgt()
        self.shot_widget = self.sel_task_wgt._createShotWgt()
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.asset_widget, "Asset Task")
        self.tab_widget.addTab(self.shot_widget, "Shot Task")

        self.next_btn = QtWidgets.QPushButton('Publish')
        self.btn_lay = QtWidgets.QHBoxLayout()
        self.btn_lay.addStretch()
        self.btn_lay.addWidget(self.next_btn)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.tab_widget)
        lay.addLayout(self.btn_lay)

        self.next_btn.clicked.connect(self.next)

    def next(self):
        sel_info = self.tab_widget.currentWidget().getSelection()
        if sel_info:
            self.close()
            # 打开检查窗口
            s = CheckingWidget(subengine.CheckingEngine, self._engine, self)
            s.show()
        else:
            print u'请选择环节'


class CheckingWidget(QtWidgets.QDialog):
    '''
    检查窗口
    '''

    def __init__(self, _engine, par_engine='', parent=None):
        super(CheckingWidget, self).__init__(parent)
        self.resize(800, 550)
        self._engine = _engine
        self._par_engine = par_engine
        self.setWindowTitle("check and fix >>> {}".format(self._engine.task().get('step')))

        self._init_ui()

    def _init_ui(self):
        # create check widget
        import check_widget
        reload(check_widget)
        from check_widget import CheckWidget
        self.check_win = CheckWidget(self._engine, self)
        self.next_btn = QtWidgets.QPushButton('Next')
        self.next_btn.setEnabled(False)

        # create layout
        lay2 = QtWidgets.QHBoxLayout()
        lay2.addStretch()
        lay2.addWidget(self.next_btn)
        main_lay = QtWidgets.QVBoxLayout(self)
        main_lay.addWidget(self.check_win)
        main_lay.addLayout(lay2)

        self.next_btn.clicked.connect(self.nextAction)

    def nextAction(self):
        self.close()
        # 打开提交窗口
        if self._par_engine.__name__ == 'SubmitEngine':
            wgt_name = self._par_engine.getStepConfig().get('submit_widget', 'CommentWidget')
            this_module = sys.modules[__name__]  # __name__表示当前文件
            print getattr(this_module, wgt_name)
            s = getattr(this_module, wgt_name)(self._par_engine, 'Submit')
        else:
            wgt_name = self._par_engine.getStepConfig().get('publisher_widget', 'CommentWidget')
            this_module = sys.modules[__name__]  # __name__表示当前文件
            s = getattr(this_module, wgt_name)(self._par_engine, 'Publish')
        s.show()


class SceneAssetWidget(QtWidgets.QWidget):
    '''
    选择场景物体的窗口
    '''

    def __init__(self, parent=None):
        super(SceneAssetWidget, self).__init__(parent)
        self._init_wgt()

    def _init_wgt(self):
        self._data_tree = self.createDataTree()
        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self._data_tree)

    def createDataTree(self):
        _init_Data = sw.getReferenceObjects()
        data_tree = MyTreeWidget()
        data_tree.setHeaderStyle()()
        data_tree.setHeaderLabels(['asset', 'object'])
        if _init_Data:
            for item in _init_Data:
                first_root = QtWidgets.QTreeWidgetItem(data_tree)
                first_root.setExpanded(True)
                duplicate_num = re.findall(r'\d', item.get('namespace'))
                if duplicate_num:
                    first_root.setText(0, item.get('name').split('_')[0] + str(duplicate_num[0]))
                else:
                    first_root.setText(0, item.get('name').split('_')[0])
                second_root = QtWidgets.QTreeWidgetItem(first_root)
                second_root.setCheckState(0, QtCore.Qt.Checked)
                second_root.setText(0, item.get('name'))
                second_root.setText(1, item.get('full_name'))
        return data_tree

    def getCheckedItems(self):
        return self._data_tree.getCheckedItems()


class AssemblyDataWidget(QtWidgets.QWidget):
    def __init__(self, engine, parent=None):
        super(AssemblyDataWidget, self).__init__(parent)

        self._engine = engine
        self.task = engine.task()
        self.database = engine.database()

        self._init_wgt()

    def _init_wgt(self):
        self.dataTree = MyTreeWidget()
        self.dataTree.setHeaderStyle()

        self.headerLabel = ['asset_type', 'asset_name', 'abc_name', 'mat_name', 'mat_path', 'map_name', 'type']
        self.dataTree.setHeaderLabels(self.headerLabel)

        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.dataTree)
        self.setLayout(lay)

        # self.allData = self.displayData()

    def getShotLinkedAssets(self, assetType=[]):
        '''
        返回到镜头在CGT上link的资产信息
        @param assetType:
        @return:
        '''
        shotInfo = {
            'id': self.task['shot_id'],
            'project': self._engine.project()
        }

        assetInfo = self.database.getShotLinkedAssets(shotInfo)
        if assetType:
            lis = []
            for astInfo in assetInfo:
                if astInfo['sequence'] in assetType:
                    lis.append(astInfo)
            return lis
        return assetInfo

    def getCameraCahe(self, seq, shot):
        '''
        得到相机缓存文件
        '''
        result = []
        cameraPath = 'Z:/LongGong/sequences/{seq}/{shot}/camera/approved/{seq}_{shot}_camera.abc'.format(seq=seq,
                                                                                                         shot=shot)
        asset_type = 'camera'
        asset_name = 'camera'

        if not os.path.exists(cameraPath):
            abc_path = ''
            abc_name = ''
        else:
            abc_path = cameraPath
            abc_name = os.path.basename(cameraPath)

        info = {'asset_type': asset_type,
                'asset_name': asset_name,
                'abc_path': abc_path,
                'abc_name': abc_name,
                'type': 'Camera'}

        result.append(info)
        return result

    def splitFileName(self, file_name):
        asset_re = re.search('.*(\\prop[A-Za-z]+)|(\\set[A-Za-z]+)|(\\char[A-Za-z]+)', file_name)
        if asset_re:
            if asset_re.groups()[0]:
                asset_name = asset_re.groups()[0]
                asset_type = 'prop'
            elif asset_re.groups()[1]:
                asset_name = asset_re.groups()[1]
                asset_type = 'set'
            elif asset_re.groups()[2]:
                asset_name = asset_re.groups()[2]
                asset_type = 'char'
            else:
                asset_name = ''
                asset_type = ''
            return asset_name, asset_type

        return '', ''

    def getSetCache1(self, seq):
        '''
        拿到Z:/LongGong/assets/set/{asset}/model/cache文件夹下"{asset}_nCloth.abc"文件
        '''
        result = []

        # 镜头所link的资产
        abc_path = "Z:/LongGong/sequences/{0}/nCloth/cache/{1}_prop*_nCloth*.abc"
        mapping_path_format = "Z:/LongGong/assets/{0}/{1}/surface/approved/{2}_tex_highTex_mapping.json"

        shot_info = {
            'id': self.task['shot_id'],
            'project': self._engine.project()
        }
        asset_info = self.database.getShotLinkedAssets(shot_info)

        _set = [x['name'] for x in asset_info if x['type_name'] == "set"]
        for i in _set:
            allAbc2 = glob.glob(abc_path.format(seq, i))
            for abc_path in allAbc2:
                abc_path = abc_path.replace('\\', '/')
                abc_name = os.path.basename(abc_path)

                file_name = os.path.basename(abc_path).split('.')[0]
                asset_task_name = "_".join(file_name.split('_')[1:-1])
                asset_name = asset_task_name.split("_")[0]
                num = re.findall(r'\d+$', asset_task_name)

                if num:
                    l = len(num[0])
                    asset_task_name = asset_task_name[:-l]

                if asset_task_name.startswith('char'):
                    asset_type = 'char'
                elif asset_task_name.startswith('set'):
                    asset_type = 'set'
                elif asset_task_name.startswith('prop'):
                    asset_type = 'prop'
                else:
                    asset_type = ''

                mapping_path = mapping_path_format.format(asset_type, asset_name, asset_task_name)
                mapping_name = os.path.basename(mapping_path)
                if not os.path.exists(mapping_path):
                    mapping_path = ''
                    mapping_name = ''

                mat_path = mapping_path.replace('_mapping.json', '.ma')
                mat_name = os.path.basename(mapping_path)
                if not os.path.exists(mat_path):
                    mat_path = ''
                    mat_name = ''

                info = {'abc_path': abc_path,
                        'abc_name': abc_name,
                        'asset_type': asset_type,
                        'asset_name': asset_name,
                        'map_path': mapping_path,
                        'map_name': mapping_name,
                        'mat_path': mat_path,
                        'mat_name': mat_name,
                        'type': 'nCloth'}
                result.append(info)

        return result

    def getSetCache(self, seq):
        result = []
        lighting_rig_path = 'Z:/LongGong/sequences/{sequence}/lightingRig/approved/scenes/{sequence}_*_lighting_rig.mb'.format(
            sequence=seq)
        getFiles = glob.glob(lighting_rig_path)
        if not getFiles:
            return []

        for f in getFiles:
            light_set_path = f.replace('\\', '/')

            abc_path = light_set_path
            abc_name = os.path.basename(light_set_path)

            setType = abc_name.split('_')[1]

            info = {'abc_path': abc_path,
                    'abc_name': abc_name,
                    'asset_type': 'set',
                    'asset_name': 'Not Link',
                    'map_path': 'Not Link',
                    'map_name': 'Not Link',
                    'mat_path': 'Not Link',
                    'mat_name': 'Not Link',
                    'type': 'LightingRig',
                    'setType': setType}

            result.append(info)

        return result

    def getNClothCache(self, seq, shot):
        result = []
        cache_path = 'Z:/LongGong/sequences/{seq}/{shot}/Cache/nCloth/approved/*.abc'.format(seq=seq, shot=shot)
        mapping_path_format = "Z:/LongGong/assets/{asset_type}/{asset_name}/surface/approved/{asset_name}_tex_highTex_mapping.json"
        all_abc = glob.glob(cache_path)
        for abc_path in all_abc:
            abc_path = abc_path.replace('\\', '/')
            abc_name = os.path.basename(abc_path)

            file_name = os.path.basename(abc_path).split('.')[0]
            asset_name, asset_type = self.splitFileName(file_name)
            mapping_path = mapping_path_format.format(asset_type=asset_type, asset_name=asset_name)
            mapping_name = os.path.basename(mapping_path)
            if not os.path.exists(mapping_path):
                mapping_path = ''
                mapping_name = ''

            mat_path = mapping_path.replace('_mapping.json', '.ma')
            mat_name = os.path.basename(mat_path)
            if not os.path.exists(mat_path):
                mat_path = ''
                mat_name = ''

            info = {'abc_path': abc_path,
                    'abc_name': abc_name,
                    'asset_type': asset_type,
                    'asset_name': asset_name,
                    'map_path': mapping_path,
                    'map_name': mapping_name,
                    'mat_path': mat_path,
                    'mat_name': mat_name,
                    'type': 'nCloth'}

            result.append(info)

        return result

    def getshotFinalCache(self, seq, shot):
        result = []
        module_path = 'Z:/LongGong/sequences/{seq}/{shot}/Cache/shotFinaling/approved/*.abc'.format(seq=seq, shot=shot)
        mapping_path_format = "Z:/LongGong/assets/{asset_type}/{asset_name}/surface/approved/{asset_name}_tex_highTex_mapping.json"
        allAbc2 = glob.glob(module_path)

        for abc_path in allAbc2:
            abc_path = abc_path.replace('\\', '/')
            abc_name = os.path.basename(abc_path)

            file_name = os.path.basename(abc_path).split('.')[0]
            asset_name, asset_type = self.splitFileName(file_name)

            mapping_path = mapping_path_format.format(asset_type=asset_type, asset_name=asset_name)
            mapping_name = os.path.basename(mapping_path)
            if not os.path.exists(mapping_path):
                mapping_path = ''
                mapping_name = ''

            mat_path = mapping_path.replace('_mapping.json', '.ma')
            mat_name = os.path.basename(mat_path)
            if not os.path.exists(mat_path):
                mat_path = ''
                mat_name = ''

            info = {'abc_path': abc_path,
                    'abc_name': abc_name,
                    'asset_type': asset_type,
                    'asset_name': asset_name,
                    'map_path': mapping_path,
                    'map_name': mapping_name,
                    'mat_path': mat_path,
                    'mat_name': mat_name,
                    'type': 'SF'}

            result.append(info)

        return result

    def getSeqNclothCache(self, seq):
        '''
        拿到Z:\LongGong\sequences\{Seq}\nCloth\cache文件夹下".abc"文件
        '''
        result = []
        module_path = 'Z:/LongGong/sequences/{seq}/nCloth/cache/*.abc'.format(seq=seq)
        mapping_path_format = "Z:/LongGong/assets/{asset_type}/{asset_name}/surface/approved/{asset_name}_tex_highTex_mapping.json"
        allAbc = glob.glob(module_path)

        for abc_path in allAbc:
            abc_path = abc_path.replace('\\', '/')
            abc_name = os.path.basename(abc_path)

            file_name = os.path.basename(abc_path).split('.')[0]
            asset_name, asset_type = self.splitFileName(file_name)

            mapping_path = mapping_path_format.format(asset_type=asset_type, asset_name=asset_name).replace("//", "/")
            mapping_name = os.path.basename(mapping_path)
            if not os.path.exists(mapping_path):
                mapping_path = ''
                mapping_name = ''

            mat_path = mapping_path.replace('_mapping.json', '.ma')
            mat_name = os.path.basename(mat_path)
            if not os.path.exists(mat_path):
                mat_path = ''
                mat_name = ''

            info = {'abc_path': abc_path,
                    'abc_name': abc_name,
                    'asset_type': asset_type,
                    'asset_name': asset_name,
                    'map_path': mapping_path,
                    'map_name': mapping_name,
                    'mat_path': mat_path,
                    'mat_name': mat_name,
                    'type': 'nCloth'}

            result.append(info)

        return result

    def getAssemblyData(self):
        seq = self.task['sequence']
        shot = self.task['shot']

        # camera abc
        cameraInfo = self.getCameraCahe(seq, shot)

        # nCloth abc
        nClothInfo = self.getNClothCache(seq, shot)

        # shot final abc
        sFInfo = self.getshotFinalCache(seq, shot)

        # set abc
        setInfo = self.getSetCache(seq)

        # set nCloth abc
        setInfo1 = self.getSetCache1(seq)

        # set Sequence nCloth abc
        setInfo2 = self.getSeqNclothCache(seq)

        return cameraInfo + nClothInfo + setInfo + sFInfo + setInfo1 + setInfo2

    def displayData(self):
        self.dataTree.clear()
        data = self.getAssemblyData()
        self.allItem = []
        for inf in data:
            item = QtWidgets.QTreeWidgetItem(self.dataTree)

            for i in xrange(len(self.headerLabel)):
                label = self.headerLabel[i]

                if inf['asset_type'] == 'camera':
                    item.setText(i, inf.get(label))
                else:
                    item.setText(i, inf.get(label, '------'))
                item.setSizeHint(i, QtCore.QSize(500, 25))

            item.setCheckState(0, QtCore.Qt.Checked)
            item.info = inf
            self.allItem.append(item)

        return data

    def getSelectData(self):
        data = []
        for item in self.allItem:
            if item.checkState(0) == QtCore.Qt.Checked:
                data.append(item.info)
        return data


class SceneAssembly(QtWidgets.QDialog):

    def __init__(self, engine, parent=None):
        super(SceneAssembly, self).__init__(parent)
        self.resize(800, 550)
        self.setWindowTitle('Assembly Scene')
        self._engine = engine

        self._init_wgt()

    def _init_wgt(self):
        self.shot_wgt = ShotsWidget(self._engine)
        self.dataWidget = AssemblyDataWidget(self._engine)

        assemble_btn = QtWidgets.QPushButton('Assembly')
        assemble_btn.clicked.connect(self.assembly)

        btnLay  = QtWidgets.QHBoxLayout()
        btnLay.addStretch(1)
        btnLay.addWidget(assemble_btn)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(self.shot_wgt)
        lay.addWidget(self.dataWidget)
        lay.addLayout(btnLay)

        self.setLayout(lay)

        self.shot_wgt.task_widget.item.clicked.connect(lambda: self.shot_wgt.task_widget.displayData(data))

    def _selectShot(self, info):
        if info:
            # self.engine.setParm('shot',info)
            self.engine.setExtraContext(info)
            info['shot_id'] = info['id']
            info['shot'] = info['code']
            self.dataWidget.task = info
            self.dataWidget.displayData()

            info['step'] = os.environ['PKMG_STEP']
            # plcr.setEnv(info)

    def assembly(self):
        allData = self.dataWidget.getSelectData()
        self.engine.assemble(allData)

        QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, 'Message', 'Assembly Finished !').exec_()


if __name__ == '__main__':
    app = QtWidgets.QAPPliction([])
    win = SceneAssetWidget()
    win.show()
    app.exec_()
