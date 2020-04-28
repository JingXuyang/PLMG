
def run(path='', cam=''):
    import HudWatermark
    reload(HudWatermark)
    
    hudmk = HudWatermark.HudWatermark(path=path, cam=cam)

    # set camera attr
    hudmk.setCameraAttr()

    # playblast
    hudmk.playblast()

    # add hud watermark
    hudmk.addHudWatermark()

    # composite mov and output
    hudmk.outputMov()
