### A script to make a collected movie of a sequence or a selection of shots ###
### Needs ffmpeg to be installed and set in env path to work ###
###

#TODO Remove movie path hardcoding and replace with configClass paths.

from PySide2 import QtWidgets, QtCore, QtGui
try:
    import maya.cmds as cmds
    in_maya = True

except:
    from PySide2 import QtWidgets, QtCore, QtGui
    in_maya = False

from getConfig import getConfigClass
CC = getConfigClass()


import os
import subprocess
import re

if in_maya:
	import MayaDockable
	import reloadModules


class MainWindow(QtWidgets.QWidget):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setObjectName("HookUp Playblasts")
		self.setWindowTitle("HookUp Playblasts")
		self.setWindowFlags(QtCore.Qt.Window)
		self.onlyInt = QtGui.QIntValidator()
		self.film_path = CC.get_film_path() #.CreatePathFromDict(cfg.project_paths["film_path"])
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


	# def RunScenePublish(self):
	# 	if in_maya:
	# 		cmds.file(save=True)
	# 	self.pub_class.RunInMayaPy()

	def CreateWindow(self):
		self.main_layout = QtWidgets.QVBoxLayout()
		self.top_button_layout = QtWidgets.QHBoxLayout()
		self.bot_button_layout = QtWidgets.QVBoxLayout()

		self.list_layout = QtWidgets.QHBoxLayout()
		self.episode_label = QtWidgets.QLabel("Episode: ")

		self.episode_dd = QtWidgets.QComboBox()

		self.top_button_layout.addWidget(self.episode_label)

		self.top_button_layout.addWidget(self.episode_dd)

		self.seq_label = QtWidgets.QLabel("SQ: ")

		self.seq_dd = QtWidgets.QComboBox()
		self.top_button_layout.addWidget(self.seq_label)

		self.top_button_layout.addWidget(self.seq_dd)

		# widgets
		self.shot_list = QtWidgets.QListWidget()
		self.shot_list.setSelectionMode(QtWidgets.QListWidget.ExtendedSelection)
		self.list_layout.addWidget(self.shot_list)

		self.shot_list.itemDoubleClicked.connect(self.ShotDoubleClicked)
		# self.asset_list.itemDoubleClicked.connect(self.DoubleClickOnAsset)

		self.hookup_selected_button = QtWidgets.QPushButton("Hook-up Selected")
		self.hookup_selected_button.clicked.connect(self.HookUp_Selected)

		self.hookup_seq_button = QtWidgets.QPushButton("Hook-up Sequence")
		self.hookup_seq_button.clicked.connect(self.HookUp_Seq)
		self.open_folder_button = QtWidgets.QPushButton("Open Playblast Folder")
		self.open_folder_button.clicked.connect(self.OpenFolder)

		self.bot_button_layout.addWidget(self.hookup_selected_button)
		self.bot_button_layout.addWidget(self.hookup_seq_button)
		self.bot_button_layout.addWidget(self.open_folder_button)



		# Connect layouts
		self.main_layout.addLayout(self.top_button_layout)

		self.main_layout.addLayout(self.list_layout)
		self.main_layout.addLayout(self.bot_button_layout)

		self.setLayout(self.main_layout)

	def OpenFolder(self):
		self.sequence_path = "%s/%s/%s/" % (self.film_path, self.episode_dd.currentText(), self.seq_dd.currentText())
		playblast_path = "%s/_Preview/" % (self.sequence_path)
		os.startfile(playblast_path)

	def ShotDoubleClicked(self, cur_shot):
		cur_shot=cur_shot.text()
		self.sequence_path = "%s/%s/%s/" % (self.film_path, self.episode_dd.currentText(), self.seq_dd.currentText())
		playblast_path = "%s/_Preview/" % (self.sequence_path)
		preview_content = os.listdir(playblast_path)
		notFound=True
		for p_con in preview_content:
			if cur_shot in p_con and notFound:
				p_con_path = "%s/%s" % (playblast_path, p_con)
				os.startfile(p_con_path)
				notFound = False
		if notFound:
			animatic_path = "%s/%s/%s_Animatic.mov" % (self.sequence_path, cur_shot, cur_shot)
			os.startfile(animatic_path)

	def GetSelected(self):
		temp_shot_list = self.shot_list.selectedItems()
		return_list = []
		for shot in temp_shot_list:
			return_list.append(shot.text())
		return sorted(return_list)

	def MakeHookup(self, shot_list, hookup_name):
		self.sequence_path = "%s/%s/%s/" % (self.film_path, self.episode_dd.currentText(), self.seq_dd.currentText())
		playblast_path = "%s/_Preview/" % (self.sequence_path)

		hook_up_txt = "%s/hook_up.txt" % (playblast_path)

		hook_up_list = []
		outFile = open(hook_up_txt, "w")  # create the txt file

		preview_content = os.listdir(playblast_path)
		for shot in shot_list:
			notFound = True
			for p_con in preview_content:
				if shot in p_con and notFound:
					p_con_path = "%s/%s" % (playblast_path, p_con)
					convert_to_pro_res = """ffmpeg -i %s -c:v prores_ks -profile:v 0 -ar 44100 -ac 1 -acodec mp3 -y %s""" % (
						p_con_path, "%s/%s_HookUpTemp.mov" % (playblast_path, shot))
					notFound = False
			if notFound:
				animatic_path = "%s/%s/%s_Animatic.mov" % (self.sequence_path, shot, shot)
				convert_to_pro_res = """ffmpeg -i %s -c:v prores_ks -profile:v 0 -ar 44100 -ac 1 -acodec mp3 -y %s""" % (
					animatic_path, "%s/%s_HookUpTemp.mov" % (playblast_path, shot))
			hook_up_list.append("%s/%s_HookUpTemp.mov" % (playblast_path, shot))
			subprocess.call(convert_to_pro_res, shell=False)
			outFile.write("file '%s_HookUpTemp.mov'\n" % (shot))

		outFile.close()

		hook_up_collect = "%s%s.mov" % (playblast_path, hookup_name)  # (ffmpeg PATH)
		prores_quality = 1
		hook_up_cmd = """ffmpeg -f concat -safe 0 -i %s -s 1280:720 -c:a copy -c:v prores_ks -profile:v %s -crf 0 -y %s""" % (
			hook_up_txt, prores_quality, hook_up_collect)
		subprocess.call(hook_up_cmd, shell=False)

		# cleanup!
		for hookup in hook_up_list:
			os.remove(hookup)
		os.remove(hook_up_txt)

		print("Hookup Created!")
		os.startfile(hook_up_collect)

	def HookUp_Seq(self):
		self.shot_list.selectAll()
		self.MakeHookup(self.GetSelected(), "%s_HookUp" % (self.seq_dd.currentText()))

	def HookUp_Selected(self):
		my_shots = self.GetSelected()
		start = (my_shots[0]).split("_")[-1]
		end = (my_shots[-1]).split("_")[-1]
		self.MakeHookup(my_shots, "%s_%s-%s_HookUp" % (self.seq_dd.currentText(), start, end))

	def FindEpisode(self,content):
		low_case = content.lower()
		re_compile = re.compile(CC.episode_regex) #re.compile("^(e)\d{2}$")
		if re_compile.search(low_case):
			# print(content + " matches!")
			return True
		else:
			return False

	def FindSequence(self, content):
		low_case = content.lower()
		re_compile = re.compile(CC.seq_regex)#re.compile("^(e)\d{2}(_sq)\d{3}$")
		if re_compile.search(low_case):
			# print(content + " matches!")
			return True
		else:
			return False

	def FindShot(self,content):
		low_case = content.lower()
		re_compile = re.compile(CC.shot_regex)#re.compile("^(e)\d{2}(_sq)\d{3}(_sh)\d{3}$")
		if re_compile.search(low_case):
			# print(content + " matches!")
			return True
		else:
			return False

