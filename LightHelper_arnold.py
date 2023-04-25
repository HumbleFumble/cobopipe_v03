try:
    from PySide2 import QtWidgets, QtCore, QtGui
    # import maya.cmds as cmds
    # import maya.mel as mel
    # import maya.OpenMaya as om_api
    # import maya.OpenMayaUI as om_apiUI
    # import Maya_Functions.vray_util_functions as vray_util
    import MayaDockable
except:
    from PySide2 import QtWidgets, QtCore, QtGui



from getConfig import getConfigClass
from Log.CoboLoggers import getLogger
CC = getConfigClass(project_name="LegoFriends")
logger = getLogger()


from shutil import copy as shutil_copyfile
# import json
import file_util
import os




"""
For button script in Maya:
import LightHelper as LH
reload(LH)
LH.Run()
"""

def convertPathToPixmap(image_path, width, height, added_name="", overwrite=False):  # function to get pixmap from path
    key_value = "no_thumb_icon"

    # If a path has been passed as parameter: 'Always happens'
    if image_path:
        if os.path.exists(image_path):
            # The path exists and will be combined with the added name
            key_value = "%s%s" % (image_path, added_name)
        else:
            # Get regular path for 'missing thumbnail' image
            image_path = CC.get_no_thumb_icon_path() #cfg_util.CreatePathFromDict(cfg.thumbnail_paths["no_thumb_icon_path"])
            key_value = "no_thumb_icon"
    else:
        # Get regular path for 'missing thumbnail' image
        image_path = CC.get_no_thumb_icon_path() #cfg_util.CreatePathFromDict(cfg.thumbnail_paths["no_thumb_icon_path"])
        key_value = "no_thumb_icon"

    # Get pixmap from Qt cache memory
    pixmap = QtGui.QPixmapCache.find(key_value)

    # If said pixmap exists and should be overridden, take it from the cache so it will refresh with a new pixmap
    if pixmap and overwrite:
        QtGui.QPixmapCache.remove(key_value)

        # try to remove the other thumbnails of image:
        if QtGui.QPixmapCache.find("%s_thumbnail" % image_path):
            QtGui.QPixmapCache.remove("%s_thumbnail" % image_path)
        pixmap = None

    # If pixmap is not in Qt cache memory, create it.
    if not pixmap:

        pixmap = QtGui.QPixmap(image_path)
        # If image size is greater than 160x90: copy and resize image
        if pixmap.width() > 160:

            logger.info("\nA large thumbnail was found in use. Copying and resizing now:")

            img_folder, image_file = os.path.split(image_path)
            new_image_file = "Big_" + image_file
            new_image_path = os.path.join(img_folder, new_image_file)

            shutil_copyfile(image_path, new_image_path)

            pixmap = pixmap.scaled(160, 90, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            pixmap.save(image_path)

            logger.debug("    +'{0}' - copied to - {1}\n".format(image_file, new_image_file))

        pixmap = pixmap.scaled(width, height, QtCore.Qt.KeepAspectRatio,QtCore.Qt.SmoothTransformation)
        QtGui.QPixmapCache.insert(key_value, pixmap)
        pixmap = QtGui.QPixmapCache.find(key_value)


    # This method is called whenever the QListView is scrolled to update thumbnails out of view
    # Uncomment below logger.infos to view results
    # logger.info key_value  # path
    # logger.info pixmap  # object
    # logger.info ""

    return QtGui.QPixmap(pixmap)


class UIUtils(object):

    def populateCombobox(self, combobox, items, aux=[]):
        # Remove all items from current combobox
        combobox.clear()

        # Add categories to combobox
        if items:
            for item in items:
                combobox.addItem(item)

        # Add auxiliary categories to combobox
        for item in aux:
            combobox.addItem(item)


#TODO Fix the UI! Put all import/export buttons into menu.


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.uiUtils = UIUtils()
        self.setObjectName("LightHelper")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setWindowTitle("LightHelper")
        QtGui.QPixmapCache.setCacheLimit(100 * 10240)

        self.base_folder = CC.get_light_export_folder()

        self.save_path_cameras = "%s/Cam_Dict.json" % self.base_folder
        self.save_path_categories = "%s/Categories_Dict.json" % self.base_folder
        self.scene_camera = None
        self.scene_light_setup = None

        self.all_nodes = []
        self.category_dict = self.__getCategoryDict()

        # old_node_dict = self.LoadSettings(self.save_path_cameras)
        old_node_dict = file_util.load_json(self.save_path_cameras)

        if old_node_dict:
            for n in old_node_dict.keys():
                self.all_nodes.append(CustomCamNode(node_path=old_node_dict[n]["node_path"],image_path=old_node_dict[n]["image_path"],node_name=old_node_dict[n]["node_name"],cam_loc=old_node_dict[n]["cam_loc"]))

        self.sort_nodes = self.all_nodes #what nodes are being shown in thumbview



        self.CreateWindow()
        self.UpdateThumbView()
        self.initiateCamAndSetupComboBox()

    def CreateWindow(self):
        self.main_layout = QtWidgets.QVBoxLayout()

        #Button setup
        self.button_layout = QtWidgets.QHBoxLayout()
        self.setup_light_bttn = QtWidgets.QPushButton("Setup Light Group")
        # self.setup_light_bttn.clicked.connect(self.CreateLightSetup)

        self.pick_camera_bttn = QtWidgets.QPushButton("Pick Render Camera")
        # self.pick_camera_bttn.clicked.connect(self.PickCamera)

        self.pick_camera_combo = QtWidgets.QComboBox()
        self.pick_camera_combo.setMinimumWidth(200)
        # self.pick_camera_combo.currentTextChanged.connect(self.PickCameraComboChange)

        self.export_light_bttn = QtWidgets.QPushButton("Export Light")
        self.export_light_bttn.clicked.connect(self.ExportLight)

        self.remove_namespace_bttn = QtWidgets.QPushButton("Remove Namespace")
        # self.remove_namespace_bttn.clicked.connect(self.remove_namespace_call)
        self.remove_namespace_bttn.setToolTip("Removes namespace from selected light group")

        #Category Combobox
        self.category_layout = QtWidgets.QHBoxLayout()
        self.cat_combo = QtWidgets.QComboBox(self)
        self.cat_combo.setMaximumWidth(300)

        self.set_cat_bttn = QtWidgets.QPushButton("Create New Category")
        self.set_cat_bttn.setMaximumWidth(140)
        self.set_cat_bttn.clicked.connect(self.CreateNewCategory)
        self.rem_cat_bttn = QtWidgets.QPushButton("Delete Category")
        self.rem_cat_bttn.setMaximumWidth(140)
        self.rem_cat_bttn.clicked.connect(self.DeleteCategory)

        self.import_z_bttn = QtWidgets.QPushButton("Import Z Planes")
        # self.import_z_bttn.clicked.connect(self.LF.ImportZplanes)

        self.menu_bar = QtWidgets.QMenuBar()

        self.menu_functions = QtWidgets.QMenu("Functions")

        self.recon_z_action = QtWidgets.QAction("ReConnect Z Planes", self.menu_bar)
        # self.recon_z_action.triggered.connect(self.LF.ReconnectZplanesToVray)
        self.menu_functions.addAction(self.recon_z_action)

        self.menu_bar.addMenu(self.menu_functions)


        self.menu_ui = QtWidgets.QMenu("UI")

        self.update_nodes = QtWidgets.QAction("Check For new LightSetups",self.menu_bar)
        self.update_nodes.triggered.connect(self.UpdateDict)
        self.menu_ui.addAction(self.update_nodes)

        self.menu_file = QtWidgets.QMenu("Import/Export")

        self.menu_bar.addMenu(self.menu_functions)
        self.menu_bar.addMenu(self.menu_ui)

        self.button_layout.addWidget(self.setup_light_bttn)
        self.button_layout.addWidget(self.export_light_bttn)
        self.button_layout.addWidget(self.remove_namespace_bttn)

        self.button_layout.addWidget(self.import_z_bttn)

        self.pick_layout = QtWidgets.QHBoxLayout()
        self.pick_layout.addWidget(self.pick_camera_bttn)
        self.pick_layout.addWidget(self.pick_camera_combo)

        self.category_layout.addWidget(self.cat_combo)
        self.category_layout.addWidget(self.set_cat_bttn)
        self.category_layout.addWidget(self.rem_cat_bttn)

        self.category_layout.addStretch(1)



        #ThumbView
        self.thumb_view = QtWidgets.QListView()
        self.thumb_view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.thumb_view.setViewMode(QtWidgets.QListView.IconMode)
        self.thumb_view.setFlow(QtWidgets.QListView.LeftToRight)
        self.thumb_view.setResizeMode(QtWidgets.QListView.Adjust)
        self.thumb_view.setSpacing(20)
        self.thumb_view.setFrameStyle(1)


        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.pick_layout)
        self.main_layout.addLayout(self.category_layout)

        self.main_layout.addWidget(self.menu_bar)
        self.main_layout.addWidget(self.thumb_view)
        self.setLayout(self.main_layout)
        self.thumb_view.installEventFilter(self)

        self.__populate_CatCombo()
        self.cat_combo.currentTextChanged.connect(self.UpdateThumbView)
        self.cat_combo.setCurrentText("All")

    def __getCategoryDict(self):
        # return self.LoadSettings(self.save_path_categories)
        return file_util.load_json(self.save_path_categories)

    def __populate_CatCombo(self):
        # self.uiUtils.populateCombobox(combobox=self.cat_combo, items=self.LoadSettings(self.save_path_categories), aux=["All"])
        self.uiUtils.populateCombobox(combobox=self.cat_combo, items=file_util.load_json(self.save_path_categories), aux=["All"])

    def eventFilter(self, source, event):
        if not (event):
            return QtWidgets.QWidget.eventFilter(self, source,event)
        if (event.type() == QtCore.QEvent.ContextMenu and source is self.thumb_view):
            menu = QtWidgets.QMenu()
            if source == self.thumb_view:
                # Does not register click
                if self.thumb_view.selectedIndexes():

                    all_selection = self.thumb_model.getNode(self.thumb_view.selectedIndexes())
                    node = all_selection[0] #single node
                else:
                    return QtWidgets.QWidget.eventFilter(self, source, event)
                    # return super(MainWindow, self).eventFilter(source, event)

            menu.addAction("Show in Directory")
            menu.addAction("Update Thumbnail")
            menu.addAction("Rename Light Export")
            menu.addSeparator()
            cat_menu = menu.addMenu("Add to Category")
            menu.addAction("Remove from Category")
            menu_cat_list = []
            if self.category_dict:
                for cur_category in self.category_dict:
                    cat_menu.addAction("Add to %s" % cur_category)
                    menu_cat_list.append("Add to %s" % cur_category)
            menu.addSeparator()
            menu.addAction("Import Light")
            menu.addAction("Import Light without Namespace")
            menu.addSeparator()
            menu.addAction("Delete Light Export")


            #TODO Make dynamic menu item (Add to category) with catories as subitems

            action = menu.exec_(event.globalPos())
            if not action == None:
                if action.text() in menu_cat_list:
                    self.AddToCategory(category=action.text().split("Add to ")[-1])

                if action.text() == "Import Light":
                    logger.debug("Now Importing light! For %s" % node.GetName())
                    # self.LF.ImportLightGroup(cur_node=node)
                    self.PickLightSetup()
                if action.text() == "Import Light without Namespace":
                    logger.debug("Now Importing light without namespace! For %s" % node.GetName())
                    # self.LF.ImportLightGroup(cur_node=node, namespace=False)
                    self.PickLightSetup()
                if action.text() == "Update Thumbnail":
                    logger.debug("Now Updating Thumbnail! For %s" % node.GetName())
                    self.TakeThumbnail(cur_node=node)
                if action.text() == "Rename Light Export":
                    logger.debug("Now Renaming light! For %s" % node.GetName())
                    self.RenameNode(cur_node=node)
                if action.text() == "Update Cam position":
                    logger.debug("Now Updating cam position! For %s" % node.GetName())
                    self.UpdateCamLoc(cur_node=node)
                if action.text() == "Delete Light Export":
                    logger.debug("Now Deleting NODE!! For %s" % node.GetName())
                    self.DeleteCurrentNode(cur_node=node)
                if action.text() == "Remove from Category":
                    logger.debug("Now Removing NODE from Category!! For %s" % node.GetName())
                    self.RemoveFromCategory()
                    # self.DeleteCurrentNode(cur_node=node)

        return QtWidgets.QWidget.eventFilter(self, source,event)  # Tried using this methode instead of:  return super(MainWindow, self).eventFilter(source, event)

    def remove_namespace_call(self):
        pass
        # self.LF.RemoveNamespace()
        # self.PickLightSetup()

    def PickCameraComboChange(self):
        if self.pick_camera_combo.currentText():
            pass#    self.LF.setRenderCam(self.pick_camera_combo.currentText())

    def PickCamera(self):
        pass
        # from_panel = self.LF.getCurrentCameraFromPanel()
        # cam_combo_list = self.LF.getAllCamerasInScene()
        #
        # self.pick_camera_combo.clear()
        # self.pick_camera_combo.addItems(cam_combo_list)
        #
        # scene_camera = self.LF.findAnimCam()
        # if scene_camera:
        #     self.pick_camera_combo.setCurrentText(scene_camera)
        #     return True
        # if from_panel:
        #     from_panel_cam = from_panel.split("Shape")[0]
        #     if from_panel_cam in cam_combo_list:
        #         self.pick_camera_combo.setCurrentText(from_panel_cam)
        #         self.LF.setRenderCam(from_panel)

    def initiateCamAndSetupComboBox(self):
        pass

    def GetDictFromCurrentNodes(self):
        node_dict = {}
        for c in self.all_nodes:
            node_dict[c.GetName()]=c.GetDict()
        return node_dict

    def DeleteCurrentNode(self, cur_node):
        #delete files
        try:
            os.remove(cur_node.GetPath())
            os.remove(cur_node.GetImage())
        except:
            logger.info("can't find files to delete for %s" % cur_node.GetName())
        #delete key in dict
        temp_dict = self.UpdateJsonDict(self.save_path_cameras)
        temp_dict.pop(cur_node.GetName())
        # self.SaveSettings(self.save_path_cameras, temp_dict)
        file_util.save_json(self.save_path_cameras, temp_dict)
        self.all_nodes.remove(cur_node)
        self.UpdateThumbView(self.cat_combo.currentText())
        #save dict

    def closeEvent(self, event):
        if not os.path.exists(os.path.split(self.save_path_cameras)[0]):
            os.mkdir(os.path.split(self.save_path_cameras)[0])
        # Save all nodes to json file.
        # self.SaveSettings(self.save_path_cameras, self.UpdateJsonDict(self.save_path_cameras))  # Save nodes
        file_util.save_json(self.save_path_cameras, self.UpdateJsonDict(self.save_path_cameras)))
        QtGui.QPixmapCache.clear()
        super(MainWindow, self).closeEvent(event)

    def ExportLight(self):
        text, ok = QtWidgets.QInputDialog().getText(self, "Set Name: ","example: Clearing_Cam_04:", QtWidgets.QLineEdit.Normal, "")
        if ok and text:
            node_name = text
        else:
            logger.info("Cancel creation because no name was given")
            return
        #
        # cur_objs = self.LF.GetExportObjs()
        # if cur_objs:
        #     cur_location = cur_objs[1]
        #     del cur_objs[1]
        #     file_path = "%s/Files/%s_LightSetup.ma" % (self.base_folder, node_name)
        #     self.LF.ExportLight(cur_objs, file_path)
        #     new_node = CustomCamNode(node_path=file_path,image_path="%s/Thumbs/%s_Thumb.png" % (self.base_folder,node_name),node_name=node_name,cam_loc=cur_location)
        #     self.all_nodes.append(new_node)
        #     self.TakeThumbnail(new_node)
        #     #Then save
        #     self.SaveSettings(self.save_path_cameras, self.UpdateJsonDict(self.save_path_cameras))
        #     try:
        #         if not self.cat_combo.currentText() == "All":
        #             self.AddToCategory(category=self.cat_combo.currentText(),selection=[node_name])
        #     except:
        #         logger.warning("Couldn't add %s to the current category" % node_name)
        #     self.UpdateThumbView(self.cat_combo.currentText())
        # else:
        #     cmds.warning("Please select your light export group and try again!")

    def CreateNewCategory(self):
        # Dialog box for getting user input
        text, ok = QtWidgets.QInputDialog().getText(self, "Create New Category", "example: Forest:",
                                                    QtWidgets.QLineEdit.Normal, "")
        if ok and text:
            category = text
        else:
            logger.info("Cancel creation because no name was given")
            return

        # Get contents of JSON as Dict Example: {"Forest":[node_name, node_name2]}
        # old_info = self.LoadSettings(save_location=self.save_path_categories)
        old_info = file_util.load_json(self.save_path_categories)

        # if LoadSettings return None, Make empty dictionary
        if not old_info:
            old_info = {}

        # Add new category to dictionary
        result = old_info.copy()
        result[category] = []

        # If selection is made, put selected items into new category
        selection = self.thumb_view.selectedIndexes()
        if selection:
            for i in selection:
                name = i.data()  # Gets name of item from QModelIndex data
                result[category].append(name)

        # Save result to JSON
        logger.debug("Updated Dict: %s" % result)
        # self.SaveSettings(save_location=self.save_path_categories, save_info=result)
        file_util.save_json(self.save_path_categories, result)
        self.category_dict = result

        # Update combobox
        self.__populate_CatCombo()
        # self.cat_combo.setCurrentText(category)

    def DeleteCategory(self):
        from QtCustomWidgets import confirmPopup

        current_category = self.cat_combo.currentText()
        if confirmPopup(self, title="Delete Category??", label="This will delete the Category: %s\nDo you want to continue?\nPS: It does not delete the light-exports, only the way of sorting" % current_category):
            # Get dictionary and remove (pop) the category key within
            # cat_dict = self.LoadSettings(self.save_path_categories)
            cat_dict = file_util.load_json(self.save_path_categories)
            cat_dict.pop(current_category)

            # Save result to JSON
            logger.debug("Updated Dict: %s" % cat_dict)
            # self.SaveSettings(save_location=self.save_path_categories, save_info=cat_dict)
            file_util.save_json(self.save_path_categories, cat_dict)
            self.category_dict = cat_dict

            # Update combobox
            self.__populate_CatCombo()
            # logger.debug(self.cat_combo.currentText())
            self.cat_combo.setCurrentText("All")
        else:
            pass

    def AddToCategory(self, category=None,selection=None):
        """
        category= String
        selection= List

        """
        if not category:
            category=self.cat_combo.currentText()
        # Get contents of JSON as Dict Example: {"Forest":[node_name, node_name2]}
        # old_info = self.LoadSettings(save_location=self.save_path_categories)
        old_info = file_util.load_json(self.save_path_categories)

        # if LoadSettings return None, Make empty dictionary
        if not old_info:
            old_info = {}

        # Put selected indexes of QListView into a list
        if not selection:
            selection = []
            for i in self.thumb_view.selectedIndexes():
                name = i.data()  # Gets name of item from QModelIndex data
                selection.append(name)

        # Remove selected items from lists in dictionary if present
        result = old_info.copy()
        if old_info:
            if category in old_info: #check if category is in file dict
                for cur_name in selection:
                    if not cur_name in old_info[category]:
                        if category in result:
                            result[category].append(cur_name)
                        else:
                            result[category] = [cur_name]
                        logger.debug("Added %s to %s" % (cur_name, category))
            else:
                result[category] = selection
                logger.debug("Added %s to %s" %(selection, category))
        else:
            result[category] = selection
            logger.debug("Added %s to %s" % (selection, category))

        # Save result to JSON
        logger.debug("Updated Dict: %s" % result)
        # self.SaveSettings(save_location=self.save_path_categories, save_info=result)
        file_util.save_json(self.save_path_categories, result)
        self.category_dict = result

        # Update combobox
        # self.__populate_CatCombo()
        # self.cat_combo.setCurrentText(category)

        #

    def RemoveFromCategory(self):
        current_category = self.cat_combo.currentText()
        if current_category == "All":
            return
        # Get contents of JSON as Dict
        # old_info = self.LoadSettings(save_location=self.save_path_categories)
        old_info = file_util.load_json(self.save_path_categories)
        if not old_info:
            old_info = {}
        result = old_info.copy() #Take copy of current category dict

        # Put selected indexes of QListView into a list
        selection = []
        for i in self.thumb_view.selectedIndexes():
                name = i.data()  # Gets name of item from QModelIndex data
                selection.append(name)

        #Compare category list using sets, since we don't need duplicates. And apperantly thats a fast approach..
        if current_category in result:
            result[current_category] = list(set(result[current_category]) - set(selection))

        # Save result to JSON
        # self.SaveSettings(save_location=self.save_path_categories, save_info=result)
        file_util.save_json(self.save_path_categories, result)
        self.category_dict = result

        # Update combobox
        self.__populate_CatCombo()
        if current_category in self.category_dict:
            self.cat_combo.setCurrentText(current_category)
        else:
            self.cat_combo.setCurrentText("All")

    def RenameNode(self, cur_node):
        text, ok = QtWidgets.QInputDialog().getText(self, "Set New Name: ", "example: Clearing_Cam_04:", QtWidgets.QLineEdit.Normal, "")
        if ok and text:
            node_name = text
        else:
            logger.info("Cancel creation because no name was given")
            return

        # Check light exports for duplicate names before renaming to avoid clashing
        if node_name in self.GetDictFromCurrentNodes():
            self.my_pop = QtWidgets.QMessageBox()
            self.my_pop.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
            self.my_pop.setText("Name Already Exists!! Pick another or cancel")
            self.my_pop.setStandardButtons(QtWidgets.QMessageBox.Ok)
            wait_reply = self.my_pop.exec_()
            if wait_reply == QtWidgets.QMessageBox.Ok:
                self.RenameNode(cur_node)
            else:
                return False
        else:
            cur_node.Rename(node_name)

            # TODO RENAME() CHANGE FILE NAME AND THUMB NAME ON SERVER

            # Set new name for CamNodes file on server

            # Set new name for Category file on server

    def CreateLightSetup(self):
        pass #self.LF.SetupLightGroup()

    def UpdateThumbView(self,current_text=None):
        self.sort_nodes = []
        if current_text=="All" or not current_text:
            self.sort_nodes = self.all_nodes
        else:
            for cur_node in self.all_nodes:
                if cur_node.GetName() in self.category_dict[current_text]:
                    self.sort_nodes.append(cur_node)
        self.sort_nodes = sorted(self.sort_nodes, key=lambda x: x.GetName())
        self.thumb_model = ThumbModel(self.sort_nodes, self)
        self.thumb_view.setModel(self.thumb_model)

    def ThumbnailPopup(self, title="Update Thumbnail"):
        temp_popup = QtWidgets.QMessageBox()
        temp_popup.setIcon(QtWidgets.QMessageBox.Question)
        temp_popup.setText(
            "Update Thumbnail?\n(Viewport thumbnail only works if the viewport has focus\n Just click something in the wanted viewport )")
        temp_popup.setWindowTitle(title)
        temp_popup.addButton("Viewport", QtWidgets.QMessageBox.ActionRole)
        temp_popup.addButton("Render", QtWidgets.QMessageBox.ActionRole)
        temp_popup.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        temp_popup.exec_()
        to_return = temp_popup.clickedButton().text()
        temp_popup.deleteLater()
        return to_return

    def UpdateDict(self):
        self.UpdateJsonDict(save_path=self.save_path_cameras)

    def UpdateJsonDict(self, save_path=None,current_dict=None):
        if not current_dict:
            current_dict = self.GetDictFromCurrentNodes()

        # new_dict = self.LoadSettings(save_path)
        new_dict = file_util.load_json(save_path)
        if new_dict:
            new_dict.update(current_dict)
            return new_dict
        else:
            return current_dict

    def TakeThumbnail(self,cur_node=None):
        # IMPORT SAVE VIEWPORT FUNCTIONALITY
        # cur_node = "My_Camera_Class"
        if cur_node:
            choice = self.ThumbnailPopup()
            if not choice == "cancel":
                # thumb_path = cfg_util.CreatePathFromDict(cfg.thumbnail_paths["asset_thumbnail_path"],cur_node.GetAssetInfo())
                thumb_path = cur_node.GetImage()
                thumb_folder, thumb_file = os.path.split(thumb_path)
                if not os.path.exists(thumb_folder):
                    os.makedirs(thumb_folder)
                if choice == "Render":  # Save image in vray frame buffer!
                    mel.eval('vray vfbControl -saveimage "%s"' % thumb_path)
                elif choice == "Viewport":  # Save image from maya viewport
                    # mel.eval('vray hideVFB')
                    view = om_apiUI.M3dView.active3dView()
                    image = om_api.MImage()
                    view.readColorBuffer(image, True)
                    image.writeToFile(thumb_path, "png")

                # Update thumbnail of asset:
                c_pix = convertPathToPixmap(thumb_path, 160, 90, added_name="", overwrite=True)


    # def SaveSettings(self, save_location, save_info):
    #     with open(save_location, 'w+') as saveFile:
    #         json.dump(save_info, saveFile)
    #     saveFile.close()

    # def LoadSettings(self, save_location):
    #     if os.path.isfile(save_location):
    #         with open(save_location, 'r') as saveFile:
    #             loadedSettings = json.load(saveFile)
    #         # if 'selected node' in loadedSettings.keys():
    #         if loadedSettings:
    #             return loadedSettings
    #     else:
    #         logger.debug("not a file")
    #     return None


