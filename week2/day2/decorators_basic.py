# Python: basic decorators + functools.wraps

# 1. Decorators 
# A decorator is a callable that takes another function, adds or modifies some behaviour, and returns a callable, usually without changing the original function's source code.

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
# Output:
# Before function
# Hello
# After function

# 2. @decorator syntax
# greet = my_decorator(greet) using the syntax we do not have to write this
@my_decorator
def greet():
    print("Hello")
greet() # this will also gives you the same output

# But there is a problem our decorator do not handle arguments. If we use a function which has arguments then it will give us TypeError. Here, we have another concept
# 3. *args and **kwargs
# These are special syntaxes used in function definitions to allow the function to accept a variable number of arguments.
# *args   → extra positional arguments → tuple
# **kwargs → extra keyword arguments   → dictionary
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

print(add(10, 20))

# Note : do not ignore return result 
# def wrapper(*args, **kwargs):
#     func(*args, **kwargs)

# def add(a, b):
#     return a + b # None
# The correct code is : 
# def wrapper(*args, **kwargs):
#     return func(*args, **kwargs) 

# 4. Decorators damages metadata How???
def my_decorator(func):

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
@my_decorator
def greet():
    """Greets the user."""
    print("Hello")

print(greet.__name__) # We expect that the ouput for this is greet but the actual output is wrapper
print(greet.__doc__) # None

# So, to fix this we use functools.wraps
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

print(greet.__name__) # greet
print(greet.__doc__) # Greets the user.
# The wrapper is the actual executing function, but we want it to externally preserve the identity of the original function.
# wraps(func) actually preserves or copy the useful metadata of the original function.
# One important thing is, functools.wraps is a decorator itself. Specifically, it is a decorator factory (a function that accepts arguments and returns a decorator).

# 5. Logging decorator
# logging : To record the importants events of program execution.
# Basic idea of how a the code looks with a real logging module

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

# 6. Timing decorator
# If we want to find the execution time of the function then we use time.perf_counter()

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
    total = 0
    for i in range(1_000_000):
        total += i

    return total

calculate() # calculate took 0.030134 seconds

# After studying this much about the decorator, we have to know about decorator is not only for printing befor/after
# common use cases of decorators are:
# Logging, Timing, Authentication, Authorization, Validation, Caching, Retry, Rate limiting, Tracing/monitoring, Transactions
# Decorators are especially useful for cross-cutting concerns—behaviour.

# Multiple decorators
# @decorator1
# @decorator2
# def greet():
#     ...

# greet = decorator1(decorator2(greet))

# original greet
#      ↓
#  decorator2
#      ↓
#  decorator1
#      ↓
# final greet

# 7. Decorators with arguments
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
greet = repeat(3)(greet)

# repeat(3)
#    ↓
# returns decorator

# decorator(greet)
#    ↓
# returns wrapper

# wrapper()
#    ↓
# calls greet()

# What about timing/logging if any exception happens???
# To fix this we can use try and finally
# def wrapper(*args, **kwargs):
#     start = time.perf_counter()
#     try:
#         return func(*args, **kwargs)
#     finally:
#         end = time.perf_counter()
#         print(f"Time: {end - start}")

# because finally executes in success and exception both

# Practice 1 : @timer

def time_decorator(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        start = time.perf_counter()
        result = func(*args,**kwargs)
        end = time.perf_counter()
        print(f"Time: {end - start:.6f} seconds")
        return result
    return wrapper

@time_decorator
def addition(a,b):
    return a+b

print(addition(97,66))  # Time: 0.000001 seconds | 163

# Practice 2 : @logger

def logging_decorator(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        print(f"Calling {func.__name__} with args = {args}, kwargs = {kwargs}")
        result = func(*args,**kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

@logging_decorator
def log(statement):
    print(f"This is the following statement: {statement}")

print(log("My name is Arjun Pant."))
# Calling log with args = ('My name is Arjun Pant.',), kwargs = {}
# This is the following statement: My name is Arjun Pant.
# log returned None
# None