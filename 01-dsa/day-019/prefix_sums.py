"""
Day 19: Prefix Sums & Difference Arrays — O(1) Range Queries

This script builds prefix sums and difference arrays from first principles.
Each class is implemented step by step with visual output showing exactly
what the data structures look like and how queries resolve.

The unifying idea: prefix sums are discrete integrals, difference arrays
are discrete derivatives, and they are exact inverses of each other.

Run: python prefix_sums.py
"""


# ===========================================================================
# SECTION 1: 1D Prefix Sums
# ===========================================================================

class PrefixSum1D:
    """Precompute cumulative sums for O(1) range sum queries.

    The prefix array has length n+1 with a sentinel zero at index 0.
    This avoids special-casing queries that start at index 0 — the same
    reason mathematicians define the empty sum as 0."""

    def __init__(self, arr):
        n = len(arr)
        # prefix[0] = 0 is the sentinel: sum of zero elements
        # prefix[k] = arr[0] + arr[1] + ... + arr[k-1]
        self.prefix = [0] * (n + 1)
        for i in range(n):
            self.prefix[i + 1] = self.prefix[i] + arr[i]
        self.arr = arr

    def query(self, left, right):
        """Return sum of arr[left..right] inclusive.

        This is the discrete Fundamental Theorem of Calculus:
        integral(f, a, b) = F(b) - F(a)
        sum(arr[left..right]) = prefix[right+1] - prefix[left]"""
        return self.prefix[right + 1] - self.prefix[left]

    def show(self):
        """Print the original array and prefix array side by side."""
        print(f"  Array:  {self.arr}")
        print(f"  Prefix: {self.prefix}")


def demo_1d_prefix_sum():
    """Demonstrate 1D prefix sums with several range queries."""
    print("=" * 60)
    print("1D PREFIX SUMS")
    print("=" * 60)

    arr = [3, 1, 4, 1, 5, 9, 2, 6]
    ps = PrefixSum1D(arr)
    ps.show()
    print()

    # Run several queries to show O(1) range sums
    queries = [(0, 2), (1, 4), (3, 7), (0, 7), (5, 5)]
    for left, right in queries:
        result = ps.query(left, right)
        # Verify against brute force so you can see both match
        brute = sum(arr[left:right + 1])
        print(f"  sum(arr[{left}..{right}]) = {result}  "
              f"(brute force: {brute}, subarray: {arr[left:right + 1]})")

    print()


# ===========================================================================
# SECTION 2: 2D Prefix Sums
# ===========================================================================

class PrefixSum2D:
    """Precompute 2D cumulative sums for O(1) rectangle sum queries.

    Uses inclusion-exclusion from combinatorics: to avoid double-counting
    the overlap when summing "everything above" and "everything to the left",
    we subtract the overlap once and add back what we over-subtracted.

    This is the same principle behind the Principle of Inclusion-Exclusion
    (PIE) and is why OLAP cubes work."""

    def __init__(self, matrix):
        if not matrix or not matrix[0]:
            self.prefix = [[0]]
            return

        rows = len(matrix)
        cols = len(matrix[0])

        # prefix has (rows+1) x (cols+1) with sentinel zeros on top and left
        self.prefix = [[0] * (cols + 1) for _ in range(rows + 1)]

        for r in range(rows):
            for c in range(cols):
                # Inclusion-exclusion: add what's above and to the left,
                # subtract the double-counted corner, add current cell
                self.prefix[r + 1][c + 1] = (
                    matrix[r][c]
                    + self.prefix[r][c + 1]      # everything above
                    + self.prefix[r + 1][c]      # everything to the left
                    - self.prefix[r][c]           # subtracted twice, add back
                )

        self.matrix = matrix

    def rectangle_sum(self, r1, c1, r2, c2):
        """Return sum of all elements in rectangle (r1,c1) to (r2,c2) inclusive.

        The formula carves out the desired rectangle from the total by
        subtracting the regions above and to the left, then adding back
        the corner that was subtracted twice."""
        return (
            self.prefix[r2 + 1][c2 + 1]
            - self.prefix[r1][c2 + 1]       # above the rectangle
            - self.prefix[r2 + 1][c1]       # left of the rectangle
            + self.prefix[r1][c1]            # double-subtracted corner
        )

    def show(self):
        """Print the matrix and prefix table."""
        print("  Matrix:")
        for row in self.matrix:
            print(f"    {row}")
        print("  Prefix table:")
        for row in self.prefix:
            print(f"    {row}")


