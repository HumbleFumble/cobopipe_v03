from Log.CoboLoggers import getLogger
logger = getLogger()

from PySide2 import QtWidgets, QtCore, QtGui
from getConfig import getConfigClass
CC = getConfigClass()

import pprint
pp = pprint.PrettyPrinter(indent=4)
import os
import subprocess
import shutil
import re




class RepositoryFactory(object):
    """Creates repository type objects"""

    def __init__(self, filmPath):
        self.__filmPath = filmPath
        self.__footage_dict = {}

    def __createEpisodes(self):
        dirs = os.listdir(self.__filmPath)
        result = []
        for episodename in dirs:
            # if not "E" in episodename or len(episodename) > 3:
            #     continue
            if not self.FindEpisode(episodename):
                continue
            episode = Node(episodename, self.__filmPath + "/" + episodename, None,"episode")

            self.__footage_dict[episodename] = {}
            self.__footage_dict[episodename]["object"] = episode
            self.__footage_dict[episodename]["children"] = []
            self.__footage_dict[episodename]["parent"] = None
            self.__footage_dict[episodename]["type"] = "episode"

            episode.append(self.__createSequences(episode))
            result.append(episode)
            episode.setChildren(self.__footage_dict[episodename]["children"])

        return result

    def __createSequences(self, episode):
        dirs = os.listdir(episode.getUrl())
        result = []
        for sequencename in dirs:
            # if "PREVIS" in sequencename or "TEST" in sequencename:
            #     continue
            if not self.FindSequence(sequencename):
                continue

            sequence = Node(sequencename, episode.getUrl() + "/" + sequencename, episode,"sequence")
            self.__footage_dict[episode.getName()]["children"].append(sequence)
            self.__footage_dict[sequencename] = {}
            self.__footage_dict[sequencename]["object"] = sequence
            self.__footage_dict[sequencename]["type"] = "seq"
            self.__footage_dict[sequencename]["children"] = []
            self.__footage_dict[sequencename]["parent"] = episode

            sequence.append(self.__createShots(sequence))
            sequence.setChildren(self.__footage_dict[sequencename]["children"])
            result.append(sequence)

        return result

    def __createShots(self, sequence):
        dirs = os.listdir(sequence.getUrl())
        result = []
        for shotname in dirs:
            # if "Preview" in shotname or "PREVIS" in shotname:
            #     continue
            if not self.FindShot(shotname):
                continue

            shot = Node(name=shotname, url=sequence.getUrl() + "/" + shotname, parent=sequence,type="shot")

            self.__footage_dict[shotname] = {}
            self.__footage_dict[sequence.getName()]["children"].append(shot)
            self.__footage_dict[shotname]["object"] = shot
            self.__footage_dict[shotname]["type"] = "shot"
            self.__footage_dict[shotname]["children"] = []
            self.__footage_dict[shotname]["parent"] = sequence

            result.append(shot)

        return result

        # REGEX FOR CHECKING FOLDER NAMES:

    def FindEpisode(self, content):
        # test = "^(s)\d{3}$"
        low_case = content.lower()
        # re_compile = re.compile("^(s)\d{3}$")
        re_compile = re.compile("%s$" % CC.episode_regex)
        if re_compile.search(low_case):
            return True
        else:
            return False

    def FindSequence(self, content):
        low_case = content.lower()
        re_compile = re.compile("%s%s$" % (CC.episode_regex, CC.seq_regex))
        if re_compile.search(low_case):
            return True
        else:
            return False

    def FindShot(self, content):
        low_case = content.lower()
        # re_compile = re.compile("^(s)\d{3}(_sq)\d{3}(_sh)\d{3}$")
        re_compile = re.compile(
            "%s%s%s$" % (CC.episode_regex, CC.seq_regex, CC.shot_regex))
        if re_compile.search(low_case):
            return True
        else:
            return False

    def create(self):
        # Create episode objects
        episodes = self.__createEpisodes()
        repository = Repository(episodes, self.__footage_dict)
        return repository

class Node(object):
    def __init__(self, name=None, url=None, parent=None, type=None):
        self.__name = name
        self.__url = url
        self.__parent = parent
        self.__children = []
        self._row = 0
        self.__type = type
        self.comp_style = CC.project_style["default_comp_style"]
        self.animation_style = CC.project_style["default_animation_style"]

    def getInfoDict(self):
        shot_dict = {}
        if self.__type == "episode":
            shot_dict = {}
            shot_dict["episode_name"] = self.__name
        if self.__type == "seq":
            shot_dict = {}
            shot_dict["episode_name"], shot_dict["seq_name"] = self.__name.split("_")
        if self.__type == "shot":
            shot_dict = {}
            shot_dict["episode_name"], shot_dict["seq_name"], shot_dict["shot_name"] = self.__name.split("_")
        return shot_dict

    def getPassesFolder(self):
        return "%s/Passes/" % self.__url

    def getAnimationStyle(self):
        return self.animation_style

    def getCompStyle(self):
        return self.comp_style

    def setAnimationStyle(self, animation_style):
        self.animation_style = animation_style

    def setCompStyle(self, comp_style):
        self.comp_style = comp_style

    def getType(self):
        return self.__type

    def append(self, c_obj):
        self.__children.append(c_obj)
        self._row = 0
        # self._row = len(self.__children)

    def child(self, in_row):  # Treeview
        if in_row >= 0 and in_row < len(self.__children):
            return self.__children[in_row]

    def row(self):  # Treeview
        return self._row

    def getName(self):
        return self.__name

    def getUrl(self):
        return self.__url

    def getParent(self):
        return self.__parent

    def setChildren(self, c_list=None):
        self.__children = c_list
        self._row = len(self.__children)

    def getChildren(self):
        return self.__children

    def getAllChildren(self,cur_node=None):
        if not cur_node:
            cur_node = self
        return_list = []
        for child in cur_node.getChildren():
            if child.getType() =="shot":
                return_list.append(child)
            else:
                return_list.extend(self.getAllChildren(child))
        return return_list

