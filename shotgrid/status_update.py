import shotgrid.wrapper as sg


sg_api = sg.initialize(script="status_update",key="Eaxdtjyiiddtpx9~jxhkhqyor")
def run_on_selected(list_of_ids):
    if "," in list_of_ids:
        list_of_ids = list_of_ids.split(",")
    else:
        list_of_ids = [list_of_ids]
    for cur_id in list_of_ids:
        cur_task = sg.Task(id=int(cur_id))

        if cur_task.sg_status_list in ["apr"]:
            for ds in cur_task.downstream_tasks:
                down_task = sg.Task(id=int(ds["id"]))
                if down_task.sg_status_list in ["wtg"]:
                    #Check if there is any other tasks upstream that needs to be apr
                    set_this =True
                    if len(down_task.upstream_tasks) >1:
                        for ut in down_task.upstream_tasks:
                            if ut["id"] != cur_task.id:
                                up_task = sg.Task(id=int(ut["id"]))
                                if not up_task.sg_status_list in ["apr"]:
                                    set_this = False
                    if set_this:
                        print(f"{down_task.entity['name']}.{down_task.content} changed from '{down_task.sg_status_list}' to 'Ready to Start'")
                        down_task.sg_status_list = "ready"
                        down_task.update()
    print("### Remember to refresh browser to see changes made (F5) ###")

def run(project_code="LegoFriends"):
    filters = [["project.Project.code", "is", project_code],["sg_status_list","in",["apr"]],["downstream_tasks.Task.sg_status_list", "in", ["wtg"]]]
    fields = ["downstream_tasks"]

    all_tasks = sg_api.find(entity_type="Task",filters=filters,fields=fields)
    print(all_tasks)
    print(f"Found {len(all_tasks)} Tasks that can be set to ready")
    for found_tasks in all_tasks:
        for sg_down_task in found_tasks["downstream_tasks"]:
            wrap_down_task = sg.Task(**sg_down_task,query=True)
            set_this = True
            #Checking that this is not a mistake or haven't been changed already
            if not wrap_down_task.sg_status_list in ["wtg"]:
                set_this = False
            if len(wrap_down_task.upstream_tasks) > 1:
                print("Found multiple upstreams tasks. Checking if they are all Approved")
                for ut in wrap_down_task.upstream_tasks:
                    if ut["id"] != found_tasks["id"]:
                        up_task = sg.Task(id=int(ut["id"]))
                        if not up_task.sg_status_list in ["apr"]:
                            set_this = False
            if set_this:
                print(f"{wrap_down_task.entity['name']}.{wrap_down_task.content} changed from '{wrap_down_task.sg_status_list}' to 'Ready to Start'")
                wrap_down_task.sg_status_list = "ready"
                wrap_down_task.update()
    print("### Remember to refresh browser to see changes made (F5) ###")

def check_shot_asset_status(shot_id,task_status):
    task_relation = {"Animation":"Rig", "Lighting":"Texture","Layout":"Model"}
    cur_shot = sg.Shot(id=shot_id)
    asset_list = cur_shot.get_assets()

    for asset in asset_list:
        cur_asset_tasks = asset.get_tasks()
        if not check_apr_task_status(cur_asset_tasks,task_relation[task_status]):
            print(f"Found {asset.code} linked to {cur_shot.code}, is not ready for {task_status}")
            return False
    return True
def check_apr_task_status(task_list, task_name):
    for cur_task in task_list:
        if cur_task.content == task_name:
            if cur_task.sg_status_list in ["apr"]:
                return True
            else:
                return False

def check_subasset_status(asset_id,task_status):
    task_relation = {"Animation":"Rig", "Lighting":"Texture","Layout":"Model"}
    base_asset = sg.Asset(id=asset_id)
    asset_list = base_asset.get_assets()

    for sub_asset in asset_list:
        cur_asset_tasks = sub_asset.get_tasks()
        if not check_apr_task_status(cur_asset_tasks,task_relation[task_status]):
            print(f"Found {sub_asset.code} linked to {base_asset.code}, is not ready for {task_status}")
            return False
    return True

def update_downstream(task_id):
    approved_task = sg.Task(id=task_id)
    if not approved_task.sg_status_list == 'apr':
        return False
    
    for downstream_task in approved_task.get_downstream_tasks():
        if downstream_task.sg_status_list == 'wtg':
            status_list = []
            for upstream_task in downstream_task.get_upstream_tasks():
                status_list.append(upstream_task.sg_status_list)
            if set(status_list) == {'apr'}:
                downstream_task.sg_status_list = 'ready'
                downstream_task.update()
    return True