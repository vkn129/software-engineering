"""
Day 174: Persistent Segment Tree — From Scratch

Path copying: every point update creates O(log N) new nodes and shares
the rest with previous versions. All historical versions remain queryable.

Time:
  build:  O(N)
  update: O(log N) per version
  query:  O(log N)
Space:
  initial: O(N)
  per update: O(log N) extra
"""

import sys
sys.setrecursionlimit(10**6)


# ---------------------------------------------------------------------------
# 1. Node class — immutable after construction
# ---------------------------------------------------------------------------

class Node:
    __slots__ = ('left', 'right', 'sum')

    def __init__(self, left=None, right=None, sum=0):
        self.left = left
        self.right = right
        self.sum = sum


# ---------------------------------------------------------------------------
# 2. Persistent Segment Tree
# ---------------------------------------------------------------------------

class PersistentSegTree:
    """
    Persistent segment tree over indices [0, n-1].
    Supports: build from array, point-update -> new version, range-sum on any version.
    """

    def __init__(self, arr):
        self.n = len(arr)
        # Versions stored as root pointers; versions[0] = initial.
        self.versions = [self._build(arr, 0, self.n - 1)]

    def _build(self, arr, l, r):
        if l == r:
            return Node(sum=arr[l])
        m = (l + r) // 2
        lc = self._build(arr, l, m)
        rc = self._build(arr, m + 1, r)
        return Node(lc, rc, lc.sum + rc.sum)

    def _update(self, node, l, r, idx, val):
        if l == r:
            return Node(sum=val)
        m = (l + r) // 2
        if idx <= m:
            new_l = self._update(node.left, l, m, idx, val)
            return Node(new_l, node.right, new_l.sum + node.right.sum)
        else:
            new_r = self._update(node.right, m + 1, r, idx, val)
            return Node(node.left, new_r, node.left.sum + new_r.sum)

    def _query(self, node, l, r, ql, qr):
        if qr < l or r < ql:
            return 0
        if ql <= l and r <= qr:
            return node.sum
        m = (l + r) // 2
        return (self._query(node.left, l, m, ql, qr) +
                self._query(node.right, m + 1, r, ql, qr))

    def update(self, version, idx, val):
        """Create a new version derived from `version` by setting arr[idx] = val.
        Returns new version index."""
        new_root = self._update(self.versions[version], 0, self.n - 1, idx, val)
        self.versions.append(new_root)
        return len(self.versions) - 1

    def range_sum(self, version, l, r):
        """Sum of arr[l..r] in the given version."""
        return self._query(self.versions[version], 0, self.n - 1, l, r)


# ---------------------------------------------------------------------------
# 3. Versioned Array (single-element get) built on persistent segtree
# ---------------------------------------------------------------------------

class VersionedArray:
    """
    Versioned array via persistent segment tree.
    set(version, i, v) -> new version
    get(version, i)    -> value of arr[i] in that version
    """

    def __init__(self, arr):
        self.st = PersistentSegTree(arr)

    def set(self, version, i, v):
        return self.st.update(version, i, v)

    def get(self, version, i):
        return self.st.range_sum(version, i, i)


# ---------------------------------------------------------------------------
# 4. K-th smallest in range using persistent segtree (compressed values)
# ---------------------------------------------------------------------------

