import maya.cmds as cmds
from getConfig import getConfigClass
from Maya_Functions.file_util_functions import loadJson
from Log.CoboLoggers import getLogger
logger = getLogger()

CC = getConfigClass()
print(CC.get_project_shelf_json())
build_dict = loadJson(save_location=CC.get_project_shelf_json())

#TODO Add in seperators?

# Build out from code found here: https://gist.github.com/vshotarov/1c3176fe9e38dcaadd1e56c2f15c95d9


def _null(*args):
    pass


class ShelfCreator:
    """A simple class to build shelves in maya. Since the build method is empty,
    it should be extended by the derived class to build the necessary shelf elements.
    By default it creates an empty shelf called "customShelf"."""

    def __init__(self, name="customShelf", iconPath="", build_dict={}, overwrite=True):

        logger.info("Initializing")
        self.name = name
        self.build_dict = build_dict
        self.iconPath = iconPath
        self.labelBackground = (0.2, 0.2, 0.2, 0.5)
        self.labelColour = (.9, .9, .9)
        if "-" in self.name:
            self.name = self.name.replace("-", "_")
        if build_dict:
            logger.debug("Build-dict available")
            self._cleanOldShelf(overwrite)
            cmds.setParent(self.name)
            self.build()
        else:
            logger.debug("<No build-dict. Keeping old shelf>")

    def build(self):
        """This method should be overwritten in derived classes to actually build the shelf
        elements. Otherwise, nothing is added to the shelf."""
        logger.info("Building new shelf")
        for cur_sort in sorted(self.build_dict.keys()):

            cur_item = self.build_dict[cur_sort]
            logger.debug("****Building: %s" % cur_item["label"])
            if cur_item["type"] == "bttn":
                cur_bttn = self.addButton(
                    label=cur_item["label"],
                    icon=cur_item["icon"],
                    command=cur_item["cmd"],
                    doubleCommand=cur_item["dcmd"],
                    tool_tip=cur_item["tool_tip"]
                )
                if cur_item["children"]:
                    pop_menu = cmds.popupMenu(b=1, parent=cur_bttn)
                    for cur_child_sort in sorted(cur_item["children"]):
                        cur_child = cur_item["children"][cur_child_sort]
                        if cur_child["type"]=="menu_item":
                            self.addMenuItem(
                                parent=pop_menu,
                                label=cur_child["label"],
                                command=cur_child["cmd"]
                            )
            if cur_item["type"] == "separator":
                self.addSeparator()

    def addButton(self, label, icon="", command=_null, doubleCommand=_null, tool_tip=""):
        """Adds a shelf button with the specified label, command, double click command and image."""
        if icon == "":
            icon = "commandButton.png"
        cmds.setParent(self.name)
        if icon:
            icon = self.iconPath + icon
        if not tool_tip:
            tool_tip = label
        return cmds.shelfButton(
            width=25,
            height=25,
            image=icon,
            l=label,
            command=command,
            dcc=doubleCommand,
            imageOverlayLabel=label,
            olb=self.labelBackground,
            olc=self.labelColour,
            annotation="SC: %s" % tool_tip
        )

    def addSeparator(self):
        cmds.setParent(self.name)
        cmds.separator(annotation="SC: ",width=24, height=35, style='shelf', hr=False)

    def addMenuItem(self, parent, label, command=_null, icon=""):
        """Adds a shelf button with the specified label, command, double click command and image."""
        if icon:
            icon = self.iconPath + icon
        return cmds.menuItem(p=parent, l=label, c=command, i=icon)

    def addSubMenu(self, parent, label, icon=None):
        """Adds a sub menu item with the specified label and icon to the specified parent popup menu."""
        if icon:
            icon = self.iconPath + icon
        return cmds.menuItem(p=parent, l=label, i=icon, subMenu=1)

    def _cleanOldShelf(self, overwrite=True):
        """Checks if the shelf exists and empties it if it does or creates it if it does not."""
        logger.info("Cleaning old Shelf")
        label_list = []
        for cur_shelf_item in self.build_dict.values():
            label_list.append(cur_shelf_item["label"])
        if cmds.shelfLayout(self.name, ex=1):
            if cmds.shelfLayout(self.name, q=1, ca=1):
                for each in cmds.shelfLayout(self.name, q=1, ca=1):
                    if True:
                        logger.debug("****Found: %s" % each)
                    if overwrite:  # deletes everything
                        logger.debug("********Deleting: %s" % each)
                        cmds.deleteUI(each)
                        continue

                    try:
                        if "separator" in each:
                            cmds.deleteUI(each)
                            continue
                        logger.debug("****Trying to check shelfButton %s" % each)
                        if cmds.shelfButton(each, q=True, ann=True).startswith("SC: "):  # only replaces scripts from build dict
                            cmds.deleteUI(each)
                        else:
                            logger.debug("****Skipping:%s" % each)
                    except:
                        logger.warning("****Error on %s" % each)
        else:
            cmds.shelfLayout(self.name, p="ShelfLayout")


###################################################################################
'''This is an example shelf.'''
# class customShelf(_shelf):
#     def build(self):
#         self.addButon(label="button1")
#         self.addButon("button2")
#         self.addButon("popup")
#         p = cmds.popupMenu(b=1)
#         self.addMenuItem(p, "popupMenuItem1")
#         self.addMenuItem(p, "popupMenuItem2")
#         sub = self.addSubMenu(p, "subMenuLevel1")
#         self.addMenuItem(sub, "subMenuLevel1Item1")
#         sub2 = self.addSubMenu(sub, "subMenuLevel2")
#         self.addMenuItem(sub2, "subMenuLevel2Item1")
#         self.addMenuItem(sub2, "subMenuLevel2Item2")
#         self.addMenuItem(sub, "subMenuLevel1Item2")
#         self.addMenuItem(p, "popupMenuItem3")
#         self.addButon("button3")
# customShelf()
###################################################################################


"""
dict example
"I010":
{"label": "",
 "type": "",
 "icon": "",
 "cmd": "",
 "dcmd": "",
 "children": {}
 }
"""
#TODO Get path and name from config file. If no key found in config file, skip.

def run(overwrite=True):
    shelf_name = "%s_Shelf" % CC.project_name
    if "project_shelf_json" in CC.__dict__:
        build_dict = loadJson(save_location=CC.get_project_shelf_json())

        ShelfCreator(
            name=shelf_name,
            build_dict=build_dict,
            overwrite=overwrite,
            iconPath="T:/_Pipeline/cobopipe_v02-001/icon/Maya/")
    else:
        pass
