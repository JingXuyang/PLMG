# -*- coding: utf-8 -*-

import os
import copy
import json


import qtlb
QtGui, QtWidgets, QtCore, QtWebKit = qtlb.QtGui, qtlb.QtWidgets, qtlb.QtCore, qtlb.QtWebKit

def formatString(string, mapping):
    dic = copy.deepcopy(mapping)

    for i in dic.keys():
        k = '{'+i+'}'
        #print 'k:',k
        if k in string:
            mapValue = dic[i]
            if type(mapValue) in (str, unicode):
                try:
                    string = string.replace(k, mapValue)
                except:
                    pass
                    #traceback.print_exc()
            else:
                return mapValue
    
    return string


class _ColorButton(QtWidgets.QLabel):
    
    def __init__(self, color, size=26, parent=None):
        self._color = color
        
        QtWidgets.QLabel.__init__(self, parent=parent)
        self.setFixedSize(size, size)
        self.setValue(color)
    
    def mousePressEvent(self, event):
        oldColor = QtGui.QColor()
        oldColor.setNamedColor(self._color)
        
        color = QtWidgets.QColorDialog.getColor(oldColor)
        if color.isValid():
            self.setValue(color.name())
    
    def value(self):
        return self._color
    
    def setValue(self, color):
        self._color = color
        
        s = '''
QLabel {
    background-color: %s;
}
''' % color
        self.setStyleSheet(s)

class _FontButton(QtWidgets.QFontComboBox):
    
    def __init__(self, font, parent=None):
        QtWidgets.QFontComboBox.__init__(self, parent=parent)
        self.setValue(font)
    
    def value(self):
        font = self.currentFont()
        return font.family()
    
    def setValue(self, font):
        if font:
            font = QtGui.QFont(font)
            self.setCurrentFont(font)


class _SetAllButton(QtWidgets.QPushButton):
    
    def __init__(self, key, widget, window=None, parent=None):
        self._key = key
        self._widget = widget
        self._window = window
        
        QtWidgets.QPushButton.__init__(self, 'Set All')
        self.clicked.connect(self.run)
    
    def run(self):
        for lab in self._window._labels:
            value = self._widget.value()
            data = copy.deepcopy(lab.value())
            data[self._key] = value
            lab.setValue(data)