class KthSmallestRangeQuery:
    """
    For static array `arr`, answer k-th smallest in arr[l..r] in O(log V).
    Builds N+1 persistent versions, each adding one element.
    """

    def __init__(self, arr):
        self.n = len(arr)
        # Coordinate compression
        sorted_vals = sorted(set(arr))
        self.vals = sorted_vals
        rank = {v: i for i, v in enumerate(sorted_vals)}
        self.v_size = len(sorted_vals)

        empty = self._build(0, self.v_size - 1)
        self.versions = [empty]
        cur = empty
        for x in arr:
            cur = self._update(cur, 0, self.v_size - 1, rank[x])
            self.versions.append(cur)

    def _build(self, l, r):
        if l == r:
            return Node(sum=0)
        m = (l + r) // 2
        lc = self._build(l, m)
        rc = self._build(m + 1, r)
        return Node(lc, rc, 0)

    def _update(self, node, l, r, idx):
        if l == r:
            return Node(sum=node.sum + 1)
        m = (l + r) // 2
        if idx <= m:
            new_l = self._update(node.left, l, m, idx)
            return Node(new_l, node.right, new_l.sum + node.right.sum)
        else:
            new_r = self._update(node.right, m + 1, r, idx)
            return Node(node.left, new_r, node.left.sum + new_r.sum)

    def kth(self, l, r, k):
        """k-th smallest in arr[l..r], k >= 1."""
        return self._kth(self.versions[l], self.versions[r + 1],
                         0, self.v_size - 1, k)

    def _kth(self, ln, rn, l, r, k):
        if l == r:
            return self.vals[l]
        m = (l + r) // 2
        left_count = rn.left.sum - ln.left.sum
        if k <= left_count:
            return self._kth(ln.left, rn.left, l, m, k)
        return self._kth(ln.right, rn.right, m + 1, r, k - left_count)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_persistent_basic():
    print("=" * 60)
    print("DEMO 1: Persistent Segment Tree — versioned sums")
    print("=" * 60)
    arr = [1, 2, 3, 4, 5]
    st = PersistentSegTree(arr)
    print(f"  v0 (initial): {arr}")
    print(f"    sum [0..4] = {st.range_sum(0, 0, 4)}")
    v1 = st.update(0, 2, 100)   # arr[2] = 100 in new version
    print(f"  v1 after arr[2]=100")
    print(f"    v1 sum [0..4] = {st.range_sum(v1, 0, 4)}")
    print(f"    v0 sum [0..4] = {st.range_sum(0, 0, 4)}  (unchanged!)")
    v2 = st.update(v1, 0, 50)   # arr[0]=50 from v1
    print(f"  v2 after arr[0]=50 (from v1)")
    print(f"    v2 sum [0..4] = {st.range_sum(v2, 0, 4)}")
    print(f"    v1 sum [0..4] = {st.range_sum(v1, 0, 4)}  (still 110)")


def demo_versioned_array():
    print("\n" + "=" * 60)
    print("DEMO 2: Versioned Array — undo via prior version")
    print("=" * 60)
    va = VersionedArray([10, 20, 30, 40, 50])
    print(f"  v0: index 2 = {va.get(0, 2)} (expected 30)")
    v1 = va.set(0, 2, 999)
    print(f"  v1: set [2]=999. v1[2]={va.get(v1, 2)}, v0[2]={va.get(0, 2)}")
    v2 = va.set(v1, 3, 888)
    print(f"  v2: set [3]=888. v2={[va.get(v2, i) for i in range(5)]}")
    print(f"  v1={[va.get(v1, i) for i in range(5)]}")
    print(f"  v0={[va.get(0, i) for i in range(5)]}")


def demo_kth():
    print("\n" + "=" * 60)
    print("DEMO 3: K-th Smallest in Range")
    print("=" * 60)
    arr = [5, 1, 4, 2, 8, 3, 7, 6]
    k_struct = KthSmallestRangeQuery(arr)
    print(f"  arr = {arr}")
    queries = [(0, 7, 1), (0, 7, 4), (2, 5, 2), (3, 6, 3), (0, 3, 2)]
    for l, r, k in queries:
        ans = k_struct.kth(l, r, k)
        sub_sorted = sorted(arr[l:r+1])
        print(f"  k-th={k} in arr[{l}..{r}] = {ans}, "
              f"check sorted[{k-1}]={sub_sorted[k-1]}: "
              f"{'OK' if ans == sub_sorted[k-1] else 'MISMATCH'}")


if __name__ == "__main__":
    demo_persistent_basic()
    demo_versioned_array()
    demo_kth()
