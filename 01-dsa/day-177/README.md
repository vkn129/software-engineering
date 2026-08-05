# Day 177: Capstone Part A — Database Query Engine (Part 1/2)

## What This Is

A working **SQL query engine**. Not a wrapper around SQLite — the real
thing: parser, logical plan, physical plan, B-tree indexes, hash joins,
sort-merge joins. Stdlib only.

You can run it:

```bash
python3 day-177/query_engine.py
```

It loads two small in-memory tables (`employees`, `departments`), parses
SQL strings, builds plans, and prints results.

Day 178 continues this same engine — same code, same tables — and adds a
cost-based optimizer that picks between hash join and sort-merge join.

## The Pipeline

```
   SQL text
       |
       v
  +----------+      +--------------+      +----------------+
  | Tokenizer| ---> | Parser (AST) | ---> | Logical Plan   |
  +----------+      +--------------+      +----------------+
                                                |
                                                v
                                        +-----------------+
                                        | Physical Plan   |  <-- (day 178 adds optimizer)
                                        +-----------------+
                                                |
                                                v
                                        +-----------------+
                                        | Executor        |
                                        +-----------------+
                                                |
                                                v
                                            Result rows
```

Every box is real code. Every Phase from this curriculum's earlier days
shows up:

| Phase Concept | Used Here |
|---|---|
| Hash table (Phase 4) | Hash join build side |
| B-tree (Phase 5) | Index lookup |
| Comparison sort (Phase 7) | Sort step for sort-merge join |
| Merge from merge-sort (Phase 7) | Merge step in sort-merge join |
| Greedy / cost models (Phase 8) | Optimizer (day 178) |
| Recursion (Phase 9) | Recursive descent parser, plan trees |

## Why Build This

A query engine is the **single best test** of whether you actually
understand data structures. Every operator is a data structure
specialization:

- **Sequential scan** = array iteration
- **Index scan** = B-tree range traversal
- **Hash join** = hash table probe
- **Sort-merge join** = merge-sort merge step
- **Aggregation** = hash table or sort+groupby

Production engines (Postgres, MySQL, DuckDB, Spark) are 100k–1M LOC. The
spine is what you see here.

## The Three Plan Layers

### 1. Logical plan
What you want, not how. `Select(emp) → Filter(salary > 50000) → Project(name, salary)`.
No notion of "use the index" or "use hash join". It's algebra.

### 2. Physical plan
How. `IndexScan(emp, salary_idx) → Project(name, salary)`. Each logical
operator gets a physical implementation. Joins in particular have many
choices.

### 3. Execution
Pull rows through the plan. Each operator implements `__iter__` (the
classic Volcano model). Pipelining keeps memory low.

## Supported SQL (this day)

```
SELECT col [, col]* FROM table [WHERE col OP literal]
SELECT ... FROM t1 JOIN t2 ON t1.col = t2.col [WHERE ...]
```

Predicates: `=`, `<`, `>`, `<=`, `>=`, `!=`. Literals: ints, strings.
That's it. No `GROUP BY`, no subqueries, no `ORDER BY` — enough to
demonstrate every interesting algorithm.

## B-Tree Index

Built from the Phase 5 B-tree. The index is a `dict[key -> list[row_id]]`
backed by a simple in-memory B-tree. `WHERE salary > 50000` rewrites to a
range scan instead of a full table scan.

## Hash Join vs Sort-Merge Join

| | Hash join | Sort-merge join |
|---|---|---|
| Build phase | Hash one side | Sort both sides |
| Memory | O(|build side|) | O(1) per merge step (after sort) |
| Best when | One side small | Both sides large, presorted, or sorted output needed |
| Worst when | Build side > memory | Inputs unsorted and huge (sort cost dominates) |

We implement both. Day 178's optimizer picks based on cardinality
estimates.

## Failure Modes

1. **Naive parser breaks on whitespace edge cases.** Production parsers
   use real grammars (yacc/ANTLR). Ours is hand-written recursive descent
   and will reject things like trailing commas. Intentional — keeping
   the parser small lets the engine be the focus.

2. **No type checking.** `WHERE name > 50` happily compares string to
   int. Postgres would error; we'll coerce or crash.

3. **Hash join with skew = pain.** All rows with the same key collide
   in one bucket. Real engines detect skew and switch strategies.

4. **No transaction layer.** No ACID, no MVCC. Pure read-only query
   engine.

## Checkpoint Questions

1. Why does the engine separate logical and physical plans? Couldn't
   the parser produce a physical plan directly?
2. The Volcano model uses `__iter__` to pipeline. What's the alternative
   (batch / vectorized execution) and why do modern engines prefer it
   for analytical queries?
3. Hash join builds the hash table on which side and probes with the
   other. How do you choose which side to build on?
4. For `SELECT * FROM big WHERE id = 42`, sequential scan is O(N) and
   B-tree lookup is O(log N). What's the constant factor break-even
   point in real systems?
5. Sort-merge join sorts both inputs. Why is it sometimes faster than
   hash join even though sorting is `O(N log N)` vs hash join's `O(N)`?
6. The optimizer (day 178) picks the join algorithm. What input does
   it need from the storage layer to make a good decision?