class _SceneHUDItemDialog(QtWidgets.QDialog):
    
    def __init__(self, text='Spider', font='Arial', color='#DDD',
                 alpha=1, scale=1, hpos=0, window=None, parent=None):
        self._parent = parent
        self._window = window
        
        QtWidgets.QDialog.__init__(self)#, parent=parent)
        self.setWindowTitle('Edit HUD')
        
        textLab = QtWidgets.QLabel('Text')
        self._textWgt = QtWidgets.QLineEdit()
        self._textWgt.setText(text)
        
        colorLab = QtWidgets.QLabel('Color')
        self._colorWgt = _ColorButton(color)
        setAllColorBtn = _SetAllButton('color', self._colorWgt, self._window)
        
        fontLab = QtWidgets.QLabel('Font')
        self._fontWgt = _FontButton(font)
        setAllFontBtn = _SetAllButton('font', self._fontWgt, self._window)
        
        alphaLab = QtWidgets.QLabel('Alpha')
        self._alphaWgt = QtWidgets.QDoubleSpinBox()
        self._alphaWgt.setSingleStep(0.1)
        self._alphaWgt.setRange(0, 1)
        self._alphaWgt.setValue(alpha)
        setAllAlphaBtn = _SetAllButton('alpha', self._alphaWgt, self._window)
        
        scaleLab = QtWidgets.QLabel('Scale')
        self._scaleWgt = QtWidgets.QDoubleSpinBox()
        self._scaleWgt.setSingleStep(1)
        self._scaleWgt.setRange(1, 1000)
        self._scaleWgt.setValue(scale)
        setAllScaleBtn = _SetAllButton('scale', self._scaleWgt, self._window)
        
        hposLab = QtWidgets.QLabel('HPos')
        self._hposWgt = QtWidgets.QDoubleSpinBox()
        self._hposWgt.setSingleStep(1)
        self._hposWgt.setRange(-1000, 1000)
        self._hposWgt.setValue(hpos)
        setAllHPosBtn = _SetAllButton('hpos', self._hposWgt, self._window)
        
        applyBtn = QtWidgets.QPushButton('Apply')
        applyBtn.setMinimumWidth(80)
        applyBtn.clicked.connect(self.apply)
        okBtn = QtWidgets.QPushButton('OK')
        okBtn.setMinimumWidth(80)
        okBtn.clicked.connect(self.ok)
        
        lay1 = QtWidgets.QGridLayout()
        lay1.setContentsMargins(0, 0, 0, 0)
        lay1.addWidget(textLab, 0, 0)
        lay1.addWidget(self._textWgt, 0, 1, 1, 2)
        lay1.addWidget(colorLab, 1, 0)
        lay1.addWidget(self._colorWgt, 1, 1)
        lay1.addWidget(setAllColorBtn, 1, 2)
        lay1.addWidget(fontLab, 2, 0)
        lay1.addWidget(self._fontWgt, 2, 1)
        lay1.addWidget(setAllFontBtn, 2, 2)
        lay1.addWidget(alphaLab, 3, 0)
        lay1.addWidget(self._alphaWgt, 3, 1)
        lay1.addWidget(setAllAlphaBtn, 3, 2)
        lay1.addWidget(scaleLab, 4, 0)
        lay1.addWidget(self._scaleWgt, 4, 1)
        lay1.addWidget(setAllScaleBtn, 4, 2)
        lay1.addWidget(hposLab, 5, 0)
        lay1.addWidget(self._hposWgt, 5, 1)
        lay1.addWidget(setAllHPosBtn, 5, 2)
        
        #lay1 = QtWidgets.QFormLayout()
        #lay1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        #lay1.setContentsMargins(0, 0, 0, 0)
        #
        #lay1.addRow('Text', self._textWgt)
        #lay1.addRow('Color', self._colorWgt)
        #lay1.addRow('Font', self._fontWgt)
        #lay1.addRow('Alpha', self._alphaWgt)
        #lay1.addRow('Scale', self._scaleWgt)
        
        bLay = QtWidgets.QHBoxLayout()
        bLay.addStretch(1)
        bLay.addWidget(applyBtn)
        bLay.addWidget(okBtn)
        
        lay = QtWidgets.QVBoxLayout()
        lay.addLayout(lay1)
        lay.addLayout(bLay)
        
        self.setLayout(lay)
    
    def value(self):
        result = {
            'text': self._textWgt.text(),
            'color': self._colorWgt.value(),
            'font': self._fontWgt.value(),
            'alpha': self._alphaWgt.value(),
            'scale': self._scaleWgt.value(),
            'hpos': self._hposWgt.value()
        }
        
        return result
    
    def apply(self):
        self._parent.setValue(self.value())
    
    def ok(self):
        self.done(1)
    
    def exec_(self):
        r = QtWidgets.QDialog.exec_(self)
        if r:
            return self.value()

