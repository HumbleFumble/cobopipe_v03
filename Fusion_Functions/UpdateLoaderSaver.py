from pprint import pprint
import os
#import pyperclip

#TODO change so we use project config instead of hardcoded.
#TODO change to see if we can avoid using pyperclip
import re
from getConfig import getConfigClass
CC = getConfigClass()


class GeneralTool(object):
    def __init__(self,fusion, cur_comp):
        self.fusion = fusion
        self.comp = cur_comp
        self.comp_name = ""

    def updateSavers(self):
        savers = self.comp.GetToolList(False, "Saver").values()

    def updateLoaders(self):
        loaders = self.comp.GetToolList(False, "Loader").values()
    def findSceneName(self):
        file_path = (self.comp.GetAttrs("COMPS_FileName")).replace("\\", "/")
        comp_name = self.comp.GetAttrs("COMPS_Name")
        res = re.search(r'(_v\d{4}\.)', comp_name.lower())
        print(res)
        if res:
            self.scene_name = comp_name.split(res)[0]
        else:
            self.scene_name = comp_name

    def ReplaceEpisode(self, content, replace_content):
        # low_case = content.lower()
        e_compile = "(/%s/)" % (CC.episode_regex[1:])
        print(e_compile)
        # result = re.split(re_compile,content, flags=re.IGNORECASE)
        # replace_content = "/S101/"
        result = re.subn(e_compile, replace_content, content, flags=re.IGNORECASE)
        print(result)
        return result[0]

    def ReplaceSQ(self,content,replace_content):
        # low_case = content.lower()
        sq_compile = "(/%s%s/)" % (CC.episode_regex[1:], CC.seq_regex)
        print(sq_compile)
        # result = re.split(re_compile,content, flags=re.IGNORECASE)
        # replace_content = "/S101_SQ020/"
        result = re.subn(sq_compile,replace_content,content,flags=re.IGNORECASE)
        print(result)
        return result[0]
    def ReplaceShot(self,content,replace_content):
        # low_case = content.lower()
        shot_compile = "(%s%s%s)" % (CC.episode_regex[1:], CC.seq_regex, CC.shot_regex)
        print(shot_compile)
        # result = re.split(re_compile,content, flags=re.IGNORECASE)
        # replace_content = "S101_SQ020_SH040"
        result = re.subn(shot_compile,replace_content,content,flags=re.IGNORECASE)
        print(result)
        return result[0]


