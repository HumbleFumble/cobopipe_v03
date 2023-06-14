import os
import Deadline.util as deadutil
import random
import string
from getConfig import getConfigClass

CC = getConfigClass()

def submit(fusion):

	# COMPS_Name = QuickSubmitTest.comp
	# COMPN_GlobalStart = 1
	# COMPN_RenderStartTime = 1
	# COMPN_RenderEndTime = 35



    cur_comp = fusion.GetCurrentComp()

    job_name = cur_comp.GetAttrs("COMPS_Name").split(".")[0]
    render_start = cur_comp.GetAttrs("COMPN_RenderStart")     # COMPN_RenderStart = 1
    render_end = cur_comp.GetAttrs("COMPN_RenderEnd")     # COMPN_RenderEnd = 35
    pool = CC.project_settings.get("deadline_pool")


    priority=50
    frame_range = f"{render_start}-{render_end}"
    comp_path = (cur_comp.GetAttrs("COMPS_FileName")).replace("\\", "/")

    # userName = ""




    job_lines = [
        f"Name={job_name}", #Name=QuickSubmitTest.comp
        f"Frames={frame_range}", # Frames=1-35
        f"Pool={pool}",
        f"Group=fusion",
        f"Priority={priority}",
        f"OverrideTaskExtraInfoNames=False",
        f"Plugin=Fusion"
        # f"UserName={userName}"
    ]
    # ChunkSize=10
    # MachineLimit=1 #Only use for movs?

    # f"OutputDirectory0={output_directory}",  # OutputDirectory0=P:\930435_Liva_og_De_Uperfekte\Teaser\Film\S101\S101_SQ010\_Preview
    # f"OutputFilename0={output_filename}",  # OutputFilename0=S101_SQ010_SH070_Comp????.png / # OutputFilename1=S101_SQ010_SH070_Comp.mov
    current_outputs = findActiveSavers(cur_comp)
    single =False
    for number,out in enumerate(current_outputs):
        if checkSingleOutput(out):
            single = True

        out_dir = f"OutputDirectory{number}={os.path.dirname(out)}"
        try:
            int(out.split(".")[0][-4:])
        except:
            pass #ADD FRAME PADDING WITH "?"

        out_path = f"OutputFilename{number}={out}"
        job_lines.append(out_dir)
        job_lines.append(out_path)

    if single:
        job_lines.append(f"MachineLimit=1")
        job_lines.append(f"ChunkSize={render_end}")







    tempFolder = deadutil.callDeadlineCommand("-GetCurrentUserHomeDirectory")
    tempFolder = trim(tempFolder)
    tempFolder = os.path.join(tempFolder, "temp")
    random_string = ''.join(random.choice(string.ascii_lowercase + '0123456789') for i in range(6))

    # pluginInfoFilePath = pluginInfoFile(tempFolder=tempFolder,random_string=random_string,comp_path=comp_path)

    jobInfoFilePath = os.path.join(tempFolder, f"fusion_submit_info_{random_string}.job")
    for f in job_lines:
        print(f)

    # with open(jobInfoFilePath, "w") as f:
    #     for line in job_lines:
    #         f.write(f"{line}\n")

    # deadutil.callDeadlineCommand(jobInfoFilePath, pluginInfoFilePath)
def checkSingleOutput(output):
    ext = output.split(".")
    if ext in ["jpg","png","exr","tiff","tga"]:
        return True
    else:
        return False

def findActiveSavers(cur_comp):
    all_savers = cur_comp.GetToolList(False, "Saver").values()
    all_outputs = []
    for saver in all_savers:
        if not saver.GetAttrs()["TOOLB_PassThrough"]:
            # print(saver.GetAttrs())
            full_output = saver.Clip[0]
            all_outputs.append(full_output)
    return all_outputs






def pluginInfoFile(
    tempFolder,
    random_string,
    comp_path,
):
    pluginInfoFilePath = os.path.join(tempFolder, f"maya_plugin_info_{random_string}.job")

    lines = [
        f"Build=None",
        f"CheckOutput=False",
        f"FlowFile={comp_path}",
        f"HighQuality=False",
        f"Proxy=1",
        f"Version=18"
    ]

    with open(pluginInfoFilePath, "w") as f:
        for line in lines:
            f.write(f"{line}\n")

    return pluginInfoFilePath

def trim(_string):
    return _string.replace("\n", "").replace("\r", "")

# JOB_INFO Both types
# Denylist=
# EventOptIns=
# Frames=1-35
# Group=fusion
# MachineName=WSX12
# Name=QuickSubmitTest.comp
# OutputDirectory0=P:\930435_Liva_og_De_Uperfekte\Teaser\Film\S101\S101_SQ010\_Preview
# OutputDirectory1=P:\930435_Liva_og_De_Uperfekte\Teaser\Film\S101\S101_SQ010\_Preview
# OutputFilename0=S101_SQ010_SH070_Comp????.png
# OutputFilename1=S101_SQ010_SH070_Comp.mov
# OverrideTaskExtraInfoNames=False
# Plugin=Fusion
# Pool=liva-journey
# Region=
# ScheduledStartDateTime=14/06/2023 12:17
# UserName=cg

# PLUGIN_INFO
# Build=None
# CheckOutput=False
# FlowFile=P:\930435_Liva_og_De_Uperfekte\Teaser\Film\S101\S101_SQ010\S101_SQ010_SH070\03_Comp\QuickSubmitTest.comp
# HighQuality=False
# Proxy=1
# Version=18



#Stack option
# Denylist=
# EventOptIns=
# Frames=1-35
# Group=fusion
# MachineName=WSX12
# Name=QuickSubmitTest_stack.comp
# OutputDirectory0=P:\930435_Liva_og_De_Uperfekte\Teaser\Film\S101\S101_SQ010\_Preview
# OutputFilename0=S101_SQ010_SH070_Comp????.jpg
# OverrideTaskExtraInfoNames=False
# Plugin=Fusion
# Pool=liva-journey
# Region=
# ScheduledStartDateTime=14/06/2023 12:43
# UserName=cg


#EXTRA DRAFT MOV?
# BatchName=QuickSubmitTest.comp
# Denylist=
# EventOptIns=
# ExtraInfoKeyValue0=SubmitQuickDraft=True
# ExtraInfoKeyValue1=DraftExtension=mov
# ExtraInfoKeyValue2=DraftType=movie
# ExtraInfoKeyValue3=DraftResolution=1
# ExtraInfoKeyValue4=DraftCodec=h264
# ExtraInfoKeyValue5=DraftQuality=85
# ExtraInfoKeyValue6=DraftFrameRate=25
# ExtraInfoKeyValue7=DraftColorSpaceIn=Identity
# ExtraInfoKeyValue8=DraftColorSpaceOut=Identity
# Frames=1-35
# Group=fusion
# MachineName=WSX12
# Name=QuickSubmitTest.comp
# OutputDirectory0=P:\930435_Liva_og_De_Uperfekte\Teaser\Film\S101\S101_SQ010\_Preview
# OutputFilename0=S101_SQ010_SH070_Comp????.jpg
# OverrideTaskExtraInfoNames=False
# Plugin=Fusion
# Pool=liva-journey
# Region=
# ScheduledStartDateTime=14/06/2023 12:48
# UserName=cg
# ChunkSize=10
# MachineLimit=1 #Only use for movs?