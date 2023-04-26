### Sequence view ###
### A tool to create and work with sequence based scenes in maya ###

### Check if inside or outside maya
from PySide2 import QtWidgets, QtCore, QtGui

import Maya_Functions.anim_util_functions

try:
    import maya.cmds as cmds
    in_maya = True
    import maya.cmds as cmds
    import maya.mel as mel
    from queue import Queue

except:
    from PySide2 import QtWidgets, QtCore, QtGui
    in_maya = False
    from queue import Queue

from Log.CoboLoggers import getLogger, setFileLevel
logger = getLogger()
# setFileLevel(logger,0)

from runtimeEnv import getRuntimeEnvFromConfig

from getConfig import getConfigClass

CC = getConfigClass()

from runtimeEnv import getRuntimeEnvFromConfig
run_env = getRuntimeEnvFromConfig(config_class=CC)

print(run_env.keys())


import os
import shutil
import subprocess
import Maya_Functions.file_util_functions as file_util
import Maya_Functions.general_util_functions as gen_util
import Maya_Functions.anim_util_functions as anim_util
from datetime import datetime
# from threading import Thread
# from threading import activeCount
# import multiprocessing

# from Multiplicity import ThreadPool
from Multiplicity import ThreadPool2

from multiprocessing import cpu_count

if in_maya:
    import MayaDockable
    import reloadModules

#TODO HARDCODED PATHS -> Previs/Playblast/Animatic/Sound/ImageplaneStack
#TODO Make asset_info dict instead of self.ep and self.seq.