class ThumbModel(QtCore.QAbstractListModel): #Quick Selection mode on type/category selection
    def __init__(self, nodes,ui_parent):
        super(ThumbModel, self).__init__()
        self.setObjectName("MyThumby")
        self.nodes = nodes
        self.size_factor = 1.5
        self.no_thumb_picture = CC.get_no_thumb_icon_path()#cfg_util.CreatePathFromDict(cfg.thumbnail_paths["no_thumb_icon_path"])
        self.ui_parent = ui_parent

    def GetName(self, elem):
        return elem.GetName()

    def rowCount(self, parent=None):
        return len(self.nodes)

    def getNode(self, index_list):
        return_list = []
        for index in index_list:
            if index.isValid():
                r = index.row()
                try:
                    node = self.nodes[r]
                    return_list.append(node)
                except IndexError:
                    continue
        return return_list
        # return None

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):

        if not index.isValid():
            logger.debug("index is not valid")
            return None

        cur_row = index.row()

        cur_node = self.nodes[cur_row]

        if role == QtCore.Qt.ToolTipRole:
            return "Cam Loc: %s" % cur_node.GetCamLoc()

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignHCenter

        # if role == QtCore.Qt.SizeHintRole:
        #     return QtCore.QSize(self.thumb_size[0],self.thumb_size[1]+20)

        if role == QtCore.Qt.DisplayRole:
            return "%s" % (cur_node.GetName())

        if role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignVCenter()

            # return "Cam Loc: %s" % cur_node.GetCamLoc()
        #         return "%s : %s : %s" % (self.nodes[cur_row][cur_col].Episode(),self.nodes[cur_row][cur_col].Sequence(), self.nodes[cur_row][cur_col].GetName() )
        if role == QtCore.Qt.DecorationRole:
            image_path = cur_node.GetImage()
            pixmap = convertPathToPixmap(image_path,160,90,"",False)
            return QtGui.QPixmap(pixmap)


