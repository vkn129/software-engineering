"""
Day 29: Stack Practice Exercises
=================================

Five exercises that apply stacks to real problems. Each has:
  - A TODO stub for you to implement
  - A _sol_ solution to check against
  - Tests in run_tests()

Run: python practice.py

No external libraries. Comments explain WHY, not what.
"""


# ---------------------------------------------------------------------------
# Exercise 1: Min-Stack with O(1) getMin
# ---------------------------------------------------------------------------
# WHY: A regular stack gives you the top element in O(1), but the minimum
# requires scanning all elements -- O(n). The trick: maintain a parallel
# stack that tracks the running minimum. When you push a value <= current
# min, push it onto the min stack too. When you pop the current min, pop
# from the min stack too. Space trade-off: O(n) extra space worst case,
# but O(1) time for get_min.

class MinStack:
    """Stack that supports push, pop, peek, and get_min -- all in O(1)."""

    def __init__(self):
        # TODO: initialize two internal stacks (use plain lists)
        pass

    def push(self, val):
        # TODO: push val onto main stack
        # Also push onto min stack if val <= current min (or min stack empty)
        pass

    def pop(self):
        # TODO: pop from main stack
        # If popped value equals min stack top, pop min stack too
        pass

    def peek(self):
        # TODO: return top of main stack without removing
        pass

    def get_min(self):
        # TODO: return current minimum in O(1)
        pass


class _sol_MinStack:
    """Solution: two-stack approach for O(1) min tracking."""

    def __init__(self):
        self._data = []
        self._mins = []  # Parallel stack: tracks running minimum

    def push(self, val):
        self._data.append(val)
        # Push onto mins if it is a new minimum (or equal -- handles duplicates)
        if not self._mins or val <= self._mins[-1]:
            self._mins.append(val)

    def pop(self):
        val = self._data.pop()
        # If we are removing the current minimum, update the min stack
        if val == self._mins[-1]:
            self._mins.pop()
        return val

    def peek(self):
        return self._data[-1]

    def get_min(self):
        return self._mins[-1]


# ---------------------------------------------------------------------------
# Exercise 2: Evaluate Reverse Polish Notation (Postfix)
# ---------------------------------------------------------------------------
# WHY: Postfix notation removes all ambiguity about operator precedence and
# associativity. No parentheses needed. This is why stack-based VMs (JVM,
# Python bytecode, WebAssembly) evaluate expressions this way -- it maps
# directly to push/pop operations. HP calculators used RPN for the same reason.

def eval_rpn(tokens):
    """Evaluate a list of tokens in Reverse Polish Notation.

    tokens: list of strings, e.g. ["2", "1", "+", "3", "*"]
    Returns: integer result

    Rules:
    - Numbers get pushed onto the stack.
    - Operators (+, -, *, /) pop two operands, compute, push result.
    - Division truncates toward zero (like int(a/b) in Python 3).
    """
    # TODO: implement using a stack (plain list)
    pass


def _sol_eval_rpn(tokens):
    """Solution: classic stack-based RPN evaluator."""
    stack = []
    for token in tokens:
        if token in '+-*/':
            b = stack.pop()  # Second operand is on top (pushed last)
            a = stack.pop()  # First operand is below
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                # Truncate toward zero, not toward negative infinity
                # int() truncates; // floors (different for negatives)
                stack.append(int(a / b))
        else:
            stack.append(int(token))
    return stack.pop()


# ---------------------------------------------------------------------------
# Exercise 3: Infix to Postfix (Shunting-Yard Algorithm)
# ---------------------------------------------------------------------------
# WHY: Compilers cannot evaluate infix expressions directly because of
# precedence and associativity rules. Dijkstra's shunting-yard algorithm
# converts infix to postfix using a stack, respecting precedence. The
# postfix output can then be evaluated trivially with Exercise 2's approach.
# This is how real expression parsers work.

def infix_to_postfix(expression):
    """Convert an infix expression string to a postfix token list.

    expression: string like "3 + 4 * 2" (tokens separated by spaces)
    Returns: list of strings in postfix order, e.g. ["3", "4", "2", "*", "+"]

    Supports: +, -, *, /, parentheses (). All operators are left-associative.
    Precedence: * and / are higher than + and -.
    """
    # TODO: implement using the shunting-yard algorithm
    # Hint: use an operator stack. For each token:
    #   - number -> output directly
    #   - operator -> pop higher/equal precedence ops from stack to output, then push
    #   - '(' -> push to stack
    #   - ')' -> pop to output until '(' is found
    pass


