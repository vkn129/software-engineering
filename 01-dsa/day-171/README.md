# Day 171: Offline Algorithms — Mo's Algorithm

## Why Offline Algorithms Matter

**Online** algorithms answer queries as they arrive — no peeking at future
queries. Most data structures (segment trees, BITs) work online.

**Offline** algorithms see **all queries up front**, then reorder them to
amortize work. This trades latency for throughput, and often beats any online
algorithm by a polynomial factor.

- **Mo's algorithm**: O((N+Q) · sqrt(N)) for range queries
- **Offline LCA**: Tarjan's algorithm using Union-Find
- **Offline RMQ**: 2D problem reductions, sweep line
- **Offline DSU**: divide-and-conquer over query time
- **Batch graph algorithms**: process all edge insertions then queries

Use when:
- You can collect all queries first (batch reporting, log analysis)
- No online data structure exists (e.g., count distinct elements in range)
- You need raw throughput, not low latency

## The Idea: Sqrt Decomposition

Split a length-N array into blocks of size sqrt(N). Each query [l, r] either
lies in one block or spans several.

```
N=16, block=4:  | 0..3 | 4..7 | 8..11 | 12..15 |
```

Maintain block summaries (sum, min, count, etc). Query [l, r]:
- Partial-block prefix: scan l..end_of_block(l)
- Whole blocks: read precomputed summary
- Partial-block suffix: scan start_of_block(r)..r

Both prefix and suffix are O(sqrt(N)). Whole-block read is O(1) each, and
there are at most sqrt(N) blocks. **Total O(sqrt(N)) per query.**

## Mo's Algorithm

Beautiful application of sqrt decomposition. Solves problems like:
- "How many distinct elements in array[l..r]?"
- "Sum of squares of frequencies in array[l..r]?"
- "Range mode (most frequent element)"

These have **no efficient online structure**.

### The Trick

Maintain a sliding window [L, R] over the array. We can move:
- R → R+1: add array[R+1] (O(1) update)
- R → R-1: remove array[R] (O(1))
- L → L-1: add array[L-1]
- L → L+1: remove array[L]

If we process queries in arbitrary order, total pointer moves can be
O(N · Q). But if we **reorder queries cleverly**, pointer moves drop to
**O((N + Q) · sqrt(N))**.

### The Ordering

Bucket queries by `floor(l / sqrt(N))`. Within a bucket, sort by `r`.

```
Sort key:  (l // block_size, r)
```

Within a bucket, l varies by at most sqrt(N), and r is monotone. Across
buckets, r resets but l advances. The pointer moves total to O((N+Q)·sqrt(N)).

### Even Better: Hilbert Curve / Odd-Even Blocks

For the **odd-even trick**, alternate r-direction in successive buckets:
- Even bucket: sort by r ascending
- Odd bucket: sort by r descending

This avoids the "r jumps back to 0" cost at bucket boundaries. About 2x
speedup in practice.

## Pseudocode

```python
def mos_algorithm(arr, queries):
    n = len(arr)
    block = int(n ** 0.5)
    Q = sorted(enumerate(queries),
               key=lambda iq: (iq[1][0] // block, iq[1][1]))
    answer = [0] * len(queries)
    L, R = 0, -1   # current window [L..R]
    state = State()
    for i, (l, r) in Q:
        while R < r:
            R += 1; state.add(arr[R])
        while R > r:
            state.remove(arr[R]); R -= 1
        while L < l:
            state.remove(arr[L]); L += 1
        while L > l:
            L -= 1; state.add(arr[L])
        answer[i] = state.query()
    return answer
```

The order of these `while` loops matters — always expand before shrinking
to avoid an empty window with invalid indices.

## Complexity Analysis

For each bucket (sqrt(N) of them):
- l stays within a block → l moves at most sqrt(N) per query, sqrt(N) queries
  in bucket → O(N) for l moves per bucket → O(sqrt(N)) buckets * N moves
  is wrong... let's redo:

- Per bucket: l moves ≤ sqrt(N) per query. Bucket has ≤ Q/sqrt(N) queries.
  Total l moves in bucket: O(Q). All buckets combined: O(Q·sqrt(N))? Wait.

Let me redo carefully:
- l moves: bounded by sqrt(N) per query within a bucket. Q queries → O(Q·sqrt(N)).
- r moves: monotone within a bucket → O(N) per bucket × sqrt(N) buckets → O(N·sqrt(N)).
- **Total: O((N + Q) · sqrt(N))**

For N = Q = 10^5, that's ~10^5 · 316 = 3 · 10^7. Fast in Python.

## Where Mo's Beats Segment Trees

Segment trees handle queries where the answer combines associatively:
sum, min, max, gcd. They're **online** and O(log N) per query.

But for queries like "count distinct" or "mode" or "k-th frequency",
there's no associative merge operator. Segment trees don't directly work.

Mo's algorithm exploits the **sliding window** structure: adding/removing
one element is O(1), so the algorithm doesn't need any merge structure.

## Sqrt Decomposition (Online)

Without query reordering, sqrt decomposition still gives O(sqrt(N)) per
range query on associative ops:

```python
class SqrtDecomp:
    def __init__(self, arr):
        self.arr = arr[:]
        self.n = len(arr)
        self.block = int(self.n ** 0.5) + 1
        self.blocks = [0] * (self.n // self.block + 1)
        for i, v in enumerate(arr):
            self.blocks[i // self.block] += v

    def update(self, i, v):
        self.blocks[i // self.block] += v - self.arr[i]
        self.arr[i] = v

    def range_sum(self, l, r):
        # ... combine full blocks + edges
```

Worse than segment tree's O(log N), but simpler to code and lets you handle
oddball queries that segment trees can't (mode, count-distinct).

## Connection to Earlier Days

- **Day 52 Segment tree**: online range queries with associative merge
- **Day 56 BIT**: even simpler online prefix sums
- **Day 18 DFS**: Mo's can be extended to trees via Euler tour (Mo on trees)
- **Day 86 Union-Find**: alternative offline DSU technique with rollback

Mo's is the **escape hatch** when associativity is missing.

## Failure Modes

- **Empty window**: be careful with L > R order; always expand first
- **State must be reversible**: add and remove must be inverses
- **Heavy state**: if "add" is O(log N), total is O((N+Q) sqrt(N) log N) —
  still fine but watch the constants
- **Updates between queries**: vanilla Mo's doesn't handle updates. Use
  **Mo's with updates** (3D sort: l/block, r/block, t) for O(N^(5/3))
- **Tree paths**: use Euler tour to flatten, then Mo's on the flattened array

## Real-World Usage

| System | Application | Why offline |
|--------|-------------|-------------|
| Competitive programming | Range distinct, mode, kth-frequency | No online structure |
| Bioinformatics | Read alignment, k-mer counting | Batch query workload |
| Analytics | Cohort range stats, log analysis | All queries known upfront |
| Compilers | Live variable analysis | Block-by-block summaries |
| Network monitoring | Sliding window aggregates | Window slides predictably |

## Checkpoint Questions

1. Why O(sqrt(N))? Where does the square root come from?
2. Why must the state operations be O(1) for Mo's to hit O((N+Q)·sqrt(N))?
3. When would you prefer sqrt decomposition over a segment tree?
4. Why doesn't Mo's algorithm work for online queries?
5. How does Mo's on trees use Euler tour?
6. Modify Mo's to support a single point update interleaved with queries.
   How does complexity change?
