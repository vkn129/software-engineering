# Day 109: van Emde Boas Trees

## Why It Matters

Every comparison-based search is stuck at `Omega(log n)`. A decision tree over
`n` keys has `n!` orderings to distinguish and each comparison yields one bit,
so no comparison algorithm beats `log n`. Day 106's binary search is already
optimal *in that model*.

van Emde Boas (vEB) trees get `O(log log U)` by leaving the model. They never
compare two keys. They **decompose the bits of a key**: the high half of the
bits picks a cluster, the low half picks a slot inside it. That is arithmetic
on the key, not a comparison — the same escape hatch radix sort uses to beat
`n log n`.

The price is stated up front: keys must be integers from a **known, bounded
universe** `{0, 1, ..., U-1}`. No universe bound, no vEB.

For `U = 2^32` a successor query costs 5 levels of recursion. Binary search
over 4 billion sorted keys costs 32 probes.

Where the bounded-universe + summary idea actually ships:

- **Linux O(1) scheduler** (2.6 era): a 140-bit priority bitmap plus
  `find_first_bit`. That is a one-level vEB summary — "which cluster is
  non-empty?" answered in a single word scan.
- **Buddy and slab allocators**: free-list bitmaps with a summary word per
  order, so "smallest free block at least this big" is a successor query.
- **Kernel ID allocators** (`IDR`/`IDA`): a radix tree of bitmaps over a
  bounded integer ID space — same layering, wider fan-out.
- **Hardware priority encoders / `find first set`**: the `U = 64` base case
  implemented in silicon, one cycle.

Full recursive vEB is rare in production, and the honest reason is in the
Space section below.

## The Universe Assumption vs Day 108's Distribution Assumption

Both days beat `log n`. They beat it by assuming different things, and they
fail differently.

| | Day 108 interpolation search | Day 109 vEB |
|---|---|---|
| Assumption | keys are **uniformly distributed** over their range | keys come from a **bounded universe** `U` |
| Bound type | `O(log log n)` **expected**, average case | `O(log log U)` **worst case** |
| When the assumption breaks | exponential/clustered data degrades to `O(n)` | there is nothing to break — the bound holds for every input |
| How you verify it | you cannot, cheaply; you must know your data | you check `max_key < U`, a one-line assertion |
| Cost of the guarantee | none (it is free, and unreliable) | space, see below |
| `n` vs `U` | scales with the number of keys | scales with the *size of the key space*, not the key count |

Interpolation search makes a **statistical** bet about the data. vEB makes a
**structural** bet about the type. Structural bets are checkable; statistical
bets are not. That is why vEB's bound is worst case and interpolation's is not.

Note the `U` in `log log U`, not `n`. Inserting more keys never slows a vEB
down. Widening the key type from 32 to 64 bits does — by exactly one level.

## The Recursion

Let `U = 2^(2k)` so `sqrt(U)` is an integer power of two. Split every key `x`
into two halves of its bit pattern:

```
high(x) = x // sqrt(U)      # which cluster       (upper bits)
low(x)  = x %  sqrt(U)      # slot in the cluster (lower bits)
index(h, l) = h * sqrt(U) + l
```

A vEB node of universe `U` holds:

- `min`, `max` — the smallest and largest keys stored here
- `cluster[0 .. sqrt(U)-1]` — `sqrt(U)` child vEB nodes, each over universe `sqrt(U)`
- `summary` — one more vEB node over universe `sqrt(U)`, storing **which
  cluster indices are non-empty**

When `U == 2` the node is just the pair `(min, max)` over `{0, 1}`. That is
the base case; no children.

```
U = 16, keys = {2, 3, 4, 9, 15},  sqrt(U) = 4

  min=2  max=15
  summary: {0, 1, 2, 3}       <- clusters 0,1,2,3 are non-empty
  cluster[0]: {3}             <- key 3   (min=2 is NOT stored below)
  cluster[1]: {0}             <- key 4
  cluster[2]: {1}             <- key 9
  cluster[3]: {3}             <- key 15
```

## The One Trick That Makes It `log log U`

`min` is stored **only** in the node, never inside any cluster. `max` is
stored in both places.

That looks like a bookkeeping detail. It is the entire algorithm.

Consider `successor(x)`:

1. If `x < min`, answer is `min`. **Done, no recursion.**
2. Otherwise look at `cluster[high(x)]`. If it has an element above `low(x)`,
   recurse **into that cluster** and stop.
3. Otherwise ask `summary` for the next non-empty cluster above `high(x)`,
   then take that cluster's `min` — which is `O(1)` because min is cached in
   the node, not buried in a recursive lookup.

Each branch makes **exactly one** recursive call, on a universe of size
`sqrt(U)`:

```
T(U) = T(sqrt(U)) + O(1)
```

Substituting `m = log2(U)` turns `sqrt(U)` into `m/2`:

