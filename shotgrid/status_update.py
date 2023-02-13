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


def update_downstream(entity_id):
    approved_task = sg.Task(id=entity_id)
    for downstream_task in approved_task.get_downstream_tasks():
        status_list = []
        for upstream_task in downstream_task.get_upstream_tasks():
            status_list.append(upstream_task.sg_status_list)
        if set(status_list) == {'apr'}:
            downstream_task.sg_status_list = 'ready'
            downstream_task.update()