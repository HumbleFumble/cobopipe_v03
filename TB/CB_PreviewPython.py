import sys
sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" )

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
import ffmpeg



os.environ["BOM_PIPE_PATH"] = os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
if os.environ.get("BOM_PIPE_PATH"):
    import sys
    sys.path.append(os.environ["BOM_PIPE_PATH"])
    from getConfig import getConfigClass
    CC = getConfigClass()




    use_config = True
else:
    use_config = False

class PreviewPython_UI(QDialog):
    def __init__(self, parent=None):
        super(PreviewPython_UI, self).__init__(parent)
        self.setWindowTitle("Preview")
        self.setObjectName("Preview")
        self.setWindowFlags(self.windowFlags()|Qt.Window|Qt.WindowStaysOnTopHint)
        self.node_list = []
        self.create_ui()
        if use_config:
            self.config_info()

        self.show()
    def projectChanged(self):
        self.p_edit.setText(self.p_dd.currentText())
        if use_config:
            CC = getConfigClass(project_name=self.p_dd.currentText())
            if CC.project_settings.get("tb_size_multi"):
                self.crop_check.setChecked(True)
                self.crop_edit.setText(str(CC.project_settings.get("tb_size_multi")))
            else:
                self.crop_check.setChecked(False)


    def userChanged(self):
        self.u_edit.setText(self.u_dd.currentText())
    def config_info(self):
        all_users = []
        for k in CC.users:
            all_users.extend(CC.users[k])
        all_users = sorted(list(set(all_users)))
        project_list = []
        for con in os.listdir(f"{os.environ['BOM_PIPE_PATH']}/Configs"):
            if "Config_" in con and not ".pyc" in con:
                project_list.append(con.split("Config_")[-1].split(".")[0])
        self.p_dd.addItems(project_list)
        self.u_dd.addItems(all_users)
        self.p_dd.setCurrentText(CC.project_name)


    def crop_toggle(self):
        self.crop_edit.setEnabled(self.crop_check.isChecked())

    def create_ui(self):
        self.main_lay = QVBoxLayout()

        self.p_lay = QHBoxLayout()

        self.p_dd = QComboBox()
        self.p_edit = QLineEdit()
        self.p_lay.addWidget(QLabel("Project: "))
        self.p_lay.addWidget(self.p_dd)
        self.p_lay.addWidget(self.p_edit)

        self.u_lay = QHBoxLayout()

        self.u_dd = QComboBox()
        self.u_edit = QLineEdit()
        self.u_lay.addWidget(QLabel("User: "))
        self.u_lay.addWidget(self.u_dd)
        self.u_lay.addWidget(self.u_edit)

        self.blocking_check = QCheckBox("Blocking")
        self.render_check = QCheckBox("Render Quailty")
        self.slate_check = QCheckBox("Slate")

        self.crop_check = QCheckBox("Crop: ")
        self.crop_edit = QLineEdit("1.1")
        self.crop_edit.setFixedWidth(40)

        self.options_lay = QHBoxLayout()
        self.options_lay.addWidget(self.blocking_check)
        self.options_lay.addWidget(self.render_check)
        self.options_lay.addWidget(self.slate_check)
        self.options_lay.addWidget(self.crop_check)
        self.options_lay.addWidget(self.crop_edit)

        self.main_lay.addLayout(self.p_lay)
        self.main_lay.addLayout(self.u_lay)
        self.main_lay.addLayout(self.options_lay)
        self.run_bttn = QPushButton("Create Preview")
        self.main_lay.addWidget(self.run_bttn)
        self.setLayout(self.main_lay)
        self.crop_check.setChecked(True)
        self.slate_check.setChecked(True)
        self.run_bttn.clicked.connect(self.create_preview)
        self.p_dd.currentTextChanged.connect(self.projectChanged)
        self.u_dd.currentTextChanged.connect(self.userChanged)
        self.crop_check.stateChanged.connect(self.crop_toggle)

    def findPassesFolder(self):
        sess = harmony.session()  # Fetch the currently active session of Harmony
        project = sess.project  # The project that is already loaded.
        scene_dir = project.project_path
        passes_dir = "%s/Passes/" % "/".join(scene_dir.split("/")[0:-1])
        if not os.path.exists(passes_dir):
            os.mkdir(passes_dir)
        return passes_dir


    def create_preview(self):

        if use_config:
            pass
        else:
            #gather info like
            pass

    def create_crop_locally(self,stream, width=1920, height=1080,factor=1.1):
        x = ((width*factor) - width) / 2
        y = ((height*factor) - height) / 2
        return ffmpeg.filter(stream, "crop", w=width, h=height, x=str(x), y=str(y))
    def create_slate_locally(self,video, title=None, frameCount=True, timecode=False, date=True,user=None):
        import datetime
        font = '/Windows/Fonts/Arial.ttf'

        if title:
            video = ffmpeg.drawtext(video, text=title, fontfile=font, x='w-(text_w+20)', y='20', fontsize='24',
                                    fontcolor='white', shadowcolor='black', shadowx=2, shadowy=2)
        if user:
            video = ffmpeg.drawtext(video, text='Made by: %s' % user, fontfile=font, x='20', y='20', fontsize='24',
                                    fontcolor='white', shadowcolor='black', shadowx=2, shadowy=2)
        if frameCount:
            video = ffmpeg.drawtext(video, '%{eif:n:d:5}', start_number=1, fontfile=font, x='w-(text_w+20)', y='50',
                                    fontsize='24', fontcolor='white', escape_text=False, shadowcolor='black',
                                    shadowx=1.5, shadowy=1.5)
        if timecode:
            video = ffmpeg.drawtext(video, timecode='00:00:00:00', timecode_rate=25, start_number=0, fontfile=font,
                                    x='20', y='h-(text_h+20)', fontsize='24', fontcolor='white',
                                    shadowcolor='black', shadowx=2, shadowy=2)
        if date:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M")
            video = ffmpeg.drawtext(video, text=timestamp, fontfile=font, x='w-(text_w+20)', y='h-(text_h+20)',
                                    fontsize='24', fontcolor='white', shadowcolor='black', shadowx=2, shadowy=2)
        return video
    def create_preview_locally_func(self,input_path="", output_path="", title=None, slate=True,crop=False,audio=None):
    # def createPreview_2D(shot, inputPath='', output_path='', audioPath='', crop=False, cropWidth=1920, cropHeight=1080, title=True, frameCount=True, timecode=False, date=True, useAudioFile=False, runCmd=True,build_slate=True,user=None):

        stream = ffmpeg.input(input_path).video

        if audio:
            if os.path.exists(audio):
                audio = ffmpeg.input(audio).audio
                audio_check = preview_util.needAudioCheck(video_path=input_path,audio_path=audioPath)
                if audio_check:
                    if audio_check < 0:
                        dur = preview_util.probeDuration(input_path, codec_type="video")
                        audio = audio.filter("atrim",duration=dur)

        if not useAudioFile:
            audio_check = preview_util.needAudioCheck(input_path)
            if audio_check:
                audio = preview_util.readySoundStream(input_path, input_path)
            else:
                audio = ffmpeg.input(input_path).audio
        if crop:
            stream = preview_util.CropIn(input_path, stream, width=cropWidth, height=cropHeight)

        if slate:
            stream = self.create_slate_locally(stream, title=title, frameCount=True, timecode=True, date=True,user=user)

        audio = audio.filter('asetpts', expr='PTS-STARTPTS')
        stream = ffmpeg.output(audio, stream, output_path, acodec='pcm_s16le', pix_fmt='yuv420p')

        _string = ' '.join(ffmpeg.compile(stream, overwrite_output=True))
        try:
            print('::::>> RUNNING:\n' + _string)
            ffmpeg.run(stream, overwrite_output=True)
        except Exception as e:
            print(e)

        return _string

if __name__ == '__main__':
    import sys
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    t = PreviewPython_UI()
    t.show()
    app.exec()