def _sol_infix_to_postfix(expression):
    """Solution: Dijkstra's shunting-yard algorithm."""
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    output = []
    op_stack = []
    tokens = expression.split()

    for token in tokens:
        if token in precedence:
            # Pop operators with >= precedence (left-associative)
            # This ensures higher-precedence ops execute first in postfix
            while (op_stack and op_stack[-1] != '(' and
                   op_stack[-1] in precedence and
                   precedence[op_stack[-1]] >= precedence[token]):
                output.append(op_stack.pop())
            op_stack.append(token)
        elif token == '(':
            op_stack.append(token)
        elif token == ')':
            # Pop until matching '(' -- parentheses override precedence
            while op_stack and op_stack[-1] != '(':
                output.append(op_stack.pop())
            op_stack.pop()  # Remove the '(' itself
        else:
            # Operand (number) goes directly to output
            output.append(token)

    # Flush remaining operators
    while op_stack:
        output.append(op_stack.pop())

    return output


# ---------------------------------------------------------------------------
# Exercise 4: Browser Back/Forward with Two Stacks
# ---------------------------------------------------------------------------
# WHY: Browser navigation is the undo/redo pattern applied to URLs. The
# back stack holds pages you have visited. Going back pushes the current
# page onto the forward stack. Going forward reverses it. Visiting a NEW
# page clears the forward stack -- you cannot go forward to a page that
# no longer exists in your navigation path. Two stacks, same LIFO principle.

class BrowserHistory:
    """Simulate browser back/forward navigation using two stacks.

    visit(url)  -- navigate to a new URL (clears forward history)
    back()      -- go back one page (if possible), return current URL
    forward()   -- go forward one page (if possible), return current URL
    current()   -- return the current URL
    """

    def __init__(self, homepage):
        # TODO: store current page and initialize back/forward stacks
        pass

    def visit(self, url):
        # TODO: push current page onto back stack, set new current page
        # Clear forward stack -- navigating to a new page invalidates forward history
        pass

    def back(self):
        # TODO: if back stack is not empty, push current to forward, pop back to current
        # Return current URL
        pass

    def forward(self):
        # TODO: if forward stack is not empty, push current to back, pop forward to current
        # Return current URL
        pass

    def current(self):
        # TODO: return current URL
        pass


class _sol_BrowserHistory:
    """Solution: two-stack browser navigation."""

    def __init__(self, homepage):
        self._current = homepage
        self._back_stack = []
        self._forward_stack = []

    def visit(self, url):
        self._back_stack.append(self._current)
        self._current = url
        # Forward history becomes invalid -- you took a new path
        self._forward_stack.clear()

    def back(self):
        if self._back_stack:
            self._forward_stack.append(self._current)
            self._current = self._back_stack.pop()
        return self._current

    def forward(self):
        if self._forward_stack:
            self._back_stack.append(self._current)
            self._current = self._forward_stack.pop()
        return self._current

    def current(self):
        return self._current


# ---------------------------------------------------------------------------
# Exercise 5: Decode String "3[a2[bc]]"
# ---------------------------------------------------------------------------
# WHY: This is a nested structure problem -- the inner brackets must resolve
# before the outer ones. That is LIFO: when you encounter '[', you push
# context. When you encounter ']', you pop context and expand. Compilers
# handle nested scopes the same way. This pattern appears in data compression
# (run-length encoding variants) and template expansion.

def decode_string(s):
    """Decode an encoded string like "3[a2[bc]]" -> "abcbcabcbcabcbc".

    Rules:
    - k[encoded] means repeat 'encoded' exactly k times.
    - k is a positive integer.
    - Brackets can be nested: resolve inner brackets first.
    - Input is always valid (balanced brackets, valid numbers).

    Examples:
      "3[a]"       -> "aaa"
      "3[a2[c]]"   -> "accaccacc"
      "2[abc]3[cd]" -> "abcabccdcdcd"
    """
    # TODO: implement using a stack
    # Hint: when you see '[', push the current string and current number
    # onto the stack. When you see ']', pop and repeat.
    pass


def _sol_decode_string(s):
    """Solution: stack-based nested decoding."""
    stack = []          # Each entry: (string_so_far, repeat_count)
    current_str = ""    # What we are building at the current nesting level
    current_num = 0     # The multiplier for the next bracket group

    for ch in s:
        if ch.isdigit():
            # Build multi-digit numbers (e.g., "12" -> 12)
            current_num = current_num * 10 + int(ch)
        elif ch == '[':
            # Save current context before entering a new nesting level
            # This is exactly what CALL does on the hardware stack
            stack.append((current_str, current_num))
            current_str = ""
            current_num = 0
        elif ch == ']':
            # Pop the outer context -- like RETURN restoring a stack frame
            prev_str, repeat_count = stack.pop()
            current_str = prev_str + current_str * repeat_count
        else:
            # Regular character -- accumulate into current string
            current_str += ch

    return current_str


# ===========================================================================
# Tests
# ===========================================================================

