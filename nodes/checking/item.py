# -*- coding: utf-8 -*-
# ==============================================================
#  @Author     : RunningMan
#  @File       : check_item.py
#  @Create Time: 2020/03/11 16:16:11
# ==============================================================

import os

import nodes
import pymel.core as pm
import maya.cmds as cmds

engine = nodes.engine
Action = engine.ActionEngine


def checkOptions(versionNum=4,
                 allMeshs=0,
                 selectOnly=2,
                 historyOn=1,
                 quads=0,
                 nsided=0,
                 concave=0,
                 holed=0,
                 nonplanar=0,
                 zeroGeom=0,
                 zeroGeomTol=0.00001,
                 zeroEdge=0,
                 zeroEdgeTol=0.00001,
                 zeroMap=0,
                 zeroMapTol=0.00001,
                 sharedUVs=0,
                 nonmanifold=-1,
                 lamina=0,
                 invalidComponents=0):
    '''
    int		$versionNum		= $version;                                     The version of arguments being passed

    int		$allMeshes		= $args[0];                                     All selectable meshes
    int		$selectOnly		= $args[1];                                     Only perform a selection
                                                    if == 2:,
                                                    only select check options,don't implement.
    int		$historyOn		= $args[2];                                     keep construction history
    int		$quads			= $args[3];                                     check for quads polys
    int		$nsided			= $args[4];                                     check for n-sided polys
    int		$concave		= $args[5];                                     check for concave polys
    int		$holed			= $args[6];                                     check for holed polys
    int		$nonplanar		= $args[7];                                     check fo non-planar polys
    int		$zeroGeom		= $args[8];                                     check for 0 area faces
    float	$zeroGeomTol	        = $args[9];                                     tolerance for face areas
    int		$zeroEdge	        = $args[10];                                    check for 0 length edges
    float	$zeroEdgeTol	        = $args[11];                                    tolerance for edge length
    int		$zeroMap		= $args[12];                                    check for 0 uv face area
    float	$zeroMapTol		= $args[13];                                    tolerance for uv face areas
    int		$sharedUVs		= ($versionNum >= 2 ? $args[14] : "0");         Unshare uvs that are shared across vertices
    int		$nonmanifold	        = ($versionNum >= 2 ? $args[15] : "0");         check for nonmanifold polys
                                                                                            <= 0 means do not check
                                                                                            1 means cleanup with conform
                                                                                            2 means do not use conform

    int		$lamina			= ($versionNum >= 3 ? $args[16] : "0");         check for lamina polys
    int		$invalidComponents      = ($versionNum >= 4 ? $args[17] : "0");         remove invalid components
    '''


    import pymel.core as pm
    import maya.cmds as cmds

    model_name_list = []
    melCmd = '"{allMeshs}","{selectOnly}","{historyOn}","{quads}","{nsided}","{concave}","{holed}","{nonplanar}","{zeroGeom}","{zeroGeomTol}","{zeroEdge}","{zeroEdgeTol}","{zeroMap}","{zeroMapTol}","{sharedUVs}","{nonmanifold}","{lamina}","{invalidComponents}"'.format(
        allMeshs=allMeshs, selectOnly=selectOnly, historyOn=historyOn,
        quads=quads, nsided=nsided,
        concave=concave, holed=holed,
        nonplanar=nonplanar,
        zeroGeom=zeroGeom,
        zeroGeomTol=zeroGeomTol,
        zeroEdge=zeroEdge,
        zeroEdgeTol=zeroEdgeTol,
        zeroMap=zeroMap,
        zeroMapTol=zeroMapTol,
        sharedUVs=sharedUVs,
        nonmanifold=nonmanifold,
        lamina=lamina,
        invalidComponents=invalidComponents)

    melCmd = 'polyCleanupArgList {versionNum} {args};'.format(versionNum=versionNum, args="{ %s }" % melCmd)

    source = pm.mel.eval(melCmd)

    cmds.delete(all=True, constructionHistory=True)
    return source


class CheckLayer(Action):

    def cnLabel(self):
        return u'Check Hierachy'

    def run(self):
        import os
        import json

        old_name = os.path.basename(cmds.file(loc=1, q=1)).split(".")[0]
        name_split_list = old_name.split("_")
        name_split_list.remove(name_split_list[-2])
        name_split_list[-1] = name_split_list[-1][:4]
        file_name = '_'.join(name_split_list)
        if 'tex' in file_name:
            new_file = file_name.replace("tex", "model")
        elif 'rig' in file_name:
            new_file = file_name.replace("rig", "model")
        else:
            new_file = ''
        # ------------------------------------------------------
        task = engine.getTaskFromEnv()
        assetType = task['sequence']
        asset = task['shot']
        local = cmds.file(loc=1, q=1)
        folderPath = os.path.dirname(os.path.dirname(os.path.dirname(local))) + "/model/approved/"
        if assetType == "set" and "ENVIR" in old_name:
            basename = os.path.basename(os.path.splitext(local)[0])
            lastDesSeq = basename.split('_')[-1]
            json_path = folderPath + "%s_model_ENVIR_%s" % (asset, lastDesSeq) + '.json'
            if not os.path.exists(json_path):
                json_path = folderPath + "%s_model_ENVIR" % (asset) + '.json'
        else:
            # char
            json_path = folderPath + new_file + ".json"
        # ------------------------------------------------------
        # Set(ENV) File，check is error,wait...
        if os.path.exists(json_path):
            with open(json_path, 'r') as load_f:
                compare1 = json.load(load_f)
                compare = compare1.values()[0]
                print "compare:", compare
            list = pm.ls(geometry=1, shapes=1, type="mesh")
            del_camera = pm.ls(type='camera')

            list1 = [i for i in list if i not in del_camera]
            all_list = []
            new_all_list = []
            for i in list1:
                all_list.append(i.longName())
            for i in all_list:
                if "model_GRP" in i:
                    new_all_list.append(i)
            error_list = []
            for obj_name in compare:
                if obj_name in new_all_list:
                    pass
                else:
                    cmds.warning(u"'%s'不存在" % (obj_name))
                    error_list.append(obj_name)
            # print json_path, len(error_list)
            if len(error_list) != 0:
                return error_list
            else:
                return u'OK'
        else:
            return 'Not find Model hierachy file.'


