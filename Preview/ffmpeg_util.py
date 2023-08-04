# from getConfig import getConfigClass
# CC = getConfigClass()

import ffmpeg
import datetime

import os

remote = True

if os.environ.get("BOM_PIPE_PATH"):
    remote =False


ffmpeg_exe = 'T:/_Executables/ffmpeg/bin/ffmpeg.exe'
if not os.path.exists(ffmpeg_exe) or remote:
    ffmpeg_exe = 'ffmpeg'
    
ffprobe_exe = 'T:/_Executables/ffmpeg/bin/ffprobe.exe'
if not os.path.exists(ffprobe_exe) or remote:
    ffprobe_exe = 'ffprobe'

ffplay_exe = 'T:/_Executables/ffmpeg/bin/ffplay.exe'
if not os.path.exists(ffplay_exe) or remote:
    ffplay_exe = "ffplay"


def CropIn(path, stream, width=1920, height=1080):
    current_width, current_height = probeResolution(path)
    if not  current_width and not current_height:
        return stream

    if not current_width > width or not current_height > height:
        return stream

    x = (current_width - width) / 2
    y = (current_height - height) / 2

    return stream.crop(width=width, height=height, x=int(x), y=int(y))


def probeResolution(path):
    probeInfo = ffmpeg.probe(path, cmd=ffprobe_exe)
    w = None
    h = None
    for s in probeInfo["streams"]:
        if s["codec_type"] == "video":
            w = s["width"]
            h = s["height"]
    return w, h


def AddSoundToVideo(video_path, audio_path,output):
    final_a_stream = readySoundStream(video_path,audio_path)
    v_stream = ffmpeg.input(video_path) #Might need: rec709 = 'bt709' / (color_range='tv', colorspace=rec709, color_primaries=rec709, color_trc=rec709)
    v_stream = v_stream.video
    out = ffmpeg.output(final_a_stream, v_stream, output, vcodec='copy', acodec='aac') # Copying video stream, but reencoding the .wav file to work with Prores properly.
    print(generateCmd(out))
    out = ffmpeg.overwrite_output(out)
    out.run(cmd=ffmpeg_exe)


def readySoundStream(video_path,audio_path):
    if video_path == audio_path:
        v_duration, a_duration = probeDurationMerged(video_path)
    elif not audio_path:
        v_duration = probeDuration(video_path)
        a_duration = None
    else:
        v_duration = probeDuration(video_path)
        a_duration = probeDuration(audio_path)

    if v_duration and a_duration:
        silence_length = float(v_duration) - float(a_duration)
    else:
        silence_length = 0

    if silence_length > 0:
        final_a_stream = ProlongAudio(audio_path,silence_length)
    elif silence_length < 0:
        final_a_stream = ffmpeg.input(audio_path)
        final_a_stream = final_a_stream.filter("atrim", duration=v_duration)
        final_a_stream = final_a_stream.filter('asetpts', expr='PTS-STARTPTS')
        # final_a_stream = ffmpeg.trim(final_a_stream,duration=v_duration)
    elif not audio_path and silence_length==0:
        final_a_stream = ProlongAudio(audio_path,v_duration)
    else:
        final_a_stream = ffmpeg.input(audio_path)
    return final_a_stream


def ProlongAudio(audio_path, duration):
    silence = createSilenceStream(duration)
    if audio_path:
        a_stream = ffmpeg.input(audio_path)
        final_a_stream = ffmpeg.concat(a_stream,silence,n=2,v=0,a=1)
    else:
        final_a_stream = silence
    return final_a_stream


def createSilenceStream(duration):
    return ffmpeg.input("anullsrc=channel_layout=stereo:sample_rate=48000:d=%s" % duration, f="lavfi")
    # return ffmpeg.input("anullsrc=channel_layout=stereo:sample_rate=48000:d=%s" % duration, f="lavfi")


def concat(input_path_list,output_path,w=1920,h=1080, force_h264=False):
    # Trim if audio is too long, add silence if its too short?
    # use -shortest? or probe for length?
    list_v = []
    list_a = []
    for i in input_path_list:
        stream_in = ffmpeg.input(i)
        stream_in_v = stream_in.video
        stream_in_a = stream_in.audio
        stream_in_v = ffmpeg.filter(stream_in_v,"scale",w=w,h=h)
        list_v.append(stream_in_v)
        list_a.append(stream_in_a)

    concat_video = ffmpeg.concat(*list_v,n=len(list_v),v=1)
    concat_audio = ffmpeg.concat(*list_a, n=len(list_a), v=0,a=1)

    if force_h264:
        output = ffmpeg.output(concat_video, concat_audio, output_path, pix_fmt='yuv420p', vcodec='libx264')
    else:
        output = ffmpeg.output(concat_video, concat_audio, output_path)
    output = ffmpeg.overwrite_output(output)
    print('>>>>>>>>>> LOOK HERE')
    _string = ' '.join(ffmpeg.compile(output, cmd=ffmpeg_exe, overwrite_output=True))
    print(_string)
    print('>>>>>>>>>>>>')
    output.run(cmd=ffmpeg_exe)
    # print(" ".join(output.compile()))


