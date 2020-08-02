def PreRender():
    import maya.cmds as mc

    ### To not conflict with the renderSetup layers, the auto-generated old layers start with rs_
    ### Unfortuantely the Maya Common 'File name prefix' <RenderLayer> setting uses the OLD layer system names,
    ### despite rendering from the new layer system. So the layers are all named rs_.  This snippet renames
    ### the renderSetup layers to rl_(layer name) and renames the rs_(layer name) layers to just (layer name).
    ### a corresponding postrender script names them back.
    for Layer in mc.ls(typ="renderSetupLayer"):
        if not Layer.startswith("rl_"):
            try:
                mc.rename(Layer,"rl_"+Layer)
            except:
                pass
    for Layer in mc.ls(typ="renderLayer"):
        if Layer.startswith("rs_"):
            try:
                mc.rename(Layer,Layer[3:])
            except:
                pass