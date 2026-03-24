"""
Day 29: Stacks -- LIFO and the Call Stack Connection
=====================================================

Two stack implementations (array-based and linked-list-based), balanced
parentheses checker, and call stack simulation.

Run: python stack.py
"""

import time


# ---------------------------------------------------------------------------
# ArrayStack -- backed by a Python list (dynamic array)
# ---------------------------------------------------------------------------

class ArrayStack:
    """Stack built on a Python list (dynamic array).

    Why arrays? Cache locality. The top of the stack lives at the end of a
    contiguous memory block. The CPU's cache prefetcher loads neighboring
    memory automatically, so sequential access is fast. Push and pop operate
    on the end of the list -- O(1) amortized.

    The 'amortized' matters: occasionally, append() triggers a resize (copy
    the entire array to a bigger one), which is O(n). But Python grows the
    array by ~1.125x each time, so resizes are rare enough that the average
    cost per operation is O(1).
    """

    def __init__(self):
        self._data = []

    def push(self, item):
        """Add item to the top of the stack. O(1) amortized."""
        self._data.append(item)

    def pop(self):
        """Remove and return the top item. O(1).
        Raises IndexError if the stack is empty -- popping nothing is a bug,
        not a valid operation."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        """Return the top item without removing it. O(1)."""
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._data[-1]

    def is_empty(self):
        """Check if the stack has no items. O(1)."""
        return len(self._data) == 0

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"ArrayStack({self._data})"


# ---------------------------------------------------------------------------
# LinkedStack -- backed by a singly linked list
# ---------------------------------------------------------------------------

class _Node:
    """A single node in the linked stack.

    Each node holds a value and a pointer to the next node below it.
    These are heap-allocated objects scattered in memory -- this is
    why linked stacks have worse cache performance than array stacks.
    """
    __slots__ = ('value', 'next')  # Avoid per-instance __dict__ overhead

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class LinkedStack:
    """Stack built on a singly linked list.

    Every push creates a new node pointing to the current top.
    Every pop removes the top node and returns its value.

    Advantage: guaranteed O(1) for every operation -- no amortization,
    no surprise O(n) resize.
    Disadvantage: each node is a separate heap allocation with poor cache
    locality and higher per-element memory overhead (pointer + object header).
    """

    def __init__(self):
        self._top = None
        self._size = 0

    def push(self, item):
        """Add item to the top. O(1) worst-case."""
        self._top = _Node(item, self._top)
        self._size += 1

    def pop(self):
        """Remove and return the top item. O(1) worst-case."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        value = self._top.value
        self._top = self._top.next
        self._size -= 1
        return value

    def peek(self):
        """Return the top item without removing it. O(1)."""
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._top.value

    def is_empty(self):
        """Check if the stack has no items. O(1)."""
        return self._top is None

    def __len__(self):
        return self._size

    def __repr__(self):
        items = []
        node = self._top
        while node:
            items.append(repr(node.value))
            node = node.next
        return f"LinkedStack([{', '.join(items)}])"


# ---------------------------------------------------------------------------
# balanced_parentheses -- the canonical stack problem
# ---------------------------------------------------------------------------

def balanced_parentheses(expression):
    """Check if parentheses, brackets, and braces are properly balanced.

    Why a stack? Brackets are NESTED -- the most recently opened bracket
    must close first. That is LIFO behavior. A simple counter would work
    for a single bracket type, but with multiple types you need to remember
    WHICH opener to match, and in what order. Only a stack tracks that.
    """
    stack = ArrayStack()
    # Map each closer to its expected opener
    matching = {')': '(', ']': '[', '}': '{'}
    openers = set('([{')

    for char in expression:
        if char in openers:
            stack.push(char)
        elif char in matching:
            if stack.is_empty():
                return False  # Closer with no opener -- unbalanced
            if stack.pop() != matching[char]:
                return False  # Wrong type of opener -- mismatched
    # If the stack is non-empty, some openers were never closed
    return stack.is_empty()


# ---------------------------------------------------------------------------
# simulate_call_stack -- show what the CPU does on function calls
# ---------------------------------------------------------------------------

