import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import urllib.parse
import pprint
import shotgrid.wrapper as sg
from getConfig import getConfigClass
from runtimeEnv import getRuntimeEnvFromConfig

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
    fh = open(r'C:\Users\mha\Projects\cobopipe_v02-001\shotgrid\output.txt', 'w')
    fh.write(pprint.pformat((action, params)))
    fh.close()

    project = sg.Project(name=params['project_name'], id=params['project_id'])
    CC = getConfigClass(project_name=project.code)
    runtime_environment = getRuntimeEnvFromConfig(config_class=CC)

    if params['entity_type'][0] == 'Task':
        task = sg.Task(id=params['selected_ids'][0])
        fh = open(r'C:\Users\mha\Projects\cobopipe_v02-001\shotgrid\output.txt', 'w+')
        fh.write(pprint.pformat(task.name))
        fh.close()

if __name__ == '__main__':
    # print('Running :D')
    # fh = open(r'C:\Users\mha\Projects\cobopipe_v02-001\shotgrid\output.txt', 'w+')
    # for arg in sys.argv:
    #     fh.write(arg + "\n")
    # fh.close()
    # print('Hiii')
    sys.exit(main(sys.argv[1:]))