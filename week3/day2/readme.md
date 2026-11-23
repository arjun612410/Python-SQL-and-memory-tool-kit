# Week 3 - Day 2: Multiprocessing

This guide explains why multiprocessing is useful, how processes differ from threads, and how to use process pools and inter-process communication in Python.

## 1. Why Multiprocessing Is Needed

During the previous Day 1 CPU benchmark, a pure Python task was executed sequentially and with threads:

```python
def cpu_task():
    total = 0
    for _ in range(10_000_000):
        total += 1
```

A typical result may resemble:

```text
Sequential: 1.30 seconds
Threaded:   1.35 seconds
```

If the computer has four CPU cores, it seems that four tasks should run on four cores simultaneously. This is possible with multiprocessing.

Standard CPython uses the Global Interpreter Lock (GIL), which allows only one thread to execute Python bytecode at a time. A process pool creates separate processes, each with its own Python interpreter and GIL.

### Threading vs. Multiprocessing

Use a restaurant as an analogy:

- **Threading:** Four chefs share one kitchen and shared resources.
- **Multiprocessing:** Four independent kitchens have separate chefs and resources.

| Threading | Multiprocessing |
|---|---|
| Uses multiple threads in one process | Uses multiple independent processes |
| Threads share process memory | Processes have separate memory spaces |
| Shared GIL in standard GIL-enabled CPython | Each process has its own interpreter and GIL |
| Useful for many I/O-bound tasks | Useful for CPU-bound Python tasks |
| Thread creation is generally cheaper | Process creation is generally more expensive |

**Interview answer:**

> Multithreading runs multiple threads within a single process, whereas multiprocessing creates multiple independent processes. Multiprocessing allows CPU-bound Python tasks to execute in parallel across multiple CPU cores.

## 2. What Is a Process?

A **process** is a program that is currently executing.

When Chrome or Visual Studio Code is opened, the operating system creates one or more processes for them.

```python
print("Hello World")
```

Running this Python file creates a Python process that executes the program.

A process contains:

1. A memory space
2. A Python interpreter state
3. Variables and objects
4. Open files and other resources
5. One or more threads

Each process has a separate memory space.

```python
x = 100
```

If a child process is created, it does not automatically share the parent process's ordinary Python object updates. The process creation method may copy or share memory initially, but normal variable updates in one process do not modify another process's object.

**Interview answer:**

> A process is an independent instance of a running program. Each process has its own memory space and execution state.

## 3. The `multiprocessing` Module

Python provides the built-in `multiprocessing` module for creating processes.

```python
import multiprocessing
```

The basic structure resembles threading:

```python
import threading

thread = threading.Thread(target=my_function)
thread.start()
thread.join()
```

```python
import multiprocessing

process = multiprocessing.Process(target=my_function)
process.start()
process.join()
```

The concepts are similar, but a process is a separate execution environment rather than an execution unit inside an existing process.

## 4. `Process`, `start()`, and `join()`

```python
import multiprocessing


def worker():
    print("Child process is running")


if __name__ == "__main__":
    process = multiprocessing.Process(target=worker)
    process.start()
    process.join()
    print("Main process finished")
```

### Step-by-Step Explanation

1. `worker()` is the function that the child process executes.
2. `multiprocessing.Process(target=worker)` creates a process object. It does not execute the process immediately.
3. `process.start()` asks the operating system to start the process and execute `worker()`.
4. `process.join()` makes the main process wait until the child process finishes.

### Why the `if __name__ == "__main__"` Guard Is Needed

Python supports several process start methods, including `spawn`, `fork`, and `forkserver`.

Windows generally uses `spawn`. A spawned child starts a fresh Python interpreter and imports the main module. If process-creation code were not guarded, the child could import the module and try to create processes again.

The guard ensures that process creation runs only in the main program:

```python
if __name__ == "__main__":
    # Create and start processes here
    pass
```

**Interview answer:**

> The main guard prevents child processes from executing process-creation code again when the main module is imported. It is especially important with the spawn start method used on Windows.

## 5. Multiprocessing Pools

Creating and managing a process manually is inconvenient when there are many tasks.

A **process pool** is a fixed group of worker processes that execute submitted tasks. If a worker finishes a task, it can take the next available task.