class MainWindow(QtWidgets.QWidget): ### Main UI and Functions
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setObjectName("SeqView")
        self.setWindowTitle("SeqView:")
        self.setWindowFlags(QtCore.Qt.Window)
        self.shot_link = {}
        self.onlyInt = QtGui.QIntValidator()
        self.pool = ThreadPool2.ThreadPool(maxThreadCount=None)
        #self.thread_pool = ThreadPool.ThreadPool()
        self.CreateWindow()

        # self.thread_pool.signals.progressbar_init.connect(self.progressBar.setMaximum)
        # self.thread_pool.signals.progressbar_value.connect(self.progressBar.setValue)
        # # self.thread_pool.signals.progressbar_value.connect(self.checkIfReadyToSubmit)

        self.focus_view = cmds.getPanel(withFocus=True)
        self.PoppulateShotList()
        self.PopulateAssetList()
        self.ep = ""
        self.seq = ""
        self.GuessEpisodeAndSequence()
        self.base_path = CC.get_film_path()
        self.template_folder = CC.get_template_path()
        self.seq_template_folder = "%s%s" % (self.template_folder,"/3D_SQ_PREVIS_Template_Folder/")
        self.shot_template_folder = "%s%s" % (self.template_folder,"/3D_Shot_Template/")

    def CreateWindow(self):
        #### LAYOUTS #####
        self.main_layout = QtWidgets.QVBoxLayout()
        # self.top_layout = QtWidgets.QVBoxLayout()
        self.top_layout = QtWidgets.QGridLayout()

        self.top_button_layout = QtWidgets.QHBoxLayout()
        self.top_previs_layout = QtWidgets.QVBoxLayout()
        self.top_edit_layout = QtWidgets.QVBoxLayout()


        self.shot_buttons_layout = QtWidgets.QVBoxLayout()
        self.asset_buttons_layout = QtWidgets.QVBoxLayout()

        self.list_layout = QtWidgets.QHBoxLayout()
        self.button_layout = QtWidgets.QHBoxLayout()

        #### widgets ####
        self.shot_list = QtWidgets.QListWidget()
        self.shot_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.asset_list = QtWidgets.QListWidget()
        self.asset_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)

        self.shot_list.itemDoubleClicked.connect(self.ShotDoubleClicked)
        # self.asset_list.itemDoubleClicked.connect(self.DoubleClickOnAsset)

        #CREATE A MENU BAR TO GET RID OF SOME OF THE BUTTON CLUTTER
        self.menu_bar = QtWidgets.QMenuBar()
        ## FILE / SCENE / SHOT MENU
        self.menu_previs = QtWidgets.QMenu("File Setup")
        self.menu_previs.setToolTipsVisible(True)
        self.menu_bar.addMenu(self.menu_previs)

        self.create_previs_menu = QtWidgets.QAction("Create Previs", self.menu_bar)
        self.create_previs_menu.triggered.connect(self.CreatePrevis)
        self.menu_previs.addAction(self.create_previs_menu)

        self.save_file_menu = QtWidgets.QAction("Save As Previs", self.menu_bar)
        self.save_file_menu.triggered.connect(self.PrevisSave)
        self.menu_previs.addAction(self.save_file_menu)

        self.menu_previs.addSeparator()

        self.save_shots_action = QtWidgets.QAction("Split Previs into Animation scenes", self.menu_bar)
        self.save_shots_action.setToolTip("Takes the selected shots and saves them out as animation scenes.\nRemoves any references that are not linked"
                                          " to the shot and moves the start time to 1.\nIt moves the animation keys to fit the start, but does not delete the keys from other shots")
        self.save_shots_action.triggered.connect(self.splitPrevisIntoAnimScenes)
        self.menu_previs.addAction(self.save_shots_action)

        self.menu_previs.addSeparator()

        self.cleanup_shot_action = QtWidgets.QAction("Clean Up Animation Scene", self.menu_bar)
        self.cleanup_shot_action.triggered.connect(self.CleanUpCall)
        self.menu_previs.addAction(self.cleanup_shot_action)

        self.menu_previs.addSeparator()

        self.save_shot_report_action = QtWidgets.QAction("Save Publish Report", self.menu_bar)
        self.save_shot_report_action.triggered.connect(self.makePrevizPublishReport)
        self.menu_previs.addAction(self.save_shot_report_action)

        ### EDIT MENU
        self.menu_edit = QtWidgets.QMenu("Edit Previs/Shots")
        self.menu_edit.setToolTipsVisible(True)
        self.menu_bar.addMenu(self.menu_edit)

        self.open_shot_folder_action = QtWidgets.QAction("Open Selected Shot Folder", self.menu_bar)
        self.open_shot_folder_action.triggered.connect(self.OpenShotFolder)
        self.menu_edit.addAction(self.open_shot_folder_action)

        self.menu_edit.addSeparator()

        self.check_previs_action = QtWidgets.QAction("Check New Edits", self.menu_bar)
        self.check_previs_action.triggered.connect(self.CreateEditCheck)
        self.menu_edit.addAction(self.check_previs_action)

        self.apply_edit_action = QtWidgets.QAction("Apply Edits", self.menu_bar)
        self.apply_edit_action.triggered.connect(self.ApplyEdits)
        self.menu_edit.addAction(self.apply_edit_action)

        self.delete_edit_shots_action = QtWidgets.QAction("Delete Old Edit Nodes", self.menu_bar)
        self.delete_edit_shots_action.triggered.connect(self.DeleteEditNodes)
        self.menu_edit.addAction(self.delete_edit_shots_action)

        self.menu_edit.addSeparator()

        self.split_shot_action = QtWidgets.QAction("Split Animation Scene into 2", self.menu_bar)
        self.split_shot_action.triggered.connect(self.SplitShot)
        self.split_shot_action.setToolTip("Pick Shot in list. Place time cursor at split location. Notify producers about new shot and changes to durations")
        self.menu_edit.addAction(self.split_shot_action)

        self.menu_edit.addSeparator()
        self.select_keys_action = QtWidgets.QAction("Select All Keys", self.menu_bar)
        self.select_keys_action.triggered.connect(self.SelectAllKeys)
        self.menu_edit.addAction(self.select_keys_action)

        self.menu_edit.addSeparator()
        self.unlock_geo_key_action = QtWidgets.QAction("Unlock/Lock Geo on Selected Asset", self.menu_bar)
        self.unlock_geo_key_action.triggered.connect(self.LockGeoGroup)
        self.menu_edit.addAction(self.unlock_geo_key_action)

        self.set_keys_on_cam_action = QtWidgets.QAction("Set start/end keys on Cams of selected shots", self.menu_bar)
        self.set_keys_on_cam_action.triggered.connect(self.SetKeysOnCamera)
        self.menu_edit.addAction(self.set_keys_on_cam_action)

        self.check_no_asset_key_action = QtWidgets.QAction("Check for shots with NO Asset linked", self.menu_bar)
        self.check_no_asset_key_action.triggered.connect(self.CheckForNoAssetLinks)
        self.menu_edit.addAction(self.check_no_asset_key_action)
        self.menu_edit.addSeparator()
        self.new_shot_window_action = QtWidgets.QAction("Open Window for making New Shots", self.menu_bar)
        self.new_shot_window_action.triggered.connect(self.CreateNewShotWindow)
        self.menu_edit.addAction(self.new_shot_window_action)


        ### PLAYBLAST MENU
        self.menu_playblast = QtWidgets.QMenu("Playblast")
        self.menu_bar.addMenu(self.menu_playblast)

        self.playblast_action = QtWidgets.QAction("Playblast Selected", self.menu_bar)
        self.playblast_action.triggered.connect(self.ShotsToPlayblast)
        self.menu_playblast.addAction(self.playblast_action)

        self.playblast_im_checkbox = QtWidgets.QAction("Imageplane On/Off", self.menu_bar)
        self.playblast_im_checkbox.setCheckable(True)
        self.menu_playblast.addAction(self.playblast_im_checkbox)

        self.playblast_skipRendering_checkbox = QtWidgets.QAction("floatCheck On/Off", self.menu_bar)
        self.playblast_skipRendering_checkbox.setCheckable(True)
        self.menu_playblast.addAction(self.playblast_skipRendering_checkbox)


        self.playblast_light_action = QtWidgets.QAction("PB Selected - But with viewport light", self.menu_bar)
        self.playblast_light_action.triggered.connect(self.ShotsToPlayblastWithLight)
        self.menu_playblast.addAction(self.playblast_light_action)

        self.playblast_stack_action = QtWidgets.QAction("PB Selected - as png stack", self.menu_bar)
        self.playblast_stack_action.triggered.connect(self.ShotsToPlayblastStacks)
        self.menu_playblast.addAction(self.playblast_stack_action)

        self.open_playblast_folder_action = QtWidgets.QAction("Open Playblast folder", self.menu_bar)
        self.open_playblast_folder_action.triggered.connect(self.OpenPlayblastFolder)
        self.menu_playblast.addAction(self.open_playblast_folder_action)

        self.main_layout.addWidget(self.menu_bar)


        ### BUTTONS ###
        self.update_button = QtWidgets.QPushButton("UPDATE")
        self.update_button.clicked.connect(self.Update)
        self.set_view = QtWidgets.QPushButton("Select Focus View")
        self.set_view.clicked.connect(self.SetFocusView)

        self.im_refresh = QtWidgets.QPushButton("Refresh ImagePlane")
        self.im_refresh.setToolTip("The AttributeEditor needs to be open for this to work")
        self.im_refresh.clicked.connect(self.ImagePlaneRefresh)

        self.im_toggle = QtWidgets.QPushButton("Toggle ImagePlane")
        self.im_toggle.clicked.connect(self.ImagePlaneToggle)

        #right layout
        self.link_asset = QtWidgets.QPushButton("Link Asset")
        self.link_asset.clicked.connect(lambda: self.AssetLinking(linking=True))
        self.unlink_asset = QtWidgets.QPushButton("Unlink Asset")
        self.unlink_asset.clicked.connect(lambda: self.AssetLinking(linking=False))

        #Add Lists
        self.list_layout.addWidget(self.shot_list)
        self.list_layout.addWidget(self.asset_list)

        #right
        self.asset_buttons_layout.addWidget(self.link_asset)
        self.asset_buttons_layout.addWidget(self.unlink_asset)
        #top grid

        self.top_layout.addWidget(self.update_button, 0, 0)
        self.top_layout.addWidget(self.set_view, 0, 1)

        self.top_layout.addWidget(self.im_refresh, 1, 0)
        self.top_layout.addWidget(self.im_toggle, 1, 1)

        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setMaximumWidth(300)
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progress_bar_label = QtWidgets.QLabel("")
        self.progress_bar_label.setMinimumHeight(5)
        self.progress_bar_label.setWordWrap(True)



        #Connect layouts
        self.main_layout.addLayout(self.top_layout)

        self.main_layout.addLayout(self.list_layout)
        self.main_layout.addLayout(self.button_layout)
        self.button_layout.addLayout(self.asset_buttons_layout)
        self.main_layout.addWidget(self.progressBar)
        self.setLayout(self.main_layout)

    def closeEvent(self, event):
        print("CLOSING SEQVIEW")
        QtGui.QPixmapCache.clear()
        # del self.thread_pool
        del self.pool
        # super(MainWindow, self).closeEvent(event)

    def CreateNewShotWindow(self):
        self.cn_window = QtWidgets.QDialog(parent=self)

        self.cn_layout = QtWidgets.QHBoxLayout()
        self.shot_name_field = QtWidgets.QLineEdit()
        self.shot_length_field = QtWidgets.QLineEdit()
        self.shot_length_field.setValidator(QtGui.QIntValidator())
        rx = QtCore.QRegExp("[0-9]\\d{2}")
        self.shot_validator = QtGui.QRegExpValidator(rx, self)
        self.shot_name_field.setValidator(self.shot_validator)
        self.shot_name_label = QtWidgets.QLabel("Shot Name: (###) ")
        self.shot_length_label = QtWidgets.QLabel("Shot Range: ")

        self.create_new_shot_bttn = QtWidgets.QPushButton("Create New Shot")
        self.create_new_shot_bttn.clicked.connect(self.CreateNewShot)
        self.cn_layout.addWidget(self.shot_name_label)
        self.cn_layout.addWidget(self.shot_name_field)
        self.cn_layout.addWidget(self.shot_length_label)
        self.cn_layout.addWidget(self.shot_length_field)
        self.cn_layout.addWidget(self.create_new_shot_bttn)
        self.cn_window.setLayout(self.cn_layout)
        self.cn_window.show()

    def SetKeysOnCamera(self):
        shots = self.ReturnSelectedShots()
        if shots:
            for shot in shots:
                shot_name = shot.text()
                shot_start = cmds.shot(shot_name, q=True, st=True)
                shot_duration = cmds.shot(shot_name, q=True, et=True) - shot_start
                c_cam = "%s_Cam" % shot_name
                c_cam_shape = "%s_CamShape" % shot_name
                if cmds.objExists(c_cam):
                    cmds.camera(c_cam_shape, e=True, lt=False)
                    cmds.currentTime(shot_start)
                    cmds.setKeyframe([c_cam,c_cam_shape], t=shot_start)
                    cmds.currentTime(shot_duration + shot_start)
                    cmds.setKeyframe([c_cam,c_cam_shape], t=shot_duration + shot_start)
                    # cmds.camera(c_cam_shape, e=True, lt=True)


    def CleanUpCall(self):
        cur_shot = self.ReturnSelectedShots(only_first=True)
        if cur_shot:
            cur_shot = cur_shot.text()
            file_name = cmds.file(q=True, sn=True, shn=True)

            if "Animation" in file_name:
                self.ep = file_name.split("_")[0]
                self.seq = file_name.split("_")[1]
                file_shot = file_name.split("_")[2]
                logger.info("Selected: %s - File: %s" %(cur_shot, file_shot))
                if cur_shot == file_shot:
                    Maya_Functions.anim_util_functions.CleanUpAnimationScene(cur_shot)
                else:
                    cmds.warning("Selected shot is not the same as the shot in filename!")
        else:
            cmds.warning("Please select the shot you want to clean up!")

    def Update(self):
        self.PoppulateShotList()
        self.PopulateAssetList()
        self.GuessEpisodeAndSequence()

    def PrevisSave(self):
        if self.ep == "":
            if not self.GetFileInput():
                return False
        save_path = "%s/%s/%s_%s/%s_%s_PREVIS/01_Maya/%s_%s_PREVIS.ma" % (self.base_path, self.ep, self.ep, self.seq, self.ep, self.seq, self.ep, self.seq)

        if os.path.exists(save_path):
            logger.info("File Already Exists!")
        else:
            buttonReply = QtWidgets.QMessageBox.question(self, 'Save here?', "%s" % save_path,
                                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
            if buttonReply == QtWidgets.QMessageBox.Yes:
                dir_path = ("/").join(save_path.split("/")[:-1])
                if not os.path.exists(dir_path):

                    seq_path = ("/").join(save_path.split("/")[:-3])
                    if not os.path.exists((seq_path)):
                        os.makedirs(seq_path)
                    new_folder_path = seq_path = ("/").join(save_path.split("/")[:-2])
                    shutil.copytree(self.seq_template_folder, new_folder_path)

                logger.info("Saving here: %s" % save_path)
                cmds.file(rename=save_path)
                cmds.file(type="mayaAscii")
                cmds.file(save=True, f=True)

    def LockGeoGroup(self):
        logger.debug("Trying to lock Geo_Group")
        # selected = self.asset_list.selectedItems()
        selected = self.ReturnSelectedAssets()
        if selected:
            for sel in selected:
                name = sel.text()
                geo_group = "%s:Geo_Group" % name
                if cmds.objExists(geo_group):
                    current = cmds.getAttr("%s.overrideEnabled" % geo_group)
                    if current == 0:
                        cmds.setAttr("%s.overrideEnabled" % geo_group, 1)
                    else:
                        cmds.setAttr("%s.overrideEnabled" % geo_group, 0)
                    # cmds.setAttr("%s.overrideDisplayType" % geo_group, 2)

    def GetFileInput(self):
        i, okPressed = QtWidgets.QInputDialog.getInt(self, "Set Episode #:", "Episode #:", 0, 0, 100, 10)
        if okPressed:
            cur_ep = i
            x, ok_seq = QtWidgets.QInputDialog.getInt(self, "Set Sequence #:", "Sequence #:", 0, 0, 100, 10)
            if ok_seq:
                self.ep = "E%s" % str(cur_ep).zfill(2)
                self.seq = "SQ%s" % str(int(x)*10).zfill(3)
                return True
        return False

    def CheckForNoAssetLinks(self):
        shot_list = cmds.ls(type="shot")
        to_return = ""
        for shot in shot_list:
            assets = gen_util.GetAssetsinShot(shot)
            if not assets:
                to_return = "%sNo assets linked to %s\n" %(to_return,shot)
        logger.info(to_return)

    def splitPrevisIntoAnimScenes(self):
        previs_file = cmds.file(q=True,sn=True)
        shot_list = []
        selected_shots = self.ReturnSelectedShots()
        if selected_shots:
            for ss in selected_shots:
                if gen_util.GetAssetsinShot(ss.text()):
                    shot_list.append(ss.text())
                else:
                    buttonReply = QtWidgets.QMessageBox.question(self, 'NO ASSET LINKED', "NO ASSET LINKED TO SHOT: %s. Skip shot?" % ss.text(),
                                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                                 QtWidgets.QMessageBox.No)
                    if buttonReply == QtWidgets.QMessageBox.No:
                        shot_list.append(ss.text())
                    else:
                        logger.info("Skipping %s. No asset linked to that shot!" % ss.text())
            orig_file = cmds.file(q=True, sn=True)
            to_clean_up = []
            new_file =False
            for shot_name in shot_list:
                #print(shot_name,)
                if not "_EDIT" in shot_name:
                    logger.debug('starting folder setup')
                    shot_folder = CC.get_shot_path(episode_name=self.ep,seq_name=self.seq,shot_name=shot_name)
                    if file_util.createFolderFromTemplate(destination=shot_folder):
                        shot_path = CC.get_shot_anim_path(episode_name=self.ep,seq_name=self.seq,shot_name=shot_name)
                        if not os.path.exists(shot_path):
                            logger.info("Creating %s!" % shot_name)
                            shutil.copy(previs_file,shot_path)
                            to_clean_up.append([shot_path, self.ep, self.seq, shot_name])
                        else:
                            logger.info("%s already exists, skipped creation!" % shot_name)
                    else:
                        logger.error("FAILED CREATING %s FOLDERS" % shot_name)
            # if(new_file):
            #     cmds.file(new=True,f=True)
            # proc_list = []
            logger.info("Here we go cleaning up!")
            # for pair in to_clean_up:
            #     c_cmd = CreateMayaPyCmd(pair[0], pair[1], pair[2], pair[3]) #Create commandline to run with mayapy
            #     proc_list.append(ThreadPool.Worker(func=self.runMayaPyCmd,my_cmd=c_cmd))

            self.pool.signals.finished.connect(self.deletePool)
            
            for pair in to_clean_up:
                print(pair)
                c_cmd = CreateMayaPyCmd(pair[0], pair[1], pair[2], pair[3])
                worker = ThreadPool2.Worker(self.runMayaPyCmd, c_cmd)
                self.pool.addWorker(worker)
                # self.pool.append(worker)
                
            #     logger.info("Now running Proc of: %s" % pair[1])
            #     proc_list.append([pair[1],c_cmd])
            # CreateProcQueue(proc_list) #Create a thread queue and work through it
            logger.info("Starting threadpool")
            self.pool.run()
            print('pool started :D')
            # self.thread_pool.startBatch(proc_list)

    def deletePool(self):
        self.pool.clear()
    
    def runMayaPyCmd(self, my_cmd):
        base_command = 'mayapy.exe -c "%s"' % (my_cmd)
        print(base_command)
        logger.info("Running: %s" % base_command)
        c_p = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE, env=getRuntimeEnvFromConfig(CC))
        my_out,my_err = c_p.communicate()
        if my_out:
            print(my_out)
            logger.info("Output: %s\n" %(my_out))
        if my_err:
            print(my_err)
            logger.info("Error: %s\n" % (my_err))
        return True

    def GuessEpisodeAndSequence(self):
        file_name = cmds.file(q=True, sn=True,shn=True)
        if "PREVIS" in file_name or "Animation" in file_name:
            self.ep = file_name.split("_")[0]
            self.seq = file_name.split("_")[1]
            self.setWindowTitle("SeqShot: %s_%s" % (self.ep, self.seq))
            logger.info("EP: %s - SEQ: %s" % (self.ep, self.seq))
            print(file_name)
            print(self.ep)
            print(self.seq)
            print("SeqShot: %s_%s" % (self.ep, self.seq))
        else:
            self.setWindowTitle("SuperSequenceShot: Unknown Episode")


    def SetFocusView(self):
        self.focus_view = cmds.getPanel(withFocus=True)
        cmds.sequenceManager(mp=self.focus_view)

    def ImagePlaneRefresh(self):
        self.cur_shot = self.ReturnSelectedShots(only_first=True)
        if self.cur_shot:
            cur_shots = self.GetAllItemsInWidget(self.shot_list)
            for cur_i in range(len(cur_shots)):
                cur_item = cur_shots[cur_i]
                if cur_item.text() == self.cur_shot.text():
                    if cur_i < len(cur_shots):
                        self.ShotDoubleClicked(cur_shots[cur_i])
                        cmds.select("%s_IMShape2" % cur_shots[cur_i].text(), r=True)
                        #add a step. like move a frame.
                        cur_time = cmds.currentTime(q=True)
                        cmds.currentTime(cur_time+1)
                        next_shot = cur_i+1
                        if next_shot == len(cur_shots):
                            next_shot = 0
            self.shot_list.setCurrentRow(next_shot)

    def ImagePlaneToggle(self):
        shot_list = self.shot_list.selectedItems()

        for shot in shot_list:
            shot_name = "%s_IMShape2" % shot.text()

            if cmds.getAttr("%s.alphaGain" % shot_name) == 1:
                cmds.setAttr("%s.alphaGain" % shot_name, 0.45)
            elif cmds.getAttr("%s.alphaGain" % shot_name) == 0.45:
                cmds.setAttr("%s.alphaGain" % shot_name, 0)
            elif cmds.getAttr("%s.alphaGain" % shot_name) == 0:
                cmds.setAttr("%s.alphaGain" % shot_name, 1)
            else:
                cmds.setAttr("%s.alphaGain" % shot_name, 0)

    def GetPrevisTextInput(self):

        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', self.base_path, "Text Files (*.txt)")
        my_text = fname[0]
        if my_text != "":
            return my_text
        else:
            return False

    def SelectAllKeys(self):
        anim_keys = cmds.ls(type=["animCurveTA", "animCurveTU", "animCurveTL"])
        cmds.select(anim_keys, r=True)

    def CreatePrevis(self): #FUNCTION TO CREATE SHOT BASED ON TEXT LIST AND IMPORTING SOUND AND ANIMATIC
        cmds.currentUnit(time='pal')
        # get shot_list from text file
        idx = 0
        #cur_path = "P:/tools/_Scripts/Development_Maya/E01_SQ020.txt"
        # cur_path = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E01/E01_SQ020/E01_SQ020_PREVIS/03_Output/Shot_List.txt"
        cur_path = self.GetPrevisTextInput()
        self.ep = (cur_path.split("/")[-1]).split("_")[0]
        self.seq = ((cur_path.split("/")[-1]).split("_")[1]).split(".")[0]
        logger.info("EP: %s and SQ: %s" % (self.ep,self.seq))
        if cur_path: #Open file to read shot list and shot lengths
            file = open(cur_path, "r")
            file_lines = file.readlines()
            file.close()

            shot_list = file_lines
            logger.info(shot_list)


            maya_time = 0
            sequence_time = 0
            buffer_time = 50
            #Go through list of each shot and create a shot node and set sound and animatic for that shot
            for shot in shot_list:
                if not shot == '\r\n': #empty line
                    logger.info(shot)
                    shot = shot.split(",")
                    name = shot[0]
                    if not "SOUND" in name:
                        range = int(shot[1])
                        anim_util.CreateShotNode(name,range, maya_time, sequence_time, self.ep, self.seq,None)
                        maya_time = maya_time + range + buffer_time
                        sequence_time = sequence_time + range + buffer_time
                        logger.info("name: %s, range: %s" % (name, range))
            self.PoppulateShotList()



    def GetInteger(self):
        i, okPressed = QtWidgets.QInputDialog.getInt(self, "Choose Shot number", "Number between 1-9:", 5, 0, 100, 1)
        if okPressed:
            return i
        else:
            return False

    def SplitShot(self):
        cur_shot = self.ReturnSelectedShots(only_first=True)
        if cur_shot:
            cur_shot = cur_shot.text()
            new_shot_number = self.GetInteger()
            if not new_shot_number:
                logger.info("Have to pick a number!")
                return False
            if new_shot_number < 10:
                new_shot = "%s%s" % (cur_shot[:-1], new_shot_number)  # new name for shot
                if cmds.objExists(new_shot):
                    cmds.warning("THAT SHOT ALREADY EXISTS.. pick another number!")
                    return False
            else:
                logger.warning("invalid shot number (valid shot numbers are: 1-9)")

            cur_shot_et = cmds.shot(cur_shot, q=True, et=True)
            cur_shot_cam = cmds.shot(cur_shot, q=True, cc=True)
            cur_shot_im = "%s_IMShape2" % cur_shot
            if cmds.objExists(cur_shot_im):
                cmds.setAttr("%s.frameOut" % cur_shot_im, cmds.currentTime(q=True) - 1)

            new_shot_st = cmds.currentTime(q=True) - 1
            new_shot_et = cur_shot_et
            new_shot_duration = new_shot_et - new_shot_st

            cmds.shot(cur_shot, e=True, et=new_shot_st)
            print(cmds.shot(cur_shot, e=True, et=new_shot_st))

            # # define the name of the directory to be created
            # temp_path = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E03/E03_SQ090/E03_SQ090_%s" % new_shot
            # print temp_path
            # try:
            #     os.mkdir(temp_path)
            # except OSError:
            #     print ("Creation of the directory %s failed" % temp_path)
            # else:
            #     print ("Successfully created the directory %s " % temp_path)

            anim_util.CreateShotNode(new_shot, new_shot_duration, new_shot_st, new_shot_st, self.ep, self.seq, cur_shot_cam)
            # shot_list_items = self.GetAllItemsInWidget(self.shot_list)
            # for i in range(len(shot_list_items)):
            #     cur_item_selected = shot_list_items[i]
            #     if cur_item_selected.text() == cur_shot:
            #         self.ShotDoubleClicked(shot_list_items[i])
            self.Update()
            self.ShotDoubleClicked(item=None, shot_name=new_shot)

    def CreateEditCheck(self):
        cmds.currentUnit(time='pal')
        # get shot_list from text file
        idx = 0
        #cur_path = "P:/tools/_Scripts/Development_Maya/E01_SQ020.txt"
        # cur_path = "P:/930382_Kiwi&Strit_2/Production/Film/E01/E01_SQ020/E01_SQ020_PREVIS/03_Output/Shot_List.txt"
        cur_path = self.GetPrevisTextInput()
        self.ep = (cur_path.split("/")[-1]).split("_")[0]
        self.seq = ((cur_path.split("/")[-1]).split("_")[1]).split(".")[0]
        logger.info("EP: %s and SQ: %s" % (self.ep,self.seq))
        if cur_path:
            file = open(cur_path, "r")
            file_lines = file.readlines()
            file.close()

            shot_list = file_lines

            maya_time = 0
            sequence_time = 0
            buffer_time = 50
            for shot in shot_list:
                shot = shot.split(",")
                name = shot[0]
                if not "SOUND" in name:
                    range = int(shot[1])
                    shot_name = "%s_EDIT" % name
                    self.CreateEditShotNode(shot_name, name, range, maya_time, sequence_time, self.ep, self.seq)
                    maya_time = maya_time + range + buffer_time
                    sequence_time = sequence_time + range + buffer_time
                    logger.info("name: %s, range: %s" % (shot_name, range))
            self.PoppulateShotList()

    def CreateNewShot(self,episode_name=None,seq_name=None,shot_name=None):
        episode = 60
        seq_name = 10
        shot_name = self.shot_name_field.text()
        shot_length = self.shot_length_field.text()
        if shot_name and shot_length:
            if len(shot_name) == 3:
                print(shot_name,shot_length)
                # Check if shot_name exists in scene and in the folder structure.
                # Check where the shot should be placed. It should be after all the other shot nodes I think. With a buffer of 50 frames.
                # else build it:
                # self.CreateShotFolder(shot_name=shot_name)
                # self.CreateShotNode(name=shot_name,range=20,ep=episode_name,seq=seq_name)
                # pass


    def CreateEditShotNode(self, name,orig_name, range, start, seq_start, ep, seq):
        start_time = start + 1
        end_time = start + range
        seq_start_time = seq_start + 1

        # do the thing
        if cmds.objExists(orig_name):
            seq_start_time = cmds.shot(orig_name, q=True, sst=True)
            duration = end_time - start_time
            start_time = cmds.shot(orig_name, q=True, st=True)
            end_time = start_time + duration

        new_shot = cmds.shot(name, st=start_time, et=end_time, sst=seq_start_time)

    def DeleteEditNodes(self):
        shots = cmds.ls(type="shot")
        for shot in shots:
            if "_EDIT" in shot:
                cmds.delete(shot)

    def ApplyEdits(self):
        shots = cmds.ls(type="shot")
        orig_shots = []
        edit_shots = []
        for shot in shots:
            if "_EDIT" in shot:
                edit_shots.append(shot)
            else:
                orig_shots.append(shot)
        orig_shots = sorted(orig_shots)
        edit_shots = sorted(edit_shots)

        for i in range(len(edit_shots)):
            edit_shot = edit_shots[i]
            orig_shot = edit_shot.split("_EDIT")[0]

            if cmds.objExists(orig_shot):
                logger.info("EDIT: %s -> ORIG: %s" % (edit_shot, orig_shot))
                o_i = orig_shots.index(orig_shot)
                e_shot_start = cmds.shot(edit_shot, q=True, st=True)
                e_shot_end = cmds.shot(edit_shot, q=True, et=True)
                e_shot_duration = (e_shot_end - e_shot_start) + 1
                e_seq_start = cmds.shot(edit_shot, q=True, sst=True)

                o_shot_start = cmds.shot(orig_shot, q=True, st=True)
                o_shot_duration = (cmds.shot(orig_shot, q=True, et=True) - o_shot_start) + 1


                move_amount = e_shot_duration-o_shot_duration
                move_start = cmds.shot(orig_shot, q=True, et=True) + 25
                move_end = 3000
                logger.info("%s has %s amount to move" % (edit_shot, move_amount))
                if move_amount > 0:
                    #
                    self.MoveShot(orig_shots[o_i+1:], move_start, move_end, move_amount)
                    # cmds.shot(orig_shot, e=True, et=e_shot_end)
                shot_end_again = cmds.shot(orig_shot, q=True, et=True)
                logger.info("Setting %s's endFarme to %s" %(orig_shot, shot_end_again+move_amount))
                cmds.setAttr("%s.endFrame" % orig_shot, shot_end_again+move_amount)
            else:
                #TRY TO CREATE A NEW SHOT
                e_shot_start = cmds.shot(edit_shot, q=True, st=True)
                e_shot_end = cmds.shot(edit_shot, q=True, et=True)
                e_shot_duration = (e_shot_end - e_shot_start) + 1
                # e_seq_start = cmds.shot(edit_shot, q=True, sst=True)

                prev_shot = edit_shots[i-1].split("_EDIT")[0]
                prev_end = 1
                if cmds.objExists(prev_shot):
                    prev_end = cmds.shot(prev_shot, q=True, et=True) + 25

                    move_amount = e_shot_duration + 50
                    move_end = 3000
                    logger.info("%s has %s amount to move" % (prev_end, move_amount))
                    if move_amount > 0:
                        self.MoveShot(orig_shots[i:], prev_end, move_end, move_amount)


                new_start = prev_end + 25
                self.CreateShotNode(orig_shot,e_shot_duration,new_start,new_start,self.ep, self.seq,None)
                logger.info("New Shot: %s" % edit_shot)



    def MoveShot(self, shot_list, start, end, amount):
        logger.info("Moving shots: %s - From: %s  - This Much:%s" %(shot_list,start,amount))
        cmds.undoInfo(cn="MovingShots", ock=True)
        Maya_Functions.anim_util_functions.MoveAnimation(start, end, amount)

        for shot in shot_list[::-1]:
            c_st = cmds.shot(shot, q=True, st=True)
            c_et = cmds.shot(shot, q=True, et=True)

            # c_sst = cmds.shot(shot, q=True, sst=True)

            end_time = c_et + amount
            start_time = c_st + amount
            logger.info("Moving %s: From %s:%s to %s:%s" % (shot, c_st,c_et, start_time, end_time))

            # cmds.shot(shot, e=True, et=c_et + amount)
            # cmds.shot(shot, e=True, )
            cmds.setAttr("%s.startFrame" % shot, start_time)
            cmds.setAttr("%s.endFrame" % shot, end_time)
            cmds.setAttr("%s.sequenceStartFrame" % shot, start_time)

            # cmds.shot(shot, e=True, sst=start_time, set=end_time)
            # cmds.shot(shot, e=True, st=start_time, et=end_time)

            if cmds.objExists("%s_IMShape2" % shot):
                im = "%s_IMShape2" % shot
                cur_offset = (-1 * start_time)-1
                cmds.setAttr("%s.frameOffset" % im, cur_offset)
                cmds.setAttr("%s.frameIn" % im, start_time)
                cmds.setAttr("%s.frameOut" % im, end_time)
        cmds.undoInfo(cck=True)

    def GetAllItemsInWidget(self, cur_list):
        cur_items = []
        for x in range(cur_list.count()):
            cur_items.append(cur_list.item(x))
        return cur_items

    def OpenPlayblastFolder(self):
        if self.ep !="":
            seq_path = "%s/%s/%s_%s/" % (self.base_path, self.ep, self.ep, self.seq)
            _collect_folder = "%s/_Preview/" % (seq_path)
            if os.path.exists(_collect_folder):
                self.OpenFolder(_collect_folder)

    def OpenShotFolder(self):
        if self.ep !="":
            seq_path = "%s/%s/%s_%s/" % (self.base_path, self.ep, self.ep, self.seq)
            # _collect_folder = "%s/_Preview/" % (seq_path)
            selected = self.shot_list.selectedItems()
            if len(selected)>0:
                shot_name = selected[0].text()
                shot_folder = "%s/%s_%s_%s/" % (seq_path, self.ep,self.seq,shot_name)

                if os.path.exists(shot_folder):
                    self.OpenFolder(shot_folder)

    def OpenFolder(self,path):
        os.startfile(path)

    def ReturnSelectedShots(self,only_first=False):
        cur_items = self.shot_list.selectedItems()
        logger.debug(cur_items)
        if cur_items != []:
            if only_first:
                return cur_items[0]
            return cur_items
        logger.info("No Shots selected!")
        return False

    def ReturnSelectedAssets(self, only_first=False):
        cur_items = self.asset_list.selectedItems()
        if cur_items != []:
            if only_first:
                return cur_items[0]
            return cur_items
        logger.info("No assets selected!")
        return False

    def ShotsToPlayblastWithLight(self):
        cur_shots = self.shot_list.selectedItems()
        play_list = []
        for c in cur_shots:
            play_list.append(c.text())
        if not self.ep == "":
            self.PlayblastShots(self.ep, self.seq, play_list, True)

    def ShotsToPlayblast(self):
        self.GuessEpisodeAndSequence()
        cur_shots = self.shot_list.selectedItems()
        play_list = []
        for c in cur_shots:
            play_list.append(c.text())
        if not self.ep == "":
            self.PlayblastShots(self.ep,self.seq,play_list, False)

    def ShotsToPlayblastStacks(self):
        cur_shots = self.shot_list.selectedItems()
        play_list = []
        for c in cur_shots:
            play_list.append(c.text())
        if not self.ep == "":
            self.PlayblastShotsAsPNG(self.ep, self.seq, play_list)

    def PlayblastShotsAsPNG(self, _ep,_seq,shot_list):

        editor = cmds.modelPanel(self.focus_view, q=True, me=True)
        cmds.modelEditor(editor, e=True, allObjects=False)
        cmds.modelEditor(editor, e=True, sel=False)  #Don't show selected highlighted
        cmds.modelEditor(editor, e=True, pm=True)
        cmds.modelEditor(editor, e=True, ns=True)# show nurbsSurface
        cmds.modelEditor(editor, e=True, pi=True) #particle instance goes
        cmds.modelEditor(editor, e=True,pluginObjects=["gpuCacheDisplayFilter", 1]) #show gpu caches

        for _sh in shot_list:

            output_folder = "%s/preview_stack/" % CC.get_shot_path(episode_name=_ep,seq_name=_seq,shot_name=_sh)
            if not os.path.exists(output_folder):
                os.mkdir(output_folder)
            out_path = "%s%s_%s_%s_stack" % (output_folder,_ep,_seq,_sh)
            sh_start_time = cmds.shot(_sh, q=True, st=True)
            sh_end_time = cmds.shot(_sh, q=True, et=True)
            cmds.playbackOptions(minTime=sh_start_time, maxTime=sh_end_time)
            cmds.currentTime(sh_start_time)
            cmds.modelPanel(self.focus_view, edit=True, camera="%s_Cam" % _sh)
            c_cam = "%s_CamShape" % _sh
            save_GateMask = cmds.camera(c_cam, q=True, dgm=True)
            save_FilmGate = cmds.camera(c_cam, q=True, dfg=True)
            save_ResGate = cmds.camera(c_cam, q=True, dr=True)
            cmds.camera(c_cam, e=True, dgm=False)
            cmds.camera(c_cam, e=True, dfg=False)
            cmds.camera(c_cam, e=True, dr=False)
            cmds.camera(c_cam, e=True, ovr=1)
            cmds.playblast(f=out_path, fmt="image", epn=self.focus_view, c="png", cc=True,fo=True, os=True, qlt=100, orn=False, v=False, ifz=True, wh=[3840,2160], p=100)
