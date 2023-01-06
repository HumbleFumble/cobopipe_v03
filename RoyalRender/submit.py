from subprocess import Popen, PIPE
import os
from Log.CoboLoggers import getLogger
logger = getLogger()

def batchScriptSubmit(file, sendToAll=False, project_name="MiasMagic2", client_pool="ALL", user_name="Unknown", episode=None, sequence=None, shot=None, priority=90, waitForJobID=None):
    overwrite = True
    if sendToAll:
        software = "ExecuteOnceAll"
    else:
        software = "Execute"
    software_version = "1.0"
    if "RR_Root" in os.environ:
        rr_root = os.environ["RR_Root"]
    else:
        rr_root = r"\\192.168.0.235\projekter\tools\RoyalRender"
    rr_submitter = os.path.abspath(os.path.join(rr_root, 'bin/win64/rrSubmitterconsole.exe')).replace(os.sep, '/').replace('//', os.sep + os.sep)
    # rr_submitter = "%RR_Root%/bin/win64/rrSubmitterconsole.exe"
    rr_cmd = "%s %s" % (rr_submitter, file)  # Set scene

    rr_cmd = "%s -S %s" % (rr_cmd, software)  # set software

    if waitForJobID:
        rr_cmd = '%s -WWID %s' % (rr_cmd, waitForJobID)

    # # Submitter flags:
    scene_name = file.split("/")[-1].split(".")[0]
    rr_cmd = '%s "CSCN=0~%s"' % (rr_cmd, scene_name)  # set scene name
    rr_cmd = '%s "CSQN=0~%s"' % (rr_cmd, episode)  # set episode name

    rr_cmd = '%s "CSHN=0~%s"' % (rr_cmd, sequence)
    rr_cmd = '%s "CVN=0~%s"' % (rr_cmd, shot)

    rr_cmd = '%s "UN=0~%s"' % (rr_cmd, user_name)  # set user name

    # set project "nice" name
    rr_cmd = '%s "CPN=0~%s"' % (rr_cmd, project_name)
    rr_cmd = '%s "DCG=0~%s"' % (rr_cmd, client_pool)  # set client pool
    rr_cmd = '%s "Priority=1~%s"' % (rr_cmd, priority)  # set user name

    logger.info(rr_cmd)
    process = Popen(rr_cmd, stdout=PIPE, stderr=PIPE)
    # stdout, stderr = process.communicate()
    # logger.info(stdout)
    return rr_cmd
