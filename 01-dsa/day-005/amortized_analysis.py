"""
Day 5: Amortized Analysis — Seeing the Math in Action

Three canonical examples that demonstrate why amortized analysis matters:
1. Dynamic array (append with doubling)
2. Binary counter (increment with bit flips)
3. Stack with multipop

Each tracks actual costs per operation so you can SEE that the expensive
operations are rare enough to keep the average cheap.

Run: python amortized_analysis.py
"""


# ===========================================================================
# Example 1: Dynamic Array — The canonical amortized O(1) append
# ===========================================================================

class DynamicArray:
    """A dynamic array that doubles capacity when full.

    We track the actual cost of every append to show that total cost
    grows linearly despite occasional O(n) resizes. The cost model:
    - Inserting one element into an existing slot: cost 1
    - Copying one element during resize: cost 1
    - So a resize from capacity k to 2k costs k (copies) + 1 (insert) = k + 1
    """

    def __init__(self):
        self._capacity = 1
        self._size = 0
        self._data = [None] * self._capacity
        self.costs = []  # actual cost of each append

    def append(self, value):
        cost = 1  # the insertion itself always costs 1

        if self._size == self._capacity:
            # Resize: double capacity, copy all existing elements
            cost += self._size  # copying self._size elements
            self._capacity *= 2
            new_data = [None] * self._capacity
            for i in range(self._size):
                new_data[i] = self._data[i]
            self._data = new_data

        self._data[self._size] = value
        self._size += 1
        self.costs.append(cost)

    def __len__(self):
        return self._size


def demo_dynamic_array():
    print("=" * 70)
    print("DYNAMIC ARRAY: Amortized O(1) Append")
    print("=" * 70)

    arr = DynamicArray()
    n = 64

    for i in range(n):
        arr.append(i)

    # Show cost of each operation — spikes at powers of 2
    print(f"\nCosts for {n} appends (spikes are resizes):\n")
    for i, cost in enumerate(arr.costs):
        bar = "#" * cost
        marker = " <-- RESIZE" if cost > 1 else ""
        print(f"  append {i+1:3d}: cost {cost:3d}  {bar}{marker}")

    total_cost = sum(arr.costs)
    amortized = total_cost / n
    print(f"\n  Total actual cost: {total_cost}")
    print(f"  Number of appends: {n}")
    print(f"  Amortized cost per append: {total_cost}/{n} = {amortized:.2f}")
    print(f"  Upper bound (3n): {3 * n}")
    print(f"\n  KEY INSIGHT: Total cost ({total_cost}) < 3n ({3*n}).")
    print("  The geometric series 1+2+4+...+n < 2n makes this work.")

    # Show cumulative cost grows linearly, not quadratically
    print(f"\n  Cumulative cost at milestones:")
    cumulative = 0
    for i, cost in enumerate(arr.costs):
        cumulative += cost
        op = i + 1
        if op in (1, 2, 4, 8, 16, 32, 64):
            ratio = cumulative / op
            print(f"    After {op:3d} ops: cumulative = {cumulative:4d}, "
                  f"cumulative/ops = {ratio:.2f}")


# ===========================================================================
# Example 2: Binary Counter — O(1) amortized increment
# ===========================================================================

class BinaryCounter:
    """A k-bit binary counter that counts bit flips per increment.

    Incrementing a binary counter flips bit 0 every time, bit 1 every
    other time, bit 2 every 4th time, etc. The total flips over m
    increments is m + m/2 + m/4 + ... < 2m, so amortized cost is O(1).

    This is the cleanest example for aggregate analysis because the
    total cost has an exact closed-form sum.
    """

    def __init__(self, num_bits):
        self._bits = [0] * num_bits
        self.flip_counts = []  # flips per increment

    def increment(self):
        flips = 0
        i = 0
        # Carry propagation: flip 1s to 0s until we find a 0
        while i < len(self._bits) and self._bits[i] == 1:
            self._bits[i] = 0  # flip 1 -> 0
            flips += 1
            i += 1
        if i < len(self._bits):
            self._bits[i] = 1  # flip 0 -> 1
            flips += 1
        self.flip_counts.append(flips)

    @property
    def value(self):
        return sum(b * (2 ** i) for i, b in enumerate(self._bits))

    def __str__(self):
        # MSB first for readability
        return "".join(str(b) for b in reversed(self._bits))


