import copy

## 1. id of objects
a = [1,2,3]
b = [1,2,3]
print(id(a)) ## 2402592925696
print(id(b)) ## 2402592776576
## as we see here both a and b have same values but different id's, so they are different objects in memory
a = [1,2]
b = a
print(id(a)) ## 2402592925696
print(id(b)) ## 2402592925696
## as we can see here both a and b have same values and same id's because when we write b=a then b refers to the same object as a, so they are same objects in memory

## 2. is vs ==
a = [1,2,3]
b = [1,2,3]
print(a == b) ## True
print(a is b) ## False
## as we can see here that a is b is False because "is" checks for object identity while "==" checks for value equality, so even though a and b have same values they are different objects in memory

## 3. mutable vs immutable objects
p = [1,2,3,4]
p.append(5)
print(p) ## [1, 2, 3, 4, 5]
## as we can see here that p is a mutable object because we can change its value by appending 5 to it
name = "Arjun"
## name[0] = "a" ## TypeError: 'str' object does not support item assignment
## as we can see here that name is an immutable object because we cannot change its value by trying to assign a new value to its first character
name = name + " Pant"
print(name) ## Arjun Pant
## as we can see here that we can change the value of name by creating a new string and assigning it to name, but we cannot change the value of name in place because strings are immutable objects

## 4. name are references not boxes
x = [1,2]
y = x
## it means that y is a reference to the same object as x, so if we change the value of x then y will also change because they are both referring to the same object in memory and vice versa is also true
y.append(3)
print(x) ## [1, 2, 3]

## 5. aliasing a list
z = [4,5]
w = z
w.append(6)
print(z) ## [4, 5, 6]

## 6. copy vs deepcopy
original = [[1, 2], [3, 4]]
shallow_copy = copy.copy(original)
deep_copy = copy.deepcopy(original)

shallow_copy[0].append(3)
print(original) ## [[1, 2, 3], [3, 4]]
print(shallow_copy) ## [[1, 2, 3], [3, 4]]

deep_copy[0].append(5)
print(original) ## [[1, 2, 3], [3, 4]]
print(deep_copy) ## [[1, 2, 5], [3, 4]]
## here we can see the clear difference between shallow copy and deep copy, shallow copy creates a new object but does not create copies of nested objects, while deep copy creates a new object and also creates copies of all nested objects.

## 7. mutable default argument bug 
def add_item(item, x=[]):
    x.append(item)
    return x
print(add_item(1))  # [1]
print(add_item(2))  # [1, 2]

def add_item_fixed(item, x=None):
    if x is None:
        x = []
    x.append(item)
    return x
print(add_item_fixed(1))  # [1]
print(add_item_fixed(2))  # [2]
## here we can see that in the first function add_item, the default value of x is a mutable list, so when we call the function multiple times, it keeps appending to the same list. But in the second function add_item_fixed, we check if x is None and create a new list each time, so it does not have the same issue.

## 8. mutate vs return new
def mutate(lst):
    lst.append(4)

def new(lst):
    return lst + [4]

nums = [1, 2, 3]
# mutate(nums)
# print(nums)  # [1, 2, 3, 4]
res = new(nums)
print(nums, res)  # [1, 2, 3] [1, 2, 3, 4]
## here we can see that in the first function mutate, we are mutating the original list by appending 4 to it, while in the second function new, we are returning a new list that is the original list plus 4, so the original list remains unchanged.

## 9. rebinding vs mutation
x = [1, 2, 3]
y = x
x = [9]
print(y)  # [1, 2, 3]
## here we can see that when we rebind x to a new list [9], it does not affect y because y is still referring to the original list [1, 2, 3]. Rebinding creates a new reference, while mutation changes the object that the reference points to.