class MIA_Tool(object):

    __fusion = None
    __cur_comp = None

    def __init__(self, fusion, cur_comp):
        self.__fusion = fusion
        self.__cur_comp = cur_comp

    def CheckForPasses(self, passes_folder):
        # passes_folder = "%s/%s/Passes/" % (self.sequence_path, cur_shot)
        # to_return = []
        to_return = {}
        duration = 0
        to_return["OnlyBG"] = False
        passes_content = os.listdir(passes_folder)
        for con in passes_content:
            con_path = "%s/%s" % (passes_folder, con)
            if os.path.isdir(con_path):
                if "_History" in con or "OLD" in con or "V00" in con or con.endswith('_Crypto'):
                    print("skipping: %s" % con)
                else:
                    exr_con = sorted(os.listdir(con_path))
                    if len(exr_con) > duration:
                        duration = len(exr_con)
                    for pas_con in exr_con:
                        if pas_con.endswith(".exr"):
                            if "OnlyBG" not in pas_con:
                                # print("Found .exr for shot: %s" % cur_shot)
                                # to_return.append("%s/%s" %(con_path, pas_con))
                                to_return[con] = "%s/%s" % (con_path, pas_con)
                                break
                            else:
                                to_return["OnlyBG"] = True
        if not duration == 0:
            to_return["duration"] = duration
        return to_return

    def DoneNotifier(self, _text=None):
        #os_txt = "The path for the 3D camera has been copied. Paste it into the upcoming browser and delete the last 'space' character, then click 'Open'!"
        # pyperclip_txt = "The path for the 3D camera has been copied. Paste it into the upcoming browser, then click 'Open'!"
        dialog_text = {1: "doneNotifier", "Name": "", 2: "Text", "ReadOnly": True, "Lines": 3, "Wrap": True, "Default": _text}
        dialog = {1: dialog_text}
        self.__cur_comp.AskUser("Loaders and Savers Updated!", dialog)

    def DropDown(self, _pass_options):
        # gui
        dialog_dropdown = {1: "passDrop", "Name": "Passes", 2: "Dropdown", "Options": _pass_options, "Default": 0}
        dialog = {1: dialog_dropdown}
        ret = self.__cur_comp.AskUser("Choose render input:", dialog)

        # get the pass status as a list. Output 0 = Color, 1 = Fast. To get it as a number, take the [0] element
        pass_status = ret.values()
        return _pass_options[int(pass_status[0])]

    def Update3DCamera(self, _file_path, shot_name):
        # GET FILEPATH FOR CORRECT CAMERA 3D
        shot_folder = _file_path.split("/03_Comp/")[0]
        publish_folder = "%s/04_Publish/" % shot_folder
        maya_camera = "%s%s_CameraPublish.ma" % (publish_folder, shot_name)
    
        # GET CAMERA TOOL FROM FLOW

        cameras = self.__cur_comp.GetToolList(False, "Camera3D").values()
        if cameras:
            camera = cameras[0]
        else:
            return False
        self.DoneNotifier("Updating Camera. Please click import cam in the selected node, and Ctrl-V and 1 x backspace in the coming dialog and hit enter. Then unlock the cam-node and save.")
        # pyperclip.copy(maya_camera) # install pyperclip using powershell: pip install pyperclip
        #C:/Python27/python.exe -m pip install pyperclip
        # os.system("echo %s|clip" % "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E01/E01_SQ020/E01_SQ020_SH080/04_Publish/E01_SQ020_SH080_CameraPublish.ma")
        os.system("echo %s|clip" % maya_camera)
        self.__cur_comp.SetActiveTool(camera)
        #camera.Import[1] = 1 #Opens the import menu.

    def UpdateBGLoaders(self, loader_list, _passes_folder, _shot_name):
        try:
            for loader in loader_list:
                loader_name = loader.GetAttrs('TOOLS_Name')
                if "BG" in loader_name:
                    print("Changing input for %s to use pass OnlyBG" % loader_name)
                    #print("cur: %s" % loader.GetAttrs('TOOLST_Clip_Name').values()[0])
                    print('_passes_folder: ' + str(_passes_folder))
                    print('_shot_name: ' + str(_shot_name))
                    loader.Clip = "%sOnlyBG/%s_OnlyBG.0001.exr" % (_passes_folder, _shot_name)
                    #print("new: %s\n" % loader.GetAttrs('TOOLST_Clip_Name').values()[0])
        except ValueError:
            print("use whole numbers for episode, sequence and shot")

    def ChangeLoaderPaths(self):
        loaders = self.__cur_comp.GetToolList(False, "Loader").values()
        savers = self.__cur_comp.GetToolList(False, "Saver").values()

        file_path = (self.__cur_comp.GetAttrs("COMPS_FileName")).replace("\\", "/")
        comp_name = self.__cur_comp.GetAttrs("COMPS_Name")
        name_parts = comp_name.split("_")
        print(name_parts)

        ep = name_parts[0]
        sq = name_parts[1]
        sh = name_parts[2]
        shot_name = "%s_%s_%s" % (ep, sq, sh)

        cur_split = file_path.split("/03_Comp/")

        passes_folder = "%s/Passes/" % cur_split[0]
        passes = self.CheckForPasses(passes_folder)
        print("\nFound %s in Passes" % passes)
        only_bg_in_passes = passes["OnlyBG"]
        passes.pop("OnlyBG")
        print("Found BG Pass: %s" % only_bg_in_passes)

        bg_in_loaders = False
        vfx_in_loaders = False

        if passes:
            self.__cur_comp.SetAttrs({"COMPN_GlobalStart": 1})
            self.__cur_comp.SetAttrs({"COMPN_GlobalEnd": passes["duration"]})
            self.__cur_comp.SetAttrs({"COMPN_RenderStart": 1})
            self.__cur_comp.SetAttrs({"COMPN_RenderStartTime": 1})
            self.__cur_comp.SetAttrs({"COMPN_RenderEnd": passes["duration"]})
            passes.pop("duration")

            if len(passes.keys()) > 1:
                pick_key = self.DropDown(sorted(passes.keys()))
            else:
                pick_key = passes.keys()[0]
            print("Pick key: %s" % pick_key)

            mid_oid_dict = {}#mid_oid_dict = {"MID": {}, "OID": {}}
            for cur_loader in loaders:
                cur_loader_path = (cur_loader.GetAttrs("TOOLST_Clip_Name")[1]).replace("\\", "/")
                if "/Passes/" in cur_loader_path:
                    loader_name = cur_loader.GetAttrs('TOOLS_Name')
                    print(loader_name)
                    # Go through and check for OID/MID ranges
                    # Find the cur image

                    if "BG" in loader_name:
                        bg_in_loaders = True
                        print("Changing input for %s to use pass OnlyBG" % loader_name)
                        # cur_loader.Clip = "%sOnlyBG/%s_OnlyBG.0001.exr" % (passes_folder, shot_name)
                        bg_path = "%s%s_OnlyBG/%s_%s_OnlyBG.0001.exr" % (passes_folder, pick_key, shot_name,pick_key)
                        if not os.path.exists(bg_path):
                            test_old_path = "%sOnlyBG/%s_OnlyBG.0001.exr" % (passes_folder, shot_name)
                            if os.path.exists(test_old_path):
                                bg_path = test_old_path
                        cur_loader.Clip = bg_path
                        self.updateClipDict(cur_loader,mid_oid_dict)
                        dict_clip = bg_path
                        cur_loader["GlobalIn"] = 1
                        cur_loader.ClipTimeStart = 0
                        # cur_loader["GlobalIn"] = 1
                        if cur_loader.GetAttrs("TOOLIT_Clip_Length").values()[0] <2:
                            print("Found 1 frame, setting to loop")
                            cur_loader.Loop = 1
                            cur_loader["GlobalIn"] = 0
                            cur_loader.ClipTimeStart = 0
                            cur_loader["GlobalIn"] = 1
                            cur_loader["GlobalOut"] = 1

                    elif "Crypto" in loader_name or "crypto" in loader_name or "Cryptomatte" in loader_name or "cryptomatte" in loader_name:
                       print("Changing input %s to use pass Crypto" % loader_name)
                       cur_loader.Clip = '%s%s_Crypto/%s_%s_Crypto.0001.exr' % (passes_folder, pick_key, shot_name, pick_key)
                       cur_loader["GlobalIn"] = 1
                       cur_loader.ClipTimeStart = 0
                       continue
                    elif "VFX" in loader_name:
                        vfx_in_loaders = True
                        continue
                    else:
                        print("Changing input for %s" % loader_name)
                        cur_loader.Clip = passes[pick_key]  # SET NEW PATH!
                        dict_clip = passes[pick_key]
                        self.updateClipDict(cur_loader, mid_oid_dict)
                        cur_loader["GlobalIn"] = 1
                        cur_loader.ClipTimeStart = 0
                        # cur_loader["GlobalIn"] = 1
                        if cur_loader.GetAttrs("TOOLIT_Clip_Length").values()[0] <2:
                            print("Found 1 frame, setting to loop")
                            cur_loader.Loop = 1
                            cur_loader["GlobalIn"] = 0
                            cur_loader.ClipTimeStart = 0
                            cur_loader["GlobalIn"] = 1
                            cur_loader["GlobalOut"] = 1
                    self.setClipPart(cur_loader=cur_loader, cur_dict=mid_oid_dict[dict_clip])


        for cur_saver in savers:
            saver_name = cur_saver.GetAttrs("TOOLS_Name")
            cur_saver_path = (cur_saver.GetAttrs("TOOLST_Clip_Name")[1]).replace("\\", "/")
            sq_path = "%sFilm/%s/%s_%s" % (cur_split[0].split("Film/")[0], ep, ep, sq)
            if "/_Preview/" in cur_saver_path:
                rush_path = "%s/_Preview/%s_Comp.mov" % (sq_path, shot_name)
                cur_saver.Clip = rush_path
                print("Changing output for %s" % saver_name)
            elif "/05_CompOutput/" in cur_saver_path:
                compoutput_path = "%s/%s/05_CompOutput/%s_.exr" % (sq_path, shot_name, shot_name)
                cur_saver.Clip = compoutput_path
                print("Changing output for %s" % saver_name)
        if bg_in_loaders and not only_bg_in_passes:
            bg_text = "Couldn't Find OnlyBG in passes to fit with the BG loaders. Please Check the comp-flow for BG nodes"
            self.DoneNotifier(bg_text)
        if vfx_in_loaders:
            vfx_text = "There is VFX loaders in this comp\nThey have NOT been updated\nPlease disable or update them manually."
            self.DoneNotifier(vfx_text)

        #self.DoneNotifier()
        self.Update3DCamera(file_path, shot_name)

    def updateClipDict(self,cur_loader,cur_dict):
        dict_clip = cur_loader.Clip[0]
        if not dict_clip in cur_dict.keys():
            cur_dict[dict_clip] = {"MID": {}, "OID": {}}
            if cur_loader.Clip1.OpenEXRFormat.Part:
                parts = cur_loader.Clip1.OpenEXRFormat.Part.GetAttrs()
                if "INPIDT_ComboControl_ID" in parts.keys():
                    channel_dict = cur_loader.Clip1.OpenEXRFormat.Part.GetAttrs()["INPIDT_ComboControl_ID"]

                    for combo_name in channel_dict.values():

                        # combo_name = channel_dict[combo_id]
                        mid_info = self.returnRangeInfo(combo_name, "MID")
                        oid_info = self.returnRangeInfo(combo_name, "OID")
                        if mid_info:
                            cur_dict[dict_clip]["MID"][int(mid_info)] = combo_name
                        if oid_info:
                            cur_dict[dict_clip]["OID"][int(oid_info)] = combo_name

    def setClipPart(self,cur_loader,cur_dict):

        cur_part = cur_loader.Clip1.OpenEXRFormat.Part[0]
        print("For Loader: %s - is set to: %s" % (cur_loader.GetAttrs('TOOLS_Name'), cur_part))
        for cur_type in ["MID", "OID"]:
            cur_range = self.returnRangeInfo(cur_part, cur_type)
            if cur_range:
                if cur_range in cur_dict[cur_type].keys():
                    print("Found %s" % cur_dict[cur_type][cur_range])
                    cur_loader.Clip1.OpenEXRFormat.Part = cur_dict[cur_type][cur_range]
                else:
                    print("Can't find RenderElement %s_%s..." % (cur_type, cur_range))


    def returnRangeInfo(self,name,ID_type):
        if ID_type in name:
            range = name.split("_")[1]
            if "-" in range:
                range = range.split("-")[0]
            # print("For %s - range is: %s" % (name,int(range)))
            return int(range)
        return None



