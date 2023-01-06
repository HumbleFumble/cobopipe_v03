import subprocess
import os


class FFMPEG(object):
    def __init__(self, cwd=None):
        self.__cwd = cwd
        self.__env = dict(os.environ, PATH="C:/Program Files/ffmpeg/bin")
        self.__shell = True

    def setCwd(self, cwd):
        self.__cwd = cwd

    def scaleVideo(self, input_name, width):
        img_format = input_name.split(".")[-1]
        output_name = "{0}_w{1}_Scaled.{2}".format(input_name.replace(".mov", ""), width, img_format)
        args = "ffmpeg -i {0} -vf scale={1}:-1 {2}".format(input_name, width, output_name)
        subprocess.run(
            args=args,
            cwd=self.__cwd,
            env=self.__env,
            shell=self.__shell
        )
        return output_name

    def scaleImage(self, input_name=None, output_name=None, width=160, apply_gamma=None):  # TODO Check if it can convert exr to png
        add_gamma = ""
        if apply_gamma:
            add_gamma = "-apply_trc iec61966_2_1"
        args = "ffmpeg {0} -y -i {1} -vf scale={2}:-1 {3}".format(add_gamma, input_name, width, output_name)
        subprocess.Popen(args=args, universal_newlines=True,shell=True)
        # subprocess.run(
        #     args=args,
        #     cwd=self.__cwd,
        #     env=self.__env,
        #     shell=self.__shell
        # )
        return output_name

    def videoToSequence(self, input_name, output_name, output_width, output_format, output_fps):
        args = "ffmpeg -i {0} -vf \"fps={1}, scale={2}:-1\" {3}_%03d.{4}".format(input_name, output_fps, output_width,
                                                                                 output_name, output_format)
        subprocess.run(
            args=args,
            cwd=self.__cwd,
            env=self.__env,
            shell=self.__shell
        )

    def videoToImage(self, input_name, output_name, output_width, time_code):
        args = "ffmpeg -ss {1} -i {0} -y -frames:v 1 -vf \"scale={2}:-1\" {3}".format(input_name, time_code,
                                                                                      output_width, output_name)
        subprocess.Popen(
            args=args,
            cwd=self.__cwd,
            shell=self.__shell
        )
        # subprocess.run(
        #     args=args,
        #     cwd=self.__cwd,
        #     env=self.__env,
        #     shell=self.__shell
        # )

    def prores_convert(self, input_path, output_path):
        args = "ffmpeg -i {0} -c:v prores_ks -profile:v 0 -vf scale=1920x1080 -ar 44100 -ac 1 -acodec mp3 -y {1}".format(input_path, output_path)
        # args = "ffmpeg -i {0} -preset slow -codec:a aac -b:a 128k -codec:v libx264 -pix_fmt yuv420p -b:v 4500k -minrate 4500k -maxrate 9000k -bufsize 9000k -vf scale=-1:1080 -y {1}".format(input_path, output_path)
        # args = "ffmpeg -i {0} -c copy -bsf:v h264_mp4toannexb -f mpegts -y {1}".format(input_path, output_path)
        # ffmpeg -i input1.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts intermediate1.ts
        # ffmpeg -i input2.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts intermediate2.ts
        # ffmpeg -i "concat:intermediate1.ts|intermediate2.ts" -c copy -bsf:a aac_adtstoasc output.mp4
        subprocess.run(args=args)
        # subprocess.run(
        #     args=args,
        #     cwd=self.__cwd,
        #     shell=self.__shell
        # )

    def concat_filter_complex(self, video_paths):
        # Video signature should be str "E01_SQ010_SH010.mov"
        input_paths = ""
        input_settings = ""
        input_amount = len(video_paths)
        output_path = r"SQ_CONCAT.mov"
        for en, video in enumerate(video_paths):
            if os.path.exists(video):
                input_paths += "-i {video} ".format(video=video)
                input_settings += "[{en}:0] [{en}:1] ".format(en=en)
                print("Was vailid: " + video)
            else:
                print("Not a valid path: " + video)
        # Signatures in examples
        # Filenames/paths   = '-i opening.mkv -i episode.mkv -i ending.mkv'
        # Input settings    = '[0:v:0] [0:a:0] [1:v:0] [1:a:0] [2:v:0] [2:a:0]'
        args = 'ffmpeg -y {input_paths}-filter_complex "{input_settings}concat=n={input_amount}:v=1:a=1 [outv] [outa]" -map "[outv]" -map "[outa]" {output_path} '.format(input_paths=input_paths,input_settings=input_settings,input_amount=input_amount,output_path=output_path)
        print(args)
        subprocess.run(
            args=args,
            cwd=self.__cwd,
            shell=self.__shell
        )
        # notFound = True
        # for p_con in preview_content:
        #     if shot in p_con and notFound:
        #         p_con_path = "%s/%s" % (playblast_path, p_con)
        #         convert_to_pro_res = "ffmpeg -i %s -c:v prores_ks -profile:v 0 -ar 44100 -ac 1 -acodec mp3 -y %s" % (p_con_path, "%s/%s_HookUpTemp.mov" % (playblast_path, shot))
        #         notFound = False
        # if notFound:
        #     animatic_path = "%s/%s/%s_Animatic.mov" % (self.sequence_path, shot, shot)
        #     convert_to_pro_res = "ffmpeg -i %s -c:v prores_ks -profile:v 0 -ar 44100 -ac 1 -acodec mp3 -y %s" % (animatic_path, "%s/%s_HookUpTemp.mov" % (playblast_path, shot))
        # hook_up_list.append("%s/%s_HookUpTemp.mov" % (playblast_path, shot))
        # subprocess.call(convert_to_pro_res, shell=False)
        # outFile.write("file '%s_HookUpTemp.mov'\n" % (shot))

    def concat_protocol(self, file=None,output_path=None):
        """NOT WORKING... Adds 1 frame at start of each shot at random"""
        # Video signature should be str "E01_SQ010_SH010.mov"
        # TODO auto creation of mylist.txt
        if not output_path:
            output_path = os.path.split(file)[0] + "/HookupTest.mov"
        args = 'ffmpeg -y -f concat -safe 0 -i {file} -s 1280:720 -c:a copy -c:v prores_ks -profile:v 1 -crf 0 {output_path}'.format(file=file,output_path=output_path)
        # args = f'ffmpeg -y -f concat -i {file} -vcodec copy {output_path}'  # WORKS
        subprocess.run(
            args=args,
            cwd=self.__cwd
        )
        # subprocess.run(
        #     args=args,
        #     cwd=self.__cwd,
        #     shell=self.__shell
        # )
        return output_path

    def getVideoLength(self, video_input):
        result = subprocess.Popen('ffprobe -i %s -show_entries format=duration -v quiet -of csv="p=0"' % video_input,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = result.communicate()
        return float(output[0])

    def viewVideo(self, input):
        args = "ffplay {0}".format(input)
        subprocess.run(
            args=args,
            cwd=self.__cwd,
            env=self.__env,
            shell=self.__shell
        )
    def intermediateConvert(self, input_path,output_path):
        """ NO AUDIO :( """
        args = "ffmpeg -i {0} -c copy -c:a aac -bsf:v h264_mp4toannexb -f mpegts  -shortest -y {1}".format(
            input_path, output_path)
        subprocess.run(args=args)


if __name__ == "__main__":
    # ffmpeg = FFMPEG(cwd=r"P:\930382_KiwiStrit2\Production\Film\E01\E01_SQ010")
    # scaled = ffmpeg.scaleVideo(input_name="Animatic.mov", width=420)
    # # ffmpeg.videoToSequence(input_name="Animatic.mov", output_name="E01_SQ010_SH010", output_width=420, output_format="png", output_fps=1)
    # path01 = "P:/930382_KiwiStrit2/Production/Film/E01/E01_SQ010/E01_SQ010_SH010/E01_SQ010_SH010_Animatic.mov"
    # path02 = "P:/930382_KiwiStrit2/Production/Film/E01/E01_SQ010/E01_SQ010_SH010/E01_SQ010_SH030_Animatic.mov"
    # ffmpeg.concat_protocol([path01, path02])
    ffmpeg = FFMPEG()
    cur_path ="P:/930483_Borste_film/Production/Film/S105/S105_SQ010/_Preview"
    ffmpeg.setCwd(cur_path)
    first_input = "%s/%s" % (cur_path,"S105_SQ010_SH050_animPreview.mov")
    first_output = "%s/%s" % (cur_path,"S105_SQ010_SH050_animPreview_test.mov")
    ffmpeg.prores_convert(first_input, first_output)
    sec_in = "%s/%s" % (cur_path,"S105_SQ010_SH060_animPreview.mov")
    sec_out = "%s/%s" % (cur_path,"S105_SQ010_SH060_animPreview_test.mov")

    ffmpeg.prores_convert(sec_in,sec_out)
    l_in = "%s/%s" % (cur_path, "S105_SQ010_SH070_animPreview.mov")
    l_out = "%s/%s" % (cur_path, "S105_SQ010_SH070_animPreview_test.mov")
    ffmpeg.prores_convert(l_in, l_out)
    # ffmpeg -i "concat:intermediate1.ts|intermediate2.ts" -c copy -bsf:a aac_adtstoasc output.mp4
    # cur_args = "ffmpeg -i \"concat:{0}|{1}\" -c copy -bsf:a aac_adtstoasc -y test_output.mp4".format(
    cur_args="ffmpeg -i \"concat:{0}|{1}|{2}\" -c:a copy -c:v prores_ks -profile:v 1 -crf 0 -r 25 -y test_output.mov".format(
            first_output, sec_out,l_out)
    subprocess.run(args=cur_args,cwd=cur_path)