class _SceneHUDBarDialog(QtWidgets.QDialog):
    
    def __init__(self, color='#111', alpha=1, scale=1,
                 top=True, bottom=True, parent=None):
        self._parent = parent
        
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle('Edit Mask')
        self.resize(300, 100)
        
        self._colorWgt = _ColorButton(color)
        
        self._alphaWgt = QtWidgets.QDoubleSpinBox()
        self._alphaWgt.setSingleStep(0.1)
        self._alphaWgt.setRange(0, 1)
        self._alphaWgt.setValue(alpha)
        
        self._scaleWgt = QtWidgets.QDoubleSpinBox()
        self._scaleWgt.setSingleStep(1)
        self._scaleWgt.setRange(1, 1000)
        self._scaleWgt.setValue(scale)
        
        self._topWgt = QtWidgets.QCheckBox()
        self._bottomWgt = QtWidgets.QCheckBox()
        
        if top:
            top = QtCore.Qt.Checked
        else:
            top = QtCore.Qt.Unchecked
        self._topWgt.setCheckState(top)
        
        if bottom:
            bottom = QtCore.Qt.Checked
        else:
            bottom = QtCore.Qt.Unchecked
        self._bottomWgt.setCheckState(bottom)
        
        applyBtn = QtWidgets.QPushButton('Apply')
        applyBtn.setMinimumWidth(80)
        applyBtn.clicked.connect(self.apply)
        okBtn = QtWidgets.QPushButton('OK')
        okBtn.setMinimumWidth(80)
        okBtn.clicked.connect(self.ok)
        
        lay1 = QtWidgets.QFormLayout()
        lay1.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        lay1.setContentsMargins(0, 0, 0, 0)
        
        lay1.addRow('Color', self._colorWgt)
        lay1.addRow('Alpha', self._alphaWgt)
        lay1.addRow('Scale', self._scaleWgt)
        lay1.addRow('Top', self._topWgt)
        lay1.addRow('Bottom', self._bottomWgt)
        
        bLay = QtWidgets.QHBoxLayout()
        bLay.addStretch(1)
        bLay.addWidget(applyBtn)
        bLay.addWidget(okBtn)
        
        lay = QtWidgets.QVBoxLayout()
        lay.addLayout(lay1)
        lay.addLayout(bLay)
        
        self.setLayout(lay)
    
    def value(self):
        if self._topWgt.checkState() == QtCore.Qt.Checked:
            top = True
        else:
            top = False
        if self._bottomWgt.checkState() == QtCore.Qt.Checked:
            bottom = True
        else:
            bottom = False
        
        result = {
            'color': self._colorWgt.value(),
            'alpha': self._alphaWgt.value(),
            'scale': self._scaleWgt.value(),
            'top': top,
            'bottom': bottom
        }
        
        return result
    
    def apply(self):
        self._parent._setBars(self.value())
    
    def ok(self):
        #print 'ok'
        self.done(1)
    
    def exec_(self):
        r = QtWidgets.QDialog.exec_(self)
        if r:
            return self.value()

def _getColor(color, alpha=1):
    if type(alpha) in (int, float):
        alpha = alpha*255
    else:
        alpha = 255
    
    color = QtGui.QColor(color).getRgb()
    color = list(color)[:3] + [alpha]
    color = tuple(color)
    color = 'rgba(%s, %s, %s, %s)' % color
    
    return color

