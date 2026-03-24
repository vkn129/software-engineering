"""
Day 31 Practice: Queue Exercises

5 exercises with TODO stubs and solutions.
Run this file directly to execute all tests.
"""

from collections import deque


# ---------------------------------------------------------------------------
# Exercise 1: Queue Using Two Stacks
# ---------------------------------------------------------------------------
# WHY: This is a classic interview question, but the real lesson is about
# amortized analysis. Each element is moved between stacks at most once,
# so n operations cost O(n) total — O(1) amortized per operation.
# Real-world: this pattern appears in functional languages where immutable
# lists make efficient queues hard (e.g., Haskell, Erlang).

class QueueFromStacks:
    """Implement a FIFO queue using only two LIFO stacks (Python lists with append/pop)."""

    def __init__(self):
        self._in_stack = []   # For enqueue
        self._out_stack = []  # For dequeue

    def enqueue(self, item):
        # TODO: Add item to the queue
        pass

    def dequeue(self):
        # TODO: Remove and return front item. Raise IndexError if empty.
        # Hint: only transfer from in_stack to out_stack when out_stack is empty
        pass

    def is_empty(self):
        # TODO
        pass


class _sol_QueueFromStacks:
    def __init__(self):
        self._in_stack = []
        self._out_stack = []

    def enqueue(self, item):
        # Always push to in_stack — O(1)
        self._in_stack.append(item)

    def dequeue(self):
        # Key insight: only transfer when out_stack is empty.
        # This gives O(1) amortized — each element moves at most once.
        if not self._out_stack:
            if not self._in_stack:
                raise IndexError("Queue is empty")
            # Reverse the order by popping from in -> pushing to out
            while self._in_stack:
                self._out_stack.append(self._in_stack.pop())
        return self._out_stack.pop()

    def is_empty(self):
        return not self._in_stack and not self._out_stack


# ---------------------------------------------------------------------------
# Exercise 2: Stack Using Two Queues
# ---------------------------------------------------------------------------
# WHY: The dual of Exercise 1. Shows that stacks and queues are
# computationally equivalent — you can simulate either with the other.
# But the cost differs: this approach makes push O(n) or pop O(n),
# unlike the amortized O(1) of queue-from-stacks.

class StackFromQueues:
    """Implement a LIFO stack using only two FIFO queues (collections.deque with append/popleft)."""

    def __init__(self):
        self._q1 = deque()
        self._q2 = deque()

    def push(self, item):
        # TODO: Push item onto the stack.
        # Hint: make the new item the front of the queue by rotating through q2.
        pass

    def pop(self):
        # TODO: Remove and return top item. Raise IndexError if empty.
        pass

    def is_empty(self):
        # TODO
        pass


class _sol_StackFromQueues:
    def __init__(self):
        self._q1 = deque()
        self._q2 = deque()

    def push(self, item):
        # Strategy: make the newest item always at the front of q1.
        # 1. Put new item in empty q2
        # 2. Move everything from q1 to q2 (preserving LIFO order)
        # 3. Swap q1 and q2
        # This is O(n) per push, but pop is O(1).
        self._q2.append(item)
        while self._q1:
            self._q2.append(self._q1.popleft())
        self._q1, self._q2 = self._q2, self._q1

    def pop(self):
        if not self._q1:
            raise IndexError("Stack is empty")
        return self._q1.popleft()

    def is_empty(self):
        return len(self._q1) == 0


# ---------------------------------------------------------------------------
# Exercise 3: Generate Binary Numbers 1 to N
# ---------------------------------------------------------------------------
# WHY: Elegant BFS-style generation. Each binary number b produces
# children b+"0" and b+"1". The queue ensures we generate them in
# numeric order. This pattern generalizes to any level-order generation
# (e.g., generating permutations, combinations).

def generate_binary(n):
    """
    Return a list of binary string representations for numbers 1 through n.
    E.g., generate_binary(5) -> ['1', '10', '11', '100', '101']

    Approach: Start with '1' in a queue. For each dequeued string s,
    enqueue s+'0' and s+'1'. Collect n results.
    """
    # TODO: Implement using a queue
    pass


def _sol_generate_binary(n):
    if n <= 0:
        return []
    result = []
    q = deque()
    q.append('1')  # Seed: binary representation of 1

    for _ in range(n):
        # Dequeue the next binary number
        current = q.popleft()
        result.append(current)
        # Generate the next two binary numbers from this one
        # current + '0' is 2*current in decimal
        # current + '1' is 2*current + 1 in decimal
        q.append(current + '0')
        q.append(current + '1')

    return result


# ---------------------------------------------------------------------------
# Exercise 4: Hot Potato / Josephus Simulation
# ---------------------------------------------------------------------------
# WHY: The Josephus problem has real history (siege survival) and appears
# in round-robin scheduling. The queue naturally models the circular
# rotation: dequeue a person, enqueue them at the back (they go to the
# end of the circle). Every k-th person is eliminated.

