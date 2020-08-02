# -*- coding:utf-8 -*-

import os
import maya.cmds as cmds
from PySide import QtGui

import swif

sw = swif._maya.Maya()


class Window(QtGui.QDialog):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.setWindowTitle("Banner Playblast")
        self.resize(400, 100)

        self._UI()

    def _UI(self):

        self.path = QtGui.QLineEdit()
        but = QtGui.QPushButton('path...')
        but.clicked.connect(self.selectOutputPath)
        but1 = QtGui.QPushButton('playbalst')
        but1.clicked.connect(self.run)

        lay2 = QtGui.QHBoxLayout()
        lay2.addWidget(self.path)
        lay2.addWidget(but)

        cameraLabel = QtGui.QLabel('Select Camera:')

        allCam = self.getCameras()

        allCam.insert(0, '')
        self.cameraCom = QtGui.QComboBox()
        self.cameraCom.addItems(allCam)
        self.cameraCom.activated.connect(self.selectCamera)

        lay1 = QtGui.QHBoxLayout()
        lay1.addWidget(cameraLabel)
        lay1.addWidget(self.cameraCom)
        lay1.addStretch(1)
        lay1.addWidget(but1)

        lay = QtGui.QVBoxLayout()
        lay.addLayout(lay2)
        lay.addLayout(lay1)

        self.setLayout(lay)

    def getCameras(self):
        allCamera = sw.getCameras(includeHidden=True)
        # print "allCamera:",allCamera
        result = []
        for cam in allCamera:
            result.append(cam['code'])
        return result

    def selectCamera(self):
        # self.cameraCom.clear()
        self.camera = self.cameraCom.currentText()

    def selectOutputPath(self):
        path = QtGui.QFileDialog.getExistingDirectory(self, 'Browse...', '')
        if path:
            movie_name = os.path.basename(cmds.file(location=1, q=1)).split(".")[0] + ".mov"
            self.path.setText(path + "\\" + movie_name)

    def run(self):
        if self.path.text():

            if not self.cameraCom.currentText():
                wgt = QtGui.QMessageBox(QtGui.QMessageBox.Information, 'Tip', 'Please select camera!')
                wgt.exec_()
                return

            import playBlast2
            reload(playBlast2)
            playBlast2.run(self.path.text(), self.camera)

            wgt = QtGui.QMessageBox(QtGui.QMessageBox.Information, 'Tip', 'Playblast successful !')
            wgt.exec_()
