import os
import subprocess
import multiprocessing
import re
from PySide2 import QtWidgets, QtCore, QtGui
from threading import Thread, activeCount



from getConfig import getConfigClass
CC = getConfigClass()
from Log.CoboLoggers import getLogger
logger = getLogger()
from runtimeEnv import getRuntimeEnvFromConfig
# Check if the script is running inside Maya
try:
    import maya.cmds as cmds
    in_maya = True
except:
    in_maya = False


if in_maya:
    import maya.mel as mel
    from Queue import Queue
    import MayaDockable
    import reloadModules
    try:
        import YetiFunctions as YF
    except:
        pass
else:
    from queue import Queue


class PublishAnimScene():
    def __init__(self):

        self.base_path = CC.get_film_path()
        self.ep = ""
        self.seq = ""
        self.sequence_path = ""

    def GetSceneInfo(self):
        scene_path = cmds.file(q=True, sn=True)
        scene_name = cmds.file(q=True, sn=True, shn=True)
        self.info_dict = {}
        self.info_dict = CC.util.ComparePartOfPath(scene_path,CC.get_shot_anim_path(),self.info_dict)
        if self.info_dict:
            self.publish_path = CC.get_AnimScene(**self.info_dict) #cfg_util.CreatePathFromDict(cfg.ref_paths["AnimScene"], self.info_dict)
            self.light_path = CC.get_shot_light_file(**self.info_dict) #cfg_util.CreatePathFromDict(cfg.project_paths["shot_light_file"], self.info_dict)
            self.start = cmds.playbackOptions(q=True, minTime=True)
            self.end = cmds.playbackOptions(q=True, maxTime=True)
            return True
        else:
            print("NOT AN ANIMATION SCENE")
            return False

    def RunInMayaPy(self,yeti_check=True):
        if in_maya:
            print("In maya.. running")
            if self.GetSceneInfo():
                scene_path = cmds.file(q=True, sn=True)
                RunMayaPy(shot_path=scene_path, cache_yeti=yeti_check)
        else:
            print("maya not running.")

    # def DeleteDisplayLayers(self):  # Delete display layers
    #     cur_layers = cmds.ls(type="displayLayer")
    #     for lay in cur_layers:
    #         try:
    #             cmds.delete(lay)
    #         except:
    #             print("Can't delete %s. Needs to be removed in Ref" % lay)
    #
    # def removeUnloadedRefs(self):  # Removes unload refs. Does not work recursively.
    #     refs = cmds.file(q=True, r=True)
    #     for c_ref in refs:
    #         is_load = cmds.referenceQuery(c_ref, isLoaded=True)
    #         if not is_load:
    #             ref_file = cmds.referenceQuery(c_ref, f=True)
    #             # cmds.file(ref_file, rr=True, mergeNamespaceWithRoot=True)
    #             cmds.file(ref_file, rr=True)
    # set_key_on_dict= {"KarlA":{"L_wrist_switch_CTRL":}}
    def PublishScene(self,cache_yeti=True):  # Run through publish steps
        import Maya_Functions.delete_and_clean_up_functions as delete_util
        import Maya_Functions.ref_util_functions as ref_util
        import Maya_Functions.publish_util_functions as publish_util
        import Maya_Functions.asset_util_functions as asset_util
        import Maya_Functions.yeti_util_functions as yeti_util
        if self.GetSceneInfo():
            logger.info("Moving on to publishing")
            # rename the file to ref publish path.
            cmds.file(rename=self.publish_path)
            # do the things / clean up
            print("removing unloaded references")
            ref_util.RemoveUnloadedRefs()
            content_dict = {}
            from Maya_Functions.publish_util_functions import readyPublishReport, savePublishReport
            self.info_dict["publish_report_name"] = 'AnimScene'
            readyPublishReport(info_dict=self.info_dict, current_dict=content_dict, ref=True, texture=False)
            savePublishReport(info_dict=self.info_dict, content=content_dict)
            print("Changing refs to render")
            logger.info("Changing refs to render")
            ref_util.ChangeRefType()
            print("Deleting Image Planes")
            logger.info("Deleting Image Planes")
            delete_util.DeleteImagePlanes()
            print("Deleting LD Light")
            logger.info("Deleting LD Light")
            publish_util.DeleteLightDirection()
            print("Deleting ALL lights")
            logger.info("Deleting ALL lights")
            delete_util.deleteAllLights()
            logger.debug("Deleting Sun and Sky")
            delete_util.deleteSunAndSky()
            print("Delete Displaylayers")
            logger.info("Delete Displaylayers")
            delete_util.DeleteDisplayLayers()
            print("Remove visibility keys from asset root groups")
            logger.info("Remove visibility keys from asset root groups")
            asset_util.RemoveVisibilityKeys()
            print("Delete Project Specifics")
            logger.info("Delete Project Specifics")
            delete_util.cleanProjectUniques(project_name=CC.project_name, publish_step="AnimPublish")
            print("Deleting Unused Nodes")
            logger.info("Deleting Unused Nodes")
            delete_util.DeleteUnusedNodes()
            print("Deleting Unknown")
            logger.info("Deleting Unknown")
            delete_util.DeleteUnknown()
            print("Deleting keys on camera coi")
            logger.info("Deleting keys on camera coi")
            publish_util.DeleteKeyAndChangeCenter(self.info_dict["shot_name"])
            print('setting end key')
            logger.info('setting end key')
            publish_util.setVelocityEndKeys()
            # print("trying to cache no-flip arm constraints") #Removed to because it didn't work
            # publish_util.CacheAllArmConstraintsInScene()
            publish_util.ExportBakedCamera(self.info_dict["shot_name"],CC.get_shot_path(**self.info_dict),"%s_%s_%s" % (self.info_dict["episode_name"],self.info_dict["seq_name"],self.info_dict["shot_name"]))
            if cache_yeti:
                print("Caching Yeti")
                yeti_util.CacheYetiNode(selection=False,cache_folder=CC.get_shot_yeti_cache_path(**self.info_dict))
            else:
                print("Not caching yeti")
                yeti_util.CacheYetiNode(selection=False,cache_folder=CC.get_shot_yeti_cache_path(**self.info_dict),skip_caching=True)

            print("Saving")
            # Save scene.

            cmds.file(type="mayaBinary")
            cmds.file(save=True, f=True)
            if not os.path.exists(self.light_path):
                self.CreateLightScene()
            else:
                cmds.file(new=True, f=True)
            print("Finished publishing one shot")
            logger.info("Finished publishing one shot")

    def CreateLightScene(self):
        # if not os.path.exists(self.light_path):
        import Maya_Functions.delete_and_clean_up_functions as delete_util
        print("Making Light Scene")
        cmds.file(new=True, f=True)
        print("Setting framerate")
        cmds.currentUnit(time='pal')
        cmds.file(rename=self.light_path)
        cmds.file(self.publish_path, r=True, namespace="Anim", lrd="all")
        print("Setting time range")
        cmds.playbackOptions(minTime=self.start, maxTime=self.end)
        delete_util.DeleteUnknown()
        print("Setting file type and saving")
        cmds.file(type="mayaAscii")
        cmds.file(save=True)
        print("Finished making Light scene")

    # def RemoveArnold(self):  # Try to remove Arnold pluging from scene.
    #     is_arnold = cmds.pluginInfo("mtoa", q=True, loaded=True)
    #     print("Arnold is loaded: %s" % is_arnold)
    #     if is_arnold:
    #         ai_path = cmds.pluginInfo("mtoa", q=True, path=True)
    #         cmds.pluginInfo(ai_path, e=True, writeRequires=False)
    #
    #         arnold_nodes = cmds.pluginInfo("mtoa", q=True, dn=True)
    #         arnold_in_scene = cmds.ls(type=arnold_nodes)
    #         for an in arnold_in_scene:
    #             if cmds.objExists(an):
    #                 print("Deleting: %s " % an)
    #                 cmds.delete(an)
    #             else:
    #                 print("Couldn't find: %s" % an)
    #         cmds.unloadPlugin("mtoa", f=True)
    #     self.DeleteUnknown()


    def ExportCamera(self):
        import Maya_Functions.publish_util_functions as publish_util
        self.GetSceneInfo()
        if self.info_dict["shot_name"] != "":
            publish_util.ExportBakedCamera(self.info_dict["shot_name"],CC.get_shot_path(**self.info_dict),"%s_%s_%s" % (self.info_dict["episode_name"],self.info_dict["seq_name"],self.info_dict["shot_name"]))
        #     camera_name = "%s_Cam" % self.shot
        #     camera_path = "%s/_Preview/Camera_Export/%s_%s_%s_CameraPublish.ma" % (
        #         self.sequence_path, self.ep, self.seq, self.shot)
        #     fol,file_name = os.path.split(camera_path)
        #     if not os.path.exists(fol):
        #         os.mkdir(fol)
        #     # camera_path = "%s/%s_%s_%s/04_Publish/%s_%s_%s_CameraPublish.ma" % (self.sequence_path, self.ep, self.seq, self.shot, self.ep, self.seq, self.shot)
        #     print("CAMERA PATH: %s" % camera_path)
        #     cmds.camera(camera_name, e=True, lt=False)
        # else:
        #     return False
        # # export camera
        # if cmds.objExists(camera_name):
        #     print("EXPORTING CAMERA")
        #     cmds.select(camera_name, r=True)
        #     cmds.file(camera_path, f=True, type="mayaAscii", es=True, chn=True, exp=False, con=True,preserveReferences=False)


