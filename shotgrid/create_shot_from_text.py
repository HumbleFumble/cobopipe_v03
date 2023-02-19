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
            new_shot = seq.create_shot(code=shot, task_template=wrap_task_temp, sg_cut_duration=int(duration))
            list_of_wrap_shots.append(new_shot)
        else:
            print(f"Shot: {shot} already exist. Skipping it." )
    print(f"Calls to shotgrid api: {sg.sg_counter}")
    return list_of_wrap_shots

def auto_bid(shot_name=None,task_id=None,project_name=None,task_bid_dict={"Layout":230, "Animation":23,"Lighting":50,"Comp":50}):
    """
    Roughed out. Doesn't set it yet. Not sure what the best auto calculation setup would be.
    """
    if shot_name and not task_id:
        #query all task attached to shot
        if project_name:
            p = sg.Project(code=project_name)
            shot = sg.Shot(code=shot_name,project=p.identity)
        else:
            shot = sg.Shot(code=shot_name)
        task_list = shot.get_tasks()
    else:
        task_list = [sg.Task(id=task_id)]
    if shot:
        duration = float(shot.sg_cut_duration)
    for cur_task in task_list:
        if cur_task.content in task_bid_dict:
            print(cur_task.content, duration, duration/task_bid_dict[cur_task.content])
            if not cur_task.est_in_mins:

                pass #cur_task.est_in_mins = cur_task.duration/task_bid_dict[cur_task.content]
    print(task_list)





def ready_shot_list_from_file(file_path=None):

    shot_list = []
    # file_path = r"C:\Users\cg\PycharmProjects\cobopipe_v02-001\local\previs_output_test.txt"
    with open(file_path, 'r') as shot_file:
        content = shot_file.read()
    shot_file.close()
    for line in content.split("\n"):
        if not line == "":
            shot, duration = line.split(",")
            shot_list.append([shot, duration])
    return shot_list

if __name__ == "__main__":
    auto_bid("S105_SQ010_SH010",project_name="LegoFriends")

    ##### Create shots example #####
    # project_name = "LegoFriends"
    # file_path = r"C:\Users\cg\PycharmProjects\cobopipe_v02-001\local\previs_output_test.txt"
    # shot_list = ready_shot_list_from_file(file_path)
    #
    # # if working with the current split-up file(S105_SQ010.txt) output we could do:
    # # episode_name, seq_name = filename.split(".")[0].split("_")
    # episode_name = "S105"
    # seq_name = "S105_SQ010"
    #
    #
    # ready_up_classes(list_of_shots=shot_list, project_name=project_name, episode_name=episode_name,seq_name=seq_name)

