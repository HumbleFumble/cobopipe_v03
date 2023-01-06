
from PySide2 import QtCore
signal = QtCore.Signal



class Signals(QtCore.QObject):
    created = signal(dict)
    error = signal(object)  # To be defined later...
    finished = signal(dict)
    result = signal(str)

    thread_finished = signal(dict)
    thread_created = signal(dict)
    thread_result = signal(dict)

    progressbar_init = signal(int)
    progressbar_value = signal(int)
    progressbar_reset = signal(int)

    ch01 = signal(int)
    ch02 = signal(str)
    ch03 = signal(dict)
    ch04 = signal(dict)