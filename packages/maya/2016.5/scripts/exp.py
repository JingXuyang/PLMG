import plcr
Action = plcr.Action
class ExportAbc1(Action):

    def __init__(self, input1, path1):
        self.input = input1
        self.output = path1

    def run(self):
        import pymel.core as pm
        import maya.cmds as cmds
        import maya.mel as mel
        import time
        self._cmds = cmds
        self._pm = pm
        
        print 8888888888888888888
        sw = self.software()
        objs = self.input
        if sw and objs:
            if type(objs) != list:
                objs = [objs]
            
            #print 'objs1:',objs
            
            path = self.output
            
            makeFolder(path)
            
            frameRange = [self._cmds.currentTime(query=True), self._cmds.currentTime(query=True)]
        
            #print frameRange
            args = '-frameRange %s %s ' % (frameRange[0], frameRange[1])
            options =  ['-uvWrite','-worldSpace','-dataFormat ogawa','-ro']
            if type(options) in (list, tuple):
                options = ' '.join(options)
            
            if options:
                args += options + ' '
            
            for obj in objs:
                args += '-root %s ' % obj
            args += '-file %s' % path
            plugin_list = self._cmds.pluginInfo(query=True, listPlugins=True)
            if 'mtoa' in plugin_list:
                args += ' -attr aiSubdivType -attr aiSubdivIterations'
            if 'AbcExport' not in plugin_list:
                self._cmds.loadPlugin("AbcExport")
            cmd = 'AbcExport -j "%s";' % args
            print cmd
            time_start = time.time()
            mel.eval(cmd)
            time_end = time.time()
            print "OjbK", time_end - time_start
            
            return path