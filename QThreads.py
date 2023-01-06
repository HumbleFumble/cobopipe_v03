from threading import Thread
from threading import activeCount
import multiprocessing
import subprocess
from getConfig import getConfigClass
CC = getConfigClass()
from runtimeEnv import getRuntimeEnvFromConfig

from Log.CoboLoggers import getLogger
logger = getLogger()

try:
    from queue import Queue
except:
    from Queue import Queue


def ProcRun(maya_py_cmd):
    run_env = getRuntimeEnvFromConfig(CC,local_user=True)
    logger.info("RUN ENV: %s" % run_env["BOM_PROJECT_NAME"])
    base_command = 'mayapy.exe -c "%s"' % (maya_py_cmd)
    c_p = subprocess.Popen(base_command, shell=True, universal_newlines=True, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,env=run_env)
    #print("%s" % (c_p.communicate()[0]))
    var = c_p.communicate()
    logger.debug(var[0])
    logger.debug(var[1])

def ProcWorker(queue):
    for args in iter(queue.get, None):
        try:
            ProcRun(args)
            #ProcRun(*args)
        except Exception as e:  # catch exceptions to avoid exiting the
            # thread prematurely
            # print('%r failed: %s' % (args, e,), file=sys.stderr)
            logger.warning('%s failed: %s' % (args, e))

def CreateProcQueue(cmd_list=None):
    # start threads
    cpu_total = multiprocessing.cpu_count()
    cpu_current = activeCount()
    logger.info("Total Process's: %s -> Using: %s" % (cpu_total, cpu_current))
    number_of_workers = int(int(cpu_total) - int(cpu_current) - 1)
    q = Queue()
    threads = [Thread(target=ProcWorker, args=(q,)) for _ in range(number_of_workers)]
    for t in threads:
        t.daemon = True  # threads die if the program dies
        t.start()

    # populate files
    if cmd_list:
        for c in cmd_list:
            q.put_nowait(c)

    for _ in threads: q.put_nowait(None)  # signal no more files
    for t in threads: t.join()  # wait for completion
    logger.info("Procs working on queue")



def CreateMayaPyCmd(shot_path, shot_name):
    script_content = """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
import SequenceView as SV
cmds.file('%s', open=True,f=True)
SV.CleanUpAnimationScene('%s')
cmds.file(rename='%s')
cmds.file(type='mayaAscii')
cmds.file(save=True)
cmds.quit(f=True)
""" % (shot_path, shot_name,shot_path)
    script_content = ";".join(script_content.split("\n"))
    return script_content
    # base_command = 'mayapy.exe -c "%s"' % (script_content)

if __name__ == "__main__":
    path_list = ["my_path","next_path"] #list of things to do.

    proc_list = [] #List of workers to put to the queue.
    for path in path_list:
        c_cmd = CreateMayaPyCmd(path)  # Create commandline to run with mayapy
        proc_list.append(c_cmd)
    CreateProcQueue(proc_list)  # Create a thread queue and work through it