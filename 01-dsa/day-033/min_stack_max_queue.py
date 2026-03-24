"""
Day 33: Min-Stack / Max-Queue

Why these exist:
- Monitoring systems need "what's the min/max over recent data?" in O(1).
- Trading platforms need instant access to price extremes.
- Sliding-window algorithms (Day 34+) are built on top of max-queues.

All implementations use only Python builtins — no heapq, no collections.
"""


# ---------------------------------------------------------------------------
# MinStack — O(1) push, pop, top, get_min
# ---------------------------------------------------------------------------

class MinStack:
    """
    Stack that supports O(1) minimum queries.

    Key insight: the minimum of all elements *below* a given position never
    changes while that element sits on the stack.  So we store a parallel
    "min so far" alongside each element.

    We use a single list of (value, current_min) tuples rather than two
    separate lists — fewer cache misses, simpler bookkeeping.
    """

    def __init__(self):
        # Each entry: (value, min_from_bottom_to_here)
        self._stack = []

    def push(self, val: int) -> None:
        # The new minimum is either the incoming value or the previous minimum.
        current_min = val if not self._stack else min(val, self._stack[-1][1])
        self._stack.append((val, current_min))

    def pop(self) -> int:
        if not self._stack:
            raise IndexError("pop from empty MinStack")
        return self._stack.pop()[0]

    def top(self) -> int:
        if not self._stack:
            raise IndexError("top from empty MinStack")
        return self._stack[-1][0]

    def get_min(self) -> int:
        """O(1) — just read the stored minimum at the top."""
        if not self._stack:
            raise IndexError("get_min from empty MinStack")
        return self._stack[-1][1]

    def __len__(self):
        return len(self._stack)

    def __bool__(self):
        return bool(self._stack)


# ---------------------------------------------------------------------------
# MaxStack — O(1) push, pop, top, get_max
# ---------------------------------------------------------------------------

class MaxStack:
    """
    Identical idea to MinStack, but tracking maximum.

    Why a separate class instead of a flag?  Clarity.  In production you'd
    likely parameterise with a comparator, but for learning the duplication
    makes each structure self-contained and easy to reason about.
    """

    def __init__(self):
        # Each entry: (value, max_from_bottom_to_here)
        self._stack = []

    def push(self, val: int) -> None:
        current_max = val if not self._stack else max(val, self._stack[-1][1])
        self._stack.append((val, current_max))

    def pop(self) -> int:
        if not self._stack:
            raise IndexError("pop from empty MaxStack")
        return self._stack.pop()[0]

    def top(self) -> int:
        if not self._stack:
            raise IndexError("top from empty MaxStack")
        return self._stack[-1][0]

    def get_max(self) -> int:
        if not self._stack:
            raise IndexError("get_max from empty MaxStack")
        return self._stack[-1][1]

    def __len__(self):
        return len(self._stack)

    def __bool__(self):
        return bool(self._stack)


# ---------------------------------------------------------------------------
# MaxQueue — amortized O(1) enqueue, dequeue, get_max
# ---------------------------------------------------------------------------

class MaxQueue:
    """
    Queue (FIFO) with O(1) amortised max queries.

    Built from two MaxStacks:
      - _in_stack:  receives all enqueues (push)
      - _out_stack: serves all dequeues (pop)

    When _out_stack is empty and we need to dequeue, we transfer all elements
    from _in_stack to _out_stack (reversing order => FIFO).

    Amortisation argument:
        Each element is pushed onto _in_stack exactly once and popped+pushed
        onto _out_stack exactly once.  Total work across ALL operations for
        n elements = O(n).  Therefore amortised cost per operation = O(1).

    Max query:
        Both stacks independently track their own max.  The queue's max is
        simply max(_in_stack.max, _out_stack.max).  Each of those is O(1),
        so the combined query is O(1) — no amortisation needed for the query
        itself.
    """

    def __init__(self):
        self._in_stack = MaxStack()   # enqueue side
        self._out_stack = MaxStack()  # dequeue side

    def enqueue(self, val: int) -> None:
        self._in_stack.push(val)

    def _transfer(self) -> None:
        """Move all elements from in-stack to out-stack, reversing order."""
        # This is the "expensive" step, but each element crosses at most once.
        while self._in_stack:
            self._out_stack.push(self._in_stack.pop())

    def dequeue(self) -> int:
        if not self._out_stack:
            if not self._in_stack:
                raise IndexError("dequeue from empty MaxQueue")
            self._transfer()
        return self._out_stack.pop()

    def get_max(self) -> int:
        """
        O(1) — take the max of both stacks' tracked maximums.
        Works because the queue's elements are partitioned across the two stacks,
        and each stack knows its own max.
        """
        if not self._in_stack and not self._out_stack:
            raise IndexError("get_max from empty MaxQueue")
        if not self._in_stack:
            return self._out_stack.get_max()
        if not self._out_stack:
            return self._in_stack.get_max()
        return max(self._in_stack.get_max(), self._out_stack.get_max())

    def __len__(self):
        return len(self._in_stack) + len(self._out_stack)

    def __bool__(self):
        return bool(self._in_stack) or bool(self._out_stack)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("=" * 60)
    print("MinStack Demo")
    print("=" * 60)
    ms = MinStack()
    for v in [5, 3, 7, 1, 4]:
        ms.push(v)
        print(f"  push({v})  ->  min = {ms.get_min()}")
    print()
    while ms:
        min_before = ms.get_min()
        popped = ms.pop()
        min_after = ms.get_min() if ms else "N/A"
        print(f"  pop() = {popped}  ->  min was {min_before}, now {min_after}")

    print()
    print("=" * 60)
    print("MaxStack Demo")
    print("=" * 60)
    mx = MaxStack()
    for v in [2, 8, 3, 9, 1]:
        mx.push(v)
        print(f"  push({v})  ->  max = {mx.get_max()}")
    print()
    while mx:
        max_before = mx.get_max()
        popped = mx.pop()
        max_after = mx.get_max() if mx else "N/A"
        print(f"  pop() = {popped}  ->  max was {max_before}, now {max_after}")

    print()
    print("=" * 60)
    print("MaxQueue Demo")
    print("=" * 60)
    mq = MaxQueue()
    ops = [
        ("enqueue", 3), ("enqueue", 1), ("enqueue", 5),
        ("dequeue", None), ("enqueue", 2), ("dequeue", None), ("dequeue", None),
    ]
    for op, val in ops:
        if op == "enqueue":
            mq.enqueue(val)
            print(f"  enqueue({val})  ->  max = {mq.get_max()}")
        else:
            removed = mq.dequeue()
            max_str = mq.get_max() if mq else "N/A"
            print(f"  dequeue() = {removed}  ->  max = {max_str}")

    print()
    print("All demos passed.")
