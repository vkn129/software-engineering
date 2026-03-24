# Day 29: Stacks -- LIFO and the Call Stack Connection

## Why This Exists

The stack is everywhere in computing, hiding in plain sight. Every function call you make pushes a frame onto the **call stack**. Every time you press Ctrl+Z, you pop from an **undo stack**. Every time your compiler checks that your parentheses match, it uses a stack. The stack is not just a data structure -- it is a fundamental computation pattern.

Understanding stacks means understanding:
- **Why recursion works** (and why it can crash with stack overflow)
- **Why compilers can parse nested expressions** (balanced delimiters)
- **Why undo/redo needs exactly two stacks** (and what happens to redo history on new input)
- **Why RPN calculators and bytecode VMs are stack machines**

If you cannot explain what a stack frame contains and why the hardware stack grows downward, you do not yet understand how your programs execute.

## Theory

### 1. LIFO: The Core Constraint

A stack enforces **Last In, First Out**. You can only interact with the top element. This is not a limitation -- it is a *guarantee*. By restricting access, you get predictable behavior that makes entire classes of problems trivial.

```
Operations:
  push(item)   -- add to top        O(1) amortized (array) / O(1) worst-case (linked)
  pop()        -- remove from top    O(1)
  peek()       -- view top           O(1)
  is_empty()   -- check emptiness    O(1)
  size()       -- element count      O(1)
```

### 2. Array-Backed vs. Linked-List-Backed

**Array-backed** (Python list): The top of the stack is the end of a contiguous memory block. `append()` and `pop()` are O(1) amortized. Occasionally `append` triggers a resize (copy entire array), but Python grows by ~1.125x, making resizes rare. Cache locality is excellent -- the CPU prefetcher loads neighboring addresses automatically, so sequential access is fast.

**Linked-list-backed**: Each node is a separate heap allocation pointing to the one below. Every operation is O(1) *worst-case* (no amortization). But each node is scattered in memory -- every access is a potential cache miss (~100ns vs ~1ns for L1 cache). Higher memory overhead per element (pointer + object header).

**Which wins?** Array-backed, almost always. The only exception: real-time systems where you need guaranteed O(1) worst-case (no amortized resize pauses).

### 3. Amortized O(1) -- What It Really Means

When Python's list runs out of capacity, it allocates a new, larger array and copies everything -- an O(n) operation. But this happens so rarely (every ~8 pushes due to the 1.125x growth factor) that if you average the cost across all operations, each push costs O(1) on average. This is **amortized analysis**: the occasional expensive operation is "paid for" by the many cheap ones.

### 4. The Call Stack and Stack Frames

When you call a function, the CPU pushes a **stack frame** containing:
- The return address (where to resume after the function returns)
- The function's local variables
- The arguments passed to the function

```
High memory
+------------------+
|  main() frame    |   <-- stack grows DOWNWARD on most architectures
+------------------+
|  return address  |
|  func_a() frame  |
+------------------+
|  return address  |
|  func_b() frame  |
+------------------+
|                  |   <-- RSP (stack pointer register) points here
|   (free space)   |
+------------------+
Low memory
```

The x86-64 `CALL` instruction pushes the return address and jumps. `RET` pops the return address and jumps back. The stack pointer register (RSP) tracks the current top.

### 5. Stack Overflow

The OS allocates a fixed amount of memory for the call stack (typically 1-8 MB). If recursion goes too deep -- or you allocate huge local variables -- the stack grows past its limit and the OS kills your process. This is a **stack overflow**. Python adds its own recursion limit (default 1000) to catch this before the OS does.

### 6. Balanced Parentheses -- The Canonical Stack Problem

Brackets are *nested*: the most recently opened bracket must close first. That is LIFO. Push opening brackets, pop on closing brackets, check they match. If the stack is non-empty at the end, something was never closed.

## Practice

Work through `practice.py`. Five exercises covering min-stack, reverse Polish notation evaluation, infix-to-postfix conversion, browser history simulation, and string decoding. Each has a TODO stub and a solution function.

## Checkpoint Questions

1. **Call stack**: What exactly is stored in a stack frame? Why does the hardware stack grow downward on x86? What historical design decision caused this?

2. **Amortized analysis**: If you push 1000 items onto an array-backed stack, roughly how many total element copies happen due to resizing? Why is the amortized cost still O(1)?

3. **Stack overflow**: Python's default recursion limit is 1000. If you increase it to 1,000,000 and recurse that deep, what happens at the OS level? Why does Python have a software limit at all?

4. **Array vs. linked**: A linked-list stack has O(1) worst-case for every operation. An array stack has O(1) amortized. In what specific real-world scenario would you choose the linked-list version despite worse cache performance?

5. **Balanced parentheses**: Can you solve balanced parentheses without a stack, using only a counter? For which cases does a counter work, and for which does it fail? What does this tell you about when you truly need a stack?