```
T'(m) = T'(m/2) + O(1)  =>  T'(m) = O(log m) = O(log log U)
```

Without the min-outside rule, step 3 would need a recursive `summary` query
*and* a recursive `min` lookup in the found cluster — two recursive calls,
`T(U) = 2*T(sqrt(U)) + O(1) = O(log U)`. All the way back to binary search.

`insert` uses the mirror trick: inserting into an **empty** cluster is `O(1)`
(just set its min and max), and only then do we touch the summary. So insert
also makes one real recursive call, not two.

## Space, and Why x-fast / y-fast Tries Exist

The textbook vEB allocates all `sqrt(U)` child pointers eagerly. That gives:

```
S(U) = (sqrt(U) + 1) * S(sqrt(U)) + O(1)  =>  S(U) = Theta(U)
```

`Theta(U)` — **independent of how many keys you store**. A vEB over 32-bit
keys holding 10 elements still wants 4 billion slots. That is why you rarely
see one in production.

Three standard fixes:

- **Lazy child allocation** (what this day's implementation does): create a
  cluster only on first insert, keep them in a dict. Space becomes
  `O(n * log log U)` — good enough to actually run, and the time bounds are
  unchanged. Cost: a hash lookup per level instead of an array index.
- **x-fast tries** (Willard 1983): store the `log U` levels of the binary
  trie over the keys in hash tables, one per level, and binary-search the
  *levels* for the deepest matching prefix. `O(log log U)` query, `O(n log U)`
  space, but `O(log U)` update.
- **y-fast tries** (Willard 1983): bucket the keys into `O(n / log U)` groups
  of `Theta(log U)` consecutive keys, put one representative per group into
  an x-fast trie, and keep each group in a balanced BST. `O(log log U)`
  query *and* expected `O(log log U)` update, in `O(n)` space — space
  proportional to the key count, not the universe.

y-fast is the version you would actually deploy: vEB's time bound at a sorted
array's space bound. It is strictly more complicated, which is why we build
vEB first — y-fast is "vEB over a summary of representatives".

## Complexity

| Operation | vEB | Balanced BST | Sorted array + binary search | Hash set |
|-----------|-----|--------------|------------------------------|----------|
| `insert` | O(log log U) | O(log n) | O(n) | O(1) avg |
| `delete` | O(log log U) | O(log n) | O(n) | O(1) avg |
| `member` | O(log log U) | O(log n) | O(log n) | O(1) avg |
| `successor` / `predecessor` | O(log log U) | O(log n) | O(log n) | **O(n)** |
| `min` / `max` | O(1) | O(log n) | O(1) | O(n) |
| Space (textbook) | Theta(U) | O(n) | O(n) | O(n) |
| Space (lazy / y-fast) | O(n log log U) / O(n) | O(n) | O(n) | O(n) |

The column that matters is `successor`. A hash set answers `member` faster
than anything here and answers `successor` not at all — it destroys the order
information. vEB is what you reach for when you need **ordered** queries on
integer keys and `log n` is too slow.

## Failure Modes

| Failure | When | Fix |
|---------|------|-----|
| Key out of universe | `insert(U)` or a negative key | Validate at the boundary; vEB has no room to grow. Rebuild with a larger `U`, or offset the key space |
| `U` not a power of two | `sqrt(U)` is not an integer, the bit split misaligns | Round `U` up to the next power of two; the padding costs nothing with lazy clusters |
| Memory blow-up | eager child arrays with large `U` | Lazy clusters, or y-fast tries |
| Cache misses dominate | `log log U` pointer hops, each a random address | For `U <= 2^16` a flat bitmap plus `find_first_set` beats vEB outright — fewer levels, sequential words |
| Deleting a non-member corrupts min/max | textbook `delete` assumes the key is present | Check `member(x)` first (this implementation does) |
| `min` double-counted | forgetting that `min` is *not* stored in any cluster | Handle `x == min` explicitly in `delete` by promoting the next key into the min slot |
| Float or string keys | there is no bit decomposition to do | vEB does not apply. Use a BST, or map keys to integer ranks first |

## Checkpoint Questions

1. Comparison search cannot beat `Omega(log n)`. Explain precisely which
   assumption of that lower bound vEB violates.
2. Why is the bound `log log U` and not `log log n`? Construct a case where
   vEB is *worse* than a sorted array.
3. Storing `min` outside every cluster is what makes each operation recurse
   once instead of twice. Walk through `successor` and show where the second
   recursive call would appear without it.
4. Solve `T(U) = T(sqrt(U)) + O(1)` by substituting `m = log U`. Where does
   the second `log` come from?
5. Day 108 also claims `log log`. State each day's assumption and what
   happens to each bound when its assumption is false.
6. Why is textbook vEB space `Theta(U)` rather than `O(n)`, and what exactly
   does a y-fast trie replace to get back to `O(n)`?
7. When would you pick a flat bitmap with `find_first_set` over a vEB tree?
