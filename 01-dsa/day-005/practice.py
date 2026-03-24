"""
Day 5 Practice: Amortized Analysis Exercises
=============================================

These exercises build your ability to reason about amortized costs using
all three methods. You will implement cost trackers, prove bounds, and
analyze data structures that depend on amortized arguments.

Fill in the TODO sections. Run this file to check your answers.

Run: python practice.py
"""


# =============================================================================
# Exercise 1: Amortized Cost Tracker for Dynamic Array
# =============================================================================

def exercise_1_cost_tracker(operations):
    """Track and verify amortized costs for a dynamic array.

    Given a list of 'append' operations (just the count n), simulate a
    dynamic array that doubles on resize and return a dict with:
    - 'total_actual': total actual cost of all appends
    - 'total_amortized': total amortized cost (using $3 per append)
    - 'credit_history': list of credit values after each operation
    - 'credit_never_negative': True if credit stayed >= 0 throughout

    The credit after each operation = total amortized charged so far
    minus total actual cost so far. If this ever goes negative, the
    amortized bound of $3 would be invalid.

    TODO: Implement the simulation. Track size, capacity, and costs.
    """
    size = 0
    capacity = 1
    total_actual = 0
    total_amortized = 0
    credit_history = []

    for i in range(operations):
        # TODO: Calculate actual cost of this append
        # Hint: cost is 1 normally, but size+1 when size == capacity (resize)
        actual_cost = 0  # FIX THIS

        # TODO: Update capacity if resize happened
        pass  # FIX THIS

        size += 1
        total_actual += actual_cost
        total_amortized += 3  # accounting method: charge $3 per append
        credit_history.append(total_amortized - total_actual)

    return {
        'total_actual': total_actual,
        'total_amortized': total_amortized,
        'credit_history': credit_history,
        'credit_never_negative': all(c >= 0 for c in credit_history),
    }


# =============================================================================
# Exercise 2: Binary Counter — Aggregate Analysis
# =============================================================================

def exercise_2_binary_counter_analysis(m, num_bits=16):
    """Analyze bit flip costs for m increments of a binary counter.

    Implement a binary counter and count total bit flips. Then verify
    the aggregate analysis bound: total flips < 2m.

    Return a dict with:
    - 'total_flips': actual total number of bit flips
    - 'per_bit_flips': list where per_bit_flips[k] = how many times bit k flipped
    - 'theoretical_bound': 2 * m
    - 'bound_holds': True if total_flips < 2 * m

    TODO: Implement the counter and tracking.
    """
    bits = [0] * num_bits
    total_flips = 0
    per_bit_flips = [0] * num_bits

    for _ in range(m):
        # TODO: Implement increment with carry propagation
        # Hint: flip 1->0 while carrying, then flip first 0->1
        # Track which bits flip in per_bit_flips
        pass  # FIX THIS

    return {
        'total_flips': total_flips,
        'per_bit_flips': per_bit_flips,
        'theoretical_bound': 2 * m,
        'bound_holds': total_flips < 2 * m,
    }


# =============================================================================
# Exercise 3: Queue from Two Stacks — Prove O(1) Amortized
# =============================================================================

class QueueFromTwoStacks:
    """A FIFO queue implemented using two stacks.

    Stack 'inbox' receives enqueue operations.
    Stack 'outbox' serves dequeue operations.
    When outbox is empty, pour all of inbox into outbox (reversing order).

    The pour operation costs O(n) — but each element is poured at most once
    in its lifetime. This is the key to the amortized argument.

    TODO: Implement enqueue, dequeue, and cost tracking.

    Use the accounting method:
    - Charge enqueue $3: $1 for push to inbox, $1 for future pour, $1 for future pop from outbox
    - Charge dequeue $0: paid by enqueue's credit
    - Verify: credit never goes negative
    """

    def __init__(self):
        self.inbox = []
        self.outbox = []
        self.operations = []  # list of (name, actual_cost)

    def enqueue(self, value):
        # TODO: Push to inbox, record actual cost of 1
        pass  # FIX THIS

    def dequeue(self):
        # TODO: If outbox is empty, pour inbox into outbox (track cost of each move)
        # Then pop from outbox (cost 1)
        # Record total actual cost of this dequeue
        # Return the dequeued value (or None if empty)
        pass  # FIX THIS

    def verify_amortized_bound(self):
        """Verify that charging $3 per enqueue and $0 per dequeue
        keeps credit non-negative throughout all operations.

        TODO: Compute credit after each operation and check it never goes negative.
        """
        credit = 0
        for name, actual_cost in self.operations:
            if name == "enqueue":
                amortized = 3
            else:
                amortized = 0
            credit += amortized - actual_cost
            if credit < 0:
                return False
        return True