def createSlate(video, title=None, frameCount=True, timecode=False, date=True,user=None):
    font = 'C:\\/Windows/Fonts/Arial.ttf'
    
    if title:
        video = ffmpeg.drawtext(video, text=title, fontfile=font, x='w-(text_w+20)', y='20', fontsize='24', fontcolor='white', shadowcolor='black', shadowx=2, shadowy=2)
    if user:
        video = ffmpeg.drawtext(video, text='Made by: %s' % user, fontfile=font, x='20', y='20', fontsize='24',
                                fontcolor='white', shadowcolor='black', shadowx=2, shadowy=2)
    if frameCount:
        video = ffmpeg.drawtext(video, '%{eif:n:d:5}', start_number=1,fontfile=font, x='w-(text_w+20)', y='50', fontsize='24', fontcolor='white', escape_text=False, shadowcolor='black', shadowx=1.5, shadowy=1.5)
    if timecode:
        video = ffmpeg.drawtext(video, timecode='00:00:00:00', timecode_rate=25, start_number=0, fontfile=font, x='20', y='h-(text_h+20)', fontsize='24', fontcolor='white', shadowcolor='black', shadowx=2, shadowy=2)
    if date:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
        video = ffmpeg.drawtext(video, text=timestamp, fontfile=font, x='w-(text_w+20)', y='h-(text_h+20)', fontsize='24', fontcolor='white', shadowcolor='black', shadowx=2, shadowy=2)
    return video


def generateCmd(stream):
    _string = ' '.join(ffmpeg.compile(stream, cmd=ffprobe_exe, overwrite_output=True))
    return _string


def createEmpty(duration):
    empty = ffmpeg.input("nullsrc=s=1920x1080:d=%s" % duration,f="lavfi")
    out_stream = createSlate(empty,"TEST")
    # output = ffmpeg.output(out_stream,path,pix_fmt='yuv420p')
    return out_stream


def probeDurationMerged(path):
    """
    Checks the length of video and audio in the same input path
    :param path:
    :return:
    """

    probe_streams = ffmpeg.probe(path, cmd=ffprobe_exe)
    # test = ffmpeg.probe(path,loglevel="error",format="duration",of=True,p=0) # cmd = "ffprobe -loglevel error -show_entries format=duration -of csv=p=0 " + path
    # print("what")
    video_duration = None
    audio_duration = None
    for s in probe_streams["streams"]:
        if s["codec_type"] == "video":
            video_duration = s["duration"]
        if s["codec_type"] == "audio":
            audio_duration = s["duration"]
    return video_duration,audio_duration


def probeDuration(path,index=0,codec_type=None):
    """
    Checks the duration of the index in the given input path
    :param path:
    :return:
    """
    probe_streams = ffmpeg.probe(path, cmd=ffprobe_exe)

    to_return = probe_streams["streams"][index]["duration"]
    if codec_type:
        for i in probe_streams["streams"]:
            if i["codec_type"] == codec_type:
                to_return = i["duration"]
                break
    return to_return



def probeStreams(path):
    """
    Print out the stream info
    :param path:
    :return:
    """
    probe = ffmpeg.probe(path, cmd=ffprobe_exe)
    for p in probe["streams"]:
        print(p)


def needAudioCheck(video_path=None,audio_path=None):
    if not audio_path:
        video, audio = probeDurationMerged(video_path)
    else:
        video = probeDuration(video_path, codec_type="video")
        audio = probeDuration(audio_path, codec_type="audio")
    print("Video: %s - Audio: %s for %s" %(video,audio,video_path))
    if not audio:
        return True
    if video:
        if not float(video) == float(audio):
            return float(video)-float(audio)
    return False


def createMultiStreamOverlay(patha,pathb,output_path):
    """
    intended for creating multiple video tracks in output. DOESN'T F WORK
    :param patha:
    :param pathb:
    :param output_path:
    :return:
    """
    stream_input = ffmpeg.input(patha)
    v_stream = stream_input.video
    overlay_stream_input = ffmpeg.input(pathb)
    v_overlay_stream = overlay_stream_input.video
    # slate = createSlate(v_overlay_stream,"TEST")
    slate = createEmpty(v_overlay_stream,72)

    output_v = ffmpeg.output(slate,v_stream,output_path)
    output_v = ffmpeg.overwrite_output(output_v)
    # output_slate = ffmpeg.output(v_stream,output)
    # print(output_v.get_args())

    # output_compile = output.compile()

    _string = ' '.join(ffmpeg.compile(output_v, cmd='T:/_Executables/ffmpeg/bin/ffmpeg.exe', overwrite_output=True))
    print(_string)
    output_v.run(cmd=ffmpeg_exe)
    print(_string)

