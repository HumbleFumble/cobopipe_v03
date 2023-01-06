from getConfig import getConfigClass
CC = getConfigClass()

from Log.CoboLoggers import getLogger
logger = getLogger()

import os
import shutil


def createPreview(shot, inputPath='', outputPath='', title=True, frameCount=True, timecode=False, date=True, runCmd=True):
    import Preview.ffmpeg_util as preview_util
    import ffmpeg
    if title == True:
        title = shot

    if not inputPath:
        inputPath = CC.get_shot_anim_preview_file(*shot.split('_'))

    if not outputPath:
        outputPath = "%s_Temp.mov" % inputPath.split(".")[0]

    stream = ffmpeg.input(inputPath).video
    audio_check = preview_util.needAudioCheck(inputPath)
    if audio_check:
        audio = preview_util.readySoundStream(inputPath, inputPath)
    else:
        audio = ffmpeg.input(inputPath).audio
    stream = preview_util.createSlate(stream, title=title, frameCount=frameCount, timecode=timecode, date=date)


    if audio_check:
        stream = ffmpeg.output(audio, stream, outputPath, pix_fmt='yuv420p',  acodec = 'pcm_s16le')
    else:
        stream = ffmpeg.output(audio,stream, outputPath, pix_fmt='yuv420p', acodec='copy')
    # audio = ffmpeg.output(audio, output)
    # stream = ffmpeg.merge_outputs(stream, audio)

    _string = ' '.join(ffmpeg.compile(stream, cmd='T:/_Executables/ffmpeg/bin/ffmpeg.exe', overwrite_output=True))

    if runCmd:
        try:
            print('::::>> RUNNING:   ' + _string)
            ffmpeg.run(stream, cmd='T:/_Executables/ffmpeg/bin/ffmpeg.exe', overwrite_output=True)
            logger.info("Created preview with FFMPEG-Python for %s" % shot)
            #os.startfile(previewFile)
        except Exception as e:
            print(e)

    return _string


def createPreview_2D(shot, inputPath='', outputPath='', audioPath='', crop=False, cropWidth=1920, cropHeight=1080, title=True, frameCount=True, timecode=False, date=True, useAudioFile=False, runCmd=True,build_slate=True,user=None):
    import Preview.ffmpeg_util as preview_util
    import ffmpeg
    logger.info("crop: %s - slate: %s" %(crop,build_slate))
    if title == True:
        title = shot
    if user == True:
        user = "Unknown"
    if not inputPath:
        inputPath = CC.get_shot_anim_preview_file(*shot.split('_'))

    if not outputPath:
        outputPath = "%s_Temp.mov" % inputPath.split(".")[0]

    stream = ffmpeg.input(inputPath).video
        
    if useAudioFile:
        if not audioPath:
            audioPath = CC.get_shot_sound_file(*shot.split('_'))
            logger.info("using this audio file: %s" % audioPath)
        #audio = preview_util.readySoundStream(inputPath, audioPath)
        # audio_check = preview_util.needAudioCheck(audioPath)
        if os.path.exists(audioPath):
            audio = ffmpeg.input(audioPath).audio
            audio_check = preview_util.needAudioCheck(video_path=inputPath,audio_path=audioPath)
            if audio_check:
                if audio_check < 0:
                    dur = preview_util.probeDuration(inputPath, codec_type="video")
                    # audio = ffmpeg.trim(audio,duration=dur)
                    audio = audio.filter("atrim",duration=dur)
        else:
            logger.warning("Cannot find audio file, continues without using audio file. <" + audioPath + ">")
            useAudioFile = False
            
    if not useAudioFile:
        audio_check = preview_util.needAudioCheck(inputPath)
        if audio_check:
            audio = preview_util.readySoundStream(inputPath, inputPath)
        else:
            audio = ffmpeg.input(inputPath).audio
    if crop:
        stream = preview_util.CropIn(inputPath, stream, width=cropWidth, height=cropHeight)

    if build_slate:
        logger.info("Using slate!")
        stream = preview_util.createSlate(stream, title=title, frameCount=frameCount, timecode=timecode, date=date,user=user)
    else:
        logger.info("NOT BUILDING SLATE")


    # stream = ffmpeg.output(audio,stream, outputPath, acodec='copy', pix_fmt='yuv420p')
    audio = audio.filter('asetpts', expr='PTS-STARTPTS')
    stream = ffmpeg.output(audio, stream, outputPath, acodec='pcm_s16le', pix_fmt='yuv420p')
    ffmpeg_exe = 'T:/_Executables/ffmpeg/bin/ffmpeg.exe'
    if not os.path.exists(ffmpeg_exe):
        ffmpeg_exe = "ffmpeg"
    _string = ' '.join(ffmpeg.compile(stream, cmd=ffmpeg_exe, overwrite_output=True))
    logger.info(_string)
    if runCmd:
        try:
            print('::::>> RUNNING:   ' + _string)
            logger.info(_string)
            ffmpeg.run(stream, cmd=ffmpeg_exe, overwrite_output=True)
            #ffmpeg.run_async(stream, cmd='T:/_Executables/ffmpeg/bin/ffmpeg.exe', overwrite_output=True)
            #os.startfile(previewFile)
        except Exception as e:
            print(e)

    return _string


