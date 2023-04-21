# import sys
# sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" )

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
import ffmpeg
import json

try:
	from ToonBoom import harmony
	in_toonboom = True
except Exception as e:
	in_toonboom = False
import sys

if os.environ.get("BOM_PIPE_PATH"):
    sys.path.append(os.environ["BOM_PIPE_PATH"])
    from getConfig import getConfigClass
    CC = getConfigClass()
    import Preview.anim as PA
    import Preview.ffmpeg_util as ffmpeg_util
    use_config = True
else:
    sys.path.append(os.path.abspath(os.path.dirname(os.path.realpath(__file__)))) #Same dir as this script
    # sys.path.append(os.environ)
    import ffmpeg_util
    use_config = False

class PreviewPython_UI(QDialog):
    def __init__(self, parent=None):
        super(PreviewPython_UI, self).__init__(parent)
        self.setWindowTitle("Preview")
        self.setObjectName("Preview")
        self.setWindowFlags(self.windowFlags()|Qt.Window|Qt.WindowStaysOnTopHint)
        self.save_location = "C:/Temp/TB/PythonPreview.json"
        self.width = 1280
        self.height = 720

        self.create_ui()

        self.checkAndApplySettings()

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

    def checkAndApplySettings(self):
        if use_config:
            self.config_info()
        load_dict = self.loadJson(self.save_location)
        if load_dict:
            self.slate_check.setChecked(load_dict["slate_check"])
            if self.u_dd.findText(load_dict["user"])>-1:
                self.u_dd.setCurrentText(load_dict["user"])
            self.u_edit.setText(load_dict["user"])
            self.blocking_check.setChecked(load_dict["blocking_check"])
            self.render_check.setChecked(load_dict["render_check"])
        if use_config:
            if os.environ.get("BOM_USER"):
                self.u_edit.setText(os.environ["BOM_USER"])


    def loadJson(self,load_file):
        if os.path.isfile(load_file):
            with open(load_file, 'r') as cur_file:
                return json.load(cur_file)
        else:
            return {}

    def saveJson(self, save_location, save_info):
        with open(save_location, 'w+') as saveFile:
            json.dump(save_info, saveFile)
        saveFile.close()

    def closeEvent(self,event):

        save_dict = {"slate_check":self.slate_check.isChecked(),
                     "user":self.u_edit.text(),
                     "blocking_check":self.blocking_check.isChecked(),
                     "render_check":self.render_check.isChecked()}
        self.saveJson(self.save_location,save_dict)
        super(PreviewPython_UI, self).closeEvent(event)


    def findSceneInfo(self):
        sess = harmony.session()  # Fetch the currently active session of Harmony
        project = sess.project  # The project that is already loaded.
        scene_dir = project.project_path
        self.scene_name = project.scene_name
        self.preview_name = self.scene_name
        self.preview_path = "%s/_Preview/" % scene_dir.split(self.scene_name)[0]

        if self.blocking_check.isChecked():
            self.preview_path = "%s/Blocking/" % self.preview_path
            self.preview_name = "%s_Blocking" % self.preview_name
        if not os.path.exists(self.preview_path):
            os.makedirs(self.preview_path)
        self.temp_path = "C:/Temp/temp_previews/%s_Temp.mov" % self.scene_name
        self.preview_final = "%s/%s.mov" % (self.preview_path,self.preview_name)

        self.sound_file = "%s/%s/%s_Sound.wav" %(scene_dir.split(self.scene_name)[0],self.scene_name,self.scene_name)
        if not os.path.exists(self.sound_file):
            self.sound_file = None
            log("NO SOUND FILE FOUND")


    def create_preview(self):
        self.findSceneInfo()
        self.render_height = float(self.crop_edit.text())*self.height
        self.render_width = float(self.crop_edit.text()) * self.width


        if self.render_check.isChecked():
            js_exporter.exportToQuicktime("", -1, -1, True, self.render_width, self.render_height, self.temp_path, "", False,1)
        else:
            js_exporter.exportOGLToQuicktime(self.preview_name + "_Temp", "C:/Temp/temp_previews/", -1, -1,
                                             self.render_width, self.render_height)
        if use_config:
            log("Pipeline slate")
            use_audio = False
            if self.sound_file:
                use_audio =True
            PA.createPreview_2D(self.scene_name,
                                inputPath=self.temp_path,
                                outputPath=self.preview_final,
                                audioPath=self.sound_file,
                                crop=self.crop_check.isChecked(),
                                cropWidth=self.width,
                                cropHeight=self.height,
                                title=self.scene_name,
                                frameCount=True,
                                timecode=True,
                                date=True,
                                useAudioFile=use_audio,
                                runCmd=True,
                                build_slate=self.slate_check.isChecked(),
                                user=self.u_edit.text())

        else:
            log("CREATING REMOTE SLATE")
            self.create_preview_locally_func(input_path=self.temp_path,
                                             output_path=self.preview_final,
                                             title=self.preview_name,
                                             slate=self.slate_check.isChecked(),
                                             crop=self.crop_check.isChecked(),
                                             crop_w=int(self.width),
                                             crop_h=int(self.height),
                                             audio=self.sound_file,
                                             user=self.u_edit.text())


    def create_preview_locally_func(self,input_path="", output_path="", title=None, slate=True,crop=False,crop_w=1920,crop_h=1080,audio=None,user=None):

        stream = ffmpeg.input(input_path).video

        if audio:
            audio_stream = ffmpeg.input(audio).audio
            audio_check = ffmpeg_util.needAudioCheck(video_path=input_path,audio_path=audio)
            if audio_check:
                if audio_check < 0:
                    dur = ffmpeg_util.probeDuration(input_path, codec_type="video")
                    audio_stream = audio_stream.filter("atrim",duration=dur)

        else:
            audio_check = ffmpeg_util.needAudioCheck(input_path)
            if audio_check:
                audio = ffmpeg_util.readySoundStream(input_path, input_path)
            else:
                audio = ffmpeg.input(input_path).audio
        if crop:
            stream = self.create_crop_locally(stream, width=crop_w, height=crop_h)

        if slate:
            stream = self.create_slate_locally(stream, title=title, frameCount=True, timecode=True, date=True,user=user)
        if audio:
            audio_stream = audio_stream.filter('asetpts', expr='PTS-STARTPTS')
            stream = ffmpeg.output(audio_stream, stream, output_path, acodec='pcm_s16le', pix_fmt='yuv420p')
        else:
            stream = ffmpeg.output(stream,output_path)

        _string = ' '.join(ffmpeg.compile(stream, overwrite_output=True))
        try:
            log('::::>> RUNNING:\n' + _string)
            ffmpeg.run(stream, overwrite_output=True)
        except Exception as e:
            log(e)

        return _string

    def create_crop_locally(self,stream, width=1920, height=1080):
        x = (self.render_width - width) / 2
        y = (self.render_height - height) / 2
        log("CROPPING")
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

def log(message):
	if in_toonboom:
		sess = harmony.session()
		sess.log(str(message))
	else:
		print(message)

def run():
    global preview_ui
    preview_ui = PreviewPython_UI()
    # preview_ui.show()


if __name__ == '__main__':
    import sys
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    t = PreviewPython_UI()
    t.show()
    app.exec()