class checkCGtFrame(Action):

    def cnLabel(self):
        return u"Change CGT's Frame"

    def run(self):
        import cgtw
        import dbif
        import maya.cmds as cmds
        t_tw = cgtw.tw()
        data_task = engine.getTaskFromEnv()

        data_base = dbif.CGT().database
        if data_base:
            model = data_task['type']
            t_task_module = t_tw.task_module(str(data_base), str(model), [data_task['task_id']])
            cg_time = t_task_module.get(['shot.frame'])[0]["shot.frame"]
            cg_start_f = t_task_module.get(['shot.first_frame'])[0]['shot.first_frame']
            cg_end_f = t_task_module.get(['shot.last_frame'])[0]['shot.last_frame']

        start_f = cmds.playbackOptions(q=1, ast=1)
        end_f = cmds.playbackOptions(q=1, aet=1)

        ani_time = end_f - start_f + 1

        if int(start_f) == int(cg_start_f) and int(end_f) == int(cg_end_f):
            return "OK"
        else:
            return "CGT's frame range is not the same as Maya"

    def fix(self):
        import cgtw
        import dbif
        t_tw = cgtw.tw()

        data_task = engine.getTaskFromEnv()
        data_base = dbif.CGT().database
        t_shot = t_tw.info_module(data_base, "shot")
        t_shot.init_with_id([data_task['shot_id']])

        start_f = cmds.playbackOptions(q=1, ast=1)
        end_f = cmds.playbackOptions(q=1, aet=1)
        ani_time = end_f - start_f + 1

        print t_shot.set({'shot.frame': ani_time})
        print t_shot.set({'shot.first_frame': start_f})
        print t_shot.set({'shot.last_frame': end_f})

        return "OK"


class changeAniFrame(Action):

    def cnLabel(self):
        return u"Change Maya Frame Range"

    def run(self):
        import maya.cmds as cmds
        
        import cgtw
        import dbif

        t_tw = cgtw.tw()
        data_task = engine.getTaskFromEnv()

        data_base = dbif.CGT().database
        if data_base:
            model = data_task['type']
            t_task_module = t_tw.task_module(str(data_base), str(model), [data_task['task_id']])
            cg_time = t_task_module.get(['shot.frame'])[0]["shot.frame"]
            cg_start_f = t_task_module.get(['shot.first_frame'])[0]['shot.first_frame']
            cg_end_f = t_task_module.get(['shot.last_frame'])[0]['shot.last_frame']

        start_f = cmds.playbackOptions(q=1, ast=1)
        end_f = cmds.playbackOptions(q=1, aet=1)

        ani_time = end_f - start_f + 1

        if int(start_f) == int(cg_start_f) and int(end_f) == int(cg_end_f):
            return "OK"
        else:
            return "Maya's frame range is not the same with CGT"

    def fix(self):
        import maya.cmds as cmds
        
        import cgtw
        import dbif
        t_tw = cgtw.tw()

        data_task = engine.getTaskFromEnv()
        data_base = dbif.CGT().database
        t_shot = t_tw.info_module(data_base, "shot")
        t_shot.init_with_id([data_task['shot_id']])

        ani_time = t_shot.get(['shot.frame'])[0]['shot.frame']
        start_f = t_shot.get(['shot.first_frame'])[0]['shot.first_frame']
        end_f = t_shot.get(['shot.last_frame'])[0]['shot.last_frame']

        cmds.playbackOptions(aet=end_f, max=end_f)
        cmds.playbackOptions(ast=start_f, min=start_f)

        return "OK"


class CheckCamera(Action):
    def cnLabel(self):
        return u'Check Camera Name'

    def run(self):
        import maya.cmds as cmds
        
        # self.cam_name = "cam"+"_"+engine.getTaskFromEnv()["sequence"][-3:]+"_"+engine.getTaskFromEnv()["shot"][-3:]
        self.cam_name = "cam" + '_' + filter(str.isdigit, str(engine.getTaskFromEnv()["sequence"])) + '_' + filter(
            str.isdigit, str(engine.getTaskFromEnv()["shot"]))

        allCamera = cmds.ls(cameras=True, long=True)
        defaultCamera = ['|persp', '|front', '|side', '|top', '|back', '|left', '|right', '|bottom']
        cameraList = []
        for i in allCamera:
            cameraName = cmds.listRelatives(i, allParents=True, fullPath=True)[0]
            if cameraName not in defaultCamera:
                cameraList.append(cameraName)
        self.name = cameraList[0].split('|')[-1]
        self.name = self.name.split(':')[-1]
        if self.name == self.cam_name:
            return "OK"
        else:
            return "Please check camera's name"

    def fix(self):
        import pymel.core as pm
        import maya.cmds as cmds
        node = pm.PyNode(self.name)
        long = node.longName()
        cmds.rename(long, self.cam_name)


class CheckUnknown(Action):

    def cnLabel(self):
        return u'Check Unknown Nodes'

    def run(self):
        import maya.cmds as cmds
        if cmds.ls(type=["unknown", "unknownDag", "unknownTransform"]):
            return u"There are unknownNodes!"
        else:
            return "OK"

    def fix(self):
        import maya.cmds as cmds
        try:
            for i in cmds.ls(type=["unknown", "unknownDag", "unknownTransform"]):
                cmds.delete(i)
        except:
            pass


class RenameShape(Action):
    def cnLabel(self):
        return u'Rename Shape Node'

    def run(self):
        
        data = engine.getTaskFromEnv()
        if data["asset_type"] == "char":
            import pymel.core as pm
            import maya.cmds as cmds
            list = pm.ls(geometry=1, shapes=1, type="mesh")
            del_camera = pm.ls(type='camera')
            list1 = [i for i in list if i not in del_camera]
            for i in list1:
                shape = i.longName().split("|")[-1]
                if "Orig" in shape:
                    if not cmds.listConnections(str(i)):
                        cmds.delete(str(i))
        return "OK"


class DeleteOrig(Action):
    def cnLabel(self):
        return u'删除无用的orig'

    def run(self):
        import pymel.core as pm
        import maya.cmds as cmds
        list = pm.ls(geometry=1, shapes=1, type="mesh")
        del_camera = pm.ls(type='camera')
        list1 = [i for i in list if i not in del_camera]
        for i in list1:
            shape = i.longName().split("|")[-1]
            if "Orig" in shape:
                if not cmds.listConnections(str(i)):
                    cmds.delete(str(i))
        return "OK"


