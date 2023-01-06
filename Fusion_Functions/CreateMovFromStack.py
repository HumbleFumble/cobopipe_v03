import shutil
import os
import subprocess
#TODO Gather info automatically. Find duration.
#TODO Use project config instead of hardcoding paths

#OUTDATED - USE
class CreatePreviewInsideFusion():
    def __init__(self, fusion, _input=None, _output=None, comp_file=None, project_name="MiasMagic2", user=None,shot_info={}):
        self.__fusion = fusion
        # self.__composition = self.__fusion.GetCurrentComp()
        self.project_name = project_name
        self.user = user
        self.template_path = "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Pipeline/Template/CreateMovFromStack_Template.comp"
        self.comp_file = comp_file
        self.preview_comp_file = None
        self.input = _input
        self.output = _output
        self.duration = 20

        # self.ep = None
        # self.sq = None
        # self.sh = None
        # if shot_info:
        #     self.ep = shot_info["episode_name"]
        #     self.sq = shot_info["seq_name"]
        #     self.sh = shot_info["shot_name"]

        # self.run(from_file=True)

    def GatherInfoFromOpenComp(self):
        start_comp = self.__fusion.GetCurrentComp()
        file_path = (start_comp.GetAttrs("COMPS_FileName")).replace("\\", "/")
        comp_name = start_comp.GetAttrs("COMPS_Name")
        name_parts = comp_name.split("_")

        self.ep = name_parts[0]
        self.sq = name_parts[1]
        self.sh = name_parts[2]
        shot_name = "%s_%s_%s" % (self.ep, self.sq, self.sh)
        self.preview_comp_file = "%s/04_Publish/%s_MovRender.comp" % (file_path.split("/03_Comp/")[0], shot_name)
        self.input = "%s/05_CompOutput/%s_0001.exr" % (file_path.split("/03_Comp/")[0], shot_name)
        from Fusion_Functions.getProjectAndUserInfo import askUserInfo
        ask_input = askUserInfo(start_comp)
        if ask_input:
            project, user = ask_input
            self.user = user
            self.project_name = project
        self.duration = int(start_comp.GetAttrs("COMPN_RenderStart")) - int(start_comp.GetAttrs("COMPN_RenderStart")) + 1
        temp_file = file_path.split("/03_Comp/")[0]
        self.output = "%s/_Preview/%s_Comp.mov" % (temp_file.split("/%s" % shot_name)[0], shot_name)

    def ChangeLoaderAndSaver(self):
        self.__composition = self.__fusion.GetCurrentComp()
        self.__composition.GetAttrs({"COMPS_Name":1})

        self.__composition.SetAttrs({"COMPN_GlobalStart": 1})
        self.__composition.SetAttrs({"COMPN_GlobalEnd": self.duration})
        self.__composition.SetAttrs({"COMPN_RenderStart": 1})
        self.__composition.SetAttrs({"COMPN_RenderStartTime": 1})
        self.__composition.SetAttrs({"COMPN_RenderEnd": self.duration})

        loaders = self.__composition.GetToolList(False, "Loader").values()
        savers = self.__composition.GetToolList(False, "Saver").values()
        self.saver = savers[0]
        loaders[0].Clip = self.input  # SET NEW PATH!
        loaders[0]["GlobalIn"] = 1
        loaders[0].ClipTimeStart = 0
        self.saver.Clip = self.output

    def run(self,submit=True):
        self.project_name = self.project_name + "_Fusion"
        self.GatherInfoFromOpenComp()
        DuplicateTemplate(template_path=self.template_path,dest_path=self.preview_comp_file)
        self.__fusion.LoadComp(self.preview_comp_file, True)
        self.ChangeLoaderAndSaver()
        self.__composition.Unlock()
        self.__composition.Save()

        if submit:
            submitToRR(project_name=self.project_name,user=self.user,comp_path=self.preview_comp_file,ep=self.ep,sq=self.sq,sh=self.sh,)
        else:
            self.__composition.Render()

