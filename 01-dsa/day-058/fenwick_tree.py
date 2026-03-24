"""
Day 58: Fenwick Tree (Binary Indexed Tree) — Prefix Sums via Bit Manipulation
===============================================================================
A Fenwick tree stores partial sums in a flat array where each index i
is responsible for a range of elements determined by its lowest set bit.

    prefix_sum(i): walk toward index 0 by stripping lowest set bits
    update(i, d):  walk toward index n by adding lowest set bits

Both operations are O(log n). Build is O(n) using parent propagation.

Internally 1-indexed (bit tricks require it), but the API is 0-indexed
so callers don't need to think about it.

Run: python fenwick_tree.py
"""


# ─── 1D Fenwick Tree ──────────────────────────────────────────────

class FenwickTree:
    """
    1D Binary Indexed Tree for prefix sum queries and point updates.

    API is 0-indexed: positions 0..n-1.
    Internally stored as 1-indexed: positions 1..n.
    """

    def __init__(self, n_or_array):
        """
        Create a Fenwick tree.

        If n_or_array is an int, creates a tree of that size initialized to 0.
        If n_or_array is a list, builds the tree in O(n) from the array.
        """
        if isinstance(n_or_array, int):
            self.n = n_or_array
            self.tree = [0] * (self.n + 1)
            self._data = [0] * self.n  # track actual element values
        else:
            arr = n_or_array
            self.n = len(arr)
            self._data = list(arr)
            # O(n) build: copy values then propagate to parents
            self.tree = [0] * (self.n + 1)
            for i in range(self.n):
                self.tree[i + 1] = arr[i]
            # Each node propagates its value to its immediate parent
            # Parent of i is i + (i & -i)
            for i in range(1, self.n + 1):
                parent = i + (i & -i)
                if parent <= self.n:
                    self.tree[parent] += self.tree[i]

    def update(self, i, delta):
        """Add delta to position i (0-indexed). O(log n)."""
        self._data[i] += delta
        i += 1  # convert to 1-indexed
        while i <= self.n:
            self.tree[i] += delta
            i += (i & -i)  # move to parent

    def prefix_sum(self, i):
        """Sum of elements in [0..i] (0-indexed, inclusive). O(log n)."""
        i += 1  # convert to 1-indexed
        total = 0
        while i > 0:
            total += self.tree[i]
            i -= (i & -i)  # strip lowest set bit
        return total

    def range_sum(self, l, r):
        """Sum of elements in [l..r] (0-indexed, inclusive). O(log n)."""
        if l == 0:
            return self.prefix_sum(r)
        return self.prefix_sum(r) - self.prefix_sum(l - 1)

    def point_query(self, i):
        """Get the current value at position i. O(1) via stored data."""
        return self._data[i]

    def __len__(self):
        return self.n

    def __repr__(self):
        return f"FenwickTree(n={self.n}, tree={self.tree[1:]})"


# ─── 2D Fenwick Tree ──────────────────────────────────────────────

class FenwickTree2D:
    """
    2D Binary Indexed Tree for rectangle sum queries and point updates.

    API is 0-indexed: rows 0..R-1, cols 0..C-1.
    Internally 1-indexed.
    """

    def __init__(self, rows, cols):
        """Create an R x C Fenwick tree initialized to 0."""
        self.rows = rows
        self.cols = cols
        self.tree = [[0] * (cols + 1) for _ in range(rows + 1)]

    def update(self, r, c, delta):
        """Add delta to position (r, c) (0-indexed). O(log R * log C)."""
        r += 1  # convert to 1-indexed
        while r <= self.rows:
            j = c + 1  # convert to 1-indexed
            while j <= self.cols:
                self.tree[r][j] += delta
                j += (j & -j)
            r += (r & -r)

    def prefix_sum(self, r, c):
        """Sum of rectangle [(0,0)..(r,c)] (0-indexed, inclusive). O(log R * log C)."""
        r += 1  # convert to 1-indexed
        total = 0
        while r > 0:
            j = c + 1  # convert to 1-indexed
            while j > 0:
                total += self.tree[r][j]
                j -= (j & -j)
            r -= (r & -r)
        return total

    def range_sum(self, r1, c1, r2, c2):
        """
        Sum of rectangle [(r1,c1)..(r2,c2)] (0-indexed, inclusive).
        Uses inclusion-exclusion on prefix sums. O(log R * log C).
        """
        total = self.prefix_sum(r2, c2)
        if r1 > 0:
            total -= self.prefix_sum(r1 - 1, c2)
        if c1 > 0:
            total -= self.prefix_sum(r2, c1 - 1)
        if r1 > 0 and c1 > 0:
            total += self.prefix_sum(r1 - 1, c1 - 1)
        return total


# ─── Counting Inversions ──────────────────────────────────────────

def count_inversions(arr):
    """
    Count inversions in arr using a Fenwick tree.

    An inversion is a pair (i, j) where i < j but arr[i] > arr[j].
    This measures "how unsorted" the array is.

    Approach:
    1. Coordinate compress values to range [0, n)
    2. Process elements left to right
    3. For each element, count how many previously inserted elements
       are greater (using prefix sum on the frequency BIT)
    4. Insert current element into BIT

    Time: O(n log n), Space: O(n)
    """
    if not arr:
        return 0

    # Coordinate compression: map values to ranks 0..n-1
    sorted_unique = sorted(set(arr))
    rank = {v: i for i, v in enumerate(sorted_unique)}
    m = len(sorted_unique)

    bit = FenwickTree(m)
    inversions = 0

    for val in arr:
        r = rank[val]
        # Count elements already inserted with rank > r
        # = total inserted so far - count of elements with rank <= r
        total_inserted = bit.prefix_sum(m - 1) if m > 0 else 0
        leq = bit.prefix_sum(r)
        inversions += total_inserted - leq
        # Insert this element
        bit.update(r, 1)

    return inversions