class CheckUnknownPlugin(Action):

    def cnLabel(self):
        return u'Chec Unknown Plugin'

    def run(self):
        import maya.cmds as cmds
        cmds.dataStructure(removeAll=True)
        all_unknownPlug = cmds.unknownPlugin(q=True, l=True)
        if all_unknownPlug:
            return u"There are extra useless plug-ins"

    def fix(self):
        import maya.cmds as cmds
        all_unknownPlug = cmds.unknownPlugin(q=True, l=True)
        if all_unknownPlug:
            for i in all_unknownPlug:
                try:
                    cmds.unknownPlugin(i, r=1)
                except:
                    pass
        cmds.dataStructure(removeAll=True)
        return "OK"


class RenameShape1(Action):
    def cnLabel(self):
        return u'Rename Shape Node'

    def run(self):
        import pymel.core as pm
        import maya.cmds as cmds
        list = pm.ls(geometry=1, shapes=1, v=1, type="mesh")
        del_camera = pm.ls(type='camera')
        list1 = [i for i in list if i not in del_camera]
        all_list = []
        un_rename = []
        for i in list1:
            shape = i.longName().split("|")[-1]
            if "Deformed" in shape:
                # print shape
                # print i.longName()
                # print len(shape.split("_"))
                if len(shape.split("_")) == 3:
                    seq = (shape.split("_")[-3], shape.split("_")[-2], "SG")
                elif len(shape.split("_")) == 2:
                    seq = (shape.split("_")[-2], "SG")
                else:
                    seq = (shape.split("_")[-3], shape.split("_")[-2], "SG")
                newshape = "_".join(seq)
                all_list.append(newshape)
                try:
                    cmds.rename(i.longName(), newshape)
                except:
                    print i.longName()
        return "OK"


class DelHistory(Action):
    def cnLabel(self):
        return u'Delete History'

    def run(self):
        import maya.cmds as cmds
        import maya.mel as mel
        mel.eval('DeleteHistory;')
        cmds.delete(ch=1)
        return "OK"


class FreezeTr(Action):
    def cnLabel(self):
        u'冻结变换'
        return u'Freeze Transformations'

    def run(self):
        import maya.mel as mel
        import maya.cmds as cmds
        del_ls = [u'persp', u'top', u'front', u'side']
        cmds.select([i for i in cmds.ls(assemblies=True) if i not in del_ls])
        mel.eval('FreezeTransformations;')
        return "OK"


class CheckInvalidVertices(Action):
    def cnLabel(self):
        return u'Check Invalid Vertices'

    def run(self):
        import maya.cmds as cmds
        allTrsf = cmds.ls(type='transform')
        cmds.select(allTrsf)
        ver = cmds.polyInfo(invalidVertices=True)
        cmds.select(deselect=True)
        if not ver:
            return "OK"
        else:
            return ver

    def fix(self):
        import maya.cmds as cmds
        allTrsf = cmds.ls(type='transform')
        cmds.select(allTrsf)
        ver = cmds.polyInfo(invalidVertices=True)
        cmds.delete(ver)
        return "OK"


class CheckZeroAreaFaces(Action):
    def cnLabel(self):
        return u'Check Zero Area Faces'

    def run(self):
        get = checkOptions(allMeshs=1, selectOnly=2, zeroGeom=1, zeroGeomTol=0.00001)
        if get:
            return get

    def fix(self):
        import maya.cmds as cmds
        get = checkOptions(allMeshs=1, selectOnly=1, zeroGeom=1, zeroGeomTol=0.00001)
        if get:
            cmds.delete(get)

    def select(self, objs):
        import maya.cmds as cmds
        cmds.select(objs, r=1)


class CheckFacesWithHoles(Action):
    def cnLabel(self):
        return u'Check Faces With Holes'

    def run(self):
        import maya.cmds as cmds
        cmds.select(cmds.ls(exactType='mesh'))
        cmds.polySelectConstraint(mode=3, type=0x8000, where=1)
        hole_face = cmds.ls(sl=1)
        cmds.polySelectConstraint(disable=1)
        if hole_face:
            return hole_face
        else:
            return "OK"

    def select(self, objs):
        import maya.cmds as cmds
        cmds.select(objs, r=1)


class CheckRigVersion(Action):

    def getCharAsset(self):
        data = engine.getTaskFromEnv()
        list = []
        t_tw = self.cgtw2.tw()
        task_id_list = t_tw.task.get_id("proj_longgong_0", "shot", [["shot.shot", "=", data["shot"]]])
        i = task_id_list[0]
        link_id_list = t_tw.link.get_asset('proj_longgong_0', 'shot', 'task', i)
        if len(link_id_list) > 0:
            t_asset_list = t_tw.info.get('proj_longgong_0', 'asset', link_id_list, ['asset.asset_name'])
            for n in t_asset_list:
                # print u"资产信息:",n
                list.append(n["asset.asset_name"])

        temp = []
        for i in list:
            if "char" in i:
                temp.append(i)
        return temp

    def getAllRFs(self):
        import maya.cmds as cmds
        '''获取不存在的RF文件'''
        RFfiles = []
        for i in cmds.ls(rf=1):
            if "_UNKNOWN_REF_NODE_" not in i:
                try:
                    path = cmds.referenceQuery(i, filename=True)
                    if "{" not in path:
                        RFfiles.append(path)
                except:
                    pass
        RFfiles = list(set(RFfiles))
        char = self.getCharAsset()

        charfile = {}
        for file in RFfiles:
            file = file.replace("//", "/")
            if file.split("/")[3] == "char":
                charname = file.split("/")[4]
                charname = charname[0].lower() + charname[1:]
                t_tw = self.cgtw.tw()
                t_shot = t_tw.info_module("proj_longgong_0", "version")
                filters = ([
                    ["version.step", "=", "Rig"],
                    "and",
                    ["version.version_type", "=", "publish"],
                    "and",
                    ["version.shot", "=", charname]
                ]
                )
                t_shot.init_with_filter(filters)
                version = []
                for i in t_shot.get(["version.version"]):
                    version.append(i['version.version'])
                version.sort()

                message = {}
                ver = "".join([x for x in self.os.path.basename(file) if x.isdigit()])
                if ver:
                    message['version'] = "v" + ver
                else:
                    message['version'] = version[-1]

                message['last_version'] = version[-1]
                charfile[charname] = message
        return charfile

    def cnLabel(self):
        return u'Check Rig Version'

    # UI
    def run(self):
        import sys
        sys.path.append(r"c:/cgteamwork/bin/base")
        import cgtw
        import cgtw2
        import maya.cmds as cmds
        import os

        self.cgtw = cgtw
        self.cgtw2 = cgtw2
        self.cmds = cmds
        self.os = os

        rf = self.getAllRFs()
        message = ""
        for num, ch in enumerate(rf):
            if rf[ch]['version'] != rf[ch]['last_version']:
                message += str(num + 1) + ". '%s' current version is '%s', but the lasted version is '%s'\n" % (
                    ch, rf[ch]['version'], rf[ch]['last_version'])
            else:
                message += str(num + 1) + ". '%s' current version is the latest version '%s'\n" % (
                    ch, rf[ch]['version'])

        return message


