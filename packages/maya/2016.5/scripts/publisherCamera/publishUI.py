
try:
    from PySide import QtGui as QtWidgets
    from PySide import QtCore
    
except:
    from PySide2 import QtWidgets,QtCore,QtGui



import publishCam
reload(publishCam)

import maya.OpenMayaUI as omui
import shiboken
mayaWindowPtr = omui.MQtUtil.mainWindow()
mayaWindow = shiboken.wrapInstance(long(mayaWindowPtr),QtWidgets.QWidget)

import swif
sw = swif._maya.Maya()

class UI(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self,mayaWindow)
        
        self.setWindowTitle('Publish Camera')
        
        self.setParent(mayaWindow)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.seqCom = QtWidgets.QComboBox()
        self.shotCom = QtWidgets.QComboBox()
        
        seqList = self.getSequences()
        self.seqCom.addItems(seqList)
        #self.seqCom.currentIndexChanged.connect(self.setShot)
        self.seqCom.activated.connect(self.setShot)
        
        comlay = QtWidgets.QHBoxLayout()
        comlay.addWidget(self.seqCom)
        comlay.addWidget(self.shotCom)
        
        allCam = self.getCameras()
        
        allCam.insert(0,'')
        self.cameraCom = QtWidgets.QComboBox()
        self.cameraCom.addItems(allCam)
        
        self.bakeCamCheck = QtWidgets.QCheckBox('Bake')
        
        pubBtn = QtWidgets.QPushButton('Publish')
        pubBtn.clicked.connect(self.publish)
        
        btnLay = QtWidgets.QHBoxLayout()
        #btnLay.addWidget(self.bakeCamCheck)
        btnLay.addWidget(self.cameraCom)
        btnLay.addStretch(1)
        btnLay.addWidget(pubBtn)
        

        lay = QtWidgets.QVBoxLayout()
        lay.addLayout(comlay)
        lay.addLayout(btnLay)
        self.setLayout(lay)
        self.resize(300,130)
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    def getCameras(self):
        allCamera = sw.getCameras(includeHidden=True)
        #print "allCamera:",allCamera
        result = []
        for cam in allCamera:
            result.append(cam['code'])
        return result
    
    
    def setShot(self):
        self.shotCom.clear()
        seq = self.seqCom.currentText()
        allShots = self.getShots(seq)
        
        self.shotCom.addItems(allShots)
        
        
        
    def getSequences(self):
        return publishCam.getSequences()
    
    def getShots(self,seq):
        return publishCam.getShots(seq=seq)
        
        
    def publish(self):
        
        seq = self.seqCom.currentText()
        shot = self.shotCom.currentText()
        selectCam = [self.cameraCom.currentText()]
        
        if self.bakeCamCheck.isChecked():
            bake = True
        else:
            bake = False
        
        if not selectCam:
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,'Tip','Please Select "Camera"').exec_()
            return
        
        if not seq or not shot:
            QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,'Tip','Please Select "Sequence" and "Shot"').exec_()
            return
        
        publishCam.publishCam(seq,shot,selectCam,bake=bake)
        
        
        QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,'Tip','Publish Success!').exec_()
        
        
        
        
        
        
        