# Practice 1 : Row-wise vs Column-wise experiment
import itertools
import time

# Row-wise access
def row_wise(lst):
    total = 0
    n = len(lst)
    for row in range(n):
        for col in range(n):
            total += lst[row][col]
    return total

# Column-wise access
def col_wise(lst):
    total = 0
    n = len(lst)
    for col in range(n):
        for row in range(n):
            total += lst[row][col]
    return total

counter = itertools.count()
lst = [[next(counter) for _ in range(2000)] for _ in range(2000)]


def measure_time(func, lst):
    times = []

    for _ in range(3):
        start = time.perf_counter()
        total = func(lst)
        end = time.perf_counter()

        times.append(end - start)

    return total, min(times)


row_total, row_best = measure_time(row_wise, lst)
col_total, col_best = measure_time(col_wise, lst)

assert row_total == col_total

print(f"Row-wise Best time: {row_best:.6f} seconds")
print(f"Row-wise Total: {row_total}")
print(f"\nColumn-wise Best time: {col_best:.6f} seconds")
print(f"Column-wise Total: {col_total}")
print("\nBoth totals are equal!")