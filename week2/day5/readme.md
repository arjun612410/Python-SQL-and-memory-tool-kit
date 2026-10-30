# Python Context Managers

This guide explains Python context managers and the `with` statement. Context managers help manage a resource's lifecycle: they set it up before a block runs and clean it up when the block ends, even if an exception occurs.

## 1. Why context managers are useful

Resources such as files, database connections, and locks should be released after use. A manual `close()` can be skipped if an exception interrupts the code:

```python
file = open("data.txt", "r", encoding="utf-8")
try:
    data = file.read()
finally:
    file.close()
```

The `finally` block ensures that the file is closed. A context manager packages this setup-and-cleanup pattern in a reusable way.

## 2. The `with` statement

Files are a common example of context managers:

```python
with open("data.txt", "r", encoding="utf-8") as file:
    data = file.read()
```

The file is opened before the block runs and closed when the block ends, whether it ends normally or because an exception was raised. You do not need to call `file.close()` yourself.

The general flow is:

1. Enter the context and perform setup.
2. Run the body of the `with` block.
3. Exit the context and perform cleanup.

## 3. Class-based context managers

A class-based context manager implements two special methods:

- `__enter__()` runs when the `with` block is entered. It usually acquires or prepares a resource.
- `__exit__(exc_type, exc_value, traceback)` runs when the block is exited. It usually releases the resource and may handle an exception.

```python
class Demo:
    def __enter__(self):
        print("Entering")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Exiting")


with Demo():
    print("Inside the block")
```

Output:

```text
Entering
Inside the block
Exiting
```

Use the `with` statement to manage this lifecycle rather than calling `__enter__()` or `__exit__()` manually.

## 4. The value after `as`

The value assigned after `as` is whatever `__enter__()` returns. Returning `self` is common when the block needs to use the context-manager object:

```python
class Greeting:
    def __enter__(self):
        return "Hello, Python!"

    def __exit__(self, exc_type, exc_value, traceback):
        pass


with Greeting() as message:
    print(message)  # Hello, Python!
```

## 5. Exceptions and `__exit__()`

Python calls `__exit__()` when the block exits, including when an exception is raised inside it. The method receives:

- `exc_type`: the exception class, or `None` if there was no exception.
- `exc_value`: the exception instance, or `None` if there was no exception.
- `traceback`: traceback information, or `None` if there was no exception.

```python
class ReportErrors:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            print("The block completed successfully")
        else:
            print(f"The block raised: {exc_value}")
        return False


with ReportErrors():
    result = 10 / 0
```

The division raises `ZeroDivisionError`. `__exit__()` gets a chance to perform cleanup or inspect the error, but returning `False` allows the exception to keep propagating.

### Suppressing exceptions

If `__exit__()` returns a truthy value, Python treats an exception from the block as handled and suppresses it. If it returns a falsy value, the exception propagates normally. The return value has no exception to suppress when the block exits successfully.

Do not return `True` unless suppressing the exception is intentional; doing so can hide errors.

## 6. Context managers and `try/finally`

A context manager is a clean, reusable way to express setup and cleanup behavior that might otherwise use `try/finally`:

```python
with open("data.txt", encoding="utf-8") as file:
    data = file.read()
```

This has the same general resource-management purpose as:

```python
file = open("data.txt", encoding="utf-8")
try:
    data = file.read()
finally:
    file.close()
```

The `try/finally` mental model is useful: cleanup runs whether the block completes normally or raises an exception. A class-based context manager can also choose to suppress an exception through its `__exit__()` return value.

## 7. A timer context manager

The `time.perf_counter()` clock is useful for measuring elapsed time:

```python
import time


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.perf_counter() - self.start
        print(f"Time taken: {elapsed:.6f} seconds")


with Timer():
    total = sum(range(1_000_000))
```

`__enter__()` records the start time, and `__exit__()` records and reports the elapsed time. The reporting code also runs if the block raises an exception.

