# Python: __dict__, __slots__, dataclasses

# 1. __dict__ : Normally, when we make an object from a class, then the attributes of the object is stored in a dictionary-like mapping, which is called __dict__
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

s1 = Student("Arjun", 20)
print(s1.__dict__) # {'name': 'Arjun', 'age': 20}

# __dict__ is flexible because we can add more attributes after making an object
s1.city = "Delhi"
print(s1.__dict__) # {'name': 'Arjun', 'age': 20, 'city': 'Delhi'}

# This flexibility is useful, but there is also a memory cost associated with the attribute storage for every regular instance.
# This is where __slots__ come in.
# 2. __slots__ : If we know that a class has a fixed number of attributes, then we use __slots__. The primary use of this is memory/layout optimization.

class Student:
    __slots__ = ("name","age")

    def __init__(self, name, age):
        self.name = name
        self.age = age

s1 = Student("Arjun", 20)
print(s1.name) # Arjun
# print(s1.__dict__) # AttributeError

# How __slots__ saves memory?
# Python can provide fixed storage for predefined attributes instead of per-instance dictionary. This can save memory, especially when creating a large number of objects.

students = [
    Student("Arjun", 20)
    for _ in range(100000)
]
# for 100000 objects, per object saving is meaningful

# __slots__ has one more property: You cannot normally add new attributes at random.
# s1.city = "Delhi" # It will give AttributeError

# 3. dataclasses : when we use dataclasses then python automatically generates useful methods, including __init__, __repr__, or __eq__ by default.
from dataclasses import dataclass

@dataclass
class Student:
    name: str
    age: int
    marks: float

s1 = Student("Arjun", 20, 92.5)
print(s1) # Student(name='Arjun', age=20, marks=92.5)

# default values in dataclass:
# a. Normal default
@dataclass
class Student:
    name: str
    age: int = 18

s1 = Student("Arjun")
print(s1) # Student(name='Arjun', age=18)

# b. field(default_factory=list/set/dict)
from dataclasses import field

@dataclass
class Student:
    name: str
    subjects: list = field(default_factory=list)

s1 = Student("Arjun")
s2 = Student("Rahul")

s1.subjects.append("Python")

print(s1.subjects) # ['Python']
print(s2.subjects) # []

# 4. frozen = True
# If we want to make dataclass objects immutable then we use frozen=True.
@dataclass(frozen=True)
class Student:
    name: str
    age: int

s1 = Student("Arjun", 20)
print(s1.name) # Arjun
# s1.age = 21 # FrozenInstanceError
# this is useful when the value of the object should not be changed after creation.
# frozen=true does not automatically imply deep immutability. Conceptually, if a mutable object exists within a frozen object, the nested object itself can be mutable.

@dataclass(frozen=True)
class Data:
    values: list

d = Data([1, 2, 3])
d.values.append(4)
# This is possible because you are not reassigning d_values to a new list; rather, you are mutating the existing list.

# 5. slots = True : In modern python we directly use slots with dataclass

@dataclass(slots=True)
class Student:
    name: str
    age: int
# In this we do not have to write __slots__ and also gives us the same benefits.

# 6. frozen=True + slots=True : we can also combine both 
@dataclass(frozen=True, slots=True)
class Point:
    x: int
    y: int
# now object has fixed fields, no normal instance __dict__, and fields can't normally be reassigned

# 7. sys.getsizeof()
import sys
a = 10
b = "Arjun"
c = [1,2,3]
print(sys.getsizeof(a)) # 28
print(sys.getsizeof(b)) # 46
print(sys.getsizeof(c)) # 88

# Limitation of sys.getsizeof(): if we write sys.getsizeof(c), This generally indicates the shallow size of the list container. It does not recursively add the size of each referenced object.

# normal vs slots vs dataclass

class Point1:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Point2:
    __slots__ = ("x","y","z")

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

@dataclass(slots=True)
class Point3:
    x: int
    y: int
    z: int

import tracemalloc
import time
import gc

def measure(cls, n):
    gc.collect()
    start = time.perf_counter()
    objs = [cls(1,2,3) for _ in range(n)]
    elapsed = time.perf_counter() - start
    del objs
    gc.collect()

    tracemalloc.start()
    before,_ = tracemalloc.get_traced_memory()
    objs = [cls(1,2,3) for _ in range(n)]
    after,_ = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    del objs

    return (after-before)/1024, elapsed

def main():
    n = int(sys.argv[1]) if len(sys.argv)>1 else 100_000
    styles = [
        ("Normal Class", Point1),
        ("__slots__ class", Point2),
        ("dataclass(slots=True)", Point3)
    ]
    print(f"N = {n}")
    print(f"{'Class style':<25}{'Memmory (KB)':>14}{'Bytes/obj':>12}{'Time (s)':>12}")
    print("-"*63)
    for name, cls in styles:
        kb, secs = measure(cls, n)
        print(f"{name:<25}{kb:>14.1f}{kb*1024/n:>12.1f}{secs:>12.4f}")


if __name__=="__main__":
    main()

# Output 
# N = 1000
# Class style                Memmory (KB)   Bytes/obj    Time (s)
# ---------------------------------------------------------------
# Normal Class                      102.5       105.0      0.0001
# __slots__ class                    63.5        65.0      0.0002
# dataclass(slots=True)              63.5        65.0      0.0001