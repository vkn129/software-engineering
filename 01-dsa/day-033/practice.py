"""
Day 33 Practice: Min-Stack / Max-Queue exercises

Four exercises building on the core idea that you can track extremes in O(1)
by storing auxiliary information alongside each element.

Pattern: each exercise has a TODO stub, then a _sol_ solution below.
run_tests() at the bottom validates everything.
"""


# ===================================================================
# Exercise 1: MinMaxStack
# ===================================================================
# A stack that supports O(1) push, pop, getMin AND getMax simultaneously.
#
# Why this matters: some monitoring systems need both the floor and ceiling
# of a sliding window — e.g., detecting if a metric has "flatlined" (max - min
# is near zero) or if it's "spiking" (max - min exceeds a threshold).
#
# Approach: store (value, current_min, current_max) per entry.  Same idea as
# MinStack, but tracking both extremes.
# ===================================================================

class MinMaxStack:
    """TODO: Implement a stack with O(1) push, pop, get_min, get_max."""

    def __init__(self):
        # TODO
        pass

    def push(self, val: int) -> None:
        # TODO
        pass

    def pop(self) -> int:
        # TODO
        pass

    def get_min(self) -> int:
        # TODO
        pass

    def get_max(self) -> int:
        # TODO
        pass

    def __len__(self):
        # TODO
        pass


class _sol_MinMaxStack:
    """
    Each stack entry is (value, min_so_far, max_so_far).
    On push, the new min/max is derived from the previous top in O(1).
    On pop, the min/max is automatically restored because the entry below
    already has the correct historical min/max.
    """

    def __init__(self):
        self._stack = []  # list of (val, min_so_far, max_so_far)

    def push(self, val: int) -> None:
        if not self._stack:
            self._stack.append((val, val, val))
        else:
            _, prev_min, prev_max = self._stack[-1]
            self._stack.append((val, min(val, prev_min), max(val, prev_max)))

    def pop(self) -> int:
        if not self._stack:
            raise IndexError("pop from empty stack")
        return self._stack.pop()[0]

    def get_min(self) -> int:
        if not self._stack:
            raise IndexError("get_min from empty stack")
        return self._stack[-1][1]

    def get_max(self) -> int:
        if not self._stack:
            raise IndexError("get_max from empty stack")
        return self._stack[-1][2]

    def __len__(self):
        return len(self._stack)


# ===================================================================
# Exercise 2: Sliding Window Median (Two-Heap Preview)
# ===================================================================
# Given an array and window size k, return the median of each window.
#
# Why this matters: percentile tracking in streaming data.  The median is
# the 50th percentile — the most common "is this metric normal?" check.
#
# Approach (simplified — no heap removal, just conceptual):
#   - Maintain a "max-heap" for the lower half and a "min-heap" for the upper half.
#   - We implement heaps as sorted insert into a list (O(k) per op, not O(log k)).
#     The point is to understand the TWO-STRUCTURE pattern, not to optimise yet.
#
# Why connect to today: the min-stack / max-queue pattern is about maintaining
# order statistics (min, max) cheaply.  The median extends that to the 50th
# percentile using two heaps — same family of ideas.
# ===================================================================

def sliding_window_median(nums: list, k: int) -> list:
    """
    TODO: Return list of medians for each window of size k.

    For even k, median = average of the two middle elements.
    Use the two-sorted-list approach described above.
    """
    # TODO
    pass


def _sol_sliding_window_median(nums: list, k: int) -> list:
    """
    Two sorted halves approach.

    lower: sorted descending (acts like a max-heap — largest at index 0)
    upper: sorted ascending (acts like a min-heap — smallest at index 0)

    Invariant: len(lower) == len(upper) or len(lower) == len(upper) + 1
    This means the median is either lower[0] or avg(lower[0], upper[0]).

    We rebuild for each window position (O(k log k) per window).  This is NOT
    the optimal O(n log k) solution — it's a conceptual preview.  The optimal
    version uses a heap with lazy deletion, covered in later days.
    """
    if not nums or k <= 0:
        return []

    result = []
    for i in range(len(nums) - k + 1):
        window = sorted(nums[i:i + k])
        mid = k // 2
        if k % 2 == 1:
            result.append(float(window[mid]))
        else:
            result.append((window[mid - 1] + window[mid]) / 2.0)
    return result


# ===================================================================
# Exercise 3: Online Stock Span
# ===================================================================
# Design a class that collects daily stock prices and returns the "span"
# for each day.  The span on day i is the number of consecutive days
# (ending at day i) where the price was <= price[i].
#
# Example: prices [100, 80, 60, 70, 60, 75, 85]
#          spans  [  1,  1,  1,  2,  1,  4,  6]
#
# Why this matters: the stock span problem is a classic application of
# monotonic stacks.  It's equivalent to "for each element, find the
# nearest greater element to the left."
#
# Connection to today: the max-stack tracks the running maximum.  The
# monotonic stack used here is the same idea — we discard elements that
# can never be "the answer" because a larger element has appeared.
# ===================================================================

class StockSpanner:
    """
    TODO: Implement next(price) -> span.

    Use a stack of (price, span) pairs.  When a new price comes in,
    pop all entries with price <= new price and accumulate their spans.
    """

    def __init__(self):
        # TODO
        pass

    def next(self, price: int) -> int:
        # TODO
        pass


