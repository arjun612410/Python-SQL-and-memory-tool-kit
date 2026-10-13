# Python Identity, References, Mutability, and Copying

This document explains every major concept demonstrated in `identity_demo.py` and goes deeper with examples so you understand how Python stores and manages objects in memory.

---

## 1. Object identity: `id()`

In Python, every object has a unique identity while it exists in memory. The built-in `id()` function returns the memory address of an object.

```python
a = [1, 2, 3]
b = [1, 2, 3]

print(id(a))
print(id(b))
```

Even though `a` and `b` have the same values, they are different objects. So their `id()` values are different.

```python
print(a == b)   # True
print(a is b)   # False
```

Why?
- `==` compares values.
- `is` compares object identity.
- Two different lists can contain the same items but still be different objects in memory.

### Important idea

If two variables refer to the same object, then they have the same `id()`:

```python
x = [10, 20]
y = x

print(id(x))
print(id(y))
```

Output will be the same because `y` is not a new list. It is another name pointing to the same list object.

### Real-world analogy

Think of objects as boxes in a warehouse.
- The variable name is a label attached to a box.
- `id(obj)` tells you which box it is.
- Two labels can point to the same box.

---

## 2. `is` vs `==`

This is one of the most important concepts in Python.

### `==` checks value equality

```python
a = [1, 2, 3]
b = [1, 2, 3]

print(a == b)   # True
```

Here, the contents are equal.

### `is` checks identity

```python
print(a is b)   # False
```

Even if the contents match, they are not the same object.

### Example with same object

```python
c = a
print(c == a)   # True
print(c is a)  # True
```

Now both variables point to the same object, so `is` returns `True`.

### Why this matters

This distinction is very important when comparing:
- integers
- strings
- lists
- custom objects
- data structures with nested values

For example:

```python
x = "hello"
y = "hello"
print(x == y)   # True
print(x is y)   # Often True for interned strings, but not guaranteed in all cases
```

Small string literals may be interned by Python, but that is an optimization. `is` should generally be used only when checking whether two references point to the exact same object.

### Best practice

Use:
- `==` when checking equality of values
- `is` when checking if two names refer to the exact same object

Example:

```python
None is None   # True
```

This is the correct use of `is` for singleton values like `None`.

---

## 3. Mutable vs immutable objects

Python objects are either mutable or immutable.

### Mutable objects

Mutable objects can be changed after creation.

```python
numbers = [1, 2, 3]
numbers.append(4)
print(numbers)   # [1, 2, 3, 4]
```

Lists are mutable because we can modify them in place.

Other examples of mutable objects:
- dictionaries
- sets
- custom classes

### Immutable objects

Immutable objects cannot be changed after creation.

```python
name = "Arjun"
# name[0] = "a"   # TypeError
```

Strings are immutable. You cannot modify a character inside a string.

```python
name = name + " Pant"
print(name)   # Arjun Pant
```

This is not in-place mutation. It creates a new string object and assigns it to the variable `name`.

### Key idea

For immutable objects, changing the value means creating a new object.

```python
x = 10
x = x + 5
print(x)  # 15
```

The value 10 is not changed in place. Python creates a new integer object 15 and rebinds `x` to it.

### Why mutability matters

Mutability affects:
- memory behavior
- function side effects
- debugging
- concurrency and shared data
- performance and optimization

---

## 4. Names are references, not boxes

A variable in Python is not a container that stores a copy of the value. Instead, it is a reference to an object.

```python
x = [1, 2]
y = x
```

Here:
- `x` points to a list object
- `y` points to the same list object

So `x` and `y` are two names for the same object.

```python
y.append(3)
print(x)   # [1, 2, 3]
```

Because both names point to the same list, modifying through one name is visible through the other.

### Mental model

Do not think of variables as boxes holding independent copies.

Think of them as labels on the same object.

```python
a = {'name': 'Arjun'}
b = a
b['name'] = 'Rohit'
print(a)   # {'name': 'Rohit'}
```

This is called aliasing.

---

## 5. Aliasing

Aliasing happens when two or more variables refer to the same object.

```python
z = [4, 5]
w = z
w.append(6)
print(z)   # [4, 5, 6]
```

Both `z` and `w` reference the same list.

### Why aliasing is important

Aliasing may cause surprises in code.

```python
def add_to_list(items):
    items.append('x')

numbers = [1, 2, 3]
add_to_list(numbers)
print(numbers)   # [1, 2, 3, 'x']
```

The function changed the original list because it received a reference to the same object.

### When aliasing is useful

Sometimes aliasing is intentional and helpful:
- shared configuration objects
- caching references
- passing large objects to functions without copying

### When aliasing is dangerous

It can create bugs when you expect a function to work on a copy but actually mutates the original data.

---

## 6. Copying objects

Python provides different ways to duplicate data structures.

### A shallow copy

A shallow copy creates a new outer object, but does not duplicate nested objects.

```python
import copy

original = [[1, 2], [3, 4]]
shallow_copy = copy.copy(original)
```

Now the outer list is different, but the inner lists are still shared.

```python
shallow_copy[0].append(3)
print(original)      # [[1, 2, 3], [3, 4]]
print(shallow_copy)  # [[1, 2, 3], [3, 4]]
```

Both outer lists appear changed because their shared inner list was mutated.

### A deep copy

A deep copy creates a completely independent clone of all nested objects.

```python
deep_copy = copy.deepcopy(original)

deep_copy[0].append(5)
print(original)      # [[1, 2, 3], [3, 4]]
print(deep_copy)     # [[1, 2, 5], [3, 4]]
```

The deep copy is independent from the original.

### Why this matters

Nested data structures are common in real programs.

Example:

```python
students = [
    {'name': 'A', 'marks': [90, 95]},
    {'name': 'B', 'marks': [80, 88]},
]
```

