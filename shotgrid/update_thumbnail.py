import os.path

import shotgrid.wrapper as sg
from getConfig import getConfigClass

def ready_sg_site(list_of_task_entities=None, list_of_ids=None):
    """sort through list_of_ids

    get all shot/assets for current level of entity of ids and linked children.
    get the shot entity for the task.
    maybe have a dict that says what thumbnails are called for each task.
    check the server shot folder for thumbnails.
    Attach available thumbnails to the correct level of tasks on shot/asset
    """
    sg_api = sg.get_shotgrid()
    CC = getConfigClass(project_name="LegoFriends")
    if not list_of_task_entities:
        for cur_id in list_of_ids:
            cur_task_class = sg.Task(id=int(cur_id))
            list_of_task_entities.append(cur_task_class)

    for cur_entity in list_of_task_entities:
        "Generate info dict: Need episode/seq/shot name, and a task name"
        thumbnail_path_list = find_server_thumbnail_func(CC=CC,info_dict=cur_info_dict)
        for thumb in thumbnail_path_list:
            "Might have to rename thumbs before uploading?"
            sg_api.upload_thumbnail("Task",int(cur_entity.id),thumb)
def update_shot_thumbnail(project_name=None,shot_name=None,task_list=[]):
    """Another approach    """
    sg_api = sg.get_shotgrid()
    CC = getConfigClass(project_name=project_name)
    sg_project = sg.Project(code=project_name)
    sg_shot = sg.Shot(code=shot_name,project=sg_project.identity)
    episode_name,    seq_name,    shot_name = shot_name.split["_"]

    sg_task_list = []
    if task_list:
        sg_task_list = sg_shot.get_tasks()
    else:
        temp_list = sg_shot.get_tasks()
        for cur_task in temp_list:
            if cur_task.content in task_list:
                sg_task_list.append(cur_task)
    print(sg_task_list)
    for cur_task in sg_task_list:
        info_dict = {"episode_name":episode_name,"seq_name":seq_name,"shot_name":shot_name,task_list:[cur_task.content]}
        # "Generate info dict: Need episode/seq/shot name, and a task name"
        thumbnail_path_list = find_server_thumbnail_func(CC=CC,info_dict=info_dict)
        for thumb in thumbnail_path_list:
        #     "Might have to rename thumbs before uploading?"
            sg_api.upload_thumbnail("Task",int(cur_task.id),thumb)
    print(f"Calls to shotgrid api: {sg.sg_counter}")

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

if __name__ == "__main__":
    update_shot_thumbnail(project_name="LegoFriends",shot_name="S105_SQ010_SH010",task_list=["Layout","Animation"])