class CustomCamNode(object):
    def __init__(self,node_path=None,image_path=None,node_name=None,cam_loc=None,tags=None):
        self.node_path = node_path
        self.image_path = image_path
        self.node_name = node_name
        self.cam_loc = cam_loc
        self.tags = tags

    def GetName(self):
        return self.node_name

    def GetCamLoc(self):
        return self.cam_loc

    def SetCamLoc(self, new_loc):
        self.cam_loc = new_loc

    def GetPath(self):
        return self.node_path

    def GetImage(self):
        return self.image_path

    def Rename(self, new_name):
        self.node_name = new_name

    def GetDict(self):
        return {"image_path":self.image_path,"node_path":self.node_path,"node_name":self.node_name, "cam_loc":self.cam_loc}

#
# class LightFunctions():
#     def __init__(self):
#         self.template_folder = CC.get_template_path() #cfg_util.CreatePathFromDict(cfg.project_paths["template_path"])
#         self.z_planes_import_path = "%s/Z_Planes_Template.ma" % self.template_folder
#         self.render_cam = None
#         self.light_setup = None
#         self.sky = None
#
#     def getSceneSun(self):
#         sun = None
#         l = cmds.ls(type="VRaySunShape")
#         for i in l:
#             for x in cmds.listConnections(i):
#                 if "VRaySky" in x:
#                     v = cmds.listConnections('vraySettings.cam_envtexGi')
#                     if v:
#                         for q in v:
#                             if "VRaySky" in q:
#                                 sun = i
#                     break
#         if not sun and l:
#             sun = l[0]
#         return cmds.listRelatives(sun, p=True)[0]
#
#
#     def moveLocatorsToSelectedObject(self):
#         selected = cmds.ls(sl=True)[-1]
#         highlight_aims = cmds.ls("::*_Highlight_aim_LOC")
#         selectedMatrix = cmds.xform(selected, q=True, matrix=True, ws=True)
#         cmds.xform(highlight_aims, matrix=selectedMatrix, ws=True)
#
#
#     def selectHighlightLocators(self):
#         highlight_aims = cmds.ls("::*_Highlight_aim_LOC")
#         cmds.select(deselect=True)
#         cmds.select(highlight_aims)
#
#
#     def elevateHighlightAims(self, height=500):
#         highlight_aims = cmds.ls("::*_Highlight_aim_LOC")
#         sun = self.getSceneSun()
#         sunParent = cmds.listRelatives(sun, parent=True)[0]
#
#         c, a, b = cmds.xform(sun, q=True, t=True, ws=True)
#         f, d, e = cmds.xform(sunParent, q=True, t=True, ws=True)
#         c = c - f
#         a = a - d
#         b = b - e
#
#         y = height
#         z = y * (b / a)
#         x = y * (c / a)
#
#         cmds.xform(highlight_aims, t=[x, y, z])
#
#     def findSun(self, input):
#         children = cmds.listRelatives(input, allDescendents=True, fullPath=True)
#         if children:
#             for child in children:
#                 if child:
#                     if cmds.objectType(child) == 'VRayGeoSun':
#                         return child
#                     # else:
#                     #     output = self.findSun(child)
#                     #     if output:
#                     #         return output
#                     #     else:
#                     #         return False
#
#     def findSky(self, light_setup):
#         if self.light_setup:
#             sun = self.findSun(self.light_setup)
#             if sun:
#                 sunShape = cmds.listRelatives(sun, shapes=True, fullPath=True)[0]
#                 for item in cmds.listConnections(sunShape):
#                     if cmds.objectType(item) == 'VRaySky':
#                         self.sky = item
#                         return self.sky
#
#     def getLightSetup(self):
#         if self.light_setup:
#             if not self.sky:
#                 self.findSky(self.light_setup)
#             return self.light_setup
#         else:
#             light_setup = self.FindLightGroupInScene()
#             if light_setup:
#                 self.setLightSetup(light_setup)
#                 self.sky = self.findSky(self.light_setup)
#                 return self.light_setup
#             logger.info("PICK A LIGHT SETUP GROUP FIRST!")
#             return False
#
#     def setLightSetup(self,light_setup):
#         self.light_setup = light_setup
#         if not cmds.attributeQuery("setup_name",node=light_setup,exists=True):
#             self.SetupMessageAttr(self.light_setup, rebuild=True)
#         self.ConnectMessageAttr(from_message= "setup_name",target_obj=light_setup)
#
#     def FindLightGroupInScene(self, all=False):
#         light_groups = cmds.ls("::*LightSetup_Group", l=True)
#         if all:
#             return light_groups
#         if len(light_groups) > 1:
#             for light_group in light_groups:
#                 if cmds.getAttr("%s.visibility" % light_group) == 1:
#                     # self.setLightSetup(light_group)
#                     return light_group
#         elif len(light_groups)== 1:
#             # self.setLightSetup(light_groups[0])
#             return light_groups[0]
#         else:
#             return False
#
#     def getCurrentCameraFromPanel(self):
#         focus_view = cmds.getPanel(withFocus=True)
#         try:
#             m_editor = cmds.modelPanel(focus_view, q=True, me=True)
#             cur_cam = cmds.modelEditor(m_editor, q=True, camera=True)
#             return cur_cam
#         except:
#             cmds.warning("Can't find camera from %s" % focus_view)
#         return False
#
#     def getAllCamerasInScene(self):
#         cam_list = cmds.listCameras(p=True)
#         return cam_list
#
#     def setRenderCam(self,cam_node):
#         self.render_cam = self.getCameraShape(cam_node)
#         if self.light_setup:
#             self.ConnectMessageAttr(from_message= "render_cam", target_obj=cam_node)
#
#     def findAnimCam(self):
#         scenePath = cmds.file(query=True, sceneName=True)
#         sceneName = scenePath.split('/')[-1]
#         for bit in sceneName.split('_'):
#             if 'SH' in bit:
#                 if len(bit) == 5:
#                     if int(bit[3:]):
#                         camera = cmds.ls('::' + bit + '_Cam')[0]
#                         self.setRenderCam(camera)
#                         return camera
#         return None
#
#     def getCameraShape(self, cam_node):
#         if cmds.nodeType(cam_node) == "camera":
#             return cam_node
#         else:
#             cam = cmds.listRelatives(cam_node,type="camera")
#             if cam:
#                 return cam[0]
#
#     def createSphere(self):
#         cur_name = self.returnAvailableSphereName("Scene")
#         vray_util.CreateVraySphereFade(cur_name=cur_name)
#
#     def returnAvailableSphereName(self,cur_name="Scene"):
#         if cmds.objExists("%s_SphereFade" % cur_name):
#             if cur_name.endswith("ne"):
#                 cur_name = "Scene%s" % 1
#                 return self.returnAvailableSphereName(cur_name)
#             else:
#                 ver = int(cur_name.split("Scene")[1])
#                 ver = ver + 1
#                 return self.returnAvailableSphereName("Scene%s" % ver)
#         else:
#             return cur_name
#
#     def ImportZplanes(self):
#         if not self.getLightSetup():
#             return False
#         if cmds.attributeQuery("camLocator", n=self.light_setup, ex=True):
#             cam_locator = cmds.listConnections("%s.camLocator" % self.light_setup)
#         else:
#             return False
#         if not cam_locator:
#             cmds.warning("Couldn't get camera!")
#             return False
#         else:
#             cmds.file(self.z_planes_import_path, i=True, typ="mayaAscii", ignoreVersion=True, ra=False,mergeNamespacesOnClash=True, options="v=0;")
#         z_group = "ZPlane_Group"
#         self.ConnectMessageAttr(from_message="%s.zplanes" % self.light_setup, target_obj=z_group)
#
#         p_delete = cmds.parentConstraint(cam_locator, z_group, mo=False, n="PO_CamLco")
#         s_delete = cmds.scaleConstraint(cam_locator, z_group, mo=False, n="SC_CamLoc")
#         # cmds.delete(p_delete)
#         # cmds.delete(s_delete)
#         cmds.parent(z_group,self.light_setup)
#
#         nearZ_float = "nearZ"
#         farZ_float = "farZ"
#
#         nearZ_show = "nearZShow"
#         farZ_show = "farZShow"
#         if not cmds.attributeQuery(nearZ_show, n=self.light_setup, ex=True):
#             cmds.addAttr(self.light_setup, ln=nearZ_show, at="long", min=0, max=1, dv=0, k=True)
#             cmds.addAttr(self.light_setup, ln=farZ_show, at="long", min=0, max=1, dv=0, k=True)
#
#             cmds.addAttr(self.light_setup, ln=nearZ_float, at="float", min=0, dv=5, k=True)
#             cmds.addAttr(self.light_setup, ln=farZ_float, at="float", min=0, dv=1000, k=True)
#
#         cmds.connectAttr("%s.farZ" % self.light_setup, "FarZ_Multiply.input1X", f=True)
#         cmds.connectAttr("%s.farZ" % self.light_setup, "FarZ_Multiply.input1Y", f=True)
#
#         cmds.connectAttr("%s.nearZ" % self.light_setup, "NearZ_Multiply.input1X", f=True)
#         cmds.connectAttr("%s.nearZ" % self.light_setup, "NearZ_Multiply.input1Y", f=True)
#
#         cmds.connectAttr("%s.%s" % (self.light_setup, nearZ_float), "%s.%s" % (z_group, nearZ_float), f=True)
#         cmds.connectAttr("%s.%s" % (self.light_setup, farZ_float), "%s.%s" % (z_group, farZ_float), f=True)
#
#         cmds.connectAttr("%s.%s" % (self.light_setup, farZ_show), "%s.%s" % (z_group, farZ_show), f=True)
#         cmds.connectAttr("%s.%s" % (self.light_setup, nearZ_show), "%s.%s" % (z_group, nearZ_show), f=True)
#
#         z_elements = ["Z_No_Filter", "Z_depth"]
#         for cur_z in z_elements:
#             if cmds.objExists(cur_z):
#                 cmds.connectAttr("%s.%s" % (z_group, farZ_float), "%s.vray_depthWhite" % (cur_z), f=True)
#                 cmds.connectAttr("%s.%s" % (z_group, nearZ_float), "%s.vray_depthBlack" % (cur_z), f=True)
#
#     def ReconnectZplanesToVray(self, z_element=None):
#         nearZ_float = "nearZ"
#         farZ_float = "farZ"
#         if not self.getLightSetup():
#             logger.info("Can't find a light group")
#             return False
#         z_group = cmds.listConnections("%s.zplanes" % self.light_setup)
#
#         # z_group = "ZPlane_Group"
#         if z_group:
#             z_group = z_group[0]
#             logger.info("Found %s as light_group, connecting z_planes to z elements" % self.light_setup)
#             if z_element:
#                 if cmds.objExists(z_element):
#                     cmds.connectAttr("%s.%s" % (z_group, farZ_float), "%s.vray_depthWhite" % (z_element), f=True)
#                     cmds.connectAttr("%s.%s" % (z_group, nearZ_float), "%s.vray_depthBlack" % (z_element), f=True)
#             else:
#                 z_elements = ["Z_No_Filter", "Z_depth"]
#                 for cur_z in z_elements:
#                     if cmds.objExists(cur_z):
#                         cmds.connectAttr("%s.%s" % (z_group, farZ_float), "%s.vray_depthWhite" % (cur_z), f=True)
#                         cmds.connectAttr("%s.%s" % (z_group, nearZ_float), "%s.vray_depthBlack" % (cur_z), f=True)
#         else:
#             logger.info("Can't find z planes")
#
#     def RemoveNamespace(self):
#         if not self.getLightSetup():
#             return False
#         # light_group = cmds.ls("::*LightSetup_Group", sl=True, l=True)[0]
#         if ":" in self.light_setup:
#             cur_namespace = self.light_setup.split(":")[0]
#             if "|" in cur_namespace: #remove the root line
#                 cur_namespace = cur_namespace.split("|")[1]
#             cmds.namespace(rm=cur_namespace,mnp=True)
#         else:
#             return False
#
#     def GetExportObjs(self):
#         if not self.getLightSetup():
#             return False
#         # light_obj = cmds.ls("::*LightSetup_Group", sl=True,l=True)
#         # if light_obj:
#         cam_loc_obj = "%s|Cam_Location_Loc" % self.light_setup
#         if cmds.objExists(cam_loc_obj):
#             cam_loc = cmds.xform(cam_loc_obj, q=True, t=True, a=True, ws=True)
#             output = [self.light_setup, cam_loc]
#             if not self.sky:
#                 self.findSky(self.light_setup)
#             if self.sky:
#                 output.append(self.sky)
#             return output
#         return False
#
#     def ExportLight(self, export_objs=None, export_path=None):
#         cmds.select(deselect=True)
#         for item in export_objs:
#             cmds.select(item, add=True)
#         cmds.file(export_path,force=True, options="v=0;", typ="mayaAscii", pr=True, es=True,ch=False,exp=False)
#
#     def ImportLightGroup(self, cur_node, namespace=True):
#         # import with prefix of node-name
#         #TODO aim constraint from cam locator to dome is broken, need to fix it!
#
#         preClean()
#
#         import_path = cur_node.GetPath()
#         node_name = cur_node.GetName()
#
#         if namespace:
#             imported_objs = cmds.file(import_path, i=True, typ="mayaAscii", ignoreVersion=True, ra=True, mergeNamespacesOnClash=True, namespace=node_name, options="v=0;", pr=True)
#             light_group = "%s:LightSetup_Group" % node_name
#         if not namespace:
#             imported_objs = cmds.file(import_path, i=True, typ="mayaAscii", ignoreVersion=True, options="v=0;", pr=True)
#             light_group = "LightSetup_Group"
#         logger.debug("imported: %s" % imported_objs)
#
#         # Check if 'domeLight' has all attributes of 'light_group' and if not assign values
#         dome_super_root = False
#         cam_locator = False
#         if cmds.attributeQuery("domeLight", n=light_group, ex=True):
#             logger.debug("Looking for dome and cam locator")
#             dome_super_root = cmds.listConnections("%s.domeLight" % light_group)[0]
#             cam_locator = cmds.listConnections("%s.camLocator" % light_group)[0]
#
#         skies = []
#         children = cmds.listRelatives(light_group, allDescendents=True, type='VRayGeoSun', fullPath=True)
#         if children:
#             for child in children:
#                 childShape = cmds.listRelatives(child, fullPath=True)[0]
#                 if childShape:
#                     connections = cmds.listConnections(childShape, type='VRaySky')
#                     if connections:
#                         for sky in connections:
#                             if sky not in skies:
#                                 skies.append(sky)
#
#         if skies:
#             from Maya_Functions.vray_util_functions import setCurrentRenderer
#             setCurrentRenderer()
#             cmds.setAttr("vraySettings.cam_overrideEnvtex", 1)
#         for sky in skies:
#             cmds.connectAttr(sky + '.outColor', 'vraySettings.cam_envtexGi', force=True)
#             cmds.connectAttr(sky + '.outColor', 'vraySettings.cam_envtexReflect', force=True)
#             cmds.connectAttr(sky + '.outColor', 'vraySettings.cam_envtexRefract', force=True)
#
#         # If a camera is viewed through, proceed
#         cur_cam = self.getCurrentCameraFromPanel()
#         if cur_cam:
#             logger.debug("FOUND %s" % cur_cam)
#
#             #Get new cam
#             #find dome_super_root
#             in_group = cmds.listRelatives("%s:LightSetup_Group" % node_name, type="transform", f=True)
#             if not dome_super_root:
#                 dome_namespace = "%s:Day" % node_name
#                 for cur_obj in in_group:
#                     if cmds.referenceQuery(cur_obj, inr=True):
#                         dome_namespace = cmds.referenceQuery(cur_obj, ns=True)
#                 dome_super_root = "%s:SuperRoot_Ctrl" % dome_namespace
#                 if not cmds.objExists(dome_super_root):
#                     cmds.warning("Can't find a dome light in LightSetup_Group, skipping aligning")
#                     return
#             if not cam_locator:
#                 cam_locator = "%s:Cam_Location_Loc" % node_name
#             # make constraints to cam_loc
#             # aim_delete = cmds.aimConstraint(cam_locator, dome_super_root, mo=True,weight=1,aimVector=[1, 0, 0], upVector=[0, 1, 0], worldUpType="vector", worldUpVector=[0, 1, 0], skip=["x","z"])
#             # cmds.setAttr("%s.rotateOrder" % dome_super_root,1)
#             par_delete = cmds.parentConstraint(cam_locator, "%s:CamDependent_Lights" % node_name,mo=True)
#
#             #align loc with new cam and delete constraints
#             cp_delete = cmds.parentConstraint(cur_cam,cam_locator,mo=False)
#             # cmds.delete(aim_delete, par_delete,cp_delete)
#
#     def GetCurrentLocation(self):
#         if self.render_cam:
#             return cmds.xform(self.render_cam, q=True, t=True, a=True, ws=True)
#         else:
#             logger.info("Pick Render-Cam and try again")
#             return False
#
#     def connectToZplanes(self):
#         pass
#
#     def ConnectToDome(self):
#         if self.light_setup:
#             light_group = self.light_setup
#         else:
#             light_group = self.FindLightGroupInScene()
#
#         selection = cmds.ls(sl=True)
#         if selection:
#             light_dome = selection[0]
#         else:
#             logger.info("PICK LIGHT DOME and try again")
#             return False
#         if cmds.objExists(light_group) and cmds.objExists(light_dome):
#             cmds.attributeQuery("lightDome", n=light_group, ex=True)
#             self.ConnectMessageAttr("%s.lightDome" % light_group,light_dome)
#
#     def ConnectToLocator(self):
#         if self.light_setup:
#             light_group = self.light_setup
#         else:
#             light_group = self.FindLightGroupInScene()
#         cam_locator = "%s|Cam_Location_Loc" % (light_group)
#         if cmds.objExists(light_group) and cmds.objExists(cam_locator):
#             cmds.attributeQuery("camLocator", n=light_group, ex=True)
#             self.ConnectMessageAttr("%s.camLocator" % light_group,cam_locator)
#
#     def RebuildMessageAttr(self):
#         # light_group = cmds.ls("::*LightSetup_Group", sl=True,l=True)[0]
#         if self.getLightSetup():
#             self.SetupMessageAttr(self.light_setup,rebuild=True)
#
#     def ConnectMessageAttr(self, from_message, target_obj):
#         if self.light_setup and not "." in from_message:
#             from_message = "%s.%s" % (self.light_setup,from_message)
#         if cmds.attributeQuery("message",node=target_obj,exists=True):
#             if not cmds.attributeQuery(from_message.split(".")[1],node=from_message.split(".")[0],exists=True):
#                 return False
#             cmds.connectAttr("%s.message" % target_obj, from_message, f=True)
#
#     def SetupMessageAttr(self,light_group=None, cam_loc=None,rebuild=False):
#         for atn in ["render_cam","setup_name","camLocator","lightDome","zplanes"]:
#             if not cmds.attributeQuery(atn,node=light_group,exists=True):
#                 cmds.addAttr(light_group, ln=atn, at="message", w=True, h=False)
#         # cmds.addAttr(light_group, ln="render_cam", at="message", w=True, h=False)
#         # cmds.addAttr(light_group, ln="setup_name", at="message", w=True, h=False)
#         # cmds.addAttr(light_group, ln="camLocator", at="message", w=True, h=False)
#         # cmds.addAttr(light_group, ln="lightDome", at="message", w=True, h=False)
#         # cmds.addAttr(light_group, ln="zplanes", at="message", w=True, h=False)
#         if cam_loc:
#             self.ConnectMessageAttr("%s.camLocator" % light_group, cam_loc)
#         if rebuild:
#             if self.light_setup:
#                 self.ConnectMessageAttr("%s.setup_name" % light_group, self.light_setup)
#             if self.render_cam:
#                 self.ConnectMessageAttr("%s.render_cam" % light_group, self.render_cam)
#
#     def rebuildConstraints(self):
#         if not self.getLightSetup():
#             return False
#         if not self.render_cam:
#             logger.info("Can't find camera!")
#             return False
#         # cam_locator = cmds.listConnections("%s.camLocator" % self.light_setup)[0]
#         # cam_dependent = cmds.listConnections("%s.camLocator" % self.light_setup)[0]
#         # zplane_group = cmds.listConnections("%s.zplanes" % self.light_setup)[0]
#         if ":" in self.light_setup:
#             namespace = "%s:" % self.light_setup.split(":")[0]
#         else:
#             namespace = ""
#         zplane_group = "%s|%sZPlane_Group" % (self.light_setup,namespace)
#         cam_locator = "%s|%sCam_Location_Loc" % (self.light_setup,namespace)
#         cam_dependent = "%s|%sCamDependent_Lights" % (self.light_setup,namespace)
#         for t in [cam_dependent,zplane_group]:
#             if cmds.objExists(t):
#                 if not cmds.listRelatives(t,type="parentConstraint"):
#                     cmds.parentConstraint(cam_locator,t,mo=True)
#                 else:
#                     logger.info("Already a constraint on %s" % t)
#             else:
#                 logger.info("CAN'T FIND %s" % t)
#             logger.info("finished with %s" % t)
#         self.ReAlignLocator()
#
#     def SetupLightGroup(self):
#         light_group = cmds.group(n="LightSetup_Group", empty=True)
#         # create Static Light Group
#         static_group = cmds.group(n="Static_Lights", empty=True)
#         # create Movable Light Group
#         cam_dep_group = cmds.group(n="CamDependent_Lights", empty=True)
#         cam_loc = cmds.spaceLocator(n="Cam_Location_Loc")[0]
#         #Get camera and align locator:
#         focus_view = cmds.getPanel(withFocus=True)
#         self.SetupMessageAttr(light_group, cam_loc)
#         self.ConnectMessageAttr(from_message="%s.setup_name" % light_group,target_obj=light_group)
#         try:
#             m_editor = cmds.modelPanel(focus_view, q=True, me=True)
#             cur_cam = cmds.modelEditor(m_editor, q=True, camera=True)
#             p_delete = cmds.parentConstraint(cur_cam, cam_loc, mo=False, n="PO_ToDelete")
#             self.ConnectMessageAttr(from_message="%s.render_cam" % light_group,target_obj=cur_cam)
#             cmds.delete(p_delete)
#         except:
#             logger.info("Please set focus on the camera view and click ReAlign")
#         cmds.parent([static_group, cam_dep_group, cam_loc], light_group)
#         return light_group
#
#     def ReAlignZplanes(self):
#         if self.light_setup and self.render_cam:
#             zplanes = cmds.listConnections("%s.zplanes" % self.light_setup)[0]
#             if zplanes:
#                 cam_xform = cmds.listRelatives(self.render_cam, type="transform",parent=True)
#                 if not cmds.listRelatives(zplanes,type="parentConstraint"):
#                     temp = cmds.parentConstraint(cam_xform,zplanes,mo=False)
#                 # cmds.delete(temp)
#         else:
#             logger.info("Please Pick LightSetup and Camera, and try again")
#
#     def ReAlignLocator(self):
#         if self.light_setup and self.render_cam:
#             cam_locator = cmds.listConnections("%s.camLocator" % self.light_setup)[0]
#             zplanes = cmds.listConnections("%s.zplanes" % self.light_setup)[0]
#             if cam_locator:
#                 cam_xform = cmds.listRelatives(self.render_cam, type="transform",parent=True)
#                 if not cmds.listRelatives(cam_locator,type="parentConstraint"):
#                     temp = cmds.parentConstraint(cam_xform,cam_locator,mo=False)
#             if zplanes:
#                 if not cmds.listRelatives(zplanes,type="parentConstraint"):
#                     temp = cmds.parentConstraint(cam_xform,zplanes,mo=False)
#                 # cmds.delete(temp)
#         else:
#             logger.info("Please Pick LightSetup and Camera, and try again")


