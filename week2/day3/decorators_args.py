# A normal decorator receives a function directly. But sometimes we want to configure the decorator itself. For example:
# @retry(times=3)
# Here, times=3 configures the decorator rather than the decorated function. To support this, we need an additional outer function that receives the decorator's arguments and creates the actual decorator.

# 1. Decorator Factory
# Basically, there are 2 levels in a normal decorator. For example,
def decorator(func):
    def wrapper():
        func()
    return wrapper

# But, a decorator with arguments generally have 3 levels. For example,
def decorator_factory(config): # Level 1 : Factory → receives configuration
    def decorator(func): # Level 2 : Decorator → receives the original function
        def wrapper(*args, **kwargs): # Level 3 : Wrapper → receives the function-call arguments
            return func(*args, **kwargs)
        return wrapper
    return decorator

# This extra outer layer allows us to write configurable decorators such as: @decorator_factory(times=3)

# The three levels exist because information becomes available at three different stages.
# The outer factory receives the decorator configuration, such as times=3. The middle decorator receives the function being decorated, and the inner wrapper receives the arguments supplied when that function is eventually called.
# So each layer has a separate responsibility.

# Now an actual example of decorator with arguments
from functools import wraps
def retry(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    print(f"Attempt {attempt + 1} failed")
            print("All attempts failed")
        return wrapper
    return decorator

@retry(times=3)
def fetch_data():
    print("Fetching...")
    raise ValueError("Network error")

fetch_data()
# Output : 
# Fetching...
# Attempt 1 failed
# Fetching...
# Attempt 2 failed
# Fetching...
# Attempt 3 failed
# All attempts failed

# First, retry(times=3) creates the decorator. The returned decorator receives fetch_data, creates a wrapper around it, and returns that wrapper. The name fetch_data then refers to the wrapped function.

# The wrapper is also a closure. It remembers both the configuration variable times from the outer factory and the original func from the decorator's enclosing scope.
# This is why the wrapper can still use those values later when the decorated function is called.

# Retry decorators are useful for transient failures—failures that may disappear on a later attempt, such as temporary network or service issues.
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
                    if attempt < times - 1:
                        time.sleep(delay)
            raise RuntimeError("All attempts failed")
        return wrapper
    return decorator

# They should not be used blindly for permanent programming errors. Real retry systems usually include a retry limit, delays or backoff, exception filtering, and logging.

# Decorator factories are useful whenever the decorator itself needs configuration.
# Typical examples include retry counts, logging levels, required permissions, rate limits, cache sizes, timeouts, and repetition counts.

# 2. Decorator Stacking
# @timer
# @logger
# def process():
#     print("Processing")

# The question is which decorator will apply first timer or logger
# When decorators are stacked, Python applies them from bottom to top.
# But what will be the output so to identify that let's take an example.

from functools import wraps
def A(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("A before")
        result = func(*args, **kwargs)
        print("A after")
        return result
    return wrapper

def B(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("B before")
        result = func(*args, **kwargs)
        print("B after")
        return result
    return wrapper

@A
@B
def hello():
    print("HELLO")

hello()
# So the output is 
# A before
# B before
# HELLO
# B after
# A after

# Decorators are applied bottom-to-top, but wrapper execution begins from the outermost decorator.
# Decorator order can change program behavior because each decorator wraps the result of the decorator below it.

# For concerns such as authentication, logging, caching, validation, and timing, changing the order can change what gets logged, cached, validated, or measured.

# 3. Simple Class based decorator
# A class-based decorator uses a class instead of the usual nested-function structure.
# The class can store the decorated function as state, and __call__ can define what happens when the decorated callable is invoked.
# For the current scope, understanding the idea is enough; deep implementation is not required.
class Logger:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print(f"Calling {self.func.__name__}")
        return self.func(*args, **kwargs)

@Logger
def add(a, b):
    return a + b

# 4. Caching
# Caching means storing the result of a computation so that if the same request occurs again, the stored result can be reused instead of recomputing it.
# Caching can improve performance when computations are expensive and the same inputs occur repeatedly.

# How to build cache manually?
def cache(func):
    stored = {}
    @wraps(func)
    def wrapper(n):
        if n in stored:
            print("Returning cached result")
            return stored[n]
        print("Calculating result")
        result = func(n)
        stored[n] = result
        return result
    return wrapper

@cache
def square(n):
    return n * n

print(square(5))
print(square(5)) # For this one the result is already stored in the dict {5:25} so without calculating it will give the result.

# A simple cache decorator can use a closure to keep a dictionary alive between function calls.
# The dictionary belongs to the enclosing decorator scope, but the wrapper continues to reference it, so previously computed results remain available.

# manual cache with general arguments
def cache(func):
    stored = {}
    @wraps(func)
    def wrapper(*args):
        if args in stored:
            return stored[args]
        result = func(*args)
        stored[args] = result
        return result
    return wrapper

@cache
def add(a, b):
    print("Calculating...")
    return a + b

# Caching works best for expensive computations where the same inputs occur repeatedly and the output is determined by those inputs.
# It is less appropriate for functions whose result is expected to change between calls, such as functions based on current time or frequently changing external state.

# functools.lru_cache
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate(n):
    print("Calculating...")
    return n * n

print(calculate(9))

# LRU : Least recently used
# An LRU cache keeps recently used results and, when its capacity is reached, removes entries that have not been used recently.
# LRU cache is also a decorator with arguments.

# Caching vs Memoization
# Caching is the broader idea of storing data for faster future access.
# Memoization is a specific form of caching where the results of function calls are stored based on their input arguments.

# Important limitation of cache
# Cached function arguments need to be usable as cache keys. With lru_cache, this generally means they must be hashable.
# Immutable values such as integers, strings, and tuples of hashable values usually work naturally, whereas mutable lists cannot directly be used as cache keys.

# We can also inspect cache
@lru_cache(maxsize=128)
def square(n):
    return n * n

square(5)
square(5)
square(10)

print(square.cache_info()) # CacheInfo(hits=1, misses=2, maxsize=128, currsize=2)

# Practice 1 : @retry(times, delay)

from functools import wraps
def retry(times,delay):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            for attemp in range(times):
                try:
                    result = func(*args,**kwargs)
                    return result
                except Exception:
                    if attemp == times-1:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

count = 0

@retry(times=3, delay=0.5)
def fetch_data():
    global count
    count += 1

    print(f"Function called: attempt {count}")

    if count < 3:
        raise ValueError("Temporary error")

    return "Data fetched successfully!"

print(fetch_data())

# Practice 2 : @cache

def decorator(func):
    stored = {}
    @wraps(func)
    def wrapper(*args,**kwargs):
        if args in stored:
            print("From cache")
            return stored[args]
        result = func(*args)
        print("Computing")
        stored[args] = result
        return result
    return wrapper

@decorator
def cal(a,b):
    return a+b

print(cal(10,20))
print(cal(10,20))

# Practice 3 : Stacking
def tagA(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        print("Entering A")
        result = func(*args,**kwargs)
        print("Exiting A")
        return result
    return wrapper

def tagB(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        print("Entering B")
        result = func(*args,**kwargs)
        print("Exiting B")
        return result
    return wrapper

@tagA
@tagB
def funct():
    print("Hello World")

print(funct())

# Practice 4 : @rate_limit(calls, period)

def rate_limit(calls,period):
    def decorator(func):
        timestamps = []
        @wraps(func)
        def wrapper(*args,**kwargs):
            current_time = time.time()
            timestamps[:] = [
                timestamp
                for timestamp in timestamps
                if timestamp > current_time - period
            ]
            if len(timestamps) < calls:
                timestamps.append(current_time)        
                return func(*args,**kwargs)
            raise Exception("Rate limit exceeded")
        return wrapper
    return decorator

@rate_limit(calls=3, period=2)
def test_function():
    print("Function executed!")
    return "Success"

for i in range(5):
    try:
        print(f"Call {i + 1}:", test_function())
    except Exception as e:
        print(f"Call {i + 1}: {e}")

print("\nWaiting for 2 seconds...")
time.sleep(2)