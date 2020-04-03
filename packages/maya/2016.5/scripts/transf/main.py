# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(r'Z:\bin\pltk\packages\maya\2016.5\scripts\transf\_maya')
import testB
reload(testB)


def get_desktop():
    import _winreg
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders')
    return _winreg.QueryValueEx(key, "Desktop")[0]


desktopPath = get_desktop()

maPath = r"D:\project\THHJ\assets\Ch\Jiaolong\rig\publish\v002\Jiaolong.ma"
uvPath = r"D:\project\THHJ\assets\Ch\Jiaolong\tex\publish\v001\Jiaolong.abc"
logPath = '%s/%s_uvLog.txt'%(desktopPath,os.path.basename(os.path.splitext(maPath)[0]))
openLog=True
mayabatchPath="%s/bin/mayabatch.exe"%(os.environ['MAYA_LOCATION'])
melPath=r'C:\Spider1.0\startup\maya\transmitFileUVBackStage\transmit.mel'
block=False


cmd = testB.transmitFileUVBackStage(maPath,uvPath,
                                      logPath=logPath,
                                      openLog=openLog,
                                      mayabatchPath=mayabatchPath,
                                      melPath=melPath,
                                      block=block)
                              
print cmd
                              
