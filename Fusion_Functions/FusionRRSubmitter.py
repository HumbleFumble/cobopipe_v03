import os
import subprocess
import shutil
from sys import stderr
#from Preview.comp import createBatchScript


# c_path = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E01/"
# content = os.listdir(c_path)
# for con in content:
# 	if not con.startswith(".DS_"):
# 		print ("%s And so on" % con)
#

def RenderSubmitInfo(project_name="MIA2_Fusion",client_pool="CompNodes",project_path=None, user_name="Bernardo", render_file=None, episode=None, sequence=None, shot=None, single_out=False, waitForJobID=None):
	# render_file = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E02/E02_SQ020/E02_SQ020_SH010/03_Comp/E02_SQ020_SH020_001.comp"
	# project_name = "FusionRender" #FusionRender
	# client_pool = "CompNodes"
	# user_name = self.user_dd.currentText()
	# user_name = "mmcb"
	# project_path = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/"
	overwrite = True
	software = "fusion"
	render_software = "fusion"
	# software_version = "9.0.2"
	software_version = "17.4.3"

	# rr_submitter = "P:/tools/RoyalRender/bin/win64/rrSubmitter.exe"
	rr_submitter = "%RR_Root%/bin/win64/rrSubmitterconsole.exe"
	rr_cmd = "%s %s" % (rr_submitter, render_file)  # Set scene
	# FLAGS
	# rr_cmd = '%s -NoAutoSceneRead' % (rr_cmd)  # set flag that so rr doesn't parse through maya scene
	if overwrite:
		rr_cmd = "%s -AutoDeleteEnabled" % (
			rr_cmd)  # set flag so rr deletes all files that it is suppose to render over

	# SCENE INFO

	rr_cmd = "%s -S %s" % (rr_cmd, software)  # set software
	# rr_cmd = "%s -R %s" % (rr_cmd, render_software)  # set render plugin
	rr_cmd = "%s -V %s" % (rr_cmd, software_version)  # set software version

	rr_cmd = "%s -SOS win" % (rr_cmd)  # set os
	rr_cmd = '%s -DB %s' % (rr_cmd, project_path)  # set project

	if single_out:
		rr_cmd = '%s -ImageSingleOutputFile' % (rr_cmd)  # set only one machine render
	# rr_cmd = "%s -SLO 1" % (rr_cmd)  # set layer
	# rr_cmd = '%s -SLO "** All **    (watch EXR_1)"' % (rr_cmd)  # set layer

	if waitForJobID:
		rr_cmd ='%s -WWID %s' % (rr_cmd,waitForJobID)

	# # Submitter flags:
	scene_name = render_file.split("/")[-1].split(".")[0]
	rr_cmd = '%s "CSCN=0~%s"' % (rr_cmd, scene_name) #set scene name
	rr_cmd = '%s "CSQN=0~%s"' % (rr_cmd, episode) #set episode name

	rr_cmd = '%s "CSHN=0~%s"' % (rr_cmd, sequence)
	rr_cmd = '%s "CVN=0~%s"' % (rr_cmd, shot)

	rr_cmd = '%s "UN=0~%s"' % (rr_cmd, user_name)  # set user name

	rr_cmd = '%s "CropEXR=1~0"' % (rr_cmd)
	rr_cmd = '%s "PreviewGamma2.2=1~1"' % (rr_cmd)  # set preview gamma correctly
	rr_cmd = '%s "PPCreateSmallVideo=1~0"' % (rr_cmd)  # create small video 0/1
	rr_cmd = '%s "CPN=0~%s"' % (rr_cmd, project_name)  # set project "nice" name
	rr_cmd = '%s "DCG=0~%s"' % (rr_cmd, client_pool)  # set client pool
	rr_cmd = '%s "Priority=1~75"' % (rr_cmd)  # set user name
	# rr_cmd = '%s "UN=0~%s"' % (rr_cmd, user_name)  # set user name
	print(rr_cmd)
	print("Scene Submitted to RoyalRender!")
	return rr_cmd
