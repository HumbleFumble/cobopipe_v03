import os
from subprocess import Popen, PIPE


def submit_command_line_job(executable=r'C:\Windows\system32\cmd.exe', arguments='', **kwargs):
  """Submits a commandline job to Deadline.

  Args:
      executable (str, optional): Path to executable. Defaults to r'C:\Windows\system32\cmd.exe'.
      arguments (str, optional): Arguments to run as a string. Defaults to ''.

  Returns:
      _type_: _description_
  """

  deadlineBin = os.getenv("DEADLINE_PATH")
  deadline_exe = f'{deadlineBin}{os.sep}deadlinecommand.exe'
  command = f'"{deadline_exe}" -SubmitCommandLineJob -executable "{executable}"'

  if arguments:
    # Converting the arguments to Deadline's way of writing arguments with conflicting quotation.
    arguments = arguments.replace('"', '<QUOTE>')
    command = f'{command} -arguments "{arguments}"'
    
  for keyword, value in kwargs.items():
    command = f'{command} -{keyword} "{value}"'

  # Submitting the command
  process = Popen(command, stdout=PIPE, stderr=PIPE)
  stdout, stderr = process.communicate()
  
  print(stdout.decode('utf-8'))
  print(stderr.decode('utf-8'))
  
  return  stdout, stderr


if __name__ == "__main__":
  submit_command_line_job(
    executable=r'T:\_Executables\python\Python310\python.exe',
    arguments=r'"T:\_Pipeline\cobopipe_v02-001\zipUtil.py" "\\192.168.0.225\production\930462_HOJ_Project\Production\Film\S107\S107_SQ020\S107_SQ020_SH010\S107_SQ020_SH010" "\\192.168.0.225\production\930462_HOJ_Project\Production\Film\S107\S107_SQ020\S107_SQ020_SH010\S107_SQ020_SH010_zipped.zip"',
    pool='hoj',
    group='python',
    priority=50,
    name='S107_SQ020_SH010.zip'
  )