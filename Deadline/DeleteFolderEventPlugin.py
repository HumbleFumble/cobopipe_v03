"""
Notes:

    Need to define which cmdline or powershell call, can be run from python to delete the folder.
    If I manage to delete it via python, we should be able to call it for each job recieved.

    Using EventPlugins for deadline.

    Step 1.
    Find a way to remove the folder from python. Either calling powershell.
        Problem 1. Permissions. We are not allowed to delete the files because we don't have the correct permissons.
        needs to be elevated to admin or deadline user?
        Problem 2. The python lock file is "in use" so we can delete it. We kill the worker before we manually delete it now.
        Could try to find the process and kill it. But if it is the worker process then we have to start the worker service again afterwards.
    Could be needed to kill the worker process. Can we start it up again?
    Step 2.
    Create a custom event that uses the call back: OnSlaveStartingJob
    Check out the documentation on deadline: https://docs.thinkboxsoftware.com/products/deadline/10.3/1_User%20Manual/manual/event-plugins.html
    Questions: How are eventPlugins run? Are they still being RunAsUser?
    Are they a child process to the worker service, so if we kill the worker service the eventPlugin process also dies?
"""
