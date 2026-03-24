# Day 41: Binary Tree Views

## Why Views Matter

Tree views solve a concrete problem: **how do you project a 3D structure onto a 2D plane?**

This matters in practice:
- **UI rendering**: File explorers, org charts, and tree visualizers must decide which nodes to show from a given perspective
- **Debugging**: When you `print()` a tree, you're computing a view — choosing which nodes represent the structure from a particular angle
- **Serialization**: Top/bottom views compress a tree into a single row for display in constrained spaces (terminal columns, breadcrumb trails)
- **Interview frequency**: View problems appear constantly because they combine BFS/DFS mastery with coordinate reasoning

## The Column/Level Coordinate System

Every node in a binary tree can be assigned two coordinates:

```
Column index (horizontal position):
    root = column 0
    left child = parent_column - 1
    right child = parent_column + 1

Level index (vertical position):
    root = level 0
    any child = parent_level + 1
```

This creates a 2D grid where nodes can overlap at the same (column, level) position:

```
            1              col: 0, level: 0
           / \
          2   3            col: -1,+1, level: 1
         / \   \
        4   5   6          col: -2,0,+2, level: 2
       /
      7                    col: -3, level: 3

Column:  -3  -2  -1   0  +1  +2
Level 0:                1
Level 1:          2          3
Level 2:     4         5          6
Level 3: 7
```

Node 5 (col=0) is directly below node 1 (col=0) — they share a column. This is why top view shows 1 but not 5: node 1 is seen first from above.

## The Six Views

### Left View — Leftmost node at each level
```
    1           You see: [1, 2, 4, 7]
   / \          (first node encountered at each level in BFS)
  2   3
 / \   \
4   5   6
/
7
```

### Right View — Rightmost node at each level
```
    1           You see: [1, 3, 6, 7]
   / \          (last node encountered at each level in BFS)
  2   3
 / \   \
4   5   6
/
7
```

### Top View — First node seen at each column (looking down)
```
Column: -3  -2  -1   0  +1  +2
         7   4   2   1   3   6

Node 5 (col=0) is hidden behind node 1.
BFS ensures we see the shallowest node at each column first.
```

### Bottom View — Last node seen at each column (looking up)
```
Column: -3  -2  -1   0  +1  +2
         7   4   2   5   3   6

Node 5 (col=0) is below node 1, so bottom view shows 5 instead.
```

### Boundary Traversal — Anti-clockwise walk around the perimeter
```
    1
   / \
  2   3         Boundary: [1, 2, 4, 7, 5, 6, 3]
 / \   \
4   5   6       = left boundary (top-down, excluding leaves)
/                 + all leaves (left-to-right)
7                 + right boundary (bottom-up, excluding leaves)
```

### Vertical Order — Group by column, sort by level within column
```
Column -3: [7]
Column -2: [4]
Column -1: [2]
Column  0: [1, 5]    ← both at column 0, sorted by level
Column +1: [3]
Column +2: [6]
```

## Why BFS vs DFS Matters for Views

**Top view requires BFS.** Here's why:

```
        1
       / \
      2   3
       \
        4
```

Node 4 is at column 0 (same as root 1). With BFS, we process level-by-level, so node 1 (level 0) is seen at column 0 before node 4 (level 2). With DFS, the traversal order depends on left-vs-right-first, and we might visit node 4 before finishing all nodes at shallower levels.

**Rule of thumb:**
- "First/last at each **level**" (left/right view) → BFS natural, DFS also works
- "First/last at each **column**" (top/bottom view) → BFS required for correct level ordering
- "All nodes grouped by column" (vertical order) → BFS with column tracking

## Diagonal Traversal

Nodes on the same diagonal satisfy: `column - level = constant`

```
            1  (0-0=0)
           / \
          2   3  (-1-1=-2, 1-1=0)
         / \   \
        4   5   6  (-2-2=-4, 0-2=-2, 2-2=0)

Diagonal 0:  [1, 3, 6]     (col - level = 0)
Diagonal -2: [2, 5]        (col - level = -2)
Diagonal -4: [4]           (col - level = -4)
```

Going right keeps the diagonal constant (col+1, level+1 → difference unchanged).
Going left decreases the diagonal by 2 (col-1, level+1 → difference decreases by 2).

## Failure Modes

1. **Using DFS for top view**: DFS visits deep-left nodes before shallow-right nodes. If a deep node shares a column with a shallow node, DFS may record the deep node first — giving wrong results for "first node at each column."

2. **Forgetting column tracking**: Left/right views only need level tracking. Top/bottom views need column tracking. Mixing them up produces garbage.

3. **Boundary traversal double-counting**: The left boundary's last node might be a leaf. The leaf traversal also collects it. You must exclude leaves from the left/right boundary collection, or you'll duplicate nodes.

4. **Single-child edge cases**: When a node has only a left child or only a right child, is it part of the left boundary? The right boundary? Both? The convention: follow the path you'd walk if tracing the outline.

5. **Empty tree and single node**: Boundary traversal on a single node should return `[root.val]`, not `[root.val, root.val, root.val]` (root appears in left boundary, leaves, AND right boundary if you're not careful).

## What to Build Today

1. All six view functions: left, right, top, bottom, boundary, vertical order
2. Diagonal traversal as a bonus coordinate-system exercise
3. Practice problems reinforcing the column/level mental model

## Checkpoint Questions

Before moving on, you should be able to answer:
- Why can't you compute top view with a simple DFS? What specific tree structure breaks it?
- What is the relationship between vertical order traversal and top/bottom views? (Hint: top view = first element of each column group)
- In boundary traversal, why do we reverse the right boundary? What happens if we don't?
- For a tree with n nodes, what's the maximum number of distinct columns? (Hint: think about a left-skewed tree)
- Why does diagonal traversal group nodes where `col - level` is constant? What real-world structure does this correspond to?