# RenderSubmitInfo()

def run(fusion=None):
	__fusion = fusion
	cur_comp = __fusion.GetCurrentComp()
	import Fusion_Functions.gpuDisable
	Fusion_Functions.gpuDisable.run(cur_comp)
	cur_comp.Save()
	comp_name = cur_comp.GetAttrs("COMPS_Name")
	name_parts = comp_name.split("_")
	CC = None
	ep = name_parts[0]
	sq = name_parts[1]
	sh = name_parts[2]
	shotname = ep + '_' + sq + '_' + sh

	from Fusion_Functions.getProjectAndUserInfo import askUserInfo
	ask_input = askUserInfo(cur_comp)
	if ask_input:
		project, user = ask_input
		from getConfig import getConfigClass
		CC = getConfigClass(project_name=project)
		print(CC.base_path)
		project_path = CC.get_base_path()
		project_name = project + "_Fusion"
	else:
		project_path = "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/"
		user = "Comp"
		project_name = "MiasMagic2_Fusion"
	submit_type, render_local = submitWindow(cur_comp)
	if submit_type not in [0, 1, 2]:
		return False

	render_file = (cur_comp.GetAttrs("COMPS_FileName")).replace("\\", "/")
	jobID = None


	if submit_type in [0,1]:
		if render_local:
			cur_comp.Render()
		else:
			sub_cmd = RenderSubmitInfo(project_name=project_name, client_pool="CompNodes", project_path=project_path,
									   user_name=user, render_file=render_file, episode=ep, sequence=sq, shot=sh)
			proc = subprocess.Popen(sub_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			stdoutdata, stderrdata = proc.communicate()
			#print(str(stdoutdata))
			jobID = stdoutdata[-36:-16]
			jobID = jobID.decode("utf-8")

	if CC and submit_type in [0,2]:
		from runInPython3 import runInPython3
		from Preview.general import getPreview
		if render_local:
			result = runInPython3(getPreview, shotname, type='comp', force=True, local=True, user=user, waitForJobID=jobID)
		else:
			result = runInPython3(getPreview, shotname, type='comp', force=True, local=False, user=user, waitForJobID=jobID)
		print(result)


def createCompPreview(comp_file=None,preview_file=None,_input=None,_output=None):
	import Fusion_Functions.CreateMovFromStack as fusion_preview
	# Comp Preview
	duration = fusion_preview.GetDurationFromFile(comp_file=comp_file)
	fusion_preview.DuplicateTemplate(dest_path=preview_file)
	fusion_preview.replaceInTemplate(input_path=_input, output_path=_output, preview_comp_file=preview_file, duration=duration)


def submitWindow(cur_comp):
	from Maya_Functions.file_util_functions import saveJson, loadJson
	fusion_user_data = "C:/Temp/fusion_user_data.json"
	cur_data = loadJson(fusion_user_data)
	submit_default = 0
	check_local_default = 0
	if cur_data:
		print(cur_data)
		if "submitDrop" in cur_data.keys():
			submit_default = cur_data["submitDrop"]
		if "checkbox_local" in cur_data.keys():
			check_local_default = cur_data["checkbox_local"]
	submit_dropdown = {1: "submitDrop", "Name": "Render:", 2: "Dropdown",
					   "Options": ["Comp + Preview", "Comp Only", "Preview Only"], "Default": submit_default}
	check_box_local = {1: "checkbox_local", "Name": "Render Locally", 2: "Checkbox",
					   "Default": check_local_default}
	dialog = {1: submit_dropdown, 2: check_box_local}
	ret = cur_comp.AskUser("Submit Options:", dialog)
	if ret:
		print(ret.values())
		submit_type = int(ret.values()[0])
		render_local = int(ret.values()[1])
		cur_data["submitDrop"] = submit_type
		cur_data["checkbox_local"] = render_local
		saveJson(fusion_user_data, cur_data)
		return submit_type, render_local
	return False, False


def runOutsideFusion(project_name,project_path,render_file,user,episode,sequence,shot, single_out=False,waitForJobID=None):
	sub_cmd = RenderSubmitInfo(project_name=project_name, client_pool="CompNodes", project_path=project_path,
							   user_name=user, render_file=render_file, episode=episode, sequence=sequence,
							   shot=shot,single_out=single_out, waitForJobID=waitForJobID)
	proc = subprocess.Popen(sub_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdoutdata, stderrdata = proc.communicate()
	jobID = stdoutdata[-36:-16] # Returning JobID
	# print(stdoutdata)
	# print("GOT JOB ID: %s" % str(jobID))
	return jobID.decode("utf-8")





#OUTDATED TESTING TESTING
def RenderSubmitTest(render_file, episode,sequence,shot, wait_id, use_console):
	# render_file = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E02/E02_SQ020/E02_SQ020_SH010/03_Comp/E02_SQ020_SH020_001.comp"
	project_name = "FusionRender" #FusionRender
	client_pool = "CompNodes"
	# user_name = self.user_dd.currentText()
	user_name = "mmcb"
	project_path = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/"
	overwrite = True

	software = "fusion"
	render_software = "fusion"
	software_version = "9.0.2"

	if use_console:
		rr_submitter = "%RR_Root%/bin/win64/rrSubmitterconsole.exe"
	else:
		rr_submitter = "%RR_Root%/bin/win64/rrSubmitter.exe"
	rr_cmd = "%s %s" % (rr_submitter, render_file)  # Set scene
	# FLAGS
	# rr_cmd = '%s -NoAutoSceneRead' % (rr_cmd)  # set flag that so rr doesn't parse through maya scene
	if overwrite:
		rr_cmd = "%s -AutoDeleteEnabled" % (
			rr_cmd)  # set flag so rr deletes all files that it is suppose to render over
	# SCENE INFO
	rr_cmd = "%s -S %s" % (rr_cmd, software)  # set software
	# rr_cmd = "%s -R %s" % (rr_cmd, render_software)  # set render plugin
	rr_cmd = "%s -V %s" % (rr_cmd, software_version)  # set software version

	rr_cmd = "%s -SOS win" % (rr_cmd)  # set os
	rr_cmd = '%s -DB %s' % (rr_cmd, project_path)  # set project
	if wait_id:
		rr_cmd = '%s -WWID %s' % (rr_cmd, wait_id)  # set wait id
	if render_file.endswith(".mov"):
		rr_cmd = '%s -ISO 1' % (rr_cmd)  # set wait id


	# rr_cmd = "%s -SLO 1" % (rr_cmd)  # set layer
	# rr_cmd = '%s -SLO "** All **    (watch EXR_1)"' % (rr_cmd)  # set layer

	# # Submitter flags:
	rr_cmd = '%s "CSCN=0~%s"' % (rr_cmd, episode)  # set height

	rr_cmd = '%s "CSHN=0~%s"' % (rr_cmd, sequence)  # set height
	rr_cmd = '%s "CVN=0~%s"' % (rr_cmd, shot)  # set height

	rr_cmd = '%s "CropEXR=1~0"' % (rr_cmd)  # set height

	rr_cmd = '%s "CPN=0~%s"' % (rr_cmd, project_name)  # set project "nice" name
	rr_cmd = '%s "DCG=0~%s"' % (rr_cmd, client_pool)  # set client pool
	rr_cmd = '%s "Priority=1~75"' % (rr_cmd)  # set user name
	# rr_cmd = '%s "UN=0~%s"' % (rr_cmd, user_name)  # set user name
	print(rr_cmd)
	print("Scene Submitted to RoyalRender!")
	c_p = subprocess.Popen(rr_cmd, shell=False, universal_newlines=True, stdout=subprocess.PIPE)
	stdout = c_p.communicate()[0]
	print(stdout)
	# print(stdout.splitlines()[-4:-1])
	job_id = stdout.splitlines()[-2].split(" ")[-4]
	# print(job_id)
	return job_id

	# return rr_cmd

def script_content(_input,_output,duration):
	content = """composition: Execute("!Py2: comp.Lock()
cur_loader = comp.Loader()
cur_saver = comp.Saver()
cur_loader.Clip = '%s'
cur_saver.Clip = '%s'
comp.SetAttrs({'COMPN_RenderStartTime': 1})
comp.SetAttrs({'COMPN_RenderEnd': %s})
save_con = cur_saver.FindMainInput(1)
save_con.ConnectTo(cur_loader.Output)
comp.Save()
comp.Unlock()")""" % (_input, _output,duration)
	content = ";".join(content.split("\n"))
	return content

def CreateQuicktimeCompFile():
	template_location = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Pipeline/Templates/Fusion_Quicktime_Render.comp"
	quick_file = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E08/E08_SQ020/E08_SQ020_SH010/03_Comp/E08_SQ020_SH010_Quicktime.comp"
	passes_folder = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E08/E08_SQ020/E08_SQ020_SH010/Passes/"
	if os.path.exists(passes_folder):
		passes_content = os.listdir(passes_folder)
		if not passes_content == []:
			c_list = []
			if "Color" in passes_content:
				exr_list = os.listdir("%s/Color/" % passes_folder)
			else:
				exr_list = os.listdir("%s/%s/" % (passes_folder,passes_content[0]))
				# c_list = []

			for c in exr_list:
				if c.endswith(".exr"):
					c_list.append(c)
			duration = len(c_list) - 1
	else:
		duration = 2


	_output = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E08/E08_SQ020/_Rushes/E08_SQ020_SH010.mov"
	_input = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E08/E08_SQ020/E08_SQ020_SH010/05_CompOutput/E08_SQ020_SH010_0001.exr"

	shutil.copy(template_location,quick_file)
	script_path = "%s.lua" % quick_file.split(".comp")[0]
	script_file = open(script_path, "w+")
	in_script = script_content(_input, _output,duration)
	script_file.write(in_script)
	script_file.close()
	subprocess.Popen("Fusion %s" % quick_file)


#"C:\Program Files\Blackmagic Design\Fusion 17\Fusion.exe" "\\dumpap2\projekter\_WFH_Projekter\930486_MiaMagicPlayground_S3-4\4_Production\_Temp\Test_Render_Comp.comp" /render /start 1 /end 2 /step 1 /quit /quietlicense /clean /cleanlog /log "C:\RR_localdata\temp\A\fusion.log"
#"C:\Program Files\Blackmagic Design\Fusion 17\Fusion.exe" "\\dumpap2\projekter\_WFH_Projekter\930486_MiaMagicPlayground_S3-4\4_Production\_Temp\Test_Render_Comp.comp" /render /start 1 /end 2 /step 1 /quietlicense


# _output = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E08/E08_SQ020/_Rushes/E08_SQ020_SH010.mov"
# _input = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E08/E08_SQ020/E08_SQ020_SH010/05_CompOutput/E08_SQ020_SH010_0001.exr"
#
#
#
# render_file = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E08/E08_SQ020/E08_SQ020_SH010/03_Comp/E08_SQ020_SH010_001.comp"
# quick_file = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E08/E08_SQ020/E08_SQ020_SH010/03_Comp/E08_SQ020_SH010_Quicktime.comp"
#
#
# job_id = RenderSubmitTest(render_file, "E08","SQ020", "SH010", None, True)
# # CreateQuicktimeCompFile()
# job_id = RenderSubmitTest(quick_file, "E08","SQ020", "SH010", job_id, True)