def hot_potato(names, k):
    """
    Simulate the hot potato game. Players stand in a circle. Count to k,
    and the person holding the potato is eliminated. Repeat until one remains.

    Args:
        names: list of player names
        k: number of passes before elimination

    Returns:
        (winner_name, elimination_order)
    """
    # TODO: Use a queue to simulate the circular elimination
    pass


def _sol_hot_potato(names, k):
    q = deque(names)
    elimination_order = []

    while len(q) > 1:
        # Rotate k times: dequeue from front, enqueue to back
        # This simulates passing the potato around the circle
        for _ in range(k):
            q.append(q.popleft())
        # The person now at the front is eliminated
        eliminated = q.popleft()
        elimination_order.append(eliminated)

    winner = q.popleft()
    return winner, elimination_order


# ---------------------------------------------------------------------------
# Exercise 5: Recent Counter (Requests in Last 3000ms)
# ---------------------------------------------------------------------------
# WHY: Sliding window problems are queue problems. Old entries fall off
# the front, new entries arrive at the back. This exact pattern is used
# in rate limiters (API throttling), monitoring (requests per second),
# and streaming analytics (tumbling/sliding windows).

class RecentCounter:
    """
    Count the number of requests made in the last 3000 milliseconds.
    Each call to ping(t) adds a request at time t and returns the count
    of requests in [t - 3000, t].

    Guarantee: each call to ping has a strictly larger t than the previous call.
    """

    def __init__(self):
        self._requests = deque()

    def ping(self, t):
        """
        Record a request at time t.
        Return the number of requests in [t - 3000, t].
        """
        # TODO: Add t to the queue, remove expired entries, return count
        pass


class _sol_RecentCounter:
    def __init__(self):
        self._requests = deque()

    def ping(self, t):
        self._requests.append(t)
        # Remove all requests outside the window.
        # Since times are strictly increasing, expired entries are always
        # at the front — this is why a queue works perfectly here.
        while self._requests[0] < t - 3000:
            self._requests.popleft()
        return len(self._requests)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")
            print(f"        expected: {expected}")
            print(f"        got:      {got}")

    # --- Exercise 1: Queue from two stacks ---
    print("\nExercise 1: Queue Using Two Stacks")
    q = _sol_QueueFromStacks()
    q.enqueue(1)
    q.enqueue(2)
    q.enqueue(3)
    check("dequeue order", [q.dequeue(), q.dequeue(), q.dequeue()], [1, 2, 3])

    q.enqueue('a')
    q.enqueue('b')
    check("dequeue after re-enqueue", q.dequeue(), 'a')
    q.enqueue('c')
    check("interleaved ops", [q.dequeue(), q.dequeue()], ['b', 'c'])
    check("is_empty after drain", q.is_empty(), True)

    try:
        q.dequeue()
        check("dequeue empty raises", False, True)
    except IndexError:
        check("dequeue empty raises", True, True)

    # --- Exercise 2: Stack from two queues ---
    print("\nExercise 2: Stack Using Two Queues")
    s = _sol_StackFromQueues()
    s.push(1)
    s.push(2)
    s.push(3)
    check("pop order (LIFO)", [s.pop(), s.pop(), s.pop()], [3, 2, 1])
    check("is_empty after drain", s.is_empty(), True)

    s.push('x')
    s.push('y')
    check("pop after re-push", s.pop(), 'y')
    s.push('z')
    check("interleaved ops", [s.pop(), s.pop()], ['z', 'x'])

    # --- Exercise 3: Generate binary numbers ---
    print("\nExercise 3: Generate Binary Numbers 1 to N")
    check("n=1", _sol_generate_binary(1), ['1'])
    check("n=5", _sol_generate_binary(5), ['1', '10', '11', '100', '101'])
    check("n=8", _sol_generate_binary(8),
          ['1', '10', '11', '100', '101', '110', '111', '1000'])
    check("n=0", _sol_generate_binary(0), [])

    # --- Exercise 4: Hot potato ---
    print("\nExercise 4: Hot Potato / Josephus Simulation")
    players = ["Alice", "Bob", "Charlie", "David", "Eve"]
    winner, eliminated = _sol_hot_potato(players, 3)
    check("5 players k=3 winner", winner, "David")
    check("5 players k=3 eliminated count", len(eliminated), 4)

    winner2, _ = _sol_hot_potato(["A", "B"], 1)
    check("2 players k=1", winner2, "A")

    winner3, _ = _sol_hot_potato(["Solo"], 5)
    check("1 player", winner3, "Solo")

    # --- Exercise 5: Recent counter ---
    print("\nExercise 5: Recent Counter")
    rc = _sol_RecentCounter()
    check("ping(1)", rc.ping(1), 1)
    check("ping(100)", rc.ping(100), 2)
    check("ping(3001)", rc.ping(3001), 3)      # window: [1, 3001]
    check("ping(3002)", rc.ping(3002), 3)      # window: [2, 3002], 1 expired
    check("ping(7000)", rc.ping(7000), 1)      # window: [4000, 7000], only 7000

    # Summary
    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed}")
    if failed == 0:
        print("All tests passed!")
    print(f"{'=' * 40}")


if __name__ == "__main__":
    run_tests()
