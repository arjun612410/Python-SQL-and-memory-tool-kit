# Week 3 - Day 1: Python GIL and Threading

This guide covers concurrency, threads, the Global Interpreter Lock (GIL), I/O-bound and CPU-bound tasks, `ThreadPoolExecutor`, and race conditions.

## 1. Concurrency

**Concurrency** is the ability of a program to manage multiple tasks during overlapping periods of time. The tasks do not necessarily run at the exact same instant.

For example, a server may wait for a database response while processing another incoming request.

### Concurrency vs. Parallelism

| Concept | Meaning | Example |
|---|---|---|
| Concurrency | Managing multiple tasks with overlapping execution periods | Switching between waiting network requests |
| Parallelism | Executing multiple tasks at the same instant | Using multiple CPU cores for calculations |

Concurrency can happen on one CPU core because the operating system or runtime switches between tasks. Parallelism requires hardware or runtime support that permits simultaneous execution.

## 2. Processes and Threads

A **process** is a running instance of a program. A process normally has its own memory address space and system resources.

Examples include a running Python script, a web browser, or an editor.

A **thread** is an execution unit inside a process. Threads share the process's memory and resources, while each thread has its own execution state and call stack.

| Process | Thread |
|---|---|
| Independent program execution | Execution unit within a process |
| Separate address space | Shared process address space |
| Relatively expensive to create | Usually cheaper to create |
| Communication can require inter-process mechanisms | Communication can use shared memory |
| Process failure is isolated from other processes | A serious thread failure can affect the whole process |

A browser is one process that may use separate threads for its interface, network operations, and background tasks.

**Interview answer:**

> A process is an independent instance of a running program with its own memory space. A thread is a lightweight unit of execution within a process. Threads in the same process share memory and resources, but maintain their own execution state.

## 3. Creating Threads

Python provides the built-in `threading` module.

A normal sequential example takes approximately four seconds:

```python
import time


def task():
    print("Task started")
    time.sleep(2)
    print("Task completed")


task()
task()
```

The first call finishes before the second call begins.

### 3.1 The `Thread` class

```python
import threading
import time


def task():
    print("Task started")
    time.sleep(2)
    print("Task completed")


thread_1 = threading.Thread(target=task)
thread_2 = threading.Thread(target=task)

thread_1.start()
thread_2.start()

thread_1.join()
thread_2.join()

print("All tasks completed")
```

- `threading.Thread(target=task)` creates a thread object for the `task` function.
- Pass `task`, not `task()`, as the target.
- `start()` begins scheduling and executing the thread.
- `join()` makes the calling thread wait until the target thread finishes.

If the main thread calls `thread.join()`, the main thread does not continue past that point until `thread` is complete.

**Interview answer:**

> `start()` starts the execution of a thread, while `join()` makes the calling thread wait for the thread to finish.

## 4. I/O-Bound Tasks

An **I/O-bound task** spends much of its time waiting for input or output operations.

Examples include:

- Downloading files
- Making API calls
- Reading or writing files
- Waiting for database queries
- Waiting for a server response

```python
import time


def download(file_name):
    print(f"Downloading {file_name}")
    time.sleep(3)
    print(f"Finished {file_name}")


download("a.txt")
download("b.txt")
```

Sequential downloads would take approximately six seconds. Two threads can overlap the waiting periods:

```python
import threading
import time


def download(file_name):
    print(f"Downloading {file_name}")
    time.sleep(3)
    print(f"Finished {file_name}")


first = threading.Thread(target=download, args=("a.txt",))
second = threading.Thread(target=download, args=("b.txt",))

first.start()
second.start()
first.join()
second.join()
```

With two workers, the idealized wait time is closer to three seconds.

Threading is useful for I/O-bound tasks because one thread can wait while another thread performs work or starts another I/O operation.

**Interview answer:**

> An I/O-bound task spends most of its time waiting for external operations, such as network requests, database queries, or file operations. Threading can improve performance by allowing other tasks to run while one task is waiting.

