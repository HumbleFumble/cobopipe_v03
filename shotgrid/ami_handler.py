import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import urllib.parse
import pprint
import shotgrid.wrapper as sg
from getConfig import getConfigClass
from runtimeEnv import getRuntimeEnvFromConfig
import time
import launchHandler

protocol_dictionary = {
    "launch_in_maya": "Launch in Maya",
    "update_status": "Update status",
}


def main(args):
    # Make sure we have only one arg, the URL
    if len(args) != 1:
        return 1
    # Parse the URL:
    protocol, fullPath = args[0].split(":", 1)
    path, fullArgs = fullPath.split("?", 1)
    action = path.strip("/")
    args = fullArgs.split("&")
    params = urllib.parse.parse_qs(fullArgs)
    # This is where you can do something productive based on the params and the
    # action value in the URL. For now we'll just print out the contents of the
    # parsed URL.

    # COMMENT THIS OUT
    shotgrid_folder = os.path.dirname(__file__)
    fh = open(f"{shotgrid_folder}/output.txt", "w")
    fh.write(pprint.pformat((action, params)))

    try:
        print(
            """\n
   ██████╗ ██████╗ ██████╗  ██████╗ ██████╗ ██╗██████╗ ███████╗
  ██╔════╝██╔═══██╗██╔══██╗██╔═══██╗██╔══██╗██║██╔══██╗██╔════╝
  ██║     ██║   ██║██████╔╝██║   ██║██████╔╝██║██████╔╝█████╗  
  ██║     ██║   ██║██╔══██╗██║   ██║██╔═══╝ ██║██╔═══╝ ██╔══╝  
  ╚██████╗╚██████╔╝██████╔╝╚██████╔╝██║     ██║██║     ███████╗
   ╚═════╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝\n\n"""
        )
        project = sg.Project(
            name=params["project_name"][0], id=int(params["project_id"][0])
        )
        print(f"{'   Project name:':<25}{project.name:<31}{project.id:>5}", end="\n\n")
        CC = getConfigClass(project_name=project.code)
        runtime_environment = getRuntimeEnvFromConfig(config_class=CC)

        if action == "status_update":
            import shotgrid.status_update as status_update
            status_update.run()
        elif action == 'launch_in_maya':


            entities = []
            selected = params["selected_ids"][0].split(",")
            number_of_entities = len(selected)
            _type = params["entity_type"][0]
            wrapper_class = sg.__dict__[_type.capitalize()]



            for _id in selected:
                entity = wrapper_class(id=int(_id))
                entities.append(entity)

            if _type == "Task":
                print(f"   Selected {_type.lower()}(s):{'':<5}", end="")
                sorted_dictionary = {}

                for entity in entities:
                    parent_name = entity.entity["name"]
                    if parent_name not in sorted_dictionary:
                        sorted_dictionary[parent_name] = [entity]
                    else:
                        sorted_dictionary[parent_name].append(entity)

                first = True
                for parent_name, tasks in sorted_dictionary.items():
                    if first:
                        first = False
                        print(f"{parent_name}{'':<16}{tasks[0].entity['id']}")
                    else:
                        print(f"{'':<25}{parent_name}{'':<16}{tasks[0].entity['id']}")

                    for i, task in enumerate(tasks):
                        if i + 1 == len(tasks):
                            print(f"{'':<25} └─ {task.name:<28}{task.id}")
                        else:
                            print(f"{'':<25} ├─ {task.name:<28}{task.id}")
                    print("")

            print(f"{'   Protocol: ':<25}{protocol_dictionary[action]}")
            print(f"\n   {'─'*60}\n")

            single_target_protocols = ['launch_in_maya']
            if action in single_target_protocols:
                if len(entities) > 1:
                    print("   The current protocol only affects a single target.\n")
                    print(f"{'   Target:':<25}", end="")
                    entity = entities[0]
                    parent_name = entity.entity['name']
                    print(f"{parent_name}{'':<16}{tasks[0].entity['id']}")
                    print(f"{'':<25} └─ {task.name:<28}{task.id}")
                    print(f"\n   {'─'*60}\n")

            if action == 'launch_in_maya':
                task = entities[0]
                parent = task.get_parent(query=False)

                file_path = None
                if parent.type == 'Shot':
                    if task.name == 'Layout':
                        pass
                    elif task.name == 'Animation':
                        file_path = CC.get_shot_anim_path(*parent.name.split('_'))
                    elif task.name == 'Lighting':
                        file_path = CC.get_shot_light_file(*parent.name.split('_'))
                elif parent.type == 'Asset':
                    pass


                print(f"   Launching Autodesk Maya . . .\n")
                launchHandler.launch('maya', CC=CC, file_path=file_path)

        fh.close()
    except Exception as e:
        print(f"   EXCEPTION:\n   {e}\n")
        fh.write("\n\n\n" + str(e))
        fh.close()


    # input('\n   > Press ENTER to exit') # To keep console open
    time.sleep(10)

def get_shot_dict(episode="", sequence="", shot=""):
    return {"episode_name": episode, "seq_name": sequence, "shot_name": shot}


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
