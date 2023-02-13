import os.path

import shotgrid.wrapper as sg
from getConfig import getConfigClass

def ready_sg_site(list_of_entities=None,list_of_ids=None):
    """sort through list_of_ids

    get all shot/assets for current level of entity of ids and linked children.
    get the shot entity for the task.
    maybe have a dict that says what thumbnails are called for each task.
    check the server shot folder for thumbnails.
    Attach available thumbnails to the correct level of tasks on shot/asset
    """
    sg_api = sg.get_shotgrid()
    CC = getConfigClass(project_name="LegoFriends")
    if not list_of_entities:
        for cur_id in list_of_ids:
            cur_class = sg.Task(id=int(cur_id))
            list_of_entities.append(cur_class)

    for cur_entity in list_of_entities:
        thumbnail_path_list = find_server_thumbnail_func(CC=CC,info_dict=cur_info_dict)
        for thumb in thumbnail_path_list:
            sg_api.upload_thumbnail("Task",int(cur_entity.id),thumb)

def find_server_thumbnail_func(CC=None,info_dict=None):
    # ask for project

    return_list = []
    if "asset_name" in info_dict:
        thumb_path = CC.get_asset_thumbnail_path(**info_dict)
        if os.path.exists(thumb_path):
            return_list.append(thumb_path)
    if "shot_name" in info_dict:
        if "Layout" in info_dict["task_list"]:
            thumb_path = CC.get_shot_anim_thumbnail_path(**info_dict)
            if os.path.exists(thumb_path):
                return_list.append(thumb_path)
        elif "Animation" in info_dict["task_list"]:
            thumb_path = CC.get_shot_animatic_thumbnail_path(**info_dict)
            if os.path.exists(thumb_path):
                return_list.append(thumb_path)
        elif "Comp" in info_dict["task_list"]:
            thumb_path = CC.get_shot_comp_thumbnail_path(**info_dict)
            if os.path.exists(thumb_path):
                return_list.append(thumb_path)
    return return_list
