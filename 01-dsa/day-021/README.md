# Day 21: Mini-Project — In-Memory Column Store (Arrays as Database Primitives)

## Why This Exists

This is Week 3's capstone. For the past six days you learned arrays (days 15-16), two pointers (day 17), sliding window (day 18), prefix sums (day 19), and binary search (day 20). Today you combine all of them to build something real: an in-memory columnar database engine.

Every analytics database you will encounter in production — BigQuery, ClickHouse, DuckDB, Redshift, Parquet files — stores data in **columns** rather than rows. This is not a style choice. It is a consequence of physics: how CPUs fetch data from RAM, how caches work, and how compression exploits data locality. You already learned (day 15) that sequential memory access is 10-100x faster than random access. Column stores exploit that fact at the database level.

The question this project answers: **why does `SELECT AVG(salary) FROM employees` run 10x faster on a column store than on a row store, even with identical data?**

The answer involves cache lines, branch prediction, prefix sums for running aggregates, binary search on sorted columns for range queries, and run-length encoding on sorted data. You have built every one of these tools. Now you wire them together.

## Theory (40 min)

### Row Store vs Column Store: The Physics

A **row store** keeps each record's fields together in memory:

```
Row store layout (employees table):
[id=1, name="Alice", dept="Eng", salary=95000]  ← row 0
[id=2, name="Bob",   dept="Sales", salary=72000] ← row 1
[id=3, name="Carol", dept="Eng", salary=88000]  ← row 2
...
```

A **column store** keeps each field's values together:

```
Column store layout:
id_col:     [1, 2, 3, 4, 5, ...]        ← all IDs contiguous
name_col:   ["Alice", "Bob", "Carol",...] ← all names contiguous
dept_col:   ["Eng", "Sales", "Eng", ...] ← all depts contiguous
salary_col: [95000, 72000, 88000, ...]   ← all salaries contiguous
```

### Why Columns Win for Analytics

**Cache line utilization.** When you compute `AVG(salary)`, the row store loads entire rows into cache — including `id`, `name`, `dept` that you never use. On a 64-byte cache line, maybe 8 bytes are the salary and 56 bytes are wasted. The column store loads *only* salary values. Every byte in the cache line is useful.

```
Row store: SELECT AVG(salary)
  Cache line 1: [id=1][name="Alice"___][dept="Eng"][salary=95000]
                 ^^^^   wasted data    ^^^^wasted  ^^^^^ useful
  Utilization: ~12%

Column store: SELECT AVG(salary)
  Cache line 1: [95000][72000][88000][91000][67000][78000][83000][96000]
  Utilization: 100%
```

**Mathematical model.** Let:
- R = number of rows
- C = number of columns
- S = size of one field (average)
- L = cache line size (64 bytes)
- K = number of columns in query

Row store bytes loaded: `R * C * S` (every column of every row)
Column store bytes loaded: `R * K * S` (only the K columns you need)

Speedup ≈ C / K. A table with 20 columns where you query 2 gives ~10x speedup, purely from memory bandwidth.

### Column Operations Map to Array Algorithms

| Database Operation | Array Algorithm | Day Learned |
|---|---|---|
| Full column scan | Sequential array traversal | Day 15-16 |
| WHERE col BETWEEN a AND b | Binary search on sorted column | Day 20 |
| Running SUM/AVG | Prefix sums | Day 19 |
| Range aggregation | Prefix sum range query | Day 19 |
| Merge-style joins | Two pointer technique | Day 17 |
| Moving average window | Sliding window | Day 18 |

### Compression: Run-Length Encoding on Sorted Columns

When a column is sorted, repeated values cluster together. Run-length encoding (RLE) replaces repeated values with (value, count) pairs:

```
Sorted dept column: ["Eng", "Eng", "Eng", "Eng", "Sales", "Sales", "Sales"]
RLE encoded:        [("Eng", 4), ("Sales", 3)]
```

This is not just space savings. Operations on RLE data are faster because you process groups, not individual values. `COUNT WHERE dept = 'Eng'` becomes a single lookup returning 4, instead of scanning 7 elements.

### Prefix Sums Enable O(1) Range Aggregates

Pre-compute prefix sums on numeric columns. Then `SUM(salary) WHERE row BETWEEN i AND j` is just `prefix[j+1] - prefix[i]` — O(1) instead of O(j-i).

```
salary_col:  [95000, 72000, 88000, 91000, 67000]
prefix_sum:  [0, 95000, 167000, 255000, 346000, 413000]

SUM(salary[1..3]) = prefix[4] - prefix[1] = 346000 - 95000 = 251000
```

## Practice (20 min)

Work through `practice.py` which has six exercises:

1. **Implement column scan with WHERE** — filter a column by predicate
2. **Implement SUM/AVG/COUNT aggregates** — operate on raw column arrays
3. **Build prefix sum index** — pre-compute for O(1) range aggregates
4. **Binary search on sorted column** — find range boundaries for WHERE clauses
5. **Run-length encode a sorted column** — compress and query compressed data
6. **Benchmark column vs row store** — measure and explain the performance gap

## Daily Project

Build a complete in-memory column store in `column_store.py`. The implementation includes:

- `ColumnTable`: create tables, insert rows, store as columns
- `SELECT` with `WHERE` filtering (equality, range, comparison)
- Aggregate functions: `SUM`, `AVG`, `COUNT`, `MIN`, `MAX`
- Sorted column indexes with binary search for fast range queries
- Run-length encoding compression on sorted columns
- Prefix sum indexes for O(1) range aggregation
- Benchmark comparing column store vs row store performance

Run the demonstration:
```bash
python column_store.py
```

Run and complete the exercises:
```bash
python practice.py
```

## Checkpoint Questions

1. A table has 50 columns and 1 million rows. Your query uses 3 columns. What is the approximate speedup of a column store over a row store, and why? (Hint: think about bytes loaded, not algorithmic complexity.)

2. You have a sorted column of 10 million department names where 80% are one of 5 values. How much space does RLE save? What is the time complexity of `COUNT WHERE dept = 'Engineering'` with RLE vs without?

3. You need `SUM(revenue) WHERE date BETWEEN '2024-01-01' AND '2024-06-30'` on a table with 100 million rows. Describe two different approaches using techniques from this week, their time complexities, and which is better for repeated queries vs one-off queries.

4. Why does a column store perform *worse* than a row store for `SELECT * FROM employees WHERE id = 42`? When would you choose a row store over a column store?

5. You are building a monitoring dashboard that shows "average CPU usage in the last 5 minutes" updating every second. Which data structure from this week handles this most efficiently? Why?