def preClean():
    light_groups = cmds.ls('::*LightSetup_Group*', long=True)
    for item in light_groups:
        try:
            cmds.delete(item)
        except:
            logger.warning('Could not delete ' + str(item))

    suns = cmds.ls(type='VRayGeoSun', long=True)
    for item in suns:
        try:
            parent = cmds.listRelatives(item, parent=True)[0]
            cmds.delete(parent)
        except:
            logger.warning('Could not delete ' + str(parent))

    skies = cmds.ls(type='VRaySky', long=True)
    for item in skies:
        try:
            cmds.delete(item)
        except:
            logger.warning('Could not delete ' + str(item))

def _maya_main_window():
    """Return Maya's main window"""
    for obj in QtWidgets.QApplication.topLevelWidgets():
        if obj.objectName() == 'MayaWindow':
            return obj
    raise RuntimeError('Could not find MayaWindow instance')


def Run():
    objectName = 'LightHelperDock'
    if not MayaDockable.dockableExists(objectName):
        MayaDockable.runDockable(objectName, 'Light Helper', MainWindow())

    # mainWin = MainWindow(parent=_maya_main_window())
    # mainWin.resize(500, 500)
    # mainWin.show()
    # mainWin.raise_()


if __name__ == '__main__':
    import sys

    if not QtWidgets.QApplication.instance():
        app = QtWidgets.QApplication(sys.argv)
    else:
        app = QtWidgets.QApplication.instance()
    # addExtraEnv()
    mainWin = MainWindow()
    mainWin.show()

# print(os.environ)
app.exec_()