def _maya_main_window():
	"""Return Maya's main window"""
	for obj in QtWidgets.QApplication.topLevelWidgets():
		if obj.objectName() == 'MayaWindow':
			return obj
	raise RuntimeError('Could not find MayaWindow instance')


def Run():
	objectName = 'ShotHookupDock'
	if not MayaDockable.dockableExists(objectName):
		MayaDockable.runDockable(objectName, 'Shot Hookup', MainWindow())

	# mainWin = MainWindow(parent=_maya_main_window())
	# mainWin.show()


def FindObjectByName(name):
	# widget = QtWidgets.QApplication.instance().topLevelWidgets()
	widget = QtWidgets.QApplication.instance().allWidgets()
	widget = widget + QtWidgets.QApplication.instance().allWindows()
	QtWidgets.QApplication.instance().allWindows()
	# QtWidgets.QListView.objectName().__str__()
	for x in widget:
		if str(x.objectName()) == name:
			# print("WORKS! %s" % x.objectName())
			return x
	return False


if not in_maya:

	if __name__ == '__main__':
		import sys
		if not QtWidgets.QApplication.instance():
			app = QtWidgets.QApplication(sys.argv)
		else:
			app = QtWidgets.QApplication.instance()
		mainWin = MainWindow()
		# mainWin.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
		# mainWin.setFixedSize(584, 662)
		# mainWin.resize(584, 662)
		# print(QtWidgets.qApp.topLevelWidgets())

		mainWin.show()

		sys.exit(app.exec_())
