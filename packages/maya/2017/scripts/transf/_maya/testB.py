# -*- coding: utf-8 -*-
import os
import subprocess
import maya.cmds as cmds

def mayaBatchBackstageCmd(  mayabatchPath='',
                            melPath='',
                            customParms=[],
                            block=True):
    '''
    mayabatch background Command,not be used batch render.
    parameters:
        mayaBatchPath: "C:/Program Files/Autodesk/Maya2017/bin/mayabatch.exe"
        melPath: "{path}/{name}.mel"
        pyPath/pythonPath: "{path}/{name}.py"
        customParms/customParameters: [ "str",
                                        '{key:value}',
                                        "[1,2,3]"]
        if you want to pass a dict or list,they are must be handle strings.
        block: if block is True, the progress will be block,else will not be blocked. 
    '''
    mayabatchPath = mayabatchPath.replace('\\','/')
    melPath = melPath.replace('\\','/')
    melDir = os.path.dirname(melPath)
    
    modulePath = os.path.dirname(melDir)
    moduleName = os.path.basename(melDir)
    pyPath = "%s/__init__.py"%(melDir)
    
    melFunc = '''import sys
import subprocess
parms = sys.argv[3:]
sys.path.append(r'{modulePath}')
import {moduleName}
reload({moduleName})
{moduleName}.main(parms)'''.format(pyPath=pyPath,modulePath=modulePath,moduleName=moduleName)

    melList = melFunc.split('\n')

    mel = '''python "print '----------- start -----------'";'''
    mel += '\n'
    for i in melList:
        if mel:
            mel += 'python "%s";\n'%i
    mel += '''python "print '-----------  end  -----------'";'''
    #print mel
    
    
    # create mel path,write mel
    import __builtin__
    melFolder = os.path.dirname(melPath)
    if not os.path.exists(melFolder):
       os.makedirs(melFolder)
       
    with __builtin__.open(melPath,'w') as f:
        f.write(mel)
    
    
    # create python path,write python
    pythonFunc ='''import sys
def main(argv):
    
    print "argv:",argv
'''
    
    
    if not os.path.exists(pyPath):
        
        with __builtin__.open(pyPath,'w') as f:
            f.write(pythonFunc)
    #print pyPath
    #print pythonFunc
    #======================================
    parmStr = " ".join(customParms)
    
    cmd = '"{mayabatchPath}" -script "{melPath}" {parmStr}'.format(mayabatchPath=mayabatchPath,
                                                                   melPath=melPath,
                                                                   parmStr=parmStr)
    
    if block:
        subprocess.call(cmd,shell=True)
    else:
        subprocess.Popen(cmd,shell=True)
    return cmd

def transmitFileUVBackStage(maPath,
                            uvPath,
                            logPath='',
                            openLog=False,
                            longName=True,
                            mayabatchPath='',
                            melPath='',
                            block=False):
    
    maPath = maPath.replace('\\','/')
    uvPath = uvPath.replace('\\','/')
    logPath = logPath.replace('\\','/')
    customParms = [maPath,uvPath,logPath,str(openLog),str(longName)]
    # os.environ['MAYA_UI_LANGUAGE'] = "en_US"
    
    cmd = mayaBatchBackstageCmd(mayabatchPath,
                                melPath,
                                customParms=customParms,
                                block=block)
    return cmd
    

    
            
            
            
    
    
    
