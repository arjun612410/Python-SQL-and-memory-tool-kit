# Python Iterators and Type Hints

This guide explains the topics demonstrated in [`iterators_demo.py`](./iterators_demo.py). The examples use Python 3.10 or later because they include built-in generic types such as `list[int]` and the union syntax `str | None`.

## 1. Iterable vs. iterator

An **iterable** is an object whose values can be visited one at a time. Lists, tuples, strings, dictionaries, sets, and `range` objects are common iterables. For example, a list can be used directly in a `for` loop:

```python
numbers = [10, 20, 30]

for number in numbers:
    print(number)
```

An **iterator** is an object that produces the next value when asked. Use `iter()` to get an iterator from an iterable, and `next()` to request values:

```python
numbers = [10, 20, 30]
iterator = iter(numbers)

print(next(iterator))  # 10
print(next(iterator))  # 20
print(next(iterator))  # 30
```

After all values have been returned, another `next(iterator)` raises `StopIteration` to signal that the iterator is exhausted.

## 2. The `__iter__` and `__next__` methods

These two special methods make up the core of Python's iterator protocol:

- `__iter__()` returns an iterator.
- `__next__()` returns the next value, or raises `StopIteration` when there are no more values.

Here is a simple iterator that produces the numbers 1 through 3:

```python
class Counter:
    def __init__(self):
        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.current > 3:
            raise StopIteration

        value = self.current
        self.current += 1
        return value
```

This object is both an iterable and an iterator: `iter(counter)` returns the counter itself, and each call to `next(counter)` advances its state.

## 3. `StopIteration`

An iterator must indicate when it has no more values. It does this by raising `StopIteration` from `__next__()`. Without this signal, a custom iterator such as the first `Counter` version in the script would keep producing values indefinitely.

For the `Counter` above, the sequence is:

```python
counter = Counter()
print(next(counter))  # 1
print(next(counter))  # 2
print(next(counter))  # 3
print(next(counter))  # raises StopIteration
```

Normally, a `for` loop handles `StopIteration` for you, so it ends cleanly when the iterator is exhausted.

## 4. What a `for` loop does internally

A `for` loop gets an iterator from the iterable, repeatedly requests the next value, and stops when `StopIteration` is raised. This is conceptually similar to:

```python
numbers = [10, 20, 30]
iterator = iter(numbers)

while True:
    try:
        number = next(iterator)
    except StopIteration:
        break
    print(number)
```

You generally write the simpler `for` loop; understanding this process explains how it works with both built-in and custom iterators.

## 5. Using a custom iterator in a `for` loop

Because `Counter` implements the iterator protocol, it can be used directly in a loop:

```python
for number in Counter():
    print(number)

# 1
# 2
# 3
```

The loop calls `iter()` and `next()` for you and finishes when `Counter.__next__()` raises `StopIteration`.

## 6. Identifying an iterable or iterator

Calling `iter(value)` is a practical way to check whether an object is iterable. An iterator also works with `next()`:

```python
numbers = [10, 20, 30]
iterator = iter(numbers)

print(next(iterator))                  # 10
print(iter(iterator) is iterator)      # True
```

The list is iterable, but it is not itself an iterator, so `next(numbers)` raises `TypeError`. The iterator returned by `iter(numbers)` can provide values one at a time.

## 7. Basic type hints

Type hints document the types expected for variables, function parameters, and return values:

```python
name: str = "Arjun"
age: int = 20
cgpa: float = 8.5
is_student: bool = True

def add(a: int, b: int) -> int:
    return a + b
```

In `add`, `a` and `b` are expected to be integers, and `-> int` indicates that the function is expected to return an integer. Type hints help readers and static-analysis tools; Python does not automatically enforce them at runtime.

## 8. `list[int]`

`list[int]` describes a list whose elements are expected to be integers:

```python
def total(numbers: list[int]) -> int:
    return sum(numbers)

marks: list[int] = [90, 80, 95]
print(total(marks))  # 265
```

Similarly, `list[str]` describes a list of strings, such as `names: list[str] = ["Arjun", "Rahul"]`.

## 9. `dict[str, int]`

For a dictionary, the first type inside the brackets describes the key and the second describes the value. Therefore, `dict[str, int]` means string keys and integer values:

```python
marks: dict[str, int] = {
    "Arjun": 90,
    "Rahul": 85,
}
```

## 10. `str | None`

The union type `str | None` means a value can be either a string or `None`. It is useful when a function may not find or produce a value:

```python
def find_user(user_id: int) -> str | None:
    if user_id == 1:
        return "Arjun"
    return None

print(find_user(1))  # Arjun
print(find_user(2))  # None
```

## 11. `Callable`

`Callable` describes a function or other callable object. In `Callable[[str], str]`, the inner list describes the argument types and the final `str` describes the return type:

```python
from collections.abc import Callable

def execute(func: Callable[[str], str], value: str) -> str:
    return func(value)

def make_uppercase(text: str) -> str:
    return text.upper()

print(execute(make_uppercase, "hello"))  # HELLO
```

Here, `execute` accepts a function that takes a string and returns a string.

## 12. Countdown iterator

The script's `Countdown` class produces decreasing positive integers, beginning at the provided start value:

```python
class Countdown:
    def __init__(self, start):
        self.start = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.start < 1:
            raise StopIteration

        value = self.start
        self.start -= 1
        return value
```

It can be used in a `for` loop:

```python
for number in Countdown(4):
    print(number)

# 4
# 3
# 2
# 1
```

It can also be consumed manually with `next()`. An iterator keeps its progress, so calling `list()` consumes whatever values remain:

```python
countdown = Countdown(4)

print(next(countdown))  # 4
print(next(countdown))  # 3
print(list(countdown))  # [2, 1]
print(list(countdown))  # []
```

The second `list()` is empty because the same iterator was already exhausted. Create a new `Countdown(4)` when you need to start over.
