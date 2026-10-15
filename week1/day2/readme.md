# Python Dunder Methods

`dunder_demo.py` mein custom Python objects ko built-in operations ke saath kaam
karna sikhaya gaya hai. **Dunder** ka matlab **double underscore** hai:
`__name__` jaise methods ke naam ke aage aur peeche double underscores hote hain.

Python in methods ko `len(obj)`, `str(obj)`, `obj1 + obj2` jaise operations ke
dauran khud call karta hai. Isse apni classes ke objects ka behavior define
kiya ja sakta hai.

## 1. `__init__` — object ko initialize karna

Object banne ke baad `__init__` uske attributes set karta hai. `self` us naye
object ko refer karta hai.

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age


student = Student("Arjun", 20)
print(student.name)  # Arjun
print(student.age)   # 20
```

`Student("Arjun", 20)` likhne par Python object banata hai aur uske liye
`__init__` ko arguments deta hai. Aam taur par `__init__` koi value return
nahi karta; iska kaam object ko initialize karna hai.

## 2. `__str__` — user-friendly text

`__str__` define karta hai ki `str(obj)` ya `print(obj)` par object kaunsa
readable text de. Agar yeh method na ho, to print mein aam taur par class aur
object ki identity wali default representation dikhti hai.

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

`__str__` ko **string** return karni chahiye.

## 3. `__repr__` — developer-friendly representation

`__repr__` debugging aur interactive console ke liye object ki informative
representation deta hai. `repr(obj)` ise explicitly call karta hai.

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

`!r` f-string mein value ke `repr()` ko use karta hai. Agar `__str__`
define na ho, to `str(obj)` aam taur par `__repr__` par fallback karta hai.

## 4. `__eq__` — `==` ka behavior

`__eq__` tay karta hai ki do custom objects `==` se kab equal maane jayenge.
Isse define na karne par, aam taur par do alag objects equal nahi hote, chahe
unke attributes same hon.

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

Yahan equality `name` aur `age` par based hai. `NotImplemented` doosre type
ke object ke comparison ko Python ke doosre operand ya normal fallback ke
liye chhodta hai.

## 5. `__hash__` — sets aur dictionary keys

`__hash__` integer hash value deta hai. Hash-based collections, jaise `set`
aur `dict` keys, iska istemal karte hain. Agar `__eq__` ke mutabik do objects
equal hain, to unka hash bhi same hona zaroori hai.

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

Hash values alag program runs mein badal sakte hain; isliye kisi fixed hash
number ko output ke roop mein expect nahi karna chahiye. Hashable objects ko
set ya dictionary key banane ke baad unke equality/hash mein istemal hone
waale attributes badalna bhi unsafe hai. Mutable objects ke liye aksar
`__hash__` define nahi karna chahiye.

## 6. `__len__` — `len(obj)` ka behavior

`__len__` batata hai ki `len(obj)` par kaunsi length milegi. Isse
non-negative integer return karna chahiye.

```python
class Playlist:
    def __init__(self, songs):
        self.songs = songs

    def __len__(self):
        return len(self.songs)


playlist = Playlist(["Song1", "Song2", "Song3"])
print(len(playlist))  # 3
```

## 7. `__bool__` — object ko true ya false maanna

`__bool__` define karta hai ki `bool(obj)` aur `if obj:` mein object true
maana jayega ya false. Is method ko `True` ya `False` return karna chahiye.

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

## 8. `__getitem__` — index se item lena

`__getitem__` `obj[index]` ka behavior define karta hai. Example mein list ko
index karne ka kaam class apne andar ki `songs` list ko deti hai.

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

Index valid na ho to andar ki list ki tarah `IndexError` aa sakta hai.

## 9. `__contains__` — `in` operator

`__contains__` define karta hai ki `item in obj` ka result kya hoga.

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

Is method ka result boolean hona chahiye. Agar `__contains__` na ho, to
Python kuch iterables ke liye iteration ke zariye membership check kar sakta
hai.

## 10. `__add__` — `+` operator

`__add__` batata hai ki `obj1 + obj2` kaise kaam karega. Yeh example do
points ke `x` aur `y` coordinates ko add karke naya point banata hai.

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

`__add__` ko result ke roop mein naya `Point` object milta hai; `__str__`
use print karne layak `(x, y)` text mein badalta hai.

## `Money` example: `__repr__`, `__eq__`, aur `__hash__`

File ka `Money` example teen methods ko ek class mein jodta hai. Yahan do
money records tab equal hain jab unka naam, withdrawal aur deposit sab same
hon.

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

`__eq__` aur `__hash__` mein wahi fields use ki gayi hain, isliye equal
`Money` objects set mein ek hi entry banate hain. Is example mein fields ko
object banne ke baad badalne se bachna chahiye jab object set/dictionary key
ke roop mein use ho raha ho.

## `Playlist` example: length, indexing, aur iteration

File ka aakhri example `__len__`, `__getitem__`, aur `__iter__` ko ek saath
use karta hai. `__iter__` songs par seedha loop chalata hai.

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

`__iter__` iterator deta hai; `for` loop usse har song ek-ek karke leta hai.
Is class mein `__getitem__` indexing deta hai aur `__len__` playlist ki
length.

## File chalana

`week1/day2` folder se:

```bash
python dunder_demo.py
```
