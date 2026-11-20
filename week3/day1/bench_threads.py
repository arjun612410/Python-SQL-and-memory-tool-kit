# Practice 1 : I/O benchmark 

import time
import threading

def io_task():
    time.sleep(1)

# Sequential version
start = time.perf_counter()
for _ in range(50):
    io_task()
end = time.perf_counter()
sequential_time = end - start
print(f"Total time taken for I/O tasks: {sequential_time:.2f} seconds")

# Threaded version
start = time.perf_counter()
threads = []
for _ in range(50):
    thread = threading.Thread(target=io_task)
    threads.append(thread)
    thread.start()
for thread in threads:
    thread.join()
end = time.perf_counter()
threaded_time = end - start
print(f"Total time taken for threaded I/O tasks: {threaded_time:.2f} seconds")

speed_up = sequential_time / threaded_time

print(f"Speed-up: {speed_up:.2f}x")

# Exp 1 : 1 thread and 50 tasks
def worker():
    for _ in range(50):
        io_task()

start = time.perf_counter()
threads = [threading.Thread(target=worker)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
end = time.perf_counter()
threaded_time = end - start
print(f"Total time taken for 1 thread with 50 tasks: {threaded_time:.2f} seconds")

speed_up = sequential_time / threaded_time
print(f"Speed-up: {speed_up:.2f}x")

# Exp 2 : 10 threads and 5 tasks
def worker():
    for _ in range(5):
        io_task()

start = time.perf_counter()
threads = []
for _ in range(10):
    thread = threading.Thread(target=worker)
    threads.append(thread)
    thread.start()
for thread in threads:
    thread.join()
end = time.perf_counter()
threaded_time = end - start
print(f"Total time taken for 10 threads with 5 tasks each: {threaded_time:.2f} seconds")

speed_up = sequential_time / threaded_time
print(f"Speed-up: {speed_up:.2f}x")

# Exp 3 : 50 threads and 1 task
def worker():
    io_task()

start = time.perf_counter()
threads = []
for _ in range(50):
    thread = threading.Thread(target=worker)
    threads.append(thread)
    thread.start()
for thread in threads:
    thread.join()
end = time.perf_counter()
threaded_time = end - start
print(f"Total time taken for 50 threads with 1 task each: {threaded_time:.2f} seconds")
speed_up = sequential_time / threaded_time
print(f"Speed-up: {speed_up:.2f}x")


# Practice 2 : CPU benchmark

def cpu_task():
    n = 0
    for _ in range(10000000):
        n += 1

# Sequential version
start = time.perf_counter()
for _ in range(4):
    cpu_task()
end = time.perf_counter()
sequential_time = end - start
print(f"Total time taken for CPU tasks: {sequential_time:.2f} seconds")

# Threaded version
start = time.perf_counter()
threads = []
for _ in range(4):
    thread = threading.Thread(target=cpu_task)
    threads.append(thread)
    thread.start()
for thread in threads:
    thread.join()
end = time.perf_counter()
threaded_time = end - start
print(f"Total time taken for threaded CPU tasks: {threaded_time:.2f} seconds")


# Practice 3 : ThreadPoolExecutor.map

from concurrent.futures import ThreadPoolExecutor

def io_task(x):
    time.sleep(1)

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(io_task, range(20)))

end = time.perf_counter()
print(f"Total time taken for threaded I/O tasks: {end - start:.2f} seconds")