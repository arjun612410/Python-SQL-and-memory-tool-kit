# Python Generators

This guide explains the generator concepts demonstrated in [`generators_demo.py`](./generators_demo.py). A generator produces values one at a time, which is useful when processing large amounts of data or when values should be computed only as they are needed.

## 1. Why use generators?

A function that returns a list creates all of its values before the caller can use them:

```python
def get_numbers():
    return list(range(10_000_000))

numbers = get_numbers()
```

That list keeps millions of integers in memory at once. If a program only needs to process each value in order, it can instead produce values as requested. Generators do this lazily, without first building the entire result collection.

## 2. `return` and `yield`

`return` sends a result to the caller and ends the function. `yield` sends a value and suspends the function, preserving its state so it can continue later.

```python
def numbers():
    yield 10
    yield 20
    yield 30

gen = numbers()
print(next(gen))  # 10
print(next(gen))  # 20
print(next(gen))  # 30
```

After the final value, another call to `next(gen)` raises `StopIteration`, which signals that the generator is exhausted. A `for` loop handles this end-of-iteration signal automatically.

## 3. How a generator remembers its state

When a generator pauses at `yield`, its local variables and its position in the function are preserved. The next request resumes execution immediately after that `yield`:

```python
def counter():
    count = 1
    yield count
    count += 1
    yield count
    count += 1
    yield count

gen = counter()
print(next(gen))  # 1
print(next(gen))  # 2
print(next(gen))  # 3
```

The local variable `count` is not reset between calls to `next()`.

## 4. Generators are iterators

A generator is an iterator: it produces values one at a time and supports `next()`. It can also be used in a `for` loop:

```python
def count_to_three():
    yield 1
    yield 2
    yield 3

for value in count_to_three():
    print(value)
```

An iterable is something that can provide an iterator. A list is iterable, but the list itself is not an iterator:

```python
values = [1, 2, 3]
iterator = iter(values)
print(next(iterator))  # 1
```

## 5. Generator functions

A generator function is a function that contains `yield`. Calling it creates a generator; its body runs as values are requested:

```python
def squares(n):
    for i in range(n):
        yield i * i

for value in squares(5):
    print(value)  # 0, 1, 4, 9, 16
```

## 6. Generator expressions

A generator expression has a concise syntax similar to a list comprehension. List comprehensions use square brackets and build a list; generator expressions use parentheses and produce values lazily:

```python
list_of_squares = [x * x for x in range(5)]
square_generator = (x * x for x in range(5))

print(list_of_squares)           # [0, 1, 4, 9, 16]
print(list(square_generator))    # [0, 1, 4, 9, 16]
```

The generator expression is not a list, and its values are consumed as they are requested.

## 7. Lazy evaluation

Lazy evaluation means a value is computed only when it is requested. Creating a generator does not immediately run through all its `yield` statements:

```python
def numbers():
    print("Generating 1")
    yield 1
    print("Generating 2")
    yield 2

gen = numbers()
print(next(gen))  # Prints "Generating 1", then 1
print(next(gen))  # Prints "Generating 2", then 2
```

This is similar to streaming a video: the entire movie does not need to be loaded into memory before playback. The consumer requests a chunk, processes it, and requests the next chunk when needed.

## 8. Memory benefits and processing files

Generators are useful for large files, datasets, streaming data, pipelines, database results, and potentially infinite sequences. For example, `readlines()` loads every line into a list, while iterating over the file processes one line at a time:

```python
# Loads all lines into memory.
with open("logs.txt", encoding="utf-8") as file:
    lines = file.readlines()

# Reads and processes one line at a time.
with open("logs.txt", encoding="utf-8") as file:
    for line in file:
        process(line.rstrip("\n"))
```

A generator function can provide the same line-by-line behavior while allowing the reading logic to be reused:

```python
def read_lines(path):
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            yield line.strip()

for line in read_lines("logs.txt"):
    process(line)
```

The generator keeps only the current iteration state rather than a list of all lines. In the source demonstration, `tracemalloc` compares peak Python memory while reading a million-line file with `readlines()` and with `read_lines()`. The exact measurements depend on the machine, file, and Python version, but the generator approach avoids storing all lines at once.

## 9. A generator is usually consumed once

Generators are stateful. Once a generator is exhausted, iterating over that same generator again produces no values. Create a new generator if the sequence must be processed again:

```python
gen = (x for x in range(3))

print(list(gen))  # [0, 1, 2]
print(list(gen))  # []
```

## 10. Delegating with `yield from`

`yield from` forwards values from another iterable or generator. It is a shorter alternative to looping over the iterable and yielding each item manually:

```python
def manual_values():
    for number in [1, 2, 3]:
        yield number

def delegated_values():
    yield from [1, 2, 3]

print(list(delegated_values()))  # [1, 2, 3]
```

It also works with nested generators:

```python
def first():
    yield 1
    yield 2

def second():
    yield 3
    yield 4

def all_numbers():
    yield from first()
    yield from second()

print(list(all_numbers()))  # [1, 2, 3, 4]
```

## 11. Generators with `sum()`

A list comprehension builds the complete list before `sum()` starts adding its values. A generator expression lets `sum()` consume each computed value without retaining the whole intermediate collection:

```python
list_total = sum([x * x for x in range(1_000_000)])
generator_total = sum(x * x for x in range(1_000_000))
```

Both expressions calculate the same total. The generator expression is more memory-efficient for a large sequence when values are only needed once. Parentheses around a generator expression are optional when it is the only argument to a function.

## 12. Lists and generators: choosing between them

Use a generator when values can be processed sequentially and it is useful to avoid materializing the full result in memory. Use a list when you need random access, need to reuse the complete collection, or need operations that require all values to be available.

```python
numbers_list = [x for x in range(5)]  # Stored values; reusable and indexable
numbers_gen = (x for x in range(5))   # Values produced on demand; consumed once
```

## 13. Practice: an infinite Fibonacci generator

A generator can represent an infinite sequence because it calculates each next value only when requested. Use a consumer such as `itertools.islice` to take a finite number of values:

```python
import itertools

def fib_gen():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

first_ten = list(itertools.islice(fib_gen(), 10))
print(first_ten)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

Calling `next()` repeatedly on one `fib_gen()` instance also continues the sequence from its saved state.
