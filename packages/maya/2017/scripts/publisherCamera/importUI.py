import os,sys
import qtlb
import swif
sw = swif._maya.Maya()
from qtlb import QtCore,QtGui,QtWidgets

import selectShotWidget
reload(selectShotWidget)

cameraModuleList =  ["Z:/LongGong/sequences/{seq}/{shot}/camera/approved/{seq}_{shot}_camera.abc",
                 "Z:/LongGong/sequences/{seq}/{shot}/camera/approved/{seq}_{shot}_Ani_camera.abc"]

class ImportCamera(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Import Camera')
        self.shotWidget = selectShotWidget.SelectShotStepWidget()
        
        self.shotWidget.shotCom.activated.disconnect()
        self.shotWidget.stepCom.clear()
        
        importBtn = QtWidgets.QPushButton('Import Camera')
        importBtn.clicked.connect(self.importCamera)
        
        btnLay = QtWidgets.QHBoxLayout()
        btnLay.addStretch(1)
        btnLay.addWidget(importBtn)
        
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.shotWidget)
        lay.addLayout(btnLay)
        self.setLayout(lay)
        

    def importCamera(self,):
    
        sequence = self.shotWidget.seqCom.currentText()
        shot = self.shotWidget.shotCom.currentText()
        
        
        for cameraModule in cameraModuleList:
            cameraPath =cameraModule.format(seq=sequence,shot=shot)
            if os.path.exists(cameraPath):
                break
            else:
                cameraPath = ''
        
        if not cameraPath:
            print "cameraPath:",cameraPath
            QtWidgets.QMessageBox.information(self, "Warning", 'Not find camera file!\nCurrent file  module path is \n%s'%('\n'.join(cameraModuleList)))
            
        else:
            sw.importAbc(cameraPath)
            
            