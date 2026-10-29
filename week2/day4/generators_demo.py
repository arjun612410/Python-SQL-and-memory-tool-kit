# Why we need generator???
# First see a normal function
def get_numbers():
    return [1, 2, 3, 4, 5]

numbers = get_numbers()
# This function creates the entire list in memory at once.
# If there are 5 numbers, then there’s no problem. But imagine,
def get_numbers():
    return list(range(10_000_000))
# Now, millions of values ​​will be created in memory simultaneously.
# In many situations, we don't actually need all the values ​​at once. We need to process one value, then the next, and so on.
# In that situation generators are useful.
# A generator produces values one at a time instead of creating and storing all values at once. This makes generators useful when working with large sequences or streams of data.

# So, first we need to study about yield and also the difference between return and yield.
# If we talk about return,
# function start
#      ↓
# code execute
#      ↓
#   return
#      ↓
# function END

# In generator function we use yield instead of return. For example,
def numbers():
    yield 10
    yield 20
    yield 30
gen = numbers()
print(next(gen)) # 10
print(next(gen)) # 20 
print(next(gen)) # 30 
# print(next(gen)) # StopIteration

# return vs yield : return sends a value back to the caller and terminates the function. yield, on the other hand, produces a value and suspends the function while preserving its execution state. When the generator is resumed, execution continues from where it was paused.

# How generator remembers its state??
# A generator preserves its execution state between calls. This includes its local variables and the point at which execution was suspended. Therefore, the next time next() is called, execution resumes from the previous yield.
# For example,
def counter():
    count = 1
    yield count
    count += 1
    yield count
    count += 1
    yield count

gen = counter()
print(next(gen)) # 1
print(next(gen)) # 2

# Generator is an Iterator!!!
# A generator is an iterator because it follows the iterator protocol and produces values one at a time through next(). It can also be used directly in a for loop. That's why a generator is an iterator.
# However, every iterable is not necessarily an iterator; for example, a list is iterable but is not itself an iterator.

# Generator Function vs Generator Expression
# Generator Function : Function + yield
def squares(n):
    for i in range(n):
        yield i * i

gen = squares(5)

for value in gen:
    print(value)  # 0 1 4 9 16

# Generator Expression
# We already see list comprehension, for example, squares = [x * x for x in range(5)]. The output list is [0, 1, 4, 9, 16]
# But in generator expression we use curly brackets instead of square brackets.
squares = (x * x for x in range(5))

# A generator function uses yield to produce values, whereas a generator expression provides a concise syntax similar to a list comprehension but uses parentheses instead of square brackets. Both generate values lazily.

# Lazy Evaluation
# Lazy evaluation means that a value is computed only when it is actually requested. Generators use lazy evaluation, so they do not need to create the entire sequence in advance. For example,
def numbers():
    print("Generating 1")
    yield 1

    print("Generating 2")
    yield 2

    print("Generating 3")
    yield 3

gen = numbers()
print(next(gen)) # Generating 1 1
print(next(gen)) # Generating 2 2
print(next(gen)) # Generating 3 3

# Real Life analogy : Lets we take example of netflix. If netflix says before playing the movie load full movie of 20GB in RAM. So, this is a bad idea. Instead of doing this, data streams in chunks
# need data
#   ↓
# get chunk
#   ↓
# consume
#   ↓
# need next
#   ↓
# get next chunk

# The mental model of generator is similar to this : 
#   consumer asks
#       ↓
# generator produces one value
#       ↓
#     pause
#       ↓
# consumer asks again
#       ↓
#  produce next

# Memory benefit on big data
# Generators are especially useful for large datasets because they produce items one at a time rather than materializing the entire result in memory. For example, a large file can be processed line by line instead of loading all of its contents at once.
# Suppose,
numbers = [x for x in range(10_000_000)]
# This will materialize the result consisting of millions of integers—into a list. Conceptually, RAM: [0, 1, 2, 3, 4, 5, .......... 9,999,999]. But in generator,
numbers = (x for x in range(10_000_000))
# It does not store the entire resulting sequence at once. Conceptually, Generator state -> next value when requested.
# That's why generator are useful for : large files, huge datasets, streaming data, pipelines, database results, potentially infinite sequences

# Real world example of big file : Imagine a file of 20GB. So, the bad approach will be 
# file = open("logs.txt")
# data = file.readlines()
# Here, we are trying to load the whole file in a memory. So, the better pattern will be
# def read_file(filename):
#     with open(filename) as file:
#         for line in file:
#             yield line
# for line in read_file("logs.txt"):
#     print(line)

# Important trade-off : generator is only consumed one time
# Generators are stateful and are generally consumed once. After a generator is exhausted, iterating over the same generator object again does not restart it. A new generator must usually be created. For example,
gen = (x for x in range(3))
print(list(gen)) # [0, 1, 2]
print(list(gen)) # []

# yield from
# It delegates iteration to another iterable or generator. Instead of manually looping over an iterable and yielding each value, we can use yield from to forward its values directly.
# In python instead of iterating all the elements in the iterable like this 
def generator():
    numbers = [1, 2, 3]

    for number in numbers:
        yield number
# Instead of doing this python gives us a shorthand : 
def generator():
    yield from [1, 2, 3]

for x in generator():
    print(x) # 1 2 3

# This is also useful in nested generator
def first():
    yield 1
    yield 2

def second():
    yield 3
    yield 4

def all_numbers():
    yield from first() # 1 2
    yield from second() # 3 4

# sum([..]) vs sum((..)) : A list comprehension creates the complete list before sum() processes it. A generator expression produces each value on demand, allowing sum() to consume the values without storing the entire intermediate sequence.
# In list, sum([x * x for x in range(1_000_000)]) first it will create list [0, 1, 4, 9, 16, ........] then, sum() will consume
# In generator, sum((x * x for x in range(1_000_000))) generator produces value one by one so, the flow will
# generate value
#       ↓
# sum consumes it
#       ↓
# generate next
#       ↓
# sum consumes it

# List vs generator : A list stores its elements in memory, whereas a generator produces values lazily, one at a time. I would prefer a generator when processing a large amount of data sequentially because it avoids materializing the entire result in memory. However, if I need random access or need to reuse the complete collection multiple times, a list may be more suitable.

# Practice 1 : fib_gen()
import itertools
def fib_gen():
    a,b = 0,1
    while True:
        yield a 
        a,b = b,a+b

fib = list(itertools.islice(fib_gen(),10))
print(fib) # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

gen = fib_gen()
print(next(gen)) # 0
print(next(gen)) # 1
print(next(gen)) # 1 
print(next(gen)) # 2

# Practice 2 : read_lines(path)
line_content = "This is line number {} of the generated English text dataset.\n"

with open("logs.txt", "w", encoding="utf-8") as file:
    batch = []
    for i in range(1, 1_000_001):
        batch.append(line_content.format(i))
        if i % 50_000 == 0:
            file.writelines(batch)
            batch = []

print("Done! 'logs.txt' has been created.")
import tracemalloc
def read_lines(path):
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            yield line.strip()

# readlines() : peak = 115356507
tracemalloc.start()

with open("logs.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

current, peak = tracemalloc.get_traced_memory()

print("Peak:", peak)

tracemalloc.stop()

# generator : peak = 34539
tracemalloc.start()

for line in read_lines("logs.txt"):
    pass

current, peak = tracemalloc.get_traced_memory()

print("Peak:", peak)

tracemalloc.stop()
