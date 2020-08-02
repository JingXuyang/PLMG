import os,sys
import qtlb

from qtlb import QtCore,QtGui,QtWidgets

import selectShotWidget
reload(selectShotWidget)

ModulePath = 'Z:/LongGong/sequences/{sequence}/Seq_Camera/{sequence}_camera.mb'
import swif
sw = swif._maya.Maya()

class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        self.resize(400,50)
        #
        self.pathLine = QtWidgets.QLineEdit()
        
        #
        self.shotWidget = selectShotWidget.SelectShotStepWidget()
        self.shotWidget.seqCom.activated.disconnect()
        self.shotWidget.seqCom.activated.connect(self.setExportPath)
        
        self.shotWidget.shotLabel.hide()
        self.shotWidget.shotCom.hide()
        self.shotWidget.stepLabel.hide()
        self.shotWidget.stepCom.hide()
        
        exportBtn = QtWidgets.QPushButton('Export Camera')
        exportBtn.clicked.connect(self.run)
        
        lay1 = QtWidgets.QHBoxLayout()
        lay1.addWidget(self.shotWidget)
        lay1.addSpacing(50)
        lay1.addWidget(exportBtn)
        
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.pathLine)
        lay.addLayout(lay1)
        
        self.setLayout(lay)
        
    
    def exportAllCamera(self,path):
        import maya.cmds as cmds
        allCamera = sw.getCameras(includeHidden=True)
        camList = []
        for cam in allCamera:
            camList.append(cam['full_path'])
        
        cmds.select(camList)
        sw.exportSelected(path)
        cmds.select(clear=True)
        
    def setExportPath(self,path):
        seq = self.shotWidget.seqCom.currentText()
        path = ModulePath.format(sequence=seq)
        self.pathLine.setText(path)
        
    def run(self):
        path = self.pathLine.text()
        # export camera
        
        dirPath = os.path.dirname(path)
        if not os.path.exists(dirPath):
            os.makedirs(dirPath)
            
        self.exportAllCamera(path)
        
        
        
        
        