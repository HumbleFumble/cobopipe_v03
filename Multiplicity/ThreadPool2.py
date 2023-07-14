from multiprocessing import cpu_count

from PySide2.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide2.QtWidgets import QApplication

from Log.CoboLoggers import getLogger

logger = getLogger()


"""QThread offers an event loop and using signals and slots in a QThread is thread-safe.
    This means if you have a process you'd like to run alongside the application. For example continuously checking for updates etc.
    Then it'd be better to use a QThread.
    
    QRunnable is great for a small task that does not require an event loop.
    This means if you have a finite process, you want to run, the QRunnable is a good choice.
    
    QThreadPool is a global instance and controls all threads in the Qt application. 
"""


class PoolSignals(QObject):
    """Creating signals for pool.

    Args:
        QObject (object): Instance of PySide.QtCore.QObject.
    """

    created = Signal(dict)
    error = Signal(object)  # To be defined later...
    finished = Signal(dict)
    result = Signal(dict)


class WorkerSignals(QObject):
    """Creating signals for worker.

    Args:
        QObject (object): Instance of PySide2.QtCore.QObject.
    """

    created = Signal(dict)
    error = Signal(object)  # To be defined later...
    finished = Signal(object)
    result = Signal(dict)


class ThreadPool(QObject):
    """ThreadPool to control QRunnable objects.

    Args:
        QObject (object): PySide2.QtCore.QObject.
    """

    def __init__(self, maxThreadCount=None):
        """Initializing ThreadPool instance.

        Args:
            maxThreadCount (int, optional): Max number of threads pool can use. Defaults to None.
        """
        super(ThreadPool, self).__init__()
        self.signals = PoolSignals()
        self.workers = []
        self.finished = False
        self.output = {}
        self.pool = QThreadPool.globalInstance()
        self.setMaxThreads(maxThreadCount)

    def setMaxThreads(self, maxThreadCount=None, keep=4):
        """Setting maximum amount of threads to use at once.

        * ! Never take up every thread on the machine.
        * ! multiprocessing.cpu_count cannot identify efficiency and performance cores.
        * ! This is not a good method, finding a more intelligent way to control thread count would be best.

        Args:
            maxThreadCount (int, optional): Max number of threads pool can use. Defaults to None.
            keep (int, optional): Number of threads to keep free. Defaults to 4.
        """
        if not maxThreadCount:
            maxThreadCount = int(int(cpu_count()) - keep)
        self.pool.setMaxThreadCount(maxThreadCount)

    def addWorker(self, worker):
        """Adding a worker to pool.

        Args:
            worker (object): Instance of PySide2.QtCore.QRunnable.
        """
        self.workers.append(worker)

    def startWorker(self, worker):
        """Starting a worker.

        Args:
            worker (object): Instance of PySide2.QtCore.QRunnable.

        Raises:
            TypeError: Must be inherited from Worker class.
        """
        if isinstance(worker, Worker):
            worker.signals.result.connect(self.updateOutput)
            worker.signals.finished.connect(self.workerDone)
            self.pool.start(worker)
        else:
            raise TypeError("Worker must be inherited.")

    def workerDone(self, worker):
        """Handling when a worker within the pool finishes.

        Args:
            worker (object): Instance of PySide2.QtCore.QRunnable.
        """
        logger.info("workerDone running in pool ")
        if worker in self.workers:
            self.workers.remove(worker)
        if not self.workers:
            logger.info("All workers are done")
            try:
                self.finished = True
                self.signals.finished.emit(self.output)
            except:
                pass

    def updateOutput(self, result):
        """Collecting results from worker and updating the output dictionary.

        Args:
            result (dict): Result dictionary from worker.
        """
        for worker in result.keys():
            self.output[worker] = result[worker]

    def getResult(self, worker):
        """Get result for specific worker from output dictionary.

        Args:
            worker (object): Instance of PySide2.QtCore.QRunnable.

        Returns:
            any: Return the output of the worker.
        """
        if worker in self.output.keys():
            print(self.output)
            return self.output[worker]

    def run(self):
        """Starting all workers in pool."""
        if self.workers:
            self.output = {}
            for worker in self.workers:
                self.startWorker(worker)
        else:
            print("Cannot run, empty pool")

    def wait(self):
        """Waiting for pool to finish.
        * ! This will freeze the main thread until pool is done.
        """
        self.pool.waitForDone()
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        app.processEvents()

    def clear(self):
        """Clears pool."""
        self.workers = []
        self.finished = False
        self.output = {}
        self.pool.clear()


class Worker(QRunnable):
    """QRunnable based threadpool worker.

    Args:
        QRunnable (object): Instance of PySide2.QtCore.QRunnable.
    """
    def __init__(self, func, *args, **kwargs):
        """Initialize instance of Worker.

        Args:
            func (func): function to run.
        """
        super(Worker, self).__init__()
        self.signals = WorkerSignals()
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

    def run(self):
        """Running worker."""
        result = self.__func(*self.__args, **self.__kwargs)
        try:
            self.signals.result.emit({self: result})
        except:
            pass

        try:
            self.signals.finished.emit(self)
        except:
            pass

    def getFunc(self):
        """Returns name of function assigned to worker.

        Returns:
            str: Name of function.
        """
        return self.__func.__name__


#####################
### TESTING STUFF ###
#####################
def reverseLetters(_string):
    return _string[::-1]


def testRun():
    pool = ThreadPool()

    _list = ["Apple", "Banana", "Citrus"]
    workers = []

    for i in _list:
        worker = Worker(reverseLetters, i)
        pool.addWorker(worker)
        workers.append(worker)

    pool.run()
    pool.wait()

    for i in workers:
        print(pool.output[i])
    print("Finished!")


def finished(result):
    print("DONE")
    print(result)


if __name__ == "__main__":
    import sys

    from PySide2.QtWidgets import QApplication, QWidget

    app = QApplication(sys.argv)
    window = QWidget()
    window.show()

    from Preview import comp

    pool = ThreadPool()

    _list = ["E05_SQ030_SH020"]
    workers = []

    for i in _list:
        worker = Worker(comp.getShotPreview, i)
        pool.addWorker(worker)
        workers.append(worker)

    pool.signals.finished.connect(finished)

    pool.run()

    sys.exit(app.exec_())
