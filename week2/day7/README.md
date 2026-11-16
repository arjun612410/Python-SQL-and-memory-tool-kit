# Python Memory Management: Reference Counting, Garbage Collection, and `tracemalloc`

This guide explains how Python keeps track of objects, reclaims unused memory, and helps developers investigate memory growth. It builds on Day 6's overview of process memory and focuses on Python objects and references.

## 1. Objects and references

When you assign a value to a variable, the variable name refers to an object:

```python
x = [10, 20, 30]
y = x

print(x is y)  # True: both names refer to the same list object
```

The assignment `y = x` does not copy the list. A change through either name is visible through the other:

```python
y.append(40)
print(x)  # [10, 20, 30, 40]
```

Deleting a name removes that reference; it does not necessarily destroy the object:

```python
del x
print(y)  # [10, 20, 30, 40]
```

The list remains available because `y` still refers to it. An object can be reclaimed when it is no longer reachable, according to the memory-management rules of the Python implementation.

## 2. Reference counting

Reference counting tracks how many strong references point to an object. In CPython, which uses reference counting as its primary memory-management mechanism, an object's memory can generally be reclaimed as soon as its reference count reaches zero.

```python
values = [10, 20, 30]  # One name refers to the list
another_name = values  # A second name refers to the same list

del another_name       # Removes one reference
del values             # Removes the last name shown here
```

References may also be held by containers, function arguments, and other objects. The example illustrates the idea; it is not a way to calculate an exact count.

### Observing a reference count with `sys.getrefcount()`

In CPython, `sys.getrefcount()` can help inspect an object's reference count:

```python
import sys

numbers = [1, 2, 3]
print(sys.getrefcount(numbers))
```

The reported value is usually one higher than expected because passing `numbers` to the function creates a temporary reference. The exact value can vary with the execution context and Python implementation. Use this as a debugging aid, not as a measure of memory size.

### Reference count versus memory size

These tools answer different questions:

- `sys.getrefcount(obj)` reports a reference count in CPython.
- `sys.getsizeof(obj)` reports the object's shallow size in bytes.
- `tracemalloc` tracks Python memory allocations and their source locations.

## 3. Reference cycles

Reference counting alone cannot reclaim objects in a cycle if the objects keep references to one another:

```python
a = []
b = []
a.append(b)
b.append(a)
```

The two lists refer to one another. If the external names are deleted, the lists can still have references from inside the cycle:

```python
del a
del b
```

The cycle may now be unreachable from the rest of the program even though the objects refer to each other. A cycle is not automatically a memory leak: Python's cyclic garbage collector can reclaim unreachable cycles.

Cycles can also occur between instances:

```python
class Person:
    def __init__(self, name):
        self.name = name
        self.friend = None


first = Person("A")
second = Person("B")
first.friend = second
second.friend = first
```

## 4. The cyclic garbage collector

CPython combines reference counting with a cyclic garbage collector:

| Mechanism | Main role |
|---|---|
| Reference counting | Reclaims objects when their reference count reaches zero |
| Cyclic garbage collector | Finds unreachable groups of objects that refer to one another |

The `gc` module lets you inspect and interact with the cyclic collector:

```python
import gc

print(gc.isenabled())  # Whether automatic cyclic collection is enabled
collected = gc.collect()
print(f"Collected objects: {collected}")
```

`gc.collect()` requests a collection and returns a count of collected objects. That count is not the number of bytes released. Collection timing and details can depend on the Python version and runtime.

CPython's cyclic collector uses generations. The general idea is that many objects have short lifetimes, so newer objects are checked more often, while objects that survive collections are treated as older. This is an implementation detail; generation behavior can change between Python versions.

The collector does not remove objects that are still reachable. For example, an object stored in a global list remains reachable until it is removed from that list:

```python
cache = []

def keep_data():
    data = [0] * 100_000
    cache.append(data)  # The global list keeps the data reachable
```

## 5. Measuring shallow and deep object size

`sys.getsizeof()` reports the shallow size of an object:

```python
import sys

numbers = [10, 20, 30]
print(sys.getsizeof(numbers))
```

A list stores references to its elements. Its shallow size does not include the complete sizes of all referenced objects. A **deep-size estimate** also accounts for nested or referenced objects. Such an estimate must avoid counting the same shared object multiple times, and its result depends on which kinds of objects it traverses.