## 5. CPU-Bound Tasks

A **CPU-bound task** spends much of its time performing computations.

Examples include:

- Large mathematical calculations
- Image processing
- Video encoding
- Complex data processing
- Large Python loops

```python
def calculate():
    total = 0
    for number in range(10_000_000):
        total += number
    return total
```

This task continuously uses the CPU. It does not spend most of its time waiting for a network or database.

In standard GIL-enabled CPython, multiple threads generally cannot execute Python bytecode in parallel. Therefore, using four threads around a pure Python CPU-bound loop does not necessarily make it four times faster. Multiprocessing is usually a better choice for CPU-bound Python work.

**Interview answer:**

> A CPU-bound task spends most of its time performing calculations. In standard GIL-enabled CPython, multiple threads cannot generally execute Python bytecode in parallel, so multiprocessing is often more suitable.

## 6. The Global Interpreter Lock (GIL)

The **Global Interpreter Lock (GIL)** is a lock in standard GIL-enabled CPython that allows only one thread to execute Python bytecode at a particular time.

Suppose a computer has four CPU cores and a Python program creates four threads:

```text
Thread 1  -->  Core 1
Thread 2  -->  Core 2
Thread 3  -->  Core 3
Thread 4  -->  Core 4
```

This may look like guaranteed parallel execution, but standard GIL-enabled CPython does not allow multiple threads to execute Python bytecode simultaneously.

The GIL does not prevent threads from existing or from performing I/O. It limits parallel execution of Python bytecode.

### 6.1 Why does CPython have the GIL?

CPython uses reference counting as part of its memory management. Reference counts must remain consistent when object references are added or removed.

The GIL helps protect interpreter internals and CPython object state, including reference count operations, while simplifying thread safety inside the interpreter.

It should not be described as a lock whose only purpose is reference counting. It is part of CPython's interpreter and thread-safety design.

**Interview answer:**

> The GIL was introduced in CPython to protect interpreter internals and simplify thread safety, including operations related to reference counting. It ensures that only one thread executes Python bytecode at a time in a standard GIL-enabled build.

### 6.2 Does the GIL make Python concurrency impossible?

No. Python threads can still provide concurrency.

- Threads are useful for I/O-bound tasks.
- Threads overlap waiting periods.
- Multiprocessing is usually better for CPU-bound Python bytecode.
- Some CPU-heavy C/C++ libraries can release the GIL.

An application that calls a native library optimized for image processing or numerical computation may achieve parallel behavior even when using threads, depending on whether the library releases the GIL.

### 6.3 The GIL and I/O operations

Consider a thread making an API request:

1. The thread starts the API request.
2. The network operation waits for a response.
3. The blocking I/O operation can release the GIL.
4. Another thread can execute Python code.
5. The original thread resumes when the response is ready.

```python
import threading
import urllib.request


def fetch(url):
    with urllib.request.urlopen(url, timeout=10) as response:
        print(len(response.read()))


urls = [
    "https://example.com",
    "https://www.python.org",
]

threads = [threading.Thread(target=fetch, args=(url,)) for url in urls]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
```

This example may depend on network availability.

The GIL is released for many blocking I/O operations, but this behavior also depends on the operation and library implementation. It is incorrect to assume that every external operation releases the GIL.

## 7. ThreadPoolExecutor

Creating each thread manually becomes difficult when there are many tasks.

`ThreadPoolExecutor` is a high-level tool in `concurrent.futures`. It manages a pool of worker threads and distributes submitted tasks among them.

```python
from concurrent.futures import ThreadPoolExecutor
import time


def task(number):
    print(f"Task {number} started")
    time.sleep(2)
    return f"Task {number} completed"


with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(task, range(5))

    for result in results:
        print(result)
```

- `max_workers=3` allows at most three worker threads.
- `executor.map(task, range(5))` schedules `task(0)` through `task(4)`.
- The first three tasks can start concurrently.
- A worker becomes available for the next task after completing a task.
- The `with` block waits for submitted work to finish and shuts down the executor.
- `map()` returns results in input order, even if tasks finish in a different order.