# cmds.delete(scene_camera_duplicate)

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setObjectName("PublishAnimScene")
        self.setWindowTitle("PublishAnimScene")
        self.setWindowFlags(QtCore.Qt.Window)
        self.onlyInt = QtGui.QIntValidator()
        self.film_path = CC.get_film_path() #cfg_util.CreatePathFromDict(cfg.project_paths["film_path"])
        self.pub_class = PublishAnimScene()
        self.ep_list = {}
        # self.ep_list = {"E01":{"E01_SQ010":["E01_SQ010_SH010","E01_SQ010_SH020"],"E01_SQ020":["E01_SQ020_SH010","E01_SQ020_SH020"]},"E02":{"E02_SQ010":["E02_SQ010_SH010"],"E02_SQ020":[]}}
        self.PopulateEpisode()
        self.CreateWindow()
        self.UpdateDD()

        self.ep = ""
        self.seq = ""
        self.sequence_path = ""



    def PopulateEpisode(self):
        film_content = os.listdir(self.film_path)
        for cur_con in film_content:
            if self.FindEpisode(cur_con):
                cur_path = "%s/%s" % (self.film_path, cur_con)
                if os.path.isdir(cur_path):
                    self.ep_list[cur_con] = {}
                    self.PopulateSeq(cur_con,cur_path)

    def PopulateSeq(self,cur_ep,cur_ep_path):
        ep_content = os.listdir(cur_ep_path)
        for cur_con in ep_content:
            if self.FindSequence(cur_con):
                cur_path = "%s/%s" % (cur_ep_path, cur_con)
                if os.path.isdir(cur_path):
                    self.ep_list[cur_ep][cur_con] = []
                    self.PopulateShot(cur_ep,cur_con,cur_path)

    def PopulateShot(self,cur_ep,cur_seq,cur_seq_path):
        seq_content = os.listdir(cur_seq_path)
        for cur_con in seq_content:
            if self.FindShot(cur_con):
                cur_path = "%s/%s" % (cur_seq_path, cur_con)
                if os.path.isdir(cur_path):
                    self.ep_list[cur_ep][cur_seq].append(cur_con)
        # sorted(self.ep_list[cur_ep][cur_seq])


    def UpdateDD(self):
        self.episode_dd.clear()
        self.episode_dd.addItems(sorted(self.ep_list.keys()))
        self.episode_dd.currentIndexChanged.connect(self.UpdateSeqDD)
        self.UpdateSeqDD()

    def UpdateSeqDD(self):
        self.seq_dd.clear()
        cur_ep = self.episode_dd.currentText()
        if cur_ep:
            self.seq_dd.addItems(sorted(self.ep_list[cur_ep]))
        self.seq_dd.currentIndexChanged.connect(self.UpdateShotList)
        self.UpdateShotList()

    def UpdateShotList(self):
        self.shot_list.clear()
        cur_ep = self.episode_dd.currentText()
        cur_seq = self.seq_dd.currentText()
        if cur_ep and cur_seq:
            self.shot_list.addItems(sorted(self.ep_list[cur_ep][cur_seq]))


    def RunScenePublish(self):
        if in_maya:
            cmds.file(save=True)
        self.pub_class.RunInMayaPy(yeti_check=self.cache_checkbox.isChecked())

    def CreateWindow(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.top_button_layout = QtWidgets.QHBoxLayout()
        self.bot_button_layout = QtWidgets.QVBoxLayout()

        self.list_layout = QtWidgets.QHBoxLayout()
        self.episode_label = QtWidgets.QLabel("Episode: ")
        # self.episode_input = QtWidgets.QLineEdit()
        # self.episode_input.setValidator(self.onlyInt)
        self.episode_dd = QtWidgets.QComboBox()
        self.use_scene = QtWidgets.QPushButton("Publish Open Scene")
        self.use_scene.clicked.connect(self.RunScenePublish)
        self.top_button_layout.addWidget(self.use_scene)
        self.top_button_layout.addWidget(self.episode_label)
        # self.top_button_layout.addWidget(self.episode_input)
        self.top_button_layout.addWidget(self.episode_dd)

        self.seq_label = QtWidgets.QLabel("SQ: ")
        # self.seq_input = QtWidgets.QLineEdit()
        # self.seq_input.setValidator(self.onlyInt)
        self.seq_dd = QtWidgets.QComboBox()
        self.top_button_layout.addWidget(self.seq_label)
        # self.top_button_layout.addWidget(self.seq_input)
        self.top_button_layout.addWidget(self.seq_dd)

        # self.load_sq_button = QtWidgets.QPushButton("Load")
        # self.load_sq_button.clicked.connect(self.LoadSequence)
        # self.top_button_layout.addWidget(self.load_sq_button)

        # widgets
        self.shot_list = QtWidgets.QListWidget()
        self.shot_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
        self.list_layout.addWidget(self.shot_list)

        # self.shot_list.itemDoubleClicked.connect(self.ShotDoubleClicked)
        # self.asset_list.itemDoubleClicked.connect(self.DoubleClickOnAsset)

        self.hookup_selected_button = QtWidgets.QPushButton("Publish Selected")
        self.hookup_selected_button.clicked.connect(self.HookUp_Selected)

        self.hookup_seq_button = QtWidgets.QPushButton("Publish Sequence")
        self.hookup_seq_button.clicked.connect(self.HookUp_Seq)

        self.export_cams = QtWidgets.QPushButton("Export Camera")
        self.export_cams.clicked.connect(self.ExportCamera)

        self.yeti_cache_layout = QtWidgets.QHBoxLayout()


        self.cache_yeti = QtWidgets.QPushButton("Cache Yeti")
        self.cache_yeti.clicked.connect(self.CacheYeti)

        self.cache_checkbox = QtWidgets.QCheckBox("Auto Cache Yeti")
        self.cache_checkbox.setFixedWidth(110)
        self.cache_checkbox.setChecked(True)

        self.yeti_cache_layout.addWidget(self.cache_checkbox)
        self.yeti_cache_layout.addWidget(self.cache_yeti)

        self.bot_button_layout.addWidget(self.hookup_selected_button)
        self.bot_button_layout.addWidget(self.hookup_seq_button)
        self.bot_button_layout.addWidget(self.export_cams)
        # self.bot_button_layout.addWidget(self.cache_yeti)
        self.bot_button_layout.addLayout(self.yeti_cache_layout)

        # Connect layouts
        self.main_layout.addLayout(self.top_button_layout)

        self.main_layout.addLayout(self.list_layout)
        self.main_layout.addLayout(self.bot_button_layout)

        self.setLayout(self.main_layout)

    def CacheYeti(self):
        my_shots = self.GetSelected()
        # ep_seq = "%s_%s" % (self.ep, self.seq)
        sequence_path = "%s/%s/%s/" % (self.film_path, self.episode_dd.currentText(), self.seq_dd.currentText())
        for shot in my_shots:
            print("SHOULD BE CACHING HERE!")
            # shot_path = "%s/%s/01_Animation/%s_Animation.ma" % (sequence_path, shot, shot)
            # if os.path.exists(shot_path):
            #     MayaPy_ExportCamera(shot_path)


    def ExportCamera(self):
        my_shots = self.GetSelected()
        # ep_seq = "%s_%s" % (self.ep, self.seq)
        sequence_path = "%s/%s/%s/" % (self.film_path, self.episode_dd.currentText(), self.seq_dd.currentText())
        for shot in my_shots:
            shot_path = "%s/%s/01_Animation/%s_Animation.ma" % (sequence_path, shot, shot)
            if os.path.exists(shot_path):
                MayaPy_ExportCamera(shot_path)

    # def LoadSequence(self):
    #     print("loading!")
    #     self.shot_list.clear()
    #     self.ep = "E%s" % (self.episode_input.text()).zfill(2)
    #     self.seq = "SQ%s" % (str(int(self.seq_input.text()) * 10)).zfill(3)
    #     # print("EP: %s SEQ: %s" % (self.ep, self.seq))
    #     self.sequence_path = "%s%s/%s_%s/" % (self.film_path, self.ep, self.ep, self.seq)
    #     temp_shot_list = []
    #     if os.path.exists(self.sequence_path):
    #         content = os.listdir(self.sequence_path)
    #         for con in content:
    #             con_path = "%s/%s/" % (self.sequence_path, con)
    #             if os.path.isdir(con_path) and con.startswith("%s_%s_SH" % (self.ep, self.seq)):
    #                 # print("is shot: %s" % con)
    #                 temp_shot_list.append(con)
    #     self.shot_list.addItems(sorted(temp_shot_list))

    def GetSelected(self):
        temp_shot_list = self.shot_list.selectedItems()
        return_list = []
        for shot in temp_shot_list:
            return_list.append(shot.text())
        return sorted(return_list)

    def HookUp_Seq(self):
        # self.shot_list.selectAll()
        # self.MakeHookup(self.GetSelected(), "%s_%s_HookUp" % (self.ep, self.seq))
        cmd_list = self.PublishSequence()
        for c in cmd_list:
            print(c)
        CreateProcQueue(cmd_list)

    def HookUp_Selected(self):
        my_shots = self.GetSelected()
        cmd_list = []
        for shot in my_shots:
            c_cmd = self.PublishSequence(shot=shot)
            if c_cmd:
                cmd_list.append(c_cmd)
        for c in cmd_list:
            print(c)
        CreateProcQueue(cmd_list)

    def PublishSequence(self, shot=None):
        print("Publishing")
        sequence_path = "%s/%s/%s/" % (self.film_path, self.episode_dd.currentText(), self.seq_dd.currentText())
        shot_to_publish = []

        if not shot:
            for cur_shot in self.ep_list[self.episode_dd.currentText()][self.seq_dd.currentText()]:
                anim_path = "%s/%s/01_Animation/%s_Animation.ma" % (sequence_path,cur_shot, cur_shot)
                shot_cmd = CreateMayaPyCmd(anim_path,self.cache_checkbox.isChecked())
                shot_to_publish.append([cur_shot, shot_cmd])
            return shot_to_publish
        else:
            shot_path = "%s%s/01_Animation/%s_Animation.ma" % (sequence_path, shot, shot)
            if os.path.exists(shot_path):
                shot_cmd = CreateMayaPyCmd(shot_path,self.cache_checkbox.isChecked())
                return [shot, shot_cmd]
            else:
                return None

    # REGEX FOR CHECKING FOLDER NAMES:
    def FindEpisode(self,content):
        low_case = content.lower()
        re_compile = re.compile("^(e)\d{2}$")
        if re_compile.search(low_case):
            # print(content + " matches!")
            return True
        else:
            return False

    def FindSequence(self, content):
        low_case = content.lower()
        re_compile = re.compile("^(e)\d{2}(_sq)\d{3}$")
        if re_compile.search(low_case):
            # print(content + " matches!")
            return True
        else:
            return False

    def FindShot(self,content):
        low_case = content.lower()
        re_compile = re.compile("^(e)\d{2}(_sq)\d{3}(_sh)\d{3}$")
        if re_compile.search(low_case):
            # print(content + " matches!")
            return True
        else:
            return False

def CreateMayaPyCmd(shot_path,cache_yeti=True):
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import PublishAnimScene as PA
cmds.file('%s', open=True,f=True)
c = PA.PublishAnimScene()
c.PublishScene(cache_yeti=%s)
cmds.quit(f=True)
""" % (shot_path,cache_yeti)
    script_content = ";".join(script_content.split("\n"))
    return script_content


def RunMayaPy(shot_path="",cache_yeti=True):  # NOT USED -> Changed to CreateMayaPyCmd
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import PublishAnimScene as PA
cmds.file('%s', open=True,f=True)
c = PA.PublishAnimScene()
c.PublishScene(cache_yeti=%s)
cmds.quit(f=True)
""" % (shot_path,cache_yeti)
    script_content = ";".join(script_content.split("\n"))
    base_command = 'mayapy.exe -c "%s"' % (script_content)
    print(base_command)
    # subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # my_out = subprocess.check_output(base_command, shell=True, stderr=subprocess.STDOUT)
    # print(my_out)

    run_env = getRuntimeEnvFromConfig(config_class=CC, local_user=True) # ocio=False
    c_p = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE,env=run_env)
    stdout = c_p.communicate()[0]
    print("STDOUT:%s" % stdout)