class CheckAovs(Action):
    def cnLabel(self):
        return u'Check Aovs Layers'

    def run(self):
        import maya.cmds as cmds
        allAovList = cmds.ls(type="aiAOV")
        if allAovList:
            return 'Ther are extra Aovs layers.'

    def fix(self):
        import maya.cmds as cmds
        for i in cmds.ls(type="aiAOV"):
            cmds.delete(i)


# useless
class CleanScene(Action):
    def cnLabel(self):
        return u'Clean Scene(expression,deleteComponent,script,renderLayer)'

    def run(self):
        import maya.cmds as cmds
        del_exp = []
        for i in cmds.ls(type='expression'):
            if "xgm" in i:
                del_exp.append(i)
        comp = cmds.ls(type='deleteComponent')
        script_ls = cmds.ls(type='script')
        render_ls = cmds.ls(type="renderLayer")
        render_ls.remove("defaultRenderLayer")
        result = del_exp + comp + script_ls + render_ls
        return result

    def fix(self):
        import maya.cmds as cmds
        del_exp = []
        for i in cmds.ls(type='expression'):
            if "xgm" in i:
                del_exp.append(i)
        comp = cmds.ls(type='deleteComponent')
        script_ls = cmds.ls(type='script')
        render_ls = cmds.ls(type="renderLayer")
        render_ls.remove("defaultRenderLayer")

        result = comp + del_exp + script_ls + render_ls
        for i in result:
            try:
                cmds.delete(i)
            except:
                pass

        try:
            cmds.dataStructure(removeAll=True)
        except:
            pass

        return "OK"


class CheckObjcetCenter(Action):
    def cnLabel(self):
        return u'Check Objcet Center'

    def run(self):
        import maya.cmds as cmds
        CTL_ls = cmds.ls("*m_all_CTL", r=True)
        result = []
        for i in CTL_ls:
            if "translateX" in cmds.listAttr(i):
                if cmds.getAttr(i + ".translateX") != 0 or cmds.getAttr(i + ".translateY") != 0 or cmds.getAttr(
                        i + ".translateZ") != 0:
                    result.append("1")
                else:
                    result.append("0")
        if "0" in result:
            return u"There are objs at the center"
        else:
            return "OK"


class CheckNameSpace(Action):
    def cnLabel(self):
        return u'Check Namespace'

    def run(self):
        import maya.cmds as cmds
        nonamespace = []
        for i in cmds.ls(rf=1):
            try:
                if len(cmds.referenceQuery(i, namespace=True)) <= 1:
                    nonamespace.append(i)
            except:
                pass
        result = ''
        if nonamespace:
            for i in nonamespace:
                result += i + " doesn't have namespace.  "
            return result


class NonManifoldPolys(Action):
    def cnLabel(self):
        u'检查非流体面'
        return 'NonManifold Polys'

    def run(self):
        '''
        check for non manifold polys.

        A non manifold edge is a surface with
        three or more joints on the same edge.
        The presence of such an edge indicates
        that there may be repeated surfaces or
        T-joints.
        '''
        get = checkOptions(allMeshs=1, selectOnly=2, nonmanifold=1)
        return get

    def fix(self):
        checkOptions(allMeshs=1, selectOnly=1, nonmanifold=1)


class CheckReference(Action):
    def cnLabel(self):
        return u'Check Import file'

    def run(self):
        import maya.cmds as cmds
        defaultCamera = ['persp', 'front', 'side', 'top',
                         'back', 'left', 'right', 'bottom']
        all = []
        for i in cmds.ls(assemblies=True):
            if "char" in i or "set" in i or "prop" in i:
                all.append(i)
        noRF = []
        for i in all:
            if i not in defaultCamera:
                if not cmds.referenceQuery(i, isNodeReferenced=True):
                    noRF.append(i)
        result = ''
        if noRF:
            for i in noRF:
                result += i + " is not reference file. "
            return result
        else:
            return "OK"


class DeleteExtraMaterial(Action):

    def cnLabel(self):
        u'删除多余材质'
        return 'Delete Extra Material'

    def getSgLinkMat(self):
        import maya.cmds as cmds
        defaultSE = [u'initialParticleSE', u'initialShadingGroup']
        allSE = cmds.ls(type='shadingEngine')
        allSE = list(set(allSE).difference(set(defaultSE)))

        result = []
        for se in allSE:
            if cmds.defaultNavigation(destination=se + ".surfaceShader", defaultTraversal=True) == [] and cmds.getAttr(
                    se + ".volumeShader") == None and cmds.getAttr(se + ".displacementShader") == None:
                result.append(se)
            else:
                pass
        return result

    def getOmitMaterials(self):
        import maya.cmds as cmds
        defaultSE = [u'initialParticleSE', u'initialShadingGroup']
        allSE = cmds.ls(type='shadingEngine')
        allSE = list(set(allSE).difference(set(defaultSE)))

        result = []
        for se in allSE:
            temp = cmds.listConnections(se, d=True, type='mesh')
            if not temp:
                result.append(se)
        return result

    def run(self):
        if self.getOmitMaterials() or self.getSgLinkMat():
            return u"There are extra materials"

    def fix(self):
        import maya.cmds as cmds
        for i in self.getOmitMaterials():
            material = cmds.defaultNavigation(destination=i + ".surfaceShader", defaultTraversal=True)
            cmds.delete(material)
            cmds.delete(i)
        if self.getSgLinkMat():
            for i in self.getSgLinkMat():
                cmds.delete(i)
        return "OK"


class CheckProxyEyes(Action):
    def cnLabel(self):
        u'检查眼球插件'
        return 'Check Proxy Eyes'

    def run(self):
        import maya.cmds as cmds
        for i in cmds.ls("*.showProxyEyes", r=1):
            cmds.cutKey(i, clear=True)
            cmds.setAttr(i, 0)
        return "OK"