def run_tests():
    """Run all exercise tests. Tries your implementation first, falls back
    to the solution if yours returns None (not yet implemented)."""

    passed = 0
    failed = 0
    total = 0

    def check(label, got, expected):
        nonlocal passed, failed, total
        total += 1
        if got == expected:
            passed += 1
            print(f"  PASS  {label}")
        else:
            failed += 1
            print(f"  FAIL  {label}")
            print(f"        expected: {expected}")
            print(f"        got:      {got}")

    # --- Exercise 1: MinStack ---
    print("\n--- Exercise 1: MinStack ---")
    for label, MSClass in [("yours", MinStack), ("solution", _sol_MinStack)]:
        ms = MSClass()
        ms.push(5)
        ms.push(3)
        ms.push(7)
        ms.push(1)
        # If get_min returns None, the class is not implemented yet
        if ms.get_min() is None and label == "yours":
            print("  (not implemented, testing solution)")
            continue
        check(f"[{label}] min after push 5,3,7,1", ms.get_min(), 1)
        ms.pop()  # remove 1
        check(f"[{label}] min after pop(1)", ms.get_min(), 3)
        ms.pop()  # remove 7
        check(f"[{label}] min after pop(7)", ms.get_min(), 3)
        ms.push(2)
        check(f"[{label}] min after push(2)", ms.get_min(), 2)
        if label == "yours":
            break  # Only test solution as fallback

    # --- Exercise 2: Evaluate RPN ---
    print("\n--- Exercise 2: Evaluate RPN ---")
    rpn_cases = [
        (["2", "1", "+", "3", "*"], 9),
        (["4", "13", "5", "/", "+"], 6),
        (["10", "6", "9", "3", "+", "-11", "*", "/", "*", "17", "+", "5", "+"], 22),
        (["3", "4", "+"], 7),
        (["5"], 5),
    ]
    for tokens, expected in rpn_cases:
        result = eval_rpn(tokens)
        fn_label = "yours"
        if result is None:
            result = _sol_eval_rpn(tokens)
            fn_label = "solution"
        check(f"[{fn_label}] {' '.join(tokens)} = {expected}", result, expected)

    # --- Exercise 3: Infix to Postfix ---
    print("\n--- Exercise 3: Infix to Postfix ---")
    infix_cases = [
        ("3 + 4", ["3", "4", "+"]),
        ("3 + 4 * 2", ["3", "4", "2", "*", "+"]),
        ("( 3 + 4 ) * 2", ["3", "4", "+", "2", "*"]),
        ("1 + 2 * 3 - 4 / 2", ["1", "2", "3", "*", "+", "4", "2", "/", "-"]),
        ("( 1 + 2 ) * ( 3 + 4 )", ["1", "2", "+", "3", "4", "+", "*"]),
    ]
    for expr, expected in infix_cases:
        result = infix_to_postfix(expr)
        fn_label = "yours"
        if result is None:
            result = _sol_infix_to_postfix(expr)
            fn_label = "solution"
        check(f"[{fn_label}] \"{expr}\" -> {expected}", result, expected)

    # --- Exercise 4: Browser History ---
    print("\n--- Exercise 4: Browser History ---")
    for label, BHClass in [("yours", BrowserHistory), ("solution", _sol_BrowserHistory)]:
        bh = BHClass("google.com")
        if bh.current() is None and label == "yours":
            print("  (not implemented, testing solution)")
            continue
        check(f"[{label}] start", bh.current(), "google.com")
        bh.visit("youtube.com")
        bh.visit("github.com")
        check(f"[{label}] after 2 visits", bh.current(), "github.com")
        check(f"[{label}] back()", bh.back(), "youtube.com")
        check(f"[{label}] back()", bh.back(), "google.com")
        check(f"[{label}] back() at start", bh.back(), "google.com")
        check(f"[{label}] forward()", bh.forward(), "youtube.com")
        bh.visit("stackoverflow.com")
        check(f"[{label}] visit clears forward", bh.current(), "stackoverflow.com")
        check(f"[{label}] forward after new visit", bh.forward(), "stackoverflow.com")
        if label == "yours":
            break

    # --- Exercise 5: Decode String ---
    print("\n--- Exercise 5: Decode String ---")
    decode_cases = [
        ("3[a]", "aaa"),
        ("3[a2[c]]", "accaccacc"),
        ("2[abc]3[cd]", "abcabccdcdcd"),
        ("abc3[cd]xyz", "abccdcdcdxyz"),
        ("3[a2[bc]]", "abcbcabcbcabcbc"),
    ]
    for encoded, expected in decode_cases:
        result = decode_string(encoded)
        fn_label = "yours"
        if result is None:
            result = _sol_decode_string(encoded)
            fn_label = "solution"
        check(f"[{fn_label}] \"{encoded}\" -> \"{expected}\"", result, expected)

    # --- Summary ---
    print(f"\n{'=' * 50}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    if failed == 0:
        print("All tests passed!")
    else:
        print("Some tests failed -- check the FAIL lines above.")
    print(f"{'=' * 50}")


if __name__ == '__main__':
    run_tests()