def ProcRun(shot_name, shot_cmd):
    base_command = 'mayapy.exe -c "%s"' % (shot_cmd)
    c_p = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    print("%s:\n %s" % (shot_name, c_p.communicate()[0]))


def ProcWorker(queue):
    for args in iter(queue.get, None):
        try:
            ProcRun(*args)
        except Exception as e:  # catch exceptions to avoid exiting the
            # thread prematurely
            # print('%r failed: %s' % (args, e,), file=sys.stderr)
            print('%s failed: %s' % (args, e))


def CreateProcQueue(cmd_list=None):
    # start threads
    cpu_total = multiprocessing.cpu_count()
    cpu_current = activeCount()
    print("Total Process's: %s -> Using: %s" % (cpu_total, cpu_current))
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
    print("ALL FINISHED")


def MayaPy_ExportCamera(file_path):
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import PublishAnimScene as PA
cmds.file('%s', open=True,f=True)
c = PA.PublishAnimScene()
c.ExportCamera()
cmds.quit(f=True)
""" % (file_path)
    script_content = ";".join(script_content.split("\n"))
    base_command = 'mayapy.exe -c "%s"' % (script_content)
    print(base_command)
    subprocess.Popen(base_command, shell=False, universal_newlines=True)

def RunMayaPyCleanUp(file_path, file_type):  # Unused??
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import PublishAnimScene as PA
cmds.file('%s', open=True,f=True)
c = PA.PublishAnimScene()
#c.RemoveArnold()
cmds.file(type='%s')
cmds.file(save=True)
cmds.quit(f=True)
""" % (file_path, file_type)
    script_content = ";".join(script_content.split("\n"))
    base_command = 'mayapy.exe -c "%s"' % (script_content)
    print(base_command)
    subprocess.Popen(base_command, shell=False, universal_newlines=True)

