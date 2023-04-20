### Render submit via Maya or bat file ###
### need PyQt5 and Python 3+ to work as bat file ###
### Needs to have env path set for Maya to work as bat file ### (C:\Program Files\Autodesk\Maya2019\bin)

from Log.CoboLoggers import getLogger,setFileLevel,setConsoleLevel


logger = getLogger()
setFileLevel(logger,10)
setConsoleLevel(logger,10)
from getConfig import getConfigClass
CC = getConfigClass()


try:
    import maya.mel as mel
    import maya.cmds as cmds

    from PySide2 import QtWidgets, QtCore, QtGui
    import maya.app.renderSetup.views.renderSetupPreferences as prefs
    from maya import OpenMaya as om
    import Maya_Functions.vray_util_functions as vray_util
    import Maya_Functions.file_util_functions as file_util
    import Maya_Functions.submit_to_deadline as deadline
    import cryptoAttributes
    import maya.app.renderSetup.model.aovs as arnold_aovs
    import maya.app.renderSetup.model.renderSettings as arnold_renderSettings
    import maya.mel as mel
    in_maya = True
    logger.debug("In maya!")

except:
    from PySide2 import QtWidgets, QtCore, QtGui
    in_maya = False

from Multiplicity import ThreadPool
import runtimeEnv as runtime
# from runtimeEnv import runtime.getRuntimeEnvFromConfig

if in_maya:
    import MayaDockable
    import reloadModules
# import ClearImportedModules as CIM
# CIM.dropCachedImports("Configs.ConfigUtil","OIDManager","LightHelper","Maya_Functions.ref_util_functions")



# import ProjectConfig as cfg
# import ConfigUtil as cfg_util

import json
import os
import getpass
from shutil import copyfile
import subprocess
import re
import users

# Get renderer
if "maya_render" in CC.project_settings.keys():
	render_type = CC.project_settings["maya_render"]
else:
	render_type = "vray"


