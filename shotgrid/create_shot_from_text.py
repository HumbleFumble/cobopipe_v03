import shotgrid.wrapper as sg

def ready_up_classes(list_of_shots=None,project_name=None,seq_name=None,task_template=r"CB// Anim 3D"):
    list_of_wrap_shots = []
    p = sg.Project(code=project_name)
    seq = sg.Sequence(project=p.identity, code=seq_name)
    for shot,duration in list_of_shots:
        print(shot,duration)
        list_of_wrap_shots.append(seq.create_shot(code=shot,task_template=task_template,sg_cut_duration=duration))

ready_up_classes()
