from getConfig import getConfigClass
CC = getConfigClass()

from Log.CoboLoggers import getLogger
logger = getLogger()

from subprocess import Popen, PIPE
import os
import RoyalRender.submit as submit
import Preview.general


def createPreview(shot, inputPath='', outputPath='', title=None, frameCount=True, timecode=False, date=True, runCmd=True):
    import Preview.ffmpeg_util as preview_util
    import ffmpeg
    '''
    Converts a EXR stack in linear colorspace to a H.264 Quicktime (.mov) file in rec709 colorspace

    :param shot: Shot name as string (example: 'E05_SQ030_SH020')
    :param title: Title as string
    :param frameCount: Add framecount boolean
    :param timecode: Add timecode boolean
    :return:
    '''
    if title == True:
        title=shot
        
    if outputPath:
        compOut = outputPath
    else:
        compOut = CC.get_shot_comp_output_folder(*shot.split('_'))  # Getting the comp output folder path
        
    stackExists = False
    if os.path.exists(compOut):
        for file in os.listdir(compOut):
            if file.endswith('.exr'):
                stackExists = True
                break

    if inputPath:
        stackPath = inputPath
    else:
        stackPath = os.path.join(compOut, shot + '_%04d.exr')  # Joining comp output folder path with file name
        stackPath = os.path.abspath(stackPath).replace(os.sep, '/')  # Creating absolute path without backwards slashes
    

    sound_file = "%s/%s_Sound.wav" % (CC.get_shot_path(*shot.split("_")),shot)


    previewFile = CC.get_shot_comp_preview_file(*shot.split('_')) # Getting the preview file path
    previewFile = os.path.abspath(previewFile).replace(os.sep, '/') # Creating absolute path without backwards slashes

    if os.path.exists(previewFile):
        os.remove(previewFile)

    rec709 = 'bt709'
    gammaValue = 'gammaval(0.416666667)'
    stream = ffmpeg.input(stackPath, color_range='tv', colorspace=rec709, color_primaries=rec709, color_trc=rec709)
    stream = stream.video
    stream = ffmpeg.filter(stream, 'lutrgb', r=gammaValue, g=gammaValue, b=gammaValue)
    stream = preview_util.createSlate(stream,title=title,frameCount=frameCount,timecode=timecode)
    #audio_stream = preview_util.readySoundStream(stackPath,sound_file)
    stream = ffmpeg.output(stream, previewFile, pix_fmt='yuv420p', acodec='copy', color_range='tv', colorspace=rec709, color_primaries=rec709, color_trc=rec709) #audio_stream
    # stream.global_args("-preset","slower")
    # stream.global_args("-crf", "18")

    if runCmd:
        if stackExists:
            try:
                ffmpeg.run(stream, overwrite_output=True, cmd='T:/_Executables/ffmpeg/bin/ffmpeg.exe')
                #os.startfile(previewFile)
            except Exception as e:
                print(e)
        else:
            print('>> ERROR: NO EXR STACK')
    
        # else:
    #     cmd = """T:/_Executables/ffmpeg/bin/ffmpeg.exe -color_primaries bt709 -color_range tv -color_trc bt709 -colorspace bt709 -i <stackPath> -filter_complex [0]lutrgb=b=gammaval(0.416666667):g=gammaval(0.416666667):r=gammaval(0.416666667)[s0];[s0]drawtext=fontcolor=white:fontfile=Arial:fontsize=24:shadowcolor=black:shadowx=2:shadowy=2:text=True:x=w - (text_w + 20):y=20[s1];[s1]drawtext=fontcolor=white:fontfile=Arial:fontsize=24:shadowcolor=black:shadowx=1.5:shadowy=1.5:start_number=1:text=%{frame_num}:x=w - (text_w + 20):y=50[s2] -map [s2] -color_primaries bt709 -color_range tv -color_trc bt709 -colorspace bt709 -pix_fmt yuv420p <previewFile> -y"""
    #     cmd = ffmpegCmd.replace('<stackPath>', stackPath)
    #     cmd = ffmpegCmd.replace('<previewFile>', previewFile)
    
    return ' '.join(ffmpeg.compile(stream, cmd='T:/_Executables/ffmpeg/bin/ffmpeg.exe', overwrite_output=True))


