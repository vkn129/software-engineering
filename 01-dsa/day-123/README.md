# Day 123: Tree DP

## Why Trees Make DP Easy

A tree is a DAG with extra structure: a unique parent, no cycles, and a
natural recursive shape. That means:

- **Subproblems align with subtrees.** `dp[v]` depends only on `dp[c]`
  for children `c` of `v`.
- **No iteration order question.** Post-order DFS visits children before
  parents, so dependencies resolve automatically.
- **Two-pass tricks (rerooting).** Sometimes you want the answer for
  every node as root — compute it for one root, then "shift" the root
  in O(1) per neighbor.

Tree DP is where DP feels like a glove. Get the state right and you're done.

## Pattern 1: Max Path Sum

A "path" here is any simple path through the tree (not constrained to
start/end at root). The classic LeetCode 124.

**State**: `down[v]` = max path sum **starting at v and going strictly downward**
(into v's subtree).

**Recurrence**:
```
down[v] = node_value[v] + max(0, max over children c of down[c])
```

**Best path through v** (could turn at v) =
`node_value[v] + sum of top 2 positive down[c]`.

**Global answer** = max over all v of best-through-v.

### Why Two Quantities

`down[v]` answers "what can I tell my parent about my best one-armed path?"
That's the only piece of information a parent needs.

But the **best path** could turn at v — going down one child and up the
other. So at each v, we separately consider a turn-here path.

This **split** between "what bubbles up" and "what's locally optimal" is
the cleanest pattern in tree DP.

### Subproblem Dependency Graph

```
       down[v]
        / | \
       /  |  \
  down[c1] down[c2] down[c3]    (children's values)
```

Post-order DFS computes children first; parent assembles afterwards.

## Pattern 2: House Robber on Tree

Each node has a value; you cannot rob two adjacent (parent-child) nodes.
Maximize stolen value.

**State**: `(rob[v], skip[v])`:
- `rob[v]` = max if you rob v
- `skip[v]` = max if you skip v

**Recurrence**:
```
rob[v]  = value[v] + sum over children c of skip[c]
skip[v] = sum over children c of max(rob[c], skip[c])
```

**Answer**: `max(rob[root], skip[root])`.

### Why Two States Per Node

Without `skip[v]`, you can't tell if a child decision was "free" or
"locked." Tracking both alternatives at each node is the standard
inclusion/exclusion pattern.

## Pattern 3: Tree Diameter

Longest path between any two nodes (in terms of edges or weighted edges).

### O(n) DP Approach

**State**: `height[v]` = longest path from v down into subtree.

While computing, at each v, the longest path **passing through v** is
`top1 + top2` of children heights. Track the global max.

```
def dfs(v, parent):
    h1 = h2 = 0  # top two child heights
    for c in adj[v]:
        if c == parent: continue
        h = dfs(c, v) + 1  # +1 for edge v-c
        if h > h1: h2, h1 = h1, h
        elif h > h2: h2 = h
    diameter = max(diameter, h1 + h2)
    return h1
```

### Alternative: Two BFS

1. BFS from any node, find farthest node `u`.
2. BFS from `u`, find farthest node `v`. Distance `u→v` = diameter.

Why it works: in a tree, the farthest node from **any** node is an
endpoint of some diameter. Two BFS is the textbook proof.

## Pitfall: Iterative vs Recursive DFS

Python's recursion limit (default 1000) bites you on deep trees.
For competitive contests with n = 10^5+, you must either:

- `sys.setrecursionlimit(10**6)` and pray, or
- Use an iterative post-order DFS with an explicit stack.

Iterative post-order is uglier but bulletproof. The pattern:
1. Push (node, state=0) onto stack.
2. Pop. If state==0: re-push with state=1, push all children with state=0.
3. If state==1: process node — children are done.

## Pitfall: Treating Tree as Generic Graph

In tree DP, **the parent is special** — it's the one neighbor you DON'T
recurse into. Forgetting to filter it gives infinite loops on undirected
trees. Always pass `parent` to the recursive call.

## Rerooting (Bonus Pattern)

If you need the answer with every node as root, naive O(n^2) is wasteful.

1. Root anywhere; compute `dp[v]` for the chosen root.
2. DFS again: when moving the root from v to neighbor c, update the DP
   by "subtracting c's contribution from v" and "adding v's new
   contribution to c." This is O(1) per re-root call.

Total: O(n). Used in problems like "sum of distances to all nodes from
each node."

## Real-World Usage

| System | Application | Why Tree DP |
|--------|-------------|-------------|
| **Compilers** | Register allocation in tree-structured code | Subtree-local choices |
| **Phylogenetics** | Most-parsimonious ancestor labeling (Sankoff/Fitch) | Two-pass post/pre-order |
| **Networking** | Min-cost spanning trees with constraints | Subtree merge DP |
| **VLSI** | Steiner tree heuristics on chip layouts | Tree DP over forced terminals |
| **NLP** | Dependency parse scoring | Parent/child grammatical roles |
| **Game trees** | Minimax / alpha-beta | Bubble-up game values |

## Checkpoint Questions

1. In max path sum, why do you take `max(0, down[c])` instead of just
   `down[c]`? Construct a counterexample without the `max(0, ...)`.
2. In house robber on tree, what changes if a node can have multiple
   parents (i.e., DAG)? Why does the DP break?
3. Prove the two-BFS diameter algorithm: that any BFS from any node
   ends at a diameter endpoint.
4. Convert the recursive max-path-sum DP to iterative for trees with
   n = 10^6 nodes.
5. For "sum of distances from each node to all others," sketch the
   rerooting recurrence.