def demo_2d_prefix_sum():
    """Demonstrate 2D prefix sums with rectangle queries."""
    print("=" * 60)
    print("2D PREFIX SUMS")
    print("=" * 60)

    matrix = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
    ]
    ps2d = PrefixSum2D(matrix)
    ps2d.show()
    print()

    # Several rectangle queries
    queries = [
        (0, 0, 0, 0, "single element (top-left)"),
        (0, 0, 2, 3, "entire matrix"),
        (1, 1, 2, 2, "inner 2x2 block"),
        (0, 2, 1, 3, "top-right 2x2 block"),
        (2, 0, 2, 3, "bottom row"),
    ]
    for r1, c1, r2, c2, desc in queries:
        result = ps2d.rectangle_sum(r1, c1, r2, c2)
        # Brute force verification
        brute = sum(
            matrix[r][c]
            for r in range(r1, r2 + 1)
            for c in range(c1, c2 + 1)
        )
        print(f"  sum({desc}) = rect({r1},{c1},{r2},{c2}) = {result}  "
              f"(brute: {brute})")

    print()


# ===========================================================================
# SECTION 3: Difference Arrays
# ===========================================================================

class DifferenceArray:
    """O(1) range updates with deferred reconstruction.

    The difference array is the discrete derivative of the target array.
    Each range update [left, right] += val only touches two boundary
    positions. After all updates, we "integrate" (prefix sum) to recover
    the final array.

    This is optimal when you have many updates but only read the result
    once at the end — the batch-write, single-read pattern."""

    def __init__(self, n, initial=None):
        # Start from an initial array or all zeros
        if initial is not None:
            # Convert the initial array to its difference representation
            # diff[0] = initial[0], diff[i] = initial[i] - initial[i-1]
            self.diff = [0] * n
            self.diff[0] = initial[0]
            for i in range(1, n):
                self.diff[i] = initial[i] - initial[i - 1]
        else:
            self.diff = [0] * n
        self.n = n

    def range_update(self, left, right, val):
        """Add val to every element in [left, right] inclusive.

        Only touch two positions — the start and one past the end.
        This records the "step up" and "step down" of the update,
        like marking the derivative of a step function."""
        self.diff[left] += val
        if right + 1 < self.n:
            self.diff[right + 1] -= val

    def reconstruct(self):
        """Recover the actual array by taking the prefix sum of diff.

        This "integrates" the derivative back into the original function.
        Each position accumulates all the increments that started at or
        before it, minus those that ended before it."""
        result = [0] * self.n
        result[0] = self.diff[0]
        for i in range(1, self.n):
            result[i] = result[i - 1] + self.diff[i]
        return result


def demo_difference_array():
    """Demonstrate difference arrays with multiple range updates."""
    print("=" * 60)
    print("DIFFERENCE ARRAYS")
    print("=" * 60)

    n = 8
    da = DifferenceArray(n)

    # Apply several range updates — in production, these might be
    # overlapping booking intervals or salary adjustments
    updates = [
        (1, 4, 5, "add 5 to indices [1..4]"),
        (2, 6, 3, "add 3 to indices [2..6]"),
        (0, 3, -2, "subtract 2 from indices [0..3]"),
    ]

    print(f"  Starting with array of {n} zeros")
    print()

    for left, right, val, desc in updates:
        da.range_update(left, right, val)
        print(f"  Update: {desc}")
        print(f"    diff array: {da.diff}")

    print()
    result = da.reconstruct()
    print(f"  Final array:  {result}")

    # Verify against brute force
    brute = [0] * n
    for left, right, val, _ in updates:
        for i in range(left, right + 1):
            brute[i] += val
    print(f"  Brute force:  {brute}")
    print(f"  Match: {result == brute}")
    print()


