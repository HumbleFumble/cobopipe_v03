import shotgrid.wrapper as sg
#to do  go through
def ready_up_classes(list_of_shots=None, project_name=None, seq_name=None, episode_name=None,task_template=r"CB// Anim 3D"):
    list_of_wrap_shots = []

    p = sg.Project(code=project_name)
    episodes = p.get_episodes(extra_filters=[["code", "is", episode_name]])
    seq_list = p.get_sequences(extra_filters=[["code", "is", seq_name]])
    shots = p.get_shots()
    if episodes:
        ep = episodes[0]
    else:
        ep = p.create_episode(code=episode_name)
    if seq_list:
        seq = seq_list[0]
    else:
        seq = ep.create_sequence(code=seq_name)
    wrap_task_temp = sg.TaskTemplate(code=task_template)
    for shot, duration in list_of_shots:
        if not shot in (shot_i.code for shot_i in shots):
            new_shot = seq.create_shot(code=shot, task_template=wrap_task_temp, sg_cut_duration=duration)
            list_of_wrap_shots.append(new_shot)
        else:
            print(f"Shot: {shot} already exist. Skipping it." )



    print(episodes)
    print(seq_list)
    print(shots)
    print(f"Calls to shotgrid api: {sg.sg_counter}")
    # seq = sg.Sequence(project=p.identity, code=seq_name)
    # wrap_task_temp = sg.TaskTemplate(code=task_template)
    #

    #
    # return list_of_wrap_shots


if __name__ == "__main__":
    project_name = "LegoFriends"
    seq_name = "S105_SQ010"
    shot_list = [["S105_SQ010_SH015", 20]]
    ready_up_classes(list_of_shots=shot_list, project_name=project_name, episode_name="S105",seq_name=seq_name)