def simulate_call_stack(func_calls):
    """Simulate how the CPU call stack works during nested function calls.

    Takes a list of ('call', name) and ('return', name) tuples and shows
    the stack state after each operation. This is exactly what happens at
    the hardware level: CALL pushes a frame, RET pops it.

    Args:
        func_calls: list of tuples like [('call', 'main'), ('call', 'foo'),
                     ('return', 'foo'), ('return', 'main')]

    Returns:
        list of (operation, stack_snapshot) tuples for inspection.
    """
    stack = ArrayStack()
    trace = []

    for action, name in func_calls:
        if action == 'call':
            # CPU pushes return address + frame onto the stack
            frame = {
                'function': name,
                'return_addr': f'<after {name}()>',
                'locals': {},
            }
            stack.push(frame)
            snapshot = []
            # Walk the internal data to show full stack state
            for i in range(len(stack._data) - 1, -1, -1):
                snapshot.append(stack._data[i]['function'])
            trace.append((f"CALL {name}()", snapshot))

        elif action == 'return':
            if stack.is_empty():
                trace.append((f"RETURN {name}() -- ERROR: stack empty!", []))
                continue
            frame = stack.pop()
            if frame['function'] != name:
                trace.append((
                    f"RETURN {name}() -- ERROR: top was {frame['function']}!",
                    []
                ))
                continue
            snapshot = []
            for i in range(len(stack._data) - 1, -1, -1):
                snapshot.append(stack._data[i]['function'])
            trace.append((f"RETURN {name}() -> resume at {frame['return_addr']}", snapshot))

    return trace


# ===========================================================================
# __main__ -- demonstrate everything
# ===========================================================================

if __name__ == '__main__':

    # --- Verify both implementations ---
    print("=" * 65)
    print("SECTION 1: Stack Implementations -- Verification")
    print("=" * 65)

    for name, StackClass in [("ArrayStack", ArrayStack), ("LinkedStack", LinkedStack)]:
        print(f"\n--- {name} ---")
        s = StackClass()
        print(f"  Empty: {s.is_empty()}")

        for val in [10, 20, 30, 40]:
            s.push(val)
        print(f"  After pushing 10, 20, 30, 40: {s}")
        print(f"  Peek: {s.peek()}")
        print(f"  Size: {len(s)}")

        popped = []
        while not s.is_empty():
            popped.append(s.pop())
        print(f"  Pop order: {popped}")
        print(f"  LIFO confirmed: {popped == [40, 30, 20, 10]}")

    # --- Performance comparison ---
    print("\n" + "=" * 65)
    print("SECTION 2: Performance -- Array vs. Linked Stack")
    print("=" * 65)

    def benchmark_stack(StackClass, n):
        """Push n items then pop all. Return total time."""
        s = StackClass()
        start = time.perf_counter()
        for i in range(n):
            s.push(i)
        for i in range(n):
            s.pop()
        return time.perf_counter() - start

    sizes = [10_000, 100_000, 1_000_000]
    print(f"\n  {'N':>12} {'ArrayStack':>14} {'LinkedStack':>14} {'Ratio':>10}")
    print("  " + "-" * 55)

    for n in sizes:
        t_array = benchmark_stack(ArrayStack, n)
        t_linked = benchmark_stack(LinkedStack, n)
        ratio = t_linked / t_array if t_array > 0 else float('inf')
        print(f"  {n:>12,} {t_array:>13.4f}s {t_linked:>13.4f}s {ratio:>9.1f}x")

    print("\n  Array wins because of cache locality: contiguous memory means")
    print("  the CPU prefetcher keeps the hot end in L1 cache (~1ns access).")
    print("  Linked list nodes are scattered -- each access risks a cache")
    print("  miss (~100ns). Same big-O, 100x real-world difference.")

    # --- Balanced parentheses ---
    print("\n" + "=" * 65)
    print("SECTION 3: Balanced Parentheses")
    print("=" * 65)

    paren_tests = [
        ("()", True),
        ("()[]{}", True),
        ("{[()]}", True),
        ("(]", False),
        ("([)]", False),
        ("(()", False),
        ("", True),
        ("a * (b + c) - [d / {e + f}]", True),
    ]

    print(f"\n  {'Expression':<35} {'Expected':>8} {'Got':>8} {'Pass':>6}")
    print("  " + "-" * 60)
    for expr, expected in paren_tests:
        result = balanced_parentheses(expr)
        status = "OK" if result == expected else "FAIL"
        print(f"  {expr:<35} {str(expected):>8} {str(result):>8} {status:>6}")

    # --- Call stack simulation ---
    print("\n" + "=" * 65)
    print("SECTION 4: Call Stack Simulation")
    print("=" * 65)

    # Simulate: main() calls foo(), foo() calls bar(), bar returns,
    # foo returns, main calls baz(), baz returns, main returns.
    calls = [
        ('call', 'main'),
        ('call', 'foo'),
        ('call', 'bar'),
        ('return', 'bar'),
        ('return', 'foo'),
        ('call', 'baz'),
        ('return', 'baz'),
        ('return', 'main'),
    ]

    trace = simulate_call_stack(calls)
    print()
    for operation, stack_state in trace:
        frames = " -> ".join(stack_state) if stack_state else "(empty)"
        print(f"  {operation:<50} stack: [{frames}]")

    print("\n  Each CALL pushes a frame (return address + locals).")
    print("  Each RETURN pops the frame and jumps to the saved return address.")
    print("  Stack overflow = too many frames, stack grows past its memory limit.")

    print("\n" + "=" * 65)
    print("Done! Now work through practice.py for hands-on exercises.")
    print("=" * 65)