For example, twenty CPU-intensive tasks can be processed by four worker processes:

```python
import multiprocessing


def square(number):
    return number * number


if __name__ == "__main__":
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(square, [1, 2, 3, 4, 5])

    print(results)
```

Expected output:

```text
[1, 4, 9, 16, 25]
```

### How It Works

- `multiprocessing.Pool(processes=4)` creates four worker processes.
- `pool.map(square, values)` applies `square()` to every value.
- `map()` returns results in input order, even if workers finish tasks in a different order.
- Exiting the `with` block closes and shuts down the pool.

### `Pool.map()` vs. `ThreadPoolExecutor.map()`

| `ThreadPoolExecutor.map()` | `multiprocessing.Pool.map()` |
|---|---|
| Creates threads | Creates separate processes |
| Uses shared process memory | Uses separate process memory |
| Useful for I/O-bound tasks | Useful for CPU-bound tasks |
| Shares the standard process GIL | Each process has its own GIL |

**Interview answer:**

> A process pool manages a fixed number of worker processes and distributes tasks among them. The map method applies a function to each input and collects the results in input order.

## 6. `ProcessPoolExecutor`

`concurrent.futures.ProcessPoolExecutor` provides a modern interface similar to `ThreadPoolExecutor`.

```python
from concurrent.futures import ProcessPoolExecutor


def square(number):
    return number * number


if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(square, [1, 2, 3, 4, 5]))

    print(results)
```

`max_workers=4` allows at most four worker processes.

### Choosing an Executor

```text
ThreadPoolExecutor     -> I/O-bound work
ProcessPoolExecutor    -> CPU-bound Python work
```

Both executors provide `map()` and `submit()`.

`map()` processes multiple inputs and preserves input order:

```python
results = executor.map(square, [1, 2, 3])
```

`submit()` schedules one task and immediately returns a `Future`:

```python
future = executor.submit(square, 5)
print(future.result())  # 25
```

Calling `result()` waits for that task when necessary and returns its result.

**Interview answer:**

> `ProcessPoolExecutor` provides the `Executor` interface for CPU-bound work using separate processes. `map()` handles multiple inputs, while `submit()` schedules individual tasks and returns a `Future`.

## 7. How Multiprocessing Avoids the GIL Limitation

In standard GIL-enabled CPython, threads within one process share the GIL. Therefore, a pure Python CPU loop cannot normally run in parallel across threads.

Multiprocessing creates separate processes. Every process has:

- Its own Python interpreter
- Its own GIL
- Its own memory space

On a four-core machine:

```text
Process 1 -> CPU core 1
Process 2 -> CPU core 2
Process 3 -> CPU core 3
Process 4 -> CPU core 4
```

These processes can execute Python bytecode at the same time. The operating system decides how processes are scheduled across cores. Setting `max_workers=4` does not guarantee that all workers will execute on separate physical cores.

**Interview answer:**

> Multiprocessing avoids the standard CPython thread limitation by using separate Python interpreter processes. Each process has its own GIL, so multiple processes can execute Python bytecode in parallel on multiple CPU cores.

## 8. Process Creation Cost

Creating a process is more expensive than creating a thread. The operating system must:

1. Initialize a new process.
2. Start a Python interpreter, especially with `spawn`.
3. Load required modules and functions.
4. Allocate and manage process resources.
5. Schedule the process.

Consider 100 very small calculations:

- Creating 100 individual processes adds substantial overhead.
- A pool of four workers creates only four processes.
- Workers reuse processes and distribute the process creation cost across all tasks.

Multiprocessing can also be slower if a task is too small. Process creation, task serialization, result transfer, and scheduling may take more time than the calculation itself.

For many small tasks, use a fixed-size process pool rather than creating a process for every task.

**Interview answer:**

> Creating a process has overhead because the operating system must initialize and manage a separate execution environment. For many small tasks, this overhead can exceed the computation time. A process pool reduces this cost by reusing workers.

## 9. Passing Data Between Processes

Processes have separate memory spaces. An ordinary variable passed to a child process is not automatically updated in the parent process.

```python
import multiprocessing


def change_value(value):
    value = 500
    print("Child:", value)


if __name__ == "__main__":
    value = 100
    process = multiprocessing.Process(
        target=change_value,
        args=(value,),
    )
    process.start()
    process.join()
    print("Main:", value)
```

