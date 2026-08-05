# Day 174: Persistent Data Structures

## Why Persistent Structures Matter

**Persistence** = every modification produces a new version, without
destroying the old one. You can still query any past version at any time.

This sounds like immutability — but persistent structures share **most of
the memory** between versions, achieving O(log N) extra memory per update
instead of O(N).

Applications:
- **Functional languages**: Clojure, Haskell, OCaml use persistent
  vectors/maps everywhere
- **Undo/redo**: editors, IDEs keep version history cheaply
- **MVCC databases**: PostgreSQL, Datomic keep all historical versions
- **Time-travel debugging**: rr, replay.io, Pernosco
- **Git**: every commit is a snapshot, with shared subtrees in objects
- **K-th order statistics on subarrays**: persistent BIT / segment tree
- **Versioned arrays**: undo a single index update in O(1)
- **Algorithm contests**: "k-th smallest in range [l, r]"

## Path Copying — the Core Trick

A segment tree has O(N) nodes. A point update touches **only O(log N)
nodes on a single root-to-leaf path**.

If we copy just those O(log N) nodes and share the rest with the old
version, we get a new tree that:
- represents the updated state
- shares O(N - log N) nodes with the previous version
- uses O(log N) **extra** memory per update

Both old and new roots remain valid. We can keep an array of roots,
one per version.

```
old tree:                        new tree (after update at leaf 5):
       [root]                            [root']
       /    \                            /    \
     [A]    [B]              shares [A]      [B'] (copy)
     / \    / \                            / \
    [.][.] [.][.]                         [.][.]  ... only touched path copied
```

## Persistent Segment Tree (Point Update, Range Sum)

Each node has `left, right, sum`. Updates create new nodes along the path:

```python
class Node:
    __slots__ = ('left', 'right', 'sum')
    def __init__(self, left=None, right=None, sum=0):
        self.left = left
        self.right = right
        self.sum = sum

def build(arr, l, r):
    if l == r:
        return Node(sum=arr[l])
    m = (l + r) // 2
    lc = build(arr, l, m)
    rc = build(arr, m + 1, r)
    return Node(lc, rc, lc.sum + rc.sum)

def update(node, l, r, idx, val):
    if l == r:
        return Node(sum=val)
    m = (l + r) // 2
    if idx <= m:
        new_l = update(node.left, l, m, idx, val)
        return Node(new_l, node.right, new_l.sum + node.right.sum)
    else:
        new_r = update(node.right, m + 1, r, idx, val)
        return Node(node.left, new_r, node.left.sum + new_r.sum)

def query(node, l, r, ql, qr):
    if qr < l or r < ql:
        return 0
    if ql <= l and r <= qr:
        return node.sum
    m = (l + r) // 2
    return query(node.left, l, m, ql, qr) + query(node.right, m + 1, r, ql, qr)
```

Each `update` creates O(log N) new nodes. Each `query` is O(log N) reads.
Maintain a list `versions[t]` of roots.

## Versioned Arrays

A "versioned array" is just a persistent segment tree where the segment tree
stores values, not sums. Updates → new version. Reads → query a specific
version.

Memory: O(N) initial build, O(log N) per update. Many updates total to
O(U log N) for U updates — far better than O(U·N) for naive copying.

## Application: K-th Smallest in Range [l, r]

**Classic persistent segment tree problem**.

Compress values to ranks [0..V-1]. Build a persistent segment tree where
each version represents counts of values seen in `a[0..i]`. Insert a[i]
into version i to get version i+1 (so we have N+1 versions).

To find k-th smallest in a[l..r]:
- Query difference of versions `r+1` and `l`.
- This gives a "histogram of values seen in [l..r]".
- Binary-search down the tree: at each node, if left child's count ≥ k,
  descend left; else subtract left count from k and descend right.

```python
def kth_smallest(left_root, right_root, l, r, k):
    if l == r:
        return l
    m = (l + r) // 2
    left_count = right_root.left.sum - left_root.left.sum
    if k <= left_count:
        return kth_smallest(left_root.left, right_root.left, l, m, k)
    return kth_smallest(left_root.right, right_root.right, m+1, r, k - left_count)
```

Time per query: O(log V). Total memory: O((N + Q) log V).

## Persistent vs Immutable

Both terms are sometimes conflated:

- **Immutable**: object cannot change. Period.
- **Persistent**: old versions remain accessible after "updates" (which
  produce new versions). Implementations are usually built on immutability.

So "persistent" implies "immutable", but persistence is a stronger guarantee
about the entire **history**.

## Garbage Collection of Versions

If you only ever need the latest K versions, you can discard older roots
and let GC reclaim unreferenced nodes.

If you keep ALL versions forever, memory grows by O(log N) per update.
For 10^6 updates on a 10^5 array, that's ~10^6 · 17 ≈ 17 · 10^6 nodes.

## Connection to Earlier Days

- **Day 52 Segment tree**: persistent segment tree adds versioning
- **Day 53 Lazy segment tree**: persistent + lazy is possible but tricky
- **Day 56 BIT**: persistent BIT exists but is less common
- **Day 173 Centroid decomposition**: persistent structures help with
  "answer queries about distance distribution"

## Failure Modes

- **Reference cycles**: there shouldn't be any, but careless mutation
  can break the immutability invariant
- **Path copying for range updates**: lazy propagation requires copying
  ALL nodes touched by the lazy tag, not just O(log N). Be careful.
- **Recursion depth**: Python's 1000 default limit is fine for N≤2^15;
  bigger needs setrecursionlimit
- **Mutable shared substructure**: bug city. Make Node's fields `__slots__`
  and never re-assign them after construction

## Real-World Usage

| System | Application | Why persistent |
|--------|-------------|----------------|
| PostgreSQL | MVCC: readers see snapshot at txn start | Snapshot isolation |
| Datomic | All data is immutable, time-travel queries | Audit + reproducibility |
| Clojure / Scala | persistent vectors / maps (HAMT) | Functional purity |
| Git | Objects + tree references | Cheap history |
| Editors | Undo/redo stacks | User history |
| Cosmos DB / DynamoDB | Multi-version snapshots | Point-in-time restore |

## Checkpoint Questions

1. Why does path copying give O(log N) memory per update, not O(N)?
2. What invariant must Nodes maintain to keep persistence safe?
3. Why is "kth smallest in [l,r]" naturally solved by persistent segtree?
4. How would lazy propagation interact with persistence?
5. What's the difference between persistent and immutable?
6. Sketch how Git's tree objects are a persistent dictionary.
