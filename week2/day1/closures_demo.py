# Python: LEGB, first-class functions, closures
# 1. LEGB
# LEGB stands for Local, Enclosing, Global and Built-in. It describes the order Python follows when looking up a name. It first checks the local scope, then the enclosing function's scope, then the global scope, and finally the built-in scope.

x = "global"

def outer():
    x = "enclosing"

    def inner():
        x = "local"
        print(x)

    inner()

outer() # local

# a. Local : Variables defined inside the current inner function.
def hello():
    name = "Arjun"
    print(name) # Arjun

# b. Enclosing : Variables inside the outer function(s).
def outer():
    x = 10

    def inner():
        print(x)

    inner()

outer() # 10

# c. Global : Variables defined at the top level of the module/file.
x = 100

def func():
    print(x)

func() # 100

# d. Built-in : Predefined Python names (like print() or len()).
def func():
    print(len([1, 2, 3]))

func() # 3

# 2. Functions are objects
# In python, function is also an object. It means, we can manipulate a function like a variable.
def greet():
    print("Hello")

x = greet # This does not mean creating a copy of the function. x is simply referring to a function object. It is just like we studied in week1 
# a = [1, 2, 3]
# b = a
# b refers to the list object. x refers to the same function object.

x() # Hello

# You can also store a function in a variable. For example,
def add(a, b):
    return a + b

operation = add

print(operation(2, 3)) # 5

# You can also store functions in a list. For example,
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

operations = [add, multiply]

print(operations[0](2, 3)) # 5
print(operations[1](2, 3)) # 6

# 3. Higher-order Functions
# Higher-order functions (HOFs) are functions that either accept one or more functions as arguments, return a function as a result, or both.
# Example 1 : Function as argument
def square(x):
    return x * x

def apply_operation(func, value):
    return func(value)

print(apply_operation(square, 5)) # 25
# we give square function as argument in apply_operation function. Therefore, apply_operation is a higher-order function.

# Real python examples : map(), filter(), sorted()
numbers = [1, 2, 3, 4]
result = list(map(lambda x: x * 2, numbers))
print(result)
# We are providing a function to map().

# Example 2 : Returning a function
def outer():
    def inner():
        print("Hello")

    return inner

func = outer()
func() # Hello

# 4. Closure
# A closure is a function that remembers variables from the place where it was created. For example,
def outer():
    x = 10

    def inner():
        print(x)

    return inner

func = outer()
func() # 10

# The main question is that outer() has already executed. So, how is x still available?
# This is Closure
# The inner function remembered/captured the variables from its enclosing scope.

# Best example of Closure:
def make_counter():
    count = 0

    def counter():
        print(count)

    return counter

# But there is a problem. If we want to increase the counter
# def make_counter():
#     count = 0

#     def counter():
#         count += 1
#         print(count)

#     return counter
# This will give error
# So, what can we do to increase the count 

# 5. nonlocal
# The nonlocal keyword in Python is used inside nested functions to declare that a variable belongs to the nearest enclosing scope (the outer function) rather than the local scope.
def make_counter():
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count

    return counter

counter = make_counter()

print(counter()) # 1
print(counter()) # 2
print(counter()) # 3
# The function is remembering variables from its creation environment. That's Closure

# 6. Uses of Closure
# a. Function Factory (Configurable Logic) : Closures allow you to "bake" specific variables into a function. For instance, you can create customized multiplier functions dynamically:
def make_multiplier(factor):
    # Enclosing scope variable: factor
    def multiply(number):
        return number * factor  # Captures 'factor' from outer scope
    return multiply

# Create specialized functions
double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # Output: 10
print(triple(5))  # Output: 15

# b. Encapsulating State (Data Hiding) : If you need a function to remember data across invocations but want to avoid polluting the global scope, closures are an elegant alternative to classes. By using the nonlocal keyword, the inner function can modify the outer variable:
def make_counter():
    count = 0  # Private state variable
    
    def counter():
        nonlocal count  # Declares intent to modify outer variable
        count += 1
        return count
    return counter

my_counter = make_counter()
print(my_counter())  # Output: 1
print(my_counter())  # Output: 2
print(my_counter())  # Output: 3

# c. Behind the Scenes of Decorators : Python decorators rely heavily on closures to pass target functions as arguments and remember them when execution happens later:
def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()  # The closure remembers 'func'
        print("Something is happening after the function is called.")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()

# 7. Closure vs Normal Function
# Normal function : Values ​​must be explicitly passed to the function.
def add(a, b):
    return a + b

# Closure : 
def make_adder(a):

    def add(b):
        return a + b

    return add

add_10 = make_adder(10) 
print(add_10(5)) # 15
# we do not have to give again a=10 to add_10

# 8. Late-Binding Loop trap
functions = []

for i in range(3):
    functions.append(lambda: i)

for func in functions:
    print(func()) 
# we expected that the output of the above function is 0 1 2. But, the actual output of the function is 2 2 2.
# WHY ??? The reason is very simple, The lambda did not create a copy of the current value. It reference to i. After finishing the loop the value of i is 2. When functions were executed later, all three looked at the current value of i which is 2. Hence, the output of the following function is 2 2 2

# How to fix this ???
functions = []

for i in range(3):
    functions.append(lambda i=i: i)

for func in functions:
    print(func())

# The output of this function is 0 1 2 
# WHY ??? i=i captures the current value in a default argument.

# Practice 1 : make_counter()
def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter

a = make_counter()
b = make_counter()

print(a(), a(), a()) # 1 2 3
print(b()) # 1

# Practice 2 : make_multiplier(n)
def make_multiplier(n):
    def double(x):
        return n*x
    return double

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5), triple(5)) # 10 15 

# Practice 3 : late binding
output = []
for i in range(5):
    output.append(lambda: i)

print([f() for f in output])  # [4, 4, 4, 4, 4]

# To fix this 
output = []
for i in range(5):
    output.append(lambda i=i: i)

print([f() for f in output])  # [0, 1, 2, 3, 4]

a = make_counter()
a(); a()
print(a.__closure__[0].cell_contents) # 2
print(a.__code__.co_freevars) # ('count',)