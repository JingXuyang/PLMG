
def run(path=''):
    import HudWatermark
    reload(HudWatermark)
    
    hudmk = HudWatermark.HudWatermark(path=path)

    # set camera attr
    hudmk.setCameraAttr()

    # playblast
    hudmk.playblast()

    # add hud watermark
    hudmk.addHudWatermark()

    # composite mov and output
    hudmk.outputMov()