class _SceneHUDItem(QtWidgets.QLabel):
    
    def __init__(self, data={}, alignment='center',
                 parent=None):
        self._data = data
        self._parent = parent
        self._currentFrame = 1
        
        QtWidgets.QLabel.__init__(self, parent=parent._bgLab)
        
        if alignment == 'left':
            a = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft
        elif alignment == 'right':
            a = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight
        elif alignment == 'center':
            a = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter
        else:
            a = ''
        
        if a:
            self.setAlignment(a)
        
        self.setValue(data, resize=False)
    
    def setCurrentFrame(self, frame):
        self._currentFrame = frame
    
    def color(self):
        color = self._data.get('color')
        alpha = self._data.get('alpha')
        color = _getColor(color, alpha)
        return color
    
    def setSelectStyleSheet(self):
        #font = self.font()
        #font.setItalic(True)
        #font.setBold(True)
        ##font.setOverline(True)
        #self.setFont(font)
        
        s = '''
QLabel {
    color: %s;
    background-color: rgba(0, 85, 85, 155);
}
''' % self.color()
        
        self.setStyleSheet(s)
    
    def setDeselectStyleSheet(self):
        #font = self.font()
        #font.setItalic(False)
        #font.setBold(False)
        ##font.setOverline(False)
        #self.setFont(font)
        
        s = '''
QLabel {
    color: %s;
    background-color: rgba(0, 0, 0, 0);
}
''' % self.color()
        
        self.setStyleSheet(s)
    
    def select(self):
        '''
        Selects the item to set things below:
            Font color: rgba(r, g, b, alpha)
            Background rgba(0, 85, 85, 155)
        '''
        self.setSelectStyleSheet()
        
        self._parent._currentLabel = self
        
        for lab in self._parent._labels:
            if lab != self:
                lab.deselect()
    
    def deselect(self):
        '''
        Deselects the item to set things below:
            Font color: rgba(r, g, b, alpha)
            Background rgba(0, 0, 0, 0)
        '''
        self.setDeselectStyleSheet()
    
    def mousePressEvent(self, event):
        self.select()
        
        kwargs = copy.deepcopy(self._data)
        kwargs['window'] = self._parent
        kwargs['parent'] = self
        dialog = _SceneHUDItemDialog(**kwargs)
        r = dialog.exec_()
        
        if r:
            self.setValue(r)
    
    def value(self):
        return self._data
    
    def evalText(self, text):
        dic = {'frame': str(self._currentFrame)}
        for i in range(1, 11):
            key = 'frame.%s' % i
            value = str(self._currentFrame).zfill(i)
            dic[key] = value
        #print [text, dic]
        
        return formatString(text, dic)
    
    def setValue(self, data, resize=True):
        '''
        data is a dictionary with keys:
            text
            color
            font
            alpha
            scale
        '''
        if type(data) == dict:
            pass
        else:
            return
        
        self._data.update(data)
        
        text = data.get('text')
        if text:
            evalText = self.evalText(text)
            self.setText(evalText)
        
        self.setFont2(data)
        
        if self._parent._currentLabel == self:
            self.setSelectStyleSheet()
        else:
            self.setDeselectStyleSheet()
        
        if resize:
            self._parent.resizeEvent()
            
        #self.setFont(QtWidgets.QFont("Arial",20,QtWidgets.QFont.Bold))
    
    def setFont2(self,data):
        font = data.get('font')
        if font:
            font = QtGui.QFont(font)
            scale = data.get('scale')
            
            if type(scale) in (float, int):
                font.setPixelSize(scale)
            font.setWeight(75)
            self.setFont(font)
    
    def updateText(self,data={}):
        if data:
            self._data = data
        #print "data:",self._data
        text = self._data.get('text')
        #print "text:",text
        if text:
            evalText = self.evalText(text)
            #print [self._data['font'],self._data['scale']]
            #self.setFont(QtWidgets.QFont(self._data['font'],self._data['scale']))
            
            self.setFont2(self._data)
            self.setText(evalText)

class _SceneHUDsBar(QtWidgets.QLabel):
    
    def __init__(self, data={}, parent=None):
        self._data = data
        self._parent = parent
        
        QtWidgets.QLabel.__init__(self, parent=parent._bgLab)
        self.setValue(data)
    
    def value(self):
        return self._data
    
    def setValue(self, data):
        '''
        data is a dictionary with keys:
            color
            alpha
            scale
            display
        '''
        if type(data) == dict:
            pass
        else:
            return
        
        self._data.update(data)
        
        #scale = data.get('scale')
        #if type(scale) in (float, int):
        #    self.setFixedHeight(scale)
        
        color = data.get('color')
        if color:
            if data.get('display'):
                alpha = data.get('alpha')
            else:
                alpha = 0
            
            color = _getColor(color, alpha)
            
            s = '''
QLabel {
    background-color: %s;
}
''' % color

            #print
            #print 'stylesheet:'
            #print s
            
            self.setStyleSheet(s)