class CheckCharState(Action):
    def cnLabel(self):
        return u"Check Character's state"

    def getAllRFs(self):
        '''获取不存在的RF文件'''
        import maya.cmds as cmds
        RFfiles = []
        for i in cmds.ls(rf=1):
            if i == "_UNKNOWN_REF_NODE_":
                continue

            if "char" in i:
                try:
                    path = cmds.referenceQuery(i, filename=True)
                except:
                    continue
                if "{" not in path:
                    file = path.replace("//", "/")
                    if file.split("/")[3] == "char":
                        RFfiles.append(path)
        RFfiles = list(set(RFfiles))
        return RFfiles

    def run(self):
        import sys
        sys.path.append("C:/cgteamwork/bin/base")
        sys.path.append('C:/cgteamwork/bin/cgtw')
        import cgtw2

        noPublsh = []
        for i in self.getAllRFs():
            file = i.replace("//", "/")
            charname = i.split("/")[4]

            filters = ([
                ["asset.asset_name", "=", charname],
                "and",
                ["task.pipeline", "=", "Rig"],
                "and",
                ["task.task_name", "=", "Rig"]
            ]
            )
            t_tw = cgtw2.tw()

            t_id_list = t_tw.task.get_id('proj_longgong_0', 'asset', filters)

            if t_id_list:

                dir = t_tw.task.get('proj_longgong_0', "asset", t_id_list, ['task.sup_review'])

                if dir[0]['task.sup_review'] != "Published":
                    noPublsh.append(charname)
            else:
                print 'have not asset "%s"' % charname
        result = ''
        if noPublsh:
            for i in noPublsh:
                result += i + " is not published.  "
            return result
        else:
            return "OK"


class CheckTriangleFace(Action):
    def cnLabel(self):
        u'检查三角面(针对于角色动画)'
        return u'Check Triangle Face(For The Characters)'

    def getNPolygonFaces_bak(self, n=4):
        '''
        n:  greater than {4}
        '''
        import maya.cmds as cmds
        import pymel.core as pm
        filterSides = n
        all = cmds.ls(type="mesh")
        all = [i for i in all if not cmds.getAttr("%s.intermediateObject" % i)]
        multilateralFace = []
        for i in all:
            cmds.select(i)
            pm.mel.eval('ConvertSelectionToFaces;')
            faces = cmds.ls(sl=True, flatten=True)
            for f in faces:
                edges = cmds.polyListComponentConversion(f, te=True)
                vfList = cmds.ls(edges, flatten=True)
                edgesNum = len(vfList)
                if edgesNum == filterSides:
                    multilateralFace.append(f)
        return multilateralFace

    def run(self):
        data_task = engine.getTaskFromEnv()
        if data_task['sequence'] == "char":
            self.objs = self.getNPolygonFaces_bak(3)
            if self.objs:
                return self.objs
            else:
                return "OK"
        else:
            return "OK"

    def select(self):
        import maya.cmds as cmds
        cmds.select(self.objs, r=1)


class CleanDistanceBetweenNodes(Action):
    def cnLabel(self):
        return u'Check distanceBetween nodes'

    def run(self):
        import maya.cmds as cmds
        result = []
        distanceBt_node = cmds.ls(type="distanceBetween")
        for i in distanceBt_node:
            source_ls = cmds.listConnections(i, source=True)
            if source_ls:
                if len(set(i)) == 1:
                    result.append(i)
            elif source_ls == None:
                result.append(i)

        # ----------- OK
        # deleteCm_node = cmds.ls(type = "deleteComponent")
        # for i in deleteCm_node:
        # source_ls = cmds.listConnections(i, source=True)
        # if source_ls == None:
        # result.append(i)

        # ----------- OK
        # nodeGE = cmds.ls(type = "nodeGraphEditorInfo")
        # for i in nodeGE:
        # source_ls = cmds.listConnections(i, source=True)
        # if source_ls == None:
        # result.append(i)

        # ----------- OK
        # materialInfo = cmds.ls(type = "materialInfo")
        # for i in materialInfo:
        # source_ls = cmds.listConnections(i, source=True)
        # if source_ls == None:
        # result.append(i)

        self.result = result

        return self.result

    def fix(self):
        import maya.cmds as cmds
        for i in self.result:
            cmds.delete(i)


class LockCmaera(Action):
    def cnLabel(self):
        return u'Lock Cmaera'

    def run(self):
        import maya.cmds as cmds
        cam = cmds.ls(type="camera")
        for i in cam:
            if cmds.referenceQuery(i, isNodeReferenced=True):
                cmds.camera(i, e=True, lockTransform=True)
            else:
                if "cam" in i:
                    cmds.camera(i, e=True, lockTransform=True)
        return "OK"


class FramePreview(Action):
    def cnLabel(self):
        return u'Frame Preview and check T-pose '

    def run(self):
        import maya.cmds as cmds
        cmds.playbackOptions(ast=971)
        return "Please note if the first frame is T-pose"


class LockRigVersion(Action):

    def getFilters(self, path):
        '''过滤资产条件'''
        dir = {}
        pathLs = path.replace("//", "/").split("/")
        if pathLs[2] == "assets":
            dir["two"] = 'asset'
        dir["type"] = pathLs[3]
        if pathLs[5] == "model":
            dir["stage"] = "Model"
        elif pathLs[5] == "rig":
            dir["stage"] = "Rig"
        elif pathLs[5] == "surface":
            dir["stage"] = "Texture"
        else:
            dir["stage"] = pathLs[5]

        dir["asestname"] = pathLs[4]
        return dir

    def cnLabel(self):
        return u'Lock Rig Verison'

    def run(self):
        import maya.cmds as cmds
        m_all_CTL = [x for x in cmds.ls("*m_all_CTL", r=True) if "char" in x]

        for i in m_all_CTL:
            if cmds.referenceQuery(i, isNodeReferenced=True):
                rig_version = cmds.getAttr(i + '.rigVersion')
                file_path = cmds.referenceQuery(i, filename=True)
                old_name = os.path.basename(file_path)
                num = filter(str.isdigit, str(old_name))

                if num != filter(str.isdigit, str(old_name)):
                    return ''
                else:
                    return "%s need to lock the rig version" % (cmds.referenceQuery(i, referenceNode=True))

    def fix(self):
        import sys, os
        sys.path.append(r"C:/cgteamwork/bin/base")
        import cgtw2
        import maya.cmds as cmds
        m_all_CTL = [x for x in cmds.ls("*m_all_CTL", r=True) if "char" in x]

        for i in m_all_CTL:
            if cmds.referenceQuery(i, isNodeReferenced=True):
                rig_version = cmds.getAttr(i + '.rigVersion')
                file_path = cmds.referenceQuery(i, filename=True)

                t_tw = cgtw2.tw()
                dir = self.getFilters(file_path)
                id_list = t_tw.info.get_id('proj_longgong_0', 'asset',
                                           [["asset.asset_name", "=", dir["asestname"]], 'and',
                                            ['asset.type_name', '=', dir["type"]]])
                target_path = t_tw.info.get_dir("proj_longgong_0", 'asset', id_list, ["Rig_publish_versions"])[0][
                    'Rig_publish_versions']

                old_name = os.path.basename(file_path)
                num = filter(str.isdigit, str(old_name))

                if num != filter(str.isdigit, str(rig_version)):
                    print num, i
                else:
                    name_ls = old_name.split("_")
                    name_ls.insert(2, rig_version)
                    new_name = "_".join(name_ls)
                    path = target_path + "/" + new_name
                    rf_node = cmds.referenceQuery(i, referenceNode=True)
                    cmds.file(path, loadReference=rf_node, type="mayaBinary", options="v=0;")
            else:
                pass