def run(fusion):
    #print('>> 1')
    cur_comp = fusion.GetCurrentComp()
    cur_comp.Lock()
    tool = MIA_Tool(fusion=fusion, cur_comp=cur_comp)
    tool.ChangeLoaderPaths()
    cur_comp.Unlock()
    # camera = composition.GetToolList(False, "Camera3D").values()[0]
    # camera.Import[1] = 0


if __name__ == '__main__':
    import sys
    content = "P:/930435_Liva_og_De_Uperfekte/Teaser/Film/S101/S101_SQ010/S101_SQ010_SH050/passes/ColorB/S101_SQ010_SH050_ColorB.0001"
    gt = GeneralTool(None,None)

    episode = "S102"
    sq = "%s_SQ020" % episode
    shot = "%s_SH040" %(sq)

    new_content = content
    new_content = gt.ReplaceEpisode(new_content,f"/{episode}/")
    new_content = gt.ReplaceSQ(new_content, f"/{sq}/")
    new_content = gt.ReplaceShot(new_content, f"{shot}")

    # gt.ReplaceSQ(content,"")
    # if not QtWidgets.QApplication.instance():
    #     app = QtWidgets.QApplication(sys.argv)
    # else:
    #     app = QtWidgets.QApplication.instance()
    # mainWin = MainWindow()
    # mainWin.show()

    # app.exec_()