# ===========================================================================
# SECTION 4: The Calculus Connection
# ===========================================================================

def demo_calculus_connection():
    """Show that prefix sums and difference arrays are exact inverses.

    prefix_sum(difference_array(arr)) == arr
    difference_array(prefix_sum(arr)) == arr

    This is the discrete Fundamental Theorem of Calculus."""
    print("=" * 60)
    print("THE CALCULUS CONNECTION")
    print("=" * 60)

    arr = [3, 1, 4, 1, 5, 9, 2, 6]
    print(f"  Original array: {arr}")
    print()

    # Step 1: Compute the difference array (discrete derivative)
    diff = [arr[0]]
    for i in range(1, len(arr)):
        diff.append(arr[i] - arr[i - 1])
    print(f"  Difference (derivative): {diff}")

    # Step 2: Compute prefix sum of the difference array (integrate the derivative)
    # Should recover the original
    recovered = [diff[0]]
    for i in range(1, len(diff)):
        recovered.append(recovered[-1] + diff[i])
    print(f"  Prefix sum of diff (integrate derivative): {recovered}")
    print(f"  Matches original: {recovered == arr}")
    print()

    # Now the other direction
    # Step 1: Compute prefix sums (discrete integral)
    prefix = [0]
    for x in arr:
        prefix.append(prefix[-1] + x)
    print(f"  Prefix sums (integral): {prefix}")

    # Step 2: Compute differences of prefix sums (differentiate the integral)
    # Should recover the original (shifted by one because of sentinel)
    recovered2 = []
    for i in range(1, len(prefix)):
        recovered2.append(prefix[i] - prefix[i - 1])
    print(f"  Diff of prefix sums (differentiate integral): {recovered2}")
    print(f"  Matches original: {recovered2 == arr}")
    print()

    print("  This is exactly the Fundamental Theorem of Calculus:")
    print("    d/dx integral(f, 0, x) = f(x)")
    print("    integral(f', a, b) = f(b) - f(a)")
    print()


# ===========================================================================
# SECTION 5: Practical Example — Counting Overlapping Intervals
# ===========================================================================

def demo_overlapping_intervals():
    """Real-world application: given a list of events with start/end times,
    find the maximum number of concurrent events.

    This is the same problem as "maximum overlapping bookings" or
    "peak server load" — and difference arrays solve it elegantly."""
    print("=" * 60)
    print("APPLICATION: Maximum Overlapping Intervals")
    print("=" * 60)

    # Events represented as (start, end) in discrete time slots
    events = [
        (1, 5, "Meeting A"),
        (2, 6, "Meeting B"),
        (4, 8, "Meeting C"),
        (7, 9, "Meeting D"),
    ]

    # Find the time range
    max_time = max(end for _, end, _ in events)

    # Use difference array: each event adds 1 to its time range
    da = DifferenceArray(max_time + 1)
    for start, end, name in events:
        da.range_update(start, end, 1)
        print(f"  {name}: time [{start}..{end}]")

    timeline = da.reconstruct()
    peak = max(timeline)
    peak_time = timeline.index(peak)

    print()
    print(f"  Timeline (concurrent events at each time slot):")
    for t, count in enumerate(timeline):
        bar = "#" * count
        print(f"    t={t}: {bar} ({count})")

    print()
    print(f"  Peak concurrency: {peak} at time {peak_time}")
    print(f"  You need at least {peak} meeting rooms.")
    print()


# ===========================================================================
# MAIN
# ===========================================================================

if __name__ == "__main__":
    demo_1d_prefix_sum()
    demo_2d_prefix_sum()
    demo_difference_array()
    demo_calculus_connection()
    demo_overlapping_intervals()