# useless
class CheckFullMaterial(Action):
    def cnLabel(self):
        return u'check lambert materials'

    def run(self):
        import maya.cmds as cmds
        defaultSE = [u'initialParticleSE', u'initialShadingGroup']
        allSE = cmds.ls(type='shadingEngine')
        allSE = list(set(allSE).difference(set(defaultSE)))
        result = []
        for i in allSE:
            sf_node = cmds.listConnections(i + ".surfaceShader", source=True)[0]
            if "lambert" in sf_node:
                shape = cmds.listConnections(i, type="shape")
                for i in cmds.ls(shape, long=True):
                    result.append(i)
        if result:
            return result
        else:
            return ""

    def select(self, objs):
        import maya.cmds as cmds
        cmds.select(result)


class KeyNurbsCurve970(Action):

    def cnLabel(self):
        return 'key nurbsCurve 970'

    def getControl(self, topGroup):
        import maya.cmds as cmds
        allNurbsCurve = cmds.ls(topGroup, type='nurbsCurve', dag=True)

        masterControl = ['m_all_CTL', 'm_all2_CTL', 'm_all3_CTL', 'm_all4_CTL']

        otherControl = []

        for sp in allNurbsCurve:
            curveTransfList = cmds.listRelatives(sp, p=True, fullPath=True)
            if curveTransfList:
                curveTransf = curveTransfList[0]

                shortTransf = curveTransf.split('|')[-1]
                if ":" in shortTransf:
                    shortTransf = shortTransf.split(':')[-1]

                if shortTransf not in masterControl and shortTransf.endswith('CTL'):
                    otherControl.append(curveTransf)

        return otherControl

    def run(self):
        import maya.cmds as cmds
        import pymel.core as pm
        allControl = []
        singleControl = []
        assetList = ['charHei', 'charMei', 'charPMTurtle', 'charCuttleFish']
        topGroup = cmds.ls(assemblies=True)

        refPathList = []
        for g in topGroup:
            if cmds.referenceQuery(g, isNodeReferenced=True):
                node = cmds.referenceQuery(g, rfn=True)

                try:
                    filePath = cmds.referenceQuery(node, filename=True)
                    s = 1
                except:
                    s = 0

                if s:
                    if filePath not in refPathList:
                        refPathList.append(filePath)
                        #
                        assetName = filePath.split('/')[4]

                        if assetName in assetList:
                            ctlList = self.getControl(g)
                            if ctlList:
                                allControl += ctlList
                                singleControl.append(ctlList[0])

        cmds.currentTime(970)
        if singleControl:
            cmds.select(singleControl)
            pm.mel.eval('source goToDefaultPose.mel;')
        if allControl:
            cmds.setKeyframe(allControl, breakdown=0, hierarchy="none", controlPoints=0, shape=0)


class CleanHistory(Action):
    def cnLabel(self):
        return 'Clean History'

    def run(self):
        import maya.cmds as cmds
        cmds.delete(all=True, constructionHistory=True)


class RenameDuplicateShape(Action):
    def cnLabel(self):
        return u'重命名重复的Shape/Object'

    def run(self):
        import maya.cmds as cmds

        # rename transform
        allMesh = cmds.ls(type='transform', long=True)

        sortList = []
        for m in allMesh:
            shortName = m.split('|')[-1]

            # print shortName
            if shortName not in sortList:
                sortList.append(shortName)
            else:
                continue

            num = cmds.ls(shortName)
            if len(num) > 1:
                # print shortName,num
                for i in xrange(len(num)):
                    shape = num[i]
                    if not cmds.referenceQuery(shape, isNodeReferenced=True):
                        cmds.rename(shape, shortName + str(i))


class DeleteUnlinkedShape(Action):
    def cnLabel(self):
        return 'Delete Unlinked Shape'

    def run(self):
        import maya.cmds as cmds
        allM = cmds.ls(type='mesh')
        self.s = []
        for i in allM:
            if not cmds.listConnections(i):
                self.s.append(i)

        return self.s

    def fix(self):
        import maya.cmds as cmds
        for i in self.s:
            cmds.delete(i)


class DeviceAspectRatio(Action):
    def cnLabel(self):
        return 'Device/Pixel Aspect Ratio'

    def run(self):
        import maya.cmds as cmds
        d = cmds.getAttr("defaultResolution.deviceAspectRatio")
        p = cmds.getAttr("defaultResolution.pixelAspect")

        d = float("%.3f" % d)
        p = float("%.3f" % p)

        if d != 2.347 or p != 1.0:
            return [str(d), str(p)]

    def fix(self):
        import maya.cmds as cmds
        cmds.setAttr("defaultResolution.deviceAspectRatio", 2.347)
        cmds.setAttr("defaultResolution.pixelAspect", 1.00)

    # ------------------------ clear Node Tool ---------------------


class DeleteTurtleObject(Action):
    def cnLabel(self):
        return 'Delete Turtle Object'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('turtle_proc(0,1);')
        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('turtle_proc(1,1);')


class DeleteUselessGroupId(Action):
    def cnLabel(self):
        return 'Delete Useless GroupId'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('groupId_proc(0,1);')

        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('groupId_proc(1,1);')


class DeleteAiOptions(Action):
    def cnLabel(self):
        return 'Delete aiOptions'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('aiOptions_proc(0,1);')

        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('aiOptions_proc(1,1);')


class DeleteAiAOVDriver(Action):
    def cnLabel(self):
        return 'Delete aiAOVDriver'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('aiAOVDriver_proc(0,1);')

        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('aiAOVDriver_proc(1,1);')