# =============================================================================
# Exercise 4: Potential Method for Splay Tree Operations
# =============================================================================

def exercise_4_potential_analysis():
    """Analyze a simplified splay-like structure using the potential method.

    Consider a self-adjusting list where accessing element at position i
    costs i+1 (linear search), then the element moves to the front (free).

    Potential function: Phi = sum of positions of all elements
    (using 0-indexed positions, so Phi for a list of n elements
    starts at 0 + 1 + 2 + ... + (n-1) = n(n-1)/2).

    When we access element at position i:
    - Actual cost: i + 1 (scan to position i, 1-indexed cost)
    - The accessed element moves from position i to position 0
    - Elements at positions 0..i-1 each shift right by 1
    - Change in Phi: (-i) + (i) = 0... but wait, let's compute carefully.

    TODO: Work through the potential analysis.

    Return a dict with:
    - 'sequence_costs': list of (actual_cost, phi_before, phi_after, amortized_cost)
      for accessing elements at the given positions in sequence
    - 'total_actual': sum of actual costs
    - 'total_amortized': sum of amortized costs

    Access sequence: positions [3, 0, 2, 4, 1] on a list of 5 elements [A,B,C,D,E]
    """

    n = 5
    # List stores element identifiers; position = index in list
    lst = list(range(n))  # [0, 1, 2, 3, 4] representing [A, B, C, D, E]
    access_sequence = [3, 0, 2, 4, 1]  # access element at these POSITIONS

    sequence_costs = []

    for target_pos in access_sequence:
        # TODO: Find the element currently at the given conceptual position
        # (Hint: the access_sequence gives the element ID to access, not position)
        # Actually, let's access by element ID for clarity:
        # Find where element 'target_pos' currently is in the list

        # TODO: Compute phi_before = sum of indices of all elements
        phi_before = 0  # FIX THIS

        # TODO: Compute actual cost (position of target + 1)
        current_position = lst.index(target_pos)
        actual_cost = 0  # FIX THIS

        # TODO: Move accessed element to front
        # (remove from current position, insert at 0)
        pass  # FIX THIS

        # TODO: Compute phi_after = sum of indices of all elements
        phi_after = 0  # FIX THIS

        amortized_cost = actual_cost + phi_after - phi_before
        sequence_costs.append((actual_cost, phi_before, phi_after, amortized_cost))

    total_actual = sum(sc[0] for sc in sequence_costs)
    total_amortized = sum(sc[3] for sc in sequence_costs)

    return {
        'sequence_costs': sequence_costs,
        'total_actual': total_actual,
        'total_amortized': total_amortized,
    }


# =============================================================================
# Exercise 5: Why Doesn't Increment-by-1 Give O(1) Amortized?
# =============================================================================

def exercise_5_linear_resize():
    """Show that growing a dynamic array by +1 each time does NOT give O(1) amortized.

    When the array is full, increase capacity by 1 (not doubling).
    This means EVERY append after the first triggers a resize.

    TODO: Simulate n appends with +1 capacity growth.
    Return total actual cost and show it is O(n^2), not O(n).

    Hint: resize at append i copies i elements, so total cost
    = n (for insertions) + 1 + 2 + 3 + ... + (n-1) = n + n(n-1)/2.
    """

    n = 100
    size = 0
    capacity = 1
    total_cost = 0

    for i in range(n):
        # TODO: Calculate cost — 1 for insert, +size for copy if resize needed
        # TODO: If full, increase capacity by 1 (not doubling!)
        cost = 0  # FIX THIS
        total_cost += cost

    # TODO: Return results
    return {
        'total_cost': total_cost,
        'n': n,
        'expected_order': 0,  # FIX: what is n + n*(n-1)/2 ?
        'is_quadratic': False,  # FIX: is total_cost in O(n^2)?
    }


