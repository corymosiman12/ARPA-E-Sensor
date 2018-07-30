from queue import Queue
import threading

print_lock = threading.Lock()

def exampleJob(worker):
    print("I'm working")
    with print_lock:
        print(threading.current_thread().name, worker)

def threader():
    while True:
        worker = q.get()

        exampleJob(worker)
        q.task_done()

q = Queue()

