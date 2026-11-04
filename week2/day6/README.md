# Memory, Virtual Memory, and Cache Locality

This guide explains the memory-management and performance concepts for Day 6. The examples are simplified models; real behavior depends on the operating system, CPU, and hardware architecture.

## 1. Why does a program need memory?

While a program runs, it needs places to keep its instructions, variables, objects, and runtime state. For example:

```python
x = 10
name = "Arjun"
values = [1, 2, 3, 4]
```

Python stores these objects in memory so the program can use them. The CPU works with data held in registers and caches, and the system uses RAM for active program data. SSDs and disks provide larger, persistent storage, but they are much slower than RAM.

## 2. Physical memory and physical addresses

Physical memory usually means the computer's RAM. A physical address identifies a location in that RAM.

If every program managed physical RAM addresses directly, programs could conflict or read one another's data. Modern systems instead give each process a protected address space and manage the connection to physical RAM.

## 3. Virtual memory

Virtual memory is an abstraction that gives each process its own virtual address space. A program uses virtual addresses; the operating system and memory-management hardware translate them to physical locations.

```text
Process uses a virtual address
             |
             v
     address translation
             |
             v
       physical RAM
```

This allows processes to be isolated, memory access to be protected, and physical RAM to be managed without requiring each program to track its actual locations.

## 4. Virtual addresses and physical addresses

A **virtual address** belongs to a process's address space. A **physical address** identifies a location in RAM. The two addresses need not be the same.

For example, two processes may both use virtual address `0x1000`, while the system maps them to different physical locations:

```text
Process A: virtual 0x1000 -> physical 0x7200
Process B: virtual 0x1000 -> physical 0xA400
```

These are illustrative addresses, not fixed mappings.

## 5. Pages and frames

Virtual memory is divided into fixed-size blocks called **pages**. Physical memory is divided into same-sized blocks called **frames**. A page can be placed in any available frame; neighboring virtual pages do not have to occupy neighboring physical frames.

```text
Virtual pages            Physical frames
Page 0  ----------------> Frame 5
Page 1  ----------------> Frame 2
Page 2  ----------------> Frame 8
```

For example, if the page size is 4 KiB, each physical frame is also 4 KiB.

## 6. Page tables

A **page table** records how a process's virtual pages map to physical frames. Page-table entries can also contain information such as whether a page is present and what access permissions apply.

```text
Virtual page    Physical frame
     0                 5
     1                 2
     2                 8
```

Different processes can have different page tables, so the same virtual page number can map to different physical frames in different processes.

## 7. Address translation: page number and offset

Conceptually, a virtual address is split into a **virtual page number** and an **offset** within that page. Translation changes the page number to a frame number; the offset stays the same.

```text
Virtual address: page 3, offset 100
Page table:      page 3 -> frame 7
Physical address: frame 7, offset 100
```

The frame and offset together identify the physical location.

## 8. Why the TLB is needed

Looking up a page table can take time, and address translation is needed frequently. A **Translation Lookaside Buffer (TLB)** is a small, fast cache of recently used address translations.

Instead of repeatedly looking up a known mapping, the processor can often use a cached entry such as `virtual page 3 -> physical frame 7`.

## 9. TLB hits and TLB misses

- A **TLB hit** means the needed translation is already in the TLB.
- A **TLB miss** means the translation is not in the TLB, so the system must resolve it through the page-table mechanism and may cache it for later use.

A TLB miss does **not** by itself mean the page is missing from RAM.

## 10. Page faults

A **page fault** is an exception raised when a memory access cannot be completed using the current mapping. The operating system handles it: it may load a page into RAM, update a mapping, or reject an invalid or prohibited access.

Therefore, a page fault is not automatically a program crash. Some faults are part of normal virtual-memory operation; invalid or unauthorized accesses may cause the program to fail.

## 11. TLB miss versus page fault

These terms describe different events:

| Event | Meaning |
|---|---|
| TLB miss | The translation is not in the fast TLB cache. The page may still be in RAM. |
| Page fault | The memory access needs operating-system handling because the current mapping cannot service it. |

A TLB miss can be resolved by consulting the page tables without a page fault.