## 8. Decorators versus context managers

A decorator (for example, `@timer` above a function definition) usually wraps a function call. A context manager surrounds a block of statements, which can include several operations:

```python
with Timer():
    total = sum(range(1_000_000))
    print(total)
```

Both can add timing behavior. Choose a decorator when the behavior belongs around a function call, and a context manager when it should surround an arbitrary block or resource lifecycle.

## 9. Generator-based context managers with `@contextmanager`

The `contextlib.contextmanager` decorator lets you write a context manager as a generator function. Code before `yield` is the setup phase; code after it is the cleanup phase:

```python
from contextlib import contextmanager


@contextmanager
def demo_context():
    print("Setup")
    yield
    print("Cleanup")


with demo_context():
    print("Inside the block")
```

Output:

```text
Setup
Inside the block
Cleanup
```

The generator pauses at `yield` while the body of the `with` block runs, then resumes when that block exits.

### Passing a value to `as`

The value yielded by the generator is assigned to the name after `as`:

```python
@contextmanager
def greeting():
    yield "Hello, Python!"


with greeting() as message:
    print(message)  # Hello, Python!
```

This is the generator-based equivalent of returning a value from `__enter__()`.

### Ensuring cleanup on exceptions

Put critical cleanup in a `finally` block so it runs whether the body succeeds or raises an exception:

```python
import time
from contextlib import contextmanager


@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"Time taken: {elapsed:.6f} seconds")
```

For a simple context manager, this generator-based approach is concise. A class-based manager can be clearer when the manager needs to maintain substantial state or expose additional behavior.

## 10. `contextlib.suppress`

`contextlib.suppress` is a context manager for intentionally ignoring specific exceptions. It is similar to an `except` block containing `pass`:

```python
import os
from contextlib import suppress


with suppress(FileNotFoundError):
    os.remove("temporary.txt")
```

This is appropriate if the file may already be absent and that is acceptable. Other exceptions, such as `PermissionError`, are not suppressed here. Suppress only the specific exceptions that are safe to ignore; broadly suppressing `Exception` can hide bugs.

## 11. Common use cases

### Files

```python
with open("data.txt", encoding="utf-8") as file:
    contents = file.read()
```

The file is closed when the block exits.

### Locks

```python
from threading import Lock

lock = Lock()

with lock:
    # Work with shared state while holding the lock.
    update_shared_state()
```

The lock is acquired on entry and released on exit, including if the protected code raises an exception.

### Timers

```python
with Timer():
    perform_work()
```

The block marks the region whose execution time should be measured.

### Database connections or sessions

```python
with database_session() as session:
    session.query(...)
```

A database library may use the context to manage acquiring and releasing a session, and possibly committing or rolling back work. The exact behavior depends on that library.

## 12. Applying the idea to a profiler

A profiler can use a context manager to measure an arbitrary block of code. On entry, it can start a timer and memory measurement; on exit, it can stop the measurements and report the results. This complements a timing decorator, which is naturally suited to measuring a function call.

## 13. Common mistakes to avoid

- **Calling `__enter__()` manually:** use `with manager:` so Python manages the lifecycle.
- **Assuming `__exit__()` only runs on success:** it also runs when the block exits because of an exception.
- **Returning `True` without intending to suppress an exception:** a truthy return handles and suppresses the block's exception.
- **Leaving critical generator-manager cleanup after `yield` without `finally`:** put cleanup that must always run in a `finally` block.

## 14. How this connects to generators and decorators

These Week 2 concepts solve related but distinct problems:

- **Closures and decorators** can add behavior around function calls.
- **Generators** use `yield` to pause and resume execution, often producing values lazily.
- **Context managers** use `__enter__()` / `__exit__()` or a generator with `@contextmanager` to manage setup and cleanup around a block.

In a generator-based context manager, the pause at `yield` gives the `with` block time to run between setup and cleanup.