Output:

```text
Child: 500
Main: 100
```

The child receives the argument and modifies only its copy. Arguments transferred across a process boundary may use serialization through `pickle`.

**Interview answer:**

> Processes have separate memory spaces. Changes made to an ordinary variable inside a child process do not automatically affect the parent's variable.

### Inter-Process Communication

Python provides communication mechanisms for processes. Two common mechanisms are `Queue` and `Pipe`.

## 10. `multiprocessing.Queue`

A queue acts like a shared message box:

- Process A places a message using `put()`.
- Process B receives it using `get()`.

```python
import multiprocessing


def worker(queue):
    queue.put("Hello from child process")


if __name__ == "__main__":
    queue = multiprocessing.Queue()
    process = multiprocessing.Process(target=worker, args=(queue,))

    process.start()
    message = queue.get()
    process.join()

    print(message)
```

Output:

```text
Hello from child process
```

A queue is useful when multiple producers or multiple consumers need to exchange messages. It handles the necessary synchronization internally.

## 11. `multiprocessing.Pipe`

A pipe provides a communication channel with two connection endpoints:

- `send()` sends data through one endpoint.
- `recv()` receives data through the other endpoint.

```python
import multiprocessing


def worker(connection):
    connection.send("Hello from child")
    connection.close()


if __name__ == "__main__":
    parent_connection, child_connection = multiprocessing.Pipe()

    process = multiprocessing.Process(
        target=worker,
        args=(child_connection,),
    )
    process.start()

    message = parent_connection.recv()
    process.join()

    print(message)
    parent_connection.close()
```

Output:

```text
Hello from child
```

### Queue vs. Pipe

| Queue | Pipe |
|---|---|
| Behaves like a message queue | Provides a direct two-endpoint connection |
| Useful for multiple producers or consumers | Usually used for communication between two endpoints |
| Uses `put()` and `get()` | Uses `send()` and `recv()` |
| Internally manages synchronization | Transfers data through the connection |

Use a queue when several workers need a shared messaging structure. Use a pipe for direct communication between two processes.

**Interview answer:**

> Inter-process communication allows separate processes to exchange information. Python provides mechanisms such as `multiprocessing.Queue` and `multiprocessing.Pipe`.

## 12. Practical Example: Resizing 10,000 Images

Question: How would you resize 10,000 images quickly in Python?

Image resizing involves decoding, resizing, and encoding operations, so it is generally CPU-intensive. It also involves disk I/O.

A practical design is:

1. Collect image paths.
2. Create a process pool.
3. Distribute image paths among workers.
4. Each worker resizes and saves one image.
5. Collect successful results and errors.

```python
from concurrent.futures import ProcessPoolExecutor


def resize_image(path):
    # Open the image, resize it, and save it.
    # A library such as Pillow or OpenCV would perform the real work.
    return path


if __name__ == "__main__":
    image_paths = ["a.jpg", "b.jpg", "c.jpg"]

    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(resize_image, image_paths))

    print(results)
```

This is a simplified example. A real implementation should handle Pillow or OpenCV operations, output paths, exceptions, memory usage, and worker limits.

**Interview answer:**

> I would use a process pool to distribute CPU-intensive image resizing tasks across multiple processes. Each worker would resize a separate image and save the result. I would limit the number of workers based on available CPU resources and benchmark the performance.

## Quick Recap

- A process is an independent instance of a running program.
- Threads share process memory; processes have separate memory spaces.
- Standard GIL-enabled CPython permits limited parallel execution of Python bytecode with threads.
- Separate processes have separate Python interpreters and GILs, enabling parallel execution across CPU cores.
- Use `ThreadPoolExecutor` for I/O-bound tasks and `ProcessPoolExecutor` for CPU-bound Python tasks.
- `multiprocessing.Pool` manages reusable worker processes.
- `Pool.map()` and `executor.map()` preserve input order in their results.
- `submit()` schedules one task and returns a `Future`.
- A process pool should be used to amortize process creation and scheduling costs.
- Multiprocessing is not always faster for very small tasks or tasks dominated by I/O or data transfer.
- Ordinary variables are not automatically shared between processes.
- Use `Queue` or `Pipe` for inter-process communication.