class SceneHUDsPrefsWidget(QtWidgets.QFrame):
    
    category = 'Special'
    multiRows = True
    
    def __init__(self, color='', backgroundImage='',
                 parm=None, parent=None):
        self._color = color
        self._backgroundImage = backgroundImage
        
        
        self._m = None
        self._realSize = []
        
        self.loadImage(self._backgroundImage)
        
        self._data = {'labels': [], 'mask': {}}
        self._bgLab = None
        self._topBorder = None
        self._bottomBorder = None
        self._maskBtn = None
        self._labels = [None]*12
        self._currentLabel = None
        
        #apdr.Widget.__init__(self, parm)
        QtWidgets.QFrame.__init__(self, parent=parent)
        self.setMinimumSize(1920, 1080)
        self.setFrameShape(QtWidgets.QFrame.Box)
        s = '''
QFrame {
    background-color: %s;
}
''' % color
        
        self.setStyleSheet(s)
        
    def loadImage(self, path):
        self._backgroundImage = path
        #print "path:",path
        if os.path.isfile(path):
            self._m = QtGui.QPixmap(path)
            imgSize = self._m.size()
            #print path
            #print  self._realSize
            #print '----------------'
            self._realSize = [imgSize.width(), imgSize.height()]
        else:
            self._realSize = []
    
    def saveImage(self):
        r = QtWidgets.QFileDialog.getSaveFileName(parent=self, caption='Save')
        if r[0]:
            #print r[0]
            pmap = QtGui.QPixmap.grabWidget(self)
            #print 'size:',pmap.size()
            pmap.save(r[0])
    
    def saveSequence(self, srcPath, dstPath, frameRange,transparentImg=''):
        # Hide the button
        self._maskBtn.setVisible(False)
        
        import fllb
        #import misc
        
        srcInfo = fllb.parseSequence(srcPath)
        dstInfo = fllb.parseSequence(dstPath)
        
        frames = fllb.frameRangeToFrames(frameRange)
        # Buffer a frame forward or the first image will be wrong(drawing or hud size is not right)
        frames = [frames[0]]+frames

        for i in frames:
            srcFrameStr = str(i).rjust(srcInfo['padding_length'], '0')
            srcFramePath = srcPath.replace(srcInfo['padding'], srcFrameStr)
            dstFrameStr = str(i).rjust(dstInfo['padding_length'], '0')
            dstFramePath = dstPath.replace(dstInfo['padding'], dstFrameStr)
            print [os.path.basename(srcFramePath)]
            #print '121'
            if os.path.isfile(srcFramePath):
                
                self.loadImage(srcFramePath)
                
                self.resizeToRealSize()
                #self._bgLab.setScaledContents(True)
                
                self._bgLab.setPixmap(self._m)

                # Update label text
                for lab in self._labels:
                    lab.setCurrentFrame(i)
                    lab.updateText()
                
                qtlb.processEvents()
                
                #misc.makeFolder(dstFramePath)
                
                f = os.path.dirname(dstFramePath)
                if not os.path.exists(f):
                    os.makedirs(f)
                
                #print 'src:',srcFramePath
                #print 'dst:',dstFramePath
                
                pmap = QtGui.QPixmap.grabWidget(self)
                #pmap.fill(QtCore.Qt.transparent)
                pmap.setMask(QtGui.QBitmap(transparentImg))
                #print pmap.hasAlpha()
                pmap.save(dstFramePath)
                
                
        self._maskBtn.setVisible(True)
    
    def resizeToRealSize(self):
        #print 'real size:',self._realSize
        if self._realSize:
            self.resize(*self._realSize)
    
    def _contextMenuEvent(self, event):
        '''Pops up the menu when user right clicks the mouse.'''        
        self._menu = QtWidgets.QMenu(self)
        self._menu.addAction('Save Image...', self.saveImage)
        self._menu.addAction('Resize To Real Size...', self.resizeToRealSize)
        self._menu.addAction('Print Prefs', self.printPrefs)
        self._menu.exec_(QtGui.QCursor().pos())
    
    def buildWidgets(self, data):
        
        #----------------------- Background Label -------------------
        
        if not self._bgLab:
            self._bgLab = QtWidgets.QLabel(self)
            s = '''
QFrame {
    background-color: #000000;
}
'''
            #self._bgLab.setStyleSheet(s)
            self._bgLab.contextMenuEvent = self._contextMenuEvent

        #--------------------------- Mask -----------------------
        if data['mask']['top']:
            dis = True
        else:
            dis = False
        d = {
            'color': data['mask']['color'],
            'alpha': data['mask']['alpha'],
            'scale': data['mask']['scale'],
            'display': dis
        }
        if not self._topBorder:
            self._topBorder = _SceneHUDsBar(d, self)
        self._topBorder.setValue(d)
        
        # Bottom border
        if data['mask']['bottom']:
            dis = True
        else:
            dis = False
        d = {
            'color': data['mask']['color'],
            'alpha': data['mask']['alpha'],
            'scale': data['mask']['scale'],
            'display': dis
        }
        if not self._bottomBorder:
            self._bottomBorder = _SceneHUDsBar(d, self)
        self._bottomBorder.setValue(d)
        
        if not self._maskBtn:
            self._maskBtn = QtWidgets.QPushButton('Mask', parent=self._bgLab)
            self._maskBtn.clicked.connect(self._barDialog)
        
        #-------------------------- Labels ------------------------
        aligns = [
            'left',
            'center',
            'center',
            'center',
            'center', 
            'right',
            
            'left',
            'center',
            'center',
            'center',
            'center', 
            'right',
        ]
        
        i = 0
        for j in aligns:
            d = data['labels'][i]
            kwargs = {
                'data': d, 
                'alignment': j,
                'parent': self
            }
            if not self._labels[i]:
                self._labels[i] = _SceneHUDItem(**kwargs)
            #self._labels[i].setValue(d)
            
            i += 1
    
    def resizeEvent(self, event=None):
        #print '1321'
        self.placeWidgets(self._data)
    
    def placeWidgets(self, data):
        size = self.size()
        deviceWidth = size.width()
        deviceHeight = size.height()
        #print deviceWidth,deviceHeight
        deviceRatio = float(deviceWidth)/deviceHeight
        
        # Get aspect ratio
        if self._realSize:
            w,h = self._realSize
            imgRatio = float(w)/h
        
        else:
            imgRatio = data.get('device_aspect_ratio')
        #print "deviceRatio,imgRatio"
        #print deviceRatio,imgRatio
        # Get image size
        if deviceRatio <= imgRatio:
            imgWidth = deviceWidth
            imgHeight = float(deviceWidth)/imgRatio
            #print '[imgWidth,imgHeight]'
            #print [imgWidth,imgHeight]
            bgLabX = 0
            bgLabY = 0.5*(deviceHeight-imgHeight)
        
        else:
            imgWidth = deviceHeight*imgRatio
            imgHeight = deviceHeight
            bgLabX = 0.5*(deviceWidth-imgWidth)
            bgLabY = 0
        
        imgWidth = int(imgWidth)
        imgHeight = int(imgHeight)
        
        
        #----------------------- Background Label -------------------
        #print bgLabX, bgLabY, imgWidth, imgHeight
        # Qt don't apply float number,the result maybe have offset,hear need to add one
        imgHeight = imgHeight+1
        
        geometry = [bgLabX, bgLabY, imgWidth, imgHeight]
        self._bgLab.setGeometry(*geometry)
        
        if self._m:
            m1 = self._m.scaled(imgWidth, imgHeight)
            self._bgLab.setPixmap(m1)
        
        
        #--------------------------- Mask -----------------------
        borderHeight = int(data['mask']['scale'])
        
        geometry = [0, 0, imgWidth, borderHeight]
        self._topBorder.setGeometry(*geometry)
        
        # Bottom border
        x = 0
        y = imgHeight - borderHeight
        geometry = [x, y, imgWidth, borderHeight]
        self._bottomBorder.setGeometry(*geometry)
        
        btnWidth = 60
        btnHeight = 20
        btnGeometry = [
            0.5*imgWidth,
            imgHeight-borderHeight-btnHeight,
            btnWidth,
            btnHeight
        ]
        self._maskBtn.setGeometry(*btnGeometry)
        
        
        #-------------------------- Labels ------------------------
        textWidth = float(imgWidth)/6
        textSize = [textWidth, borderHeight]
        
        labHPos = [b['hpos'] for b in data['labels']]
        #print 'labHPos:',labHPos
        topLabelVerticalOffset = 42
        bottomLabelVerticalOffset = -42
        textPos = [
            [labHPos[0], 0+topLabelVerticalOffset],
            [textWidth+labHPos[1], 0+topLabelVerticalOffset],
            [2*textWidth+labHPos[2], 0+topLabelVerticalOffset],
            [imgWidth-3*textWidth+labHPos[3], 0+topLabelVerticalOffset],
            [imgWidth-2*textWidth+labHPos[4], 0+topLabelVerticalOffset],
            [imgWidth-textWidth+labHPos[5], 0+topLabelVerticalOffset],
            
            [labHPos[6], y+bottomLabelVerticalOffset],
            [textWidth+labHPos[7], y+bottomLabelVerticalOffset],
            [2*textWidth+labHPos[8], y+bottomLabelVerticalOffset],
            [imgWidth-3*textWidth+labHPos[9], y+bottomLabelVerticalOffset],
            [imgWidth-2*textWidth+labHPos[10], y+bottomLabelVerticalOffset],
            [imgWidth-textWidth+labHPos[11], y+bottomLabelVerticalOffset],
        ]
        
        i = 0
        for k in xrange(len(textPos)):
            j = textPos[k]
            if k == 0:
                geometry = j+[textSize[0]+50,textSize[1]]
            elif k == 1:
                geometry = j+[textSize[0]-50,textSize[1]]
            else:
                geometry = j+textSize
            #print "geometry:",geometry
            self._labels[i].setGeometry(*geometry)
            
            i += 1
    
    def mousePressEvent(self, event):
        #print 123456
        self.clearSelection()
    
    def _barDialog(self):
        kwargs = copy.deepcopy(self._data['mask'])
        kwargs['parent'] = self
        dialog = _SceneHUDBarDialog(**kwargs)
        r = dialog.exec_()
        
        #print
        #print 'SceneHUDBarDialog.result:',r
        
        if r:
            self._data['mask'] = r
            
            self._setBars(r)
    
    def _setBars(self, data):
        #print "data:",data
        upData = copy.deepcopy(data)
        if data.get('top'):
            show = True
        else:
            show = False
        upData['display'] = show
        
        downData = copy.deepcopy(data)
        if data.get('bottom'):
            show = True
        else:
            show = False
        downData['display'] = show
        
        self._topBorder.setValue(upData)
        self._bottomBorder.setValue(downData)
        
        self._data['mask'] = data
        self.placeWidgets(self._data)
    
    def clearSelection(self):
        for lab in self._labels:
            lab.deselect()
        self._currentLabel = None
        
        
    def value(self):
        labs = []
        for lab in self._labels:
            labs.append(lab.value())
        
        self._data['labels'] = labs
        
        return self._data
    
    def setValue(self, value):
        if type(value) == dict:
            self._data = copy.deepcopy(value)
            
            #print
            #print 'data:',self._data
            
            self.buildWidgets(self._data)
            self.placeWidgets(self._data)
            
    def printPrefs(self):
        v = json.dumps(self.value(), indent=2)
        print v


