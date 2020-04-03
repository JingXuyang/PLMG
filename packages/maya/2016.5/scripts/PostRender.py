def PostRender():
    #### renames the layers back to what they were before rendering, restoring the original renderSetup name and adding rs_ back to the old system render layer names

    import maya.cmds as mc

    for Layer in mc.ls(typ="renderLayer"):
        if not Layer.startswith("rs_"):
            try:
                mc.rename(Layer, "rs_" + Layer)
            except:
                pass
    for Layer in mc.ls(typ="renderSetupLayer"):
        if Layer.startswith("rl_"):
            try:
                mc.rename(Layer,Layer[3:])
            except:
                pass