import shotgrid.wrapper as sg

def init(list_of_ids):

    sg.initialize(script="status_update",key="Eaxdtjyiiddtpx9~jxhkhqyor")
    list_of_tasks = []
    for cur_id in list_of_ids:
        cur_task = sg.Task(id=int(cur_id))
        print(cur_task.sg_client_status)
        list_of_tasks.append(cur_task)

