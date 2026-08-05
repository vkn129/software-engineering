# Day 178: Capstone Part A — Query Optimizer (Part 2/2)

## Continuation of Day 177

This day **extends** the engine from
`day-177/query_engine.py`. Same code path, same tables, same SQL. The
new layer is a **cost-based optimizer**:

- Estimate the cardinality (row count) of each operator.
- Estimate the cost of each physical plan candidate.
- Pick the cheapest plan.
- Reorder joins when there's more than one.

The optimizer is what separates a SQL query engine from a useful one.
Without it, you'll pick the wrong join, the wrong index, the wrong join
order, and watch a 50 ms query take 5 minutes.

```bash
python3 day-178/query_optimizer.py
```

## Why Cost-Based Optimization

The naive approach: pick a plan with rules. "If the predicate column has
an index, use IndexScan." That's the **rule-based** optimizer. It works
until it doesn't.

Consider `WHERE flag = true` where 99% of rows have `flag = true`. The
index "matches", but using it is **slower** than a sequential scan —
you do random I/O for almost every row. The optimizer needs to know:

- How many rows total? (statistics)
- How many will match? (selectivity)
- What does each plan cost in CPU + I/O? (cost model)

That's a cost-based optimizer.

## The Three Ingredients

### 1. Statistics

Per-table, per-column:

- `row_count` — total rows in the table.
- `ndv(column)` — number of distinct values.
- `min(column)`, `max(column)` — bounds for range estimation.

For `WHERE col = v`, selectivity ≈ `1 / ndv(col)`.
For `WHERE col > v`, selectivity ≈ `(max - v) / (max - min)`.

Real systems also keep histograms (Postgres has 10-bucket equi-depth
histograms by default). We keep it to scalars.

### 2. Cost Model

```
seq_scan(T)        = a * N
index_lookup(T, sel) = b * (sel * N)        # random I/O cost factor
hash_join(L, R)    = c * (|L| + |R|)        # build + probe
sort_merge(L, R)   = d * (|L| log |L| + |R| log |R|)
```

We use unit-free constants (`a=1, b=4, c=2, d=3`) chosen so that
short-circuiting behaviors emerge — index wins for selective predicates,
seq scan wins for "select most rows".

### 3. Plan Search

For single-table queries: enumerate the few candidate plans (one per
applicable index + the seq scan), pick the cheapest.

For multi-join queries: bottom-up dynamic programming (System-R style)
over join orders. We implement this for up to 4-way joins.

## Selectivity Estimation

| Predicate | Selectivity Estimate |
|---|---|
| `col = const` | `1 / ndv(col)` |
| `col != const` | `1 - 1/ndv(col)` |
| `col < const` | `(const - min) / (max - min)` (clamped) |
| `col > const` | `(max - const) / (max - min)` (clamped) |
| `p1 AND p2` | `sel(p1) * sel(p2)` (independence assumption) |

The independence assumption is famously wrong. Real workloads have
correlation (`car_make=Honda AND model=Civic` is much more correlated
than independence would predict). Modern engines (DuckDB, CockroachDB)
ship multi-column statistics partly to handle this.

## Join Order: Why It Matters

Two queries, same result, vastly different cost:

```
A JOIN B JOIN C    where |A|=1M, |B|=1M, |C|=10
```

- `(A JOIN B) JOIN C`: intermediate result up to 1M × 1M = 10^12. Catastrophe.
- `(A JOIN C) JOIN B` (if A↔C reduces A to 10): 10 × 1M = 10M. Tractable.

The optimizer picks the right order by estimating intermediate
cardinalities and minimizing total cost.

## System-R Style DP

For `n` tables:

```
best_plan[{t}]   = scan(t)
best_plan[S]     = min over splits (S = L ∪ R, L ∩ R = ∅) of:
                   cost(best_plan[L]) + cost(best_plan[R])
                   + join_cost(best_plan[L], best_plan[R])
```

Time: `O(3^n)` for `n` tables. Real systems cap `n` at ~12 and fall
back to greedy heuristics beyond that.

## What Day 178 Adds

| Component | Day 177 | Day 178 |
|---|---|---|
| Parser | Yes | Same |
| Logical plan | Yes | Same |
| Physical plan | Yes (caller picks strategy) | Optimizer picks |
| Cost model | None | `cost(plan)` function |
| Statistics | None | `TableStats` |
| Selectivity | None | `selectivity(pred)` |
| Plan search | None | Enumerate + DP |

## Failure Modes

1. **Bad statistics → bad plans.** If `ndv` is wrong by 10x, plan cost
   is wrong by 10x, and the optimizer happily picks the wrong plan.
   Production systems run `ANALYZE` to refresh stats. Stale stats are
   the #1 cause of "this query was fast yesterday."

2. **The independence assumption.** Multi-column predicates with
   correlated columns get wildly wrong selectivity estimates.

3. **Search-space explosion.** Beyond ~12 tables, `O(3^n)` becomes
   billions. Greedy/genetic algorithms take over.

4. **Cost model drift.** SSD vs spinning rust have radically different
   random-I/O costs. A cost model tuned for HDD picks the wrong plans
   on SSD. Cloud engines (Snowflake, BigQuery) re-tune constants per
   storage backend.

5. **Parameter sniffing.** `WHERE id = ?` cached plan based on `?=42`
   (selective) breaks when `?=NULL` (non-selective). Plan caches need
   to be invalidated or re-plan on skew detection.

## Checkpoint Questions

1. Why doesn't rule-based "use an index if one exists" work? Give a
   specific case where seq scan beats index scan.
2. The cost model uses constants like `b=4` for random I/O. What
   physical quantity does this constant represent in real systems?
3. The independence assumption fails for correlated columns. Sketch a
   selectivity estimator that doesn't make this assumption — what
   statistics would you need?
4. System-R DP is `O(3^n)`. Derive why it's `3^n` and not `2^n` or
   `n!`.
5. The optimizer in this day picks between hash join and sort-merge
   join. Under what input sizes / orderings does sort-merge dominate?
6. Why do production engines re-plan when stats change but cache plans
   for repeated queries? What's the tradeoff?

## What This Capstone Proves

You can build a real SQL engine in ~700 lines of stdlib Python. The
algorithms are not special — they're the data structures from earlier
phases combined in the right shape. The hard part is the cost model,
the statistics, and the search — all of which become tractable once
the underlying algorithms are solid.
