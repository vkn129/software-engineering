"""
Day 171: Mo's Algorithm + Sqrt Decomposition — From Scratch

Offline range queries via clever query reordering.
Time: O((N + Q) * sqrt(N))

Applied to:
  1. Range distinct count (no online structure works)
  2. Sum of frequency squares (Yandex problem)
  3. Sqrt decomposition for online range sum

Builds on Day 52 (segment trees) where merge associativity is required.
"""

from collections import defaultdict
import random
import time


# ---------------------------------------------------------------------------
# 1. Online Sqrt Decomposition (range sum)
# ---------------------------------------------------------------------------

class SqrtDecomp:
    """
    Range sum + point update in O(sqrt(N)) per operation.
    Simpler than a segment tree, but slower than O(log N).
    """

    def __init__(self, arr):
        self.arr = arr[:]
        self.n = len(arr)
        self.block = max(1, int(self.n ** 0.5))
        self.num_blocks = (self.n + self.block - 1) // self.block
        self.blocks = [0] * self.num_blocks
        for i, v in enumerate(arr):
            self.blocks[i // self.block] += v

    def update(self, i, v):
        self.blocks[i // self.block] += v - self.arr[i]
        self.arr[i] = v

    def range_sum(self, l, r):
        """Sum of arr[l..r] inclusive."""
        bl = l // self.block
        br = r // self.block
        total = 0
        if bl == br:
            for i in range(l, r + 1):
                total += self.arr[i]
            return total
        # Left partial
        for i in range(l, (bl + 1) * self.block):
            total += self.arr[i]
        # Full blocks
        for b in range(bl + 1, br):
            total += self.blocks[b]
        # Right partial
        for i in range(br * self.block, r + 1):
            total += self.arr[i]
        return total


# ---------------------------------------------------------------------------
# 2. Mo's Algorithm — range distinct count
# ---------------------------------------------------------------------------

def range_distinct_mo(arr, queries):
    """
    For each query (l, r), return count of distinct elements in arr[l..r].
    Uses Mo's algorithm: O((N+Q) * sqrt(N)).
    queries: list of (l, r) with 0 <= l <= r < N
    """
    n = len(arr)
    block = max(1, int(n ** 0.5))

    indexed = list(enumerate(queries))
    # Odd-even trick: for even bucket sort r asc, odd bucket sort r desc
    def key(item):
        i, (l, r) = item
        b = l // block
        return (b, r if b % 2 == 0 else -r)
    indexed.sort(key=key)

    freq = defaultdict(int)
    distinct = 0
    L, R = 0, -1
    answer = [0] * len(queries)

    def add(x):
        nonlocal distinct
        if freq[x] == 0:
            distinct += 1
        freq[x] += 1

    def remove(x):
        nonlocal distinct
        freq[x] -= 1
        if freq[x] == 0:
            distinct -= 1

    for qi, (l, r) in indexed:
        # Always expand first to avoid invalid empty window
        while R < r:
            R += 1
            add(arr[R])
        while L > l:
            L -= 1
            add(arr[L])
        while R > r:
            remove(arr[R])
            R -= 1
        while L < l:
            remove(arr[L])
            L += 1
        answer[qi] = distinct
    return answer


def range_distinct_brute(arr, queries):
    """Reference O(N * Q) implementation."""
    return [len(set(arr[l:r+1])) for l, r in queries]


# ---------------------------------------------------------------------------
# 3. Mo's Algorithm — sum of frequency squares
# ---------------------------------------------------------------------------

def range_freq_squared(arr, queries):
    """
    For each query, return sum_{x} freq(x)^2 over arr[l..r].
    Classic 'Yandex' problem — needs Mo's, no associative segment tree works.
    """
    n = len(arr)
    block = max(1, int(n ** 0.5))
    indexed = list(enumerate(queries))
    indexed.sort(key=lambda item: (item[1][0] // block,
                                   item[1][1] if (item[1][0] // block) % 2 == 0
                                   else -item[1][1]))

    freq = defaultdict(int)
    total = 0
    L, R = 0, -1
    answer = [0] * len(queries)

    def add(x):
        nonlocal total
        # delta = (f+1)^2 - f^2 = 2f + 1
        total += 2 * freq[x] + 1
        freq[x] += 1

    def remove(x):
        nonlocal total
        # delta = (f-1)^2 - f^2 = -2f + 1
        freq[x] -= 1
        total += -2 * freq[x] - 1

    for qi, (l, r) in indexed:
        while R < r:
            R += 1; add(arr[R])
        while L > l:
            L -= 1; add(arr[L])
        while R > r:
            remove(arr[R]); R -= 1
        while L < l:
            remove(arr[L]); L += 1
        answer[qi] = total
    return answer


def range_freq_squared_brute(arr, queries):
    out = []
    for l, r in queries:
        c = defaultdict(int)
        for x in arr[l:r+1]:
            c[x] += 1
        out.append(sum(v*v for v in c.values()))
    return out


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_sqrt():
    print("=" * 60)
    print("DEMO 1: Sqrt Decomposition (online range sum + update)")
    print("=" * 60)
    arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    sd = SqrtDecomp(arr)
    print(f"  arr: {arr}, block={sd.block}")
    print(f"  sum [2..6] = {sd.range_sum(2, 6)}  (expected 5+7+9+11+13=45)")
    sd.update(3, 100)  # arr[3]: 7 -> 100
    print(f"  after update arr[3]=100, sum [2..6] = {sd.range_sum(2, 6)} (expected 138)")


def demo_mo_distinct():
    print("\n" + "=" * 60)
    print("DEMO 2: Mo's Algorithm — Range Distinct Count")
    print("=" * 60)
    random.seed(42)
    n, q = 2000, 2000
    arr = [random.randint(0, 50) for _ in range(n)]
    queries = []
    for _ in range(q):
        l = random.randint(0, n - 1)
        r = random.randint(l, n - 1)
        queries.append((l, r))

    t1 = time.perf_counter()
    a_mo = range_distinct_mo(arr, queries)
    t_mo = time.perf_counter() - t1

    t1 = time.perf_counter()
    a_brute = range_distinct_brute(arr, queries)
    t_brute = time.perf_counter() - t1

    print(f"  n={n}, q={q}")
    print(f"    Mo's:    {t_mo:.3f}s")
    print(f"    Brute:   {t_brute:.3f}s")
    print(f"    Match:   {a_mo == a_brute}")
    print(f"    Speedup: {t_brute/t_mo:.1f}x")


def demo_freq_sq():
    print("\n" + "=" * 60)
    print("DEMO 3: Mo's Algorithm — Sum of Frequency Squares")
    print("=" * 60)
    arr = [1, 1, 2, 1, 3, 2, 1]
    queries = [(0, 6), (1, 4), (2, 5), (0, 3)]
    a_mo = range_freq_squared(arr, queries)
    a_br = range_freq_squared_brute(arr, queries)
    for q, m, b in zip(queries, a_mo, a_br):
        print(f"  query {q}: mo={m}, brute={b}")
    print(f"  Match: {a_mo == a_br}")


if __name__ == "__main__":
    demo_sqrt()
    demo_mo_distinct()
    demo_freq_sq()
