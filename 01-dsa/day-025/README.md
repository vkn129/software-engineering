# Day 25: XOR Linked List

## Why This Exists

A standard doubly-linked list stores **two pointers per node** (prev and next), doubling
the pointer overhead compared to a singly-linked list. In memory-constrained environments
-- embedded systems, kernel data structures, IoT devices with kilobytes of RAM -- that
overhead matters.

The XOR linked list compresses both pointers into **one** by exploiting a mathematical
property of XOR:

```
A XOR B XOR A = B
```

Instead of storing `prev` and `next` separately, each node stores `prev XOR next`. Given
either neighbor's address, you can recover the other. This cuts pointer storage in half
while preserving bidirectional traversal.

### Where it actually shows up

- **Linux kernel `hlist`**: The kernel's hash-table bucket lists use a similar trick
  (storing a pointer-to-pointer for the back link) to save memory across millions of
  hash buckets.
- **Embedded firmware**: Sensor networks and microcontrollers where every byte counts.
- **Memory allocators**: Free-list management in custom allocators that need bidirectional
  traversal but want minimal overhead per free block.

### Why it's rarely used in application code

- Garbage collectors can't trace XOR-mangled pointers -- they look like integers, not
  references, so nodes become invisible to the GC and get collected prematurely.
- Debugging is painful: you can't inspect a single node and see its neighbors.
- Modern CPUs have so much RAM that saving 8 bytes/node rarely justifies the complexity.

The value of studying it isn't "use this everywhere" -- it's understanding how bitwise
properties translate into concrete memory savings and what trade-offs that creates.

## Theory

### The XOR Trick

XOR has three properties that make this work:

| Property       | Statement             | Why it matters                     |
|----------------|-----------------------|------------------------------------|
| Self-inverse   | `A ^ A = 0`          | XORing with a known value cancels it |
| Identity       | `A ^ 0 = A`          | Boundary nodes work (prev=0 or next=0) |
| Commutative    | `A ^ B = B ^ A`      | Direction doesn't matter           |

Each node stores: `npx = address(prev) ^ address(next)`

**Forward traversal** (knowing prev address):
```
next = npx ^ prev
     = (prev ^ next) ^ prev
     = next                     # prev cancels out
```

**Backward traversal** (knowing next address):
```
prev = npx ^ next
     = (prev ^ next) ^ next
     = prev                     # next cancels out
```

At the head: `prev = 0`, so `npx = 0 ^ next = next`.
At the tail: `next = 0`, so `npx = prev ^ 0 = prev`.

### Python Simulation with Dict Registry

Python doesn't expose raw memory addresses for pointer arithmetic. We simulate it:

1. Assign each node an integer ID (its "address").
2. Store `npx = id(prev) ^ id(next)` as a plain integer.
3. Keep a `registry: dict[int, XORNode]` mapping IDs back to node objects.

This preserves the XOR logic exactly while keeping Python's GC happy. The registry
acts as the "address space" -- without it, there's no way to go from an integer ID
back to the actual node object.

### Complexity

| Operation        | Time   | Space (pointer overhead per node) |
|------------------|--------|-----------------------------------|
| Doubly-linked    | O(1) insert/delete | 2 pointers (16 bytes on 64-bit) |
| XOR linked       | O(1) insert/delete | 1 XOR field (8 bytes on 64-bit)  |
| Singly-linked    | O(1) insert, O(n) delete | 1 pointer (8 bytes)        |

XOR linked list gives you doubly-linked capabilities at singly-linked memory cost.

## Practice

See `xor_linked_list.py` for the full implementation with bidirectional traversal.

See `practice.py` for exercises:
1. Reverse XOR list in O(1) time
2. Find the middle element
3. Memory comparison vs standard doubly-linked list
4. Merge two XOR linked lists

## Checkpoint Questions

1. **Why does `npx = prev ^ next` let you recover either neighbor?**
   Because XOR is its own inverse: `npx ^ prev = prev ^ next ^ prev = next`.

2. **Why can't garbage-collected languages use real XOR linked lists?**
   The GC sees `npx` as an integer, not a reference. Nodes have no visible incoming
   references and get collected. Our dict registry is the workaround.

3. **What happens at the head node where there's no previous?**
   `prev = 0`, so `npx = 0 ^ next = next`. Traversal starts with `prev_addr = 0`.

4. **When would you choose this over a standard doubly-linked list?**
   When you have millions of nodes in a memory-constrained environment (embedded,
   kernel) and you need bidirectional traversal. Never in GC'd application code.

5. **Why is O(1) reversal possible?**
   The XOR field is symmetric -- `prev ^ next` is the same regardless of direction.
   Swapping head and tail pointers reverses the logical traversal direction.
