import os
import time
import threading
from multiprocessing import Pool
import multiprocessing

print(os.cpu_count()) # 16 

def cpu_task(n):
    total = 0
    for _ in range(n):
        total += 1
    return total

if __name__ == "__main__":
    # sequential 
    start = time.perf_counter()
    for i in range(4):
        cpu_task(10000000)
    end = time.perf_counter()
    sequential_time = end - start
    print(f"Sequential time: {sequential_time:.2f} seconds")

    # multithreading
    start = time.perf_counter()
    threads = []
    for i in range(4):
        thread = threading.Thread(target=cpu_task, args=(10000000,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    end = time.perf_counter()
    multithreading_time = end - start
    print(f"Multithreading time: {multithreading_time:.2f} seconds")

    # multiprocessing
    start = time.perf_counter()
    with Pool(4) as p:
        p.map(cpu_task, [10000000] * 4)
    end = time.perf_counter()
    multiprocessing_time = end - start
    print(f"Multiprocessing time: {multiprocessing_time:.2f} seconds")

    # when using multiprocessing, the time taken is significantly less than multithreading and sequential execution because each process runs in its own Python interpreter and can take advantage of multiple CPU cores. But this happens only when the input is very large. For small inputs, the overhead of creating new processes can outweigh the benefits of parallel execution.
