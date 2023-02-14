import shotgrid.wrapper as sg

def ready_up_classes(list_of_shots=None, project_name=None, seq_name=None, task_template=r"CB// Anim 3D"):
    list_of_wrap_shots = []
    p = sg.Project(code=project_name)
    seq = sg.Sequence(project=p.identity, code=seq_name)
    wrap_task_temp = sg.TaskTemplate(code=task_template)
    
    for shot, duration in list_of_shots:
        new_shot = seq.create_shot(code=shot, task_template=wrap_task_temp, sg_cut_duration=duration)
        list_of_wrap_shots.append(new_shot)

    return list_of_wrap_shots

if __name__ == "__main__":
    project_name = "LegoFriends"
    seq_name = "S105_SQ010"
    shot_list = [["S105_SQ010_SH015", 20]]
    ready_up_classes(list_of_shots=shot_list, project_name=project_name, seq_name=seq_name)
