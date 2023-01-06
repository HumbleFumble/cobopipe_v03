import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(__file__, '../../..')))

# sys.path.append(os.path.realpath(__file__)) # This doesn't work, because you're appending the Preview/harmony folder, not the root of the repository.
from getConfig import getConfigClass

from Log.CoboLoggers import getLogger
logger = getLogger()

def createSlate(project=None, shot=None, input_path=None,output_path=None, crop=False, width=1280, height=720,sound_path="",sound=True,user=None):
    
    CC = getConfigClass(project_name=project)
    from Preview.general import getPreview
    from runInPython3 import runInPython3
    # playblastPath = CC.get_shot_anim_preview_file(*shot.split('_'))
    # tempPath = "C:/Temp/temp_previews/" + shot + "_Temp.mov"
    result = runInPython3(getPreview, shot, type="anim_2D", create=True,
                          force=True, local=True, inputPath=input_path, outputPath=output_path, crop=crop, width=int(width), height=int(height), audio_path=sound_path,useAudioFile=sound,user=user)
    logger.info("Ran create slate in python3: %s" % result)

    funcs = [(os.system, "taskkill /im QuickTimePlayer.exe"),
             (os.system, "taskkill /im vlc.exe"),
             (os.startfile, output_path)]
    # (os.remove, tempPath) #commented out to see what goes wrong
    for func, arg in funcs:
        for i in range(25):
            try:
                time.sleep(0.1)
                func(arg)
                break
            except:
                pass

if __name__ == '__main__':
    if sys.argv:
        createSlate(*sys.argv[1:])
        # createSlate(project=sys.argv[1],
        #             shot=sys.argv[2],
        #             input_path=sys.argv[3],
        #             output_path=sys.argv[4],
        #             crop=sys.argv[5],
        #             width=sys.argv[6],
        #             height=sys.argv[7],
        #             sound_path=[8])
