# Dunder methods: Dunder = Double Underscore
# __xyz__ methods are called dunder methods because they have double underscores before and after their name.
# the main purpose of dunder methods is to allow us to define how our objects behave with built-in Python operations.

# 1. __init__ : This method is called when an object is created. It initializes the object's attributes.
class Student1:
    def __init__(self, name, age):
        self.name = name
        self.age = age

s1 = Student1("Arjun", 20)

print(s1.name) # Arjun
print(s1.age) # 20
# When we write Student("Arjun", 20) the python creates a object and calls the __init__ method to initialize the object like that __init__(self, "Arjun", 20)

print(s1) # <__main__.Student object at 0x000001F2D3B8C250> 
## if we are not using the __str__ method then it will print the object in the above format which is not human readable.
# 2. __str__ : The purpose of this method is to print s1 in a human readable format. 

class Student2:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.name} is {self.age} years old."

s2 = Student2("Arjun", 20)
print(s2) # Arjun is 20 years old.

# 3. __repr__ : The purpose of this method is to print s1 in a developer/debugging format.

class Student3:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __repr__(self):
        return f"Student(name={self.name!r}, age={self.age!r})"

s3 = Student3("Arjun", 20)
print(s3) # Student(name='Arjun', age=20)

s1 = Student3("Arjun", 20)
s2 = Student3("Arjun", 20)
print(s1 == s2) # False
# the output is False because the default behaviour of the == operator is to compare the memory address of the objects.

# 4. __eq__ : it decides the meaning of == operator between custom objects. We can override this method to compare the attributes of the objects instead of their memory addresses.

class Student4:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, other):
        return self.name == other.name and self.age == other.age

s4 = Student4("Arjun", 20)
s5 = Student4("Arjun", 20)
print(s4 == s5) # True

# 5. __hash__ : the purpose of this method is to enable objects to be used in hash-based collections like sets and dictionaries. If we override the __eq__ method, we should also override the __hash__ method to ensure that objects that are considered equal have the same hash value.
class Student5:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, other):
        return self.name == other.name and self.age == other.age

    def __hash__(self):
        return hash((self.name, self.age))

s5 = Student5("Arjun", 20)
s6 = Student5("Arjun", 20)
print(s5 == s6) # True
print(hash(s5) == hash(s6)) # True

# 6. __len__ : it is used to define the behavior of the built-in len() function for our custon objects. it is used to determine the length of an object.
class Playlist:
    def __init__(self, song):
        self.song = song

    def __len__(self):
        return len(self.song)

playlist = Playlist(["Song1", "Song2", "Song3"])
print(len(playlist)) # 3

## 7. __bool__ : it is used to define the behavior of the built-in bool() function for our custom objects. It is used to determine the truth value of an object.
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

# 8. __getitem__ : it is used to determine the item at a particular index
class Playlist:
    def __init__(self, song):
        self.song = song

    def __getitem__(self, index):
        return self.song[index]

playlist = Playlist(["Believer","Faded","Perfect"])
print(playlist[0]) # Believer
print(playlist[1]) # Faded

# 9. __contains__ : it defines the behavior of the item present in the object.
class Playlist:
    def __init__(self, songs):
        self.songs = songs

    def __contains__(self, song):
        return song in self.songs

playlist = Playlist(["Believer","Faded","Perfect"])

print("Faded" in playlist) # True
print("Shape of you" in playlist) # False

# 10. __add__ : this method is used to define how the object behaves when we use the + operator with it.
class point:
    def __init__(self,x,y):
        self.x = x
        self.y = y
    def __add__(self,other):
        return point(self.x + other.x, self.y + other.y)
    def __str__(self):
        return f"({self.x}, {self.y})"


    # create two points objexts
p1 = point(1,2)
p2 = point(5,5)

# adding these using + operator
p3 = p1 + p2

# display the result
print(p3) # (6, 7)


# Write Money class with __eq__, __hash__, __repr__

class Money:
    def __init__(self, name, withdraw, deposit):
        self.name = name
        self.withdraw = withdraw
        self.deposit = deposit

    def __repr__(self):
        return f"Name: {self.name!r}, Withdraw Money: {self.withdraw!r}, Deposit Money: {self.deposit!r}"

    def __eq__(self, other):
        return self.name == other.name and self.withdraw == other.withdraw and self.deposit == other.deposit

    def __hash__(self):
        return hash((self.name, self.withdraw, self.deposit))

p1 = Money("Arjun", 500, 1000)
p2 = Money("Arjun", 500, 1000)
print(p1 == p2) # True
print(hash(p1)) # -7956095260449729150
print(repr(p2)) # Name: 'Arjun', Withdraw Money: 500, Deposit Money: 1000


# Write Playlist class with __len__, __getitem__, __iter__

class Playlist:
    def __init__(self, songs):
        self.songs = songs

    def __len__(self):
        return len(self.songs)

    def __getitem__(self, index):
        return self.songs[index]

    def __iter__(self):
        return iter(self.songs)

p = Playlist(["Believer", "Faded", "Perfect"])

print(len(p))
print(p[0])
for song in p:
    print(song)