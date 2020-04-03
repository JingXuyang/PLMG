import sys,os

try:
    from PySide2 import QtWidgets,QtGui,QtCore,QtXml,QtWebKit
    import shiboken2 as shiboken2
except:
    from PySide import QtCore,QtXml,QtWebKit
    from PySide import QtGui as QtWidgets
    import shiboken


import maya.OpenMayaUI as omui

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = shiboken.wrapInstance(long(mayaMainWindowPtr),QtWidgets.QWidget)


import func
reload(func)


headerList  = ['camera','firstFrame','lastFrame']
dataInfo = func.parsingCameraShotInfo()

class DataWidget(QtWidgets.QTreeWidget):
    def __init__(self,
                headerList=[],
                dataInfo=[]):
        '''
        headerList:
            ['camera','firstFrame','lastFrame']
        dataInfo:
            [{'camera':'cam_040_190',
              'firstFrame':'',
              'lastFrame': '',},
            ]
        '''
    
        QtWidgets.QTreeWidget.__init__(self)

        
        
        #print "headerList:",headerList
        self.setWindowTitle('PlayBlast')
        self.setHeaderLabels(headerList)
        
        # set checkBox item is white
        palette = QtWidgets.QPalette()
        palette.setColor(QtWidgets.QPalette.Background, QtCore.Qt.white)
        self.setPalette(palette)
        
        
        
        
        
        self.allItem = []
        
        for info in dataInfo:
            item = QtWidgets.QTreeWidgetItem(self)
            for i in xrange(len(headerList)):
                key = headerList[i]
                value = info[key]
                item.setText(i,value)
                
                item.info = info
            item.setCheckState(0,QtCore.Qt.Unchecked)
            item.setSizeHint(0,QtCore.QSize(50,22))
            
            self.allItem.append(item)
        
        self.itemClicked.connect(self.setItemState)
        
        #self.header().setResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        
        self.setColumnWidth(0,120)
        
    def setItemState(self,item):
        
        #item = self.currentItem()
        
        if item.checkState(0) == QtCore.Qt.Checked:
            #print item.info
            # set frameRange item background color
            #print item.background(1).color().name()
            #print item.background(2).color().name()
            item.setBackground(1,QtWidgets.QBrush(QtWidgets.QColor('green')))
            item.setBackground(2,QtWidgets.QBrush(QtWidgets.QColor('green')))
            
            # 
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        else:
        
            item.setText(1,'')
            item.setText(2,'')
            item.setBackground(1,QtWidgets.QBrush(QtWidgets.QColor(43,43,43)))
            item.setBackground(2,QtWidgets.QBrush(QtWidgets.QColor(43,43,43)))
            
            
            item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsDragEnabled|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
            
        
class MainWindow(QtWidgets.QWidget):
    def __init__(self,
                headerList=headerList,
                dataInfo=dataInfo):
        QtWidgets.QWidget.__init__(self)
        
        
        self.setParent(mayaMainWindow)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.resize(350,650)
        self.dataWidget = DataWidget(headerList=headerList,
                                     dataInfo=dataInfo)
                                     
        
        self.outputFolder = QtWidgets.QLineEdit()
        outputBtn = QtWidgets.QPushButton('...')
        outputBtn.clicked.connect(self.selectOutputPath)
        
        outputLay = QtWidgets.QHBoxLayout()
        outputLay.addWidget(self.outputFolder)
        outputLay.addWidget(outputBtn)
        
        btn = QtWidgets.QPushButton('Playblast')
        btn.clicked.connect(self.playBlast)
        
        
        
        btnLay = QtWidgets.QHBoxLayout()
        btnLay.addStretch(1)
        btnLay.addWidget(btn)
        
        
        
        
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.dataWidget)
        lay.addLayout(outputLay)
        lay.addSpacing(15)
        lay.addLayout(btnLay)
        
        self.setLayout(lay)
        
    def selectOutputPath(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self,'Browse...','')
        if path:
            self.outputFolder.setText(path)
            
    
        
    def playBlast(self):
        
        allItem = self.dataWidget.allItem
        
        
        error = []
        result = []
        
        for item in allItem:
            if item.checkState(0) == QtCore.Qt.Checked:
            
                if not item.text(1) or not item.text(2):
                    error.append(item.text(0))
                
                else:
                    result.append([item.text(0),item.text(1),item.text(2)])
                
                
        if error:
            mes = '\n'.join(error)
            mes = ' %s \nFrameRange not set!'% mes
            
            wgt = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,'Warning',mes)
            wgt.exec_()
            return
        
        if not self.outputFolder.text():
            mes = 'please select the output path!'
            wgt = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,'Warning',mes)
            wgt.exec_()
            return
        
        if result:
            
            func.playBlast(path = self.outputFolder.text(),
                           info = result)
            '''
            # unload plugin eyeBallNode.py
            func.unloadPlugin()
            
            for item in result:
                camName = item.text(0)
                
                func.playBlast2(path = self.outputFolder.text(),
                               frameRange=[float(item.text(1)),float(item.text(2))],
                               camera=camName)
            
            # load plugin eyeBallNode.py
            func.loadPlugin()
            '''
        
                
                
        
        
        
        
        
        
        
        
            
            
            
            

                
                
                
            
            
        
        
        
        
    
        






