# Python Decorators with Arguments

This guide explains the decorator concepts demonstrated in [`decorators_args.py`](./decorators_args.py). The examples are small, self-contained illustrations; they are not all intended to be combined into one script.

## 1. Decorators and decorator factories

A decorator receives a function and returns a replacement callable. A basic decorator often has two levels: the decorator itself and its wrapper.

```python
def announce(func):
    def wrapper():
        print("Starting")
        result = func()
        print("Finished")
        return result
    return wrapper

@announce
def greet():
    print("Hello!")

greet()
```

The `@announce` syntax is shorthand for `greet = announce(greet)`.

Sometimes a decorator needs its own configuration, such as a retry count:

```python
def repeat_call(times):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat_call(times=3)
def say_hi(name):
    print(f"Hi, {name}!")

say_hi("Sam")
```

This form has three levels, each used at a different time:

1. **Factory** (`repeat_call`) receives decorator configuration, such as `times=3`.
2. **Decorator** (`decorator`) receives the function being decorated.
3. **Wrapper** (`wrapper`) receives the decorated function's call arguments.

The wrapper accepts `*args` and `**kwargs` so it can forward positional and keyword arguments to the original function.

### Closures and preserving function metadata

A wrapper is often a **closure**: it can continue to access variables from the surrounding factory and decorator calls, such as `times` and `func`, even after those outer calls have returned.

Use `functools.wraps` on a wrapper to preserve useful metadata from the original function, including its name and docstring:

```python
from functools import wraps

def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

## 2. Retry decorators

A retry decorator calls a function again when it raises an exception. It is useful for failures that may be temporary, such as a transient network problem. A delay can prevent immediate repeated attempts:

```python
import time
from functools import wraps

def retry(times, delay):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == times - 1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(times=3, delay=0.5)
def fetch_data():
    print("Fetching data")
    return "Data"

print(fetch_data())
```

In the practice example in `decorators_args.py`, the final failure is re-raised, so callers can handle it. Another earlier example prints a failure message and, after exhausting its attempts, returns `None`; a later version raises `RuntimeError` instead. These are different failure policies. In general, retries should be bounded and should target exceptions that may actually be temporary; retrying every exception can hide or repeatedly trigger a permanent programming error.

## 3. Stacking decorators

Decorators are applied from the bottom upward. For example:

```python
@A
@B
def hello():
    print("Hello")
```

is equivalent to:

```python
hello = A(B(hello))
```

When `hello()` runs, the outer wrapper (`A`) starts first, then calls the wrapper from `B`, then the original function. After the original function returns, the wrappers finish in reverse order. Thus, if each wrapper prints a message before and after the call, the order is:

```text
A before
B before
Hello
B after
A after
```

Decorator order matters: for example, changing the order of logging, authentication, caching, or timing decorators can change which calls they observe or affect.

## 4. Class-based decorators

A class can act as a decorator by storing the original function and implementing `__call__`. The instance is then callable:

```python
class Logger:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print(f"Calling {self.func.__name__}")
        return self.func(*args, **kwargs)

@Logger
def add(a, b):
    return a + b

print(add(2, 3))  # 5
```

Here, `@Logger` creates a `Logger` instance around `add`; calling `add(2, 3)` invokes that instance's `__call__` method.

## 5. Caching and memoization

**Caching** means keeping data or results so they can be reused. **Memoization** is a specific kind of caching: it stores function results keyed by the function's input arguments.

A simple one-argument cache can use a dictionary captured by a closure:

```python
from functools import wraps

def cache_one_argument(func):
    stored = {}

    @wraps(func)
    def wrapper(value):
        if value in stored:
            print("Returning cached result")
            return stored[value]
        result = func(value)
        stored[value] = result
        return result

    return wrapper

@cache_one_argument
def square(n):
    print("Calculating")
    return n * n

print(square(5))  # Calculates and returns 25
print(square(5))  # Reuses and returns 25
```

For multiple positional arguments, the tuple `args` can serve as the key:

```python
def cache_positional_arguments(func):
    stored = {}

    @wraps(func)
    def wrapper(*args):
        if args not in stored:
            stored[args] = func(*args)
        return stored[args]

    return wrapper
```

This version only forwards and keys on positional arguments; it does not support keyword arguments. A general-purpose cache must account for both `args` and `kwargs` when building its key. In either case, dictionary keys must be hashable. Integers and strings are hashable; mutable values such as lists cannot be used directly as keys. A custom cache also needs a policy for how long entries remain valid and how much memory it may use.

Caching is most useful when repeated calls with the same inputs can safely reuse the same result. It may be inappropriate when a function depends on changing external state, such as the current time, or has side effects that must happen on every call.

## 6. `functools.lru_cache`

Python provides `functools.lru_cache` for memoization with a bounded cache:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate(n):
    print("Calculating")
    return n * n

calculate(9)  # Computes the result
calculate(9)  # Reuses the cached result
print(calculate.cache_info())
```

`maxsize=128` limits the cache to 128 entries. **LRU** means *least recently used*: when the cache is full and a new result must be stored, an entry that has been unused for the longest time is evicted. `cache_info()` reports cache statistics such as hits, misses, maximum size, and current size.

Arguments used by `lru_cache` must be hashable, because the cache identifies calls by their arguments. Immutable values such as integers, strings, and tuples of hashable values are commonly suitable.

## 7. Rate limiting with a sliding time window

A rate limiter restricts how many times a function can run during a time period. The example in `decorators_args.py` keeps recent call timestamps in a closure:

```python
import time
from functools import wraps

def rate_limit(calls, period):
    def decorator(func):
        timestamps = []

        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            timestamps[:] = [
                timestamp
                for timestamp in timestamps
                if timestamp > current_time - period
            ]
            if len(timestamps) >= calls:
                raise Exception("Rate limit exceeded")
            timestamps.append(current_time)
            return func(*args, **kwargs)

        return wrapper
    return decorator

@rate_limit(calls=3, period=2)
def send_request():
    print("Request sent")

send_request()
```

With `calls=3` and `period=2`, the wrapper removes timestamps outside the two-second window, then allows a call only if fewer than three timestamps remain. When the limit is reached, it raises an exception. The timestamp list belongs to that decorated function's wrapper, so calls to that function share the same limit.

The example uses a general `Exception` for the limit error to keep the code simple; production code should generally define or use a specific exception type. A production rate limiter may also need thread-safe state or shared storage if calls can come from multiple workers or machines.
