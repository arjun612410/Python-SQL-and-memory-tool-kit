# Python Basic Decorators

This guide explains the decorator concepts demonstrated in [`decorators_basic.py`](./decorators_basic.py). A decorator lets you add behavior around a function without changing that function's original source code.

## 1. What is a decorator?

A decorator is a callable that takes a function and returns another callable, often a wrapper that runs extra code before or after the original function.

```python
def my_decorator(func):
    def wrapper():
        print("Before function")
        func()
        print("After function")
    return wrapper

def greet():
    print("Hello")

greet = my_decorator(greet)
greet()
```

Output:

```text
Before function
Hello
After function
```

Here, `my_decorator(greet)` creates the callable assigned back to `greet`. Calling `greet()` runs the wrapper, which calls the original function between the two messages.

## 2. The `@decorator` syntax

Python provides shorter syntax for applying a decorator:

```python
@my_decorator
def greet():
    print("Hello")
```

This is equivalent to:

```python
def greet():
    print("Hello")

greet = my_decorator(greet)
```

The decorator is applied when the function is defined. The name `greet` then refers to the decorated callable.

## 3. Forwarding arguments with `*args` and `**kwargs`

A wrapper that takes no parameters only works for functions that also take no arguments. To make a decorator work with different function signatures, accept `*args` and `**kwargs` in the wrapper and pass them through to the original function:

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result
    return wrapper

@my_decorator
def add(a, b):
    return a + b

print(add(10, 20))  # 30
```

- `*args` collects extra positional arguments into a tuple.
- `**kwargs` collects extra keyword arguments into a dictionary.
- `func(*args, **kwargs)` forwards both kinds of arguments to the decorated function.

The wrapper returns `result` so the decorated function preserves its return value. If the wrapper calls the function but does not return its result, the decorated call returns `None` instead.

## 4. Preserving function metadata with `functools.wraps`

Without extra help, the decorated function's name and docstring can appear to belong to the wrapper:

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet():
    """Greets the user."""
    print("Hello")

print(greet.__name__)  # wrapper
print(greet.__doc__)   # None
```

Use `functools.wraps` to copy the original function's useful metadata onto the wrapper:

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet():
    """Greets the user."""
    print("Hello")

print(greet.__name__)  # greet
print(greet.__doc__)   # Greets the user.
```

`wraps(func)` is itself a decorator factory: it takes the original function and returns a decorator for the wrapper.

## 5. A logging decorator

Logging records events while a program runs. A decorator can log when a function starts and finishes while still returning the function's result:

```python
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO)

def log_function(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info("Calling %s", func.__name__)
        result = func(*args, **kwargs)
        logging.info("Finished %s", func.__name__)
        return result
    return wrapper
```

The function `log_function` is defined as a reusable decorator. To use it, apply `@log_function` above a function definition. The logging calls use Python's `logging` module rather than printing messages directly.

## 6. A timing decorator

`time.perf_counter()` provides a high-resolution timer suitable for measuring elapsed time. Record the start and end around the function call, then report their difference:

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.6f} seconds")
        return result
    return wrapper

@timer
def calculate():
    return sum(range(1_000_000))

total = calculate()
```

The wrapper returns the original result, so `total` receives the value from `calculate()`. The measured time varies between runs and machines.

### Timing even when the function raises an exception

In the simple timer above, the print statement is skipped if the decorated function raises an exception. Put the call in a `try` block and the timing code in `finally` when you want to report elapsed time in both success and error cases:

```python
def wrapper(*args, **kwargs):
    start = time.perf_counter()
    try:
        return func(*args, **kwargs)
    finally:
        end = time.perf_counter()
        print(f"Time: {end - start:.6f} seconds")
```

The `finally` block runs whether the call succeeds or raises an exception. The exception is not swallowed by this example.

## 7. Common uses of decorators

Decorators are useful for cross-cutting behavior that applies to many functions. Examples include:

- Logging
- Timing
- Authentication and authorization
- Validation
- Caching
- Retrying
- Rate limiting
- Tracing and monitoring
- Transactions

They are not limited to printing messages before and after a function; they can consistently apply such behaviors across an application.

## 8. Applying multiple decorators

Decorators can be stacked:

```python
@decorator1
@decorator2
def greet():
    print("Hello")
```

This is equivalent to:

```python
greet = decorator1(decorator2(greet))
```

The decorator closest to the function (`decorator2`) is applied first; `decorator1` wraps its result. When the decorated function is called, the outer wrapper runs before the inner wrapper.

## 9. Decorators with arguments

To configure a decorator, use an outer function that accepts the configuration and returns the actual decorator. In this example, `repeat(n)` creates a decorator that calls the decorated function `n` times:

```python
from functools import wraps

def repeat(n):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet():
    print("Hello")

greet()
```

The stages are:

1. `repeat(3)` returns a decorator configured with `n = 3`.
2. That decorator receives `greet` and returns a wrapper.
3. Calling the wrapper calls the original `greet` three times.

The decorator syntax already applies the decorator. Its manual equivalent is `greet = repeat(3)(greet)`; use one form or the other, not both.

## 10. Practice: timing and logging decorators

### Timing a function

This decorator measures a function call and preserves its return value:

```python
@time_decorator
def addition(a, b):
    return a + b

print(addition(97, 66))  # 163, along with the elapsed time
```

### Logging a function call

This example logs the function name, arguments, and returned value:

```python
@logging_decorator
def log(statement):
    print(f"This is the following statement: {statement}")

log("My name is Arjun Pant.")
```

Because `log` only prints and has no explicit `return` statement, it returns `None`. The decorator logs that return value as `None`. If the decorated function returned a value, the wrapper would log and return that value instead.