# =============================================================================
# Self-check
# =============================================================================

def run_checks():
    print("=" * 70)
    print("DAY 5 PRACTICE — Checking your solutions")
    print("=" * 70)

    # Exercise 1
    print("\n--- Exercise 1: Dynamic Array Cost Tracker ---")
    result = exercise_1_cost_tracker(64)
    if result['total_actual'] == 0:
        print("  NOT YET IMPLEMENTED")
    else:
        print(f"  Total actual cost: {result['total_actual']}")
        print(f"  Total amortized cost: {result['total_amortized']}")
        print(f"  Credit never negative: {result['credit_never_negative']}")
        if result['credit_never_negative'] and result['total_actual'] < 3 * 64:
            print("  PASS: Amortized bound holds!")
        else:
            print("  FAIL: Check your cost calculation.")

    # Exercise 2
    print("\n--- Exercise 2: Binary Counter Analysis ---")
    result = exercise_2_binary_counter_analysis(1000)
    if result['total_flips'] == 0:
        print("  NOT YET IMPLEMENTED")
    else:
        print(f"  Total flips for 1000 increments: {result['total_flips']}")
        print(f"  Theoretical bound (2m): {result['theoretical_bound']}")
        print(f"  Bound holds: {result['bound_holds']}")
        # Verify per-bit flips match expected pattern
        expected_bit0 = 1000
        if result['per_bit_flips'][0] == expected_bit0:
            print("  PASS: Per-bit analysis correct!")
        else:
            print(f"  FAIL: Bit 0 should flip {expected_bit0} times, "
                  f"got {result['per_bit_flips'][0]}")

    # Exercise 3
    print("\n--- Exercise 3: Queue from Two Stacks ---")
    q = QueueFromTwoStacks()
    # Enqueue 5 elements, then dequeue all — the pour costs O(5) once
    for i in range(5):
        q.enqueue(i)
    results = [q.dequeue() for _ in range(5)]
    if not q.operations:
        print("  NOT YET IMPLEMENTED")
    else:
        if results == [0, 1, 2, 3, 4]:
            print("  FIFO order correct!")
        else:
            print(f"  FAIL: Expected [0,1,2,3,4], got {results}")
        if q.verify_amortized_bound():
            print("  PASS: Amortized bound holds (credit never negative)!")
        else:
            print("  FAIL: Credit went negative — check your accounting.")

    # Exercise 4
    print("\n--- Exercise 4: Potential Analysis for Move-to-Front ---")
    result = exercise_4_potential_analysis()
    if result['total_actual'] == 0:
        print("  NOT YET IMPLEMENTED")
    else:
        print(f"  Total actual cost: {result['total_actual']}")
        print(f"  Total amortized cost: {result['total_amortized']}")
        for i, (ac, pb, pa, am) in enumerate(result['sequence_costs']):
            print(f"    Step {i+1}: actual={ac}, Phi {pb}->{pa}, amortized={am}")

    # Exercise 5
    print("\n--- Exercise 5: Linear Resize (Why Doubling Matters) ---")
    result = exercise_5_linear_resize()
    if result['total_cost'] == 0:
        print("  NOT YET IMPLEMENTED")
    else:
        n = result['n']
        expected = n + n * (n - 1) // 2
        print(f"  Total cost with +1 growth: {result['total_cost']}")
        print(f"  Expected (n + n(n-1)/2): {expected}")
        print(f"  Is quadratic: {result['is_quadratic']}")
        if result['total_cost'] == expected and result['is_quadratic']:
            print("  PASS: Correctly shows O(n^2) cost!")
        else:
            print("  FAIL: Check your calculation.")


if __name__ == "__main__":
    run_checks()