class DeleteDeleteComponentNode(Action):
    def cnLabel(self):
        return 'Delete deleteComponent Node'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('deleteComponent_proc(0,1);')

        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('deleteComponent_proc(1,1);')


class DeleteUselessXgenNode(Action):
    def cnLabel(self):
        return 'Useless Xgen Node'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('expression_proc(0,1);')

        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('expression_proc(1,1);')


class DeleteUselessRenderSetupNode(Action):
    def cnLabel(self):
        return 'Useless RenderSetup Node'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('renderSetup_proc(0,1);')

        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('renderSetup_proc(1,1);')


class DeleteUselessSGNode(Action):
    def cnLabel(self):
        return 'Useless SG Node'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('nullSE_proc(0,1);')
        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('nullSE_proc(1,1);')


class DeleteUselessNodeGraphEditorInfoNode(Action):
    def cnLabel(self):
        return 'Useless NodeGraphEditorInfo Node'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('nodeGraphEditorInfo_proc(0,1);')
        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('nodeGraphEditorInfo_proc(1,1);')


class DeleteUselessMaterialInfoNode(Action):
    def cnLabel(self):
        return 'Useless materialInfo Node'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('materialInfo_proc(0,1);')
        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('materialInfo_proc(1,1);')


class DeleteDataStructure(Action):
    def cnLabel(self):
        return 'DataStructure'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('dataStructure_proc(0,1);')
        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('dataStructure_proc(1,1);')


class DeleteHyperLayoutNode(Action):
    def cnLabel(self):
        return 'HyperLayout Node'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('hyperLayout_proc(0,1);')
        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('hyperLayout_proc(1,1);')


class DeleteHyperViewNode(Action):
    def cnLabel(self):
        return 'HyperView Node'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('hyperView_proc(0,1);')
        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('hyperView_proc(1,1);')