if __name__ == '__main__':
    video_a = "C:/Users/chris/Documents/ToonboomLocal/_Preview/S104_SQ070_SH060.mov"
    video_a_new = "C:/Users/chris/Documents/ToonboomLocal/_Preview/S104_SQ070_SH060_user.mov"
    stream = ffmpeg.input(video_a)
    stream = createSlate(stream,user="TEST",frameCount=False,timecode=False,date=False)
    stream = ffmpeg.output(stream, video_a_new, pix_fmt='yuv420p', acodec='copy')
    ffmpeg.run(stream, cmd=ffmpeg_exe, overwrite_output=True)

    # video_test = "P:/930499_Borste_02/Production/Film/S205/S205_SQ010/_Preview/S205_SQ010_SH070_Test.mov"
    # sound_a = "P:/930499_Borste_02/Production/Film/S205/S205_SQ010/S205_SQ010_SH070/S205_SQ010_SH070_Sound.wav"
    #
    # print(probeDurationMerged(video_a))
    #
    # print(needAudioCheck(video_path=video_a,audio_path=sound_a))
    # print(probeDuration(video_a,codec_type="video"))
    # print(probeDuration(sound_a,codec_type="audio"))
    # video_a = "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E10/E10_SQ020/_Preview/E10_SQ020_SH020.mov"
    # video_b = "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E10/E10_SQ020/_Preview/E10_SQ020_SH030.mov"
    # video_c = "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E06/E06_SQ080/_Preview/E06_SQ080_SH020.mov"
    # output_path = video_c
    # audio_check = needAudioCheck(output_path)
    #
    # if audio_check == True:
    #     print("Everything is fine")
    # elif audio_check:
    #     temp_path = makeTempFile(output_path)
    #     AddSoundToVideo(temp_path, temp_path, output_path)
    #     os.remove(temp_path)
    # if not audio_check:
    #     sound_wav = "%s/%s_Sound.wav" % (node.getName(), CC.get_shot_path(**node.getInfoDict()))
    #     AddSoundToVideo(output_path, sound_wav, output_path)

    # video,audio = probeDurationMerged(video_c)
    # print(video,audio)
    # overlay_output = "C:/Temp/FFMPEG_TEST/OverlayTest.mov"
    # createMultiStreamOverlay(video_a,video_b,overlay_output)


    # stream = createEmpty(1)
    # stream = createSlate(stream,"TEST",True,False,True)
    # ffmpeg.output(stream,"C:/Temp/FFMPEG_TEST/OverlayTest_Date.mov").run()

    # print(cur.hour)
    # probeStreams(overlay_output)
    # v = ffmpeg.input(overlay_output)
    # v= v["0"]
    # print(v)
    # t = ffmpeg.output(v,"C:/Temp/FFMPEG_TEST/OverlayTest_Date.mov")
    # t.run()


    # audio_a = "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E10/E10_SQ020/E10_SQ020_SH020/E10_SQ020_SH020_Sound.wav"
    # output_a = "C:/Temp/FFMPEG_TEST/E10_SQ020_SH020_FFMPEG_Test.mov"
    # AddSoundToPreview(video_a,audio_a,output_a)
    # # output_b_v_du, output_b_a_du =
    # # print(probeDurationMerged(output_a))
    #
    # video_b = "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E10/E10_SQ020/_Preview/E10_SQ020_SH030_Comp.mov"
    # audio_b = "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E10/E10_SQ020/E10_SQ020_SH030/E10_SQ020_SH030_Sound.wav"
    # output_b = "C:/Temp/FFMPEG_TEST/E10_SQ020_SH030_FFMPEG_Test.mov"
    # AddSoundToPreview(video_b,audio_b,output_b)
    # # output_b_v_du, output_b_a_du =
    # print(probeDurationMerged(output_b))



    # concant_output = "C:/Temp/FFMPEG_TEST/anim_comp_E10_SQ020_SH020-SH030.mov"
    # concat_hookup([output_a, output_b], concant_output)
# T:/_Executables/ffmpeg/bin/ffmpeg.exe -i P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E10/E10_SQ020/_Preview/E10_SQ020_SH020.mov -i P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E10/E10_SQ020/_Preview/E10_SQ020_SH020.mov -filter_complex [0:v]drawtext=fontcolor=white:fontfile=Arial:fontsize=24:shadowcolor=black:shadowx=2:shadowy=2:text=TEST:x=w-(text_w+20):y=20[s0] -map 1:v -map [s0] C:/Temp/FFMPEG_TEST/OverlayTest.mov -y

# T:/_Executables/ffmpeg/bin/ffmpeg.exe -i P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E10/E10_SQ020/_Preview/E10_SQ020_SH030.mov -filter_complex [0:v]drawtext=fontcolor=white:fontfile=Arial:fontsize=24:shadowcolor=black:shadowx=2:shadowy=2:text=TEST:x=w-(text_w+20):y=20[s0] -map [s0] -map 0:v -map [0] -map [1] C:/Temp/FFMPEG_TEST/OverlayTest.mov -y
# T:/_Executables/ffmpeg/bin/ffmpeg.exe -i P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E06/E06_SQ080/_Preview/E06_SQ080_SH020_ffmpeg_Temp.mov -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=48000:d=0.7999999999999998 -filter_complex [0][1]concat=a=1:n=2:v=0[s0] -map [s0:a] -map 0:v P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E06/E06_SQ080/_Preview/E06_SQ080_SH020.mov -y


