import Preview.file_util
try:
    from getConfig import getConfigClass
    CC = getConfigClass()
    noCC = False
except:
    noCC = True

from Log.CoboLoggers import getLogger
logger = getLogger()

import Preview.anim as anim
import Preview.comp as comp
import RoyalRender.submit
import os


def getPreview(shot, type='comp', create=True, force=False, local=True, inputPath='', outputPath='', crop=False, width=1920, height=1080, user=None,
               waitForJobID=None,audio_path="",useAudioFile=True):
    if create:
        outdated = True
        if not force:
            if type:
                if type == 'anim':
                    os.path.exists(CC.get_shot_anim_preview_file(*shot.split('_')))
                    outdated = Preview.file_util.previewOutdatedAnim(shot)
                elif type == 'comp':
                    if os.path.exists(CC.get_shot_comp_preview_file(*shot.split('_'))):
                        outdated = Preview.file_util.previewOutdatedComp(shot)
                elif type == 'comp_2D':
                    if os.path.exists(CC.get_shot_comp_preview_file(*shot.split('_'))):
                        outdated = Preview.file_util.previewOutdatedComp(shot)

        if force or outdated:
            if local:
                    if type == 'anim':
                        anim.createPreview(shot, inputPath=inputPath, outputPath=outputPath,title=True,
                                           frameCount=True, timecode=False, date=True, runCmd=True)
                    elif type == 'anim_2D':
                        anim.createPreview_2D(shot, inputPath=inputPath, outputPath=outputPath,title=True,
                                           frameCount=True, timecode=False, date=True, useAudioFile=useAudioFile,
                                           crop=crop, cropWidth=width, cropHeight=height, runCmd=True,audioPath=audio_path,user=user)
                    elif type == 'comp':
                        comp.createPreview(shot, inputPath=inputPath, outputPath=outputPath, title=shot, frameCount=True,
                                           timecode=False, date=True, runCmd=True)
                    elif type == 'comp_2D':
                        comp.createPreview_2D(shot, inputPath=inputPath, outputPath=outputPath, title=shot, frameCount=True,
                                              timecode=False, date=True, runCmd=True)
            else:
                if type:
                    if type == 'anim':
                        pass # No code for processing animation playblasts on RR yet
                    elif type == 'comp':
                        batchScript = comp.createBatchScript(shot, inputPath=inputPath, outputPath=outputPath, title=shot,
                                                             frameCount=True, timecode=False, date=True)
                        RoyalRender.submit.batchScriptSubmit(batchScript, sendToAll=False, project_name="MiasMagic2_Fusion",
                                                             client_pool="CompNodes", user_name=user, episode=shot[:3],
                                                             sequence=shot[4:9], shot=shot[10:], waitForJobID=waitForJobID)
                    elif type == 'comp_2D':
                        batchScript = comp.createBatchScript_2D(shot, inputPath=inputPath, outputPath=outputPath, title=shot,
                                                                frameCount=True, timecode=False, date=True)
                        RoyalRender.submit.batchScriptSubmit(batchScript, sendToAll=False, project_name="MiasMagic2_Fusion",
                                                             client_pool="CompNodes", user_name=user, episode=shot[:3],
                                                             sequence=shot[4:9], shot=shot[10:], waitForJobID=waitForJobID)

    if type:
        if type == 'anim':
            return CC.get_shot_anim_preview_file(*shot.split('_'))
        if type == 'comp':
            return CC.get_shot_comp_preview_file(*shot.split('_'))