# Python Dunder Methods

`dunder_demo.py` teaches custom Python objects to work with built-in operations.
**Dunder** means **double underscore**: method names such as `__name__` have
double underscores at the beginning and end.

Python calls these methods automatically during operations such as `len(obj)`,
`str(obj)`, and `obj1 + obj2`. This lets you define the behavior of objects
from your own classes.

## 1. `__init__` — initializing an object

After an object is created, `__init__` sets its attributes. `self` refers to
that new object.

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age


student = Student("Arjun", 20)
print(student.name)  # Arjun
print(student.age)   # 20
```

When you write `Student("Arjun", 20)`, Python creates an object and passes the
arguments to its `__init__` method. Usually, `__init__` does not return a value;
its job is to initialize the object.

## 2. `__str__` — user-friendly text

`__str__` defines what readable text the object provides for `str(obj)` or
`print(obj)`. If this method is not defined, printing typically shows the
default representation, which includes the class and the object's identity.

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.name} is {self.age} years old."


print(Student("Arjun", 20))
# Arjun is 20 years old.
```

`__str__` should return a **string**.

## 3. `__repr__` — developer-friendly representation

`__repr__` provides an informative representation of an object for debugging
and the interactive console. `repr(obj)` calls it explicitly.

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"Student(name={self.name!r}, age={self.age!r})"


student = Student("Arjun", 20)
print(repr(student))
# Student(name='Arjun', age=20)
```

`!r` uses the value's `repr()` in an f-string. If `__str__` is not defined,
`str(obj)` usually falls back to `__repr__`.

## 4. `__eq__` — the behavior of `==`

`__eq__` determines when two custom objects are considered equal using `==`.
If it is not defined, two distinct objects are generally not equal, even if
their attributes are the same.

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.name == other.name and self.age == other.age


print(Student("Arjun", 20) == Student("Arjun", 20))  # True
```

Here, equality is based on `name` and `age`. `NotImplemented` lets Python try
the other operand's comparison method or use its normal fallback behavior
when comparing with an object of another type.

## 5. `__hash__` — sets and dictionary keys

`__hash__` returns an integer hash value. Hash-based collections, such as
`set` and `dict` keys, use it. If two objects are equal according to
`__eq__`, they must also have the same hash.

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return self.name == other.name and self.age == other.age

    def __hash__(self):
        return hash((self.name, self.age))


first = Student("Arjun", 20)
second = Student("Arjun", 20)
print(first == second)                 # True
print(hash(first) == hash(second))     # True
print(len({first, second}))            # 1
```

Hash values can change between program runs, so you should not expect a
specific hash number as output. It is also unsafe to change attributes used
for equality or hashing after a hashable object has been added to a set or
used as a dictionary key. For mutable objects, you generally should not
define `__hash__`.

## 6. `__len__` — the behavior of `len(obj)`

`__len__` determines the length returned by `len(obj)`. It should return a
non-negative integer.

```python
class Playlist:
    def __init__(self, songs):
        self.songs = songs

    def __len__(self):
        return len(self.songs)


playlist = Playlist(["Song1", "Song2", "Song3"])
print(len(playlist))  # 3
```

## 7. `__bool__` — determining whether an object is true or false

`__bool__` defines whether an object is considered true or false by
`bool(obj)` and `if obj:`. This method should return `True` or `False`.

```python
class BankAccount:
    def __init__(self, balance):
        self.balance = balance

    def __bool__(self):
        return self.balance > 0


account = BankAccount(500)
if account:
    print("Account has money")
else:
    print("Account is empty")
# Account has money
```

## 8. `__getitem__` — getting an item by index

`__getitem__` defines the behavior of `obj[index]`. In this example, the class
delegates indexing to its internal `songs` list.

```python
class Playlist:
    def __init__(self, songs):
        self.songs = songs

    def __getitem__(self, index):
        return self.songs[index]


playlist = Playlist(["Believer", "Faded", "Perfect"])
print(playlist[0])  # Believer
print(playlist[1])  # Faded
```

If the index is invalid, an `IndexError` may be raised, just as it would be
for the underlying list.

## 9. `__contains__` — the `in` operator

`__contains__` defines the result of `item in obj`.

```python
class Playlist:
    def __init__(self, songs):
        self.songs = songs

    def __contains__(self, song):
        return song in self.songs


playlist = Playlist(["Believer", "Faded", "Perfect"])
print("Faded" in playlist)       # True
print("Shape of you" in playlist)  # False
```

This method should return a boolean. If `__contains__` is not defined, Python
can check membership by iterating over some iterables.

## 10. `__add__` — the `+` operator

`__add__` defines how `obj1 + obj2` works. This example adds the `x` and `y`
coordinates of two points to create a new point.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return Point(self.x + other.x, self.y + other.y)

    def __str__(self):
        return f"({self.x}, {self.y})"


first = Point(1, 2)
second = Point(5, 5)
print(first + second)  # (6, 7)
```

`__add__` returns a new `Point` object; `__str__` converts it into `(x, y)`
text that can be printed.

## `Money` example: `__repr__`, `__eq__`, and `__hash__`

The `Money` example in the file combines three methods in one class. Here, two
money records are equal when their name, withdrawal, and deposit are all the
same.

```python
class Money:
    def __init__(self, name, withdraw, deposit):
        self.name = name
        self.withdraw = withdraw
        self.deposit = deposit

    def __repr__(self):
        return (
            f"Money(name={self.name!r}, withdraw={self.withdraw!r}, "
            f"deposit={self.deposit!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return (
            self.name == other.name
            and self.withdraw == other.withdraw
            and self.deposit == other.deposit
        )

    def __hash__(self):
        return hash((self.name, self.withdraw, self.deposit))


first = Money("Arjun", 500, 1000)
second = Money("Arjun", 500, 1000)
print(first == second)  # True
print(repr(first))      # Money(name='Arjun', withdraw=500, deposit=1000)
print(len({first, second}))  # 1
```

The same fields are used in `__eq__` and `__hash__`, so equal `Money` objects
become a single entry in a set. In this example, avoid changing the fields
after object creation while the object is being used in a set or as a
dictionary key.

## `Playlist` example: length, indexing, and iteration

The final example in the file uses `__len__`, `__getitem__`, and `__iter__`
together. `__iter__` iterates directly over the songs.

```python
class Playlist:
    def __init__(self, songs):
        self.songs = songs

    def __len__(self):
        return len(self.songs)

    def __getitem__(self, index):
        return self.songs[index]

    def __iter__(self):
        return iter(self.songs)


playlist = Playlist(["Believer", "Faded", "Perfect"])
print(len(playlist))  # 3
print(playlist[0])    # Believer

for song in playlist:
    print(song)
```

`__iter__` returns an iterator; the `for` loop gets each song from it one at
a time. In this class, `__getitem__` provides indexing and `__len__` provides
the playlist's length.

## Running the file

From the `week1/day2` folder:

```bash
python dunder_demo.py
```
