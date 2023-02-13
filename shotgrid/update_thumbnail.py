import shotgrid.wrapper as sg
from getConfig import getConfigClass

def ready_sg_site(list_of_ids):
    """sort through list_of_ids

    get all shot/assets for current level of entity of ids and linked children.
    get the shot entity for the task.
    maybe have a dict that says what thumbnails are called for each task.
    check the server shot folder for thumbnails.
    Attach available thumbnails to the correct level of tasks on shot/asset
    """
    sg_api = sg.get_shotgrid()
    thumbnail_path = find_server_thumbnail_func()

    sg_api.upload_thumbnail("Task",int(cur_id),thumbnail_path)
    pass

def find_server_thumbnail_func(CC=None,info_dict=None):
    # ask for project
    CC = getConfigClass(project_name="LegoFriends")
    if "asset_name" in info_dict:
        thumb_path = CC.get_asset_thumbnail_path(**info_dict)
    if "shot_name" in info_dict:
        if info_dict["task_name"] == "Animation":
            thumb_path = CC.get_shot_anim_thumbnail_path(**info_dict)
