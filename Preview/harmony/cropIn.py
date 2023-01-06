import sys
import os
import time

def cropIn(project=None, shot=None, input_path=None,output_path=None,width=1280, height=720,sound_path="",sound=False):
    _path = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
    sys.path.append(_path)
    from getConfig import getConfigClass
    CC = getConfigClass(project_name=project)
    from Preview.anim import createPreview_2D
    playblastPath = CC.get_shot_anim_preview_file(*shot.split('_'))
    folder = os.path.dirname(playblastPath)
    if not os.path.exists(folder):
        os.mkdir(folder)
    _cmd = createPreview_2D(shot, inputPath=input_path, outputPath=output_path, crop=True, cropWidth=int(width), cropHeight=int(height),
                            title=False, frameCount=False, timecode=False, date=False,build_slate=False,audioPath=sound_path,useAudioFile=sound)
    
    #os.remove(tempPath)
    #os.rename(tempPath, path)
    os.startfile(playblastPath)

if __name__ == '__main__':
    if sys.argv:
        cropIn(*sys.argv[1:])
        #         project=sys.argv[1],
        #         shot=sys.argv[2],
        #         path=sys.argv[3],
        #         width=sys.argv[4],
        #         height=sys.argv[5]
        # )