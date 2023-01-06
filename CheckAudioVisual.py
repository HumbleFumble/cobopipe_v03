from os import path
import subprocess


class MediaLengthService:

    def get_length(self, path, fps=25, silent=True):
        cmd = "ffprobe -loglevel error -show_entries format=duration -of csv=p=0 " + path
        value = float(subprocess.check_output(cmd)) * fps
        if not silent:
            print("len=" + str(value) + " : " + path)
        return value

    def compare_equal(self, path01, path02, fps=25, silent=True):
        audio_len = self.get_length(path=path01, fps=fps)
        video_len = self.get_length(path=path02, fps=fps)

        if not audio_len == video_len:
            tail01 = path.split(path01)[1]
            tail02 = path.split(path02)[1]
            msg = "Bad lengths:\n" + tail01 + " - (" + str(video_len) + ")f" + "\n" + tail02 + " - (" + str(audio_len) + ")f"
            raise MediaLengthException(msg, path.split(path01)[0], audio_len, path.split(path02)[0], video_len)
        else:
            tail01 = path.split(path01)[1]
            tail02 = path.split(path02)[1]
            msg = "All is good:\n" + tail01 + " - (" + str(video_len) + ")f" + "\n" + tail02 + " - (" + str(audio_len) + ")f"
            if not silent:
                print(msg)
                print("compare_equal print")
            return 0, msg


class MediaLengthException(BaseException):

    def __init__(self, message, media1_name, media1_duration, media2_name, media2_duration):
        super(MediaLengthException, self).__init__("Media was of uneven lengths: " + media1_name + " [" + str(media1_duration) + "] - " + media2_name + " [" + str(media2_duration) + "]")
        self.msg = message

    def getMsg(self):
        return self.msg


class SrcPath:
    def get(self):
        return __file__.split("AV")[0] + "AV"


class AV:
    def __init__(self):
        self.lengths = MediaLengthService()