## 12. Swap

When RAM is under pressure, an operating system may move less-used memory contents to disk-backed swap space and bring them back when needed. This makes it possible to manage more active memory than fits in RAM at one time, but disk or SSD access is much slower than RAM access.

## 13. Thrashing

**Thrashing** happens when a system spends so much time moving pages between RAM and storage that little time remains for useful work. Frequent page faults and heavy storage activity can be symptoms.

It can occur when the active working sets of processes do not fit well in available physical memory.

## 14. Memory protection

Virtual-memory mappings help prevent a process from freely accessing another process's memory or protected operating-system memory. Pages can have permissions such as **read**, **write**, and **execute**.

For example, a mapping might allow a process to read and execute code but not modify it. An access that violates a mapping's permissions can be rejected by the system.

## 15. The memory hierarchy

Memory and storage form a hierarchy with trade-offs between speed, size, and cost per byte:

```text
Fastest, smallest
  Registers
  CPU caches (L1, L2, L3)
  RAM
  SSD / disk
Slowest, largest
```

Upper levels are generally faster and smaller. Lower levels are generally larger and slower.

## 16. Registers

Registers are very small, very fast storage locations used directly by the CPU during instruction execution. A simplified operation might load values into registers, calculate a result, and then store the result back to memory.

## 17. L1, L2, and L3 caches

CPU caches keep useful data close to the processor to reduce the time spent waiting for RAM.

- **L1** is typically the smallest and fastest cache.
- **L2** is typically larger and slower than L1.
- **L3** is typically larger than L2 and still faster to access than RAM.

Exact cache sizes and designs differ between processors, so treat this as a general model rather than a universal hardware specification.

## 18. Temporal locality

**Temporal locality** means recently accessed data is likely to be accessed again soon.

```python
total = 0
x = 7

for _ in range(1_000):
    total += x
```

The loop repeatedly uses `x` and `total`, so keeping recently used data close to the CPU can be beneficial.

## 19. Spatial locality

**Spatial locality** means that after accessing one memory location, a program is likely to access nearby locations soon.

For example, iterating through consecutive elements of a sequence accesses neighboring elements:

```python
for value in values:
    process(value)
```

Processors transfer data in units such as cache lines, so one access can make nearby data available more quickly too.

## 20. Why sequential access can be faster

Sequential access often benefits from spatial locality: after one element is fetched, nearby elements may already be in cache. Repeatedly jumping among distant locations can make less effective use of those cache lines.

For a two-dimensional array, comparing row-wise and column-wise traversal is a common way to explore this idea:

```python
size = 500
matrix = [[row + col for col in range(size)] for row in range(size)]

# Row-wise traversal
row_total = 0
for row in matrix:
    for value in row:
        row_total += value

# Column-wise traversal
column_total = 0
for col in range(size):
    for row in range(size):
        column_total += matrix[row][col]
```

The row-wise loop walks each inner list consecutively. The column-wise loop repeatedly switches between inner lists. This illustrates access patterns, but Python's object representation and interpreter overhead affect timings; results are not a guaranteed benchmark of hardware cache speed. For controlled measurements, use a suitable array library and repeat the experiment carefully. The companion [`locality_experiment.py`](./locality_experiment.py) can be used for this exercise.

## 21. User mode and kernel mode

Applications such as ordinary Python programs normally run in **user mode**, with restricted privileges. The operating system's core runs in **kernel mode**, which allows it to perform protected operations and manage hardware resources.

When an application needs an operating-system service, it uses an OS-controlled mechanism rather than directly performing arbitrary privileged operations. For example, the operating system may handle a page fault on a process's behalf.

## Quick interview recap

- Virtual addresses are translated to physical addresses; they are not necessarily identical.
- Pages are virtual-memory blocks; frames are physical-memory blocks.
- A page table stores virtual-page-to-physical-frame mappings.
- The TLB caches recent translations.
- A TLB miss is not the same as a page fault.
- A page fault requires operating-system handling, but does not always mean a crash.
- Temporal locality concerns reusing recently accessed data; spatial locality concerns accessing nearby data.
- User mode restricts application privileges; kernel mode is used for privileged operating-system work.
