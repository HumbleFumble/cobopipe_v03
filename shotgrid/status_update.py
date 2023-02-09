import shotgrid.wrapper as sg
import shotgun_api3
import time
def run(list_of_ids):
    print(list_of_ids)
    if("," in list_of_ids):
        list_of_ids = list_of_ids.split(",")
    else:
        list_of_ids = [list_of_ids]
    print(list_of_ids)

    sg.initialize(script="status_update",key="Eaxdtjyiiddtpx9~jxhkhqyor")
    list_of_tasks = []
    for cur_id in list_of_ids:
        cur_task = sg.Task(id=int(cur_id))
        print(cur_task.sg_status_list)

        if cur_task.sg_status_list in ["apr"]:

            print(cur_task.downstream_tasks)
            for ds in cur_task.downstream_tasks:
                down_task = sg.Task(id=int(ds["id"]))
                print(down_task.sg_status_list)
                if down_task.sg_status_list in ["wtg"]:
                    print(down_task.id)
                    try:
                        shotgun_api3.Shotgun.update("Task",int(down_task.id),{"sg_status_list":"ready"})
                    except Exception as e:
                        print(e)
        #
        #
        # list_of_tasks.append(cur_task)
    time.sleep(1000)

