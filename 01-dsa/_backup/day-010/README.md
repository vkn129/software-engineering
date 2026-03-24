# Day 10: Stacks -- LIFO and the Call Stack Connection

## Why This Exists

The stack is the first *abstract data type* you are building -- a concept that exists independent of any particular implementation. A stack says: "Last In, First Out." You can push items on and pop items off the top, and that is it. No peeking at the middle, no removing from the bottom. This constraint is not a limitation -- it is the *point*. By restricting operations, you get guarantees that make certain problems trivial.

You already use a stack every time you call a function. On Day 2, you learned about the call stack: each function call pushes a frame, each return pops one. The CPU literally has a stack pointer register (RSP on x86-64) that tracks where the top of the stack is in memory. If this stack overflows -- usually from unbounded recursion -- your program crashes with a "stack overflow." The name of the most famous programming website is a reference to a bug.

Stacks appear everywhere. Your text editor's undo/redo is a stack (two stacks, actually). The browser's back button is a stack. Expression parsing in compilers uses stacks. Depth-first search uses a stack (explicitly, or implicitly via recursion). Syntax validation (matching parentheses, HTML tags) is a stack problem. The JVM, Python VM, and most interpreted languages are *stack machines* -- they evaluate expressions by pushing and popping an operand stack.

The implementation choice matters too. You can build a stack on an array or a linked list. The array-based approach wins in practice because of cache locality -- accessing sequential memory addresses is dramatically faster on modern hardware due to CPU cache prefetching. This is physics dictating data structure choice.

## Theory (40 min)

### 1. The Stack ADT (Abstract Data Type)

An abstract data type specifies *what* operations are supported, not *how* they are implemented.

```
Stack operations:
  push(item)  -- add item to the top      O(1) amortized
  pop()       -- remove and return top     O(1)
  peek()      -- return top without removing  O(1)
  is_empty()  -- check if stack has items  O(1)
  size()      -- number of items           O(1)
```

The key invariant: the last item pushed is the first item popped (LIFO).

### 2. Array-Based Implementation

Use a Python list (dynamic array) as the backing store. The "top" of the stack is the end of the list.

```python
class Stack:
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)    # amortized O(1)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()    # O(1)

    def peek(self):
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._data[-1]      # O(1)

    def is_empty(self):
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)
```

Why this works well: `list.append()` and `list.pop()` (from the end) are O(1) amortized. Memory is contiguous, so the CPU cache prefetcher keeps the hot end of the stack in L1 cache. This is typically 100x faster than chasing pointers through a linked list.

### 3. Linked List Implementation

Each node points to the one below it. Push adds a new head; pop removes the head.

```python
class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node

class LinkedStack:
    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, item):
        self._top = Node(item, self._top)
        self._size += 1

    def pop(self):
        value = self._top.value
        self._top = self._top.next
        self._size -= 1
        return value
```

Every operation is O(1) -- not amortized, truly O(1). But each node is a separate heap allocation, scattered in memory. Cache misses make this slower in practice despite the same theoretical complexity. This is the gap between theory and physics.

### 4. Why Array-Based Usually Wins

On modern CPUs:
- L1 cache access: ~1 nanosecond
- Main memory access: ~100 nanoseconds (100x slower)

Array elements are contiguous in memory. When you access `data[i]`, the CPU loads an entire cache line (64 bytes), so `data[i+1]` through `data[i+15]` (for 4-byte ints) are already in cache. Linked list nodes are scattered on the heap -- each access is a potential cache miss.

The only scenario where a linked list stack wins: when you need guaranteed O(1) worst-case (no amortized resizing pauses), such as in real-time systems.

### 5. The CPU Hardware Stack

The CPU itself has a stack built into its architecture:

```
High memory
┌──────────────┐
│  main() vars │  <-- stack grows DOWNWARD
├──────────────┤
│  return addr │
│  func_a vars │
├──────────────┤
│  return addr │
│  func_b vars │
├──────────────┤
│              │  <-- RSP (stack pointer) points here
│   (free)     │
└──────────────┘
Low memory
```

The `PUSH` instruction decrements RSP and writes data. `POP` reads data and increments RSP. Function calls use `CALL` (push return address, jump to function) and `RET` (pop return address, jump back). This is why stack overflow crashes your program -- the stack grows into memory it does not own.

### 6. Classic Stack Applications

**Parenthesis matching**: Push opening brackets, pop on closing brackets. If the popped bracket matches, continue. If the stack is empty when you try to pop, or non-empty when you finish, the expression is invalid.

**Expression evaluation** (postfix/RPN): Push numbers. When you see an operator, pop two numbers, apply the operator, push the result. Calculators like HP's used this.

**Undo/Redo**: Main stack holds undo history. When you undo, pop from undo stack and push to redo stack. When you redo, reverse the process.

**DFS (Depth-First Search)**: Push the starting node. Pop a node, push all its unvisited neighbors. This is literally what recursion does with the call stack -- explicit stack DFS is the iterative equivalent.

## Practice (20 min)

Work through `practice.py`. Implement stack-based solutions to classic problems: balanced parentheses, postfix evaluation, and more. The tests verify correctness.

## Daily Project

Run `stack.py` to see both stack implementations in action, with performance comparisons between array-based and linked-list-based stacks. The script also demonstrates real applications: parenthesis matching, postfix expression evaluation, and undo/redo simulation.

## Checkpoint Questions

1. Why does the hardware stack grow downward (from high addresses to low) on most architectures? What historical design decision led to this, and what would break if it grew upward?

2. You have a stack and need to access the item at the bottom without removing anything. What is the time complexity, and why does this violate the stack abstraction? How would you solve it?

3. Explain why `list.pop(0)` in Python is O(n) but `list.pop()` (no argument) is O(1). What does this mean for using a list as a queue vs. a stack?

4. A recursive DFS and an iterative DFS using an explicit stack are logically equivalent. Under what circumstances would you prefer the iterative version, and what practical problem does it avoid?

5. Your undo system uses a stack. The user performs 10 actions, undoes 3, then performs a new action. What happens to the 3 undone actions? Why is this the correct behavior?