# "P:/930440_Den_saerlige_mester/Pilot/Film/E01/E01_SQ030/E01_SQ030_SH090/preview_stack/E01_SQ030_SH090_stack"

        cmds.modelEditor(editor, e=True, allObjects=True)
        cmds.modelEditor(editor, e=True, sel=True)
        cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 0)


    def PlayblastShots(self,_ep, _seq, shot_list, light): #TODO Hardcoded playblast paths
        seq_path = "%s/%s/%s_%s/" % (self.base_path, _ep, _ep, _seq)
        _collect_folder = "%s/_Preview/" % (seq_path)
        if light:
            _collect_folder = "%s/_Preview/_LightDirections/" % (seq_path)
        if not os.path.exists(_collect_folder):
            os.mkdir(_collect_folder)

        # turn visibility on nurbcurves and camera off before playblast
        editor = cmds.modelPanel(self.focus_view, q=True, me=True)
        cmds.modelEditor(editor, e=True, allObjects=False)
        cmds.modelEditor(editor, e=True, sel=False)  #Don't show selected highlighted
        cmds.modelEditor(editor, e=True, pm=True)
        cmds.modelEditor(editor, e=True, ns=True)# show nurbsSurface
        cmds.modelEditor(editor, e=True, pi=True) #particle instance goes
        if self.playblast_im_checkbox.isChecked():
            cmds.modelEditor(editor, e=True,imp=True)
        cmds.modelEditor(editor, e=True,pluginObjects=["gpuCacheDisplayFilter", 1]) #show gpu caches
        #Turn off LOD visibilty of floatCheck objs
        off_list = cmds.ls("::*.vraySkipExport", long=True)
        if self.playblast_skipRendering_checkbox.isChecked():
            off_list = []
        for cur in off_list:
            cur_obj = cur.split(".")[0]
            cmds.setAttr("%s.lodVisibility" % cur_obj, 0)

        if light:
            cmds.modelEditor(editor, e=True, dl="all")
            cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 1)
            cmds.setAttr("hardwareRenderingGlobals.transparentShadow", 1)
        view = True
        if len(shot_list) > 1:
            view = False

        for _sh in shot_list:
            logger.info("Playblasting: %s -> %s_%s_%s" % (_collect_folder, _ep, _seq, _sh))
            pb_animatic = "%s/%s_%s_%s.mov" % (_collect_folder, _ep, _seq, _sh)
            
            createPlayblast = True
            useTempFileName = False
            logger.debug("Checking if %s preview is locked" % _sh)
            import Preview.file_util as fileUtil
            if os.path.exists(pb_animatic):
                if fileUtil.isFileLocked(pb_animatic):
                    from QtCustomWidgets import confirmPopupRetry
                    
                    for i in range(50):
                        result = confirmPopupRetry(self, title='File is locked', label="""The current playblast file is locked and cannot be overwritten.\nPlease check if you or anyone else have the file open.\nIf the problem persists, please contact your local TD.\n\nWould you like to playblast to a temporary file?""")
                        if result == 'Retry':
                            if not fileUtil.isFileLocked(pb_animatic):
                                break
                            
                        elif result == True:
                            import random
                            import string                   
                            pb_animatic = "%s/%s_%s_%s_%s.mov" % (_collect_folder, _ep, _seq, _sh, ''.join(random.choice(string.ascii_letters + '0123456789') for i in range(6)))
                            break
                        
                        elif result == False:
                            createPlayblast = False
                            break

            if createPlayblast:
                # if light:
                #     pb_animatic = "%s/_LightDirections/%s_%s_%s.mov" % (_collect_folder, _ep, _seq, _sh)
                # update timeline
                logger.debug("Getting camera and model panel in order for %s" % _sh)
                sh_start_time = cmds.shot(_sh, q=True, st=True)
                sh_end_time = cmds.shot(_sh, q=True, et=True)
                cmds.playbackOptions(minTime=sh_start_time, maxTime=sh_end_time)
                cmds.currentTime(sh_start_time)
                cmds.modelPanel(self.focus_view, edit=True, camera="%s_Cam" % _sh)

                #Set gatemask to FALSE!
                c_cam = "%s_CamShape" % _sh
                save_GateMask = cmds.camera(c_cam, q=True, dgm=True)
                save_FilmGate = cmds.camera(c_cam, q=True, dfg=True)
                save_ResGate = cmds.camera(c_cam, q=True, dr=True)
                cmds.camera(c_cam, e=True, dgm=False)
                cmds.camera(c_cam, e=True, dfg=False)
                cmds.camera(c_cam, e=True, dr=False)
                cmds.camera(c_cam, e=True, ovr=1)

                # update audio
                logger.debug("Checking sound for %s" % _sh)
                sh_audio_display = cmds.shot(_sh, q=True, aud=True)
                if sh_audio_display:
                    playBackSlider = mel.eval('$tmpVar=$gPlayBackSlider')
                    cmds.timeControl(playBackSlider, e=True, sound=sh_audio_display, displaySound=True)

                # Do the playblast for each shot here
                # cmds.playblast(f=pb_animatic, fmt="qt", s=sh_audio_display, epn=self.focus_view,c="H.264", cc=True, fo=True, os=True, qlt=100, orn=False, v=view, wh=[1280, 720],p=100)
                cmds.playblast(f=pb_animatic, fmt="qt", s=sh_audio_display, epn=self.focus_view, c="H.264", cc=True,
                            fo=True, os=True, qlt=100, orn=False, v=False, wh=[1280, 720], p=100)
                if os.path.exists(pb_animatic):
                    if self.SlateOnPlayblast(pb_animatic, _sh):
                        temp_path = "%s_Temp.mov" % pb_animatic.split(".")[0]
                        if os.path.exists(temp_path):
                            logger.info("renaming and removing preview_temp to preview ")
                            os.remove(pb_animatic)
                            os.rename(temp_path, pb_animatic)
                    if view:
                        os.startfile(pb_animatic)

                cmds.camera(c_cam, e=True, dgm=save_GateMask)
                if save_FilmGate:
                    cmds.camera(c_cam, e=True, ovr=1.3)
                cmds.camera(c_cam, e=True, dfg=save_FilmGate)
                cmds.camera(c_cam, e=True, dr=save_ResGate)
        #Set all to true.
        cmds.modelEditor(editor, e=True, allObjects=True)
        cmds.modelEditor(editor, e=True, sel=True)
        cmds.setAttr("hardwareRenderingGlobals.ssaoEnable", 0)
        #turn floatChecks back on
        for cur in off_list:
            cur_obj = cur.split(".")[0]
            cmds.setAttr("%s.lodVisibility" % cur_obj, 1)

        print('>> Done playblasting')


    def SlateOnPlayblast(self, playblast_path, shot_name):
        logger.info("Starting slate on %s" % shot_name)
        temp_path = "%s_Temp.mov" % playblast_path.split(".")[0]
        # os.rename(playblast_path, )
        title = '_'.join([self.ep, self.seq, shot_name])
        # slate_name = "%s_%s_%s" % (self.ep, self.seq, shot_name)
        #now = datetime.now()
        # dt_string = now.strftime("%d/%m/%Y %H.%M")
        from runInPython3 import runInPython3
        from Preview.general import getPreview
        #title = 'E01_SQ020_SH030'
        user = os.environ.get("BOM_USER")
        print(os.environ.keys())
        if not user:
            user = False
            print("NO USERS IN HERE")
        print(user)
        runInPython3(getPreview, str(title), type='anim', create=True, force=True, local=True, user=user, inputPath=str(playblast_path), outputPath=str(temp_path))
        logger.info("Created Slate on: %s" % shot_name)
        return True
    

    def HighlightAssets(self, asset_list):
        for x in range(self.asset_list.count()):
            if self.asset_list.item(x):
                if asset_list:
                    if self.asset_list.item(x).text() in asset_list:
                        self.asset_list.item(x).setSelected(True)
                    else:
                        self.asset_list.item(x).setSelected(False)
                else:
                    self.asset_list.item(x).setSelected(False)

    def ShotDoubleClicked(self, item=None, shot_name=None):
        # Print selected shot and what assets are linked to it
        if item:
            shot_clicked = item.text()
        elif shot_name:
            shot_clicked = shot_name
        # linked_assets = cmds.getAttr("%s.assetlinks" % shot_clicked)
        linked_assets = gen_util.GetAssetsinShot(shot_clicked)
        self.HighlightAssets(linked_assets)
        logger.info("Shot: " + shot_clicked + ", Linked assets: " + str(linked_assets) + "\n")
        cur_cam = shot_clicked + '_Cam'

        # Cycle through cameras
        # cmds.lookThru(cur_cam) # cycle through camera views
        cmds.modelPanel(self.focus_view, edit=True, camera=cur_cam)

        cams_in_scene = cmds.ls(type='camera')
        for cam in cams_in_scene:
            if cam == shot_clicked + "_CamShape":
                cmds.showHidden(cam)
            else:
                cmds.hide(cam)

        # Playback time range adjustments
        start_time = cmds.shot(shot_clicked, q=True, st=True)

        seq_start_time = cmds.shot(shot_clicked, q=True, sst=True)
        end_time = cmds.shot(shot_clicked, q=True, et=True)
        cmds.playbackOptions(minTime=start_time, maxTime=end_time)
        cmds.currentTime(start_time)

        # Change current time in Camera Sequencer
        cmds.sequenceManager(ct=seq_start_time)

        # change audio track based on shot
        cur_audiotrack = cmds.shot(shot_clicked, q=True, aud=True)

        if not cur_audiotrack:
            connections = cmds.listConnections(shot_clicked, d=True)
            for connection in connections:
                if connection.startswith('sequencer'):
                    items = cmds.listConnections(connection, source=True)
                    for item in items:
                        if item.startswith(str(self.ep) + '_' + str(self.seq) + '_' + shot_clicked):
                            cur_audiotrack = item
            if cur_audiotrack:
                try:
                    cmds.connectAttr(cur_audiotrack + '.message', shot_clicked + '.audio')
                except Exception as e:
                    logger.error(e)

        if cur_audiotrack:
            self.ReimportAudio(shot_clicked, cur_audiotrack)
            aPlayBackSliderPython = mel.eval('$tmpVar=$gPlayBackSlider')
            cmds.timeControl(aPlayBackSliderPython, e=True, sound=cur_audiotrack, displaySound=True)

        logger.info("Audio: %s" % cur_audiotrack)

    def ReimportAudio(self, new_shot, audioTrack):
        if cmds.objExists(new_shot):
            if cmds.getAttr("%s.frameCount" % audioTrack) == 0:
                logger.info("%s.wav not found in directory" % audioTrack)
                cmds.select(audioTrack, r=True)
                cmds.setAttr("%s.filename" % audioTrack, " ", type="string")
                cmds.setAttr("%s.filename" % audioTrack, "%s%s/%s_%s/%s_%s_%s/%s.wav" % (
                    self.base_path, self.ep, self.ep, self.seq, self.ep, self.seq, new_shot, audioTrack), type="string")

    def AssetLinking(self, linking=True,shots=None, assets=None): #Link Currently selected shots with currently selected assets
        if linking:
            logger.info("\nLinking!")
        else:
            logger.info("\nUN-Linking!")
        if not assets:
            assets = self.asset_list.selectedItems()
        if not shots:
            shots = self.shot_list.selectedItems()
        if len(shots) > 0 and len(assets) > 0:
            for shot_item in shots:
                cur_shot = shot_item.text()
                for asset_item in sorted(assets):
                    cur_asset = asset_item.text()
                    if linking:
                        asset_list = self.AddAssetLink(cur_shot,cur_asset)
                        to_add = (",").join(asset_list)
                        cmds.setAttr("%s.assetlinks" % cur_shot, to_add, type="string")
                        self.AssetLink(cur_shot, asset_list,1)
                    else:
                        asset_list = self.RemoveAssetLink(cur_shot,cur_asset)
                        if asset_list != []:
                            to_add = (",").join(asset_list)
                        else:
                            to_add = ""
                        cmds.setAttr("%s.assetlinks" % cur_shot, to_add, type="string")
                        self.AssetLink(cur_shot, [cur_asset],0)

        else:
            logger.info("Must have a shot and an asset selected")

    def AssetLink(self, shot_name, asset_list, on_off):
        start = cmds.shot(shot_name, q=True,st=True)
        end = cmds.shot(shot_name, q=True,et=True)

        org_time = cmds.currentTime(q=True)
        for asset in asset_list:
            self.SetVisibilityOnAssets(asset,on_off, start)
            self.SetVisibilityOnAssets(asset, 0, start-1)
            self.SetVisibilityOnAssets(asset, on_off, end)
            self.SetVisibilityOnAssets(asset, 0, end+1)
        # cmds.currentTime(org_time)
        cmds.currentTime(org_time, update=True)

    def AddAssetLink(self, shot_name, _asset_name):
        temp = cmds.getAttr("%s.assetlinks" % shot_name)
        if temp != None and temp != "":
            if "," in temp:
                temp = temp.split(',')  # convert to list so we can append
                for t in temp:
                    if t == _asset_name:
                        return sorted(temp)
                temp.append(_asset_name)  # add new asset
                temp = sorted(temp)
                return temp
            else:
                if temp == _asset_name:
                    return [temp]
                asset_list = sorted([temp, _asset_name])
                return asset_list
        else:
            return [_asset_name]

    def RemoveAssetLink(self, shot_name, _asset_name):
        temp = cmds.getAttr("%s.assetlinks" % shot_name)
        if temp != None and temp != "":
            if "," in temp:
                temp = temp.split(',')  # convert to list so we can append
                if _asset_name in temp:
                    temp.remove(_asset_name)  # add new asset
                temp = sorted(temp)
                return temp
                # cmds.setAttr("%s.assetlinks" % shot_name, (",").join(temp), type="string")  # convert back to string
            else:
                if temp == _asset_name:
                    return []
                else:
                    return [temp]
                    # cmds.setAttr("%s.assetlinks" % shot_name, "", type="string")  # convert back to string
        else:
            return []



    def PopulateAssetList(self): #fill the asset list
        cur_assets = self.GetAssetsInScene()
        self.asset_list.clear()
        self.asset_list.addItems(cur_assets)

    def PoppulateShotList(self):
        cur_shots = cmds.ls(type="shot")
        self.shot_list.clear()
        self.shot_list.addItems(cur_shots)


    def GetAssetsInScene(self):
        refs = cmds.file(q=True, reference=True)
        asset_list = []
        for ref in refs:
            if cmds.referenceQuery(ref, isLoaded=True):
                # node = cmds.referenceQuery(ref, rfn=True, topReference=True)
                # print("This is the ref: %s" % ref)
                cur = cmds.referenceQuery(ref, namespace=True, topReference=True, shortName=True)
                if cmds.objExists("%s:Root_Group" % cur):
                    asset_list.append(cur)
                    # top_group = "%s:Top_Group" % cur
        return asset_list

    def SetVisibilityOnAssets(self, asset, on_off, cur_time):
        asset_group = "%s:Root_Group" % asset
        # cmds.setAttr("%s.visibility" % asset_group, on_off)
        if cmds.objExists(asset_group):
            cmds.setKeyframe(asset_group, attribute='visibility', v=float(on_off),t=cur_time)

    def makePrevizPublishReport(self):
        """
        This function is meant to be a way to keep track of what assets are used in each scene.
        :return:
        """
        refs = cmds.file(q=True, reference=True)
        all_shots = cmds.ls(type="shot")

        for cur_shot in all_shots:
            shot_info_dict = {"episode_name":self.ep,"seq_name":self.seq,"shot_name":cur_shot}

            shot_content_dict = {}
            cur_shot_assets_paths = []
            shot_assets = gen_util.GetAssetsinShot(cur_shot)
            for ref in sorted(refs):
                cur = cmds.referenceQuery(ref, namespace=True, topReference=True, shortName=True)
                if cur in shot_assets:
                    if "{" in ref:
                        ref = ref.split("{")[0]
                    cur_shot_assets_paths.append(ref)
            shot_content_dict["previz_ref_paths"] = cur_shot_assets_paths
            import Maya_Functions.publish_util_functions as publish_util
            publish_util.savePublishReport(info_dict=shot_info_dict,content=shot_content_dict)



