# Python Object Memory: `__dict__`, `__slots__`, and Dataclasses

This guide explains the concepts demonstrated in [`memory_compare.py`](./memory_compare.py). The examples are intended to be run with Python 3.

## 1. Instance attributes and `__dict__`

For a regular Python class, attributes assigned to an instance are usually stored in an instance dictionary, available as `instance.__dict__`.

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

s1 = Student("Arjun", 20)
print(s1.__dict__)
# {'name': 'Arjun', 'age': 20}
```

Because the attributes are stored in a dictionary, a regular instance can usually receive new attributes after it is created:

```python
s1.city = "Delhi"
print(s1.__dict__)
# {'name': 'Arjun', 'age': 20, 'city': 'Delhi'}
```

This is convenient when an object's attributes need to be flexible. However, each instance's dictionary has a memory cost.

## 2. Fixed attributes with `__slots__`

If a class needs only a known set of attributes, `__slots__` declares those attributes in advance:

```python
class Student:
    __slots__ = ("name", "age")

    def __init__(self, name, age):
        self.name = name
        self.age = age

s1 = Student("Arjun", 20)
print(s1.name)
# Arjun
```

In the usual case, a slotted instance does not have an instance `__dict__`, and adding an undeclared attribute is not allowed:

```python
# print(s1.__dict__)  # AttributeError
# s1.city = "Delhi"   # AttributeError
```

Slots can reduce per-instance memory, especially when a program creates many instances of a class. They trade away some flexibility: attributes must be declared in `__slots__`.

## 3. Dataclasses

The `@dataclass` decorator generates common methods for a class from its annotated fields. By default, this includes an initializer (`__init__`), a readable representation (`__repr__`), and value-based equality (`__eq__`).

```python
from dataclasses import dataclass

@dataclass
class Student:
    name: str
    age: int
    marks: float

s1 = Student("Arjun", 20, 92.5)
print(s1)
# Student(name='Arjun', age=20, marks=92.5)
```

The annotations describe the fields and help tools understand the code; they do not, by themselves, enforce the values' types at runtime.

### Default field values

A field can have a regular default value. Callers can omit that field when creating an instance:

```python
@dataclass
class Student:
    name: str
    age: int = 18

s1 = Student("Arjun")
print(s1)
# Student(name='Arjun', age=18)
```

### Mutable defaults and `default_factory`

For mutable values such as lists, use `field(default_factory=...)`. The factory creates a fresh value for each instance:

```python
from dataclasses import dataclass, field

@dataclass
class Student:
    name: str
    subjects: list = field(default_factory=list)

s1 = Student("Arjun")
s2 = Student("Rahul")
s1.subjects.append("Python")

print(s1.subjects)  # ['Python']
print(s2.subjects)  # []
```

Each student gets a separate list, so changing one student's subjects does not affect another's.

## 4. Frozen dataclasses and immutability

Set `frozen=True` to prevent normal reassignment of dataclass fields after construction:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Student:
    name: str
    age: int

s1 = Student("Arjun", 20)
# s1.age = 21  # FrozenInstanceError
```

A frozen dataclass is not deeply immutable. If a field refers to a mutable object, that object's contents can still be changed:

```python
@dataclass(frozen=True)
class Data:
    values: list

d = Data([1, 2, 3])
d.values.append(4)  # Allowed: the list is mutated, not reassigned
print(d.values)
# [1, 2, 3, 4]
```

## 5. Dataclasses with `slots=True`

On supported Python versions, `@dataclass(slots=True)` creates a dataclass with slots without requiring a separate `__slots__` declaration:

```python
from dataclasses import dataclass

@dataclass(slots=True)
class Student:
    name: str
    age: int
```

This combines dataclass-generated methods with the fixed-attribute layout of slots. As with a slotted class, instances generally do not have a normal instance `__dict__` and cannot accept undeclared attributes.

`frozen` and `slots` can be combined:

```python
@dataclass(frozen=True, slots=True)
class Point:
    x: int
    y: int
```

This provides fixed fields, disallows normal field reassignment, and uses slots.

## 6. Measuring an object's size with `sys.getsizeof`

`sys.getsizeof(object)` reports the shallow size of an object in bytes:

```python
import sys

values = [1, 2, 3]
print(sys.getsizeof(values))
```

For a list, this measures the list container itself. It does not recursively add the sizes of the objects referenced by the list. The returned size can vary by Python version and platform, so example byte counts are not universal.

## 7. Comparing normal classes, slots, and slotted dataclasses

The script defines three point classes with the same three fields:

```python
class Point1:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Point2:
    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

@dataclass(slots=True)
class Point3:
    x: int
    y: int
    z: int
```

This makes it possible to compare a regular class, a manually slotted class, and a slotted dataclass while keeping their data fields alike.

### How the benchmark works

The `measure` function:

1. Runs garbage collection and creates `n` objects while timing their creation with `time.perf_counter()`.
2. Deletes those objects and runs garbage collection again.
3. Starts `tracemalloc`, records traced memory before and after creating another `n` objects, and calculates the difference.
4. Returns the approximate traced-memory difference in kilobytes and the creation time in seconds.

`gc` is the garbage-collection module, `time.perf_counter()` is a high-resolution timer, and `tracemalloc` tracks memory allocated by Python. These results are useful for an approximate comparison, not a universal guarantee: timings and memory figures depend on the Python version, platform, and runtime conditions.

The script uses 100,000 objects by default. Pass a different count as a command-line argument:

```text
python memory_compare.py 1000
```

The output reports the selected object count, approximate memory in KB, approximate bytes per object, and creation time in seconds. The values shown in the Python file are one sample run; expect your own results to differ.
