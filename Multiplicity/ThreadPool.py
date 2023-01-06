
from PySide2 import QtCore


from Multiplicity.Signals import Signals
from time import sleep
from threading import activeCount
from multiprocessing import cpu_count


class ThreadPool(QtCore.QObject):
    """
    This module wraps the QtCore.QThreadPool.globalInstance() and batches threads into it

    routine:
    #Create a pool object
    pool = ThreadPool()

    # To start a batch
    pool.startBatch(threads)

    # If you need to cancel the batch prematurely
    pool.cancelBatch()
    """
    cnt = 0

    def __init__(self, max_threads=None):
        super(ThreadPool, self).__init__()
        self.pool = QtCore.QThreadPool.globalInstance()
        self.mute = QtCore.QMutex()
        self.signals = Signals()
        if not max_threads:
            max_threads = int(int(cpu_count()) - int(activeCount()) - 1)
        self.max_threads = max_threads
        self.worker_len = 0
        self.pool.setMaxThreadCount(max_threads)

    def setMaxThreads(self):
        max_threads = int(int(cpu_count()) - int(activeCount()) - 1)
        # print("CURRENT THREADS AVAILABLE: %s" % max_threads)
        self.pool.setMaxThreadCount(max_threads)

    def getPoolObj(self):
        return self.pool

    def startBatch(self, workers=None, use_max=True,use_amount=None):
        """
        :param use_max:
        :param workers: Takes a list of Worker objects
        """
        # self.__pool.clear()
        if use_max:
            self.setMaxThreads()
        if use_amount:
            self.pool.setMaxThreadCount(use_amount)
        self.cnt = 0
        self.worker_len = len(workers)
        self.signals.progressbar_value.emit(0)
        self.signals.progressbar_init.emit(self.worker_len)

        for worker in workers:
            if isinstance(worker, Worker):
                # Pass signal on from Worker through ThreadPool to outside
                worker.signals.finished.connect(self.workerDone)
                # worker.signals.result.connect(self.signals.thread_result.emit)
                # worker.signals.created.connect(self.signals.ch03.emit)
                self.pool.start(worker)
            else:
                #print("Worker must be inherited from type 'Worker' from ThreadPool module")
                raise TypeError("Worker must be inherited from type 'Worker' from ThreadPool module")

    # def workerResult(self,*args):
    #     self.signals.result.emit(*args)

    def workerDone(self, *args):
        #print(self.cnt, self.worker_len)
        self.mute.lock()
        self.cnt += 1
        #self.signals.thread_result.emit(args)
        self.signals.progressbar_value.emit(self.cnt)
        self.mute.unlock()

        # Reset if all workers are done
        if self.worker_len == self.cnt:
            self.cnt = 0
            self.worker_len = 0
            self.signals.progressbar_value.emit(0) #emit if you want to reset progress bar after finish
            self.signals.ch01.emit(1)

    def cancelBatch(self):
        """
        Removes all non-started threads from the pool
        """
        print("Pool's Cleared")
        self.pool.clear()


class Worker(QtCore.QRunnable):
    cnt = 0
    mute = QtCore.QMutex()

    def __init__(self, func=None, *args,**kwargs):
        super(Worker, self).__init__()
        Worker.mute.lock()
        self.worker_id = Worker.cnt
        Worker.cnt += 1
        self.output = {"id": self.worker_id, "created": Worker.cnt}
        Worker.mute.unlock()
        self.signals = Signals()
        self.func = func
        self.args = args
        self.kwargs= kwargs

    def run(self):
        # Worker.mute.lock()
        # self.signals.created.emit({"created":self.func})
        result = self.func(*self.args,**self.kwargs)
        try:
            self.signals.finished.emit(self.output)
        except:
            pass
        # Worker.mute.unlock()
        # if result:
        #     try:
        #         self.signals.result.emit(result)
        #     except Exception as e:
        #         print(e)
        # self.signals.result.emit({"result":result})
        # self.signals.result.emit()

class Examplethread(QtCore.QRunnable):

    def __init__(self, number):
        super(Examplethread, self).__init__()
        self.__number = number

    def run(self):
        """Emulates the processtime of an acutal operation"""
        print(self.__number, " Working...")
        sleep(3)
        print(self.__number, " Done!")


# TODO Test worker with ThreadPool


if __name__ == "__main__":
    pass
    # threads = []
    # for i in range(50):
    #     threads.append(Examplethread(i))
    #
    # pool = ThreadPool()
    # pool.startBatch(threads)
    # sleep(4)
    # pool.cancelBatch()
    # # sleep(6)