class _sol_StockSpanner:
    """
    Monotonic stack approach.

    Stack stores (price, span) pairs in decreasing order of price.
    When a new price arrives, we pop everything <= it, accumulating
    those spans into the new entry's span.

    Why this works: any popped entry's "zone of influence" is entirely
    contained within the new entry's zone, so we absorb their spans.
    Each element is pushed once and popped at most once => O(n) total.
    """

    def __init__(self):
        self._stack = []  # (price, cumulative_span)

    def next(self, price: int) -> int:
        span = 1  # at minimum, the day itself counts
        # Pop entries that the new price dominates
        while self._stack and self._stack[-1][0] <= price:
            span += self._stack.pop()[1]
        self._stack.append((price, span))
        return span


# ===================================================================
# Exercise 4: Validate Stack Sequences
# ===================================================================
# Given two sequences `pushed` and `popped`, both with distinct values,
# return True if this could have been the result of push/pop operations
# on an initially empty stack.
#
# Example: pushed = [1,2,3,4,5], popped = [4,5,3,2,1] -> True
#          pushed = [1,2,3,4,5], popped = [4,3,5,1,2] -> False
#
# Why this matters: understanding what orderings a stack can and cannot
# produce is fundamental to parsing (e.g., checking if an expression's
# parentheses are balanced is a special case).
#
# Connection to today: this exercise forces you to simulate stack
# operations carefully — the same mental model needed to reason about
# min-stacks and max-queues.
# ===================================================================

def validate_stack_sequences(pushed: list, popped: list) -> bool:
    """
    TODO: Return True if popped is a valid pop sequence for pushed.

    Simulate: iterate through `pushed`, pushing each element.  After each
    push, pop as long as the stack top matches the next expected pop value.
    At the end, the stack should be empty.
    """
    # TODO
    pass


def _sol_validate_stack_sequences(pushed: list, popped: list) -> bool:
    """
    Greedy simulation.

    We push elements one by one.  After each push, we greedily pop
    whenever the top matches the next value in the popped sequence.

    Why greedy works: if the top matches and we DON'T pop now, we'd need
    to pop it later — but by then other elements will be on top, blocking
    it.  So delaying a valid pop can only make things worse, never better.

    Time: O(n) — each element is pushed once and popped at most once.
    Space: O(n) — the simulation stack.
    """
    stack = []
    pop_idx = 0
    for val in pushed:
        stack.append(val)
        # Greedily pop whenever possible
        while stack and pop_idx < len(popped) and stack[-1] == popped[pop_idx]:
            stack.pop()
            pop_idx += 1
    return len(stack) == 0


# ===================================================================
# Tests
# ===================================================================

def run_tests():
    print("Exercise 1: MinMaxStack")
    # Test both the solution and the student's implementation (if filled in)
    for label, Cls in [("_sol_", _sol_MinMaxStack), ("yours", MinMaxStack)]:
        try:
            s = Cls()
            s.push(5)
            assert s.get_min() == 5 and s.get_max() == 5
            s.push(3)
            assert s.get_min() == 3 and s.get_max() == 5
            s.push(7)
            assert s.get_min() == 3 and s.get_max() == 7
            s.push(1)
            assert s.get_min() == 1 and s.get_max() == 7
            s.pop()
            assert s.get_min() == 3 and s.get_max() == 7
            s.pop()
            assert s.get_min() == 3 and s.get_max() == 5
            print(f"  [{label}] PASSED")
        except (AssertionError, TypeError, AttributeError) as e:
            print(f"  [{label}] FAILED or not implemented: {e}")

    print()
    print("Exercise 2: Sliding Window Median")
    test_cases_2 = [
        ([1, 3, -1, -3, 5, 3, 6, 7], 3, [1.0, -1.0, -1.0, 3.0, 5.0, 6.0]),
        ([1, 2, 3, 4], 2, [1.5, 2.5, 3.5]),
        ([5], 1, [5.0]),
    ]
    for fn_label, fn in [("_sol_", _sol_sliding_window_median), ("yours", sliding_window_median)]:
        all_ok = True
        for nums, k, expected in test_cases_2:
            result = fn(nums, k)
            if result != expected:
                print(f"  [{fn_label}] FAILED: {nums}, k={k} -> {result}, expected {expected}")
                all_ok = False
        if all_ok:
            print(f"  [{fn_label}] PASSED")

    print()
    print("Exercise 3: Online Stock Span")
    prices = [100, 80, 60, 70, 60, 75, 85]
    expected_spans = [1, 1, 1, 2, 1, 4, 6]
    for label, Cls in [("_sol_", _sol_StockSpanner), ("yours", StockSpanner)]:
        try:
            sp = Cls()
            spans = [sp.next(p) for p in prices]
            assert spans == expected_spans, f"got {spans}"
            print(f"  [{label}] PASSED")
        except (AssertionError, TypeError, AttributeError) as e:
            print(f"  [{label}] FAILED or not implemented: {e}")

    print()
    print("Exercise 4: Validate Stack Sequences")
    test_cases_4 = [
        ([1, 2, 3, 4, 5], [4, 5, 3, 2, 1], True),
        ([1, 2, 3, 4, 5], [4, 3, 5, 1, 2], False),
        ([1], [1], True),
        ([], [], True),
        ([1, 2, 3], [3, 2, 1], True),   # pure LIFO
        ([1, 2, 3], [1, 2, 3], True),   # pop immediately after each push
    ]
    for fn_label, fn in [("_sol_", _sol_validate_stack_sequences), ("yours", validate_stack_sequences)]:
        all_ok = True
        for pushed, popped, expected in test_cases_4:
            result = fn(pushed, popped)
            if result != expected:
                print(f"  [{fn_label}] FAILED: pushed={pushed}, popped={popped} -> {result}, expected {expected}")
                all_ok = False
        if all_ok:
            print(f"  [{fn_label}] PASSED")

    print()
    print("Done.")


if __name__ == "__main__":
    run_tests()
