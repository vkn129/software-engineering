"""
Day 10: Stacks -- LIFO and the Call Stack Connection
=====================================================

Two stack implementations (array-based and linked-list-based), performance
comparison, and real-world applications: parenthesis matching, postfix
expression evaluation, and undo/redo simulation.

Run: python stack.py
"""

import time


# ---------------------------------------------------------------------------
# SECTION 1: Array-Based Stack Implementation
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
    cost per operation is O(1). This is the same amortized analysis from
    dynamic arrays (Day 7 if you covered it, or you will soon).
    """

    def __init__(self):
        self._data = []

    def push(self, item):
        """Add item to the top of the stack. O(1) amortized."""
        self._data.append(item)

    def pop(self):
        """Remove and return the top item. O(1).
        Raises IndexError if the stack is empty."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._data.pop()

    def peek(self):
        """Return the top item without removing it. O(1).
        Raises IndexError if the stack is empty."""
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
# SECTION 2: Linked-List-Based Stack Implementation
# ---------------------------------------------------------------------------

class _Node:
    """A single node in the linked stack.

    Each node holds a value and a pointer to the next node below it.
    These are heap-allocated objects scattered in memory -- this is
    why linked stacks have worse cache performance than array stacks.
    """
    __slots__ = ('value', 'next')  # Save memory by not using a dict

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class LinkedStack:
    """Stack built on a singly linked list.

    Every push creates a new node pointing to the current top.
    Every pop removes the top node and returns its value.

    Advantage: guaranteed O(1) for every operation (no amortization).
    Disadvantage: each node is a separate heap allocation. Poor cache
    locality. Higher memory overhead per element (pointer + object header).
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
# SECTION 3: Verify Both Implementations
# ---------------------------------------------------------------------------

print("=" * 65)
print("SECTION 1 & 2: Stack Implementations -- Verification")
print("=" * 65)

for name, StackClass in [("ArrayStack", ArrayStack), ("LinkedStack", LinkedStack)]:
    print(f"\n--- Testing {name} ---")
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


# ---------------------------------------------------------------------------
# SECTION 4: Performance Comparison
# ---------------------------------------------------------------------------

print("\n" + "=" * 65)
print("SECTION 3: Performance -- Array vs. Linked Stack")
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

print("\n  The array-based stack wins because of cache locality.")
print("  Linked list nodes are scattered in memory -- each access may")
print("  miss the CPU cache, costing ~100 nanoseconds per access.")
print("  Array elements are contiguous -- prefetched into cache automatically.")


# ---------------------------------------------------------------------------
# SECTION 5: Application -- Balanced Parentheses
# ---------------------------------------------------------------------------

print("\n" + "=" * 65)
print("SECTION 4: Application -- Balanced Parentheses")
print("=" * 65)

def is_balanced(expression):
    """Check if parentheses, brackets, and braces are properly balanced.

    The algorithm:
    1. For each character in the expression:
       - If it is an opening bracket, push it.
       - If it is a closing bracket, pop and check if it matches.
    2. At the end, the stack must be empty.

    This works because brackets are NESTED -- the most recently opened
    bracket must be closed first. That is LIFO behavior: a stack.
    """
    stack = ArrayStack()
    matching = {')': '(', ']': '[', '}': '{'}
    openers = set('([{')

    for char in expression:
        if char in openers:
            stack.push(char)
        elif char in matching:
            if stack.is_empty():
                return False  # Closing bracket with nothing to match
            if stack.pop() != matching[char]:
                return False  # Mismatched bracket types
    return stack.is_empty()  # True only if all brackets were matched


test_cases = [
    ("()", True),
    ("()[]{}", True),
    ("([])", True),
    ("{[()]}", True),
    ("((()))", True),
    ("(]", False),
    ("([)]", False),
    ("(()", False),
    ("())", False),
    ("", True),
    ("a * (b + c) - [d / {e + f}]", True),
    ("function(arg1, arr[i], obj{key})", True),
    ("if (x > 0) { return arr[x]; }", True),
    ("((missing close paren)", False),
]

print(f"\n  {'Expression':<40} {'Expected':>10} {'Got':>10} {'Pass':>6}")
print("  " + "-" * 70)
for expr, expected in test_cases:
    result = is_balanced(expr)
    status = "OK" if result == expected else "FAIL"
    display = expr if len(expr) <= 38 else expr[:35] + "..."
    print(f"  {display:<40} {str(expected):>10} {str(result):>10} {status:>6}")


# ---------------------------------------------------------------------------
# SECTION 6: Application -- Postfix Expression Evaluation
# ---------------------------------------------------------------------------

print("\n" + "=" * 65)
print("SECTION 5: Application -- Postfix (RPN) Expression Evaluation")
print("=" * 65)

def evaluate_postfix(expression):
    """Evaluate a postfix (Reverse Polish Notation) expression.

    In postfix notation, the operator comes AFTER its operands:
      Infix:   (3 + 4) * 2
      Postfix: 3 4 + 2 *

    Algorithm:
    1. Read tokens left to right.
    2. If it is a number, push it.
    3. If it is an operator, pop two numbers, apply the operator, push the result.
    4. At the end, the stack has one item: the answer.

    Why postfix? No parentheses needed. No operator precedence rules.
    The stack handles everything. This is why HP calculators used RPN,
    and why most virtual machines (JVM, Python VM) use stack-based evaluation.
    """
    stack = ArrayStack()
    tokens = expression.split()

    for token in tokens:
        if token in '+-*/':
            # Pop two operands (note: order matters for - and /)
            b = stack.pop()  # Second operand (pushed later, so on top)
            a = stack.pop()  # First operand
            if token == '+':
                stack.push(a + b)
            elif token == '-':
                stack.push(a - b)
            elif token == '*':
                stack.push(a * b)
            elif token == '/':
                stack.push(a / b)
        else:
            stack.push(float(token))

    return stack.pop()


postfix_tests = [
    ("3 4 +", 7.0, "3 + 4"),
    ("3 4 + 2 *", 14.0, "(3 + 4) * 2"),
    ("5 1 2 + 4 * + 3 -", 14.0, "5 + ((1 + 2) * 4) - 3"),
    ("2 3 * 4 5 * +", 26.0, "(2 * 3) + (4 * 5)"),
    ("10 2 /", 5.0, "10 / 2"),
    ("4 2 + 3 5 1 - * +", 18.0, "(4 + 2) + (3 * (5 - 1))"),
]

print(f"\n  {'Postfix':<25} {'Infix':<25} {'Expected':>10} {'Got':>10}")
print("  " + "-" * 75)
for postfix, expected, infix in postfix_tests:
    result = evaluate_postfix(postfix)
    status = "OK" if abs(result - expected) < 1e-9 else "FAIL"
    print(f"  {postfix:<25} {infix:<25} {expected:>10.1f} {result:>10.1f}  {status}")


# ---------------------------------------------------------------------------
# SECTION 7: Application -- Undo/Redo System
# ---------------------------------------------------------------------------

print("\n" + "=" * 65)
print("SECTION 6: Application -- Undo/Redo System")
print("=" * 65)

class TextEditor:
    """Simple text editor demonstrating undo/redo with two stacks.

    The undo stack records every action. When you undo, the action
    moves from the undo stack to the redo stack. When you redo, it
    moves back. When you perform a new action after undoing, the
    redo stack is cleared -- those undone actions are gone forever.

    This is exactly how Ctrl+Z / Ctrl+Y works in every text editor.
    """

    def __init__(self):
        self.text = ""
        self._undo_stack = ArrayStack()
        self._redo_stack = ArrayStack()

    def type_text(self, new_text):
        """Type new text (append to current text)."""
        self._undo_stack.push(('insert', len(new_text), self.text))
        self.text += new_text
        # New action invalidates redo history
        self._redo_stack = ArrayStack()

    def delete(self, count):
        """Delete the last 'count' characters."""
        if count > len(self.text):
            count = len(self.text)
        deleted = self.text[-count:]
        self._undo_stack.push(('delete', deleted, self.text))
        self.text = self.text[:-count]
        self._redo_stack = ArrayStack()

    def undo(self):
        """Undo the last action."""
        if self._undo_stack.is_empty():
            print("    Nothing to undo!")
            return
        action = self._undo_stack.pop()
        self._redo_stack.push(('redo', self.text))
        self.text = action[2] if len(action) > 2 else action[1]

    def redo(self):
        """Redo the last undone action."""
        if self._redo_stack.is_empty():
            print("    Nothing to redo!")
            return
        action = self._redo_stack.pop()
        self._undo_stack.push(('undo_redo', self.text))
        self.text = action[1]

    def show(self, label=""):
        """Display current text state."""
        undo_count = len(self._undo_stack)
        redo_count = len(self._redo_stack)
        print(f"    {label:<20} text=\"{self.text}\"  "
              f"(undo={undo_count}, redo={redo_count})")


# Demonstrate the undo/redo system
print("\n  Simulating a text editor session:\n")
editor = TextEditor()
editor.show("Initial")

editor.type_text("Hello")
editor.show("Type 'Hello'")

editor.type_text(" World")
editor.show("Type ' World'")

editor.type_text("!")
editor.show("Type '!'")

editor.undo()
editor.show("Undo (remove '!')")

editor.undo()
editor.show("Undo (remove ' World')")

editor.redo()
editor.show("Redo (restore ' World')")

editor.type_text("?")
editor.show("Type '?' (clears redo)")

editor.redo()
editor.show("Try redo (nothing!)")


# ---------------------------------------------------------------------------
# SECTION 8: The Call Stack Connection
# ---------------------------------------------------------------------------

print("\n" + "=" * 65)
print("SECTION 7: The Call Stack -- Recursion IS a Stack")
print("=" * 65)

def factorial_recursive(n):
    """Classic recursive factorial. Each call pushes a frame on the call stack."""
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

def factorial_iterative_stack(n):
    """Same computation, but using an explicit stack instead of recursion.

    This proves that recursion and explicit stacks are equivalent.
    Any recursive algorithm can be converted to an iterative one with a stack.
    """
    stack = ArrayStack()
    # Push all the multiplications we need to do
    for i in range(n, 1, -1):
        stack.push(i)

    # Pop and multiply
    result = 1
    while not stack.is_empty():
        result *= stack.pop()
    return result

print("\n  Comparing recursive vs. explicit stack factorial:\n")
for n in [1, 5, 10, 15, 20]:
    rec = factorial_recursive(n)
    itr = factorial_iterative_stack(n)
    match = "OK" if rec == itr else "MISMATCH"
    print(f"    {n}! = {rec:<25,} (recursive={rec}, stack={itr})  {match}")

print("\n  Key insight: the CPU's call stack IS a stack data structure.")
print("  Recursion uses it implicitly. We can always make it explicit.")
print("  The iterative version avoids stack overflow for deep recursion.")


# ---------------------------------------------------------------------------
# SECTION 9: Min-Stack (O(1) minimum retrieval)
# ---------------------------------------------------------------------------

print("\n" + "=" * 65)
print("SECTION 8: Min-Stack -- O(1) Minimum Retrieval")
print("=" * 65)

class MinStack:
    """A stack that also supports O(1) get_min().

    The trick: maintain a second stack that tracks the current minimum.
    When you push a value <= current min, push it onto the min stack too.
    When you pop the current min, pop from the min stack too.

    This uses O(n) extra space in the worst case (all descending values)
    but O(1) extra space in the best case (all ascending values).
    """

    def __init__(self):
        self._data = ArrayStack()
        self._mins = ArrayStack()

    def push(self, val):
        self._data.push(val)
        if self._mins.is_empty() or val <= self._mins.peek():
            self._mins.push(val)

    def pop(self):
        val = self._data.pop()
        if val == self._mins.peek():
            self._mins.pop()
        return val

    def get_min(self):
        """Return the minimum element in O(1)."""
        return self._mins.peek()

    def peek(self):
        return self._data.peek()


print("\n  Demonstrating MinStack:\n")
ms = MinStack()
operations = [
    ("push(5)", lambda: ms.push(5)),
    ("push(3)", lambda: ms.push(3)),
    ("push(7)", lambda: ms.push(7)),
    ("push(1)", lambda: ms.push(1)),
    ("push(4)", lambda: ms.push(4)),
    ("pop()", lambda: ms.pop()),
    ("pop()", lambda: ms.pop()),
]

for label, op in operations:
    result = op()
    pop_msg = f" -> {result}" if "pop" in label else ""
    print(f"    {label}{pop_msg:<10}  min = {ms.get_min()}")

print("\n  The min stack tracks minimums. O(1) to get the current min")
print("  at any point -- no scanning required.")


print("\n" + "=" * 65)
print("Done! Study the output, then work through practice.py")
print("=" * 65)