def demo_binary_counter():
    print("\n\n" + "=" * 70)
    print("BINARY COUNTER: Amortized O(1) Increment")
    print("=" * 70)

    num_bits = 8
    counter = BinaryCounter(num_bits)
    m = 32

    print(f"\nIncrementing an {num_bits}-bit counter {m} times:\n")
    print(f"  {'Op':>4s}  {'Counter':>10s}  {'Value':>5s}  {'Flips':>5s}  Visual")
    print(f"  {'--':>4s}  {'--------':>10s}  {'-----':>5s}  {'-----':>5s}  ------")

    for i in range(m):
        counter.increment()
        bar = "#" * counter.flip_counts[-1]
        print(f"  {i+1:4d}  {str(counter):>10s}  {counter.value:5d}  "
              f"{counter.flip_counts[-1]:5d}  {bar}")

    total_flips = sum(counter.flip_counts)
    amortized = total_flips / m
    print(f"\n  Total bit flips: {total_flips}")
    print(f"  Number of increments: {m}")
    print(f"  Amortized flips per increment: {total_flips}/{m} = {amortized:.2f}")
    print(f"  Upper bound (2m): {2 * m}")

    # Show per-bit analysis (aggregate method)
    print(f"\n  Per-bit flip analysis (aggregate method):")
    print(f"  Bit k flips every 2^k increments, so floor(m/2^k) times total.\n")
    theoretical_total = 0
    for k in range(num_bits):
        flips_for_bit = m // (2 ** k)
        theoretical_total += flips_for_bit
        if flips_for_bit > 0:
            print(f"    Bit {k}: flips {flips_for_bit:3d} times "
                  f"(every {2**k} increments)")
    print(f"\n    Theoretical total: {theoretical_total} "
          f"(actual: {total_flips})")
    print(f"    This sum is always < 2m = {2*m} because:")
    print(f"    m/1 + m/2 + m/4 + ... = m * (1 + 1/2 + 1/4 + ...) < 2m")


# ===========================================================================
# Example 3: Stack with MULTIPOP — Accounting method
# ===========================================================================

class AmortizedStack:
    """Stack supporting push, pop, and multipop.

    MULTIPOP(k) pops min(k, size) elements. Its worst-case cost is O(n),
    but amortized over a sequence of operations, everything is O(1).

    The accounting argument: charge $2 for each PUSH ($1 for the push,
    $1 saved as credit on the element). POP and MULTIPOP cost $0 amortized
    because each popped element pays with its saved credit. Every element
    is pushed exactly once, so total credit is always non-negative.
    """

    def __init__(self):
        self._data = []
        self.operations = []  # (name, actual_cost, amortized_cost)

    def push(self, value):
        self._data.append(value)
        # Actual cost: 1. Amortized cost: 2 (prepay for future pop).
        self.operations.append(("PUSH", 1, 2))

    def pop(self):
        if not self._data:
            return None
        val = self._data.pop()
        # Actual cost: 1. Amortized cost: 0 (paid by push credit).
        self.operations.append(("POP", 1, 0))
        return val

    def multipop(self, k):
        num_popped = min(k, len(self._data))
        for _ in range(num_popped):
            self._data.pop()
        # Actual cost: num_popped. Amortized cost: 0 (each element's credit pays).
        self.operations.append((f"MULTIPOP({k})", num_popped, 0))
        return num_popped

    @property
    def size(self):
        return len(self._data)


def demo_stack_multipop():
    print("\n\n" + "=" * 70)
    print("STACK WITH MULTIPOP: Accounting Method")
    print("=" * 70)

    stack = AmortizedStack()

    # Run a sequence that mixes pushes and expensive multipops
    # to show that total actual cost is bounded by total amortized cost
    sequence = [
        ("push", 1), ("push", 2), ("push", 3), ("push", 4), ("push", 5),
        ("multipop", 3),  # pops 3 elements — expensive!
        ("push", 6), ("push", 7), ("push", 8),
        ("pop", None),
        ("push", 9), ("push", 10),
        ("multipop", 10),  # pops everything remaining — expensive!
        ("push", 11), ("push", 12),
        ("multipop", 2),
    ]

    print(f"\nExecuting a sequence of {len(sequence)} operations:\n")
    print(f"  {'Op':>4s}  {'Operation':<16s}  {'Actual':>6s}  "
          f"{'Amort':>5s}  {'Stack Size':>10s}  Credit")
    print(f"  {'--':>4s}  {'---------':<16s}  {'------':>6s}  "
          f"{'-----':>5s}  {'----------':>10s}  ------")

    for i, (op, arg) in enumerate(sequence):
        if op == "push":
            stack.push(arg)
        elif op == "pop":
            stack.pop()
        elif op == "multipop":
            stack.multipop(arg)

        name, actual, amortized = stack.operations[-1]

        # Credit = total amortized charged so far - total actual spent so far
        total_actual = sum(o[1] for o in stack.operations)
        total_amort = sum(o[2] for o in stack.operations)
        credit = total_amort - total_actual

        print(f"  {i+1:4d}  {name:<16s}  {actual:6d}  "
              f"{amortized:5d}  {stack.size:10d}  {credit:6d}")

    total_actual = sum(o[1] for o in stack.operations)
    total_amort = sum(o[2] for o in stack.operations)
    print(f"\n  Total actual cost:    {total_actual}")
    print(f"  Total amortized cost: {total_amort}")
    print(f"  Credit remaining:     {total_amort - total_actual}")
    print(f"\n  KEY INSIGHT: Credit never goes negative. Every element that")
    print(f"  gets popped (individually or via MULTIPOP) was already paid for")
    print(f"  by its PUSH. So total actual cost <= total amortized cost = 2 * #pushes.")


