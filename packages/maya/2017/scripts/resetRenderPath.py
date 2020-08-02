# -*- coding: utf-8 -*-
try:
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtCore
except ImportError:
    from PySide import QtGui
    from PySide import QtCore    
import maya.cmds as cmds
import os


class MylineEdit(QtGui.QLineEdit):  
    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.setAcceptDrops(True)
    def dragEnterEvent(self, event):
        event.accept()
    def dropEvent(self, event):
        st = str(event.mimeData().urls())
        st = st.replace('[PySide.QtCore.QUrl', "")
        st = st.replace('[PySide2.QtCore.QUrl', "")
        st = st.replace("'), ", ",")
        st = st.replace("('file:///", "")
        st = st.replace("')]", "")
        self.setText(st)


class Datas(object):
    def __init__(self, windows):
        self._windows = windows

    def messageBox(self, name):
        QtGui.QMessageBox.about(self._windows, "Message", name)

    def okBtn(self):
        name = u"ok"
        self.messageBox(name)


class resetRenderPathUI(QtGui.QDialog):
    def __init__(self, parent=None):
        self.datas = Datas(self)
        super(resetRenderPathUI, self).__init__(parent)
        self.setWindowTitle(u"ResetRenderPath")
        self.resize(300, 100)

        self.browsePushButton = QtGui.QPushButton(u".   .   .")
        setButton = QtGui.QPushButton(u"Set path")

        self.setPath = QtGui.QLineEdit()
        self.setPath = MylineEdit()

        browseLayout = QtGui.QHBoxLayout()
        browseLayout.addWidget(self.setPath)
        browseLayout.addWidget(self.browsePushButton)

        AllLayout = QtGui.QVBoxLayout()
        AllLayout.addLayout(browseLayout)
        AllLayout.addWidget(setButton)
        self.setLayout(AllLayout)

        setButton.clicked.connect(self.set)
        setButton.clicked.connect(self.datas.okBtn)
        self.browsePushButton.clicked.connect(self.openFile)


    def set(self):
        pathName = self.setPath.text()
        cmds.workspace(fr=["images", pathName])
    
    def openFile(self):
        fileName = cmds.file(rn="Beiyong.mb")
        cmds.file(save=True,type="mayaBinary")
        if os.path.join(fileName):
            os.remove(fileName)
        openFile = QtGui.QFileDialog()
        OpenFile = openFile.getExistingDirectory(self,"choose directory","D:")  
        self.setPath.setText(unicode(OpenFile))




if __name__ == "__main__":
    resetRenderPath = resetRenderPathUI()
    resetRenderPath.show()