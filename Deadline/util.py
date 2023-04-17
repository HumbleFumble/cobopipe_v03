import os
import subprocess


def callDeadlineCommand(*args):
    deadlineBin = os.environ.get('DEADLINE_PATH')
    if not deadlineBin:
        commandLine = 'deadlinecommand'
    else:
        commandLine = f'{deadlineBin}{os.sep}deadlinecommand'

    return subprocess.check_output([commandLine, *args]).decode('UTF-8')


if __name__ == '__main__':
    result = callDeadlineCommand('-GetCurrentUserHomeDirectory')
    print(result)
    