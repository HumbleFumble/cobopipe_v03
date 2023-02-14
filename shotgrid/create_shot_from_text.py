import shotgrid.wrapper as sg
#to do  go through
def ready_up_classes(list_of_shots=None, project_name=None, seq_name=None, episode_name=None,task_template=r"CB// Anim 3D"):
    list_of_wrap_shots = []

    p = sg.Project(code=project_name)
    episodes = p.get_episodes()
    # seqs = p.get_sequences()
    # shots = p.get_shots()
    print(episodes)
    # print(seqs)
    # print(shots)
    # seq = sg.Sequence(project=p.identity, code=seq_name)
    # wrap_task_temp = sg.TaskTemplate(code=task_template)
    #
    # for shot, duration in list_of_shots:
    #     new_shot = seq.create_shot(code=shot, task_template=wrap_task_temp, sg_cut_duration=duration)
    #     list_of_wrap_shots.append(new_shot)
    #
    # return list_of_wrap_shots
{'type': 'Episode', 'id': 5, 'project': {'id': 122, 'name': 'Lego Friends - Wildbrain', 'type': 'Project'}, 'code': 'S105', 'description': "Olly's folly", 'sg_status_list': None, 'sequences': [{'id': 41, 'name': 'S105_SQ010', 'type': 'Sequence'}]}
# {'type': 'Episode', 'id': 6, 'project': {'id': 122, 'name': 'Lego Friends - Wildbrain', 'type': 'Project'}, 'code': 'S104', 'description': 'Cardboard beats', 'sg_status_list': None, 'sequences': []}, {'type': 'Episode', 'id': 7, 'project': {'id': 122, 'name': 'Lego Friends - Wildbrain', 'type': 'Project'}, 'code': 'S103', 'description': '8-bit Chaos', 'sg_status_list': None, 'sequences': []}, {'type': 'Episode', 'id': 8, 'project': {'id': 122, 'name': 'Lego Friends - Wildbrain', 'type': 'Project'}, 'code': 'S101', 'description': "Nova's got game", 'sg_status_list': None, 'sequences': []}, {'type': 'Episode', 'id': 9, 'project': {'id': 122, 'name': 'Lego Friends - Wildbrain', 'type': 'Project'}, 'code': 'S102', 'description': 'Muddy puppy', 'sg_status_list': None, 'sequences': []}, {'type': 'Episode', 'id': 37, 'project': {'id': 122, 'name': 'Lego Friends - Wildbrain', 'type': 'Project'}, 'code': 'S999', 'description': None, 'sg_status_list': None, 'sequences': []}, {'type': 'Episode', 'id': 38, 'project': {'id': 122, 'name': 'Lego Friends - Wildbrain', 'type': 'Project'}, 'code': 'S999', 'description': None, 'sg_status_list': None, 'sequences': []}]


if __name__ == "__main__":
    project_name = "LegoFriends"
    seq_name = "S105_SQ010"
    shot_list = [["S105_SQ010_SH015", 20]]
    ready_up_classes(list_of_shots=shot_list, project_name=project_name, seq_name=seq_name)
