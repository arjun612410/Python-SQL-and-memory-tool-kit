# Practice 1 : Reference cycle demo
import gc

class Node:
    def __init__(self):
        self.other = None

# Disable automatic garbage collection
gc.disable()

# Experiment 1: Reference cycle
x, y = Node(), Node()
x.other = y
y.other = x
del x, y

print("Reference cycle:", gc.collect())

# Experiment 2: No reference cycle
x, y = Node(), Node()
del x, y

print("No reference cycle:", gc.collect())

# Re-enable automatic garbage collection
gc.enable()

# Practice 2 : tracemalloc snapshot
import tracemalloc
def create_list():
    return [i for i in range(1000000)]

tracemalloc.start()
snap1 = tracemalloc.take_snapshot()
big_list = create_list()
snap2 = tracemalloc.take_snapshot()
stats = snap2.compare_to(snap1, "lineno")

for stat in stats[:10]:
    print(stat)

tracemalloc.stop()

# Practice 3 : Find Deliberate leak and fix it 
# Before : Unlimited Cache
import tracemalloc
cache_store = []

def cache_data():
    data = [i for i in range(10000)]
    cache_store.append(data)

tracemalloc.start()
snap1 = tracemalloc.take_snapshot()

for _ in range(100):
    cache_data()

snap2 = tracemalloc.take_snapshot()
before_stats = snap2.compare_to(snap1, "lineno")
print("BEFORE FIX")

for stat in before_stats[:5]:
    print(stat)

before_memory = sum(stat.size_diff for stat in before_stats)
cache_store.clear()

# After : Bounded Cache
from collections import deque
cache_store = deque(maxlen=10)
snap3 = tracemalloc.take_snapshot()

for _ in range(100):
    cache_data()

snap4 = tracemalloc.take_snapshot()
after_stats = snap4.compare_to(snap3, "lineno")
print("\nAFTER FIX")

for stat in after_stats[:5]:
    print(stat)

after_memory = sum(stat.size_diff for stat in after_stats)

print("\nBefore:", before_memory / (1024 * 1024), "MB")
print("After:", after_memory / (1024 * 1024), "MB")
print("Reduced:", (before_memory - after_memory) / (1024 * 1024), "MB")

tracemalloc.stop()