class Repository(Node):
    """Holds all episodes and higher methods for retrieving specific data: Directly contains 'Episode' objects"""

    def __init__(self, content, content_dict):
        self.__content = content
        self.__content_dict = content_dict

    def getEpisode(self, name):
        return self.__content_dict[name]["children"]

    def getType(self, name):
        return self.__content_dict[name]["type"]

    def GetByParent(self, parent_name, recursive_look=False):
        if recursive_look:
            pass
        return self.__content_dict[parent_name]["children"]

    def GetByName(self, name):
        if name in self.__content_dict.keys():
            return self.__content_dict[name]
        else:
            return None

    def GetByFilter(self, name_filter=None, type_filter=None, parent_filter=None):
        return_list = []
        filter_list = [name_filter, type_filter, parent_filter]
        for c_con in self.__content_dict.keys():
            if name_filter:
                if not name_filter in c_con:
                    continue
                    # key_list.append(c_con)
            if type_filter:
                if not self.__content_dict[c_con]["type"] == type_filter:
                    continue
                    # key_list.append(c_con)
            if parent_filter:
                if self.__content_dict[c_con]["parent"]:
                    if not self.__content_dict[c_con]["parent"].getName() == parent_filter:
                        continue
                else:
                    continue

            return_list.append(self.__content_dict[c_con]["object"])

        # for c_name in key_list:
        #     return_list.append(self.__content_dict[c_name]["object"])
        # return_list = sorted(return_list,  key=lambda([x.getName() for x in return_list]))
        return return_list

class CleanUpProjectClass():
    """
    Use this to clean up a project after its finished to clear up space.
    Should look at all the episode/seq/shot structure and clean up passes like ColorFast.
    Should look at _history folders and either delete them, or clean them up so only the latest 2 versions are left.
    """
    def __init__(self):
        super(CleanUpProjectClass, self).__init__()
        rep = RepositoryFactory(CC.get_film_path())
        self.node_dict: Repository = rep.create()
        self.run()

    def run(self):
        #Don't use 17,19,23
        # cur_scope="E14"
        avoid_scope_list = [17,19,23]
        for cur_n in range(1,28,1):
            if not cur_n in avoid_scope_list:
                print("E%s" % str(cur_n).zfill(2))
                cur_scope = "E%s" % str(cur_n).zfill(2)
                found = self.findColorFast(scope=cur_scope)
                if found:
                    pp.pprint(found)
                    for f in found[cur_scope]["files"].keys():
                        try:
                            print("Deleting: %s" % found[cur_scope]["files"][f][0])
                            os.remove(found[cur_scope]["files"][f][0])
                        except:
                            print("Couldn't Delete this: %s" % found[cur_scope]["files"][f][0])

                    for d in found[cur_scope]["folders"].keys():
                        for cur in found[cur_scope]["folders"][d]:
                            try:
                                print("Deleting: %s" % cur)
                                shutil.rmtree(cur)
                            except:
                                print("Couldn't Delete this: %s" % cur)
                    print("FINISHED")

    def findColorFast(self,scope=None):
        result = {}
        scope_node = self.node_dict.GetByName(scope)
        if scope_node:
            scope_node= scope_node["object"]
        else:
            return False
        scope_shots = scope_node.getAllChildren()
        result[scope] = {"folders":{},"files":{}}
        for shot in scope_shots:
            shot : Node
            p_folder = shot.getPassesFolder()
            if os.path.exists(p_folder):
                content_list = os.listdir(p_folder)
                for content in content_list:
                    c_path = "%s/%s" % (p_folder,content)
                    if "Fast" in content:
                        if os.path.isfile(c_path):
                            if content in result[scope]["files"].keys():
                                result[scope]["files"][content].append(c_path)
                            else:
                                result[scope]["files"][content] = [c_path]
                        if os.path.isdir(c_path):
                            if content in result[scope]["folders"].keys():
                                result[scope]["folders"][content].append(c_path)
                            else:
                                result[scope]["folders"][content] = [c_path]
        return result




if __name__ == '__main__':
    import sys
    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    CleanUpProjectClass()
sys.exit(app.exec_())