def createPreview_2D(shot, inputPath='', outputPath='', title=None, frameCount=True, timecode=False, date=True, runCmd=True):
    import Preview.ffmpeg_util as preview_util
    import ffmpeg
    '''
    Converts a EXR stack in linear colorspace to a H.264 Quicktime (.mov) file in rec709 colorspace

    :param shot: Shot name as string (example: 'E05_SQ030_SH020')
    :param title: Title as string
    :param frameCount: Add framecount boolean
    :param timecode: Add timecode boolean
    :return:
    '''
    if title == True:
        title=shot
        
    if inputPath:
        compOut = inputPath
    else:
        compOut = CC.get_shot_comp_output_file_mov(*shot.split('_'))  # Getting the comp output file

    if outputPath:
        previewFile = outputPath
    else:
        previewFile = CC.get_shot_comp_preview_file(*shot.split('_'))
    
    sound_file = "%s/%s_Sound.wav" % (CC.get_shot_path(*shot.split("_")),shot)

    if os.path.exists(previewFile):
        os.remove(previewFile)

    rec709 = 'bt709'
    #gammaValue = 'gammaval(0.416666667)'
    stream = ffmpeg.input(compOut)
    stream = stream.video
    #stream = ffmpeg.filter(stream, 'lutrgb', r=gammaValue, g=gammaValue, b=gammaValue)
    stream = preview_util.createSlate(stream,title=title,frameCount=frameCount,timecode=timecode)
    audio_stream = preview_util.readySoundStream(compOut,sound_file)
    stream = ffmpeg.output(stream,audio_stream, previewFile, pix_fmt='yuv420p', acodec='copy')

    if runCmd:
        if os.path.exists(compOut):
            try:
                ffmpeg.run(stream, overwrite_output=True, cmd='T:/_Executables/ffmpeg/bin/ffmpeg.exe')
            except Exception as e:
                print(e)
        else:
            print('>> ERROR: NO MOV FILE')
    
    return ' '.join(ffmpeg.compile(stream, cmd='T:/_Executables/ffmpeg/bin/ffmpeg.exe', overwrite_output=True))


def createBatchScript(shot, inputPath='', outputPath='', title=True, frameCount=True, timecode=False, date=True):
    _string = """@echo off\n\n<command>\n\nEXIT /B 0"""
    ffmpegCmd = createPreview(shot, inputPath=inputPath, outputPath=outputPath, title=title,
                              frameCount=frameCount, timecode=timecode, date=date, runCmd=False)
    _string = _string.replace('<command>', ffmpegCmd)
    _string = _string.replace('%', '%%')
    shotPath = CC.get_shot_path(*shot.split('_'))
    batchPath = os.path.join(shotPath, '04_Publish', shot + '_compPreview.bat')
    batchPath = os.path.abspath(batchPath).replace(os.sep, '/')
    with open(batchPath, 'w') as batchFile:
        batchFile.write(_string)
    return batchPath


def createBatchScript_2D(shot, inputPath='', outputPath='', title=True, frameCount=True, timecode=False, date=True):
    _string = """@echo off\n\n<command>\n\nEXIT /B 0"""
    ffmpegCmd = createPreview_2D(shot, inputPath=inputPath, outputPath=outputPath, title=title,
                              frameCount=frameCount, timecode=timecode, date=date, runCmd=False)
    _string = _string.replace('<command>', ffmpegCmd)
    _string = _string.replace('%', '%%')
    shotPath = CC.get_shot_path(*shot.split('_'))
    batchPath = os.path.join(shotPath, '04_Publish', shot + '_compPreview.bat')
    batchPath = os.path.abspath(batchPath).replace(os.sep, '/')
    with open(batchPath, 'w') as batchFile:
        batchFile.write(_string)
    return batchPath


if __name__ == '__main__':
    # print(CC.get_python3())
    createPreview("E06_SQ080_SH030")