# ─── Visualization ─────────────────────────────────────────────────

def visualize_bit_structure(n):
    """Show which range each Fenwick tree index is responsible for."""
    print(f"\nBit structure for n = {n}:")
    print(f"{'Index':>6} {'Binary':>8} {'i&-i':>6} {'Range':>12} {'Covers'}")
    print("-" * 55)
    for i in range(1, n + 1):
        lowbit = i & -i
        lo = i - lowbit + 1
        binary = format(i, f'0{n.bit_length() + 1}b')
        print(f"{i:>6} {binary:>8} {lowbit:>6} [{lo:>2}..{i:>2}]    "
              f"{'#' * lowbit}")


def visualize_query_path(n, idx):
    """Show the path a prefix query takes through the tree."""
    print(f"\nPrefix query path for index {idx} (1-indexed):")
    i = idx
    steps = []
    while i > 0:
        lowbit = i & -i
        lo = i - lowbit + 1
        steps.append((i, lo, i))
        i -= lowbit
    print("  " + " + ".join(f"tree[{s[0]}] (covers [{s[1]}..{s[2]}])" for s in steps))


def visualize_update_path(n, idx):
    """Show the path an update takes through the tree."""
    print(f"\nUpdate path for index {idx} (1-indexed):")
    i = idx
    steps = []
    while i <= n:
        steps.append(i)
        i += (i & -i)
    print("  Update: " + " -> ".join(f"tree[{s}]" for s in steps))


# ─── Demo ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("Day 58: Fenwick Tree (Binary Indexed Tree)")
    print("=" * 60)

    # --- Bit structure visualization ---
    visualize_bit_structure(16)

    # --- Query and update path visualization ---
    visualize_query_path(16, 13)
    visualize_update_path(16, 3)

    # --- Basic 1D operations ---
    print("\n" + "=" * 60)
    print("1D Fenwick Tree Demo")
    print("=" * 60)

    arr = [3, 1, 4, 1, 5, 9, 2, 6]
    print(f"\nOriginal array: {arr}")

    ft = FenwickTree(arr)
    print(f"Internal tree:  {ft}")

    # Prefix sums
    print("\nPrefix sums:")
    for i in range(len(arr)):
        print(f"  prefix_sum({i}) = {ft.prefix_sum(i):>3}"
              f"  (actual: {sum(arr[:i+1])})")

    # Range sums
    print("\nRange sums:")
    for l, r in [(0, 3), (2, 5), (4, 7)]:
        print(f"  range_sum({l}, {r}) = {ft.range_sum(l, r):>3}"
              f"  (actual: {sum(arr[l:r+1])})")

    # Point query
    print("\nPoint queries:")
    for i in [0, 3, 7]:
        print(f"  point_query({i}) = {ft.point_query(i)}  (actual: {arr[i]})")

    # Update
    print("\nUpdate: add 10 to index 2")
    ft.update(2, 10)
    print(f"  point_query(2) = {ft.point_query(2)}")
    print(f"  prefix_sum(3) = {ft.prefix_sum(3)}  (was {sum(arr[:4])}, +10 = {sum(arr[:4])+10})")

    # --- O(n) build verification ---
    print("\n" + "-" * 40)
    print("O(n) Build Verification")
    print("-" * 40)
    arr2 = list(range(1, 9))  # [1, 2, 3, 4, 5, 6, 7, 8]
    ft2 = FenwickTree(arr2)
    print(f"Array:  {arr2}")
    print(f"Tree:   {ft2.tree[1:]}")
    print(f"Expected tree[4] = sum(1..4) = 10, got {ft2.tree[4]}")
    print(f"Expected tree[8] = sum(1..8) = 36, got {ft2.tree[8]}")

    # --- 2D Fenwick Tree ---
    print("\n" + "=" * 60)
    print("2D Fenwick Tree Demo")
    print("=" * 60)

    matrix = [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]
    print(f"\nMatrix:")
    for row in matrix:
        print(f"  {row}")

    ft2d = FenwickTree2D(3, 3)
    for r in range(3):
        for c in range(3):
            ft2d.update(r, c, matrix[r][c])

    print(f"\nprefix_sum(1,1) = {ft2d.prefix_sum(1,1)}"
          f"  (1+2+4+5 = {1+2+4+5})")
    print(f"prefix_sum(2,2) = {ft2d.prefix_sum(2,2)}"
          f"  (sum of all = {sum(sum(r) for r in matrix)})")
    print(f"range_sum(1,1,2,2) = {ft2d.range_sum(1,1,2,2)}"
          f"  (5+6+8+9 = {5+6+8+9})")

    # --- Counting Inversions ---
    print("\n" + "=" * 60)
    print("Counting Inversions")
    print("=" * 60)

    test_arrays = [
        [1, 2, 3, 4, 5],     # sorted: 0 inversions
        [5, 4, 3, 2, 1],     # reverse sorted: 10 inversions (n*(n-1)/2)
        [2, 4, 1, 3, 5],     # partially sorted
        [1, 1, 1],           # all equal: 0 inversions
    ]

    for a in test_arrays:
        # Brute force verification
        brute = sum(1 for i in range(len(a)) for j in range(i+1, len(a)) if a[i] > a[j])
        fenwick = count_inversions(a)
        status = "ok" if brute == fenwick else "MISMATCH"
        print(f"  {str(a):>20s} -> inversions = {fenwick:>2} (brute: {brute}) [{status}]")

    print("\nDone.")