# Todo make a file for users instead of hardcoding. In config file? Or seperate?
class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setObjectName("RenderSubmit")
        self.setWindowTitle("RenderSubmit")
        self.setWindowFlags(QtCore.Qt.Window)
        self.set_palette()

        self.base_path = CC.get_base_path() #cfg.project_paths["base_path"] # self.base_path = "P:/930382_Kiwi&Strit_2/Production/"
        self.presets_folder = CC.get_render_presets() #cfg_util.CreatePathFromDict(cfg.project_paths["render_presets"]) # self.presets_folder = "%sPipeline/RenderSettings_Presets/" % self.base_path
        self.preset_config_file = CC.get_render_preset_config() #cfg_util.CreatePathFromDict(cfg.project_paths["render_preset_config"]) # self.preset_config_file = "%sPipeline/Preset_Config.json" % self.base_path
        self.user_save_file = "C:/Temp/%s/Render_User.json" % CC.project_name
        self.user_list = CC.get_users('Render')
        if not self.user_list:
            self.user_list = ["UserA","UserB","UserC"]

        self.onlyInt = QtGui.QIntValidator()
        self.info_dict = {"episode_name":"","seq_name":"","shot_name":""}

        self.shot_path = ""
        self.shot_name = ""

        self.orr_dict = {}

        if render_type == 'arnold':
            self.imager_dict = {}
        self.aov_dict = {}
        self.preset_dict = {}
        self.preset_config = {}
        self.default_values = {}
        self.rf = RenderSubmitFunctions(self)
        self.preset_config = self.LoadSettings(self.preset_config_file)
        self.user_dict = self.LoadSettings(self.user_save_file)
        # self.signals = Signals.Signals()
        self.thread_pool = ThreadPool.ThreadPool()
        # self.thread_pool.signals.result.connect(self.printThreadResult)

        if in_maya:
            self.GetSceneInfo() # self.GuessEpisodeAndSequence()
            self.SetTimeline()
            self.callbackJobs = {}
        self.CreateWindow()
        self.rf.ImportRenderSettings()
        self.GetPresetsAndAOVs()
        self.thread_pool.signals.progressbar_init.connect(self.progressBar.setMaximum)
        self.thread_pool.signals.progressbar_value.connect(self.progressBar.setValue)
        self.thread_pool.signals.progressbar_value.connect(self.checkIfReadyToSubmit)

        if in_maya:
            self.fileCheck(auto=True)
            self.doubleSkyCheck()
            self.checkDefaultRenderLayerError()
    
    def set_palette(self):
		#TODO setting palette in maya does NOT look great
        if not in_maya:
            magenta = {"R": 142, "G": 45, "B": 197}
            blue = {"R": 50, "G": 50, "B": 255}

            hi_lgt = blue
            palette = QtGui.QPalette()
            palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
            palette.setColor(QtGui.QPalette.Base, QtGui.QColor(40, 40, 40))
            palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
            palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
            palette.setColor(QtGui.QPalette.Text, QtCore.Qt.lightGray)
            palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
            palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
            palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
            palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(hi_lgt["R"], hi_lgt["G"], hi_lgt["B"]).lighter(100))
            palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.white)
            self.setPalette(palette)
            QtWidgets.QApplication.instance().setStyle('Fusion')

    # This function creates grid layout from the values in grid_x and grid_y
    def GridLayout(self):
        
        grid_x = 2
        grid_y = 3

        x_value = []
        y_value = []
        
        for y in range(grid_x):
            for x in range(grid_y):
                x_value.append(x)
                y_value.append(y)
        return x_value, y_value
    
    def CreateWindow(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        # self.button_layout = QtWidgets.QVBoxLayout()
        self.bottom_layout = QtWidgets.QHBoxLayout()
        self.prefix_layout = QtWidgets.QHBoxLayout()

        # USER SETTINGS
        self.user_group = QtWidgets.QGroupBox("User:")
        self.user_layout = QtWidgets.QHBoxLayout()
        self.user_dd = QtWidgets.QComboBox()
        self.addUser_button = QtWidgets.QPushButton('Add')
        self.addUser_button.setMaximumWidth(50)
        self.user_layout.addWidget(self.user_dd)
        self.user_layout.addWidget(self.addUser_button)
        self.user_group.setLayout(self.user_layout)
        self.user_dd.addItems(sorted(self.user_list))
        self.user_dd.currentIndexChanged.connect(self.SaveUser)
        self.addUser_button.clicked.connect(self.add_user_popup)

        # RoyalRender Settings
        self.rr_group = QtWidgets.QGroupBox("Royal Render:")
        self.rr_layout = QtWidgets.QGridLayout()
        self.priority_label = QtWidgets.QLabel("RR Priority(%): ")
        self.priority_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.priority_int = QtWidgets.QLineEdit("50")
        # self.priority_int.setAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.priority_int.setMaximumWidth(50)
        self.priority_int.setValidator(self.onlyInt)

        self.overwrite_checkbox = QtWidgets.QCheckBox("Overwrite Frames")
        self.overwrite_checkbox.setChecked(True)

        self.stepped_label = QtWidgets.QLabel("Stepped:")
        self.stepped_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)
        self.stepped_int = QtWidgets.QLineEdit("1")
        self.stepped_int.setMaximumWidth(50)
        self.stepped_int.setValidator(self.onlyInt)

        self.rr_layout.addWidget(self.priority_label, 0,0)
        self.rr_layout.addWidget(self.priority_int, 0, 1)
        self.rr_layout.addWidget(self.stepped_label, 0, 2)
        self.rr_layout.addWidget(self.stepped_int, 0, 3)
        self.rr_layout.addWidget(self.overwrite_checkbox, 1,0,1,2)


        self.rr_group.setLayout(self.rr_layout)


        # PRESET SETTINGS
        self.preset_group = QtWidgets.QGroupBox("Preset Settings")
        self.preset_layout = QtWidgets.QVBoxLayout()
        self.preset_dd_layout = QtWidgets.QHBoxLayout()

        self.preset_dd = QtWidgets.QComboBox()
        self.preset_create_button = QtWidgets.QPushButton("+")
        self.preset_create_button.clicked.connect(self.CreateNewPreset)
        self.preset_create_button.setMaximumWidth(30)
        self.preset_delete_button = QtWidgets.QPushButton("-")
        self.preset_delete_button.clicked.connect(self.DeleteCurrentPreset)
        self.preset_delete_button.setMaximumWidth(30)
        self.preset_button_layout = QtWidgets.QHBoxLayout()

        self.pick_preset_buton = QtWidgets.QPushButton("Pick Preset")
        self.pick_preset_buton.clicked.connect(self.PickPreset)
        self.appy_preset_button = QtWidgets.QPushButton("Apply Preset")
        self.appy_preset_button.clicked.connect(self.ApplyPresetCall)

        self.save_preset_button = QtWidgets.QPushButton("Save Preset")
        self.save_preset_button.clicked.connect(self.SavePresetCall)

        self.preset_group.setLayout(self.preset_layout)
        self.preset_layout.addLayout(self.preset_dd_layout)
        self.preset_dd_layout.addWidget(self.preset_dd)
        self.preset_dd_layout.addWidget(self.preset_dd)
        self.preset_dd_layout.addWidget(self.preset_create_button)
        self.preset_dd_layout.addWidget(self.preset_delete_button)
        self.preset_layout.addLayout(self.preset_button_layout)
        self.preset_button_layout.addWidget(self.pick_preset_buton)
        self.preset_button_layout.addWidget(self.save_preset_button)

        self.preset_layout.addWidget(self.appy_preset_button)

        #------------------------------------------------------------------------------------------------------------------------
        # RENDER SETTINGS WIDGETS
        #------------------------------------------------------------------------------------------------------------------------
        self.render_settings_layout = QtWidgets.QVBoxLayout()
        self.render_group = QtWidgets.QGroupBox("Render Settings")
        self.render_settings_dd = QtWidgets.QComboBox()
        self.render_settings_dd.setMinimumWidth(200)
        self.apply_render_settings = QtWidgets.QPushButton("Apply Render Settings")
        self.apply_render_settings.clicked.connect(self.ApplyRenderSettingsCall)

        self.import_render_settings = QtWidgets.QPushButton("Import Global Settings") #Removed from UI.
        self.import_render_settings.clicked.connect(self.rf.ImportRenderSettings)

        self.render_checkbox_layout = QtWidgets.QGridLayout()
        
                
        # Render settings dictionary
        self.render_settings =  {"Add BG Render":   {"tooltip": "Add a OnlyBg render along with the picked preset. Renders only 1 frame and only Set and SetDress showing",
                                                    "default_state": False, 
                                                    "render_engine": ["vray"], 
                                                    "menu": "render settings"},
                            "Sphere Volume Render": {"tooltip": "Uses the vray volumetric override to only render the inside of volume shapes",
                                                    "default_state": False,
                                                    "render_engine": ["vray"], 
                                                    "menu": "render settings"}, 
                            "Render Layers":        {"tooltip": "Enables rendering of render layers",
                                                    "default_state": False,
                                                    "render_engine": ["vray"], 
                                                    "menu": "render settings"},
                            "Single Frame":         {"tooltip": "Render only the first frame",
                                                    "default_state": False,
                                                    "render_engine": ["vray"], 
                                                    "menu": "render settings"}, 
                            "Render ONLY BG":       {"tooltip": "Only submits the OnlyBG Render, solo with no color render",
                                                    "default_state": False,
                                                    "render_engine": ["vray"], 
                                                    "menu": "render settings"},
                            "Full-Length BG":       {"tooltip": "Render OnlyBG for the full length of the shot",
                                                    "default_state": False,
                                                    "render_engine": ["vray"], 
                                                    "menu": "render settings"},
                            "EXR MultiPart":                                {"tooltip": "EXR MultiPart", 
                                                                                "default_state": True,
                                                                                "render_engine": ["vray"], 
                                                                                "menu": "render options"}, 
                            "ENV Override OFF":                                 {"tooltip": "Sets ENV override in Overrides tab, to off, when applying the render setting", 
                                                                                "default_state": False,
                                                                                "render_engine": ["vray"], 
                                                                                "menu": "render options"}, 
                            "Auto Create PropID Set":                           {"tooltip": "Auto Create PropID Set",
                                                                                "default_state": True,
                                                                                "render_engine": ["vray"], 
                                                                                "menu": "render options"}, 
                            "Set Physical Camera Attr":                         {"tooltip": "Set Physical Camera Attr",
                                                                                "default_state": False,
                                                                                "render_engine": ["vray"], 
                                                                                "menu": "render options"}, 
                            "Render 10% extra to use for slight camera tracks": {"tooltip": "Render 10% extra to use for slight camera tracks", 
                                                                                "default_state": False,
                                                                                "render_engine": ["vray"], 
                                                                                "menu": "render options"}, 
                            "Create CryptoMatte":                               {"tooltip": "Creates a seperate scene with cryptomatte IDs and render it in a seperate stack", 
                                                                                "default_state": False,
                                                                                "render_engine": ["vray"], 
                                                                                "menu": "render options"},
                            "Bubble VFX":                                       {"tooltip": "Makes a bubble render based on the Bubble_FX set in the scene", 
                                                                                "default_state": False,
                                                                                "render_engine": ["vray"], 
                                                                                "menu": "render options"}
                            }


        # RENDER MENU SETTINGS
        # ----------------------------------------------------------------------------------------------------------------------------------------------------
        
        # self.render_options_dict = {}
        # self.checkbox_dict = {"Render Settings": self.render_settings_dict, "Render Options": self.render_options_dict}
        for key, dictionary in self.render_settings.items():
            if render_type in dictionary["render_engine"]:       # Right now the condition is "not", since the renderer is arnold, but not should be removed once done
                self.render_settings[key]['checkbox'] = QtWidgets.QCheckBox(key)
                self.render_settings[key]['checkbox'].setChecked(dictionary["default_state"])
                self.render_settings[key]['checkbox'].setToolTip(dictionary["tooltip"])

                if in_maya:
                    self.render_settings[key]['checkbox'].clicked.connect(self.layerLabelUpdate)

        # Organize the checkboxes in a grid layout
        x_value, y_value = self.GridLayout()
        for key, _x, _y  in zip(self.render_settings.keys(), x_value, y_value):
            if render_type in dictionary['render_engine']:
                if self.render_settings[key]['menu'] == 'render settings':
                    self.render_checkbox_layout.addWidget(self.render_settings[key]['checkbox'], _x, _y)

        # RENDER MENU OPTIONS
        # ----------------------------------------------------------------------------------------------------------------------------------------------------
        self.menu_bar = QtWidgets.QMenuBar()
        self.menu_options = QtWidgets.QMenu("Render Options", self.menu_bar)
        self.menu_options.setToolTipsVisible(True)
                    
        # Add checkboxes to the options menu
        for key, dictionary in self.render_settings.items():
            if render_type in dictionary['render_engine']:
                if dictionary['menu'] == 'render options':
                    self.action = QtWidgets.QWidgetAction(self.menu_bar)
                    self.action.setDefaultWidget(dictionary['checkbox'])
                    self.menu_options.addAction(self.action)
        
        self.render_settings_layout.addWidget(self.render_settings_dd)
        self.render_settings_layout.addLayout(self.render_checkbox_layout)
        self.render_settings_layout.addWidget(self.apply_render_settings)    
        self.menu_bar.addMenu(self.menu_options)
        self.render_settings_layout.addWidget(self.menu_bar)
        self.render_group.setLayout(self.render_settings_layout)


        if render_type == 'arnold':
            # IMAGER SETTINGS
            # ----------------------------------------------------------------------------------------------------------------------------------------------------

            self.imager_settings_layout = QtWidgets.QVBoxLayout()
            self.imager_buttons_layout = QtWidgets.QHBoxLayout()
            self.imager_group = QtWidgets.QGroupBox("Imager Settings")
            self.imager_settings_dd = QtWidgets.QComboBox()
            self.imager_settings_dd.setMinimumWidth(200)
            self.export_imager_settings = QtWidgets.QPushButton("Export Imager")
            self.apply_imager_settings = QtWidgets.QPushButton("Import Imager")
            self.export_imager_settings.clicked.connect(self.save_imager)
            self.apply_imager_settings.clicked.connect(self.import_imager)
            # self.apply_imager_settings.clicked.connect(self.ApplyRenderSettingsCall)
            self.imager_settings_layout.addWidget(self.imager_settings_dd)
            self.imager_settings_layout.addLayout(self.imager_buttons_layout)
            self.imager_buttons_layout.addWidget(self.export_imager_settings)
            self.imager_buttons_layout.addWidget(self.apply_imager_settings)
            self.imager_group.setLayout(self.imager_settings_layout)


         
        # AOV SETTINGS
        # ----------------------------------------------------------------------------------------------------------------------------------------------------
        
        self.aov_layout = QtWidgets.QVBoxLayout()
        self.aov_group = QtWidgets.QGroupBox("AOV Settings")
        self.aov_dd = QtWidgets.QComboBox()
        self.aov_dd.setMinimumWidth(200)
        self.import_aov = QtWidgets.QPushButton("Import AOV")
        self.import_aov.clicked.connect(self.ImportAOVsCall)
        self.clean_aov = QtWidgets.QPushButton("Clean MultiMatte AOVs")
        self.aov_layout.addWidget(self.aov_dd)
        self.aov_layout.addWidget(self.import_aov)
        # self.aov_layout.addWidget(self.clean_aov)
        self.aov_group.setLayout(self.aov_layout)

        # ADD SCENE SETTINGS
        self.scene_group = QtWidgets.QGroupBox("Submit Settings")
        self.scene_layout = QtWidgets.QVBoxLayout()

        self.set_path_button = QtWidgets.QPushButton("Set Render Path")
        self.set_path_button.clicked.connect(self.SetRenderPathCall)
        self.set_attr_on_cam = QtWidgets.QPushButton("Set Physical Attr")
        self.set_attr_on_cam.clicked.connect(self.SetAttrOnCamCall)
        self.export_cam = QtWidgets.QPushButton("Export Camera")
        self.export_cam.clicked.connect(self.ExportBakedCameraCall)

        self.scene_layout.addWidget(self.set_path_button)
        self.scene_layout.addWidget(self.set_attr_on_cam)
        self.scene_layout.addWidget(self.export_cam)
        self.scene_group.setLayout(self.scene_layout)

        if in_maya:
            # ADD RENDER LAYERS LABEL
            self.render_layers_label = QtWidgets.QLabel("Currently layers: N/A")

            # self.layerLabelUpdate()

        # File check button
        self.fileCheckButton = QtWidgets.QPushButton('Check Files')
        self.fileCheckButton.clicked.connect(lambda: self.fileCheck())

        # ADD SUBMIT BUTTON
        self.submit_button = QtWidgets.QPushButton("Submit")
        self.submit_button.clicked.connect(self.SubmitRenderCall)

        # Connect layouts
        if not in_maya:  # SHOW A EPISODE SELECTION LAYOUT
            self.ep_list = self.PopulateEpisode(CC.get_film_path())
            self.CreateSelectionUI()
            self.UpdateEpisodeDD()
            self.main_layout.addLayout(self.selection_layout)

        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setMaximumWidth(300)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progress_bar_label = QtWidgets.QLabel("")
        self.progress_bar_label.setMinimumHeight(5)
        self.progress_bar_label.setWordWrap(True)


        self.main_layout.addWidget(self.user_group)
        self.main_layout.addWidget(self.preset_group)
        self.main_layout.addWidget(self.render_group)
        if render_type == 'arnold':
            self.main_layout.addWidget(self.imager_group)
        self.main_layout.addWidget(self.aov_group)
        self.main_layout.addWidget(self.rr_group)
        self.main_layout.addWidget(self.scene_group)
        if in_maya:
            self.main_layout.addWidget(self.render_layers_label)
        self.main_layout.addWidget(self.fileCheckButton)
        self.main_layout.addWidget(self.submit_button)
        self.main_layout.addWidget(self.progressBar)

        self.setLayout(self.main_layout)
        self.CollectDefaultValues()

    def CreateSelectionUI(self):
        self.selection_layout = QtWidgets.QVBoxLayout()
        self.selection_top_layout = QtWidgets.QVBoxLayout()

        self.list_layout = QtWidgets.QHBoxLayout()
        self.load_layout = QtWidgets.QHBoxLayout()
        self.episode_label = QtWidgets.QLabel("Episode: ")
        self.episode_dd = QtWidgets.QComboBox()
        # self.episode_input = QtWidgets.QLineEdit()
        # self.episode_input.setValidator(self.onlyInt)

        self.load_layout.addWidget(self.episode_label)
        self.load_layout.addWidget(self.episode_dd)

        self.seq_label = QtWidgets.QLabel("SQ: ")
        # self.seq_input = QtWidgets.QLineEdit()
        # self.seq_input.setValidator(self.onlyInt)
        self.seq_dd = QtWidgets.QComboBox()
        self.load_layout.addWidget(self.seq_label)
        self.load_layout.addWidget(self.seq_dd)

        self.load_sq_button = QtWidgets.QPushButton("Load")
        self.load_sq_button.clicked.connect(self.LoadSequence)
        self.load_layout.addWidget(self.load_sq_button)

        self.show_light_checkbox = QtWidgets.QCheckBox("Only Shots with Light Scenes")
        self.checkbox_layout = QtWidgets.QHBoxLayout()
        self.checkbox_layout.addWidget(self.show_light_checkbox)
        self.show_light_checkbox.setChecked(True)
        self.show_light_checkbox.stateChanged.connect(self.UpdateEpisodeDD)

        self.selection_layout.addLayout(self.load_layout)
        self.selection_layout.addLayout(self.checkbox_layout)
        # LIST
        self.shot_list = QtWidgets.QListWidget()
        self.shot_list.setMinimumHeight(150)
        self.shot_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.list_layout.addWidget(self.shot_list)

        self.shot_list.itemDoubleClicked.connect(self.ShotDoubleClicked)

        self.selection_layout.addLayout(self.selection_top_layout)
        self.selection_layout.addLayout(self.list_layout)
        # return self.selection_layout

    def closeEvent(self, event):
        if in_maya:
            for layer, job in self.callbackJobs.items():
                om.MMessage.removeCallback(job)
        event.accept() # let the window close



    def layerLabelUpdate(self):
        job_list = self.rf.updateRenderableCallbacks(self.callbackJobs)
        if job_list:
            for layer, job in job_list:
                self.callbackJobs[layer] = job

        if self.render_settings["Render Layers"]['checkbox'].isChecked():
            layersToRender = self.rf.getActiveRenderLayers()
        else:
            layersToRender = ['masterLayer']

        message = 'Current layers: '
        if layersToRender == []:
            message = message + 'None'
        else:
            for i, layer in enumerate(layersToRender):
                if i == 0:
                    message = message + layer
                elif i > 0:
                    message = message + ', ' + layer

        self.render_layers_label.setText(message)

    def ShotDoubleClicked(self, item):
        logger.debug(item.text())

    def LoadSequence(self):
        logger.info("loading shots!")
        self.shot_list.clear()
        self.ep = "E%s" % (self.episode_input.text()).zfill(2)
        self.seq = "SQ%s" % (str(int(self.seq_input.text()))).zfill(3)
        # print("EP: %s SEQ: %s" % (self.ep, self.seq))
        self.sequence_path = "%sFilm/%s/%s_%s/" % (self.base_path, self.ep, self.ep, self.seq)
        temp_shot_list = []
        if os.path.exists(self.sequence_path):
            content = os.listdir(self.sequence_path)
            for con in content:
                con_path = "%s/%s/" % (self.sequence_path, con)
                append_true = True
                if os.path.isdir(con_path) and self.FindShot(con):
                    if self.show_light_checkbox.isChecked():
                        if self.CheckForLightScene(con):
                            append_true = True
                        else:
                            append_true = False
                    if append_true:
                        # print("is shot: %s" % con)
                        temp_shot_list.append(con)
        self.shot_list.addItems(sorted(temp_shot_list))

    def UpdateEpisodeDD(self):
        self.episode_dd.clear()
        self.episode_dd.addItems(sorted(self.ep_list.keys()))
        self.episode_dd.currentIndexChanged.connect(self.UpdateSeqDD)
        self.UpdateSeqDD()

    def UpdateSeqDD(self):
        self.seq_dd.clear()
        cur_ep = self.episode_dd.currentText()
        if cur_ep:
            self.info_dict["episode_name"] = cur_ep.split("_")[-1]
            self.seq_dd.addItems(sorted(self.ep_list[cur_ep]))
        self.seq_dd.currentIndexChanged.connect(self.UpdateShotList)
        self.UpdateShotList()

    def UpdateShotList(self):
        self.shot_list.clear()
        cur_ep = self.episode_dd.currentText()
        cur_seq = self.seq_dd.currentText()
        if cur_ep and cur_seq:
            self.info_dict["seq_name"] = cur_seq.split("_")[-1]
            if self.show_light_checkbox.isChecked():
                for cur_shot in sorted(self.ep_list[cur_ep][cur_seq]):
                    self.info_dict["shot_name"] = cur_shot.split("_")[-1]
                    if self.CheckForLightScene():
                        self.shot_list.addItem(cur_shot)
            else:
                self.shot_list.addItems(sorted(self.ep_list[cur_ep][cur_seq]))

    def PopulateEpisode(self,film_path):
        film_content = os.listdir(film_path)
        ep_dict = {}
        for cur_con in film_content:
            if self.FindEpisode(cur_con):
                cur_path = "%s/%s" % (film_path, cur_con)
                if os.path.isdir(cur_path):
                    ep_dict[cur_con] = {}
                    self.PopulateSeq(cur_con,cur_path,ep_dict)
        return ep_dict

    def PopulateSeq(self,cur_ep,cur_ep_path,ep_dict):
        ep_content = os.listdir(cur_ep_path)
        for cur_con in ep_content:
            if self.FindSequence(cur_con):
                cur_path = "%s/%s" % (cur_ep_path, cur_con)
                if os.path.isdir(cur_path):
                    ep_dict[cur_ep][cur_con] = []
                    ep_dict = self.PopulateShot(cur_ep,cur_con,cur_path,ep_dict)
        return ep_dict

    def PopulateShot(self,cur_ep,cur_seq,cur_seq_path,ep_dict):
        seq_content = os.listdir(cur_seq_path)
        for cur_con in seq_content:
            if self.FindShot(cur_con):
                cur_path = "%s/%s" % (cur_seq_path, cur_con)
                if os.path.isdir(cur_path):
                    ep_dict[cur_ep][cur_seq].append(cur_con)
        return ep_dict

    def FindEpisode(self,content):
        low_case = content.lower()
        re_compile = re.compile("^(e)\d{2}$")
        if re_compile.search(low_case):
            # logger.debug(content + " matches!")
            return True
        else:
            return False

    def FindSequence(self, content):
        low_case = content.lower()
        re_compile = re.compile("^(e)\d{2}(_sq)\d{3}$")
        if re_compile.search(low_case):
            # logger.debug(content + " matches!")
            return True
        else:
            return False

    def FindShot(self,content):
        low_case = content.lower()
        re_compile = re.compile("^(e)\d{2}(_sq)\d{3}(_sh)\d{3}$")
        if re_compile.search(low_case):
            # logger.debug(content + " matches!")
            return True
        else:
            return False

    def CheckForLightScene(self):
        light_path = CC.get_shot_light_file(**self.info_dict) #cfg_util.CreatePathFromDict(cfg.project_paths["shot_light_file"],self.info_dict)
        # light_path = "%s/%s/02_Light/%s_Light.ma" % (self.sequence_path, cur_shot, cur_shot)
        if os.path.exists(light_path):
            return True
        else:
            return False

    def DeleteCurrentPreset(self):
        logger.info("Should delete %s" % self.preset_dd.currentText())
        cur_key = self.preset_dd.currentText()

        self.preset_config.pop(cur_key, None)
        self.preset_dd.removeItem(self.preset_dd.currentIndex())
        self.SaveSettings()

    def SaveUser(self):
        cur_user = self.user_dd.currentText()

        user_save_dict = {"current_user":self.user_dd.currentText()}
        #check if a folder exists:
        if not os.path.exists(os.path.split(self.user_save_file)[0]):

            os.mkdir(os.path.split(self.user_save_file)[0])
        with open(self.user_save_file, 'w+') as saveFile:
            json.dump(user_save_dict, saveFile)
        saveFile.close()

    def add_user_popup(self):
        self.addUserPopup = users.add_user_ui(parent=self)
        self.addUserPopup.signals.add.connect(self.add_user)
        self.addUserPopup.show()

    def add_user(self, user):
        user = user.title()
        users.add_to_users_json('Render', user)
        self.user_list = CC.get_users('Render')
        self.user_dd.clear()
        self.user_dd.addItems(sorted(self.user_list))
        index = self.user_dd.findText(user, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.user_dd.setCurrentIndex(index)
        
        
    
    def CreateNewPreset(self):
        cur_presets = {}
        # cur_presets = self.LoadSettings()
        name = self.GetPresetInput()
        if not name:
            return False
        # Check against name case-insensitive
        check_list = []
        for check in self.preset_config.keys():
            check_list.append(check.lower())
        if name.lower() in check_list:
            logger.info("This name: %s Already exists as a preset" % name)
            return False
        # add new preset to dropdown and then save it out
        self.preset_dd.addItem(name)
        name_index = self.preset_dd.findText(name)
        self.preset_dd.setCurrentIndex(name_index)
        self.SavePresetCall()

    def save_imager(self):
        import Maya_Functions.arnold_util_functions as arnold_util
        name = self.GetPresetInput()
        path = os.path.abspath(os.path.join(CC.get_render_presets(), f"Imager_{name}.json")).replace(os.sep, '/')
        arnold_util.save_imager_preset(path)
        self.GetPresetsAndAOVs()

    def import_imager(self):
        import Maya_Functions.arnold_util_functions as arnold_util
        path = os.path.abspath(os.path.join(CC.get_render_presets(), f"{self.imager_settings_dd.currentText()}")).replace(os.sep, '/')
        arnold_util.load_imager_preset(path)

    def GetPresetInput(self):
        text, okPressed = QtWidgets.QInputDialog.getText(self, "New Preset Name", "Preset Name:",
                                                         QtWidgets.QLineEdit.Normal, "")
        if okPressed and text != '':
            return text
        else:
            return False

    def GetSceneInfo(self):
        if in_maya:
            scene_path = cmds.file(q=True, sn=True)
            self.info_dict = {}
            light_scene = CC.get_shot_light_file() #cfg_util.CreatePathFromDict(cfg.project_paths["shot_light_file"])
            self.info_dict = CC.util.ComparePartOfPath(os.path.split(scene_path)[0],os.path.split(light_scene)[0],self.info_dict) #cfg_util.ComparePartOfPath(os.path.split(scene_path)[0],os.path.split(light_scene)[0],self.info_dict) #testing
            print("INFO DICT: %s" % self.info_dict)
            if self.info_dict:
                self.setWindowTitle("RenderSubmit: EP: %s - SEQ: %s - SH %s" % (self.info_dict["episode_name"],self.info_dict["seq_name"],self.info_dict["shot_name"]))
                self.shot_name = "%s_%s_%s" % (self.info_dict["episode_name"],self.info_dict["seq_name"],self.info_dict["shot_name"])
                self.shot_path = CC.get_shot_path(**self.info_dict) #cfg_util.CreatePathFromDict(cfg.project_paths["shot_path"],self.info_dict) # self.shot_path = "%s/Film/%s/%s_%s/%s/" % (self.base_path, self.ep, self.ep, self.seq, self.shot_name)
                return True
            else:
                self.setWindowTitle("RenderSubmit: Unknown")
                logger.info("NOT A LIGHT SCENE")
                return False

    def CheckSceneAgainstDict(self):
        if in_maya:
            check_dict = {}
            scene_path = cmds.file(q=True, sn=True)
            light_scene = CC.get_shot_light_file(**check_dict) #cfg_util.CreatePathFromDict(cfg.project_paths["shot_light_file"],check_dict)
            check_dict = CC.util.ComparePartOfPath(os.path.split(scene_path)[0], os.path.split(light_scene)[0]) #cfg_util.ComparePartOfPath(os.path.split(scene_path)[0], os.path.split(light_scene)[0])
            if not check_dict or not self.info_dict:
                logger.info("can't find scene info, can't submit")
                return False
            for cur in check_dict.keys():
                if not check_dict[cur] == self.info_dict[cur]:
                    logger.info("This %s is not the same scene info: %s" % (cur,self.info_dict[cur]))
                    return False
            return True
    # def GuessEpisodeAndSequence(self):
    #     if in_maya:
    #         file_name = cmds.file(q=True, sn=True, shn=True)
    #         if "_Light" in file_name and len(file_name.split("_")) > 2:
    #             self.ep = file_name.split("_")[0]
    #             self.seq = file_name.split("_")[1]
    #             self.shot = file_name.split("_")[2]
    #             self.setWindowTitle("RenderSubmit: EP: %s - SEQ: %s - SH %s" % (self.ep, self.seq, self.shot))
    #             self.shot_name = "%s_%s_%s" % (self.ep, self.seq, self.shot)
    #             self.shot_path = "%s/Film/%s/%s_%s/%s/" % (self.base_path, self.ep, self.ep, self.seq, self.shot_name)
    #             print("EP: %s - SEQ: %s" % (self.ep, self.seq))
    #         else:
    #             self.setWindowTitle("RenderSubmit: Unknown")
    #     else:
    #         print("Select your episode and so on")

    def SetTimeline(self):
        shots = cmds.sequenceManager(lsh=True)
        if shots:
            if len(shots) == 1:
                start = cmds.shot(shots[0], q=True, st=True)
                end = cmds.shot(shots[0], q=True, et=True)

                cmds.playbackOptions(min=start)
                cmds.playbackOptions(max=end)
                cmds.playbackOptions(ast=start)
                cmds.playbackOptions(aet=end)

            else:
                logger.info('number of shots in scene is more or less than one. no timeline match is done',)

    def GetPresetsAndAOVs(self): # Getting the user last used if in maya. Finding the render presets and the exported aovs
        logger.info("Getting Presets and AOVs for dropdowns")
        # if in_maya:
        #     if cmds.optionVar(ex="RRUser"): #Setting previous user
        #         cur_user = cmds.optionVar(q="RRUser")
        #         self.user_dd.setCurrentIndex(self.user_dd.findText(cur_user))
        if self.user_dict:
            self.user_dd.setCurrentIndex(self.user_dd.findText(self.user_dict["current_user"]))
        content = os.listdir(self.presets_folder)
        for con in content:
            con_path = "%s/%s" % (self.presets_folder, con)
            if con.endswith(".json"):
                if con.startswith("AOV_"):
                    self.aov_dict[con] = con_path
                elif con.startswith("Imager_"):
                    if render_type == 'arnold':
                        self.imager_dict[con] = con_path
                else:
                    self.preset_dict[con] = con_path
        self.aov_dict['None'] = 'None'  # Adding None as an option for not using AOVs at all
        if render_type == 'arnold':
            self.imager_dict['None'] = 'None'
        self.UpdateDD()

    def UpdateDD(self):
        # clear dropdowns
        if render_type == 'arnold':
            self.imager_settings_dd.clear()
        self.aov_dd.clear()
        self.render_settings_dd.clear()
        self.preset_dd.setDisabled(True)
        self.preset_dd.clear()
        self.preset_dd.addItems(sorted(self.preset_config.keys()))
        self.preset_dd.setEnabled(True)
        aov_list = list(self.aov_dict.keys())
        if render_type == 'arnold':
            imager_list = list(self.imager_dict.keys())
        # aov_list.append("None")
        if render_type == 'arnold':
            self.imager_settings_dd.addItems(sorted(imager_list))
        self.aov_dd.addItems(sorted(aov_list))
        self.render_settings_dd.addItems(sorted(self.preset_dict.keys()))

    def CheckUpBeforeSubmit(self):
        logger.info("Checking Path is set")
        logger.info("Checking AOVs are added")

    def updatePresetWithNewKeys(self):
        missing_keys = set(self.default_values.keys()).difference(set(self.preset_config[self.preset_dd.currentText()].keys()))
        if missing_keys:
            print("Found missing keys: %s" % missing_keys)
        for k in missing_keys:
            self.preset_config[self.preset_dd.currentText()][k] = self.default_values[k]
        self.SaveSettings()


    def PickPreset(self):
        cur_preset = self.preset_dd.currentText()
        cur_rs = self.preset_config[cur_preset]["RS"]
        cur_aov = self.preset_config[cur_preset]["AOV"]
        self.updatePresetWithNewKeys()
        # check for keys not in preset
        for key in self.preset_config[cur_preset].keys():
            if key in self.render_settings.keys():
                self.render_settings[key]['checkbox'].setChecked(self.preset_config[cur_preset][key])
            

        aov_index = self.aov_dd.findText(cur_aov)
        rs_index = self.render_settings_dd.findText(cur_rs)
        if aov_index >= 0:
            self.aov_dd.setCurrentIndex(aov_index)
        if rs_index >= 0:
            self.render_settings_dd.setCurrentIndex(rs_index)

    def SavePresetCall(self):
        self.preset_config[self.preset_dd.currentText()] = {}
        self.preset_config[self.preset_dd.currentText()] = self.CollectToSaveSettings()
        self.SaveSettings()

    def CollectDefaultValues(self):
        self.default_values = self.CollectToSaveSettings()

    def CollectToSaveSettings(self):
        settings_dict = {}
        for key, dictionary in self.render_settings.items():
            if render_type in dictionary['render_engine']:
                settings_dict[key] = dictionary['checkbox'].isChecked()

            
        settings_dict["RS"] = self.render_settings_dd.currentText()
        settings_dict["AOV"] = self.aov_dd.currentText()
        settings_dict["OVERWRITE"] = self.overwrite_checkbox.isChecked()

        settings_dict["PRIO"] = self.priority_int.text()
        settings_dict["STEPPED"] = self.stepped_int.text()

        return settings_dict

    def SaveSettings(self):
        with open(self.preset_config_file, 'w+') as saveFile:
            json.dump(self.preset_config, saveFile)
        saveFile.close()

    def LoadSettings(self, load_file):
        logger.debug("Loading Settings from %s" % load_file)
        if os.path.isfile(load_file):
            with open(load_file, 'r') as cur_file:
                return json.load(cur_file)
        # self.preset_config = json.load(saveFile)
        else:
            logger.error("Can't find %s file" % load_file)
            return {}

    # CALLS TO FUNCTIONS
    def ApplyPresetCall(self):
        self.PickPreset()
        self.ApplyRenderSettingsCall()
        self.ImportAOVsCall()

    def ApplyRenderSettingsCall(self):
        # if CC.project_settings["maya_render"] == "arnold":
        #TODO IF sphere render is checked, check of "Use Envi Volume"
        #TODO IF bg only render is checked, but also sphere render, check OFF "Use Envi Volume"
        # print('ApplyRenderSettings("%s", %s)' % (self.render_settings_dd.currentText(), self.exr_multi_checkbox.isChecked()))
        if in_maya:
            cur_shot = None
            if self.info_dict:
                cur_shot = self.info_dict["shot_name"]
            self.rf.loadUnloadedChildren() #load unloaded child refs from anim-ref.
            
            if render_type == 'vray':
                settings = file_util.loadJson(CC.get_render_presets() + self.render_settings_dd.currentText())
                vray_util.applyRenderSettings(settings)
            elif render_type == 'arnold':
                settings = file_util.loadJson(CC.get_render_presets() + self.render_settings_dd.currentText())
                arnold_renderSettings.decode(settings)
                

            # self.rf.ApplyRenderSettings(rs_name=self.render_settings_dd.currentText(),exr_check=self.exr_multi_checkbox.isChecked(), bg_off=self.BG_override.isChecked(),overscan=self.extra_render_size.isChecked(),sphere_render=self.checkbox_dict["Sphere Volume Render"].isChecked(),shot=cur_shot)
            if self.render_settings["Create CryptoMatte"]['checkbox'].isChecked():
                self.rf.buildCryptoAttr()
            if self.render_settings["Auto Create PropID Set"]['checkbox'].isChecked():
                if not self.rf.CreatePropOIDSet() and CC.project_name == "KiwiStrit3":
                    err_dia = QtWidgets.QMessageBox(self)
                    err_dia.setText("OID rules are broken! Fix before submitting any more shots")
                    err_dia.exec_()
            if self.render_settings["Set Physical Camera Attr"]['checkbox'].isChecked() and self.info_dict:
                self.rf.SetPhysicalAttrOnCam(self.info_dict["shot_name"])
            self.SetRenderPathCall()

    def ImportAOVsCall(self):
        if in_maya:
            if not self.aov_dd.currentText() == "None":
                if render_type == 'arnold':
                    import Maya_Functions.arnold_util_functions as arnold_util
                    self.rf.ImportAOVsArnold(self.aov_dict[self.aov_dd.currentText()])
                    arnold_util.add_aovs_to_noice()
                else:
                    cryptoAttributes.addOID(overwrite=False)
                    # print('ImportRenderSettings("%s")' % (self.aov_dict[self.aov_dd.currentText()]))
                    self.rf.ImportAOVs(self.aov_dict[self.aov_dd.currentText()])

                

            else:
                # print('ImportRenderSettings("None")')
                self.rf.ImportAOVs("None")

            

    def SetRenderPathCall(self):
        if in_maya:
            # print('SetRenderPath("%s","%s","%s")' % (self.shot_path, self.shot_name, self.preset_dd.currentText()))

            self.rf.SetRenderPath(info_dict=self.info_dict, preset_name=self.preset_dd.currentText(),
                                  only_bg=self.render_settings["Render ONLY BG"] ['checkbox'].isChecked(),render_layer=self.render_settings["Render Layers"]['checkbox'].isChecked())
            # print('SetRenderCam("%s")' % self.shot)
            if self.info_dict: #Check if a light scene before trying to pick camera
                self.rf.SetRenderCam(self.info_dict["shot_name"])
            self.rf.SetRenderRange()

    def SetAttrOnCamCall(self):
        if in_maya:
            # logger.info('SetAttrOnCam("%s")' % self.info_dict["shot_name"])
            print(self.info_dict)
            if self.info_dict:
                self.rf.SetPhysicalAttrOnCam(self.info_dict["shot_name"])
            else:
                self.rf.SetPhysicalAttrOnCam(None)


    def ExportBakedCameraCall(self):
        if in_maya:
            self.rf.ExportCam(self.info_dict["shot_name"], self.shot_path, self.shot_name)
        else:
            for shot in self.shot_list.selectedItems():
                self.SetShotFromList(shot)
                self.rf.ExportCamMayaPy(self.shot_path, self.shot_name, self.info_dict["shot_name"])
                logger.info("Baking camera for %s" % self.shot_name)

    def SubmitRenderCall(self):
        if in_maya:
            if self.render_settings["ENV Override OFF"]['checkbox'].isChecked(): #remove BG Texture in override env.
                self.rf.CheckOffBGOverride()
            self.submitInsideOfMayaCall()
        else:
            self.submitOutsideOfMayaCall()

    def submitInsideOfMayaCall(self):
        if self.rf.RefCheck(): #check for unloaded references that might cause issues.
            cmds.file(save=True)
            current_file = cmds.file(q=True, sn=True)

            if self.CheckSceneAgainstDict(): #Check that the UI is holding info from THIS scene and not old info.
                #Make a publish report of what is added in the light-file.
                from Maya_Functions.publish_util_functions import readyPublishReport, savePublishReport
                content_dict = {}
                self.info_dict["publish_report_name"] = 'LightScene'
                readyPublishReport(info_dict=self.info_dict, current_dict=content_dict, ref=True, texture=False)
                savePublishReport(info_dict=self.info_dict, content=content_dict)
                if self.render_settings["Create CryptoMatte"]['checkbox'].isChecked():
                    self.rf.buildCryptoAttr()
                cmd_list = []

                #Check if we need to render only a single frame or a full length render of BG
                if not self.render_settings["Full-Length BG"]['checkbox'].isChecked() or self.render_settings["Single Frame"]['checkbox'].isChecked():
                    only_bg_single = True
                else:
                    only_bg_single = False
                #### BG RENDER SUBMIT ####
                if self.render_settings["Add BG Render"]['checkbox'].isChecked() or self.render_settings["Render ONLY BG"]['checkbox'].isChecked():
                    # bg_only_cmd = self.rf.RenderSubmitInfo(c_prefix=self.preset_dd.currentText(),
                                                        #    onlybg=True,
                                                        #    user_name=self.user_dd.currentText(),
                                                        #    stepped=self.stepped_int.text(),
                                                        #    r_priority=self.priority_int.text(),
                                                        #    overwrite=self.overwrite_checkbox.isChecked(),
                                                        #    info_dict=self.info_dict,
                                                        #    render_layer=None,
                                                        #    single_frame=only_bg_single
                                                        #    )

                    self.rf.SaveRenderFile(True, self.preset_dd.currentText(),current_file, self.info_dict,False, self.render_settings["Bubble VFX"]['checkbox'].isChecked())
                    # cmd_list.append(bg_only_cmd)

                #### BEAUTY RENDER SUBMIT ####
                if not self.render_settings["Render ONLY BG"]['checkbox'].isChecked():
                    if self.render_settings["Render Layers"]['checkbox'].isChecked():
                        # TODO Do a seperate cmd for BG ONLY when using render layers.
                        # for current_layer in self.rf.getActiveRenderLayers():
                            # layer_cmd = self.rf.RenderSubmitInfo(c_prefix=self.preset_dd.currentText(),
                                                                #  onlybg=False,
                                                                #  user_name=self.user_dd.currentText(),
                                                                #  stepped=self.stepped_int.text(),
                                                                #  r_priority=self.priority_int.text(),
                                                                #  overwrite=self.overwrite_checkbox.isChecked(),
                                                                #  info_dict=self.info_dict,
                                                                #  render_layer=current_layer,
                                                                #  single_frame=self.render_settings_dict["Single Frame"].isChecked())
                            # cmd_list.append(layer_cmd)
                        self.rf.SaveRenderFile(self.render_settings["Add BG Render"]['checkbox'].isChecked(),
                                               self.preset_dd.currentText(),
                                               current_file, self.info_dict,
                                               True,self.render_settings["Bubble VFX"]['checkbox'].isChecked())
                    else:
                        # preset_cmd = self.rf.RenderSubmitInfo(c_prefix=self.preset_dd.currentText(),
                                                            #   onlybg=False,
                                                            #   user_name=self.user_dd.currentText(),
                                                            #   stepped=self.stepped_int.text(),
                                                            #   r_priority=self.priority_int.text(),
                                                            #   overwrite=self.overwrite_checkbox.isChecked(),
                                                            #   info_dict=self.info_dict,
                                                            #   render_layer=None,
                                                            #   single_frame=self.render_settings_dict["Single Frame"].isChecked()
                                                            #   )
                        # cmd_list.append(preset_cmd)
                        self.rf.SaveRenderFile(False,
                                               self.preset_dd.currentText(),
                                               current_file,
                                               self.info_dict,False, self.render_settings["Bubble VFX"]['checkbox'].isChecked())

                #### CRYPTO RENDER SUBMIT ####
                if self.render_settings["Create CryptoMatte"]['checkbox'].isChecked():
                    if not self.render_settings["Render ONLY BG"]['checkbox'].isChecked():
                        self.rf.runCryptoMatteSetup(self.preset_dd.currentText(), self.info_dict)
                        # crypto_cmd = self.rf.RenderSubmitInfo(c_prefix="%s_Crypto" % self.preset_dd.currentText(),
                                                            #   onlybg=False,
                                                            #   user_name=self.user_dd.currentText(),
                                                            #   stepped=self.stepped_int.text(),
                                                            #   r_priority=self.priority_int.text(),
                                                            #   overwrite=self.overwrite_checkbox.isChecked(),
                                                            #   info_dict=self.info_dict,
                                                            #   render_layer=None,
                                                            #   single_frame=self.render_settings_dict["Single Frame"].isChecked(),
                                                            #   crop_exr=0,
                                                            #   render_file=CC.get_shot_crypto_render_file(**self.info_dict)
                                                            #   )
                        self.rf.SaveRenderFile(False, self.preset_dd.currentText(),current_file, self.info_dict)
                        # cmd_list.append(crypto_cmd)
                # for cur_cmd in cmd_list:
                    # self.rf.runRoyalRenderCmd(cur_cmd)
                # if CC.project_name == 'MiasMagic2':
                #     if current_file.endswith('_temp.ma'):
                #         os.remove(current_file) # Deleting temp file
                return True
            else:
                cmds.warning("Scene info and RenderSubmit info is not the same!!. Reopen Script please")

    def submitOutsideOfMayaCall(self):
        #TODO Make seperate files instead of a single file with multilple shots.
        cmd_threads=[]
        #self.rf.saveCmdInFile(clear=True)
        self.total = -1
        self.current_count = 0
        import Maya_Functions.file_util_functions as file_util
        self.submit_call_id = file_util.generateID()

        for shot in self.shot_list.selectedItems():
            self.SetShotFromList(shot)
            shot_dict = {}
            file_name = shot.text()
            shot_dict["episode_name"] = file_name.split("_")[0]
            shot_dict["seq_name"] = file_name.split("_")[1]
            shot_dict["shot_name"] = file_name.split("_")[2]
            self.shot_name = file_name
            self.shot_path = CC.get_shot_path(**shot_dict)

            current_file = "%s/02_Light/%s_Light.ma" % (self.shot_path, self.shot_name)
            if self.render_settings["Add BG Render"]['checkbox'].isChecked() or self.render_settings["Render ONLY BG"]['checkbox'].isChecked(): #BG ONLY RENDER
                if not self.render_settings["Full-Length BG"]['checkbox'].isChecked() or self.render_settings["Single Frame"]['checkbox'].isChecked():
                    only_bg_single = True
                else:
                    only_bg_single = False
                cmd_threads.append(ThreadPool.Worker(func=self.rf.submitOutsideMaya,
                                                     current_file=current_file,
                                                     rs_name=self.render_settings_dd.currentText(),
                                                     exr_multi=self.render_settings["EXR MultiPart"]['checkbox'].isChecked(),
                                                     only_bg=True,
                                                     aov_name=self.aov_dict[self.aov_dd.currentText()],
                                                     prefix_name=self.preset_dd.currentText(),
                                                     bg_off=self.render_settings["ENV Override OFF"]['checkbox'].isChecked(),
                                                     phys_cam=self.render_settings["Set Physical Camera Attr"]['checkbox'].isChecked(),
                                                     info_dict=shot_dict,
                                                     overscan=self.render_settings["Render 10% extra to use for slight camera tracks"]['checkbox'].isChecked(),
                                                     sphere_render=self.render_settings["Sphere Volume Render"]['checkbox'].isChecked(),
                                                     render_layer=self.render_settings["Render Layers"]['checkbox'].isChecked(),
                                                     crypto_render=self.render_settings["Create CryptoMatte"]['checkbox'].isChecked(),
                                                     overwrite=self.overwrite_checkbox.isChecked(),
                                                     project_name=CC.project_name,
                                                     r_prio=self.priority_int.text(),
                                                     stepped=self.stepped_int.text(),
                                                     user_name=self.user_dd.currentText(),
                                                     single_frame=only_bg_single,
                                                     submitCallID=self.submit_call_id,
                                                     bubbles=self.render_settings["Bubble VFX"]['checkbox'].isChecked())
                                   )

            if not self.render_settings["Render ONLY BG"]['checkbox'].isChecked(): #NORMAL RENDER
                cmd_threads.append(ThreadPool.Worker(func=self.rf.submitOutsideMaya,
                                                     current_file=current_file,
                                                     rs_name=self.render_settings_dd.currentText(),
                                                     exr_multi=self.render_settings["EXR MultiPart"]['checkbox'].isChecked(),
                                                     only_bg=False,
                                                     aov_name=self.aov_dict[self.aov_dd.currentText()],
                                                     prefix_name=self.preset_dd.currentText(),
                                                     bg_off=self.render_settings["ENV Override OFF"]['checkbox'].isChecked(),
                                                     phys_cam=self.render_settings["Set Physical Camera Attr"]['checkbox'].isChecked(),
                                                     info_dict=shot_dict,
                                                     overscan=self.render_settings["Render 10% extra to use for slight camera trucks"]['checkbox'].isChecked(),
                                                     sphere_render=self.render_settings["Sphere Volume Render"]['checkbox'].isChecked(),
                                                     render_layer=self.render_settings["Render Layers"]['checkbox'].isChecked(),
                                                     crypto_render=self.render_settings["Create CryptoMatte"]['checkbox'].isChecked(),
                                                     overwrite=self.overwrite_checkbox.isChecked(),
                                                     project_name=CC.project_name,
                                                     r_prio=self.priority_int.text(),
                                                     stepped=self.stepped_int.text(),
                                                     user_name=self.user_dd.currentText(),
                                                     single_frame=self.render_settings["Single Frame"]['checkbox'].isChecked(),
                                                     submitCallID=self.submit_call_id,
                                                     bubbles=self.render_settings["Bubble VFX"]['checkbox'].isChecked())
                                   )

        logger.info('Number of Threads: %s' % len(cmd_threads))
        self.checkIfReadyToSubmit(add=False, total=len(cmd_threads))
        self.thread_pool.startBatch(cmd_threads)
        #self.thread_pool.signals.finished.connect(submitCmdsFromFile)
        print("<<<<<<<<<<<<<< FINISHED WITH SUBMITTING >>>>>>>>>>>>>>>>>")

    def checkIfReadyToSubmit(self, add=True, total=None):
        if total:
            self.total = total
            self.current_count = 0
        if add:
            self.current_count = self.current_count + 1
        if self.total == self.current_count:
            self.total = -1
            self.current_count = 0
            self.submitCmdsFromFile()


    def submitCmdsFromFile(self):
        import Maya_Functions.file_util_functions as file_util

        folder = "C:/Temp/{project_name}/RenderSubmit/{submitCallID}".format(project_name=CC.project_name, submitCallID=self.submit_call_id) #{shotName}___{submitCallID}".format(project_name=CC.project_name,shotName=shotName,submitCallID=submitCallID)
        if os.path.exists(folder):
            for file in os.listdir(folder):
                filePath = os.path.join(folder, file).replace(os.sep, '/')
                cmd = file_util.loadJson(filePath)
                if cmd:
                    if cmd.startswith('"' + os.path.abspath(os.path.join(os.environ["RR_Root"], 'bin/win64/rrSubmitterconsole.exe')).replace(os.sep, '/').replace('//', os.sep + os.sep) + '"'):
                        self.rf.runRoyalRenderCmd(cmd)
                        os.remove(filePath)
                else:
                    logger.error("GOT ERROR! in %s" % filePath)
            os.rmdir(folder)
        else:
            logger.error("Submit folder does not exist: %s" % folder)
        # #cmd_file = "C:/Temp/{project_name}/{project_name}_SubmitCmds.txt".format(project_name=CC.project_name)
        # if os.path.isfile(cmd_file):
        #     with open(cmd_file, 'r') as open_file:
        #         for l in open_file.readlines():
        #             if l and l.startswith("%RR_Root%/bin/win64/rrSubmitterconsole.exe"):
        #                 self.rf.runRoyalRenderCmd(l)


    def SetShotFromList(self, shot): #setting info dict and shot specific variables
        file_name = shot.text()
        self.info_dict["episode_name"] = file_name.split("_")[0]
        self.info_dict["seq_name"] = file_name.split("_")[1]
        self.info_dict["shot_name"] = file_name.split("_")[2]
        self.shot_name = file_name
        self.shot_path = CC.get_shot_path(**self.info_dict) #cfg_util.CreatePathFromDict(cfg.project_paths["shot_path"],self.info_dict)
        # self.shot_path = "%s/Film/%s/%s_%s/%s/" % (self.base_path, self.ep, self.ep, self.seq, self.shot_name)


    def doubleSkyCheck(self):
        if len(cmds.ls(type='VRaySky')) > 1:
            popup = Popup(self, 'Double Sky Alert')
            _string = '\nCurrently ' + str(len(cmds.ls(type='VRaySky'))) + ' VRaySky nodes in the scene\n'
            popupLayout = QtWidgets.QVBoxLayout()
            topLabel = QtWidgets.QLabel(_string)
            topLabel.setStyleSheet('''QLabel { font: bold 14px; }''')
            popupLayout.addWidget(topLabel)
            popupLayout.addStretch(1)
            popup.setLayout(popupLayout)
            popup.show()


    def fileCheck(self, auto=False):
        shots = []
        if in_maya:
            filepath = cmds.file(q=True, sn=True)
            if filepath[-9:] == '_Light.ma' or auto == False:
                info_dict = CC.util.ComparePartOfPath(filepath, CC.get_shot_light_file())
                if info_dict:
                    shots.append(
                        {
                            'name': '{episode}_{seq}_{shot}'.format(episode=info_dict['episode_name'],
                                                                    seq=info_dict['seq_name'],
                                                                    shot=info_dict['shot_name']),
                            'workFile': CC.get_shot_anim_path(**info_dict),
                            'publishFile': CC.get_AnimScene(**info_dict)
                        }
                    )
        else:

            selected_list = self.shot_list.selectedItems()
            for selected in selected_list:
                #TODO Too hardcoded?
                info_dict = {
                    'episode_name': selected.text()[:3],
                    'seq_name': selected.text()[4:9],
                    'shot_name': selected.text()[10:]
                }

                shots.append(
                    {
                        'name': selected.text(),
                        'workFile': CC.get_shot_anim_path(**info_dict),
                        'publishFile': CC.get_AnimScene(**info_dict)
                    }
                )

        if auto:
            if not shots:
                return None

        from Maya_Functions.file_util_functions import publishOutdated
        popup = Popup(self, 'Check Files')
        popupLayout = QtWidgets.QVBoxLayout()

        if in_maya:
            topLabel = QtWidgets.QLabel('Could not find current shot.')
        else:
            topLabel = QtWidgets.QLabel('Currently no shots selected.')

        popupLayout.addWidget(topLabel)

        if shots:
            labels = []
            for shot in shots:
                if in_maya:
                    topLabel.setText('Animation seems up to date.')
                else:
                    topLabel.setText('All animation in selected files seems up to date.')

                if os.path.exists(shot['workFile']) and os.path.exists(shot['publishFile']):
                    outdated = publishOutdated(shot['workFile'], shot['publishFile'])
                    if outdated != False:
                        days = outdated.days
                        seconds = outdated.seconds
                        hours = seconds//3600
                        hours = hours + days * 24
                        minutes = (seconds // 60) % 60
                        labelText = shot['name'] + ' - ' + str(hours) + 'h ' + str(minutes) + 'm'
                        labels.append(QtWidgets.QLabel(labelText))

            if labels:
                topLabel.setText('The following shots may have outdated animation:')
                for label in labels:
                    label.setStyleSheet('''QLabel { font: 12px; }''')
                    popupLayout.addWidget(label)
            elif auto == True:
                return None

        topLabel.setStyleSheet('''QLabel { font: bold 14px; }''')
        popupLayout.addStretch(1)
        popup.setLayout(popupLayout)
        popup.show()

    def checkDefaultRenderLayerError(self):
        #TODO DOES NOT WORK. Had a file it didn't pop up in :/
        if in_maya:
            filepath = cmds.file(q=True, sn=True)
            if filepath:
                if filepath.endswith('_Light.ma'):
                    badLayers = cmds.ls('DefaultRenderLayer*')
                    if badLayers:
                        popup = Popup(self, 'Warning')
                        popupLayout = QtWidgets.QVBoxLayout()
                        warningLabel = QtWidgets.QLabel('WARNING: Contact your local TD')
                        warningLabel.setStyleSheet('''QLabel { font: bold 14px; }''')
                        smallTextLabel = QtWidgets.QLabel('There is an issue with the DefaultRenderLayer')
                        popupLayout.addWidget(warningLabel)
                        popupLayout.addWidget(smallTextLabel)
                        popupLayout.addStretch(1)
                        popup.setLayout(popupLayout)
                        popup.show()


class RenderSubmitFunctions():
    def __init__(self, ui_widget=None):
        
        # if "maya_render" in CC.project_settings.keys():
	    #     render_type = CC.project_settings["maya_render"]
        # else:
	    #     render_type = "vray"
        
        # self.shot_name = ""
        # self.shot_path = ""
        self.preset_name = ""
        self.aov_name = ""
        self.rs_name = ""
        self.ui_widget = ui_widget
        if in_maya:
            #initialize vray
            vray_util.setCurrentRenderer(renderer=render_type)


    def renderableCallback(self, message_type, plug, other_plug, client_data):
        if self.ui_widget.render_settings["Render Layers"]['checkbox'].isChecked():
            if not message_type & om.MNodeMessage.kAttributeSet:
                return

            if "renderable" in plug.name():
                if self.ui_widget:
                    self.ui_widget.layerLabelUpdate()

    def updateRenderableCallbacks(self, callbackJobs):
        if self.ui_widget.render_settings["Render Layers"]['checkbox'].isChecked():
            return_list = []
            layers = self.getActiveRenderLayers()
            for layer in layers:
                if layer == 'masterLayer':
                    layer = 'defaultRenderLayer'
                else:
                    layer = 'rs_' + layer
                if layer not in callbackJobs.keys():
                    selection = om.MSelectionList()
                    selection.add(layer)
                    m_obj = om.MObject()
                    selection.getDependNode(0, m_obj)
                    return_list.append((layer, om.MNodeMessage.addAttributeChangedCallback(m_obj, self.renderableCallback)))
            return return_list

    def loadUnloadedChildren(self):
        import Maya_Functions.ref_util_functions as ref_util
        ref_util.loadChildRefs()

    def getActiveRenderLayers(self):
        layersToRender = []
        renderLayers = (cmds.ls(type='renderLayer'))
        for renderLayer in renderLayers:
            if renderLayer[:3] == 'rs_':
                if cmds.getAttr(renderLayer + '.renderable'):
                    layersToRender.append(renderLayer[3:])

            elif renderLayer == 'defaultRenderLayer':
                if cmds.getAttr(renderLayer + '.renderable'):
                    layersToRender.append('masterLayer')
        return layersToRender

    def CreatePropOIDSet(self):
        import Maya_Functions.set_util_functions as set_util
        if not CC.OID_set_rules == "":
            set_util.CreateOIDSet(object_type="Prop", set_name="Props28OID", OID=28,use_force=False)
            #delete old set
            if cmds.objExists("Props22OID"):
                cmds.delete("Props22OID")
            try:
                import OIDManager
                OM = OIDManager.OID_Functions()
                if OM.SetAssetDictFromScene():
                    OM.DefineObjectsForScene()
                return True
            except Exception as e:
                logger.info("Can't set OID sets from rules. SOMETHING IS BROKEN! Check rule dict")
                return False

        # select_all_props = UF.FindAssetTypeInScene("Prop")
        # my_set = "Props22OID"
        # UF.CreateVrayObjectSet(my_set, select_all_props,False)
        # UF.SetOIDonObjectSet(my_set, 22)


    def SetInfoDict(self,ep_name=None,seq_name=None,shot_name=None):
        self.info_dict = {}
        self.info_dict["episode_name"]=ep_name
        self.info_dict["seq_name"] = seq_name
        self.info_dict["shot_name"] = shot_name

    def RenderOverscan(self, overscan=True, shot=None):
        # cur_camera = self.
        if shot:
            camera_name = "Anim:%s_Cam" % shot
            camera_name = cmds.listRelatives(camera_name, type="camera")[0]
            if overscan:
                cmds.setAttr("%s.cameraScale" % camera_name, 1.1)
                # width = cmds.getAttr("vraySettings.width")
                # height = cmds.getAttr("vraySettings.height")
                width = 1920
                height = 1080

                cmds.setAttr("vraySettings.width", width * 1.1)
                cmds.setAttr("vraySettings.height", height * 1.1)
            else:
                cmds.setAttr("%s.cameraScale" % camera_name, 1)
        else:
            logger.info("Can't Find Shot So can't find a camera")


    # def SubmitSteps(self):
    #     # self.PickPreset()
    #     self.ApplyRenderSettings(rs_name, exr_check)
    #     self.ImportAOVs(aov_file)
    #     self.SetRenderPath(shot_path, ep_seq_shot, preset_name)
    #     self.SetRenderCam(shot)
    #     self.SetRenderRange()
    #     self.SetAttrOnCam(shot)

    # TODO add check box for exr multi part on-off. And add that to be saved with the preset.
    def SetRenderPath(self, info_dict=None, preset_name=None, only_bg=None,render_layer=None):
        if only_bg:
            preset_name = "%s_OnlyBG" % preset_name
        # destination = "%s/passes/%s/%s_%s_#" % (shot_path, preset_name, ep_seq_shot, preset_name)
        
        
        if render_type == 'vray':
        
            if info_dict:
                info_dict["render_prefix"] = preset_name
                render_folder,render_filename = os.path.split(CC.get_shot_passes_folder(**info_dict)) #cfg_util.CreatePathFromDict(cfg.project_paths["shot_passes_folder"],info_dict)
            
                if render_layer:
                    destination = "%s/<layer>/%s<layer>#" % (render_folder,render_filename)
                else:
                    destination = "%s#" % CC.get_shot_passes_folder(**info_dict)
                cmds.setAttr("vraySettings.fileNamePrefix", destination, type="string")
                logger.info("Render path set to: %s" % destination)
            cmds.setAttr("vraySettings.imageFormatStr", "exr (multichannel)", type="string")
            cmds.setAttr("vraySettings.fileNamePadding", 5)
            cmds.setAttr("vraySettings.dontSaveImage", 1)
            cmds.setAttr("vraySettings.globopt_render_viewport_subdivision", 0)
            cmds.setAttr("defaultRenderGlobals.periodInExt", 0)

        if render_type == 'arnold':
            
            if info_dict:
                info_dict["render_prefix"] = preset_name
                print(preset_name)
                render_folder,render_filename = os.path.split(CC.get_shot_passes_folder(**info_dict)) #cfg_util.CreatePathFromDict(cfg.project_paths["shot_passes_folder"],info_dict)
            
                if render_layer:
                    destination = "%s/<layer>/%s<layer>#" % (render_folder,render_filename)
                else:
                    destination = "%s#" % CC.get_shot_passes_folder(**info_dict)
                
                cmds.setAttr("defaultRenderGlobals.imageFilePrefix", destination, type="string")
                logger.info("Render path set to: %s" % destination)
                
                cmds.setAttr("defaultArnoldDriver.multipart", 1)
                cmds.setAttr("defaultArnoldDriver.mergeAOVs", 1)
                cmds.setAttr("defaultArnoldDriver.preserveLayerName", 1)
                
    def SetRenderCam(self, shot):
        if shot != "":
            camera_name = "Anim:%s_Cam" % shot
            camera_name = cmds.listRelatives(camera_name, type="camera")[0]
            cams = cmds.ls(type="camera")
            for cam in cams:
                if camera_name == cam:
                    cmds.setAttr("%s.renderable" % cam, 1)
                    logger.info("Set %s to be the render cam" % camera_name)
                else:
                    cmds.setAttr("%s.renderable" % cam, 0)

    def SetRenderRange(self):
        range_start = cmds.playbackOptions(q=True, minTime=True)
        range_end = cmds.playbackOptions(q=True, maxTime=True)

        # if len(cmds.sequenceManager(lsh=True)) = 1:
            # range_start = cmds.shot(cmds.sequenceManager(lsh=True)[0], st=True)
            # range_end = cmds.shot(cmds.sequenceManager(lsh=True)[0], et=True)
        if render_type == 'vray':
            cmds.setAttr("vraySettings.animType", 1)
            cmds.setAttr("vraySettings.animBatchOnly", 1)
            cmds.setAttr("vraySettings.animFrames", "", type="string")
        elif render_type == 'arnold':
            mel.eval('setMayaSoftwareFrameExt(3,0)') # Choose naming convention (set "Frame/Animation ext")
        
        cmds.setAttr("defaultRenderGlobals.startFrame", range_start)
        cmds.setAttr("defaultRenderGlobals.endFrame", range_end)
        

    def ClearAOVs(self):
        aovs = cmds.ls(type="VRayRenderElement")
        for a in aovs:
            cmds.delete(a)
        aov_sets = cmds.ls(type="VRayRenderElementSet")
        for a in aov_sets:
            cmds.delete(a)

    def ImportAOVs(self, aov_file): #Clear old aovs and import new ones
        self.ClearAOVs()
        if not aov_file == "None":
            if os.path.exists(aov_file):
                print("Found it! %s" % aov_file)
            with open(aov_file, 'r') as aov_file:
                aovs = json.load(aov_file)

            self.CreateRenderElement(aovs["vray"]["renderElements"])
            vray_util.generateOIDandMID()
            # self.CheckForMissingOIDAOV()
            
    def ImportAOVsArnold(self, aov_file):
        aovs = cmds.ls(type="aiAOV")
        cmds.delete(aovs)
        data = file_util.loadJson(aov_file)
        for key in ('drivers', 'filters'):
            data['arnold'][key] = []
        arnold_aovs.decode(data, 0)

    def CreateVRayDirt(self, AOV_name): # Create DirtTexture and connect it to AO if possible.
        if not cmds.objExists("AO_VRayDirt"):
            cmds.shadingNode("VRayDirt", asTexture=True, n="AO_VRayDirt")
        cmds.connectAttr("%s.outColor" % "AO_VRayDirt", "%s.vray_texture_extratex" % AOV_name, f=True)

    def CreateRenderElement(self, re): #Create aov from json aov dict
        for elem in re:
            name = elem.keys()
            attrs = elem.values()[0]
            class_type = attrs["%s.vrayClassType" % name[0]]

            obj = mel.eval("vrayAddRenderElement %s" % class_type)

            for key in attrs.keys():
                cur_value = attrs[key]
                c_key = key.split(".")[1]
                c_attr = "%s.%s" % (obj, c_key)
                c_type = cmds.getAttr(c_attr, type=True)
                if isinstance(cur_value, list):
                    cmds.setAttr(c_attr, attrs[key][0], attrs[key][1], attrs[key][2], type="float3")
                else:
                    if c_type == "string":
                        cmds.setAttr(c_attr, attrs[key], type=c_type)
                    elif c_type == "message":
                        pass
                    else:
                        cmds.setAttr(c_attr, attrs[key])
            if name[0] == "AO":
                self.CreateVRayDirt(obj)
            if name[0] == "Sky_Full":
                self.ConnectSkyToAOV(obj)
            if name[0] == "Z_No_Filter":
                self.ConnectWithZPlanes(z_el=obj)
            if name[0] == "Z_depth":
                self.ConnectWithZPlanes(z_el=obj)
            cmds.rename(obj, name)

    def ConnectWithZPlanes(self,z_el):
        logger.info("Connecting with %s" % z_el)
        import LightHelper as LH
        LF = LH.LightFunctions()
        LF.ReconnectZplanesToVray(z_element=z_el)

    def ConnectSkyToAOV(self,sky_aov):
        """
        connects the vray sky to the extra sky texture.
        :param sky_aov:
        :return:
        """
        cur_sky = cmds.ls(type="VRaySky")
        if cur_sky:
            cmds.connectAttr("%s.outColor" % cur_sky[0], "%s.vray_texture_extratex" % sky_aov, f=True)

    def SetPhysicalAttrOnCam(self, shot):
        if not shot=="" and shot:
            camera_name = "Anim:%s_Cam" % shot
        else:
            cur_p = cmds.getPanel(withFocus=True)
            camera_name = None
            try:
                camera_name = cmds.modelPanel(cur_p, q=True, cam=True)
            except:
                print("Pick the panel to chose camera")
        if camera_name:
            cam_shape = cmds.listRelatives(camera_name, shapes=True)[0]
            mel.eval('vray addAttributesFromGroup "%s" "vray_cameraPhysical" 1' % cam_shape)
            cmds.setAttr("%s.vrayCameraPhysicalFNumber" % cam_shape, 10)
            cmds.setAttr("%s.centerOfInterest" % cam_shape, 50)
            cmds.select(cam_shape, r=True)
            logger.info("Setting physical attr on cam")

    def CheckOffBGOverride(self):
        bg_attr = "vraySettings.cam_envtexBg"
        if cmds.connectionInfo(bg_attr, id=True):
            cur_con = cmds.connectionInfo(bg_attr, sfd=True)
            cmds.disconnectAttr(cur_con, bg_attr)
        cmds.setAttr(bg_attr,0,0,0,type="double3")
        try:
            if cmds.ls("::*ForLight_Sphere"):
               for elm in cmds.ls("::*ForLight_Sphere"):
                   cmds.setAttr("%s.visibility" % elm, 0)
        except:
            logger.error("Couldn't hide the ForLight_Sphere")

    def OverrideConnectionsOnOff(self, on_off, orr_dict):
        logger.debug("Override Connections %s" % on_off)
        override_list = ["vraySettings.cam_envtexBg", "vraySettings.cam_envtexGi", "vraySettings.cam_envtexReflect",
                         "vraySettings.cam_envtexRefract", "vraySettings.cam_environmentVolume"]
        if not on_off:
            for oa in override_list:
                if cmds.connectionInfo(oa, id=True):
                    cur_con = cmds.connectionInfo(oa, sfd=True)
                    orr_dict[oa] = cur_con
                    cmds.disconnectAttr(cur_con, oa)
            return orr_dict
        else:
            for cur in orr_dict.keys():
                # print("Connecting %s - %s" % (orr_dict[cur],cur) )
                cmds.connectAttr(orr_dict[cur], cur, f=True)
            orr_dict.clear()
            return orr_dict

    def ExportCam(self,shot, shot_path, ep_seq_shot):
        from Maya_Functions.publish_util_functions import ExportBakedCamera
        ExportBakedCamera(shot, shot_path, ep_seq_shot)


    def ExportCamMayaPy(self, shot_path=None, shot_name=None, shot=None):
        # TODO Paths are hardcoded a bit, we could pull some of this out and use the config class instead
        current_file = "%s/02_Light/%s_Light.ma" % (shot_path, shot_name)
        script_content = """import maya.standalone
    maya.standalone.initialize('python')
    import maya.cmds as cmds
    import subprocess
    import Maya_Functions.publish_util_functions as pub_util
    cmds.file('%s', open=True,f=True)
    shot_path = '%s'
    shot_name = '%s'
    shot = '%s'
    pub_util.ExportBakedCamera(shot, shot_path, shot_name)
    cmds.quit(f=True)
    """ % (current_file, shot_path, shot_name, shot)
        script_content = ";".join(script_content.split("\n"))
        base_command = 'mayapy.exe -c "%s"' % (script_content)
        logger.debug(base_command)
        subprocess.Popen(base_command, shell=False, universal_newlines=True,env=runtime.getRuntimeEnvFromConfig(CC))
        # c_p = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE)
        # stdout = c_p.communicate()[0]
        # print("Saving Render File:\n%s" % stdout)
        # print("-------------SAVING DONE--------------")

    def ApplyRenderSettings(self, rs_name=None, exr_check=True, bg_off=False, overscan=False,sphere_render=False,shot=None):
        logger.debug("Apply Render Settings from render-submit")
        orr_dict = {}
        self.OverrideConnectionsOnOff(False, orr_dict)
        prefs.loadUserPreset("%s" % (rs_name).split(".")[0])
        if exr_check:
            cmds.setAttr("vraySettings.imgOpt_exr_multiPart", 1)
        else:
            cmds.setAttr("vraySettings.imgOpt_exr_multiPart", 0)
        # Set the pre and post scripts to nothing if no yeti plugin is needed. This is to avoid crashing in royal render when yeti is not loaded but it tries to run the prerender script.
        if not "pgYetiMaya" in cmds.pluginInfo(q=True, pluginsInUse=True):
            cmds.setAttr("defaultRenderGlobals.preMel","",type="string") #Should get the string and remove anything with pgYeti splitting with ";" to avoid removing other scripts
            cmds.setAttr("defaultRenderGlobals.postMel", "", type="string") #Should get the string and remove anything with pgYeti splitting with ";" to avoid removing other scripts
        else:
            cmds.setAttr("defaultRenderGlobals.preMel", "pgYetiPreRender; catch(`pgYetiVRayPreRender`)", type="string")
            cmds.setAttr("defaultRenderGlobals.postMel", "catch(`pgYetiVRayPostRender`)", type="string")
        self.OverrideConnectionsOnOff(True, orr_dict)
        # if bg_off:
        #     self.CheckOffBGOverride()
        self.RenderOverscan(overscan=overscan,shot=shot)
        if sphere_render:
            self.SphereRenderSetup()

    def SphereRenderSetup(self):
        """
        This is meant to try to re-connect volume spheres to the vray-settings.
        Not completed, it only works if it can find a volume sphere + a sphere-fade set in the scene.
        :return:
        """
        cmds.setAttr("vraySettings.cam_environmentVolumeOn", 1)
        #Check if there is anything connected to the volume-render attribute
        #if not, find all the spherevolumes in scene and connect the first one.

        if not cmds.listConnections("vraySettings.cam_environmentVolume"):
            fade_volumes = cmds.ls(type="VRaySphereFadeVolume")
            if fade_volumes:
                cmds.defaultNavigation(connectToExisting=True, source=fade_volumes[0],
                                       destination='vraySettings.cam_environmentVolume', f=True)
            else:

                sphere_fades = cmds.ls(type="VRaySphereFade")
                # if sphere_fades:
                #     import Maya_Functions.vray_util_functions as vray_util
                #     set_volume = vray_util.CreateVraySphereFadeVolume()
                #     if set_volume:
                #         for sf in sphere_fades:
                #             cmds.connect("%s.message" % set_volume, "%s.settings" % sf, f=True)
                #         cmds.defaultNavigation(connectToExisting=True, source=set_volume,
                #                                destination='vraySettings.cam_environmentVolume', f=True)

    def ImportRenderSettings(self):  # Import automatically when opening rendersubmit?
        logger.info("Importing Render Settings from Project")

        if in_maya:
            maya_local = os.getenv("MAYA_APP_DIR")
            preset_path = "%s/Presets/" % maya_local  #
        else:
            username = getpass.getuser()
            preset_path = "C:/Users/%s/Documents/maya/Presets/" % username
            # preset_path = "C:/Users/%s/OneDrive/Documents/maya/Presets/" % username #Local testing path

        if not os.path.exists(preset_path):
            os.mkdir(preset_path)
        import_path = CC.get_render_presets()#cfg_util.CreatePathFromDict(cfg.project_paths["render_presets"])# import_path = "P:/930382_Kiwi&Strit_2/Production/Pipeline/RenderSettings_Presets/"
        content = os.listdir(import_path)
        for con in content:
            if con.endswith(".json"):
                con_path = "%s/%s" % (import_path, con)
                preset_copy_path = "%s/%s" % (preset_path, con)
                # print("Copying %s to %s" % (con_path, preset_copy_path))
                copyfile(con_path, preset_copy_path)


    def RefCheck(self):  # TODO Needs to go down through ref structure instead of only the top level references
        refs = cmds.file(q=True, r=True)
        for c_ref in refs:
            # print("Checking Ref: %s" % c_ref)
            is_load = cmds.referenceQuery(c_ref, isLoaded=True)
            if not is_load:
                cmds.warning("Canceling Submit! Found a unloaded reference: %s" % c_ref)
                return False
        return True

    def bubbleVFX(self):
        #check if set exists
        #main render, set active, sky override refraction texture black
        #bg render, set disabled, sky override connected
        pass

    def buildCryptoAttr(self):
        import cryptoAttributes
        cryptoAttributes.cryptoAttrCheck()

    def runCryptoMatteSetup(self, c_prefix=None, info_dict={}):
        info_dict["render_prefix"] = c_prefix
        crypto_render_scene = CC.get_shot_crypto_render_file(**info_dict)
        render_file = CC.get_shot_render_path(**info_dict)
        # render_foldername, render_filename = os.path.split(CC.get_shot_passes_folder(**info_dict))
        # render_foldername = render_foldername + "/Crypto/"
        # render_filename = render_filename + "Crypto_#"
        # render_output_path = render_foldername + render_filename
        info_dict["render_prefix"] = "%s_Crypto" % c_prefix
        render_output_path = CC.get_shot_passes_folder(**info_dict)
        logger.debug('INFO DICT: ' + str(info_dict))
        logger.debug('render_file: ' + str(render_file))
        logger.debug('render_output_path: ' + str(render_output_path))
        info_dict["render_prefix"] = c_prefix
        script_content = """import maya.standalone
    maya.standalone.initialize('python')
    import maya.cmds as cmds
    import Maya_Functions.delete_and_clean_up_functions as del_util
    import Maya_Functions.file_util_functions as file_util
    import Maya_Functions.vray_util_functions as vray_util
    cmds.file('{render_file}', open=True, f=True)
    del_util.DeleteUnknown()
    file_util.PrepareForSave('{crypto_render_scene}', ma=True)
    vray_util.createCryptomatteScene()
    cmds.setAttr('vraySettings.fileNamePrefix', '{render_output_path}', type='string')
    cmds.setAttr('vraySettings.imgOpt_exr_multiPart', 0)
    print('Now saving file')
    cmds.file(save=True)
    cmds.quit(f=True)
    """.format(render_file=render_file, crypto_render_scene=crypto_render_scene, render_output_path=render_output_path)
        script_content = ";".join(script_content.split("\n"))
        base_command = 'mayapy.exe -c "%s"' % (script_content)
        logger.debug(base_command)
        save_proc = subprocess.Popen(base_command, shell=False, universal_newlines=True,env=runtime.getRuntimeEnvFromConfig(CC))
        save_proc.wait()
        # c_p = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE)
        # stdout = c_p.communicate()[0]
        # print("Saving Render File:\n%s" % stdout)
        # print("-------------SAVING DONE--------------")


    def runCryptoMatteSetupOutsideMaya(self, c_prefix=None, info_dict={}):
        info_dict["render_prefix"] = c_prefix
        crypto_render_scene = CC.get_shot_crypto_render_file(**info_dict)
        render_file = CC.get_shot_render_path(**info_dict)
        info_dict["render_prefix"] = "%s_Crypto" % c_prefix
        render_output_path = CC.get_shot_passes_folder(**info_dict)
        logger.debug('INFO DICT: ' + str(info_dict))
        logger.debug('render_file: ' + str(render_file))
        logger.debug('render_output_path: ' + str(render_output_path))
        import Maya_Functions.delete_and_clean_up_functions as del_util
        import Maya_Functions.file_util_functions as file_util
        import Maya_Functions.vray_util_functions as vray_util
        del_util.DeleteUnknown()
        file_util.PrepareForSave(crypto_render_scene, ma=True)
        vray_util.createCryptomatteScene()
        cmds.setAttr('vraySettings.fileNamePrefix', render_output_path, type='string')
        cmds.setAttr('vraySettings.imgOpt_exr_multiPart', 0)
        return info_dict["render_prefix"]


    def SaveRenderFile(self, onlybg=False, c_prefix=None, current_file=None, info_dict={}, render_layer=None, bubbles=False):
        if not current_file:
            current_file = CC.get_shot_light_file(**info_dict) #cfg_util.CreatePathFromDict(cfg.project_paths["shot_light_file"],info_dict)
        if onlybg:  # Check if we need to run OnlyBg in cleanup.
            c_prefix = "%s_OnlyBG" % c_prefix #c_prefix = "OnlyBG"
        info_dict["render_prefix"] = c_prefix
        render_file = CC.get_shot_render_path(**info_dict) #cfg_util.CreatePathFromDict(cfg.project_paths["shot_render_path"],info_dict)
        script_content = """import maya.standalone
	maya.standalone.initialize('python')
	import maya.cmds as cmds
	import subprocess
	from RenderSubmit import RenderSubmitFunctions
    from Maya_Functions.submit_to_deadline import submit
	RSF = RenderSubmitFunctions()
	cmds.file('{current_file}', open=True, f=True)
	RSF.SaveRenderFileFunc(render_file='{render_file}', render_layer={render_layer}, only_bg={only_bg}, bubbles={bubbles})
	cmds.file(save=True)
    submit(priority={priority})
    cmds.quit(f=True)
	""".format(current_file=current_file, render_file=render_file, only_bg=onlybg, render_layer=render_layer, bubbles=bubbles, priority=self.ui_widget.priority_int.text())
        script_content = ";".join(script_content.split("\n"))
        base_command = 'mayapy.exe -c "%s"' % (script_content)
        logger.debug(base_command)
        
        save_proc = subprocess.Popen(base_command, shell=False, universal_newlines=True, env=runtime.getRuntimeEnvFromConfig(CC))
        save_proc.wait()
        # c_p = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE)
        # stdout = c_p.communicate()[0]
        # print("Saving Render File:\n%s" % stdout)
        # print("-------------SAVING DONE--------------")

    def runRoyalRenderCmd(self, rr_cmd=None):
        logger.warning(rr_cmd)
        rr_proc = subprocess.Popen(rr_cmd)
        rr_proc.wait()

    def SaveRenderFileFunc(self, render_file=None, render_layer=False, only_bg=False, bubbles=False):
        """
        just testing the clean up function for saving out the render file
        :return:
        """
        import Maya_Functions.delete_and_clean_up_functions as del_util
        import Maya_Functions.file_util_functions as file_util
        import Maya_Functions.ref_util_functions as ref_util
        import Maya_Functions.publish_util_functions as publish_util
        import Maya_Functions.general_util_functions as general_util
        logger.info("Running SaveRenderFile: %s" %(render_file))
        del_util.DeleteUnknown()
        file_util.PrepareForSave(render_file, ma=True)
        ref_util.ImportRefs()
        del_util.DeleteDisplayLayers()
        if not render_layer:
            del_util.DeleteRenderLayers()
        #del_util.DeleteUnusedNodes() # Deletes VRay Object Property Sets because it regards them as empty
        #del_util.RemoveArnold()
        del_util.RemoveYetiPlugin()
        general_util.reissue_uuids()
        if bubbles:
            logger.info("Trying to Enable Bubble VFX Set")
            if cmds.objExists("Bubble_VFX_Set"):
                cmds.setAttr("Bubble_VFX_Set.ignore", 0)
                bg_attr = "vraySettings.cam_envtexRefract"
                if cmds.connectionInfo(bg_attr, id=True):
                    cur_con = cmds.connectionInfo(bg_attr, sfd=True)
                    cmds.disconnectAttr(cur_con, bg_attr)
                cmds.setAttr(bg_attr, 0, 0, 0, type="double3")
        if only_bg:
            publish_util.OnlyBG()
        logger.info("Finished with saving render scene: %s" % render_file)
        

    def RenderSubmitInfo(self, c_prefix=None, onlybg=None, user_name=None,stepped=None, r_priority="50", overwrite=False,info_dict=None,project_name=None, render_layer=None, single_frame=None, crop_exr=1, render_file=None):
        if onlybg:
            c_prefix = "%s_OnlyBG" % c_prefix #c_prefix = "OnlyBG"
        info_dict["render_prefix"] = c_prefix
        if not render_file:
            render_file = CC.get_shot_render_path(**info_dict) #cfg_util.CreatePathFromDict(cfg.project_paths["shot_render_path"],info_dict) # "%s/04_Publish/%s_%s_Render.mb" % (shot_path, shot_name, c_prefix)
        if not project_name:
            project_name = CC.project_name
        project_path = CC.get_base_path()

        client_pool = "WS"
        user_name = user_name

        # overwrite = True
        render_cam = "Anim:%s_Cam" % info_dict["shot_name"]
        width = cmds.getAttr("vraySettings.width")
        height = cmds.getAttr("vraySettings.height")

        # range_start = int(cmds.getAttr("defaultRenderGlobals.startFrame"))
        # range_end = int(cmds.getAttr("defaultRenderGlobals.endFrame"))

        # set start and end time
        start = int(cmds.getAttr("defaultRenderGlobals.startFrame"))
        # if len(cmds.sequenceManager(lsh=True)) == 1:
        #     if range_start != range_end:
        #         start = cmds.shot(cmds.sequenceManager(lsh=True)[0], q=True, st=True)
        #         cmds.setAttr("defaultRenderGlobals.endFrame", range_end)

        # set end time
        if single_frame:
            end = start
        else:
            end = int(cmds.getAttr("defaultRenderGlobals.endFrame"))

        # output = "%s/passes/%s/%s_%s_####.exr" % (self.shot_path, self.preset_dd.currentText(), self.shot_name, self.preset_dd.currentText())
        output_folder,filename = os.path.split(CC.get_shot_passes_folder(**info_dict))  #"%s/passes/%s/" % (shot_path, c_prefix)
        if render_layer:
            output_folder = "%s/<layer>/" % output_folder
            filename = "%s<layer>" % filename
            #TODO Please fix the scene name if we start using layers.
        scene_name = filename
        filename = "%s####.exr" % filename

        # filename = "%s_%s_%s_%s_####.exr" % (info_dict["episode_name"],info_dict["seq_name"],info_dict["shot_name"], c_prefix) #"%s_%s_####.exr" % (shot_name, c_prefix) #"%s_%s_####.exr" % (shot_name, c_prefix)

        extension = ".exr"

        software = "maya"
        # render_software = "vray 5"
        # software_version = "2020.4"
        software_version = "2022.4"


        rr_submitter = '"' + os.path.abspath(os.path.join(os.environ["RR_Root"], 'bin/win64/rrSubmitterconsole.exe')).replace(os.sep, '/').replace('//', os.sep + os.sep) + '"'

        rr_cmd = "%s %s" % (rr_submitter, render_file)  # Set scene
        # FLAGS
        rr_cmd = '%s -NoAutoSceneRead' % (rr_cmd)  # set flag that so rr doesn't parse through maya scene
        if overwrite:
            rr_cmd = "%s -AutoDeleteEnabled" % (rr_cmd)  # set flag so rr deletes all files that it is suppose to render over

        # SCENE INFO
        rr_cmd = "%s -S %s" % (rr_cmd, software)  # set software
        # rr_cmd = "%s -R %s" % (rr_cmd, render_software)  # set render plugin
        rr_cmd = "%s -V %s" % (rr_cmd, software_version)  # set software version

        rr_cmd = "%s -SOS win" % (rr_cmd)  # set os
        rr_cmd = '%s -DB %s' % (rr_cmd, project_path)  # set project
        # -ImageDir \\Fileserver\Share\outDir -ImageFileName beauty. -ImageExtension .pic
        rr_cmd = "%s -ImageDir %s" % (rr_cmd, output_folder)  # set filename. Absolute path
        if render_layer:
            rr_cmd = "%s -Layer %s" % (rr_cmd, render_layer)  # set filename. Absolute path
        rr_cmd = "%s -IF %s" % (rr_cmd, filename)  # set filename. Absolute path
        rr_cmd = "%s -ImageExtension %s" % (rr_cmd, extension)  # set filename. Absolute path
        rr_cmd = "%s -C %s" % (rr_cmd, render_cam)  # set camera
        rr_cmd = "%s -IW %s" % (rr_cmd, width)  # set width
        rr_cmd = "%s -IH %s" % (rr_cmd, height)  # set height

        # rr_cmd = "%s -SLO %s" % (rr_cmd, c_prefix)  # set layer

        rr_cmd = "%s -SeqStart %s" % (rr_cmd, start)  # set start
        rr_cmd = "%s -SeqEnd %s" % (rr_cmd, end)  # set end
        rr_cmd = "%s -SeqStep %s" % (rr_cmd, stepped)  # set stepped

        # # Submitter flags:
        rr_cmd = '%s "CSCN=0~%s"' % (rr_cmd, scene_name)  # set custom scene name
        rr_cmd = '%s "CSQN=0~%s"' % (rr_cmd, info_dict["episode_name"])  # set ep
        rr_cmd = '%s "CSHN=0~%s"' % (rr_cmd, info_dict["seq_name"])  # set seq
        rr_cmd = '%s "CVN=0~%s"' % (rr_cmd, info_dict["shot_name"])  # set shot

        rr_cmd = '%s "CPN=0~%s"' % (rr_cmd, project_name)  # set project "nice" name
        rr_cmd = '%s "DCG=0~%s"' % (rr_cmd, client_pool)  # set client pool
        rr_cmd = '%s "UN=0~%s"' % (rr_cmd, user_name)  # set user name
        rr_cmd = '%s "Priority=1~%s"' % (rr_cmd,r_priority)  # set priority
        rr_cmd = '%s "CropEXR=0~%s"' % (rr_cmd,crop_exr)  # check off crop exr
        #Added custom video script to be used instead of small video that was default
        # PreviewGamma2.2=0~0
        rr_cmd = '%s "PreviewGamma2.2=1~1"' % (rr_cmd)  # set preview gamma correctly
        rr_cmd = '%s "PPCreateCustomVideo=1~1"' % (rr_cmd)  # create custom video 0/1 with gamma correction
        rr_cmd = '%s "PPCreateSmallVideo=1~0"' % (rr_cmd)  # create small video 0/1
        # if full_video:
        #rr_cmd = '%s "PPCreateCustomVideo=1~1"' % (rr_cmd)  # create small video 0/1
        #rr_cmd = '%s "PPCreateSmallVideo=1~0"' % (rr_cmd)  # create small video 0/1
        # rr_cmd = '%s "PPCreateFullVideo=1~%s"' % (rr_cmd, full_video)  # create full video 0/1
        # rr_cmd = '%s "PPCreateSmallVideo=1~%s"' % (rr_cmd, small_video)  # create small video 0/1
        rr_cmd = '%s "MaxFrameTime==1~200"' % (rr_cmd)  # Set the max time a client can spend on a job. This is to avoid having clients stuck on a job for hours.
        logger.info(rr_cmd)
        logger.info("Scene Submitted to RoyalRender!")
        return rr_cmd
    # subprocess.Popen(rr_cmd)

    # # def TestCall(self):
    #     self.submitOutsideMaya(current_file='P:/930383_KiwiStrit3/Production/Film/E08/E08_SQ030/E08_SQ030_SH080/02_Light/E08_SQ030_SH080_Light.ma',rs_name="KS_ColorA.json.json",exr_multi=True,only_bg=False,
    #                            aov_name="P:/930383_KiwiStrit3/Production/Pipeline/RenderSettings_Presets/AOV_KSA.json",prefix_name="ColorSphereA",bg_off=False,phys_cam=False,info_dict={'seq_name': 'SQ030', 'shot_name': 'SH080', 'episode_name': 'E08','render_prefix':'ColorSphereA'},
    #                            overscan=False,sphere_render=True,project_name="KiwiStrit3",
    #                            render_layer=None,user_name="Christian",stepped=1,r_prio=50,overwrite=False)

    def submitOutsideMaya(self, current_file, rs_name, exr_multi, only_bg, aov_name, prefix_name,
                          bg_off, phys_cam, info_dict, overscan, sphere_render, render_layer, crypto_render,
                          project_name, user_name, stepped, r_prio, overwrite, single_frame, submitCallID,bubbles):
        script_content = """import maya.standalone
        maya.standalone.initialize('python')
        import maya.cmds as cmds
        from RenderSubmit import RenderSubmitFunctions
        RSF = RenderSubmitFunctions()
        RSF.submitOutsideMayaFunc(current_file='{current_file}', rs_name='{rs_name}', exr_multi={exr_multi}, only_bg={only_bg}, aov_name='{aov_name}', prefix_name='{prefix_name}', bg_off={bg_off}, phys_cam={phys_cam}, info_dict={info_dict}, overscan={overscan}, sphere_render={sphere_render}, render_layer={render_layer}, crypto_render={crypto_render}, project_name='{project_name}', user_name='{user_name}', stepped={stepped}, r_prio={r_prio}, overwrite={overwrite}, single_frame={single_frame}, submitCallID='{submitCallID}',bubbles={bubbles})
        """.format(current_file=current_file,
                   rs_name=rs_name,
                   exr_multi=exr_multi,
                   only_bg=only_bg,
                   aov_name=aov_name,
                   prefix_name=prefix_name,
                   info_dict=info_dict,
                   user_name=user_name,
                   stepped=stepped,
                   r_prio=r_prio,
                   overwrite=overwrite,
                   bg_off=bg_off,
                   overscan=overscan,
                   sphere_render=sphere_render,
                   phys_cam=phys_cam,
                   render_layer=render_layer,
                   crypto_render=crypto_render,
                   project_name=project_name,
                   single_frame=single_frame,
                   submitCallID=submitCallID,bubbles=bubbles)
        script_content = ";".join(script_content.split("\n"))
        base_command = 'mayapy.exe -c "%s"' % (script_content)
        logger.info(base_command)
        c_p = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=runtime.getRuntimeEnvFromConfig(CC))
        print(c_p.communicate()[0])
        return True
        # info = c_p.communicate()
        # stderr = info[1]
        # stdout = info[0]
        # logger.debug("%s" % stdout)
        # logger.debug("%s" % stderr)
        # print("\nHERE IS INFO:\n%s" % info)


    def saveCmdInFile(self,cmd=None,clear=False, submitCallID='00000', shotName='shotName', suffix='suffix'):
        import os
        import Maya_Functions.file_util_functions as file_util
        threadID = file_util.generateID()
        cmd_file = "C:/Temp/{project_name}/RenderSubmit/{submitCallID}/{shotName}_{suffix}___{threadID}.json".format(project_name=CC.project_name,
                                                                                                                   submitCallID=submitCallID,
                                                                                                                   shotName=shotName,
                                                                                                                   suffix=suffix,
                                                                                                                   threadID=threadID)
        #cmd_file = "C:/Temp/{project_name}/{project_name}_SubmitCmds.txt".format(project_name=CC.project_name)
        cmd_folder = os.path.split(cmd_file)[0]
        if not os.path.exists(cmd_folder):
            file_util.createDirectory(cmd_folder)
        if clear and os.path.exists(cmd_file):
            os.remove(cmd_file)
        else:
            file_util.saveJson(cmd_file, cmd)
            #file_util.saveFile(save_location=cmd_file,save_info=cmd,overwrite=False)


    def submitOutsideMayaFunc(self, current_file, rs_name, exr_multi, only_bg, aov_name, prefix_name, bg_off, phys_cam,
                              info_dict, overscan, sphere_render, render_layer, crypto_render, project_name, user_name, stepped,
                              r_prio,overwrite,single_frame, submitCallID,bubbles):
        cmds.file(current_file, open=True,f=True, lrd='all')
        self.ImportRenderSettings()
        self.ApplyRenderSettings(rs_name, exr_multi, bg_off,overscan,sphere_render)
        if bg_off:
            self.CheckOffBGOverride()
        self.SetRenderRange()
        self.CreatePropOIDSet() 
        import cryptoAttributes
        cryptoAttributes.addOID(overwrite=False)
        self.ImportAOVs(aov_name)
        self.SetRenderPath(info_dict, prefix_name, only_bg)
        self.SetRenderCam(info_dict['shot_name'])
        if crypto_render:
            self.buildCryptoAttr()
        if phys_cam:
            self.SetPhysicalAttrOnCam(info_dict['shot_name'])
        render_file = CC.get_shot_render_path(**info_dict)
        self.SaveRenderFileFunc(render_file=render_file, only_bg=only_bg, render_layer=render_layer,bubbles=bubbles)
        cmds.file(save=True)
        logger.info("Render file ready: %s" % render_file)
        shotName = info_dict['episode_name'] + '_' + info_dict['seq_name'] + '_' + info_dict['shot_name']
        if render_layer and not only_bg:
            for current_layer in self.getActiveRenderLayers():
                layer_cmd = self.RenderSubmitInfo(prefix_name, only_bg, user_name, stepped, r_prio, overwrite,info_dict, project_name, current_layer, single_frame)
                self.saveCmdInFile(cmd=layer_cmd, submitCallID=submitCallID, shotName=shotName, suffix=prefix_name)
                logger.info("For Render-Layer: %s" % current_layer)
                logger.info(layer_cmd)
                only_bg = False
        else:
            my_cmd = self.RenderSubmitInfo(prefix_name, only_bg, user_name, stepped, r_prio, overwrite, info_dict,project_name, False, single_frame)
            self.saveCmdInFile(cmd=my_cmd, submitCallID=submitCallID, shotName=shotName, suffix=prefix_name)
            logger.info(my_cmd)

        if crypto_render and not only_bg:
            logger.info("Creating CryptoMatte Render scene")
            #Set all the info for render scene and return prefix name
            crypto_prefix_name = self.runCryptoMatteSetupOutsideMaya(prefix_name, info_dict)
            cmds.file(save=True)
            crypto_cmd = self.RenderSubmitInfo(crypto_prefix_name, only_bg, user_name, stepped, r_prio, overwrite, info_dict,
                                           project_name, False, single_frame,0)
            logger.info("Saving Cmd: %s" % crypto_cmd)
            self.saveCmdInFile(cmd=crypto_cmd, submitCallID=submitCallID, shotName=shotName, suffix=crypto_prefix_name)

        cmds.quit(f=True)



        # return my_cmd


        # my_cmd = self.RenderSubmitInfo(prefix_name, only_bg,user_name, stepped,r_prio, overwrite,info_dict,project_name,render_layer)
        # print('FINISHED With saving file')
        # self.runRoyalRenderCmd(my_cmd)

#TODO Fix when using render layers
#OLD AND MAYBE OUTDATED
def SubmitOutsideMaya(current_file, rs_name, exr_multi, only_bg, aov_name, prefix_name,
                      user_name, stepped, r_prio, overwrite,bg_off,phys_cam,info_dict,overscan,sphere_render,project_name,render_layer):

    if phys_cam:
        phys_cam = "rf.SetAttrOnCam(info_dict['shot_name'])"
    else:
        phys_cam = "print('Not applying Physical Camera Attr')"

    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import RenderSubmit
cmds.file('{current_file}', open=True,f=True, lrd='all')
rs_name = '{rs_name}'
exr_multi = {exr_multi}
only_bg = {only_bg}
aov_name = '{aov_name}'
prefix_name = '{prefix_name}'
info_dict = {brackets}
info_dict['episode_name'] = '{episode_name}'
info_dict['seq_name'] = '{seq_name}'
info_dict['shot_name'] = '{shot_name}'
user_name = '{user_name}'
stepped = '{stepped}'
r_prio = '{r_prio}'
overwrite = {overwrite}
bg_off = {bg_off}
overscan = {overscan}
sphere_render = {sphere_render}
render_layer = {render_layer}
project_name = '{project_name}'
rf = RenderSubmit.RenderSubmitFunctions()
rf.ImportRenderSettings()
rf.ApplyRenderSettings(rs_name, exr_multi, bg_off,overscan,sphere_render)
rf.SetRenderRange()
rf.ImportAOVs(aov_name)
rf.SetRenderPath(info_dict, prefix_name, only_bg)
rf.SetRenderCam(info_dict['shot_name'])
rf.CreatePropOIDSet()
{phys_cam}
cmds.file(save=True)
cmds.quit(f=True)
my_cmd = rf.RenderSubmitInfo(prefix_name, only_bg,user_name, stepped,r_prio, overwrite,info_dict,project_name,render_layer)
rf.SaveRenderFile(only_bg, prefix_name,None,info_dict,render_layer)
print('FINISHED With saving file')
rf.runRoyalRenderCmd(my_cmd)""".format(current_file=current_file, rs_name=rs_name, exr_multi=exr_multi, only_bg=only_bg, aov_name=aov_name,
                                                                         prefix_name=prefix_name, episode_name=info_dict["episode_name"],seq_name=info_dict["seq_name"],shot_name=info_dict["shot_name"],
                                                                         user_name=user_name, stepped=stepped, r_prio=r_prio, overwrite=overwrite, bg_off=bg_off,overscan=overscan,
                                                                         sphere_render=sphere_render,phys_cam=phys_cam,brackets="{}",render_layer=render_layer,project_name=project_name)
    script_content = ";".join(script_content.split("\n"))
    base_command = 'mayapy.exe -c "%s"' % (script_content)
    # print(base_command)
    # subprocess.Popen(base_command, shell=False, universal_newlines=True)
    logger.debug("Submitting File:\n")

    print(base_command)
    c_p = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE,env=runtime.getRuntimeEnvFromConfig(CC))
    stdout = c_p.communicate()[0]
    logger.debug("%s" % stdout)
    print("-------------Submitting DONE--------------")
    job_id = stdout.splitlines()[-2].split(" ")[-4]
    # print(job_id)
    return job_id

def _maya_main_window():
    # Return Maya's main window
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')


def Run():
    objectName = 'RenderSubmitDock'
    if not MayaDockable.dockableExists(objectName):
        reloadModules.clearModules(["Configs.ConfigUtil_Json",
                                    "OIDManager",
                                    "LightHelper",
                                    "Maya_Functions.ref_util_functions","Maya_Functions.vray_util_functions","getConfig"])
        MayaDockable.runDockable(objectName, 'Render Submit', MainWindow())

    # mainWin = MainWindow(parent=_maya_main_window())
    # mainWin.show()


class Popup(QtWidgets.QDialog):
    def __init__(self, parent=None, title='Popup'):
        super(Popup, self).__init__(parent)
        self.setWindowTitle(title)
        flags = self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint
        flags = flags | QtCore.Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)


if not in_maya:

    if __name__ == '__main__':
        import sys
        if not QtWidgets.QApplication.instance():
            app = QtWidgets.QApplication(sys.argv)
        else:
            app = QtWidgets.QApplication.instance()
        mainWin = MainWindow()

        # # mainWin.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        # # mainWin.setFixedSize(584, 662)
        # # mainWin.resize(584, 662)
        # # print(QtWidgets.qApp.topLevelWidgets())

        mainWin.show()

        sys.exit(app.exec_())
    # P:/tools/RoyalRender/bin/win64/rrSubmitterconsole.exe P:/_WFH_Projekter/930450_MiasMagicComicBook/Production//Film/E02/E02_SQ090/E02_SQ090_SH080//04_Publish/E02_SQ090_SH080_Color_Render.mb -NoAutoSceneRead -AutoDeleteEnabled -S maya -R vray -V 2019.2 -SOS win -DB P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/ -ImageDir P:/_WFH_Projekter/930450_MiasMagicComicBook/Production//Film/E02/E02_SQ090/E02_SQ090_SH080//passes/Color/ -IF E02_SQ090_SH080_Color_####.exr -ImageExtension .exr -C Anim:SH080_Cam -IW 1920 -IH 1080 -SeqStart 1 -SeqEnd 439 -SeqStep 1 "CSCN=0~E02" "CSHN=0~SQ090" "CVN=0~SH080" "CPN=0~MiasMagicComicBook" "DCG=0~WS" "UN=0~Christian"