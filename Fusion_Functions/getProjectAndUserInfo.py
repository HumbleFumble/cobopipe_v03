def askUserInfo(cur_comp):
    from Maya_Functions.file_util_functions import saveJson, loadJson
    import os
    project_name = None
    if "BOM_PROJECT_NAME" in os.environ:
        if not os.environ["BOM_PROJECT_NAME"] == "":
            project_name = os.environ["BOM_PROJECT_NAME"]

    fusion_user_data = "C:/Temp/fusion_user_data.json"
    cur_data = loadJson(fusion_user_data)
    project_options = ["MiasMagic2", "CowOnTheRun", "KiwiStrit3"]
    user_options = ["Bernardo", "Christian", "Cedric","Jesper", "Johanna", "Kaare", "Mads"]

    project_default = 0
    user_default = 0
    if cur_data:
        if cur_data["user"] in user_options:
            user_default = user_options.index(cur_data["user"])
        if cur_data["project"] in project_options:
            project_default = project_options.index(cur_data["project"])
    else:
        cur_data = {}
    # gui
    project_dropdown = {1: "projDrop", "Name": "Project", 2: "Dropdown", "Options": project_options,
                        "Default": project_default}
    user_dropdown = {1: "userDrop", "Name": "User", 2: "Dropdown", "Options": user_options, "Default": user_default}
    if not project_name:
        dialog = {1: project_dropdown, 2: user_dropdown}
        ret = cur_comp.AskUser("Choose project and user:", dialog)
        if ret:
            print(ret.values())
            project_return = project_options[int(ret.values()[1])]
            user_return = user_options[int(ret.values()[0])]
            cur_data["project"] = project_return
            cur_data["user"] = user_return
            os.environ["BOM_PROJECT_NAME"] = project_return
        else:
            return False
    else:
        dialog = {1: user_dropdown}
        ret = cur_comp.AskUser("Choose project and user:", dialog)
        if ret:
            user_return = user_options[int(ret.values()[0])]
            cur_data["project"] = project_name
            cur_data["user"] = user_return
        else:
            return False
    saveJson(fusion_user_data, cur_data)
    return [cur_data["project"], cur_data["user"]]