A shallow copy would duplicate the outer list but still share the inner dictionaries and mark lists.

Deep copy is safer when you need full independence.

### When to use which one

Use shallow copy when:
- you only need a new top-level container
- nested objects are not expected to change independently

Use deep copy when:
- nested values must be fully independent
- you want to avoid side effects between structures

---

## 7. Mutable default argument bug

This is a classic Python bug that happens when a mutable value is used as a default parameter.

```python
def add_item(item, x=[]):
    x.append(item)
    return x

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2]
```

The problem is that the default list `x=[]` is created only once when the function is defined, not each time the function is called.

So each call reuses the same list.

### Correct version

```python
def add_item_fixed(item, x=None):
    if x is None:
        x = []
    x.append(item)
    return x

print(add_item_fixed(1))  # [1]
print(add_item_fixed(2))  # [2]
```

This works because a new empty list is created each time the argument is omitted.

### Why this is a subtle bug

Many beginners assume default arguments are recreated every function call. In Python, they are evaluated once at function definition time.

### Real-world lesson

Never use mutable objects as default arguments unless you really want shared state across calls.

---

## 8. Mutate vs return a new object

Python functions often do one of two things:
- mutate the existing object
- return a new object without changing the original

### Mutation example

```python
def mutate(lst):
    lst.append(4)

nums = [1, 2, 3]
mutate(nums)
print(nums)   # [1, 2, 3, 4]
```

This changes the original list in place.

### Returning a new object example

```python
def new(lst):
    return lst + [4]

nums = [1, 2, 3]
res = new(nums)
print(nums)   # [1, 2, 3]
print(res)    # [1, 2, 3, 4]
```

Here the original list remains unchanged because `lst + [4]` creates a new list.

### Why this distinction matters

It affects:
- function design
- predictability
- debugging
- whether your function has side effects

### Good practice

Choose based on your intent:
- mutate in place if object state should change directly
- return a new value if you want to keep original data untouched

For example, many Python functions are designed not to mutate input arguments unless clearly documented.

---

## 9. Rebinding vs mutation

This is a very important distinction and it is easy to confuse.

### Rebinding

Rebinding means assigning a variable to a new object.

```python
x = [1, 2, 3]
y = x
x = [9]
print(y)   # [1, 2, 3]
```

Here:
- `y` still points to the original list `[1, 2, 3]`
- `x` now points to a new list `[9]`

Rebinding does not change the original object that `y` refers to.

### Mutation

Mutation changes the existing object itself.

```python
x = [1, 2, 3]
y = x
x.append(4)
print(y)   # [1, 2, 3, 4]
```

Here, both `x` and `y` still point to the same list, and the list itself is changed.

### Important summary

- Rebinding changes the variable name to point somewhere else.
- Mutation changes the object the variable already points to.

This is the core reasoning behind many bugs and many correct Python patterns.

---

## 10. Why this matters in Python programming

The concepts above are essential because Python is a language where variables are references, not copies.

### Example: shared state

```python
user = {'name': 'Arjun', 'skills': ['Python', 'SQL']}
manager = user
manager['skills'].append('Data Analysis')
print(user)
```

Because both names refer to the same dictionary, updating through one name affects the other.

### Example: a function accidentally mutating data

```python
def process(items):
    items.append('done')

jobs = ['read', 'write']
process(jobs)
print(jobs)   # ['read', 'write', 'done']
```

A function that seems harmless may mutate original data if it operates on shared objects.

### Example: safer function design

```python
def process_safe(items):
    new_items = items.copy()
    new_items.append('done')
    return new_items

jobs = ['read', 'write']
result = process_safe(jobs)
print(jobs)   # ['read', 'write']
print(result)   # ['read', 'write', 'done']
```

This keeps the original data untouched.

---

## 11. Quick summary

Here are the big ideas from this file:

1. Every object in Python has an identity (`id`).
2. `==` compares values; `is` compares whether two variables refer to the same object.
3. Mutable objects can be changed in place; immutable objects cannot.
4. Variables are references to objects, not independent boxes.
5. Aliasing means multiple variables point to the same object.
6. A shallow copy duplicates the outer container only; nested items are still shared.
7. A deep copy duplicates everything recursively.
8. Mutable default arguments can create hidden shared state across calls.
9. Mutation changes an object; rebinding changes the variable’s target.
10. Understanding these behaviors makes Python code safer, more predictable, and easier to debug.

---

## 12. Final example combining all concepts

```python
import copy

# Same value, different object
A = [1, 2, 3]
B = [1, 2, 3]
print(A == B)  # True
print(A is B)  # False

# Aliasing
C = A
C.append(4)
print(A)  # [1, 2, 3, 4]

# Immutable string
name = "Arjun"
# name[0] = 'a'  # TypeError
name = name + " Pant"
print(name)  # Arjun Pant

# Shallow copy and deep copy
matrix = [[1, 2], [3, 4]]
shallow = copy.copy(matrix)
deep = copy.deepcopy(matrix)

shallow[0].append(9)
print(matrix)  # [[1, 2, 9], [3, 4]]
print(deep)    # [[1, 2], [3, 4]]

# Rebinding vs mutation
x = [10, 20]
y = x
x = [99]
print(y)      # [10, 20]

x = [10, 20]
y = x
x.append(30)
print(y)      # [10, 20, 30]
```

This example brings together all the main ideas in one place.

---

## Conclusion

The core lesson from `identity_demo.py` is that Python objects live in memory, variables reference them, and whether they are mutable or immutable determines how they behave when changed. When you truly understand identity, aliasing, mutation, and copying, you become much better at reading Python code, finding bugs, and designing programs that behave predictably.

If you study these ideas carefully, you will understand the foundation of Python memory behavior and object semantics.
