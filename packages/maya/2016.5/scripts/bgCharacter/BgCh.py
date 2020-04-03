import os
import qtlb
from qtlb import QtCore,QtGui,QtWidgets

import swif
sw = swif._maya.Maya()
import maya.cmds as cmds

import selectShotWidget
reload(selectShotWidget)

gpuModulePath = "Z:/LongGong/sequences/{seq}/{shot}/animation/approved/scenes/{seq}_{shot}_Ani_BgCharacter.abc"

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        self.setWindowTitle('BG Character Tool')
        
        self.shotWidget = selectShotWidget.SelectShotStepWidget()

        self.shotWidget.shotCom.activated.disconnect()
        self.shotWidget.stepCom.clear()
        self.shotWidget.stepCom.addItems(["Animation"])
        
        importBtn = QtWidgets.QPushButton('import')
        importBtn.clicked.connect(self._import)
        exportBtn = QtWidgets.QPushButton('export')
        exportBtn.clicked.connect(self._export)
        btnLay = QtWidgets.QHBoxLayout()
        btnLay.addStretch(1)
        btnLay.addWidget(importBtn)
        btnLay.addWidget(exportBtn)
        
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.shotWidget)
        lay.addLayout(btnLay)
        
        self.setLayout(lay)
        
    def _import(self):
        sequence = self.shotWidget.seqCom.currentText()
        shot = self.shotWidget.shotCom.currentText()
        filePath = gpuModulePath.format(seq=sequence,shot=shot)
        print "filePath:",filePath
        
        if os.path.isfile(filePath):
            sw.importGpuCache(filePath)
        else:
            QtWidgets.QMessageBox.information(self, "Warning", 'File Not Exists!')
        

    def _export(self):
        sequence = self.shotWidget.seqCom.currentText()
        shot = self.shotWidget.shotCom.currentText()
        filePath = gpuModulePath.format(seq=sequence,shot=shot)
        print "filePath:",filePath
        
        sel = cmds.ls(sl=True)
        if not sel:
            QtWidgets.QMessageBox.information(self, "Warning", 'Not Select Model!')
            return 
        
        folder = os.path.dirname(filePath)
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        sw.exportGpuCache(filePath,objects=sel)
        
        
        
        
        
        
        
        
        