if __name__ == '__main__':
    # if os.path.exists(r'\\dumpap2\projekter\_WFH_Projekter\930486_MiaMagicPlayground_S3-4\4_Production\Film\E02\E02_SQ010\_Preview\E02_SQ010_SH020.mov'):
    #     os.remove(r'\\dumpap2\projekter\_WFH_Projekter\930486_MiaMagicPlayground_S3-4\4_Production\Film\E02\E02_SQ010\_Preview\E02_SQ010_SH020.mov')
    # shutil.copyfile(r'P:\_WFH_Projekter\930486_MiaMagicPlayground_S3-4\4_Production\Film\E02\E02_SQ010\_Preview\E02_SQ010_SH020_animPreview.mov', r'\\dumpap2\projekter\_WFH_Projekter\930486_MiaMagicPlayground_S3-4\4_Production\Film\E02\E02_SQ010\_Preview\E02_SQ010_SH020.mov')
    # cmd = createPreview_2D('E02_SQ010_SH020', title=True, frameCount=True, timecode=False, date=True, useAudioFile=True, runCmd=False)
    # print(cmd)
    video_a = "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E02/E02_SQ010/_Preview/E02_SQ010_SH010.mov"
    out = "P:/930499_Borste_02/Production/Film/S205/S205_SQ010/_Preview/S205_SQ010_SH070_Test.mov"
    print(createPreview_2D(shot="E02_SQ010_SH010",inputPath=video_a,outputPath=out,title=True,frameCount = True, timecode = False, date = True,crop=True,cropWidth=1280,cropHeight=720,useAudioFile=True,runCmd=False))

    # T:/_Executables/ffmpeg/bin/ffmpeg.exe -i P:/930499_Borste_02/Production/Film/S205/S205_SQ010/S205_SQ010_SH070/S205_SQ010_SH070_Sound.wav -i P:/930499_Borste_02/Production/Film/S205/S205_SQ010/_Preview/S205_SQ010_SH070_NoSlate.mov -map 0:a -map 1:v -acodec copy -pix_fmt yuv420p -t 4:04 P:/930499_Borste_02/Production/Film/S205/S205_SQ010/_Preview/S205_SQ010_SH070_Test.mov -y

    # T:/_Executables/ffmpeg/bin/ffmpeg.exe -i P:/930499_Borste_02/Production/Film/S205/S205_SQ010/_Preview/S205_SQ010_SH070_NoSlate.mov -filter_complex [0:v]drawtext=fontcolor=white:fontfile=Arial:fontsize=24:shadowcolor=black:shadowx=2:shadowy=2:text=S205_SQ010_SH070:x=w-(text_w+20):y=20[s0];[s0]drawtext=fontcolor=white:fontfile=Arial:fontsize=24:shadowcolor=black:shadowx=1.5:shadowy=1.5:start_number=1:text=%{eif\\:n\\:d\\:5}:x=w-(text_w+20):y=50[s1];[s1]drawtext=fontcolor=white:fontfile=Arial:fontsize=24:shadowcolor=black:shadowx=2:shadowy=2:text=2022-06-28_13\\:07:x=w-(text_w+20):y=h-(text_h+20)[s2] -map 0:a -map [s2] -acodec copy -pix_fmt yuv420p P:/930499_Borste_02/Production/Film/S205/S205_SQ010/_Preview/S205_SQ010_SH070_Test.mov -y
