import os
from subprocess import Popen, PIPE


def submit_command_line_job(executable=r'C:\Windows\system32\cmd.exe', arguments='', **kwargs):
  deadlineBin = os.getenv("DEADLINE_PATH")
  deadline_exe = f'{deadlineBin}{os.sep}deadlinecommand.exe'
  command = f'"{deadline_exe}" -SubmitCommandLineJob -executable "{executable}"'
  
  if arguments:
    arguments = arguments.replace('"', '<QUOTE>')
    command = f'{command} -arguments "{arguments}"'
    
  for keyword, value in kwargs.items():
    command = f'{command} -{keyword} "{value}"'

  process = Popen(command, stdout=PIPE, stderr=PIPE)
  stdout, stderr = process.communicate()
  
  print(stdout.decode('utf-8'))
  print(stderr.decode('utf-8'))
  
  return  stdout, stderr


# def submit_python_job(executable=r'T:\_Executables\python\Python310\python.exe', arguments='', **kwargs):
#   deadlineBin = os.getenv("DEADLINE_PATH")
#   deadline_exe = f'{deadlineBin}{os.sep}deadlinecommand.exe'
#   command = f'"{deadline_exe}" -SubmitCommandLineJob -executable "{executable}"'
  
#   if arguments:
#     arguments = arguments.replace('"', '<QUOTE>')
#     command = f'{command} -arguments "{arguments}"'
    
#   for keyword, value in kwargs.items():
#     command = f'{command} -{keyword} "{value}"'

#   process = Popen(command, stdout=PIPE, stderr=PIPE)
#   stdout, stderr = process.communicate()
  
#   print(stdout.decode('utf-8'))
#   print(stderr.decode('utf-8'))
  
#   return  stdout, stderr


# SubmitCommandLineJob <executable <Value>> [<arguments <Value>>] <frames <Value>> [<chunksize <Value>> <pool <Value>> <group <Value>> <priority <Value>> <name <Value>> <department <Value>> <initialstatus <Value>> <prop <Key=Value>>]
#   Submits a generic command line job to Deadline. The <STARTFRAME> and
#   <ENDFRAME> strings in the command line arguments will be replaced with the
#   actual start and end frame for each task. The <QUOTE> string in the command
#   line arguments will be replaced with a '"' character.
#     executable               The command line executable.
#     arguments                Optional. The command line arguments.
#     frames                   The frame range to render.
#     chunksize                Optional. The task chunk size.
#     pool                     Optional. The pool the job belongs to.
#     group                    Optional. The group the job belongs to.
#     priority                 Optional. The job priority (0 is the lowest).
#     name                     Optional. The job name.
#     department               Optional. The job department.
#     initialstatus            Optional. The job's initial state
#                              (Active/Suspended).
#     prop                     Optional. Extra submission properties in the
#                              form Key=Value.


if __name__ == "__main__":
  submit_command_line_job(
    executable=r'T:\_Executables\python\Python310\python.exe',
    arguments=r'"T:\_Pipeline\cobopipe_v02-001\zipUtil.py" "\\192.168.0.225\production\930462_HOJ_Project\Production\Film\S107\S107_SQ020\S107_SQ020_SH010\S107_SQ020_SH010" "\\192.168.0.225\production\930462_HOJ_Project\Production\Film\S107\S107_SQ020\S107_SQ020_SH010\S107_SQ020_SH010_zipped.zip"',
    pool='hoj',
    group='python',
    priority=50,
    name='S107_SQ020_SH010.zip'
  )