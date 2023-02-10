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
    for d_tasks in all_tasks:
        for i in d_tasks["downstream_tasks"]:
            cur_task = sg.Task(**i,query=True)
            print(f"{cur_task.entity['name']}.{cur_task.content} changed from '{cur_task.sg_status_list}' to 'Ready to Start'")
            cur_task.sg_status_list = "ready"
            cur_task.update()
    print("### Remember to refresh browser to see changes made (F5) ###")