def DuplicateTemplate(template_path="P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Pipeline/Template/CreateMovFromStack_Template.comp",dest_path=None):
    shutil.copy2(template_path, dest_path)
    os.utime(dest_path, None)
    # os.system("start " + self.__comp_path)

def GetDurationFromEXRs(folder_path):
    duration = len(os.listdir(os.path.split(folder_path)[0]))
    return duration

def GetDurationFromFile(comp_file=None):
    f = open(comp_file, "r")
    content = f.read()
    f.close()
    render_split = content.split("RenderRange = {")[1].split(",")[1].split("}")[0]
    return int(render_split)

def replaceInTemplate(input_path,output_path,preview_comp_file,duration):
    # copy temp file and rename
    duration_replace = 1234
    duration_zero_replace = 12345
    output_replace = "paste_output_file_here"
    input_replace = "paste_input_path_here"
    output_final = output_path.replace("/", os.sep + os.sep)
    input_final = input_path.replace("/", os.sep + os.sep)
    f = open(preview_comp_file, "r")
    content = f.read()
    f.close()
    content = content.replace(str(duration_zero_replace), str(duration-1))
    content = content.replace(str(duration_replace),str(duration))
    content = content.replace(output_replace,output_final)
    content = content.replace(input_replace, input_final)
    f = open(preview_comp_file, "w")
    f.write(content)
    f.close()

def submitToRR(project_name=None,project_path="P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/",user=None,comp_path=None,ep=None,sq=None,sh=None):
    import Fusion_Functions.FusionRRSubmitter as FRR
    if not user:
        user = "Comper"
    rr_cmd = FRR.RenderSubmitInfo(project_name=project_name, client_pool="CompNodes",
                                  project_path=project_path,
                                  user_name=user, render_file=comp_path, single_out=True,episode=ep,sequence=sq, shot=sh)
    subprocess.Popen(rr_cmd)

    # def runOutsideFusion(self,submit=True):
    #     self.GetDuration()
    #     self.DuplicateTemplate()
    #     self.replaceInTemplate()

    # if not submit:
    #     try:
    #         import BlackmagicFusion as bmd
    #         self.__fusion = bmd.scriptapp("Fusion")
    #     except:
    #         print("Can't run in fusion, no fusion is open!")
    #         return False
    #     if self.__fusion:
    #         self.__fusion.LoadComp(self.comp_path, True)
    #         self.__composition.Render()
    # else:
    #     self.submitToRR()









# def Run(fusion=None,_input=None,_output=None,_file=None,submit=True,project_name="MiasMagic2",user=None):
#     create_class = CreatePreviewInsideFusion(fusion=fusion, _input=_input, _output=_output, comp_file=_file,project_name=project_name,user=user)
#     create_class.run(submit=submit)
#
# def RunOutsideFusion(_input=None,_output=None,preview_file=None,comp_file=None,project_name="MiasMagic2",user=None,submit=True,shot_info={}):
#     duration = GetDurationFromFile(comp_file=comp_file)
#     DuplicateTemplate(dest_path=preview_file)
#     replaceInTemplate(input_path=_input,output_path=_output,preview_comp_file=preview_file,duration=duration)
#     if shot_info:
#         ep = shot_info["episode_name"]
#         sq = shot_info["seq_name"]
#         sh = shot_info["shot_name"]
#     else:
#         ep=None
#         sq=None
#         sh=None
#     if submit:
#         submitToRR(project_name=project_name,user=user,comp_path=preview_file,ep=ep,sq=sq,sh=sh)
#     else:
#         from distutils import spawn
#         does_frn_exists = spawn.find_executable(
#             "FusionRenderNode.exe")  # check if this is set in the env path/installed so we can call on it.
#         if does_frn_exists:
#             cmd_line = 'FusionRenderNode.exe %s /quiet /clean /render /quit' % preview_file
#         else:
#             cmd_line = 'Fusion.exe %s /quiet /clean /render /quit' % preview_file
#         subprocess.Popen(cmd_line, shell=True)
