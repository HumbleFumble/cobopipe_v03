import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import urllib.parse
import pprint
import shotgrid.wrapper as sg
from getConfig import getConfigClass
from runtimeEnv import getRuntimeEnvFromConfig
import time

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
    fh = open(f'{shotgrid_folder}/output.txt', 'w')
    fh.write(pprint.pformat((action, params)))

    try:
        print("""
                           ██████╗ ██████╗ ██████╗  ██████╗ ██████╗ ██╗██████╗ ███████╗
                          ██╔════╝██╔═══██╗██╔══██╗██╔═══██╗██╔══██╗██║██╔══██╗██╔════╝
                          ██║     ██║   ██║██████╔╝██║   ██║██████╔╝██║██████╔╝█████╗  
                          ██║     ██║   ██║██╔══██╗██║   ██║██╔═══╝ ██║██╔═══╝ ██╔══╝  
                          ╚██████╗╚██████╔╝██████╔╝╚██████╔╝██║     ██║██║     ███████╗
                           ╚═════╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝\n\n\n""")
        project = sg.Project(name=params['project_name'][0], id=int(params['project_id'][0]))
        CC = getConfigClass(project_name=project.code)
        runtime_environment = getRuntimeEnvFromConfig(config_class=CC)

        if action == "update_status":
            print("STATUS UPDATE")
            import shotgrid.status_update as status_update
            # status_update.run_on_selected(params['selected_ids'][0])
            status_update.run()
        fh.close()
        time.sleep(1000)
    except Exception as e:
        fh.write("\n\n\n" + str(e))
        fh.close()




if __name__ == '__main__':
    # print('Running :D')
    # fh = open(r'C:\Users\mha\Projects\cobopipe_v02-001\shotgrid\output.txt', 'w+')
    # for arg in sys.argv:
    #     fh.write(arg + "\n")
    # fh.close()
    # print('Hiii')

    sys.exit(main(sys.argv[1:]))