def RunCleanUp(type=None, cate=None, name=None):
    base = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/%s/%s/%s/" % (type, cate, name)
    if os.path.exists(base):
        model_ref = "%s/02_Ref/%s_Model_Ref.mb" % (base, name)
        rig_ref = "%s/02_Ref/%s_Rig_Ref.mb" % (base, name)
        rig_anim = "%s/02_Ref/%s_Anim.mb" % (base, name)
        shading_render = "%s/02_Ref/%s_Render.mb" % (base, name)
        file_list = [model_ref, rig_ref, rig_anim, shading_render]
        for c_file in file_list:
            if c_file.endswith(".ma"):
                file_type = "mayaAscii"
            else:
                file_type = "mayaBinary"
            print("Cleaning up: %s" % c_file)
            if os.path.exists(c_file):
                RunMayaPyCleanUp(c_file, file_type)
            else:
                print("NO such file as: %s" % c_file)




def _maya_main_window():
    """Return Maya's main window"""
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')


def Run():
    objectName = 'AnimPublishDock'
    if not MayaDockable.dockableExists(objectName):
        MayaDockable.runDockable(objectName, 'Anim Publish', MainWindow())

    # mainWin = MainWindow(parent=_maya_main_window())
    # mainWin.show()


if not in_maya:
    if __name__ == '__main__':
        import sys
        if not QtWidgets.QApplication.instance():
            app = QtWidgets.QApplication(sys.argv)
        else:
            app = QtWidgets.QApplication.instance()

        mainWin = MainWindow()
        mainWin.show()

        sys.exit(app.exec_())
