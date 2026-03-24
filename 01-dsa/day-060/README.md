# Day 60: B+ Trees — Why Every Database Index Is a Linked List of Sorted Pages

## Why This Exists

B-trees store data (key-value pairs) in every node — internal and leaf. This works well for point lookups, but consider a range query: "give me all users aged 25 to 35." In a B-tree, you'd do an in-order traversal, which means repeatedly going up and down the tree. Each "go back to parent" step is an extra disk seek.

A **B+ tree** fixes this with two structural changes:
1. **Internal nodes store only keys** (separator/fence keys) — they exist purely for routing. No data lives there.
2. **Leaf nodes form a doubly or singly linked list** — once you find the starting leaf, you follow pointers to scan sequentially.

The result: range queries become **O(log n) to find the first leaf, then O(k) to scan k results** by following the leaf chain. No backtracking up the tree.

This is not a minor optimization. It is *the* fundamental structure behind virtually every relational database index:
- **MySQL InnoDB** — clustered index is a B+ tree where leaf nodes contain the actual row data
- **PostgreSQL** — btree index (the default) is a B+ tree with leaf page links
- **SQLite** — both table storage and indexes use B+ trees
- **SQL Server**, **Oracle**, **CockroachDB** — all B+ tree indexes

## Theory (40 min)

### The Key Difference from B-Trees

```
B-tree (order 3):
         [17, 35]                  ← data stored here too
        /    |    \
   [5,11]  [22,29]  [40,50]       ← data stored here too

B+ tree (order 3):
         [17 | 35]                 ← routing only, NO data
        /    |     \
   [5,11]→[17,22,29]→[35,40,50]   ← ALL data here, linked together
```

In the B+ tree:
- Key `17` appears in both an internal node (as a separator) AND in a leaf (as actual data). This duplication is the trade-off.
- The `→` arrows are the leaf chain — direct pointers between leaf nodes.
- Internal node keys are **copies** used as road signs: "keys < 17 go left, 17 <= keys < 35 go middle, keys >= 35 go right."

### Why Leaf Linking Matters

Consider: `SELECT * FROM users WHERE age BETWEEN 25 AND 35`

**Without leaf links (B-tree):**
1. Find node containing 25 → go down
2. Read key 25, need next key → go back UP to parent
3. Navigate DOWN again to next key
4. Repeat... each "up then down" = potential disk seek
5. Total: O(k * log n) disk seeks for k results

**With leaf links (B+ tree):**
1. Find leaf containing 25 → O(log n) disk seeks going down
2. Follow `next_leaf` pointer → sequential read
3. Keep following until you pass 35
4. Total: O(log n + k/B) disk seeks, where B = keys per leaf page

On spinning disks, sequential reads are 100x faster than random seeks. Even on SSDs, sequential access is 4-10x faster due to prefetching and reduced command overhead.

### Complexity

| Operation | Time | Disk I/O |
|-----------|------|----------|
| search(key) | O(log n) | O(log_B n) — typically 3-4 levels |
| insert(key) | O(log n) | O(log_B n) + possible splits |
| range_query(lo, hi) | O(log n + k) | O(log_B n + k/B) |
| traverse_all | O(n) | O(n/B) — pure sequential |

Where B = branching factor (keys per node). With 4KB pages and 8-byte keys, B ~ 500, so log_500(1 billion) ~ 3 levels.

### Node Structure

```
Internal Node:
  keys:     [17, 35]
  children: [ptr0, ptr1, ptr2]

  Invariant: all keys in children[i] < keys[i] <= all keys in children[i+1]

Leaf Node:
  keys:     [5, 11, 14]
  values:   [data5, data11, data14]
  next_leaf: → pointer to next leaf
```

### Splitting

When a leaf is full and we insert:
1. Split leaf into two halves
2. **Copy** the first key of the right half up to the parent as separator
3. If parent is full, split the parent too (but here we **push up** the middle key, not copy)

The copy-vs-push distinction matters: leaf keys are data (must stay), internal keys are just separators (can be moved).

### Space Trade-off

B+ trees duplicate some keys in internal nodes. For a tree with n keys and branching factor B:
- Leaf level: n keys (all data)
- Internal levels: ~n/B + n/B^2 + ... ~ n/(B-1) separator keys
- Overhead ratio: ~1/(B-1), which for B=500 is 0.2% — negligible

The space "waste" is trivial compared to the range scan speedup.

## Practice (20 min)

See `practice.py` — 5 exercises from range scans to SQL simulation.

## Daily Project

`bplus_tree.py` implements a complete B+ tree with insert, search, range query using leaf chain, and tree visualization.

## Checkpoint Questions

1. Why do B+ trees store data only in leaf nodes, not internal nodes? What query pattern does this optimize?
2. If a B+ tree has a branching factor of 500 and stores 1 billion keys, how many levels does it have? How many disk seeks for a point lookup?
3. Explain the difference between "copy up" (leaf split) and "push up" (internal split). Why are they different?
4. A B+ tree index on `user.age` receives the query `WHERE age BETWEEN 25 AND 35`. Walk through exactly what happens at the disk I/O level.
5. Why is the space overhead of duplicated separator keys negligible in practice? Calculate it for branching factor 500.
6. When would you choose a B-tree over a B+ tree? (Hint: think about workloads that are almost entirely point lookups with very large values.)