class DeleteNodeGraphEditorBookmarkInfoNode(Action):
    def cnLabel(self):
        return 'NodeGraphEditorBookmarkInfo Node'

    def run(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('nodeGraphEditorBookmarkInfo_proc(0,1);')
        return result

    def fix(self):
        import pymel.core as pm
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('nodeGraphEditorBookmarkInfo_proc(1,1);')


class DeleteDataReferenceEditsNode(Action):
    def cnLabel(self):
        return 'DataReferenceEdits Node'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('dataReferenceEdits_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('dataReferenceEdits_proc(1,1);')


class DeleteUselessReference(Action):
    def cnLabel(self):
        return 'Useless Reference'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('reference_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('reference_proc(1,1);')


class DeleteRenderLayer(Action):
    def cnLabel(self):
        return 'Useless RenderLayer'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('renderLayer_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('renderLayer_proc(1,1);')


class DeleteRenderSetupLayer(Action):
    def cnLabel(self):
        return 'Useless Render Setup Layer'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('renderSetupLayer_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('renderSetupLayer_proc(1,1);')


class IntermediateObject(Action):
    def cnLabel(self):
        return 'Intermediate Object'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('intermediateObject_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('intermediateObject_proc(1,1);')

    # 20190730


class DeleteUselessScript(Action):
    def cnLabel(self):
        return 'Useless Script'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('script_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('script_proc(1,1);')


class DeleteUselessExpression(Action):
    def cnLabel(self):
        return 'Useless Expression'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('expression_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('expression_proc(1,1);')


class DeleteUselessCurveInfo(Action):
    def cnLabel(self):
        return 'Useless CurveInfo'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('curveInfo_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('curveInfo_proc(1,1);')


class DeleteUselessPointOnCurveInfo(Action):
    def cnLabel(self):
        return 'Useless PointOnCurveInfo'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('pointOnCurveInfo_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('pointOnCurveInfo_proc(1,1);')


class DeleteUselessPointOnSurfaceInfo(Action):
    def cnLabel(self):
        return 'Useless PointOnSurfaceInfo'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('pointOnSurfaceInfo_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('pointOnSurfaceInfo_proc(1,1);')


class DeleteUselessClosestPointOnSurface(Action):
    def cnLabel(self):
        return 'Useless ClosestPointOnSurface'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('closestPointOnSurface_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('closestPointOnSurface_proc(1,1);')


class DeleteUselessDistanceBetween(Action):
    def cnLabel(self):
        return 'Useless DistanceBetween'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('distanceBetween_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('distanceBetween_proc(1,1);')


class DeleteUselessWire(Action):
    def cnLabel(self):
        return 'Useless Wire'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('wire_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('wire_proc(1,1);')


class DeleteUselessPolyUnite(Action):
    def cnLabel(self):
        return 'Useless PolyUnite'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('polyUnite_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('polyUnite_proc(1,1);')


class DeleteUselessBlendWeighted(Action):
    def cnLabel(self):
        return 'Useless BlendWeighted'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('blendWeighted_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('blendWeighted_proc(1,1);')


class DeleteUselessAnimCurve(Action):
    def cnLabel(self):
        return 'Useless AnimCurve'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('animCurve_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('animCurve_proc(1,1);')


class DeleteUselessGroupParts(Action):
    def cnLabel(self):
        return 'Useless GroupParts'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('groupParts_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('groupParts_proc(1,1);')


class DeleteUselessPartition(Action):
    def cnLabel(self):
        return 'Useless Partition'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('partition_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('partition_proc(1,1);')


class DeleteUselessPoseInterpolatorManager(Action):
    def cnLabel(self):
        return 'Useless PoseInterpolatorManager'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('poseInterpolatorManager_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('poseInterpolatorManager_proc(1,1);')


class DeleteUselessShapeEditorManager(Action):
    def cnLabel(self):
        return 'Useless ShapeEditorManager'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('shapeEditorManager_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('shapeEditorManager_proc(1,1);')


class DeleteUselessTrackInfoManager(Action):
    def cnLabel(self):
        return 'Useless TrackInfoManager'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('trackInfoManager_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('trackInfoManager_proc(1,1);')


class DeleteUselessCameraView(Action):
    def cnLabel(self):
        return 'Useless CameraView'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('cameraView_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('cameraView_proc(1,1);')


class DeleteUselessBlindDataTemplate(Action):
    def cnLabel(self):
        return 'Useless BlindDataTemplate'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('blindDataTemplate_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('blindDataTemplate_proc(1,1);')


class DeleteUselessConstraint(Action):
    def cnLabel(self):
        return 'Useless Constraint'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('Constraint_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('Constraint_proc(1,1);')


class DeleteUselessObjectSet(Action):
    def cnLabel(self):
        return 'Useless ObjectSet'

    def run(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('objectSet_proc(0,1);')
        return result

    def fix(self):
        pm.mel.eval('source syf_Clear_Node_Tool.mel;')
        result = pm.mel.eval('objectSet_proc(1,1);')


class CheckAudioFrms(Action):

    def cnLabel(self):
        return u"检查动画帧数与音频帧数"

    def run(self):
        audio = cmds.ls(typ="audio")
        if audio:
            audio = audio[0]
            audio_frm = cmds.getAttr("%s.sourceEnd" % audio)
            ani_start_frm = cmds.playbackOptions(ast=True, q=True)
            ani_end_frm = cmds.playbackOptions(aet=True, q=True)
            ani_frm = ani_end_frm - ani_start_frm + 1
            if ani_end_frm != ani_start_frm + audio_frm - 1:
                cmds.confirmDialog(title='tip', icon="warning",
                                   message=u'<font size="6"><b>动画帧数与音频的帧数不对，请找Jane或者制片.<\font><br><b>')
                return u"error"


class CheckObjUVs(Action):
    char_texture_abc_path = r"Z:\LongGong\assets\char\{asset}\surface\approved\{asset}_tex_highTex.abc".replace("\\",
                                                                                                                "/")
    prop_texture_abc_path = r"Z:\LongGong\assets\prop\{asset}\surface\approved\{asset}_tex_highTex.abc".replace("\\",
                                                                                                                "/")
    reference_tex = []

    def cnLabel(self):
        return u"检查物体的UV是否有误"

    def rfObjGrps(self):
        '''
        Return a list of all groups of the reference nodes.
        [u'charQian_rig_high:charQian_GRP',
         u'propQianPoster_rig_high:propQianPoster_GRP']
        '''
        all_rf_objs = [i for i in cmds.ls(assemblies=True, referencedNodes=True) if "_GRP" in i]
        return all_rf_objs

    def getShapsLs(self, name):
        '''
        Return [u'charQian_rig_high:charQian_GRP', 'charQian_rig_high1:charQian_GRP'] if name
        is 'charQian_rig_high'.
        '''
        allReferenceMesh = cmds.ls(type="mesh", referencedNodes=True, dag=True)
        allRefObj = [cmds.listRelatives(m, p=True, fullPath=True)[0] for m in allReferenceMesh if
                     not cmds.getAttr("%s.intermediateObject" % m)]
        return [i for i in allRefObj if name in i]

    def checkWrongUVs(self, src, tgt):
        '''
        Return 1 or -1 if tgt is different from src, otherwise return 0.
        '''
        a = pm.PyNode(src).getUVs()
        b = pm.PyNode(tgt).getUVs()
        result = cmp(a, b)
        return result

    @staticmethod
    def transferUV(src_transform, tgt_transform):
        '''
        Transfer the UV of src_transform to tgt_transform.
        '''
        cmds.setAttr("%s.intermediateObject" % tgt_transform, 0)
        temp = cmds.polyTransfer(tgt_transform, uv=1, ch=0, ao=src_transform)
        cmds.delete(tgt_transform, constructionHistory=True)
        if isinstance(temp, list):
            return False
        else:
            return True

    def getAllRfFiles(self):
        rf_ls = []
        for rf_node in cmds.ls(rf=1):
            try:
                path1 = cmds.referenceQuery(rf_node, filename=True)
                rf_ls.append(path1)
            except:
                pass
        return rf_ls

    def analizeDic(self):
        '''
        Get a dictionary of all worng shape name.
        {
            u'charQian_rig_high:charQian_GRP': (u'|charQian_tex_highTex1:m_skin_GEO', u'|charQian_rig_high:m_skin_GEO')
        }
        '''
        wrong_obj = {}

        for i in self.rfObjGrps():
            asset_namespace = i.split(":")[0]
            asset = i.split("_")[0]
            wrong_obj[i] = []
            if "char" in asset:
                src_abc = self.char_texture_abc_path.format(asset=asset)
            else:
                src_abc = self.prop_texture_abc_path.format(asset=asset)
            if os.path.exists(src_abc):
                filename = os.path.basename(src_abc)
                ns = os.path.splitext(filename)[0]
                if src_abc not in self.getAllRfFiles():
                    refPath = cmds.file(src_abc, reference=True, ignoreVersion=True,
                                        groupLocator=True, mergeNamespacesOnClash=False,
                                        options="v=0;", namespace=ns, type="Alembic")
                else:
                    refPath = src_abc
                self.reference_tex.append(refPath)  # add the reference node to a list
                tex_namespace = cmds.referenceQuery(refPath, namespace=True).lstrip(':')
                asset_shape_ls = self.getShapsLs(i)
                for shape in asset_shape_ls:
                    tex_obj = shape.replace("|%s" % asset_namespace, "|%s" % tex_namespace)
                    if cmds.objExists(tex_obj):
                        transmit = tex_obj
                        receive = shape
                        try:
                            if self.checkWrongUVs(transmit, receive) != 0:
                                wrong_obj[i].append((transmit, receive))
                        except:
                            pass

        return wrong_obj

    @staticmethod
    def removeRf(refPath):
        try:
            cmds.file(refPath, removeReference=True)
        except:
            pass

    def run(self):
        data = self.analizeDic()
        if data:
            mes = ""
            for i in data.keys():
                if data[i]:
                    mes += i + "\n"
            return mes

    def fix(self):
        result = []
        reply = cmds.confirmDialog(title='tip', message=u"需要传递UV吗", button=['Yes', 'No'], defaultButton='Yes',
                                   cancelButton='No', dismissString='No')
        if reply == "Yes":
            data = self.analizeDic()
            for key, value in data.iteritems():
                if value:
                    for transform in value:
                        temp = self.transferUV(transform[0], transform[1])
                        # append the obj if transfer UV failed
                        if not temp:
                            result.append(transform[1])

        if not result:
            reference_tex = list(set(self.reference_tex))
            for tex in reference_tex:
                self.removeRf(tex)
            return True
        else:
            mes = u"以下模型无法传递UV，请检查："
            for i in data.keys():
                if data[i]:
                    mes += "\n" + i
            # cmds.confirmDialog(title='tip', message=mes, button='OK')
            reference_tex = list(set(self.reference_tex))
            for tex in reference_tex:
                self.removeRf(tex)
            return mes