def _maya_main_window():
    """Return Maya's main window"""
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')

def Run(): ### Run command for maya
    objectName = 'SequenceViewDock'
    if not MayaDockable.dockableExists(objectName):
        MayaDockable.runDockable(objectName, 'Sequence Viewer', MainWindow())

    # cmds.currentUnit(time='pal')
    # mainWin = MainWindow(parent=_maya_main_window())
    # mainWin.show()



#TODO  creating procs! Clean up this a bit?

def PublishReport(info_dict):
    from Maya_Functions.publish_util_functions import readyPublishReport, savePublishReport
    content_dict = {}
    info_dict["publish_report_name"] = 'PrevizScene'
    readyPublishReport(info_dict=info_dict, current_dict=content_dict, ref=True, texture=False)
    savePublishReport(info_dict=info_dict, content=content_dict)

def CreateMayaPyCmd(shot_path, episode_name, seq_name, shot_name):
    send_dict = {'episode_name':episode_name,'seq_name':seq_name,'shot_name':shot_name}
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import SequenceView as SV
import Maya_Functions.anim_util_functions as anim_util
import sys
from Log.CoboLoggers import getLogger
logger = getLogger()
cmds.file('{shot_path}', open=True,f=True)
anim_util.CleanUpAnimationScene('{shot_name}')
SV.PublishReport({send_dict})
cmds.file(rename='{shot_path}')
cmds.file(type='mayaAscii')
cmds.file(save=True)
logger.info('{shot_name}: Saved. Clean-Up is finished')
cmds.quit(f=True)""".format(shot_path=shot_path, shot_name=shot_name,send_dict=send_dict)
    script_content = ";".join(script_content.split("\n"))
    base_command='mayapy.exe -c "%s"' % (script_content) #Not being run here, only for printing.
    # sys.stdout.write('{shot_name}: File Opened')
    # sys.stdout.write('{shot_name}: File Cleaned')
    logger.debug(base_command)
    return script_content


def ProcRun(shot_name, shot_cmd):
    base_command = 'mayapy.exe -c "%s"' % (shot_cmd)
    c_p = subprocess.Popen(base_command, shell=True, universal_newlines=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,env=getRuntimeEnvFromConfig(CC))
    logger.debug("%s:\n %s\n%s" % (shot_name, c_p.communicate()[0],c_p.communicate()[1]))

def ProcWorker(queue):
    for args in iter(queue.get, None):
        try:
            ProcRun(*args)
        except Exception as e:  # catch exceptions to avoid exiting the
            # thread prematurely
            # print('%r failed: %s' % (args, e,), file=sys.stderr)
            logger.debug('%s failed: %s' % (args, e))

def CreateProcQueue(cmd_list=None):
    # start threads
    cpu_total = multiprocessing.cpu_count()
    cpu_current = activeCount()
    logger.info("Total Process's: %s -> Using: %s" % (cpu_total, cpu_current))
    number_of_workers = int(int(cpu_total) - int(cpu_current) - 1)
    q = Queue()
    threads = [Thread(target=ProcWorker, args=(q,)) for _ in range(number_of_workers)]
    for t in threads:
        t.daemon = True  # threads die if the program dies
        t.start()
    # populate files
    if cmd_list:
        for c in cmd_list:
            q.put_nowait(c)

    for _ in threads: q.put_nowait(None)  # signal no more files
    for t in threads: t.join()  # wait for completion
    logger.info("Procs working on queue")


# def DeleteUnknown():
#     unknown = cmds.ls(type="unknown")
#     for un in unknown:
#         if cmds.objExists(un):
#             cmds.delete(un)







    # "import maya.standalone;maya.standalone.initialize('python');import maya.cmds as cmds;import SequenceView as SV;cmds.file('%s', open=True,f=True);SV.CleanUpAnimationScene('%s', '%s');cmds.quit(f=True)"