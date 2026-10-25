# Python Closures

Yeh guide [`closures_demo.py`](./closures_demo.py) mein dikhaye gaye Python concepts ko examples ke saath explain karti hai.

## 1. LEGB scope rule

Python kisi variable ka naam resolve karte waqt is order mein search karta hai:

1. **Local** — current function ke andar
2. **Enclosing** — outer/nested function ke scope mein
3. **Global** — module/file ke top level par
4. **Built-in** — Python ke built-in names, jaise `print` aur `len`

```python
x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)

    inner()

outer()  # local
```

`inner()` ke andar `x` local hai, isliye Python ko enclosing ya global `x` tak jaane ki zaroorat nahi padti. Agar `inner()` mein `x` define na ho, to Python enclosing scope mein value dhoondhega.

## 2. Functions bhi objects hote hain

Python mein function ko variable mein rakh sakte hain. Assignment se function ki copy nahi banti; dono names usi function object ko refer karte hain.

```python
def greet():
    print("Hello")

say_hello = greet
say_hello()  # Hello
```

Functions ko list mein bhi rakh sakte hain aur baad mein call kar sakte hain:

```python
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

operations = [add, multiply]

print(operations[0](2, 3))  # 5
print(operations[1](2, 3))  # 6
```

## 3. Higher-order functions

**Higher-order function** woh function hai jo ek ya zyada functions ko argument mein leta hai, function return karta hai, ya dono karta hai.

### Function ko argument ke roop mein dena

```python
def square(number):
    return number * number

def apply_operation(operation, value):
    return operation(value)

print(apply_operation(square, 5))  # 25
```

Yahan `apply_operation` ko `square` function diya gaya hai. `map()`, `filter()` aur `sorted()` bhi functions ko accept kar sakte hain.

### Function ko return karna

```python
def make_greeter():
    def greet():
        print("Hello")

    return greet

greeter = make_greeter()
greeter()  # Hello
```

Dhyan dein: `return greet` function ko return karta hai; `return greet()` us function ko turant call karega.

## 4. Closure kya hota hai?

**Closure** ek inner function hai jo apne enclosing function ke variables ko yaad rakhta hai, chahe enclosing function ka execution khatam ho chuka ho.

```python
def make_printer():
    message = "Closure remembers this"

    def print_message():
        print(message)

    return print_message

printer = make_printer()
printer()  # Closure remembers this
```

`make_printer()` return ho gaya, lekin `print_message` ko `message` ab bhi available hai. Inner function ne apne enclosing scope se `message` capture kiya hai.

## 5. `nonlocal` se enclosing variable update karna

Sirf kisi enclosing variable ko read karne ke liye `nonlocal` ki zaroorat nahi hoti. Lekin nested function mein us variable ko reassign/update karna ho, to `nonlocal` declare karna hota hai.

```python
def make_counter():
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count

    return counter

counter = make_counter()
print(counter())  # 1
print(counter())  # 2
print(counter())  # 3
```

`nonlocal count` batata hai ki `count` current `counter()` function ka local variable nahi hai; yeh nearest enclosing function ke scope mein maujood variable hai. Iske bina `count += 1` par `UnboundLocalError` aayega, kyunki assignment ke kaaran Python `count` ko local samjhega.

## 6. Closures ke common uses

### Function factory: configurable behavior

Closure kisi setting/value ko function ke saath bandh sakta hai. Ek hi factory se alag-alag multipliers banaye ja sakte hain:

```python
def make_multiplier(factor):
    def multiply(number):
        return number * factor

    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
```

`double` apna `factor=2` aur `triple` apna `factor=3` yaad rakhta hai.

### State ko encapsulate karna

Counter ka `count` closure ke andar rehta hai. Use seedhe global variable ke roop mein rakhne ki zaroorat nahi hoti; returned function ke calls ke beech uski state bani rehti hai.

Har `make_counter()` call ek naya independent counter banata hai:

```python
first = make_counter()
second = make_counter()

print(first())   # 1
print(first())   # 2
print(second())  # 1
```

### Decorators ke peeche closures

Decorator ek function leta hai, uske around wrapper banata hai aur wrapper return karta hai. `wrapper` closure ke zariye original `func` ko yaad rakhta hai:

```python
def my_decorator(func):
    def wrapper():
        print("Function se pehle")
        func()
        print("Function ke baad")

    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
```

Output:

```text
Function se pehle
Hello!
Function ke baad
```

`@my_decorator` ka matlab hai `say_hello = my_decorator(say_hello)`.

## 7. Closure aur normal function mein farq

Normal function ko har zaroori value argument ke roop mein deni padti hai:

```python
def add(a, b):
    return a + b

print(add(10, 5))  # 15
```

Closure ek value ko pehle se capture kar sakta hai:

```python
def make_adder(a):
    def add(b):
        return a + b

    return add

add_10 = make_adder(10)
print(add_10(5))  # 15
```

`add_10` ke har call par `a=10` dobara dene ki zaroorat nahi hai.

## 8. Loop mein late-binding trap

Loop ke andar banaye gaye lambdas `i` ki alag-alag copies capture nahi karte. Woh usi variable `i` ko baad mein read karte hain:

```python
functions = []

for i in range(3):
    functions.append(lambda: i)

print([function() for function in functions])
# [2, 2, 2]
```

Jab lambdas call hote hain, loop khatam ho chuka hota hai aur `i` ki current value `2` hoti hai.

Default argument ke zariye har iteration ki value capture karke ise fix kar sakte hain:

```python
functions = []

for i in range(3):
    functions.append(lambda i=i: i)

print([function() for function in functions])
# [0, 1, 2]
```

Default argument function banate waqt evaluate hota hai, isliye har lambda ko us iteration ki value milti hai.

## 9. Closure ko inspect karna

Function ke `__closure__` aur `__code__.co_freevars` attributes se captured variables inspect kiye ja sakte hain:

```python
counter = make_counter()
counter()
counter()

print(counter.__code__.co_freevars)       # ('count',)
print(counter.__closure__[0].cell_contents)  # 2
```

- `co_freevars` captured/enclosing variables ke naam batata hai.
- `__closure__` un variables ke closure cells deta hai; `cell_contents` se cell mein stored value dekh sakte hain.

Yeh introspection aur learning ke liye useful hai. Application logic mein in internal attributes par depend karna aam taur par zaroori nahi hota.
