import shutil
import os
import math
import re
import datetime

class Tool(object):
    # GLOBAL variables
    __base_path = """P:/930382_KiwiStrit2/Production/Film"""
    __template_path = """P:/930382_KiwiStrit2/Production/Pipeline/Template/Fusion_Templates"""
    __version_number = 1
    __mode_list = ["TEMPLATE", "PREVIOUS COMP"]
    __fusion = None
    __composition = None

    def __init__(self, fusion, composition):
        self.__fusion = fusion
        self.__composition = composition

    # Set mode
    def SetMode(self, _mode_list):
        set_mode = {1: "mode_ID", "Name": "Comp from", 2: "Dropdown", "Options": _mode_list, "Default": 0}
        dialog = {1: set_mode}
        res = self.__composition.AskUser("Choose mode:", dialog)
        if res is None:
            return None
        else:
            return res

    # current EP getter and setter
    def SetCurEp(self, _ep_list):
        set_ep = {1: "ep_ID", "Name": "Episode", 2: "Dropdown", "Options": _ep_list, "Default": 0}
        dialog = {1: set_ep}
        res = self.__composition.AskUser("Choose current episode:", dialog)
        if res is None:
            return None
        else:
            return res

    def GetEpList(self, _base_path):
        ep_path = os.listdir(_base_path)
        ep_list = []
        for folder in ep_path:
            if "E" in folder and len(folder) == 3 and folder.startswith("E"):
                ep_list.append(folder)
        return ep_list

    # target EP setter
    def SetTargetEp(self, _ep_list):
        set_ep = {1: "ep_ID", "Name": "Episode", 2: "Dropdown", "Options": _ep_list, "Default": 0}
        dialog = {1: set_ep}
        res = self.__composition.AskUser("Choose target episode:", dialog)
        if res is None:
            return None
        else:
            return res

    # current SQ getter and setter
    def SetCurSq(self, _sq_list):
        set_sq = {1: "sq_ID", "Name": "Sequence", 2: "Dropdown", "Options": _sq_list, "Default": 0}
        dialog = {1: set_sq}
        res = self.__composition.AskUser("Choose current sequence:", dialog)
        if res is None:
            return None
        else:
            return res

    def GetSqList(self, _base_path, _ep):
        sq_path = "%s/%s" % (_base_path, _ep)
        sq_folders = os.listdir(sq_path)
        sq_list = []
        for folder in sq_folders:
            if "SQ" in folder and len(folder) == 9 and folder.startswith("E"):
                sq_list.append(folder)
        return sq_list

    # target SQ setter
    def SetTargetSq(self, _sq_list):
        set_sq = {1: "sq_ID", "Name": "Sequence", 2: "Dropdown", "Options": _sq_list, "Default": 0}
        dialog = {1: set_sq}
        res = self.__composition.AskUser("Choose target sequence:", dialog)
        if res is None:
            return None
        else:
            return res

    # current SH getter and setter
    def SetCurSh(self, _sh_list):
        set_sh = {1: "sh_ID", "Name": "Shot", 2: "Dropdown", "Options": _sh_list, "Default": 0}
        dialog = {1: set_sh}
        res = self.__composition.AskUser("Choose current shot:", dialog)
        if res is None:
            return None
        else:
            return res

    def GetShList(self, _base_path, _ep, _sq):
        sh_path = "%s/%s/%s" % (_base_path, _ep, _sq)
        sh_folders = os.listdir(sh_path)
        sh_list = []
        for folder in sh_folders:
            if "SH" in folder and len(folder) == 15 and folder.startswith("E"):
                sh_list.append(folder)
        return sh_list

    # target SH setter
    def SetTargetSh(self, _sh_list):
        set_sh = {1: "sh_ID", "Name": "Shot", 2: "Dropdown", "Options": _sh_list, "Default": 0}
        dialog = {1: set_sh}
        res = self.__composition.AskUser("Choose target shot:", dialog)
        if res is None:
            return None
        else:
            return res

    # target version setter
    def SetTargetVersion(self, _version_list):
        set_sh = {1: "vs_ID", "Name": "Shot", 2: "Dropdown", "Options": _version_list, "Default": 0}
        dialog = {1: set_sh}
        res = self.__composition.AskUser("Choose target version:", dialog)
        if res is None:
            return None
        else:
            return res

    # folder checkers
    def CheckForRushesFolder(self, _base_path, _ep, _sq):
        rushes_path = "%s/%s/%s/_Rushes" % (_base_path, _ep, _sq)
        if not os.path.exists(rushes_path):
            print("_Rushes folder created")
            os.makedirs(rushes_path)

    def CheckForCompOutputFolder(self, _base_path, _ep, _sq, _sh):
        compoutput_path = "%s/%s/%s/%s/05_CompOutput" % (_base_path, _ep, _sq, _sh)
        if not os.path.exists(compoutput_path):
            print("05_CompOutput folder created")
            os.makedirs(compoutput_path)

    # Get all template comps from fusion template folder
    def GetFusionTemplates(self, ft_path):
        fusion_templates_path = os.listdir(ft_path)
        fusion_templates = []
        for file in fusion_templates_path:
            if ".comp" in file:
                fusion_templates.append(file)
        return fusion_templates

    # Set comp from template
    def SetCompFromTemplate(self, _template_option):
        set_template = {1: "template_ID", "Name": "Template", 2: "Dropdown", "Options": _template_option, "Default": 0}
        set_load = {1: "load_ID", "Name": "Load duplicated comp", 2: "Checkbox", "NumAcross": 2, "Default": 1}
        set_overwrite = {1: "overwrite_ID", "Name": "Overwrite existing comp", 2: "Checkbox", "NumAcross": 2,
                         "Default": 0}

        dialog = {1: set_template,
                  2: set_load,
                  3: set_overwrite}

        res = self.__composition.AskUser("Create comp:", dialog)
        if res is None:
            return None
        else:
            return res

    # Set comp from previous comp
    def SetCompFromPreviousComp(self):
        set_load = {1: "load_ID", "Name": "Load duplicated comp", 2: "Checkbox", "NumAcross": 2, "Default": 1}
        set_overwrite = {1: "overwrite_ID", "Name": "Overwrite existing comp", 2: "Checkbox", "NumAcross": 2,
                         "Default": 0}

        dialog = {1: set_load,
                  2: set_overwrite}

        res = self.__composition.AskUser("Create comp:", dialog)
        if res is None:
            return None
        else:
            return res

    # Get all current comp files for a shot (the 03_Comp folder)
    def GetCompsInSaveFolder(self, comp_path):
        comp_files_path = os.listdir(comp_path)
        comp_files = []
        for file in comp_files_path:
            if ".comp" in file:
                comp_files.append(file)
        return comp_files

    # REMINDER: informing the user that a comp already exists for that shot.
    def CompAlreadyExists(self, old, new):
        new_split = new.split("03_Comp/")[1]
        dlg_text = {1: "existsReminder", "Name": "", 2: "Text", "ReadOnly": True, "Lines": 8, "Wrap": True,
                    "Default": "Following comp already exists:\n    %s\n\nSaving as:\n    %s\n\nCheck the 'Overwrite existing comp' checkbox to overwrite." % (
                        old, new_split)}
        dialog = {1: dlg_text}
        self.__composition.AskUser("Warning!", dialog)

    # LOADING DUPLICATED COMP
    def LoadingDuplicatedComp(self, _load_comp_status, _comp_file):
        if _load_comp_status == 1:
            print("loading duplicated template\n")
            os.system("start " + _comp_file)
        elif _load_comp_status == 0:
            print("not loading duplicated template\n")
        else:
            print("something went wrong")

    # Set new comp to save out
    def SetNewComp(self, comp_path, shot_name, latest_comp):
        print("--> latest comp: %s" % latest_comp)

        latest_comp_elements = filter(None, re.split("%s_Comp_V|.comp" % shot_name, latest_comp))
        latest_version = latest_comp_elements[0]

        new_version = int(latest_version) + 1
        new_version_digits = int(math.log10(int(new_version))) + 1
        if new_version_digits == 1:
            new_version = "00%s" % new_version
        elif new_version_digits == 2:
            new_version = "0%s" % new_version
        elif new_version_digits == 3:
            new_version = "%s" % new_version
        else:
            print("too many digits in %s\n" % shot_name)

        # E##_SQ###_SH###_###.comp
        # E##_SQ###_SH###_Comp_V###.comp

        new_comp_file = "%s%s_Comp_V%s.comp" % (comp_path, shot_name, new_version)
        print("--> new comp: %s\n" % new_comp_file.split("03_Comp/")[1])
        return new_comp_file

    # SET CURRENT COMP
    def SetCurComp(self):
        cur_comp_info = []

        # SET CUR EP
        cur_ep_idx = self.SetCurEp(self.GetEpList(self.__base_path))
        if cur_ep_idx is None:
            print("You cancelled the dialog!")
        else:
            print(cur_ep_idx.values())
            cur_ep_idx = int(list(cur_ep_idx.values())[0])
            cur_ep = self.GetEpList(self.__base_path)[cur_ep_idx]
            print("current episode: %s" % cur_ep)
            cur_comp_info.append(cur_ep)

            # SET CUR SQ
            cur_sq_idx = self.SetCurSq(self.GetSqList(self.__base_path, cur_ep))
            if cur_sq_idx is None:
                print("You cancelled the dialog!")
            else:
                cur_sq_idx = int(list(cur_sq_idx.values())[0])
                cur_sq = self.GetSqList(self.__base_path, cur_ep)[cur_sq_idx]
                print("current sequence: %s" % cur_sq)
                cur_comp_info.append(cur_sq)

                # Check if _Rushes folder exists in current shot folder, if not create it
                #CheckForRushesFolder(base_path, cur_ep, cur_sq)

                # SET CUR SH
                cur_sh_idx = self.SetCurSh(self.GetShList(self.__base_path, cur_ep, cur_sq))
                if cur_sh_idx is None:
                    print("You cancelled the dialog!")
                else:
                    cur_sh_idx = int(list(cur_sh_idx.values())[0])
                    cur_sh = self.GetShList(self.__base_path, cur_ep, cur_sq)[cur_sh_idx]
                    print("current shot: %s" % cur_sh)
                    cur_comp_info.append(cur_sh)

                    # Check if 05_CompOutput folder exists in current shot folder, if not create it
                    self.CheckForCompOutputFolder(self.__base_path, cur_ep, cur_sq, cur_sh)
        if len(cur_comp_info) == 3:
            return cur_comp_info
        else:
            return None

    def SetTargetComp(self):
        target_comp_info = []

        # SET TARGET EP
        target_ep_idx = self.SetTargetEp(self.GetEpList(self.__base_path))
        if target_ep_idx is None:
            print("You cancelled the dialog!")
        else:
            target_ep_idx = int(list(target_ep_idx.values())[0])
            target_ep = self.GetEpList(self.__base_path)[target_ep_idx]
            print("target episode: %s" % target_ep)
            target_comp_info.append(target_ep)

            # SET TARGET SQ
            target_sq_idx = self.SetTargetSq(self.GetSqList(self.__base_path, target_ep))
            if target_sq_idx is None:
                print("You cancelled the dialog!")
            else:
                target_sq_idx = int(list(target_sq_idx.values())[0])
                target_sq = self.GetSqList(self.__base_path, target_ep)[target_sq_idx]
                print("target sequence: %s" % target_sq)
                target_comp_info.append(target_sq)

                # SET TARGET SH
                target_sh_idx = self.SetTargetSh(self.GetShList(self.__base_path, target_ep, target_sq))
                if target_sh_idx is None:
                    print("You cancelled the dialog!")
                else:
                    target_sh_idx = int(list(target_sh_idx.values())[0])
                    target_sh = self.GetShList(self.__base_path, target_ep, target_sq)[target_sh_idx]
                    print("target shot: %s" % target_sh)
                    target_comp_info.append(target_sh)

                    # SET TARGET VERSION NUMBER
                    target_comp_path = "%s/%s/%s/%s/03_Comp" % (self.__base_path, target_ep, target_sq, target_sh)
                    target_version_idx = self.SetTargetVersion(self.GetCompsInSaveFolder(target_comp_path))
                    if target_version_idx is None:
                        print("You cancelled the dialog!")
                    else:
                        target_version_idx = int(list(target_version_idx.values())[0])
                        #target_version = filter(None, re.split("%s_|.comp" % target_sh, GetCompsInSaveFolder(target_comp_path)[target_version_idx]))[0]
                        target_version = self.GetCompsInSaveFolder(target_comp_path)[target_version_idx]
                        print("target version: %s" % target_version)
                        target_comp_info.append(target_version)

        if len(target_comp_info) == 4:
            return target_comp_info
        else:
            return None

    # CREATE COMP FROM TEMPLATE
    def CreateCompFromTemplate(self, cur_ep, cur_sq, cur_sh):
        # SET LOAD, TEMPLATE, OVERWRITE
        comp_shot_info = self.SetCompFromTemplate(self.GetFusionTemplates(self.__template_path))
        # comp_shot_info = {'template_ID': 0.0, 'load_ID': 1.0, 'overwrite_ID': 0.0}

        if comp_shot_info is None:
            print("You cancelled the dialog!")
        else:
            comp_shot_values = comp_shot_info.values()

            # load = int(list(comp_shot_values)[0])
            load = int(comp_shot_info["load_ID"])
            print("load: %s" % load)

            # template_idx = int(list(comp_shot_values)[1])
            template_idx = int(comp_shot_info["template_ID"])
            print("template: %s" % template_idx)

            # overwrite = int(list(comp_shot_values)[2])
            overwrite = int(comp_shot_info["overwrite_ID"])
            print("overwrite: %s" % overwrite)

            template_filename = self.GetFusionTemplates(self.__template_path)[template_idx]  # template file to use
            template_filepath = """%s/%s""" % (self.__template_path, template_filename)  # source file
            saveout_path = """%s/%s/%s/%s/03_Comp/""" % (self.__base_path, cur_ep, cur_sq, cur_sh)  # where to save comp

            # check if the template exists, if not, the program will not run
            if os.path.exists(template_filepath):
                initial_comp_filepath = """%s%s_Comp_V00%s.comp""" % (saveout_path, cur_sh, self.__version_number)

                # check if we are going to create a comp file overwrite/make a new version
                if os.path.exists(initial_comp_filepath):
                    print("\ncomp already exist for %s:" % cur_sh)
                    # get latest comp filename as string
                    latest_comp_filename = self.GetCompsInSaveFolder(saveout_path)[-1]

                    # check if we are going to overwrite or make a new version
                    if overwrite == 0:
                        new_comp = self.SetNewComp(saveout_path, cur_sh, latest_comp_filename)
                        self.CompAlreadyExists(latest_comp_filename, new_comp)
                        print("saving comp file as:\n    %s\n" % new_comp)
                        shutil.copy2(template_filepath, new_comp)
                        os.utime(new_comp, None)
                        self.LoadingDuplicatedComp(load, new_comp)

                    elif overwrite == 1:
                        latest_comp_filepath = "%s%s" % (saveout_path, latest_comp_filename)
                        print("--> latest comp: %s\n" % latest_comp_filepath)
                        print("overwriting comp file:\n    %s\n" % latest_comp_filepath)
                        shutil.copy2(template_filepath, latest_comp_filepath)
                        os.utime(latest_comp_filepath, None)
                        self.LoadingDuplicatedComp(load, latest_comp_filepath)
                else:
                    print("copying file:\n    %s to\n    %s\n" % (
                        template_filepath, initial_comp_filepath))
                    shutil.copy2(template_filepath, initial_comp_filepath)
                    os.utime(initial_comp_filepath, None)
                    self.LoadingDuplicatedComp(load, initial_comp_filepath)
            else:
                print("template file does not exist\n")

    # CREATE COMP FROM PREVIOUS COMP
    def CreateCompFromPreviousComp(self, cur_ep, cur_sq, cur_sh, target_ep, target_sq, target_sh, target_version):
        # SET LOAD, TEMPLATE, OVERWRITE
        comp_shot_info = self.SetCompFromPreviousComp()
        if comp_shot_info is None:
            print("You cancelled the dialog!")
        else:
            # comp_shot_values = comp_shot_info[""]
            load = int(comp_shot_info["load_ID"])
            overwrite = int(comp_shot_info["overwrite_ID"])

            target_comp_path = """%s/%s/%s/%s/03_Comp""" % (
                self.__base_path, target_ep, target_sq, target_sh)  # where to get the target comp from
            #latest_target_comp_filename = GetCompsInSaveFolder(target_comp_path)[-1]  # latest version of the target comp

            target_comp_filepath = """%s/%s""" % (target_comp_path, target_version)  # target comp filepath

            saveout_path = """%s/%s/%s/%s/03_Comp/""" % (
                self.__base_path, cur_ep, cur_sq, cur_sh)  # where to duplicate the target comp to

            # check if the target comp exists, if not, the program will not run
            if os.path.exists(target_comp_filepath):
                initial_comp_filepath = """%s%s_Comp_V00%s.comp""" % (saveout_path, cur_sh, self.__version_number)

                # check if we are going to create a comp file overwrite/make a new version
                if os.path.exists(initial_comp_filepath):
                    print("\ncomp already exist for %s:" % cur_sh)
                    # get latest comp filename as string
                    latest_comp_filename = self.GetCompsInSaveFolder(saveout_path)[-1]

                    # check if we are going to overwrite or make a new version
                    if overwrite == 0:
                        new_comp = self.SetNewComp(saveout_path, cur_sh, latest_comp_filename)
                        self.CompAlreadyExists(latest_comp_filename, new_comp)
                        print("saving comp file as:\n    %s\n" % new_comp)
                        shutil.copy2(target_comp_filepath, new_comp)
                        os.utime(new_comp, None)
                        self.LoadingDuplicatedComp(load, new_comp)

                    elif overwrite == 1:
                        latest_comp_filepath = "%s%s" % (saveout_path, latest_comp_filename)
                        print("--> latest comp: %s\n" % latest_comp_filepath)
                        print("overwriting comp file:\n    %s\n" % latest_comp_filepath)
                        shutil.copy2(target_comp_filepath, latest_comp_filepath)
                        os.utime(latest_comp_filepath, None)
                        self.LoadingDuplicatedComp(load, latest_comp_filepath)
                else:
                    print("copying file:\n    %s to\n    %s\n" % (target_comp_filepath, initial_comp_filepath))
                    shutil.copy2(target_comp_filepath, initial_comp_filepath)
                    os.utime(initial_comp_filepath, None)
                    self.LoadingDuplicatedComp(load, initial_comp_filepath)
            else:
                print("target comp file does not exist\n")

    # CreateComp USER INPUT -> COPY TEMPLATE TO CORRECT PATH -> OVERWRITE/LOAD IF CHECKED
    def CreateComp(self):
        cur_comp_info = self.SetCurComp()
        if cur_comp_info:
            cur_ep = cur_comp_info[0]
            cur_sq = cur_comp_info[1]
            cur_sh = cur_comp_info[2]

            mode_dict = self.SetMode(self.__mode_list)
            if mode_dict is None:
                print("You cancelled the dialog!")
            else:
                mode = int(list(mode_dict.values())[0])
                print("\nCreate comp from %s\n" % self.__mode_list[mode])

                # MODE IS TEMPLATE
                if self.__mode_list[mode] == self.__mode_list[0]:
                    self.CreateCompFromTemplate(cur_ep, cur_sq, cur_sh)

                # MODE IS PREVIOUS COMP
                elif self.__mode_list[mode] == self.__mode_list[1]:
                    target_comp_info = self.SetTargetComp()
                    if target_comp_info:
                        target_ep = target_comp_info[0]
                        target_sq = target_comp_info[1]
                        target_sh = target_comp_info[2]
                        target_version = target_comp_info[3]
                        self.CreateCompFromPreviousComp(cur_ep, cur_sq, cur_sh, target_ep, target_sq, target_sh, target_version)

def run(fusion, composition):
    print("%s" % datetime.datetime.now())
    print("---------------------------------------------------------")
    fusion.GetCurrentComp()
    try:
        tool = Tool(fusion=fusion, composition=composition)
        tool.CreateComp()
    except ValueError as e:
        print("something went wrong:")
        print(e.message)
    print("---------------------------------------------------------\n\n\n")