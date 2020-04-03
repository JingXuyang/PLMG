import os
import qtlb
from qtlb import QtCore,QtGui,QtWidgets
import plcr
import dbif

db = dbif._cgteamwork.CGTeamwork()
task = plcr.getTaskFromEnv()
project = task['project']

import swif
sw = swif._maya.Maya()


def getSequences():
    seqInfo = db.getSequences(project)
    seqList = [inf['code'] for inf in seqInfo]
    
    seqList = sorted(seqList)
    return seqList
    
    
def getShots(seq=''):
    shotList = []
    if seq:
        shotInfo = db.getShots(project,seq)
        shotList = [inf['code'] for inf in shotInfo]
        
        shotList = sorted(shotList)
        
    return shotList
    
    
class SelectShotStepWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        self.allSequence = getSequences()
        self.allSequence.insert(0,'')
        
        self.seqLabel = QtWidgets.QLabel('Seq:')
        self.seqCom = QtWidgets.QComboBox()
        self.seqCom.addItems(self.allSequence)
        self.seqCom.activated.connect(self.setShot)
        
        
        self.shotLabel = QtWidgets.QLabel('Shot:')
        self.shotCom = QtWidgets.QComboBox()
        self.shotCom.activated.connect(self.setTask)
        
        self.stepLabel = QtWidgets.QLabel('Step:')
        self.stepCom = QtWidgets.QComboBox()
        self.stepCom.addItems(['shotFinaling'])
        
        lay = QtWidgets.QHBoxLayout()
        lay.addWidget(self.seqLabel)
        lay.addWidget(self.seqCom)
        lay.addStretch(1)
        lay.addWidget(self.shotLabel)
        lay.addWidget(self.shotCom)
        lay.addStretch(1)
        lay.addWidget(self.stepLabel)
        lay.addWidget(self.stepCom)
        self.setLayout(lay)
        
        self.setDefaultDisplay()
        
        
    def setShot(self):
        self.shotCom.clear()
        seq = self.seqCom.currentText()
        if seq:
            shots = getShots(seq=seq)
            self.shotCom.addItems(shots)
            
            return shots
            
    def setDefaultDisplay(self):
        seq = task['sequence']
        shot = task['shot']
        print 
        if seq and shot:
            #print [seq,shot]
            if seq in self.allSequence:
                idx = self.allSequence.index(seq)
                self.seqCom.setCurrentIndex(idx)
                
                shots = self.setShot()
                #print shots
                if shot in shots:
                    idx2 = shots.index(shot)
                    self.shotCom.setCurrentIndex(idx2)


    def setTask(self,):
        print 2
        seq = self.seqCom.currentText()
        shot = self.shotCom.currentText()
        step = self.stepCom.currentText()
        
        os.environ['PKMG_SEQUENCE'] = seq
        os.environ['PKMG_SHOT'] = shot
        os.environ['PKMG_STEP'] = step
        

        
        
        