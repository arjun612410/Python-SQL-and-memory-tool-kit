# Practice 1 : class-based Timer
import time
class Timer:
    def __init__(self):
        self.elapsed = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self
    
    def __exit__(self,exc_type,exc,tb):
        self.end = time.perf_counter()
        self.elapsed = self.end - self.start
        print(f"Elapsed time: {self.elapsed:.4f} seconds")

with Timer() as t:
    time.sleep(1)

print(t.elapsed)

# Practice 2 : @contextmanager Timer
from contextlib import contextmanager

@contextmanager
def Timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        end = time.perf_counter()
        print(f"Elapsed time: {end-start:.4f} seconds")

with Timer():
    time.sleep(1)

# Practice 3 : open_two_files(a, b)
with open("file1.txt", "w") as f:
    f.write("Hello from file 1")

with open("file2.txt", "w") as f:
    f.write("Hello from file 2")

@contextmanager
def open_two_files(a,b):
    with open(a) as f1, open(b) as f2:
        yield f1,f2

# normal test
with open_two_files("file1.txt", "file2.txt") as (f1, f2):
    print(f1.read())
    print(f2.read())

# check that the file is closed or not
with open_two_files("file1.txt", "file2.txt") as (f1, f2):
    print("Inside:")
    print(f1.closed)
    print(f2.closed)

print("Outside:")
print(f1.closed)
print(f2.closed)

# Exception test
try:
    with open_two_files("file1.txt", "file2.txt") as (f1, f2):
        print("Before error:", f1.closed, f2.closed)

        raise ValueError("Boom")

except ValueError as e:
    print("Error:", e)

print("After error:", f1.closed, f2.closed)

# Practice 4 : chdir(path)
import os
from pathlib import Path
@contextmanager
def operation(Path):
    old_path = os.getcwd()
    os.chdir(Path)
    try:
        yield
    finally:
        os.chdir(old_path)

if not Path("test_folder").is_dir():
    os.mkdir("test_folder")
print("Before:", os.getcwd())

with operation("test_folder"):
    print("Inside:", os.getcwd())

print("After:", os.getcwd())

# Practice 5 : Logger context manager
class logger:
    def __enter__(self):
        print("Entering")
    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            print("Exited cleanly")
        else:
            print(f"Type of error: {exc_type} and error: {exc}")
        return False

# clean block test
with logger():
    print("Doing some work")

# Error test
try:
    with logger():
        print("Doing some work")
        raise ValueError("Something went wrong")
except ValueError:
    print("Exception caught")