# ===========================================================================
# Example 4: Potential Method — Dynamic Array revisited
# ===========================================================================

def demo_potential_method():
    """Re-analyze the dynamic array using the potential method.

    The potential function captures "stored energy" in the data structure.
    For a dynamic array with size s and capacity c:
        Phi(D) = 2*s - c

    After a resize: s = c/2, so Phi = 2*(c/2) - c = 0. Clean slate.
    As we fill the array: Phi grows by 2 per append (no resize).
    At resize: Phi drops sharply, releasing energy to pay for copying.

    Amortized cost = actual cost + delta_Phi:
    - Normal append: actual=1, delta_Phi=+2, amortized=3
    - Append with resize from cap k: actual=k+1, delta_Phi=-(k-2), amortized=3
    """
    print("\n\n" + "=" * 70)
    print("POTENTIAL METHOD: Dynamic Array Re-analyzed")
    print("=" * 70)

    # Simulate dynamic array tracking potential
    n = 32
    size = 0
    capacity = 1

    print(f"\nPhi(D) = 2*size - capacity")
    print(f"Amortized cost = actual cost + Phi(after) - Phi(before)\n")
    print(f"  {'Op':>4s}  {'Size':>4s}  {'Cap':>4s}  {'Actual':>6s}  "
          f"{'Phi_before':>10s}  {'Phi_after':>9s}  {'dPhi':>5s}  {'Amort':>5s}")
    print(f"  {'--':>4s}  {'----':>4s}  {'---':>4s}  {'------':>6s}  "
          f"{'----------':>10s}  {'---------':>9s}  {'----':>5s}  {'-----':>5s}")

    total_actual = 0
    total_amortized = 0

    for i in range(n):
        phi_before = 2 * size - capacity
        actual_cost = 1  # insertion

        if size == capacity:
            actual_cost += size  # copying during resize
            capacity *= 2

        size += 1
        phi_after = 2 * size - capacity
        delta_phi = phi_after - phi_before
        amortized = actual_cost + delta_phi

        total_actual += actual_cost
        total_amortized += amortized

        # Only print at interesting points (resizes and a few normal ones)
        is_resize = actual_cost > 1
        is_milestone = (i + 1) in (1, 2, 3, 4, 5, 8, 9, 16, 17, 32)
        if is_resize or is_milestone:
            marker = " <-- RESIZE" if is_resize else ""
            print(f"  {i+1:4d}  {size:4d}  {capacity:4d}  {actual_cost:6d}  "
                  f"{phi_before:10d}  {phi_after:9d}  {delta_phi:+5d}  "
                  f"{amortized:5d}{marker}")

    print(f"\n  Total actual cost:    {total_actual}")
    print(f"  Total amortized cost: {total_amortized}")
    print(f"  Amortized per op:     {total_amortized}/{n} = "
          f"{total_amortized/n:.2f}")
    print(f"\n  KEY INSIGHT: The potential absorbs the variance.")
    print(f"  It rises by 2 on cheap ops and drops sharply on resizes,")
    print(f"  making every operation cost exactly 3 amortized.")


# ===========================================================================
# Main: Run all demos
# ===========================================================================

if __name__ == "__main__":
    demo_dynamic_array()
    demo_binary_counter()
    demo_stack_multipop()
    demo_potential_method()

    print("\n\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("""
  Amortized analysis gives worst-case guarantees for SEQUENCES of operations.

  Method        | Idea                    | Best for
  --------------|-------------------------|----------------------------------
  Aggregate     | Total cost / n          | Simple sums (counter, array)
  Accounting    | Prepay on cheap ops     | Element-level reasoning (stacks)
  Potential     | Energy function Phi     | Formal proofs (splay, Fibonacci)

  All three methods give the same answer — they are different proof
  techniques for the same underlying truth: expensive operations can
  only happen after enough cheap ones have "paid" for them.
    """)
