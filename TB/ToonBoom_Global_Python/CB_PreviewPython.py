# import sys
# sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" )

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os
import ffmpeg
import json
# import file_util

try:
    from ToonBoom import harmony
    in_toonboom = True
except Exception as e:
    in_toonboom = False

def log(message):
    if in_toonboom:
        sess = harmony.session()
        sess.log(str(message))
    else:
        print(message)

import sys

# os.environ["BOM_PIPE_PATH"] = "C:/Users/cg/PycharmProjects/cobopipe_v02-001/"
if os.environ.get("BOM_PIPE_PATH"):
    sys.path.append(os.environ["BOM_PIPE_PATH"])
    from getConfig import getConfigClass
    CC = getConfigClass()
    import Preview.anim as PA
    import Preview.ffmpeg_util as ffmpeg_util
    use_config = True
else:
    script_path = os.path.expandvars("%APPDATA%/Toon Boom Animation/Toon Boom Harmony Premium/2200-scripts/")
    log(script_path)
    sys.path.append(script_path) #Same dir as this script
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
        if not os.path.exists(os.path.dirname(self.save_location)):
            os.makedirs(os.path.dirname(self.save_location))
        self.width = 1280
        self.height = 720
        self.sound_file = None
        self.create_ui()
        self.checkAndApplySettings()

        self.findSceneInfo()
        self.checkLength()


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
        self.p_dd.setFixedWidth(150)
        self.p_edit = QLineEdit()
        self.p_label = QLabel("Project: ")
        self.p_label.setFixedWidth(45)
        self.p_lay.addWidget(self.p_label)
        self.p_lay.addWidget(self.p_dd)
        self.p_lay.addWidget(self.p_edit)

        self.u_lay = QHBoxLayout()

        self.u_dd = QComboBox()
        self.u_dd.setFixedWidth(150)
        self.u_edit = QLineEdit()
        self.u_label = QLabel("User: ")
        self.u_label.setFixedWidth(45)
        self.u_lay.addWidget(self.u_label)
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
        # load_dict = self.loadJson(self.save_location)
        load_dict = self.load_json(self.save_location)
        if load_dict:
            self.slate_check.setChecked(load_dict["slate_check"])
            if self.u_dd.findText(load_dict["user"])>-1:
                self.u_dd.setCurrentText(load_dict["user"])
            self.u_edit.setText(load_dict["user"])
            self.blocking_check.setChecked(load_dict["blocking_check"])
            self.render_check.setChecked(load_dict["render_check"])
        if use_config:
            if os.environ.get("BOM_USER"):
                self.u_dd.setCurrentText(os.environ["BOM_USER"])
                self.u_edit.setText(os.environ["BOM_USER"])


    def load_json(self,load_file):
        if os.path.isfile(load_file):
            with open(load_file, 'r') as cur_file:
                return json.load(cur_file)
        else:
            return {}

    def save_json(self, save_location, save_info):
        with open(save_location, 'w+') as saveFile:
            json.dump(save_info, saveFile)
        saveFile.close()

    def closeEvent(self,event):

        save_dict = {"slate_check":self.slate_check.isChecked(),
                     "user":self.u_edit.text(),
                     "blocking_check":self.blocking_check.isChecked(),
                     "render_check":self.render_check.isChecked()}
        # self.saveJson(self.save_location,save_dict)
        self.save_json(self.save_location, save_dict)
        super(PreviewPython_UI, self).closeEvent(event)


    def findSceneInfo(self):
        sess = harmony.session()  # Fetch the currently active session of Harmony
        project = sess.project  # The project that is already loaded.
        scene_dir = project.project_path
        self.folder_name = project.scene_name
        self.scene_name = self.folder_name
        if "_V" in self.scene_name:
            self.scene_name = self.scene_name.split("_V")[0]

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

    def isFileLocked(self,path):
        renamed_path = "%s_lockCheck." % path.split(".")[0] + path.split(".")[1]
        try:
            os.rename(path, renamed_path)
            os.rename(renamed_path, path)
            return False
        except Exception as e:
            if not str(e) == '[Error 32] The process cannot access the file because it is being used by another process':
                log(e)
        return True

    def checkIfLocked(self,path):
        if os.path.exists(path):
            if self.isFileLocked(path):
                QMessageBox.information(self, 'File is locked',
                                        """The current playblast file is locked and cannot be overwritten.\nPlease check if you or anyone else have the file open.\nIf the problem persists, please contact your local TD.\n""",QMessageBox.Ok,QMessageBox.Ok)
                return True
        return False



    def create_preview(self):
        self.findSceneInfo()
        if self.checkLength():
            if not self.checkIfLocked(self.preview_final):

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
                log("Finished")
                os.startfile(self.preview_final)

    def checkLength(self):
        sess = harmony.session()
        project = sess.project
        scene_length = project.scene.frame_count
        if self.sound_file:
            audio_length = ffmpeg_util.probeDuration(self.sound_file, codec_type="audio")
            audio_frames = round(float(audio_length) * float(project.scene.framerate))
            if scene_length !=audio_frames:
                log("ISSUE!: not the same length!")
                log("%s -> %s" % (audio_frames,scene_length))
                buttonReply = QMessageBox.question(self, 'Difference between scene and audio length. Continue?', "Scene: %s - Audio: %s" % (scene_length,audio_frames),
                                                             QMessageBox.Yes | QMessageBox.No,
                                                             QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    return True
                else:
                    return False
        else:
            log("Can't find any audio file to compare to")
            return False
        return True


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

        # _string = ' '.join(ffmpeg.compile(stream, overwrite_output=True))
        _string = ""
        for s in ffmpeg.compile(stream, overwrite_output=True):
            if s == "ffmpeg" or s.startswith("-"):
                _string = _string + " " + s
            else:
                _string = _string + ' "' +s + '"'
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
        font = 'C:\\/Windows/Fonts/Arial.ttf'

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