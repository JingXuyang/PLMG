# coding=utf-8
# ==============================================================
# !/usr/bin/env python
# -*- encoding: utf-8 -*-#
#
#  @Version: 
#  @Author: RunningMan
#  @File: _maya.py
#  @Create Time: 2019/12/31 14:13
# ==============================================================
import glob
import json
import os
import re
import shutil
import time
import shiboken
from PySide import QtGui, QtCore
import maya.OpenMayaUI as apiUI


class Maya:
    def __init__(self):
        import maya.cmds as cmds
        import maya.mel as mel
        import pymel.core as pm
        self._pm = pm
        self._mel = mel
        self._cmds = cmds

    def app(self):
        return 'maya'

    def extension(self):
        return self.extensions()[0]

    def extensions(self):
        return ['ma', 'mb']

    # ---------------------------------- Basic Parameters -------------------------------

    _fpsMap = {
        'game': 15,
        'film': 24,
        'pal': 25,
        'ntsc': 30,
        'show': 48,
        'palf': 50,
        'ntscf': 60,
    }
    _inverseFpsMap = {}
    for _i in _fpsMap.keys():
        _inverseFpsMap[_fpsMap[_i]] = _i

    def fps(self):
        r = self._cmds.currentUnit(fullName=True, query=True, time=True)
        return self._fpsMap.get(r)

    def setFps(self, value):
        value = self._inverseFpsMap.get(value)
        self._cmds.currentUnit(time=value)

    def resolution(self):
        width = self._cmds.getAttr('defaultResolution.width')
        height = self._cmds.getAttr('defaultResolution.height')
        return width, height

    def setResolution(self, width, height):
        self._cmds.setAttr('defaultResolution.width', width)
        self._cmds.setAttr('defaultResolution.height', height)

    def currentFrame(self):
        return self._cmds.currentTime(query=True)

    def frameRange(self):
        minT = self._cmds.playbackOptions(query=True, minTime=True)
        maxT = self._cmds.playbackOptions(query=True, maxTime=True)
        return [int(minT), int(maxT)]

    def setFrameRange(self, firstFrame, lastFrame):
        self._cmds.playbackOptions(minTime=firstFrame,
                                   maxTime=lastFrame,
                                   animationStartTime=firstFrame,
                                   animationEndTime=lastFrame)

    def filename(self):
        filename = os.path.basename(self.filepath())
        return filename

    def filepath(self):
        return self._cmds.file(query=True, location=True)

    def fileType(self, path=''):
        if not path:
            path = self.filepath()

        exts = {
            'ma': 'mayaAscii',
            'mb': 'mayaBinary',
        }
        ext = os.path.splitext(path)[1].replace('.', '')
        if exts.has_key(ext):
            typ = exts[ext]
        else:
            typ = ''
        return typ

    def hasUnsavedChanges(self):
        '''Checks whether or not there're unsaved changes.'''
        if self._cmds.file(query=True, modified=True):
            return True  # have change and don't save
        else:
            return False

    def isUntitled(self):
        '''Checks whether or not the current file is untitled.'''
        if not self._cmds.file(query=True, sceneName=True):
            return True
        else:
            return False

    def sceneUnit(self):
        '''Gets the linear unit of the current scene.'''
        # self._cmds.currentUnit(fullName=True, query=True, linear=True)
        # self._cmds.currentUnit(fullName=True, query=True, angle=True)
        # self._cmds.currentUnit(fullName=True, query=True, time=True)
        # self._cmds.currentUnit(time='ntsc')
        # self._cmds.currentUnit(angle='degree')
        # self._cmds.currentUnit(linear='in')
        return self._cmds.currentUnit(fullName=True, query=True, linear=True)

    def setSceneUnit(self, value):
        '''
        Sets the current linear unit. Valid strings are:
            [mm | millimeter | cm | centimeter | m | meter | km | kilometer |
             in | inch | ft | foot | yd | yard | mi | mile]
        '''
        self._cmds.currentUnit(linear=value)

    # ---------------------------------- Input and Output -------------------------------

    def new(self, force=False):
        self._cmds.file(force=force, newFile=True, prompt=False)
        return True

    def open(self, path, loadReferenceDepth="all", force=False):
        self._cmds.file(path, force=force, open=True, prompt=False,
                        loadReferenceDepth=loadReferenceDepth, ignoreVersion=True)
        return True

    def hasSavingError(self):
        '''
        Sometimes we can open the file but with RuntimeError.
        For this situation, when we try to save the file,
        we got an error below:
            # Error: line 1: A file must be given a name before saving. Use file -rename first, then try saving again.
            # Traceback (most recent call last):
            #   File "<maya console>", line 1, in <module>
            # RuntimeError: A file must be given a name before saving. Use file -rename first, then try saving again. #

        The current filepath has been changed on the window title,
        but it seems that the maya api doesn't get this update.

        This funtion will try to get that type of error.
        '''
        self._cmds.file(force=True, save=True, prompt=False)

    def save(self, force=False, type=''):
        if type:
            self._cmds.file(force=force, save=True, prompt=False, type=type)
        else:
            self._cmds.file(force=force, save=True, prompt=False)

        return True

    def saveAs(self, path, force=False):
        self._cmds.file(rename=path)

        typ = self.fileType(path)
        if typ:
            self.save(force=force, type=typ)
        else:
            self.save(force=force)
        return True

    def close(self):
        pass

    def exit(self):
        pass

    def setProject(self, path):
        '''Sets project folder for the scene.'''
        path = path.replace('\\', '/')
        cmd = 'setProject "%s";' % path
        self._mel.eval(cmd)

    def getSceneHierarchy(self):
        all = self._cmds.ls(type="transform")
        other = ["front", "persp", "side", "top"]
        for i in other:
            all.remove(i)
        parentHierarchy = []
        for i in all:
            A = self._cmds.listRelatives(i, p=1)
            if A == None:  # get all parent hierarchy
                parentHierarchy.append(i)
        return parentHierarchy

    def mergeImport(self, path):
        def changeHierarchy(oldH, newH):
            newLay = self._cmds.listRelatives(newH, c=1)
            oldLay = self._cmds.listRelatives(oldH, c=1)

            if not newLay:
                newLay = []

            if not oldLay:
                oldLay = []

            # print newLay,oldLay,"_____________________"
            for nlay in newLay:
                nlay2 = nlay[(nlay.index(":") + 1):]
                # print "nlay:",nlay
                if nlay2 in oldLay:
                    oldH2 = oldH + "|" + nlay2
                    newH2 = newH + "|" + nlay
                    if self._cmds.nodeType(newH2) != "mesh":
                        # print newH2
                        changeHierarchy(oldH2, newH2)
                    else:
                        root = self._pm.PyNode(newH2)
                        A = root.listRelatives(ap=True)
                        objectName = A[0].longName()
                        # print objectName
                        rootHierar = self._pm.PyNode(oldH2)
                        B = rootHierar.listRelatives(ap=True)
                        shape = B[0].longName()
                        shapeList = shape.split("|")
                        moveHierarchy = ""
                        for hiera in shapeList:
                            if hiera != "":
                                if hiera != shapeList[-1]:
                                    moveHierarchy = moveHierarchy + "|" + hiera

                        # print objectName,"-->",moveHierarchy
                        self._cmds.parent(objectName, moveHierarchy)
                        oldName = objectName.split("|")[-1]
                        newName = oldName.split(":")[-1]
                        self._cmds.rename(oldName, newName)
                else:
                    # print nlay,"-->",oldH
                    self._cmds.parent(nlay, oldH)
                    oldName = nlay.split("|")[-1]
                    newName = oldName.split(":")[-1]
                    self._cmds.rename(oldName, newName)
                    listChild = self._cmds.listRelatives(newName, ad=1)
                    for child in listChild:
                        newChild = child.split(":")[-1]
                        try:
                            self._cmds.rename(child, newChild)
                        except:
                            pass

        oldH = self.getSceneHierarchy()

        newNamespace = self.normalImport(path)

        newH = self.getSceneHierarchy()

        for i in oldH:
            newH.remove(i)

        # print oldH,newH

        result = []
        for new in newH:
            # a1
            if ":" in new:
                lenN = (new.index(":") + 1)
                new2 = new[lenN:]
                if new2 in oldH:
                    # print [new2],[new]
                    oldHierar = new2
                    newHierar = new
                    changeHierarchy(oldHierar, newHierar)

                    result.append(new)
                    self._cmds.delete(new)

        if result == []:
            self.removeObjectNamespaces(newNamespace)

        return result

    def normalImport_bak(self, path, removeNamespace=False):
        oldNamespaces = self._cmds.namespaceInfo(lon=True)

        self._cmds.file(path, i=True, ignoreVersion=True,
                        renameAll=True, mergeNamespacesOnClash=False,
                        options="v=0;", preserveReferences=True,
                        namespace='')

        newNamespaces = self._cmds.namespaceInfo(lon=True)
        for old in oldNamespaces:
            newNamespaces.remove(old)

        if newNamespaces:
            namespace = newNamespaces[0]

            if removeNamespace:
                self.removeObjectNamespaces(namespace)
                namespace = ''

        else:
            namespace = ''

        return namespace

    def normalImport(self, path, removeNamespace=False):
        oldNamespaces = self._cmds.namespaceInfo(lon=True)

        self._cmds.file(path, i=True, ignoreVersion=True,
                        renameAll=True, mergeNamespacesOnClash=True,
                        options="v=0;", preserveReferences=True,
                        namespace=':')

        newNamespaces = self._cmds.namespaceInfo(lon=True)
        for old in oldNamespaces:
            newNamespaces.remove(old)

        if newNamespaces:
            namespace = newNamespaces[0]

            if removeNamespace:
                self.removeObjectNamespaces(namespace)
                namespace = ''

        else:
            namespace = ''

        return namespace

    def import_(self, path, removeNamespace=False):
        oldH = self.getSceneHierarchy()

        if oldH:
            if removeNamespace:
                option = 'merge'
            else:
                option = 'normal'
        else:
            option = 'normal'

        if option == 'merge':
            # print 'merge'
            self.mergeImport(path)
            namespace = ''

        else:
            # print 'normal'
            namespace = self.normalImport(path, removeNamespace)

        info = {
            'namespace': namespace.lstrip(':'),
            'path': path
        }
        return info

    def importAbc(self, path, groupOption=None, displayMode=None):
        self._cmds.loadPlugin("AbcImport")
        self._cmds.AbcImport(path, mode=True)
        return True

    def importGpuCache(self, path, name=''):
        '''Import gpu cache into the scene.'''
        self._cmds.loadPlugin("gpuCache")

        if not name:
            name = os.path.splitext(os.path.basename(path))[0]

        # print 'path:',path
        # print 'name:',name

        transNode = self._cmds.createNode('transform', name=name)
        gpuNode = self._cmds.createNode('gpuCache', name=transNode + 'Shape', parent=transNode)
        self._cmds.setAttr('%s.cacheFileName' % gpuNode, path, type='string')

        info = {
            'node': gpuNode,
            'namespace': '',
            'ref_path': path,
            'path': path
        }
        return info

    def importCamera(self, template, srcName, dstName):
        self._cmds.file(template, i=True)
        self.rename(srcName, dstName)

    def rename(self, src, dst):
        return self._cmds.rename(src, dst)

    def exportFbx(self, path):
        self._cmds.file(path, force=True,
                        options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1",
                        type="FBX export", pr=True, ea=True)

    def exportAbc(self, path, singleFrame=False, frameRange=None, objects=[], first_frame="",
                  options=['-ro', '-stripNamespaces', '-uvWrite', '-worldSpace', '-eulerFilter',
                           '-dataFormat ogawa', '-writeVisibility'],
                  deleteArnoldAttr=False):
        '''Exports abc cache file.'''
        # AbcExport -j "-frameRange 1 34 -dataFormat ogawa -root |camera:tst_001_01 -root |dog:dog -file C:/Users/nian/Documents/maya/projects/default/cache/alembic/test.abc";

        # Get arguments
        if singleFrame:
            frameRange = [self.currentFrame(), self.currentFrame()]
        elif frameRange == None:
            frameRange = self.frameRange()

        # print frameRange
        if first_frame:
            args = '-frameRange %s %s ' % (first_frame, frameRange[1])
        else:
            args = '-frameRange %s %s ' % (frameRange[0], frameRange[1])

        if type(options) in (list, tuple):
            options = ' '.join(options)

        if options:
            args += options + ' '

        for obj in objects:
            args += '-root %s ' % obj

        plugin_list = self._cmds.pluginInfo(query=True, listPlugins=True)

        if not deleteArnoldAttr:
            if 'mtoa' in plugin_list:
                args += ' -attr aiSubdivType -attr aiSubdivIterations '

        import getpass
        args += "-file '%s' " % ("C:/Users/%s/haha.abc" % (getpass.getuser()))

        if 'AbcExport' not in plugin_list:
            self._cmds.loadPlugin("AbcExport")

        # Get cmd
        cmd = 'AbcExport -j "%s";' % args
        print "cmd:", cmd
        print "right path:", path
        self._pm.mel.eval(cmd)
        shutil.move("C:/Users/%s/haha.abc" % (getpass.getuser()), path)

    def exportGpuCache(self, path, singleFrame=False, frameRange=None, objects=[]):
        '''Exports gpu cache abc file.'''
        # gpuCache -startTime 1 -endTime 1 -optimize -optimizationThreshold 40000 -writeMaterials -dataFormat ogawa -directory "C:/Users/nian/jinxi/tests" -fileName "sphere_gpu" pSphere1;
        # gpuCache -startTime 1 -endTime 1 -optimize -optimizationThreshold 40000 -writeMaterials -dataFormat ogawa -directory "C:/Users/nian/jinxi/tests" -fileName "sphere_gpu" -saveMultipleFiles false pCone1 pSphere1
        # gpuCache -startTime 60 -endTime 60 -optimize -optimizationThreshold 40000 -writeMaterials -dataFormat ogawa -directory "C:/Users/nian/jinxi/tests" -fileName "building_gpu" -allDagObjects ;

        # Try to load the gpuCache plugin
        self._cmds.loadPlugin("gpuCache")

        # Get arguments
        if singleFrame:
            frameRange = [self.currentFrame(), self.currentFrame()]
        elif frameRange == None:
            frameRange = self.frameRange()

        folder = os.path.dirname(path)
        baseName = os.path.splitext(os.path.basename(path))[0]

        # print frameRange
        args = '-startTime %s -endTime %s ' % (frameRange[0], frameRange[1])
        args += '-optimize -optimizationThreshold 40000 -writeMaterials -dataFormat ogawa '
        args += '-directory "%s" -fileName "%s" ' % (folder, baseName)

        if objects:
            objects = ' '.join(objects)
            args += '-saveMultipleFiles false %s' % objects
        else:
            args += '-allDagObjects'

        # Get cmd
        cmd = 'gpuCache %s;' % args

        self._pm.mel.eval(cmd)

    def exportSelected(self, path):
        typ = self.fileType(path)
        if typ:
            self._cmds.file(path, force=True, preserveReferences=True,
                            exportSelected=True, typ=typ)
        else:
            self._cmds.file(path, force=True, preserveReferences=True,
                            exportSelected=True)

    def exportAll(self, path):
        typ = self.fileType(path)
        if typ:
            self._cmds.file(path, force=True, preserveReferences=True,
                            exportAll=True, typ=typ)
        else:
            self._cmds.file(path, force=True, preserveReferences=True,
                            exportAll=True)

    def exportRedshiftProxy(self, path, singleFrame=True, frameRange=None, objects=[]):
        self._cmds.loadPlugin("redshift4maya")

        options = "exportConnectivity=0;enableCompression=1;"
        if singleFrame == False and type(frameRange) in (tuple, list) and len(frameRange) > 1:
            keys = (frameRange[0], frameRange[1])
            options1 = "startFrame=%d;endFrame=%d;frameStep=0.5;"
            options1 = options1 % keys
            options = options1 + options

        if not objects:
            objects = self._cmds.ls(type='mesh')

        self.clearSelection()
        self.select(objects)

        # print 'objects:',objects

        self._cmds.file(path, force=True, options=options, typ="Redshift Proxy",
                        preserveReferences=True, exportSelected=True)

        self.clearSelection()

    def exportRedshiftProxyScene(self, path, singleFrame=True, frameRange=None, objects=[]):
        # Export redshift proxy
        kwargs = vars().copy()
        del kwargs['self']

        prefix = os.path.splitext(path)[0]
        rsPath = prefix + '.rs'

        kwargs['path'] = rsPath
        self.exportRedshiftProxy(**kwargs)

        # Import redshift proxy
        basename = os.path.basename(prefix)
        r = self._mel.eval('redshiftCreateProxy;')
        # r: [u'redshiftProxy2',
        #     u'redshiftProxyPlaceholderShape1',
        #     u'|redshiftProxyPlaceholder1']
        newName = self.rename(r[2], basename + '_redshiftProxy')

        self._cmds.setAttr('%s.fileName' % r[0], rsPath, type='string')
        self._cmds.setAttr("%s.displayMode" % r[0], 1)

        # Export the node to a ma file
        self.clearSelection()
        self.select(newName)
        self.exportSelected(path)
        self.clearSelection()

        # print 'newName:',newName

        # Delete the proxy node
        self.delete(newName)

    def makeBoundingbox(self, root, nameSuffix='_BBox', single=True,
                        keepOriginal=True):
        kwargs = vars().copy()
        del kwargs['self']
        del kwargs['root']
        r = self._cmds.geomToBBox(root, **kwargs)

        if single:
            return r[0]
        else:
            return root + nameSuffix

    def exportBoundingbox(self, path, root, nameSuffix='_BBox'):
        kwargs = vars().copy()
        kwargs['single'] = True
        kwargs['keepOriginal'] = True
        del kwargs['self']
        del kwargs['path']

        boxRootNode = self.makeBoundingbox(**kwargs)

        # Assign them a default material
        bboxNode = self._cmds.ls(boxRootNode, dag=True, geometry=True)
        self._cmds.sets(bboxNode, forceElement="initialShadingGroup")

        self.exportAbc(path, singleFrame=True, objects=[boxRootNode])

        self.delete(boxRootNode)

    def createAssemblyDefinition(self, name, files=[], actived=''):
        '''
        files is a list of dictionaries of representation info.
        {
            'name': 'abc',
            'type': 'Cache',
            'path': '',
        }
        type support options below:
            Cache
            Scene

        '''

        cmds = self._cmds

        cmds.loadPlugin("sceneAssembly")

        node = cmds.assembly(name=name, type='assemblyDefinition')

        for f in files:
            kwargs = {
                'edit': True,
                'createRepresentation': f['type'],
                'repName': f['name'],
            }
            path = f.get('path')
            if path:
                kwargs['input'] = path

            cmds.assembly(node, **kwargs)

        if actived:
            cmds.assembly(node, edit=True, active=actived)

        return node

    def createAssemblyDefinitionScene(self, path, name='', files=[],
                                      actived=''):
        kwargs = vars().copy()
        del kwargs['self']
        del kwargs['path']

        if not name:
            name = os.path.splitext(os.path.basename(path))[0]
        kwargs['name'] = name

        node = self.createAssemblyDefinition(**kwargs)

        self.clearSelection()
        self.select(node)
        self.exportSelected(path)

        self.delete(node)

    def createAssemblyReference(self, adPath, name='', actived=''):
        cmds = self._cmds

        if not name:
            name = os.path.splitext(os.path.basename(adPath))[0]

        node = cmds.assembly(name=name, type='assemblyReference')
        cmds.setAttr(node + '.definition', adPath, type="string")

        if actived:
            cmds.assembly(node, edit=True, active=actived)

        return node

    def createAssemblyReferenceScene(self, path, adPath, name='', actived=''):
        kwargs = vars().copy()
        del kwargs['self']
        del kwargs['path']

        if not name:
            name = os.path.splitext(os.path.basename(adPath))[0]
        kwargs['name'] = name

        node = self.createAssemblyReference(**kwargs)

        self.clearSelection()
        self.select(node)
        self.exportSelected(path)

        self.delete(node)

    def getTopReferencedObjects(self, refNode):
        '''Gets the top level objects for the referenced file.'''
        allObjectHierarchy = []
        all = self._cmds.ls(type="mesh")
        for i in all:
            root = self._pm.PyNode(i)
            A = root.listRelatives(ap=True)
            objectName = A[0].longName()
            # print objectName
            masterHierarchy = objectName.split("|")[1]

            if masterHierarchy not in allObjectHierarchy:
                allObjectHierarchy.append(masterHierarchy)

        # print
        # print 'refNode:',refNode
        importedNodes = self._cmds.referenceQuery(refNode, nodes=True)
        # print 'importedNodes:',importedNodes

        result = []
        for r in importedNodes:
            # print referenceNode[0]
            if r in allObjectHierarchy:
                result.append(r)

        return result

    def reference(self, path, groupOption=2, displayMode=None, removeNamespace=None, getTopObj=False,
                  loadReferenceDepth=False):
        '''
        file -r -type "mayaAscii"  -ignoreVersion -gl
        -mergeNamespacesOnClash false -namespace "laserwave_mod_v006"
        -options "v=0;"
        "C:/Users/nian/jinxi/develop/project_server/BL/assets/ep001/chars/laserwave/mod/work/laserwave_mod_v006.ma";
        '''
        self._cmds.loadPlugin("AbcImport")

        format = os.path.splitext(path)
        if format == '.ma':
            type = 'mayaAscii'
        elif format == '.mb':
            type = 'mayaBinary'
        elif format == '.abc':
            type = 'Alembic'
        else:
            type = 'mayaAscii'

        if not removeNamespace:
            filename = os.path.basename(path)
            namespace = os.path.splitext(filename)[0]
            if not loadReferenceDepth:
                p = self._cmds.file(path, reference=True, ignoreVersion=True,
                                    groupLocator=True, mergeNamespacesOnClash=False,
                                    options="v=0;", namespace=namespace,
                                    # type=type,
                                    )
            else:
                p = self._cmds.file(path, reference=True, ignoreVersion=True,
                                    groupLocator=True, mergeNamespacesOnClash=False,
                                    options="v=0;", namespace=namespace,
                                    loadReferenceDepth=loadReferenceDepth,
                                    # type=type,
                                    )
            node = self._cmds.referenceQuery(p, referenceNode=True)
            namespace = self._cmds.referenceQuery(p, namespace=True)
            if getTopObj:
                objects = self.getTopReferencedObjects(node)
            else:
                objects = ''
            # print namespace
            info = {
                'top_objects': objects,
                'node': node,
                'namespace': namespace.lstrip(':'),
                'ref_path': p,
                'path': path
            }
        else:
            if not loadReferenceDepth:
                p = self._cmds.file(path, reference=True, ignoreVersion=True,
                                    groupLocator=True, mergeNamespacesOnClash=True,
                                    options="v=0;", namespace=":", type=type)
            else:
                p = self._cmds.file(path, reference=True, ignoreVersion=True,
                                    groupLocator=True, mergeNamespacesOnClash=True,
                                    options="v=0;", namespace=":", type=type,
                                    loadReferenceDepth=loadReferenceDepth)
            node = self._cmds.referenceQuery(p, referenceNode=True)
            if getTopObj:
                objects = self.getTopReferencedObjects(node)
            else:
                objects = ''
            info = {
                'top_objects': objects,
                'node': node,
                'namespace': None,
                'ref_path': p,
                'path': path
            }
        return info

    def referenceCamera(self, path, resolution=None):
        return self.reference(path)

    def referenceAssembly(self, path, name='', actived=''):
        cmds = self._cmds

        if not name:
            name = os.path.splitext(os.path.basename(path))[0]

        node = cmds.assembly(name=name, type='assemblyReference')
        cmds.setAttr(node + '.definition', path, type="string")

        if actived:
            cmds.assembly(node, edit=True, active=actived)

        info = {
            'node': node,
            'namespace': '',
            'ref_path': path,
            'path': path
        }
        return info

    def removeReference(self, refPath):
        self._cmds.file(refPath, removeReference=True)

    def getReferences(self):
        result = []
        allRe = self._cmds.ls(references=True)
        if allRe:
            for rn in allRe:
                try:
                    refPath = self._cmds.referenceQuery(rn, filename=True)
                    # print 'refPath:',refPath
                except:
                    continue

                if "{" in refPath:
                    path = refPath[:refPath.index("{")]
                else:
                    path = refPath

                if os.path.exists(path):
                    namespace = self._cmds.referenceQuery(rn, namespace=True)
                else:
                    namespace = os.path.splitext(os.path.basename(path))[0]

                info = {
                    'node': rn,
                    'parent': '',
                    'ref_path': refPath,
                    'path': path,
                    'name': rn,
                    'namespace': namespace.replace(':', ''),
                    'filetype': os.path.splitext(path)[-1].replace('.', ''),
                    'node_type': 'reference',
                }
                result.append(info)

        return result

    def isAlreadyReferenced(self, f):
        if f in self._cmds.file(r=True, q=True):
            return self._cmds.referenceQuery(f, namespace=True)

        return False

    def changeReference_bak1(self, path, loadReference):
        '''loadReference is nameSpace'''
        allRe = self._cmds.ls(references=True)
        if allRe:
            for rn in allRe:
                f = self._cmds.referenceQuery(rn, ns=True)
                # print f,RN
                getRef = ":%s" % loadReference
                if f == getRef:
                    # print rn
                    self._cmds.file(path, loadReference=rn, options="v=0")

    def setReferencePath(self, ref, path):
        '''Sets the reference path to a new path.'''
        self._cmds.file(path, loadReference=ref, options="v=0")

    def getReferenceObjects(self, typ='mesh'):
        allObjectHierarchy = []
        all = self._cmds.ls(type=typ)
        for i in all:
            root = self._pm.PyNode(i)
            A = root.listRelatives(ap=True)
            objectName = A[0].longName()
            # print objectName
            # masterHierarchy = objectName.split("|")[1]

            # jxy
            if "PROPS_GRP" not in objectName:
                masterHierarchy = objectName.split("|")[1]
            else:
                masterHierarchy = objectName.split("|")[3]
            # jxy

            if masterHierarchy not in allObjectHierarchy:
                allObjectHierarchy.append(masterHierarchy)

        # print
        # print 'allObjectHierarchy:'
        # print allObjectHierarchy

        rnHierarchy = []
        paths = []
        refNodes = []

        allRn = self._cmds.ls(type="reference")
        for j in allRn:
            try:
                # print
                # print 'ref:',j

                referenceNode = self._cmds.referenceQuery(j, nodes=True)
                # print
                # print 'referenceNode:',referenceNode

                refPath = self._cmds.referenceQuery(j, filename=True)
                # print 'refPath:',refPath
                if "{" in refPath:
                    path = refPath[:refPath.index("{")]
                else:
                    path = refPath

                for r in referenceNode:
                    # print referenceNode[0]
                    if r in allObjectHierarchy:
                        rnHierarchy.append(r)
                        paths.append(path)
                        refNodes.append(j)

            except:
                # print j
                pass

        # rnHierarchy = list(set(rnHierarchy))

        # print
        # print 'rnHierarchy:'
        # print rnHierarchy

        result = []
        j = 0
        for i in rnHierarchy:
            name = self.removeStringNamespace(i)
            namespace = ':'.join(i.split(':')[:-1])
            info = {
                'node': i,
                'name': name,
                'code': name,
                'full_name': i,
                'namespace': namespace,
                'path': paths[j],
                'ref_node': refNodes[j],
                'ref_path': paths[j],
                'transform_node': i,
                'filetype': os.path.splitext(paths[j])[-1].replace('.', ''),
                'node_type': 'reference',
            }

            if info not in result:
                result.append(info)

            j += 1

        return result

    def getGpuCaches(self):
        result = []
        typ = "gpuCache"
        allGpuCache = self._cmds.ls(type=typ, long=True)
        for catch in allGpuCache:
            # Get the transform node
            r = self._cmds.listRelatives(catch, allParents=True, fullPath=True)
            if r:
                tranform = r[0]
            else:
                tranform = ''

            catchFile = self._cmds.getAttr("%s.cacheFileName" % catch)
            d = {
                'node': catch,
                'path': catchFile,
                'ref_path': catchFile,
                'parent': tranform,
                'name': tranform.split('|')[-1],
                'full_name': catch,
                'namespace': self.getObjectNamespace(tranform),
                'filetype': os.path.splitext(catchFile)[-1].replace('.', ''),
                'node_type': typ,
                'transform_node': tranform,
            }
            result.append(d)

        return result

    def setGpuCachePath(self, obj, path):
        self._cmds.setAttr('%s.cacheFileName' % obj, path, type='string')

    def getAssemblyReferences(self):
        result = []
        typ = 'assemblyReference'
        temp = self._cmds.ls(type=typ, long=True)

        for t in temp:
            # Get the transform node
            r = self._cmds.listRelatives(t, allParents=True, fullPath=True)
            if r:
                tranform = r[0]
            else:
                tranform = ''

            path = self._cmds.getAttr("%s.definition" % t)
            d = {
                'node': t,
                'path': path,
                'ref_path': path,
                'parent': tranform,
                'name': t.split('|')[-1],
                'full_name': t,
                'namespace': self.getObjectNamespace(t),
                'filetype': os.path.splitext(path)[-1].replace('.', ''),
                'node_type': typ,
                'transform_node': t,
            }
            result.append(d)

        return result

    def setAssemblyReferencePath(self, obj, path):
        self._cmds.setAttr('%s.definition' % obj, path, type='string')

    # ---------------------------------- Geometry -------------------------------

    def getTopLevelObjectsOfMeshes(self):
        '''Gets top level objects of the meshes.'''
        temp = self._cmds.ls(type='mesh', long=True)
        result = []
        for t in temp:
            # u'|cat_GRP|body|bodyShape'
            top = t.split('|')[1]
            if top not in result:
                result.append(top)
        return result

    def find(self, name, namespace='', type='transform',
             fullPath=False):
        '''Finds the objects in the scene.'''
        temp = self._cmds.ls(type=type, long=True)
        result = []
        for t in temp:
            # u'|cat_GRP|body|bodyShape'
            obj = t.split('|')[-1]

            objNamespace = self.getObjectNamespace(obj)
            objName = obj.replace(objNamespace, '').replace(':', '').strip('|')

            # print 'objNamespace:',objNamespace
            # print 'objName:',objName

            go = False
            if name == objName:
                if namespace:
                    if namespace == objNamespace:
                        go = True
                else:
                    go = True

            if go:
                if fullPath:
                    obj = t

                if obj not in result:
                    result.append(obj)

        return result

    def findObjects(self, name):
        '''
        Finds objects for the object with the name. If the object does not exist,
        try to find it from referenced nodes.
        '''
        if self.exists(name):
            return [name]

        result = []
        for ref in self.getReferenceObjects():
            # print 'ref:',ref
            if ref['name'] == name:
                result.append(ref['full_name'])
        return result

    def select(self, path, replace=True, add=False, noExpand=False):
        if path and type(path) in (str, unicode, list):
            self._cmds.select(path, replace=replace, add=add,
                              noExpand=noExpand)

    def clearSelection(self):
        self._cmds.select(deselect=True)

    def delete(self, objects):
        objs = []
        if type(objects) == list:
            for obj in objects:
                if self.exists(obj):
                    objs.append(obj)
        elif type(objects) in (str, unicode):
            if self.exists(objects):
                objs.append(objects)

        if objs:
            self._cmds.delete(objs)

    def exists(self, path):
        return self._cmds.objExists(path)

    def getObjects(self, type):
        '''Gets one type of objects.'''
        return self._cmds.ls(type=type)

    def getSets(self, root='', removeNamespace=True,
                types=['objectSet'], parms=[]):
        '''
        Gets scene sets of the type.
        If root is not an empty string, it will only list the
        sets which has objects under the root node.

        types has options below:
            objectSet
            shadingEngine
        If types is an empty list, it will get all of sets.

        Returns a list of dictionaries.
        Example:
            - name: Plastic
              parms:
                level: 0.5
              components:
                - '|dog|base|pSphere1'

            - name: Wood
              parms:
                level: 0.6
              components:
                - '|dog|base|pCone1'
        '''
        temp = self._cmds.ls(sets=True, showType=True)
        sets = []
        ts = []

        for i in range(0, len(temp), 2):
            node = temp[i]
            typ = temp[(i + 1)]

            if 'default' in node or 'initial' in node:
                pass

            else:
                if types:
                    if typ in types:
                        sets.append(node)
                        ts.append(typ)
                else:
                    sets.append(node)
                    ts.append(typ)

        # print sets
        if root:
            if not root.startswith('|'):
                root = '|' + root

        # print 'root:',root

        result = []
        i = 0
        for s in sets:
            # Get parms of the set
            parms1 = {}
            if parms:
                for parm in parms:
                    value = self.getAttribute(s, parm)
                    if value != None:
                        parms1[parm] = value

            # Get components of the set
            components = []

            temp = self._cmds.sets(s, q=True)
            if temp:
                for t in temp:
                    objs = self._cmds.ls(t, long=True)
                    for obj in objs:
                        if root:
                            if obj.startswith(root):
                                if removeNamespace:
                                    obj = self.removeStringNamespace(obj)
                                components.append(obj)
                        else:
                            if removeNamespace:
                                obj = self.removeStringNamespace(obj)
                            components.append(obj)

            info = {
                'name': s,
                'type': ts[i],
                'parms': parms1,
                'components': components
            }
            result.append(info)

            i += 1

        return result

    def createSet(self, name, type='objectSet', components=[]):
        '''
        Creates one set with the components.
        Supported types:
            objectSet
            RedshiftObjectId
            RedshiftMeshParameters
            RedshiftVisibility
            RedshiftMatteParameters
        '''
        codes = ''

        if type == 'objectSet':
            self._cmds.sets(components, name=name)
            return

        elif type == 'RedshiftObjectId':
            codes = 'redshiftCreateObjectIdNode'

        elif type == 'RedshiftMeshParameters':
            codes = 'redshiftCreateMeshParametersNode'

        elif type == 'RedshiftVisibility':
            codes = 'redshiftCreateVisibilityNode'

        elif type == 'RedshiftMatteParameters':
            codes = 'redshiftCreateMatteParametersNode'

        if codes:
            codes += '()'
            newNode = self._mel.eval(codes)
            # print [newNode]
            self._cmds.rename(newNode, name)
            self._cmds.sets(components, addElement=name)

    def createSets(self, sets, namespace=''):
        '''
        Creates scene sets.

        sets is a list of dictionaries or a file with json data.
        Example:
            - name: Plastic
              type: objectSet
              parms:
                level: 0.5
              components:
                - '|dog|base|pSphere1'

            - name: Wood
              type: RedshiftObjectId
              parms:
                level: 0.6
              components:
                - '|dog|base|pCone1'

        redshift: redshiftCreateObjectIdNode()

        '''
        if type(sets) in (str, unicode) and os.path.isfile(sets):
            f = open(sets, 'r')
            t = f.read()
            f.close()
            sets = json.loads(t)

        if not type(sets) == list:
            return

        for info in sets:
            objs = []

            for obj in info['components']:
                if namespace:
                    obj = self.addObjectNamespace(obj, namespace)
                if self.exists(obj):
                    objs.append(obj)

            name = self.addObjectNamespace(info['name'], namespace)
            if not self.exists(name):
                self.createSet(name, type=info['type'], components=objs)

                # Set parms
                parms = info.get('parms')
                if parms:
                    for parm in parms.keys():
                        self.setAttribute(name, parm, parms[parm])

    def getChildren(self, path, type=''):
        nodes = self._pm.ls(path)
        if nodes:
            result = []
            for n in nodes[0].getChildren():
                if type:
                    # print
                    # print 'node:',n.fullPath()
                    # print 'nodeType:',n.nodeType()

                    if n.nodeType() == type:
                        result.append(n)
                else:
                    result.append(n)

            return result
        else:
            return []

    def getAllSubChildren(self, path, type=''):
        result = []

        def get(p):
            r = self.getChildren(p)
            for n in r:
                if type:
                    # print
                    # print 'node:',n.fullPath()
                    # print 'nodeType:',n.nodeType()

                    if n.nodeType() == type:
                        result.append(n.fullPath())
                else:
                    result.append(n.fullPath())

                get(n.fullPath())

        get(path)

        return result

    def getCameras(self, includeHidden=False):
        allCamera = self._cmds.ls(cameras=True, long=True)
        defaultCamera = ['|persp', '|front', '|side', '|top',
                         '|back', '|left', '|right', '|bottom']

        cameraList = []
        for i in allCamera:
            # print i
            cameraName = self._cmds.listRelatives(i, allParents=True, fullPath=True)[0]
            # print cameraName
            if cameraName not in defaultCamera:
                if includeHidden:
                    cameraList.append(cameraName)
                else:
                    visi = self.getAttribute(cameraName, 'visibility')
                    if visi:
                        cameraList.append(cameraName)

        cameraL = []
        for i in cameraList:
            cameraDic = {}
            name = i.split('|')[-1]
            cameraDic['full_path'] = i
            cameraDic['namespace'] = self.getObjectNamespace(i)
            cameraDic['name'] = name
            cameraDic['code'] = name
            cameraL.append(cameraDic)

        return cameraL

    def getShots(self):
        result = []
        allShots = self._cmds.sequenceManager(listShots=True)
        if not allShots:
            return result

        for i in allShots:
            dic = {}
            startTime = self._cmds.shot(i, q=True, startTime=True)
            endTime = self._cmds.shot(i, q=True, endTime=True)
            sequenceStartTime = self._cmds.shot(i, q=True, sequenceStartTime=True)
            sequenceEndTime = self._cmds.shot(i, q=True, sequenceEndTime=True)
            cameraName = self._cmds.shot(i, q=True, currentCamera=True)
            shotName = self._cmds.getAttr("%s.shotName" % i)
            dic["name"] = shotName
            dic["first_frame"] = sequenceStartTime
            dic["last_frame"] = sequenceEndTime
            dic["sequence_start_frame"] = sequenceStartTime
            dic["sequence_end_frame"] = sequenceEndTime
            dic["camera"] = cameraName
            result.append(dic)

        return result

    def getCameraSequenceCurrentFrame(self):
        return self._cmds.sequenceManager(query=True, currentTime=True)

    def getObjectKeyframeRange(self, obj):
        first = self._cmds.findKeyframe(obj, which="first")
        last = self._cmds.findKeyframe(obj, which="last")
        return first, last

    def createHierachy(self, data):
        '''
        Creates nodes with the given data.
        The node types support:
            group
            locator

        Example of the data:
            - name: dog
              type: group
              subs:
                - name: high
                  type: group
                  subs:
                    - name: model
                    - name: rig
                - name: low
                  type: group
                  subs:
                    - name: ctrl
                      type: locator
        '''

        def create(d, parent=''):
            for info in d:
                name = info.get('name')
                if not name:
                    continue

                typ = info.get('type', 'group')
                fullName = '|'.join([parent, name])
                if not self.exists(fullName):

                    if typ == 'group':
                        kwargs = {
                            'name': name,
                            'empty': True,
                        }
                        if parent:
                            kwargs['parent'] = parent

                        self._cmds.group(**kwargs)

                    elif typ == 'locator':
                        newName = self._cmds.spaceLocator(name=name)[0]
                        newName = '|' + newName
                        self._cmds.parent(newName, parent)

                    else:
                        continue

                subs = info.get('subs')
                if subs:
                    create(subs, parent=fullName)

        if data:
            create(data)

    def getExceptionObjects(self, tree):
        '''Gets objects which are not in the hierachy tree.'''

        def check(obj, newList):
            lay = self._cmds.listRelatives(obj, c=1)
            if lay != None:
                for la in lay:
                    try:
                        root = self._pm.PyNode(la)
                        longname = root.longName()
                        if self._cmds.nodeType(longname) != "mesh":
                            # mesh = self._cmds.listRelatives(longname,c=1)
                            # if self._cmds.nodeType(mesh) != "mesh" :
                            #    newList.append(longname)
                            check(longname, newList)
                        else:
                            longN = self._cmds.listRelatives(longname, p=1)
                            root = self._pm.PyNode(longN[0])
                            longN = root.longName()
                            newList.append(longN)

                    except:
                        pass

                if self._cmds.nodeType(lay) == "locator":
                    newList.append(obj)

        def getExcessObject(dic):
            all = self._cmds.ls(type="transform")
            view = ["persp", "top", "front", "side"]
            for i in view:
                all.remove(i)

            lis = []
            for i in all:
                p = self._cmds.listRelatives(i, p=1)
                if p == None:
                    lis.append(i)

            newLis = []
            for i in lis:
                if i not in dic.keys():
                    root = self._pm.PyNode(i)
                    longname = root.longName()
                    # newLis.append(longname)
                    check(longname, newLis)
            return newLis

        return getExcessObject(tree)

    def checkHierachy(self, data):
        '''
        Checks whether the outliner hierachy matches the data.

        The node types support:
            group
            locator

        Example of the data:
            - name: dog
              type: group
              subs:
                - name: high
                  type: group
                  subs:
                    - name: model
                    - name: rig
                - name: low
                  type: group
                  subs:
                    - name: ctrl
                      type: locator

        '''
        result = []

        def check(d, parent=''):
            for info in d:
                name = info.get('name')
                if not name:
                    continue

                typ = info.get('type', 'group')
                fullName = '|'.join([parent, name])
                if not self.exists(fullName):
                    err = "{0} no exists.".format(fullName)
                    result.append(err)

                subs = info.get('subs')
                if subs:
                    check(subs, parent=fullName)

        check(data)

        return result

    def createCamera(self, name):
        r = self._cmds.camera()
        shape = self._cmds.rename(r[1], name + 'Shape')
        cam = self._cmds.rename(r[0], name)
        return [cam, shape]

    def createShot(self, name, firstFrame, lastFrame, camera=None):
        # print vars()
        self._cmds.shot(name, startTime=firstFrame, endTime=lastFrame,
                        sequenceStartTime=firstFrame, sequenceEndTime=lastFrame,
                        currentCamera=camera)

    def createSound(self, startTime, fileName, name):
        soundName = self._cmds.sound(offset=startTime, file=fileName)
        self._cmds.rename(soundName, name)

    def addExtraAttribute(self, objectName, attributeName, attributeValue, dataType='string'):
        '''Adds an extra attribute to the object.'''
        allAttributes = self._cmds.listAttr(objectName)
        if attributeName not in allAttributes:
            self._cmds.addAttr(objectName, shortName=attributeName, dataType=dataType)

        attrName = "%s.%s" % (objectName, attributeName)
        # print 'attrName:',attrName
        self._cmds.setAttr(attributeName, e=True, keyable=True)
        self._cmds.setAttr(attributeName, attributeValue, type=dataType)

    def getAttribute(self, obj, name):
        attr = '%s.%s' % (obj, name)
        if self.exists(attr):
            return self._cmds.getAttr(attr)

    def setAttribute(self, obj, name, value, type=''):
        attr = '%s.%s' % (obj, name)
        if self.exists(attr):
            if type:
                return self._cmds.setAttr(attr, value, type=type)
            else:
                return self._cmds.setAttr(attr, value)

    def getTransform(self, obj):
        '''Gets transform info of the object.'''
        attrs = [
            'translateX', 'translateY', 'translateZ',
            'rotateX', 'rotateY', 'rotateZ',
            'scaleX', 'scaleY', 'scaleZ'
        ]
        result = {}
        for a in attrs:
            v = self.getAttribute(obj, a)
            result[a] = v
        return result

    def setTransform(self, obj, info):
        for a in info.keys():
            self.setAttribute(obj, a, info[a])

    def removeObjectNamespaces(self, namespace):
        '''Removes namespaces of the scene objects.'''
        self._cmds.namespace(removeNamespace=namespace, mergeNamespaceWithParent=True)

    def removeStringNamespace(self, name):
        '''
        Removes namespaces of the name.
        For instance:
            name: |dog:dog|dog:base|dog:box|dog:boxShape
            return: |dog|base|box|boxShape

            name: |dog:box.f[10:13]
            return: |box.f[10:13]
        '''
        splitter = '|'

        pat = re.compile('\w+\.f\[\d+:\d+\]')

        split = name.split(splitter)
        temp = []
        for i in split:
            if i:
                # i: dog:box.f[10:13]
                find = pat.findall(i)
                if find:
                    new = find[-1]

                # Keep the last item
                else:
                    new = i.split(':')[-1]

            else:
                new = i

            temp.append(new)

        return splitter.join(temp)

    def addObjectNamespace(self, name, namespace):
        '''
        Adds namespaces to the name.
        For instance:
            name: |dog|base|box|boxShape
            namespace: dog
            return: |dog:dog|dog:base|dog:box|dog:boxShape

            name: |box.f[10:13]
            namespace: dog
            return: |dog:box.f[10:13]
        '''
        splitter = '|'

        pat = re.compile('[a-zA-Z0-9]+\.f\[\d+:\d+\]')

        split = name.split(splitter)
        temp = []
        for i in split:
            new = i
            if i and namespace:
                new = ':'.join([namespace, i])

            temp.append(new)

        return splitter.join(temp)

    def getObjectNamespace(self, name):
        '''
        Gets namespaces of the name.
        For instance:
            name: |dog:dog|dog:base|dog:box|dog:boxShape
            namespace: dog

            name: |dog:box.f[10:13]
            namespace: dog
        '''
        splitter = '|'

        split = name.strip('|').split(splitter)
        if split:
            obj = split[0]
        else:
            obj = name

        token = obj.split(':')
        if token:
            return ':'.join(token[:-1])
        else:
            return ''

    def getSceneNamespaces(self):
        result = []
        temp = self._cmds.namespaceInfo(lon=1)
        for i in temp:
            if i not in ("UI", "shared"):
                result.append(i)
        # print 'namespaces:',temp
        return result

    def clearSceneNamespaces(self):
        for i in self.getSceneNamespaces():
            try:
                self.removeObjectNamespaces(i)
            except:
                pass

    def getIsolatedVetices(self):
        allObject = []
        allDecimalList = []
        newObjectDic = {}
        objectDic = {}

        all = self._cmds.ls(type="mesh")

        for i in all:
            root = self._pm.PyNode(i)
            A = root.listRelatives(ap=True)
            objectName = A[0].longName()  # .split("|")[-1]
            allObject.append(objectName)

        allObject = list(set(allObject))
        for i in allObject:
            vertexNum = self._cmds.polyEvaluate(i, v=True)
            # print i,vertexNum
            if type(vertexNum) == int:
                decimalList = []
                for ver in range(0, vertexNum):
                    vertexName = i + ".vtx[" + str(ver) + "]"
                    pointPosition = self._cmds.pointPosition(vertexName)

                    decimalList.append(pointPosition)
                objectDic[i] = decimalList

                allDecimalList.append(decimalList)

        for key in objectDic:
            verList = objectDic[key]
            dic = {}

            for i in verList:
                if verList.count(i) > 1:
                    dic[str(i)] = verList.count(i)

            if dic:
                newObjectDic[key] = dic

        return newObjectDic

    def getIsolatedFaces(self):
        errorPoly = []
        all = self._cmds.ls(type="mesh")
        for i in all:
            att = self._cmds.polyEvaluate(i)
            # print i, att
            if att["face"] == 1:
                errorPoly.append(i)
        # print errorPoly

        return errorPoly

    def getNPolygonFaces(self, n=4):
        filterSides = n

        allMultilateralFace = {}
        all = self._cmds.ls(type="mesh")

        for i in all:
            root = self._pm.PyNode(i)
            A = root.listRelatives(ap=True)
            objectName = A[0].longName()  # .split("|")[-1]
            faceNum = self._cmds.polyEvaluate(objectName, f=True)
            if type(faceNum) == int:
                multilateralFace = []
                for face in range(0, faceNum):
                    faceName = objectName + ".f[" + str(face) + "]"
                    edges = self._cmds.polyListComponentConversion(faceName, te=True)
                    vfList = self._cmds.ls(edges, flatten=True)
                    edgesNum = len(vfList)
                    if edgesNum > filterSides:
                        multilateralFace.append(faceName)
                if multilateralFace:
                    allMultilateralFace[objectName] = multilateralFace

        # print allMultilateralFace

        return allMultilateralFace

    def getOverlappedUVs(self):
        return []

    def getUnFreezedObjects(self):
        self._cmds.select(all=True)
        object_name_list = self._cmds.ls(selection=True, transforms=True, geometry=True)
        absent_name = []
        for model_name in object_name_list:
            a = self._cmds.xform(model_name, q=1, ws=1, t=1)
            for xyz in a:
                if int(xyz) != 0:
                    if model_name in absent_name:
                        pass
                    else:
                        absent_name.append(model_name)
                        continue
                else:
                    pass
        self._cmds.select(cl=1)
        return absent_name

    def freezeObjects(self, objects):
        if objects:
            objects = ' '.join(objects)

            cmd = 'makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1 %s;' % objects
            self._mel.eval(cmd)

    def getProblemNormals(self):
        cmd = 'polyCleanupArgList 3 { "1","2","1","0","0","0","0","0","0","1.666667","0","0","0","0.181159","0","1","0" };'
        source = self._mel.eval(cmd)
        model_vtx = []
        model_vtx_name_data = {}
        model_name_list = []
        for q in source:
            name = q.split(".")
            if len(model_name_list) == 0:
                model_name_list.append(name[0])
                model_vtx.append(q)

            else:
                if name[0] in model_name_list:

                    model_vtx.append(q)
                    model_vtx_name_data[name[0]] = model_vtx
                else:

                    model_vtx = []
                    model_name_list.append(name[0])
                    model_vtx.append(q)
        self._cmds.select(cl=1)
        self._cmds.hilite(replace=True)

        return model_name_list

    def repairNormals(self, obj):
        model_name_list = obj
        if type(model_name_list) == list:
            for model_name in model_name_list:
                self._cmds.select(cl=1)
                self._cmds.select(model_name, r=1)
                self._cmds.polyNormal(normalMode=2)
            self._cmds.select(cl=1)

        elif type(model_name_list) == str:
            self._cmds.select(cl=1)
            self._cmds.select(model_name_list, r=1)
            self._cmds.polyNormal(normalMode=2)
            self._cmds.select(cl=1)

    def getNonManifoldObjects(self):
        model_name_list = []
        source = self._mel.eval(
            'polyCleanupArgList 3 { "1","2","1","0","0","0","0","0","0","1.666667","0","0","0","0.181159","0","2","0" };')
        for a in source:
            name = a.split(".")[0]
            if name not in model_name_list:
                model_name_list.append(name)
        return model_name_list

    def getSmallEdges(self):
        model_name_list = []
        source = self._mel.eval(
            'polyCleanupArgList 3 { "1","2","1","0","0","0","0","0","0","1.666667","1","0.0001","0","0.181159","0","-1","0" };')
        for a in source:
            name = a.split(".")[0]
            if name in model_name_list:
                pass
            else:
                model_name_list.append(name)
        self._cmds.select(cl=1)
        self._cmds.hilite(replace=True)
        return model_name_list

    # ---------------------------------- Materials -------------------------------

    def getShadingEngines(self):
        '''Gets shading engine nodes.'''
        result = []

        mats = self._cmds.ls(materials=True)

        try:
            mats.remove("lambert1")
        except:
            pass

        try:
            mats.remove("particleCloud1")
        except:
            pass

        for mat in mats:
            shad = self._cmds.listConnections(mat, type="shadingEngine")
            if shad:
                result.append(shad[0])

        return result

    def getMaterials_current(self, removeNamespace=False):
        '''
        Gets materials to a dictionary of which keys are materials and values are
        shapes and faces.
        Example of the returned dictionary:
            {
                'metal': {
                    'box': ['box.face[1-29]', 'box.face[33]'],
                    'sphere': [],
                }
            }
        '''
        shapList = []
        materDic = {}

        all = self._cmds.ls(materials=True)

        try:
            all.remove("lambert1")
        except:
            pass

        try:
            all.remove("particleCloud1")
        except:
            pass

        for i in all:
            shad = self._cmds.listConnections(i, type="shadingEngine")
            if shad != None:
                meshlist = self._cmds.sets(shad[0], int=shad[0])
                if meshlist != []:
                    materDic[shad[0]] = meshlist
        # print materDic

        for key in materDic.keys():
            for i in materDic[key]:
                if ".f[" in i:
                    shape = self._cmds.listHistory(i, q=1, historyAttr=True)[0].replace(".inMesh", "")
                    shapList.append(shape)
                else:
                    shapList.append(i)
        shapList = list(set(shapList))
        # print shapList
        for key in materDic.keys():
            shapeDic = {}
            for st in shapList:

                A = []
                for i in materDic[key]:
                    if ".f[" in i:
                        shape = self._cmds.listHistory(i, q=1, historyAttr=True)[0].replace(".inMesh", "")

                        root = self._pm.PyNode(shape)
                        mesh = root.listRelatives(ap=True)
                        newH = mesh[0].longName()
                        if "|" in shape:
                            newSha = newH + "|" + shape.split("|")[-1]
                        else:
                            newSha = newH + "|" + shape
                        # print newSha
                        if shape == st:
                            A.append("|" + i)

                            shapeDic[newSha] = A
                    else:

                        root = self._pm.PyNode(i)
                        mesh = root.listRelatives(ap=True)
                        newH = mesh[0].longName()

                        if "|" in i:
                            newSha = newH + "|" + i.split("|")[-1]
                        else:
                            newSha = newH + "|" + i
                        shapeDic[newSha] = []
            # print shapeDic
            materDic[key] = shapeDic

            # print materDic

        result = {}
        if removeNamespace:
            for mat in materDic.keys():
                result[mat] = {}

                for shape in materDic[mat].keys():
                    newShape = self.removeStringNamespace(shape)
                    result[mat][newShape] = []

                    for i in range(len(materDic[mat][shape])):
                        value = materDic[mat][shape][i]
                        newValue = self.removeStringNamespace(value)
                        result[mat][newShape].append(newValue)

        return result

    def getMaterials(self, removeNamespace=False, assetName=''):
        '''
        Gets materials to a dictionary of which keys are materials and values are
        shapes and faces.
        Example of the returned dictionary:
            {
                'metal': {
                    'box': ['box.face[1-29]', 'box.face[33]'],
                    'sphere': [],
                }
            }
        '''
        cmds = self._cmds
        pm = self._pm

        shapList = []
        materDic = {}

        all = cmds.ls(materials=True)

        try:
            all.remove("lambert1")
        except:
            pass

        try:
            all.remove("particleCloud1")
        except:
            pass

        for i in all:
            shad = cmds.listConnections(i, type="shadingEngine")
            if shad != None:
                meshlist = cmds.sets(shad[0], int=shad[0])
                if meshlist != []:
                    materDic[shad[0]] = meshlist

        for key in materDic.keys():
            for i in materDic[key]:
                if ".f[" in i:
                    shape = cmds.listHistory(i, q=1, historyAttr=True)[0].replace(".inMesh", "")
                    shapList.append(shape)
                else:
                    shapList.append(i)
        shapList = list(set(shapList))

        if assetName:
            filterStr = "|%s:" % assetName
            replaceStr = "|"
        else:
            filterStr = "|"
            replaceStr = "|"

        for key in materDic.keys():
            shapeDic = {}
            shap_list = []
            shard_node1 = pm.PyNode(key)
            trans_list1 = shard_node1.inputs()
            for trans in trans_list1:
                tra_nod = pm.PyNode(trans)
                if cmds.nodeType(tra_nod.name()) == "transform":
                    long_name = tra_nod.getShapes()[0].longName()
                    shap_list.append(long_name)
            # for st in shapList:

            # A = []
            for i in materDic[key]:
                if ".f[" in i:

                    pass

                    shape = cmds.listHistory(i, q=1, historyAttr=True)[0].replace(".inMesh", "")

                    root = pm.PyNode(shape)
                    mesh = root.listRelatives(ap=True)
                    newH = mesh[0].longName()
                    if "|" in shape:
                        newSha = newH + "|" + shape.split("|")[-1]
                    else:
                        newSha = newH + "|" + shape
                    newSha = newSha.replace(filterStr, replaceStr)
                    # print newSha
                    # if shape == st:
                    if shape in shapList:
                        if not shapeDic.has_key(newSha):
                            shapeDic[newSha] = []

                        i = "|" + i
                        i = i.replace(filterStr, replaceStr)

                        shapeDic[newSha].append(i)

                else:

                    root = pm.PyNode(i)
                    mesh = root.listRelatives(ap=True)
                    newH = mesh[0].longName()
                    if "|" in i:
                        newSha = newH + "|" + i.split("|")[-1]
                    else:
                        newSha = newH + "|" + i

                    newSha = newSha.replace(filterStr, replaceStr)

                    a = pm.PyNode(newSha)
                    insta_shap_list = a.getOtherInstances()
                    insta_shap_list.append(a)
                    if len(insta_shap_list) != 0:
                        for insta in insta_shap_list:
                            w = insta.longName()
                            if w in shap_list:
                                shapeDic[insta.fullPath()] = []
                            else:
                                pass
                    else:
                        shapeDic[newSha] = []
            # print shapeDic
            materDic[key] = shapeDic
        '''
        for key in materDic.keys():
            shard_node = pm.PyNode(key)
            trans_list = shard_node.inputs()
            for transform_node in trans_list:
                a = pm.PyNode(transform_node)
                if cmds.nodeType(a.name()) == "transform" :
                    long_name = a.getShapes()[0].longName()
                    if materDic[key].has_key(long_name):
                        pass
                    else:
                        materDic[key][long_name] = []
                   # print type(materDic[key]), 88888888
                else:
                    pass
        '''

        # print materDic

        if removeNamespace:
            result = {}

            for mat in materDic.keys():
                result[mat] = {}

                for shape in materDic[mat].keys():
                    newShape = self.removeStringNamespace(shape)
                    result[mat][newShape] = []

                    for i in range(len(materDic[mat][shape])):
                        value = materDic[mat][shape][i]
                        newValue = self.removeStringNamespace(value)
                        result[mat][newShape].append(newValue)

            return result

        else:
            return materDic

    def exportMaterials(self, path, generateMapping=False, mappingFilename='mapping',
                        removeNamespace=False, materials={}):
        '''Exports all materials to a new ma file.'''
        if not materials:
            materials = self.getMaterials(removeNamespace=removeNamespace)

        # Export materials to a file
        if materials:
            # print materials.keys()
            self.select(materials.keys(), replace=True, noExpand=True)
            self.exportSelected(path)

        # Generate a json file with materials and geometry relation
        if generateMapping:
            txt = json.dumps(materials, indent=4)
            root = os.path.dirname(path)
            jsonPath = '%s/%s.json' % (root, mappingFilename)
            f = open(jsonPath, 'w')
            f.write(txt)
            f.close()

        return materials.keys()

    def importMaterials(self, path, configs={}):
        return self.reference(path)

    def assignMaterials_bak(self, mapping, dire={}, geoNamespace='', matNamespace=''):
        dir = dire
        print dir, "%%%%%%%%%%%%%%%%%%%%%%%%"
        '''
        mapping is a dictionary or a file with geometry and materials mapping.
        gin
        Example of mapping:
            {
                "blinn1SG": {
                    "|dog|base|box|boxShape": [
                        "|box.f[0:5]",
                        "|box.f[7:9]"
                    ]
                },
                "blinn2SG": {
                    "|dog|base|pCone1|pConeShape1": []
                }
            }

            {
                "blinn1SG": {
                    "|dog|base|body|bodyShape": [
                        "|body.f[200:359]",
                        "|body.f[380:399]"
                    ]
                }, 
                "blinn2SG": {
                    "|dog|base|body|bodyShape": [
                        "|body.f[0:199]", 
                        "|body.f[360:379]"
                    ]
                }
            }
        '''
        mapping = self.parseConfigs(mapping)

        if not type(mapping) == dict:
            return

        for mat in mapping.keys():
            for shape in mapping[mat].keys():

                # The material is assigned to object faces
                if mapping[mat][shape]:
                    # shape: |dog|base|body|bodyShape
                    faces = []
                    for i in mapping[mat][shape]:
                        # i: |body.f[200:359]
                        f = i.split('.')[-1]
                        # f: f[200:359]
                        newI = '%s.%s' % (shape, f)

                        new = self.addObjectNamespace(newI, geoNamespace)
                        # new: |dog:dog|dog:base|dog:body|dog:bodyShape.f[200:359]
                        new = new.lstrip('|')

                        faces.append(new)

                    faces = ' '.join(faces)

                # The material is assigned to the object
                else:
                    faces = ''

                # Source is the material
                src = self.addObjectNamespace(mat, matNamespace)

                # Destination is the geometry
                # shape = shape.split("|")[-1]
                dst = "%s.instObjGroups[0]" % shape
                dst = self.addObjectNamespace(dst, geoNamespace)
                dst = dst.lstrip('|')

                kwargs = {
                    'source': src,
                    'destination': dst,
                    'connectToExisting': True,
                }
                if faces:
                    kwargs['navigatorDecisionString'] = faces
                try:
                    self._cmds.defaultNavigation(**kwargs)
                    if len(dir) != 0:
                        for i in dir:
                            for num, j in enumerate(dir[i]):
                                if shape.lstrip('|').split("|")[0].split("_")[0] in j:
                                    kwargs['destination'] = shape.lstrip('|').split("|")[0] + str(num + 1) + "|" + (
                                        "|").join(dst.split("|")[1:])
                                    self._cmds.defaultNavigation(**kwargs)
                except:
                    pass

    def assignMaterials(self,
                        mapping,
                        geoNamespace='',
                        matNamespace='',
                        useShortName=False):
        import maya.cmds as cmds
        errorLog = []
        for SG, meshInfo in mapping.iteritems():

            refSG = "%s:%s" % (matNamespace, SG)
            for shape, faces in meshInfo.iteritems():

                if faces:
                    faceList = []
                    for f in faces:
                        f = f[1:]  # remove first "|"
                        asset_subfix_num = [i for i in cmds.ls(assemblies=True) if shape.split("|")[1] in i]
                        # if there is one asset
                        if len(asset_subfix_num) == 1:
                            if useShortName:
                                if geoNamespace:
                                    f = f.replace('|', '|%s:' % geoNamespace)
                                f = f.rsplit('|', 1)[-1]
                            else:
                                sp = shape.rsplit('|', 1)[0]
                                parent = sp.rsplit('|', 1)[0]
                                f = parent + '|' + f
                                if geoNamespace:
                                    f = f.replace('|', '|%s:' % geoNamespace)
                                f = f.rsplit('|', 1)[-1]
                        # if there are more than one asset
                        else:
                            for f_num in asset_subfix_num:
                                # replace the top level to a new top
                                f = f_num + "|" + "|".join(f.split("|")[1:])
                                if useShortName:
                                    if geoNamespace:
                                        f = f.replace('|', '|%s:' % geoNamespace)
                                    f = f.rsplit('|', 1)[-1]
                                else:
                                    sp = shape.rsplit('|', 1)[0]
                                    parent = sp.rsplit('|', 1)[0]
                                    f = parent + '|' + f
                                    if geoNamespace:
                                        f = f.replace('|', '|%s:' % geoNamespace)
                                    f = f.rsplit('|', 1)[-1]

                        faceList.append(f)
                    obj = faceList

                else:
                    obj = shape.rsplit('|', 1)[0]
                    if geoNamespace:
                        obj = obj.replace('|', '|%s:' % geoNamespace)
                    obj = obj[1:]  # remove first "|"
                    asset_subfix_num = [i for i in cmds.ls(assemblies=True) if shape.split("|")[1] in i]
                    if len(asset_subfix_num) == 1:
                        if useShortName:
                            obj = obj.rsplit('|', 1)[-1]
                    else:
                        for f_num in asset_subfix_num:
                            obj = f_num + "|" + "|".join(obj.split("|")[1:])
                            try:
                                cmds.sets(obj, e=True, forceElement=refSG)
                            except:
                                pass

                try:
                    cmds.sets(obj, e=True, forceElement=refSG)
                except:
                    r = '----------------------------------------------' + '\n'
                    r += "refSG:  " + refSG + '\n'
                    r += "  obj:  " + str(obj) + '\n'
                    r += 'refSG ,obj, assign materials failed!!!'
                    errorLog.append(r)
                    # print [obj,refSG]
        print "errorLog:", errorLog
        return errorLog

    def getLongName(self, name, removeNamespace=False):
        pm = self._pm

        # print
        # print 'name:',name

        if "[" in name:
            if "." in name:
                root = pm.PyNode(name.split(".")[0])
            else:
                root = pm.PyNode(name)

            # print
            # print 'root:',root

            ap = root.listRelatives(ap=True)
            root_name = ap[0].longName()

            # print
            # print 'longName:',root_name

            r = root_name + "|" + name

        else:
            r = name

        if removeNamespace:
            return self.removeStringNamespace(r)
        else:
            return r

    def _writeJson(self, patn_json, write_dict):
        '''
        write json
        : param patn_json :  such as : "D:/json/dir.json" type :str
        : param patn_json :  such as :{} type:dict
        '''
        with open(patn_json, "w") as films:
            end = json.dumps(write_dict, indent=4)
            films.write(end)

    def _readJson(self, patn_json):
        '''read json
        : param patn_json :  such as : "D:/json/dir.json" type :str
        '''
        with open(patn_json) as file:
            return json.loads(file.read())

    def getSgParms_bak1(self, shaders, config, temp_dict):
        '''
        获取与sg相关联的材质的属性值
        :param shaders: 材质节点的名字
        :param config: 配置json文件路径
        :param temp_dict:
        :return: 字典
        '''
        config_dict = config
        cmds = self._cmds

        # 获取与sg节点相关联的材质节点
        shader_name_config = config_dict.keys()[1]

        for attr_name in config_dict[shader_name_config]["parms"].keys():
            if self.exists(shaders[0] + attr_name):
                attr = cmds.getAttr(shaders[0] + attr_name)
                if temp_dict.has_key("parms"):
                    temp_dict["parms"][attr_name] = attr
                else:
                    temp_dict["parms"] = {}
                    temp_dict["parms"][attr_name] = attr

        for tex_attr_name in config_dict[shader_name_config]["Texture"].keys():
            shading = shaders[0] + tex_attr_name
            if self.exists(shading):
                Texture = cmds.listConnections(shading, type='file')
                if Texture != None:
                    TextureFile = cmds.getAttr("%s.fileTextureName" % Texture[0])
                    if temp_dict.has_key("Texture"):
                        temp_dict["Texture"][tex_attr_name] = TextureFile
                    else:
                        temp_dict["Texture"] = {}
                        temp_dict["Texture"][tex_attr_name] = TextureFile

        return temp_dict

    def exportMaterials2_bak1(self, path, removeNamespace=False, configs={}):
        '''Exports all materials and objects materials mapping to a json file.'''
        out_json = path
        config = configs
        cmds = self._cmds

        if os.path.isfile(out_json):
            os.remove(out_json)

        # print
        # print 'config:'
        # print config

        config_dict = self.parseConfigs(configs)

        temp_sg = []
        temp_dict = {}

        shapesInSel = cmds.ls(dag=1, o=1, type="mesh")

        # print
        # print 'shapesInSel:'
        # print shapesInSel

        for i in range(len(shapesInSel)):
            shadingGrps_list = cmds.listConnections(shapesInSel[i], type='shadingEngine')
            # 去除重复的sg节点
            if shadingGrps_list != None:
                if len(shadingGrps_list) > 1:
                    for sg in shadingGrps_list:
                        if sg in shadingGrps_list:
                            shadingGrps_list.remove(sg)

            # print
            # print 'shadingGrps_list:'
            # print shadingGrps_list

            # 遍历sg节点，获取与其相关联材质的信息
            if shadingGrps_list is not None:
                for sg_name in shadingGrps_list:
                    # temp_sg存放已经遍历过了的sg节点防止二次遍历
                    if sg_name not in temp_sg:
                        temp_sg.append(sg_name)
                        shader_name_config = config_dict.keys()[1]
                        shaders_node = cmds.ls(cmds.listConnections(sg_name), materials=1)

                        # print
                        # print 'sg_name:',sg_name
                        # print 'shaders_node:',shaders_node

                        if type(shaders_node) == list:
                            shaders_node = shaders_node[0]

                        # 判断节点是否是aiStandard node
                        node_type = cmds.nodeType(shaders_node)

                        # print 'node_type:',node_type
                        # print 'shader_name_config:',shader_name_config

                        if shader_name_config == node_type:
                            temp_dict = self.getSgParms(shaders_node, config_dict, temp_dict)
                            try:
                                dict_all = self._readJson(out_json)
                            except:
                                dict_all = {}

                            if dict_all.has_key("Maya"):
                                dict_all["Maya"][shader_name_config].append(temp_dict)
                            else:
                                dict_all["Maya"] = {}
                                dict_all["Maya"][shader_name_config] = []
                                dict_all["Maya"][shader_name_config].append(temp_dict)

                            # 获取相同材质的所有物体以及面
                            obj_list = cmds.sets(sg_name, int=sg_name)
                            obj_list_name = []
                            obj_list_long_name = []

                            # 获取这些物体的父节点，transform节点，面的除外（pcube.f[1:3]）
                            # print
                            # print 'obj_list:'
                            # print obj_list

                            for obj in obj_list:
                                if "." not in obj:
                                    obj_list_name.append(cmds.listRelatives(obj, p=1, f=1)[0])
                                else:
                                    obj_list_name.append(obj)

                            # print
                            # print 'obj_list_name:'
                            # print obj_list_name

                            for shot_name in obj_list_name:
                                if "." in shot_name:
                                    if ":" in shot_name and "[" not in shot_name:

                                        name_temp_list_shot = shot_name.split(".")
                                        name_shot = name_temp_list_shot[0].split(":")[1] + "." + name_temp_list_shot[1]
                                        obj_list_long_name.append(
                                            self.getLongName(name_shot, removeNamespace=removeNamespace))
                                    else:

                                        obj_list_long_name.append(
                                            self.getLongName(shot_name, removeNamespace=removeNamespace))
                                else:
                                    obj_list_long_name.append(
                                        self.getLongName(shot_name, removeNamespace=removeNamespace))

                            temp_dict["object_name"] = obj_list_long_name
                            temp_dict["shader_name"] = shaders_node[0]
                            self._writeJson(out_json, dict_all)

    def getSgParms(self, shaders, config, temp_dict):
        """
        获取与sg相关联的材质的属性值
        :param sg:
        :param temp_dict:
        :return: 字典
        """
        cmds = self._cmds

        # 获取与sg节点相关联的材质节点
        config_dict = config

        # print config_dict
        shader_name_config = config_dict.keys()[1]
        # print shader_name_config
        for attr_name in config_dict[shader_name_config]["parms"].keys():
            # print attr_name
            # print
            # print 'shading:',shaders[0] + attr_name

            if cmds.objExists(shaders[0] + attr_name):
                attr = cmds.getAttr(shaders[0] + attr_name)

                if temp_dict.has_key("parms"):
                    temp_dict["parms"][attr_name] = attr
                else:
                    temp_dict["parms"] = {}
                    temp_dict["parms"][attr_name] = attr

        # print "\n"
        temp_dict["Texture"] = {}
        for tex_attr_name in config_dict[shader_name_config]["Texture"].keys():
            # print tex_attr_name
            shading = shaders[0] + tex_attr_name

            # print
            # print 'shading:',shading

            if cmds.objExists(shading):
                if ".displacementShader" not in shading:  # 判断shading是否包含.displacementShader 不包含执行以下
                    Texture = cmds.listConnections(shading, type='file')
                    if Texture != None:
                        TextureFile = cmds.getAttr("%s.fileTextureName" % Texture[0])
                        if temp_dict.has_key("Texture"):
                            temp_dict["Texture"][tex_attr_name] = TextureFile
                        else:

                            temp_dict["Texture"][tex_attr_name] = TextureFile
                else:  # 判断shading是否包含.displacementShader 包含执行以下
                    shader = shaders[0] + "SG"
                    Texture = cmds.listConnections(shader)
                    # print Texture
                    for i in Texture:
                        if 'displacementShader' in i:
                            Text = cmds.listConnections(i, type='file')  # 判断与'displacementShader'连接的file
                            # print Text
                            TextureFile = cmds.getAttr("%s.fileTextureName" % Text[0])
                            temp_dict["Texture"][".displacementShader"] = TextureFile

        # print temp_dict["Texture"]
        return temp_dict

    def parseConfigs(self, configs):
        if type(configs) in (str, unicode) and os.path.isfile(configs):
            f = open(configs, 'r')
            t = f.read()
            f.close()
            configs = json.loads(t)

        return configs

    def exportMaterials2(self, path, removeNamespace=False, configs={},
                         objects=[]):
        '''Exports all materials and objects materials mapping to a json file.'''
        """
        输出场景里AiStandard的材质信息
        :return:
        """
        out_json = path
        config = configs
        cmds = self._cmds

        if os.path.isfile(out_json):
            os.remove(out_json)

        # print 111111
        config_dict = self.parseConfigs(configs)

        temp_sg = []
        temp_dict = {}

        if objects:
            shapesInSel = objects[:]
        else:
            shapesInSel = cmds.ls(dag=1, o=1, type="mesh")

        # print
        # print 'shapesInSel:'
        # print shapesInSel

        for i in range(len(shapesInSel)):
            shadingGrps_list = cmds.listConnections(shapesInSel[i], type='shadingEngine')

            # print
            # print 'shadingGrps_list:'
            # print shadingGrps_list

            # 去除重复的sg节点
            if shadingGrps_list != None:

                if len(shadingGrps_list) > 1:
                    for sg in shadingGrps_list:
                        if sg in shadingGrps_list:
                            shadingGrps_list.remove(sg)

            # print
            # print 'shadingGrps_list2:'
            # print shadingGrps_list

            # print shadingGrps_list
            # 遍历sg节点，获取与其相关联材质的信息
            if shadingGrps_list is not None:
                for sg_name in shadingGrps_list:
                    # temp_sg存放已经遍历过了的sg节点防止二次遍历

                    # print
                    # print 'sg_name:',sg_name
                    # print 'temp_sg:'
                    # print temp_sg

                    if sg_name not in temp_sg:
                        temp_sg.append(sg_name)
                        shader_name_config = config_dict.keys()[1]
                        shaders_node = cmds.ls(cmds.listConnections(sg_name), materials=1)

                        # print
                        # print 'shader_name_config:',shader_name_config
                        # print 'shaders_node:',shaders_node

                        # 判断节点是否是aiStandard node
                        node_type = cmds.nodeType(shaders_node)

                        # print
                        # print 'shader_name_config:',shader_name_config
                        # print 'node_type:',node_type

                        if shader_name_config == node_type or node_type == None:

                            # print
                            # print 'shader_name_config:',shader_name_config
                            # print 'node_type:',node_type

                            temp_dict = self.getSgParms(shaders_node, config_dict, temp_dict)
                            try:
                                dict_all = self._readJson(out_json)
                            except:
                                dict_all = {}

                            if dict_all.has_key("Maya"):
                                dict_all["Maya"][shader_name_config].append(temp_dict)
                            else:
                                dict_all["Maya"] = {}
                                dict_all["Maya"][shader_name_config] = []
                                dict_all["Maya"][shader_name_config].append(temp_dict)

                            # 获取相同材质的所有物体以及面
                            obj_list = cmds.sets(sg_name, int=sg_name)
                            obj_list_name = []
                            obj_list_long_name = []

                            # 获取这些物体的父节点，transform节点，面的除外（pcube.f[1:3]）
                            for obj in obj_list:
                                if "." not in obj:
                                    obj_list_name.append(cmds.listRelatives(obj, p=1)[0])
                                else:
                                    obj_list_name.append(obj)

                            for shot_name in obj_list_name:
                                if "." in shot_name:
                                    if ":" in shot_name and "[" not in shot_name:
                                        name_temp_list_shot = shot_name.split(".")
                                        name_shot = name_temp_list_shot[0].split(":")[1] + "." + name_temp_list_shot[1]
                                        obj_list_long_name.sppend(self.getLongName(name_shot))

                                    else:
                                        obj_list_long_name.append(self.getLongName(shot_name))

                                else:
                                    obj_list_long_name.append(self.getLongName(shot_name))

                            temp_dict["object_name"] = obj_list_long_name
                            temp_dict["shader_name"] = shaders_node[0]
                            # print dict_all
                            self._writeJson(out_json, dict_all)

    def getFileNodes_bak1(self, materials):
        '''
        Gets file texture nodes for the materials.
        materials is a list of material names.
        '''
        fileNodes = []
        for mat in materials:
            nodes = self._cmds.listConnections(mat)
            for node in nodes:
                temp = self._cmds.listConnections(node, type="file")
                if temp:
                    if temp[0] not in fileNodes:
                        fileNodes.append(temp[0])

        return fileNodes

    def getFileNodes(self, materials=[]):
        '''
        Gets file texture nodes for the materials.
        materials is a list of material names.
        '''
        if materials:
            fileNodes = []
            for mat in materials:
                node_list = self._cmds.listConnections(mat)
                shade_name = self._cmds.ls(node_list, materials=True)[0]
                dg_list = self._cmds.listHistory(shade_name)
                filenode = self._cmds.ls(dg_list, textures=True)
                fileNodes += filenode

        else:
            fileNodes = self._cmds.ls(type='file')

        return fileNodes

    def getTexturePaths(self, fileNodes=[]):
        '''Gets texture paths for the file nodes.'''
        texDic = {}
        texError = []

        if not fileNodes:
            fileNodes = self._cmds.ls(type='file')

        for fn in fileNodes:
            texPath = self._cmds.getAttr("%s.fileTextureName" % fn)
            if os.path.exists(texPath):
                texDic[fn] = texPath
            else:
                texError.append(u'%s节点的贴图路径不存在%s' % (fn, texPath))

        return texDic

    def replaceTexturePaths(self, maPath, pathInfo):
        # print exportPath,"########################"
        f = open(maPath, "r")
        txt = f.read()
        f.close()

        for key in pathInfo.keys():
            txt = txt.replace(key, pathInfo[key])

        f = open(maPath, "w")
        f.write(txt)
        f.close()

    # ---------------------------------- Render -------------------------------
    @classmethod
    def getMayaWindow(cls):
        ptr = apiUI.MQtUtil.mainWindow()
        if ptr is not None:
            win = shiboken.wrapInstance(long(ptr), QtGui.QWidget)
            win.setWindowState(QtCore.Qt.WindowMaximized)
        return shiboken.wrapInstance(long(ptr), QtGui.QMainWindow)

    def getModelPanel4Camera(self):
        return self._cmds.modelPanel('modelPanel4', q=True, cam=True)

    def getActiveCamera(self):
        panel_views = self._cmds.getPanel(visiblePanels=True)
        if panel_views:
            try:
                return self._cmds.modelPanel(panel_views[0], q=True, cam=True)
            except:
                return self._cmds.modelPanel(panel_views[1], q=True, cam=True)

    def setActiveCameraAttributes(self, filmPivot=False, filmOrigin=False,
                                  safeAction=False, resolution=False, gateMask=False):
        '''Sets display attributes of the active camera.'''
        kwargs = vars().copy()
        del kwargs['self']

        camera = self.getActiveCamera()
        if camera:
            for arg in kwargs.keys():
                attr = '%s.display%s%s' % (camera, arg[0].upper(), arg[1:])
                self._cmds.setAttr(attr, kwargs[arg])

    def removeAllHUDs(self):
        allHUD = self._cmds.headsUpDisplay(listHeadsUpDisplays=True, q=True)
        if allHUD:
            for hud in allHUD:
                self._cmds.headsUpDisplay(hud, remove=True)
        self._cmds.headsUpDisplay('HUDIKSolverState', section=0, block=5)

    def setHUD(self, name='', section=1, block=1, blockSize='small', labelWidth=70,
               label='', labelFontSize='large'):
        '''Sets the heads up display.'''
        # print 'HUD:',vars()

        kwargs = vars().copy()
        del kwargs['self']

        name = kwargs['name']
        del kwargs['name']

        if name:
            self._cmds.headsUpDisplay(name, **kwargs)
        else:
            self._cmds.headsUpDisplay(**kwargs)

    def setHUDs(self, data):
        '''
        Sets a list of HUD items.
        data is a list of dictionaries like this:
        [
            {'name': 'combo', 'section': 1, 'block': 1, 'blockSize': 'small',
            'labelWidth': 70, 'label': 'TST', 'labelFontSize': 'large'},
            {},
        ]
        '''
        for d in data:
            # print 'HUD:', d
            self.setHUD(**d)

    def playblast(self, path, scale=50, quality=100, resolution=None, override=False,
                  firstFrame=None, lastFrame=None, ao=True, antiAliasing=True,
                  camera=None, useCameraKeyframeRange=False, movieCodec=''):
        '''
        Makes playblast for the current scene.
        Arguments:
            path: a image sequence or a avi file
                image sequence:
                    /abc/abc.####.jpg
                avi:
                    /abc/abc.avi
                qt mov:
                    /abc/abc.mov
            scale: percent of the output image
            quality: quality of the output image
            resolution: a list of width and height, default is from render setting dialog
            movieCodec: movie codec for ani and mov file
        '''
        # print vars()
        start_f = self._cmds.playbackOptions(q=1, ast=1)
        self._cmds.currentTime(start_f)
        f = fllb.parseSequence(path)
        '''
        f:
            {'basename': 'abc',
             'directory': 'C:/jinxi',
             'extension': 'jpg',
             'padding': '%06d',
             'padding_length': 6
             }
        '''

        if not resolution:
            resolution = self.resolution()

        kwargs = {
            'sequenceTime': 0,
            'clearCache': 1,
            'viewer': 0,
            'showOrnaments': 1,
            'forceOverwrite': override,
            'percent': scale,
            'quality': quality,
            'widthHeight': resolution,
            'framePadding': f['padding_length']
        }

        ext = f['extension']

        soundList = self._cmds.ls(type="audio")
        if len(soundList) != 0:
            kwargs['sound'] = soundList[0]
        else:
            pass

        # playblast  -format avi -filename "movies/dog_CH_Model_High_v006.avi"
        # -sequenceTime 0 -clearCache 0 -viewer 1 -showOrnaments 1
        # -fp 4 -percent 50 -compression "none" -quality 70 -widthHeight 1920 1080;
        if ext == 'avi':
            kwargs['format'] = ext
            kwargs['filename'] = path
            if movieCodec:
                kwargs['compression'] = movieCodec

        # playblast  -format qt -filename "movies/dog_CH_Model_High_v006.mov"
        # -sequenceTime 0 -clearCache 0 -viewer 1 -showOrnaments 1
        # -fp 4 -percent 50 -compression "Photo - JPEG" -quality 70 -widthHeight 1920 1080;
        elif ext == 'mov':
            kwargs['format'] = 'qt'
            kwargs['filename'] = path
            if movieCodec:
                kwargs['compression'] = movieCodec

        else:
            kwargs['format'] = 'image'
            kwargs['compression'] = ext
            kwargs['filename'] = '{directory}/{basename}'.format(**f)

        if firstFrame != None:
            kwargs['startTime'] = firstFrame
        if lastFrame != None:
            kwargs['endTime'] = lastFrame

        # if ao:
        # self._cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", True)

        # if antiAliasing:
        # self._cmds.setAttr("hardwareRenderingGlobals.multiSampleEnable", True)

        self._mel.eval('ogs -reset')

        if camera:
            # self._cmds.lookThru(camera)
            if useCameraKeyframeRange:
                first, last = self.getObjectKeyframeRange(camera)
                kwargs['startTime'] = first
                kwargs['endTime'] = last
        print kwargs
        self._cmds.playblast(**kwargs)

        return True

    def setView(self, camera):
        self._cmds.lookThru(camera)

    def getCurrentView(self):
        camera_views = None
        panel_views = self._cmds.getPanel(visiblePanels=True)
        for view in panel_views:
            try:
                camera_views = self._cmds.modelPanel(view, q=True, cam=True)
            except:
                pass
            # RuntimeError: modelPanel: Object 'scriptEditorPanel1' not found.
        return camera_views

    def makeSuitableCamera(self, pos=1, objects=[]):
        '''Makes a camera based the bounding box of the geometry.'''
        size, maxLength = self.getBoundingBox(objects=objects)

        x = (size[0] + size[3]) / 2
        y = (size[1] + size[4]) / 2
        z = (size[2] + size[5]) / 2

        cameraname = self._cmds.camera()

        self._cmds.setAttr("%s.farClipPlane" % cameraname[0], 10000000)

        if pos == 1:
            self._cmds.move(x, y + max(maxLength) * 0.7, z + max(maxLength) * 1.2, cameraname[0])
            # self._cmds.rotate( '-30deg',0 , 0,cameraname[0])#'-45deg'

            self._cmds.rotate('-30deg', 0, 0, cameraname[0])  # '-45deg'
            self._cmds.move(x, y, z, "%s.scalePivot" % cameraname[0], "%s.rotatePivot" % cameraname[0])
            self._cmds.setAttr("%s.rotateY" % cameraname[0], 45)

        elif pos == 2:
            self._cmds.move(x, y + max(maxLength) * 0.1, z + max(maxLength) * 2.4, cameraname[0])
            # self._cmds.rotate( '-30deg',0 , 0,cameraname[0])#'-45deg'

            # self._cmds.rotate( '-10deg',0 , 0,cameraname[0])#'-45deg'
            self._cmds.move(x, y, z, "%s.scalePivot" % cameraname[0], "%s.rotatePivot" % cameraname[0])
            # self._cmds.setAttr("%s.rotateY"%cameraname[0] ,45)
            self._cmds.setAttr("%s.rotateX" % cameraname[0], -5)

        return cameraname[0]

    def setKeyframe(self, geo, channel, frame, value):
        self._cmds.setKeyframe(geo, attribute=channel, time=frame, value=value)

    def deleteKeyframe(self, geo, channel, frame):
        self._cmds.cutKey(geo, time=(frame,), attribute=channel, clear=True)

    def moveObjectsKeyframes(self, objs, frame):
        '''Moves all of the keyframes of the objects to the frame.'''
        cameraNameList = objs
        frameNum = frame

        allNurName = []
        for cameraShape in cameraNameList:
            root = self._pm.PyNode(cameraShape)
            A = root.listRelatives(ap=True)
            cameraName = A[0].longName()
            allNurName.append(cameraName)
        allNurName = list(set(allNurName))

        minFirstList = []
        maxLastList = []
        cameraNameDic = {}
        for cameraName in allNurName:
            firstF = self._cmds.findKeyframe(cameraName, which="first")
            lastF = self._cmds.findKeyframe(cameraName, which="last")
            if firstF != lastF:
                minFirstList.append(firstF)
                maxLastList.append(lastF)
                cameraNameDic[cameraName] = [firstF, lastF]
        minFirst = min(minFirstList)
        maxLast = max(maxLastList)
        moveNum = frameNum - minFirst

        for cameraName in cameraNameDic:
            first = cameraNameDic[cameraName][0]
            last = cameraNameDic[cameraName][1]
            rangeTime = (first, last + 1)

            self._cmds.keyframe(cameraName, e=True, includeUpperBound=False,
                                animation="objects", time=rangeTime, relative=True,
                                option='over', timeChange=moveNum)

        result = {
            'original_frame_range': [minFirst, maxLast],
            'offset_frames': moveNum,
        }
        return result

    def _makeTurntableAnimation(self, geo, firstFrame=1, lastFrame=60,
                                func=None, redo=True, reopen=False, args=(), kwargs={}):
        '''Makes playblast preview render for the geo.'''
        sceneName = self.filepath()

        channel = 'rotateY'

        # Make animation for the geo
        self.setKeyframe(geo, channel, firstFrame, 0)
        self.setKeyframe(geo, channel, lastFrame, 360)

        # Make a camera
        camera = self.makeSuitableCamera(pos=2)

        # Render
        camera_views = self.getCurrentView()

        kwargs['camera'] = camera
        if func:
            func(*args, **kwargs)

        if redo:
            self._cmds.delete(camera)

            if camera_views:
                self._cmds.lookThru(camera_views)

            self.deleteKeyframe(geo, channel, firstFrame)
            self.deleteKeyframe(geo, channel, lastFrame)

        if reopen:
            self.open(sceneName, force=True)

    def makeTurntablePlayblast(self, path, geo, firstFrame=1, lastFrame=60,
                               resolution=None, scale=100, quality=100, override=False):
        '''Makes playblast preview render for the geo.'''
        kwargs = vars().copy()
        del kwargs['self']
        del kwargs['geo']
        self._makeTurntableAnimation(geo, firstFrame=firstFrame, lastFrame=lastFrame,
                                     func=self.playblast, kwargs=kwargs)

    def saveTempFile(self):
        timeStr = time.strftime("%H%M%S", time.localtime())
        filePath = self.filepath()
        folder = os.path.dirname(filePath)
        if not os.path.exists(folder):
            os.makedirs(folder)
        fileList = self.filename().split('.')
        tempFileName = "%s/%s_%s.%s" % (folder, fileList[0], timeStr, fileList[-1])
        tempFileName = tempFileName.replace("\\", "/")

        self.saveAs(tempFileName)

        return tempFileName

    def arnoldRender_bak1(self, path, firstFrame=1, lastFrame=60, resolution=[1920, 1080],
                          camera=None, hdrPath='', overrideMaterials=False, templatePath=''):
        '''
        Uses arnold to render the current scene.
        Arguments:
            path: a image sequence
                /abc/abc.####.exr
            resolution: a list of width and height
        '''
        sceneName = self.filepath()

        f = fllb.parseSequence(path)
        '''
        f:
            {'basename': 'abc',
             'directory': 'C:/jinxi',
             'extension': 'jpg',
             'padding': '%06d',
             'padding_length': 6
             }
        '''

        if os.path.isfile(templatePath):

            try:
                self._cmds.file(templatePath, i=True, ignoreVersion=True)
            except:
                pass

            '''
            try:
                info = self.import_(templatePath)
            except:
                pass
            '''

            if hdrPath:
                self._cmds.setAttr('temp.fileTextureName', hdrPath, type='string')

        # remove all camera and add current camera
        allCamera = self._cmds.ls(type='camera')

        for cm in allCamera:
            camName = self._cmds.listRelatives(cm, ap=True)[0]
            self._cmds.setAttr("%s.renderable" % cm, 0)

        # Set camera parameter
        if camera:
            camShape = self._cmds.listRelatives(camera)[0]
            self._cmds.setAttr("%s.renderable" % camShape, 1)

        # Set render settings
        self._cmds.setAttr("defaultRenderGlobals.currentRenderer", 'arnold', type="string")

        ext = f['extension']
        self._cmds.setAttr("defaultArnoldDriver.aiTranslator", ext, type="string")

        self._cmds.setAttr("defaultResolution.width", resolution[0])
        self._cmds.setAttr("defaultResolution.height", resolution[1])
        self._cmds.setAttr("defaultResolution.pixelAspect", 1)

        imageName = f['basename']
        self._cmds.setAttr("defaultRenderGlobals.imageFilePrefix", imageName, type='string')

        renderSettings = {}

        renderSettings['startFrame'] = firstFrame
        renderSettings['endFrame'] = lastFrame
        renderSettings['animation'] = 1
        renderSettings['putFrameBeforeExt'] = 1
        renderSettings['byFrameStep'] = 1

        # Find output format
        renderSettings['extensionPadding'] = f['padding_length']

        for s in renderSettings.keys():
            name = 'defaultRenderGlobals.%s' % s
            # print 'name:',name
            # print 'value:',renderSettings[s]
            self._cmds.setAttr(name, renderSettings[s])

        ## Render out
        # tempFileName = self.saveTempFile()
        #
        # binPath = os.path.dirname(sys.executable)
        # mayaRender = "%s/Render.exe" % binPath
        # mayaRender = mayaRender.replace("\\", "/")
        # mayaRender = '"%s"' % mayaRender
        #
        # newOutputPath = "%s/%s" % (f['directory'], f['basename'])
        # keys = (mayaRender, camera, newOutputPath, tempFileName)
        # cmd = '%s -cam %s -rd %s %s' % keys
        # p = subprocess.Popen(cmd, shell=True)
        # print cmd
        # p.wait()
        #
        # self.open(sceneName)

        # return

        kwargs = {
            # 'render': True,
            # 'replace': True,
            'width': int(resolution[0]),
            'height': int(resolution[1]),
            'batch': True
        }
        if camera:
            kwargs['camera'] = camera

        # print 'kwargs:',kwargs
        self._cmds.arnoldRender(**kwargs)

        return True

    _defaultSetUpArgs = {
        "imageName": '<Scene>',
        'imageFormat': 'exr',
        'animation': 1,
        'putFrameBeforeExt': 1,
        'extensionPadding': 4,
        'pixelAspect': 1,
        # 'deviceAspectRatio':1,
        'byFrameStep': 1,
        'arnoldSetUp': {},
        'rsSetUp': {}
    }

    _arnoldSetUp = {
        'AASamples': {'value': 6, "type": None},
        'GIDiffuseSamples': {'value': 2, "type": None},
        'GISpecularSamples': {'value': 2, "type": None},
        'GITransmissionSamples': {'value': 2, "type": None},
        'GISssSamples': {'value': 2, "type": None},
        'GIVolumeSamples': {'value': 12, "type": None},
        'lock_sampling_noise': {'value': 0, "type": None},
        'sssUseAutobump': {'value': 0, "type": None},
        'GITotalDepth': {'value': 14, "type": None},
        'GIDiffuseDepth': {'value': 2, "type": None},
        'GISpecularDepth': {'value': 3, "type": None},
        'GITransmissionDepth': {'value': 5, "type": None},
        'GIVolumeDepth': {'value': 0, "type": None},
        'autoTransparencyDepth': {'value': 10, "type": None},
    }

    _defaultArnoldRenderLayer = ["beauty", "diffuse",
                                 "diffuse_albedo",
                                 "diffuse_direct",
                                 "diffuse_indirect",
                                 "direct",
                                 "emission",
                                 "indirect",
                                 "N",
                                 "specular",
                                 "specular_albedo",
                                 "specular_direct",
                                 "specular_indirect",
                                 "sss",
                                 "sss_albedo",
                                 "sss_direct",
                                 "sss_indirect",
                                 "transmission",
                                 "transmission_albedo",
                                 "transmission_direct",
                                 "transmission_indirect"]

    def assignArnoldMaterial(self):
        cmds = self._cmds

        allMesh = cmds.ls(sl=True, type='mesh', dag=True)
        import mtoa.core as core
        defaultMaterialNodeName = core.createArnoldNode("aiStandardSurface")
        SGNode = cmds.listConnections("%s" % defaultMaterialNodeName, type="shadingEngine")

        if SGNode:
            cmds.setAttr('%s.base' % defaultMaterialNodeName, 1)
            cmds.setAttr('%s.baseColor' % defaultMaterialNodeName, 0.51049, 0.51049, 0.51049, type='double3')
            cmds.setAttr('%s.specular' % defaultMaterialNodeName, 0.1)
            cmds.setAttr('%s.specularRoughness' % defaultMaterialNodeName, 0.7)
            cmds.setAttr('%s.specularIOR' % defaultMaterialNodeName, 1.1)
            for ms in allMesh:
                cmds.defaultNavigation(source=SGNode[0], destination="%s.instObjGroups[0]" % ms, connectToExisting=True)

    def getBoundingBox(self, objects=[]):
        cmds = self._cmds

        x = []
        y = []
        z = []
        _x = []
        _y = []
        _z = []

        allObject = []
        if objects:
            allObject[:] = objects[:]
        else:
            allT = self._cmds.ls(type="mesh")
            for i in allT:
                root = self._pm.PyNode(i)
                A = root.listRelatives(ap=True)
                objectName = A[0].longName()
                allObject.append(objectName)

        for i in allObject:
            si = cmds.xform(i, q=1, bb=1)
            # print i,si
            x.append(si[0])
            y.append(si[1])
            z.append(si[2])
            _x.append(si[3])
            _y.append(si[4])
            _z.append(si[5])

        size = [min(x), min(y), min(z), max(_x), max(_y), max(_z)]
        # size = [-x,-y,-z,x,x,y,z]
        # x = (size[0]+size[3])/2
        # y = (size[1]+size[4])/2
        # z = (size[2]+size[5])/2
        maxLength = [abs(size[0]) + abs(size[3]),
                     abs(size[1]) + abs(size[4]),
                     abs(size[2]) + abs(size[5])]

        return size, maxLength

    def scaleLightRig(self, light):
        cmds = self._cmds

        # change light position
        selSize, maxLength = self.getBoundingBox()
        selHight = selSize[4]
        cmds.setAttr(light + '.translateY', selHight)
        selMax = max([abs(selSize[0]) + abs(selSize[3]),
                      abs(selSize[2]) + abs(selSize[5])])

        size, maxLength = self.getBoundingBox(objects=[light])
        lightMin = min([abs(size[0]) + abs(size[3]),
                        abs(size[2]) + abs(size[5])])

        normalSize = lightMin / 7
        if selMax > normalSize:
            times = selMax / normalSize
            cmds.setAttr(light + '.scaleX', times)
            cmds.setAttr(light + '.scaleY', times)
            cmds.setAttr(light + '.scaleZ', times)

    def arnoldRender(self, path, firstFrame=1, lastFrame=60, resolution=[1920, 1080],
                     camera=None, hdrPath='', overrideMaterials=False, templatePath='',
                     enableAOVs=False, frameStep=1, renderSettings={},
                     aovs={}, aovOutputPath='', silence=False):
        '''
        Uses arnold to render the current scene.
        Arguments:
            path: a image sequence
                /abc/abc.####.exr
            resolution: a list of width and height
        '''
        f = fllb.parseSequence(path)
        '''
        f:
            {'basename': 'abc',
             'directory': 'C:/jinxi',
             'extension': 'jpg',
             'padding': '%06d',
             'padding_length': 6
             }
        '''

        arnoldModulePath = templatePath
        outputPath = os.path.dirname(path)
        defaultMaterials = overrideMaterials
        startFrame, endFrame = firstFrame, lastFrame
        cmds = self._cmds

        args = self._defaultSetUpArgs.copy()
        args.update(renderSettings)
        setUpArgs = args
        # defaultImageFormat = ['png',"tif",'jpeg','mtoa_shaders','deepexr','exr','maya']

        setUpArgs['rendererType'] = 'arnold'
        setUpArgs['imageFormat'] = f['extension']
        setUpArgs["imageName"] = f['basename']
        setUpArgs['extensionPadding'] = f['padding_length']
        setUpArgs['byFrameStep'] = frameStep

        sceneName = cmds.file(query=True, location=True)
        sel = cmds.ls(sl=True)

        # import module File
        if arnoldModulePath:
            cmds.file(arnoldModulePath, i=True, ignoreVersion=True)

            # change light position
            self.scaleLightRig('arnldLight')

            # import hdr texture
            if hdrPath:
                cmds.setAttr('temp.fileTextureName', hdrPath, type='string')

        # assign object default materials
        if defaultMaterials:
            assign = self.assignArnoldMaterial()

        cmds.setAttr("defaultResolution.pixelAspect", setUpArgs['pixelAspect'])
        # cmds.setAttr("defaultResolution.deviceAspectRatio",setUpArgs['deviceAspectRatio'])
        cmds.setAttr('defaultRenderGlobals.animation', setUpArgs['animation'])
        cmds.setAttr('defaultRenderGlobals.putFrameBeforeExt', setUpArgs['putFrameBeforeExt'])
        cmds.setAttr('defaultRenderGlobals.extensionPadding', setUpArgs['extensionPadding'])
        # -- set frameRange --
        cmds.setAttr('defaultRenderGlobals.startFrame', int(startFrame))
        cmds.setAttr('defaultRenderGlobals.endFrame', int(endFrame))
        cmds.setAttr('defaultRenderGlobals.byFrameStep', setUpArgs['byFrameStep'])

        # get and set renderer type
        rendererType = setUpArgs['rendererType']
        cmds.setAttr("defaultRenderGlobals.currentRenderer", rendererType, type="string")
        # set render imageType
        cmds.setAttr("defaultArnoldDriver.aiTranslator", setUpArgs['imageFormat'], type="string")
        if setUpArgs['arnoldSetUp']:
            setDic = setUpArgs['arnoldSetUp']
            for key in setDic:
                if setDic[key]['type'] == None:
                    cmds.setAttr("defaultArnoldRenderOptions.%s" % key, setDic[key]['value'])
                elif setDic[key]['type'] == 'string':
                    cmds.setAttr("defaultArnoldRenderOptions.%s" % key, setDic[key]['value'], type='string')

        if enableAOVs:
            aovMode = 1
        else:
            aovMode = 0
        cmds.setAttr('defaultArnoldRenderOptions.aovMode', aovMode)

        byFrame = setUpArgs['byFrameStep']
        frameList = range(int(startFrame), int(endFrame), int(byFrame))
        imageN = os.path.basename(sceneName).split('.')[0]

        cam = camera
        allCamera = cmds.ls(type='camera')

        # remove all camera and add current camera
        for cm in allCamera:
            camName = cmds.listRelatives(cm, ap=True)[0]
            cmds.setAttr("%s.renderable" % cm, 0)
        camShape = cmds.listRelatives(cam)[0]
        cmds.setAttr("%s.renderable" % camShape, 1)
        # ---------------------------------------------

        # rs render
        imageName = '%s/%s' % (outputPath, setUpArgs['imageName'])
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", imageName, type='string')

        if not silence:
            cmds.arnoldRender(camera=cam, width=int(resolution[0]), height=int(resolution[1]),
                              batch=True)
            # -animation -batch -resolution [x,y]

        return []

    def assignRSMaterial(self):
        pass

    def redshiftRender(self, path, firstFrame=1, lastFrame=60, resolution=[1920, 1080],
                       camera=None, hdrPath='', overrideMaterials=False, templatePath='',
                       enableAOVs=False, frameStep=1, renderSettings={},
                       aovs={}, aovOutputPath='', silence=False):
        '''
        Uses redshift to render the current scene.
        Arguments:
            path: a image sequence
                /abc/abc.####.exr
            resolution: a list of width and height
            aovs:
            {
                'Ambient Occlusion': {
                    'name': 'AO', 'filePrefix': '',
                    'enabled': True
                },
                'Depth': {'name': 'Z', 'filePrefix': ''}
            }
        '''
        self._cmds.loadPlugin("redshift4maya")

        path = path.replace('\\', '/')
        f = fllb.parseSequence(path)
        '''
        f:
            {'basename': 'abc',
             'directory': 'C:/jinxi',
             'extension': 'jpg',
             'padding': '%06d',
             'padding_length': 6
             }
        '''

        rsModulePath = templatePath
        outputPath = os.path.dirname(path)
        defaultMaterials = overrideMaterials
        startFrame, endFrame = firstFrame, lastFrame
        cmds = self._cmds

        args = self._defaultSetUpArgs.copy()
        args.update(renderSettings)
        setUpArgs = args

        setUpArgs['rendererType'] = 'redshift'
        setUpArgs['imageFormat'] = f['extension']
        setUpArgs["imageName"] = f['basename']
        setUpArgs['extensionPadding'] = f['padding_length']
        setUpArgs['byFrameStep'] = frameStep

        defaultImageFormatDic = {'iff': 0, 'exr': 1, 'png': 2, 'tga': 3, 'jpg': 4, 'tif': 5}
        sel = cmds.ls(sl=True)
        sceneName = cmds.file(query=True, location=True)

        # import module File
        if rsModulePath:
            cmds.file(rsModulePath, i=True, ignoreVersion=True)

            # change light position
            self.scaleLightRig('rsAreaLightGroup')

            # import hdr texture
            cmds.setAttr('rsDomeLightModuleShape.tex0', hdrPath, type='string')

        # assign object default materials
        if defaultMaterials:
            assign = self.assignRSMaterial()

        cmds.setAttr("defaultResolution.pixelAspect", setUpArgs['pixelAspect'])
        # cmds.setAttr("defaultResolution.deviceAspectRatio",setUpArgs['deviceAspectRatio'])
        cmds.setAttr('defaultRenderGlobals.animation', setUpArgs['animation'])
        cmds.setAttr('defaultRenderGlobals.putFrameBeforeExt', setUpArgs['putFrameBeforeExt'])
        cmds.setAttr('defaultRenderGlobals.extensionPadding', setUpArgs['extensionPadding'])
        # -- set frameRange --

        if type(startFrame) in (int, float):
            cmds.setAttr('defaultRenderGlobals.startFrame', int(startFrame))
        if type(endFrame) in (int, float):
            cmds.setAttr('defaultRenderGlobals.endFrame', int(endFrame))
        cmds.setAttr('defaultRenderGlobals.byFrameStep', setUpArgs['byFrameStep'])

        # get and set renderer type
        rendererType = setUpArgs['rendererType']
        cmds.setAttr("defaultRenderGlobals.currentRenderer", rendererType, type="string")
        # set render imageType
        if rendererType == 'redshift':
            # set render file type {'iff':0,'exr':1,'png':2,'tga':3,'jpg':4,'tif':5}
            cmds.setAttr("redshiftOptions.imageFormat", defaultImageFormatDic[setUpArgs['imageFormat']])
            if setUpArgs['rsSetUp']:
                setDic = setUpArgs['rsSetUp']
                for key in setDic:
                    if setDic[key]['type'] == None:
                        cmds.setAttr("redshiftOptions.%s" % key, setDic[key]['value'])
                    elif setDic[key]['type'] == 'string':
                        cmds.setAttr("redshiftOptions.%s" % key, setDic[key]['value'], type='string')

        # remove all camera and add current camera
        cam = camera
        allCamera = cmds.ls(type='camera')

        for cm in allCamera:
            camName = cmds.listRelatives(cm, ap=True)[0]
            cmds.setAttr("%s.renderable" % cm, 0)
        camShape = cmds.listRelatives(cam)[0]
        cmds.setAttr("%s.renderable" % camShape, 1)
        # ---------------------------------------------

        if aovOutputPath:
            aovNodes = self._cmds.ls(type='RedshiftAOV')
            for aovNode in aovNodes:
                self.setAttribute(aovNode, 'filePrefix', aovOutputPath, type='string')

        # rs render
        imageName = '%s/%s' % (outputPath, setUpArgs['imageName'])
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", imageName, type='string')

        if not silence:
            if type(resolution) in (list, tuple) and len(resolution) == 2:
                cmds.rsRender(render=True, camera=cam, resolution=resolution,
                              replace=True, batch=True)
            else:
                cmds.rsRender(render=True, camera=cam, replace=True, batch=True)

        # Get output paths
        paths = []

        firstFrame = self.getAttribute('defaultRenderGlobals', 'startFrame')
        lastFrame = self.getAttribute('defaultRenderGlobals', 'endFrame')
        firstFrame, lastFrame = int(firstFrame), int(lastFrame)
        frameRange = '%s-%s' % (firstFrame, lastFrame)
        suffix = '.%s.%s' % (f['padding'], f['extension'])
        suffix1 = suffix + ' ' + frameRange
        suffix = rdlb.covertPadding(suffix)
        suffix1 = rdlb.covertPadding(suffix1)
        beautyInfo = {
            'pass': 'Beauty',
            'path': imageName + suffix,
            'full_path': imageName + suffix1,
            'extension': f['extension'],
            'frame_range': frameRange,
            'filetype': f['extension']
        }

        paths.append(beautyInfo)

        aovNodes = self._cmds.ls(type='RedshiftAOV')
        for aovNode in aovNodes:
            path = self.getAttribute(aovNode, 'filePrefix')
            layer = self.getAttribute(aovNode, 'name')
            # path <BeautyPath>/<RenderPass>/<BeautyFile>.<RenderPass>

            kwargs = {
                '<BeautyPath>': outputPath,
                '<RenderPass>': layer,
                '<BeautyFile>': setUpArgs['imageName']
            }
            for k in kwargs.keys():
                path = path.replace(k, kwargs[k])

            info = {
                'pass': layer,
                'path': path + suffix,
                'full_path': path + suffix1,
                'extension': f['extension'],
                'frame_range': frameRange,
                'filetype': f['extension']
            }

            paths.append(info)

        return paths

    def render(self, path, renderer='', firstFrame=1, lastFrame=60,
               resolution=[1920, 1080], camera=None, overrideMaterials=False,
               enableAOVs=False, frameStep=1, renderSettings={},
               aovs={}, aovOutputPath='', silence=False):
        renderFunc = '%sRender' % renderer

        kwargs = vars().copy()
        del kwargs['self']
        del kwargs['renderer']
        del kwargs['renderFunc']

        # print 'kwargs:',kwargs

        if hasattr(self, renderFunc):
            func = getattr(self, renderFunc)
            # print 'func:',func

            if func:
                if not camera:
                    camera = self.getCurrentView()
                    kwargs['camera'] = camera

                if firstFrame in ('', None):
                    firstFrame = self.frameRange()[0]
                if lastFrame in ('', None):
                    lastFrame = self.frameRange()[1]

                return func(**kwargs)

        return []

    def makeTurntableRenderPreview(self, path, geo, renderer='', firstFrame=1,
                                   lastFrame=60, resolution=None, hdrPath='',
                                   overrideMaterials=False, templatePath='',
                                   frameStep=1):
        renderFunc = '%sRender' % renderer

        kwargs = vars().copy()
        kwargs['enableAOVs'] = False
        del kwargs['self']
        del kwargs['geo']
        del kwargs['renderer']
        del kwargs['renderFunc']

        # print 'kwargs:',kwargs

        if hasattr(self, renderFunc):
            func = getattr(self, renderFunc)
            # print 'func:',func
            self._makeTurntableAnimation(geo, firstFrame=firstFrame, lastFrame=lastFrame,
                                         func=func, redo=False, reopen=True, kwargs=kwargs)

    def makeSceneThumbnail(self, path, objects=[]):
        '''Makes a snapshot image as the scene thumbnail.'''
        camera_views = self.getCurrentView()

        cameraname = self.makeSuitableCamera(objects=objects)
        self._cmds.lookThru(cameraname)

        currentTime = self.currentFrame()
        baseName, ext = os.path.splitext(path)
        ext = ext.replace('.', '')

        self._cmds.playblast(filename=baseName, startTime=currentTime, endTime=currentTime,
                             sequenceTime=0, clearCache=1, viewer=0, showOrnaments=0,
                             fp=0, percent=50, format="image", compression=ext,
                             quality=70, widthHeight=[512, 512])

        self._cmds.delete(cameraname)

        if camera_views:
            self._cmds.lookThru(camera_views)

        result = '%s.%d.%s' % (baseName, currentTime, ext)
        if os.path.exists(path):
            os.remove(path)
        os.rename(result, path)

    # ---------------------------------- Dialog -------------------------------

    def confirmDialog(self, *args, **kwargs):
        return self._cmds.confirmDialog(*args, **kwargs)

    def newSceneConfirmDialog(self):
        btn1 = 'Save'
        btn2 = "Don't Save"
        btn3 = 'Cancel'
        kwargs = {
            'title': 'Warning: Scene Not Saved',
            'message': 'Save changes?',
            'button': [btn1, btn2, btn3],
            # 'defaultButton': btn1,
            # 'cancelButton': btn3,
            # 'dismissString': btn2,
        }
        confirm = self._cmds.confirmDialog(**kwargs)
        # print confirm

        if confirm == btn1:
            return True
        elif confirm == btn2:
            return False
        elif confirm == btn3:
            return

    def saveAsFileDialog(self):
        multipleFilters = "Maya ASCII (*.ma);;Maya Binary (*.mb)"
        filename = self._cmds.fileDialog2(fileMode=0, caption="Save As",
                                          fileFilter=multipleFilters)

        if filename:
            return filename[0]

    def getTexturePaths2(self, rsNormalMap=False):
        '''Gets texture paths for the file nodes.'''
        typeDic = {}

        texDic = {}
        fileNodes = self._cmds.ls(type='file')
        for fn in fileNodes:
            texPath = self._cmds.getAttr("%s.fileTextureName" % fn)
            uvTilingMode = self._cmds.getAttr("%s.uvTilingMode" % fn)

            if texPath:
                if uvTilingMode == 3:  # mode is UDIM,imageName is image sequence
                    # C:\projects\TST\assets\Character\cube\lookdev\publish\textures\versions\2\shitou.spec_rough.<UDIM>.tif
                    if '<UDIM>' in texPath or '<udim>' in texPath:
                        # if '<UDIM>' in texPath:
                        # partten = texPath.replace('<UDIM>','*')
                        partten = texPath.replace('<UDIM>', '*').replace('<udim>', '*')
                        partten2 = os.path.splitext(partten)[0] + '.*'
                        getImageSeq = glob.glob(partten2)
                        # getImageSeq.append(texPath)
                    else:
                        partten = '(?<=\.)\d{3,5}(?=\.)'  # (?<=\.)以.为筛选条件，但不参与

                        fmt = re.sub(partten, '*', texPath)
                        fmt = re.sub('\.\w{2,8}$', '.*', fmt)  # '\.\w{2,4}$' 在字符串末尾找以.结束的2到4个字符

                        getImageSeq = glob.glob(fmt)

                    texDic[fn] = getImageSeq
                else:
                    if '<UDIM>' in texPath or '<udim>' in texPath:
                        partten = texPath.replace('<UDIM>', '*').replace('<udim>', '*')
                        partten2 = os.path.splitext(partten)[0] + '.*'
                        getImageSeq = glob.glob(partten2)
                    else:
                        # fmt = re.sub('\.\w{2,8}$', '.*', texPath)# '\.\w{2,4}$' 在字符串末尾找以.结束的2到4个字符

                        # getImageSeq = glob.glob(fmt)
                        if os.path.isfile(texPath):
                            getImageSeq = [texPath]
                        else:
                            getImageSeq = []
                    texDic[fn] = getImageSeq

        typeDic['file'] = texDic

        if rsNormalMap:
            mapDic = {}
            rsNormalMap = self._cmds.ls(type='RedshiftNormalMap')
            for rsn in rsNormalMap:

                mapPath = self._cmds.getAttr('%s.tex0' % rsn)
                if mapPath and os.path.isfile(mapPath):
                    fmt = re.sub('\.\w{2,8}$', '.*', mapPath)  # '\.\w{2,4}$' 在字符串末尾找以.结束的2到4个字符

                    getImageSeq = glob.glob(fmt)
                    mapDic[rsn] = getImageSeq

            typeDic['rsNormalMap'] = mapDic

        return typeDic

    def replaceTexturePaths2(self, pathInfo, replaceTo=''):
        if pathInfo:
            for L in pathInfo:
                typ, node, oldPath, newPath = L
                if typ == 'file':
                    if replaceTo == 'old':
                        self._cmds.setAttr("%s.fileTextureName" % node, oldPath, type='string')
                    elif replaceTo == 'new':
                        self._cmds.setAttr("%s.fileTextureName" % node, newPath, type='string')

                if typ == 'rsNormalMap':
                    if replaceTo == 'old':
                        try:
                            self._cmds.setAttr("%s.tex0" % node, oldPath, type='string')
                        except:
                            pass
                    elif replaceTo == 'new':
                        try:
                            self._cmds.setAttr("%s.tex0" % node, newPath, type='string')
                        except:
                            pass

    def getCurrentCamera(self):
        return self._cmds.lookThru(q=True)


class Render(object):

    def __init__(self):
        import maya.cmds as cmds
        import maya.app.renderSetup.model.override as override
        import maya.app.renderSetup.model.selector as selector
        import maya.app.renderSetup.model.collection as collection
        import maya.app.renderSetup.model.renderLayer as renderLayer
        import maya.app.renderSetup.model.renderSetup as renderSetup

        self._cmds = cmds
        self.render_setup = renderSetup.instance()
        # self.render_setup.initialize()
        self.override = override
        self.collection = collection
        self.selector = selector
        self.render_layer = renderLayer

    def create_render_layer(self, layer_name):
        '''
        create render layer
        @return: render layer
        '''
        layer_obj = self.render_setup.createRenderLayer(layer_name)
        return layer_obj

    @staticmethod
    def create_collection(render_layer, col_name):
        '''
        create collection of the render layer
        @return: collection
        '''
        col_obj = render_layer.createCollection(col_name)
        return col_obj

    def create_abs_override(self, col_name, over_name):
        '''
        create override of the collection.
        @return: override
        '''
        over_obj = col_name.createOverride(over_name, self.override.AbsOverride.kTypeId)
        return over_obj
