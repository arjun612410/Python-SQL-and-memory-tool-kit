#  iteration protocol + type hints

# 1. Iterable vs Iterator
# Iterable : An object whose elements we can iterate/loop over. For Example
numbers = [10,20,30]

for num in numbers:
    print(num)

# numbers is iterable
# Common iterable : list, tuple, string, dict, set, range

# Iterator : An object that provides the next value, one by one, during iteration. For Example
numbers = [10,20,30]

it = iter(numbers)
print(it)
print(next(it))
print(next(it))
print(next(it))
# it is an iterator

# 2. __iter__ and __next__ : they are the two special dunder (double underscore) methods that define the Iterator Protocol. Together, they allow objects to be looped over in for loops, unpacked, or used in comprehensions.
# For example, Suppose we want to create an iterator that gives numbers from 1 to 3.
class Counter:
    def __init__(self):
        self.current = 1

    def __iter__(self):
        return self

    def __next__(self):
        value = self.current
        self.current += 1
        return value

# But the main problem is that it will never stop so we need StopIteration
# 3. StopIteration
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

# 4. What a for loop really does?
# for example, we normally write
numbers = [10, 20, 30]

for x in numbers:
    print(x)

# but internally python uses iteration protocol
numbers = [10, 20, 30]
iterator = iter(numbers)
while True:
    try:
        x = next(iterator)
        print(x)
    except StopIteration:
        break

# 5. How to use custom object in for loop?
# In our counter class 
counter = Counter()
for num in counter:
    print(num)

# 6. How to identify iterable or iterator?
numbers = [10, 20, 30]
iterator = iter(numbers)
# numbers iterable hai
iter(numbers) # this is possible, but
# next(numbers) # This will give TypeError, whereas
next(iterator)
print(iter(iterator) is iterator) # True

# 7. Basic Type Hints 
# for example,
# name: str = "Arjun"
# age: int = 20
# cgpa: float = 8.5
# is_student: bool = True
def add(a: int, b: int) -> int:
    return a+b
# meaning:
# a       → expected int
# b       → expected int
# -> int  → function expected to return int

# 8. list[int] : A list whose elements are expected to be int.
def total(numbers: list[int]) -> int:
    return sum(numbers)

# marks: list[int] = [90, 80, 95]
# similarly, names: list[str] = ["Arjun", "Rahul", "Aman"]

# 9. dict[str, int]
marks: dict[str, int] = {
    "Arjun": 90,
    "Rahul": 85
}
# dict[
#     str,  ← key type
#     int   ← value type
# ]

# 10. X | None
# Suppose a function sometimes returns a str, and at other times—when nothing is found—it returns None.
def find_user(user_id: int) -> str | None:
    if user_id == 1:
        return "Arjun"

    return None

# str | None means: return value can be str or None

# 11. Callable : suppose a function accepts another function as an argument. For Example,
def execute(func, value):
    return func(value)

# So, this is callable. So, in Modern typing:
from collections.abc import Callable
def execute(
    func: Callable[[str], str],
    value: str
) -> str:

    return func(value)
# Callable[
#     [str],   ← arguments
#     str      ← return type
# ]

# Task 1 : Countdown Iterator Class
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

for n in Countdown(4):
    print(n)

c = Countdown(4)
print(next(c))
print(next(c))
print(list(c))
print(list(c))