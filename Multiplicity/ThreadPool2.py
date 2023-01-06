from PySide2.QtCore import QObject, QThreadPool, QRunnable, Signal
from PySide2.QtWidgets import QApplication
from multiprocessing import cpu_count

from Log.CoboLoggers import getLogger
logger = getLogger()


class PoolSignals(QObject):
    created = Signal(dict)
    error = Signal(object)  # To be defined later...
    finished = Signal(dict)
    result = Signal(dict)


class WorkerSignals(QObject):
    created = Signal(dict)
    error = Signal(object)  # To be defined later...
    finished = Signal(object)
    result = Signal(dict)


class ThreadPool(QObject):
    def __init__(self, maxThreadCount=None):
        super(ThreadPool,self).__init__()
        self.signals = PoolSignals()
        self.workers = []
        self.finished = False
        self.output = {}
        self.pool = QThreadPool.globalInstance()
        self.setMaxThreads(maxThreadCount)


    def setMaxThreads(self, maxThreadCount=None, keep=4):
        if not maxThreadCount:
            maxThreadCount = int(int(cpu_count()) - keep)
        self.pool.setMaxThreadCount(maxThreadCount)


    def addWorker(self, worker):
        self.workers.append(worker)


    def startWorker(self, worker):
        if isinstance(worker, Worker):
            worker.signals.result.connect(self.updateOutput)
            worker.signals.finished.connect(self.workerDone)
            self.pool.start(worker)
            #worker.run()
        else:
            raise TypeError("Worker must be inherited.")


    def workerDone(self, worker):
        logger.info('workerDone running in pool ')
        if worker in self.workers:
            # print("Removing %s from %s" % (worker,self.workers))
            self.workers.remove(worker)
        if not self.workers:
            logger.info('All workers are done')
            # print("No more workers!")
            try:
                self.finished = True
                self.signals.finished.emit(self.output)
            except:
                pass


    def updateOutput(self, result):
        for worker in result.keys():
            self.output[worker] = result[worker]


    def getResult(self, worker):
        if worker in self.output.keys():
            print(self.output)
            return self.output[worker]


    def run(self):
        if self.workers:
            self.output = {}
            for worker in self.workers:
                self.startWorker(worker)
        else:
            print("Cannot run, empty pool")
            # raise ValueError("Cannot run, threadpool is empty.")


    def wait(self):
        self.pool.waitForDone()
        app = QApplication.instance()
        if app is None:
            # if it does not exist then a QApplication is created
            app = QApplication([])
        app.processEvents()


    def clear(self):
        self.workers = []
        self.finished = False
        self.output = {}
        self.pool.clear()


class Worker(QRunnable):
    def __init__(self, func, *args, **kwargs):
        super(Worker, self).__init__()
        self.signals = WorkerSignals()
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

    def run(self):
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
        return self.__func.__name__


def reverseLetters(_string):
    return _string[::-1]

def testRun():
    pool = ThreadPool()

    _list = ['Apple', 'Banana', 'Citrus']
    workers = []

    for i in _list:
        worker = Worker(reverseLetters, i)
        pool.addWorker(worker)
        workers.append(worker)

    pool.run()
    pool.wait()

    for i in workers:
        print(pool.output[i])
    print('Finished!')

def finished(result):
    print('DONE')
    print(result)

if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication, QWidget
    app = QApplication(sys.argv)
    window = QWidget()
    window.show()

    from Preview import comp

    pool = ThreadPool()

    _list = ['E05_SQ030_SH020']
    workers = []

    for i in _list:
        worker = Worker(comp.getShotPreview, i)
        pool.addWorker(worker)
        workers.append(worker)

    pool.signals.finished.connect(finished)

    pool.run()

    sys.exit(app.exec_())



