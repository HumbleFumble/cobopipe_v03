import json
import os

from PySide2 import QtWidgets, QtCore, QtGui

from getConfig import getConfigClass
CC = getConfigClass()

class CategoryHandler(object):
    def __init__(self):
        self.category = ""
        self.save_path_categories = CC.get_contact_sheet_category_file()
        self.skip_categories = ["Sync", "Isolate", "Freeze"]
        self.category_dict = self.LoadSettings(self.save_path_categories)

    def CheckForSkip(self,category):
        if category in self.skip_categories:
            return False
        else:
            return True

    def getCategoryNodes(self,category):
        if category in self.category_dict:
            return self.category_dict[category]
        else:
            return None

    def getCategories(self):
        return self.category_dict.keys()

    def UpdateJsonDict(self, save_path=None, current_dict=None):
        # if not current_dict:
        #     current_dict = self.GetDictFromCurrentNodes()
        new_dict = self.LoadSettings(save_path)
        if new_dict:
            new_dict.update(current_dict)
            return new_dict
        else:
            return current_dict

    def CreateNewCategory(self, category, list_of_nodes=[]):

        old_info = self.LoadSettings(save_location=self.save_path_categories)

        # if LoadSettings return None, Make empty dictionary
        if category in old_info:
            return False

        old_info[category] = []
        if list_of_nodes:
            for i in list_of_nodes:
                name = i.getName()  # Gets name of item from QModelIndex data
                old_info[category].append(name)

        self.SaveSettings(save_location=self.save_path_categories, save_info=old_info)
        self.category_dict = old_info

        return self.category_dict[category]


    def DeleteCategory(self,category=None):
        # Get dictionary and remove (pop) the category key within
        cat_dict = self.LoadSettings(self.save_path_categories)
        cat_dict.pop(category)

        # Save result to JSON
        print("Updated Dict: %s" % cat_dict)
        self.SaveSettings(save_location=self.save_path_categories, save_info=cat_dict)
        self.category_dict = cat_dict

    def AddToCategory(self, category=None,list_of_nodes=[]):

        # Get contents of JSON as Dict Example: {"Forest":[node_name, node_name2]}
        file_dict = self.LoadSettings(save_location=self.save_path_categories)

        # if LoadSettings return None, Make empty dictionary

        # Put selected indexes of QListView into a list
        selection = []
        for i in list_of_nodes:
            name = i.getName()  # Gets name of item from QModelIndex data
            selection.append(name)

        if file_dict:
            if category in file_dict.keys():  # check if category is in file dict
                file_dict[category].extend(selection)
                file_dict[category] = list(set(file_dict[category]))
            else:
                file_dict[category] = selection
                print("Added %s to %s" % (selection, category))
        else:
            file_dict[category] = selection
            print("Added %s to %s" % (selection, category))

        # Save result to JSON
        print("Updated Dict: %s" % file_dict)
        self.SaveSettings(save_location=self.save_path_categories, save_info=file_dict)
        self.category_dict = file_dict

        return self.category_dict


    def RemoveFromCategory(self, category=None, list_of_nodes=[]):
        if category == "Sync":
            return
        # Get contents of JSON as Dict
        old_info = self.LoadSettings(save_location=self.save_path_categories)
        # Put selected indexes of QListView into a list
        selection = []
        for i in list_of_nodes:
            name = i.getName()  # Gets name of item from QModelIndex data
            selection.append(name)

        # Compare category list using sets, since we don't need duplicates. And apperantly thats a fast approach..
        if category in old_info:
            old_info[category] = list(set(old_info[category]) - set(selection))
        if len(old_info[category]) == 0:
            old_info.pop(category)

        # Save result to JSON
        self.SaveSettings(save_location=self.save_path_categories, save_info=old_info)
        self.category_dict = old_info

        return self.category_dict[category]

    def SaveSettings(self, save_location, save_info):
        with open(save_location, 'w+') as saveFile:
            json.dump(save_info, saveFile)
        saveFile.close()

    def LoadSettings(self, save_location):
        if os.path.isfile(save_location):
            with open(save_location, 'r') as saveFile:
                loadedSettings = json.load(saveFile)
            # if 'selected node' in loadedSettings.keys():
            if loadedSettings:
                return loadedSettings
        else:
            print("no category file found")
        return {}

    """
    States of the table:
    Isolated? -a quick category? Means that it shouldn't save changes to this category out to file.
    Sync To Tree - follows the tree (does so already, should be relatively easy to connect)
    By Category

    Functions for category setup:
    Load Category dict from file(file)
    Save Category dict to file(file,dict)
    Create Category (name, list_of_nodes)
    Filter by Category(name)
    Add to Category(name, list_of_nodes)
    Remove from Category(name, list_of_nodes)
    Delete Category(name)

    Functions for Isolate: (maybe just use category functions?)
    Isolate selection
    Add to isolate
    remove from isolate
    clear/delete isolate (clears isolate and returns to Sync)
    isolate_dict to hold node-info

    UI:
    combobox for categories. Should have Sync set as default. Should also have Isolate category added besides Sync.
    Maybe a freeze/Un-Sync function to break sync, but keep the current nodes in view?

    Bttn for create category -should create popup asking for name
    Bttn for delete category  -should create popup for confirmation of deletion

    Popup

    Right click (event manager) calls:
    Isolate Selection
    Clear isolate view
    Create Category (same as call as bttn?)
    Filter By Category (submenu) ->
        list of all categories. (Should just change the combobox?)
    Edit Category (submenu) ->
        add to category (should also work on isolate)
        remove from category (should also work on isolate)
        Delete category

    """