### `submit()` vs. `map()`

`submit()` schedules one task and returns a `Future`:

```python
from concurrent.futures import ThreadPoolExecutor


def square(number):
    return number * number


with ThreadPoolExecutor(max_workers=2) as executor:
    future = executor.submit(square, 10)
    print(future.result())
```

`future.result()` waits for the task to finish and returns its result.

`map()` is convenient when the same function must process multiple inputs:

```python
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(square, [1, 2, 3, 4])
    print(list(results))
```

| Manual Threads | ThreadPoolExecutor |
|---|---|
| Threads are created and managed manually | A worker pool is managed by the executor |
| More management code is needed | Maximum worker count is provided declaratively |
| Useful for small custom demonstrations | Convenient for many similar tasks |

**Interview answer:**

> `ThreadPoolExecutor` provides a high-level interface for reusing worker threads. It reduces manual thread creation and makes it easier to submit, map, and collect multiple tasks.

## 8. Race Conditions

A **race condition** occurs when the final result depends on the unpredictable timing or interleaving of threads that access shared data.

For example, a bank account starts with 1000 units:

- Thread A withdraws 500.
- Thread B withdraws 300.

The expected final balance is:

```text
1000 - 500 - 300 = 200
```

A possible incorrect interleaving is:

1. Thread A reads 1000.
2. Thread B reads 1000.
3. Thread A calculates 500.
4. Thread B calculates 700.
5. Thread A writes 500.
6. Thread B writes 700, overwriting Thread A's value.

This simplified example could produce an incorrect final balance of 700.

The operation:

```python
balance = balance - 500
```

can conceptually involve reading the shared balance, calculating a new value, and writing that value. These steps can be interleaved by threads.

### Does the GIL prevent race conditions?

No. The GIL protects some CPython interpreter operations, but it does not make application-level sequences of operations atomic.

Shared application data can require synchronization mechanisms such as:

- `Lock`
- `RLock`
- A mutex
- A properly synchronized shared state

Detailed locking concepts are covered in later synchronization topics.

**Interview answer:**

> A race condition occurs when multiple threads access shared data and the final result depends on the order of their operations. The GIL does not eliminate application-level race conditions.

## 9. Choosing the Right Approach

Use the nature of the workload to choose a concurrency or parallelism technique:

| Workload | Likely Approach |
|---|---|
| Multiple API calls | Threading or async I/O |
| Database waiting | Threading or async I/O |
| File downloads | Threading or async I/O |
| Heavy pure-Python calculations | Multiprocessing |
| Image processing | Multiprocessing or optimized native libraries |
| Independent background tasks | Threading or async I/O, depending on workload |

Consider the example of processing 100 images:

```text
Download images   -> I/O-bound  -> Threads or async I/O
Resize images     -> CPU-bound  -> Multiprocessing or native optimized code
Save images       -> I/O-bound  -> Threads or async I/O
```

This is a design decision. The same general workload can behave differently depending on the library implementation, hardware, network, and data size.

## Quick Recap

- Concurrency manages overlapping tasks; parallelism executes tasks simultaneously.
- A process is an independent program instance.
- A thread is an execution unit inside a process and shares process memory.
- `start()` starts a thread.
- `join()` waits for a thread to finish.
- I/O-bound tasks spend time waiting and often benefit from threading.
- CPU-bound Python tasks generally do not benefit from threads in standard GIL-enabled CPython.
- The GIL allows only one thread to execute Python bytecode at a time in standard GIL-enabled CPython.
- Blocking I/O operations may release the GIL, but this is library and operation dependent.
- `ThreadPoolExecutor` manages reusable worker threads.
- `submit()` schedules one task and returns a `Future`.
- `map()` schedules one function across multiple inputs and preserves input order.
- The GIL does not prevent application-level race conditions.