For example, `sys.getsizeof()` on a list does not mean “the total memory used by this list and everything it can reach.” Neither a shallow-size measurement nor a deep-size estimate is the same as the process's total RAM usage.

## 6. Tracking allocations with `tracemalloc`

The built-in `tracemalloc` module traces Python memory allocations. It can report current and peak traced memory and help identify source lines associated with allocation changes.

```python
import tracemalloc

tracemalloc.start()
numbers = [i for i in range(100_000)]
current, peak = tracemalloc.get_traced_memory()

print(f"Current traced memory: {current:,} bytes")
print(f"Peak traced memory: {peak:,} bytes")
tracemalloc.stop()
```

- `tracemalloc.start()` starts tracking.
- `get_traced_memory()` returns current and peak traced memory in bytes.
- `tracemalloc.stop()` stops tracking.

These figures describe traced Python allocations, not the process's complete RAM usage. Some memory allocated by native extensions or the operating system may not be represented.

### Comparing snapshots

A snapshot records traced allocations at a point in time. Comparing snapshots can show which lines are associated with allocation growth:

```python
import tracemalloc

tracemalloc.start()
before = tracemalloc.take_snapshot()

numbers = [i for i in range(100_000)]

after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, "lineno")[:5]:
    print(stat)

tracemalloc.stop()
```

Snapshot differences help narrow down where memory changed. An increase does not by itself prove a leak: the program may be intentionally retaining data, such as a cache. Compare snapshots around a repeatable workload and investigate why the objects remain alive.

## 7. Memory leaks and resource leaks

A memory leak is unnecessary retention of memory that the program no longer needs. Python's garbage collector cannot reclaim an object that is still reachable through a reference.

### Common causes

**Growing global collections:** Appending every request to a global list retains all of the request data:

```python
all_requests = []

def handle_request(data):
    all_requests.append(data)
```

Keep only the data the application needs, and remove old entries when they are no longer useful.

**Unbounded caches:** A cache with ever-growing keys can retain objects indefinitely. Use a size limit or an eviction policy where appropriate:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate(number):
    return number * number
```

**Stale registrations or entries:** Dictionaries holding inactive users, sessions, callbacks, or other objects should be cleaned up when those objects are no longer needed.

**Reachable cycles:** A cycle that is still reachable from elsewhere is not garbage. Remove the external reference if the objects are no longer needed.

### Resource leaks

File handles, sockets, and database connections are resources, not just Python objects. Failing to release them is a resource leak. A context manager helps ensure cleanup when a block exits:

```python
with open("data.txt", "r", encoding="utf-8") as file:
    contents = file.read()
```

The file is closed when the `with` block ends, including when an exception interrupts the block.

## 8. A practical memory-growth investigation

When a program's memory usage grows, use a repeatable workload and compare traced allocations around it:

```python
import tracemalloc

tracemalloc.start()
before = tracemalloc.take_snapshot()

for _ in range(1_000):
    handle_request()

after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, "lineno")[:10]:
    print(stat)

tracemalloc.stop()
```

Then:

1. Check whether the workload causes repeatable growth.
2. Inspect the reported source locations and the objects being retained.
3. Look for references in global collections, caches, or registrations.
4. Decide whether the growth is expected or whether entries need an expiry or cleanup policy.
5. Use `gc.collect()` only when investigating cyclic garbage; it will not remove objects that are still reachable.

## 9. Putting the concepts together

```text
An object is created
        |
Names and other objects refer to it
        |
References are added or removed
        |
Reference count reaches zero? ---- Yes ---> CPython can usually reclaim it
        |
        No
        |
Is it part of an unreachable cycle? -------> The cyclic GC may reclaim it

tracemalloc helps investigate where Python allocations occur;
it is a diagnostic tool, not a garbage collector.
```

## Quick recap

- Variables are names that refer to objects; assigning one name to another does not copy the object.
- `del` removes a reference. It does not necessarily destroy the object.
- CPython uses reference counting and a cyclic garbage collector.
- `sys.getrefcount()` is not a memory-size measurement and includes a temporary reference from the call.
- `sys.getsizeof()` reports shallow size, not the size of an entire object graph.
- `tracemalloc` helps compare Python allocations but does not report all process memory.
- Garbage collection cannot reclaim objects that remain reachable, including objects retained by unbounded collections or caches.
- Context managers help release resources such as files reliably.
