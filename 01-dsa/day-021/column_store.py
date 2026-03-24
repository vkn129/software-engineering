"""
Day 21: In-Memory Column Store — Arrays as Database Primitives

This module builds an in-memory columnar database from scratch using only
Python built-in data structures. It ties together every array technique
from Week 3: contiguous arrays (day 15-16), two pointers (day 17),
sliding window (day 18), prefix sums (day 19), and binary search (day 20).

WHY COLUMN STORES EXIST:
When you run SELECT AVG(salary) FROM employees on a 20-column table,
a row store loads all 20 columns into cache even though you need 1.
A column store loads only the salary column. The speedup is not
algorithmic (both are O(n)) — it is physical. Cache lines carry only
useful bytes, branch prediction works better on homogeneous data,
and sorted columns compress with run-length encoding.

Every modern analytics engine (BigQuery, ClickHouse, DuckDB, Parquet)
uses column-oriented storage for exactly these reasons.

Run: python column_store.py
"""

import time
import bisect


# ==========================================================================
# SECTION 1: Core Column Store Implementation
# ==========================================================================

class ColumnTable:
    """
    An in-memory column-oriented table.

    Data is stored as a dict of column_name -> list of values.
    All columns have the same length. Row i is the set of values
    at index i across all columns.

    Why a dict of lists instead of a list of dicts (row store)?
    Because aggregating one column means touching ONE contiguous list
    instead of jumping between N dict objects scattered on the heap.
    """

    def __init__(self, name, schema):
        """
        Create a table with a given schema.

        Args:
            name: table name (for display)
            schema: dict of {column_name: type} where type is 'int', 'float', or 'str'

        The schema is metadata — Python lists hold any type, but the schema
        lets us validate inserts and decide which operations make sense
        (you cannot SUM a string column).
        """
        self.name = name
        self.schema = schema
        # Each column is a separate contiguous list — this is the key insight
        self.columns = {col: [] for col in schema}
        self.row_count = 0

        # Optional indexes built on demand
        self._sorted_indexes = {}   # col_name -> sorted (value, original_index) pairs
        self._prefix_sums = {}      # col_name -> prefix sum array
        self._rle_data = {}         # col_name -> [(value, count), ...]

    def insert_row(self, row):
        """
        Insert a single row given as a dict {col_name: value}.

        In a real column store, single-row inserts are expensive because
        you must append to every column array. This is why column stores
        batch inserts. We keep it simple here.
        """
        for col in self.schema:
            if col not in row:
                raise ValueError(f"Missing column: {col}")
            self.columns[col].append(row[col])
        self.row_count += 1

        # Invalidate any pre-built indexes — data changed
        self._sorted_indexes.clear()
        self._prefix_sums.clear()
        self._rle_data.clear()

    def insert_rows(self, rows):
        """Batch insert — more natural for column stores."""
        for row in rows:
            # Validate all rows before inserting any (atomicity)
            for col in self.schema:
                if col not in row:
                    raise ValueError(f"Row missing column '{col}': {row}")

        for row in rows:
            for col in self.schema:
                self.columns[col].append(row[col])
            self.row_count += 1

        self._sorted_indexes.clear()
        self._prefix_sums.clear()
        self._rle_data.clear()

    # ------------------------------------------------------------------
    # SECTION 2: SELECT with WHERE — Column Scans
    # ------------------------------------------------------------------

    def select(self, columns=None, where=None):
        """
        Execute a SELECT query.

        Args:
            columns: list of column names to return (None = all)
            where: a callable that takes (col_dict_for_row_i) -> bool,
                   OR a tuple (col_name, operator, value) for simple filters

        Returns:
            list of dicts (row-oriented result for display)

        Why return rows? Because query results are typically small and
        consumed one record at a time. The column layout is for storage
        and bulk computation, not for result display.
        """
        if columns is None:
            columns = list(self.schema.keys())

        # Build the filter function
        filter_fn = self._build_filter(where) if where else lambda i: True

        results = []
        for i in range(self.row_count):
            if filter_fn(i):
                results.append({col: self.columns[col][i] for col in columns})

        return results

    def _build_filter(self, where):
        """
        Convert a WHERE clause to a filter function.

        Supports:
            - callable: used directly (takes row index)
            - tuple: (column, op, value) for simple comparisons
            - list of tuples: AND of multiple conditions
        """
        if callable(where):
            # Caller provides a function that takes row index
            return where

        if isinstance(where, tuple) and len(where) == 3:
            col, op, val = where
            col_data = self.columns[col]
            # Return a function that checks the condition for row i
            # Using direct column access (not dict lookup) for speed
            if op == '==':
                return lambda i, c=col_data, v=val: c[i] == v
            elif op == '!=':
                return lambda i, c=col_data, v=val: c[i] != v
            elif op == '<':
                return lambda i, c=col_data, v=val: c[i] < v
            elif op == '<=':
                return lambda i, c=col_data, v=val: c[i] <= v
            elif op == '>':
                return lambda i, c=col_data, v=val: c[i] > v
            elif op == '>=':
                return lambda i, c=col_data, v=val: c[i] >= v
            elif op == 'BETWEEN':
                # val should be (low, high) inclusive
                low, high = val
                return lambda i, c=col_data, lo=low, hi=high: lo <= c[i] <= hi
            else:
                raise ValueError(f"Unknown operator: {op}")

        if isinstance(where, list):
            # AND of multiple conditions
            filters = [self._build_filter(w) for w in where]
            return lambda i, fs=filters: all(f(i) for f in fs)

        raise ValueError(f"Invalid WHERE clause: {where}")

    # ------------------------------------------------------------------
    # SECTION 3: Aggregate Functions
    # ------------------------------------------------------------------

    def aggregate(self, col_name, func, where=None):
        """
        Compute an aggregate function over a column.

        Args:
            col_name: which column to aggregate
            func: 'SUM', 'AVG', 'COUNT', 'MIN', 'MAX'
            where: optional filter (same format as select())

        This is where column stores shine. We iterate over ONE contiguous
        list, touching only the bytes we need. A row store would load
        entire rows into cache to access one field.
        """
        col_data = self.columns[col_name]

        if where:
            filter_fn = self._build_filter(where)
            # Filtered aggregation — scan column with predicate
            values = [col_data[i] for i in range(self.row_count) if filter_fn(i)]
        else:
            # No filter — operate on the entire column directly
            values = col_data

        if not values:
            return None

        if func == 'SUM':
            return sum(values)
        elif func == 'AVG':
            return sum(values) / len(values)
        elif func == 'COUNT':
            return len(values)
        elif func == 'MIN':
            return min(values)
        elif func == 'MAX':
            return max(values)
        else:
            raise ValueError(f"Unknown aggregate: {func}")

    def group_by(self, group_col, agg_col, func):
        """
        GROUP BY on one column with an aggregate on another.

        SQL equivalent: SELECT group_col, func(agg_col) FROM table GROUP BY group_col

        We do a single pass over both columns simultaneously — no hash join,
        no sorting. Just accumulate values per group.
        """
        groups = {}
        group_data = self.columns[group_col]
        agg_data = self.columns[agg_col]

        for i in range(self.row_count):
            key = group_data[i]
            if key not in groups:
                groups[key] = []
            groups[key].append(agg_data[i])

        results = {}
        for key, values in groups.items():
            if func == 'SUM':
                results[key] = sum(values)
            elif func == 'AVG':
                results[key] = sum(values) / len(values)
            elif func == 'COUNT':
                results[key] = len(values)
            elif func == 'MIN':
                results[key] = min(values)
            elif func == 'MAX':
                results[key] = max(values)

        return results

    # ------------------------------------------------------------------
    # SECTION 4: Sorted Index with Binary Search (Day 20)
    # ------------------------------------------------------------------

    def build_sorted_index(self, col_name):
        """
        Build a sorted index on a column for fast range queries.

        This creates a sorted copy of the column values paired with their
        original row indices. Binary search on this sorted index gives
        O(log n) lookup for WHERE clauses on this column.

        Trade-off: O(n log n) to build, O(n) extra memory, but then
        range queries drop from O(n) scan to O(log n + k) where k is
        the number of matching rows.
        """
        col_data = self.columns[col_name]
        # Sort by value, keeping track of original row index
        indexed = sorted(range(self.row_count), key=lambda i: col_data[i])
        sorted_vals = [col_data[i] for i in indexed]
        self._sorted_indexes[col_name] = (sorted_vals, indexed)

    def range_query_indexed(self, col_name, low, high):
        """
        Find all row indices where low <= col_value <= high using binary search.

        Without index: O(n) — scan every row.
        With sorted index: O(log n + k) — binary search for boundaries,
        then collect k matching indices.

        This is exactly lower_bound and upper_bound from Day 20.
        """
        if col_name not in self._sorted_indexes:
            self.build_sorted_index(col_name)

        sorted_vals, original_indices = self._sorted_indexes[col_name]

        # Lower bound: first index where value >= low
        left = bisect.bisect_left(sorted_vals, low)
        # Upper bound: first index where value > high
        right = bisect.bisect_right(sorted_vals, high)

        # All indices in [left, right) match the range
        return [original_indices[i] for i in range(left, right)]

    def select_with_index(self, columns, col_name, low, high):
        """
        SELECT columns WHERE col_name BETWEEN low AND high,
        using the sorted index for fast range lookup.
        """
        matching_rows = self.range_query_indexed(col_name, low, high)
        if columns is None:
            columns = list(self.schema.keys())
        return [
            {col: self.columns[col][i] for col in columns}
            for i in matching_rows
        ]

    # ------------------------------------------------------------------
    # SECTION 5: Prefix Sum Index for O(1) Range Aggregation (Day 19)
    # ------------------------------------------------------------------

    def build_prefix_sum(self, col_name):
        """
        Build a prefix sum array for a numeric column.

        After building: SUM(col[i..j]) = prefix[j+1] - prefix[i]
        This turns range sum queries from O(n) to O(1).

        The trade-off: O(n) extra memory, O(n) build time, but every
        subsequent range sum is O(1). Worth it when you have many
        range queries on the same data (common in dashboards, reports).
        """
        col_data = self.columns[col_name]
        prefix = [0] * (self.row_count + 1)
        for i in range(self.row_count):
            prefix[i + 1] = prefix[i] + col_data[i]
        self._prefix_sums[col_name] = prefix

    def range_sum(self, col_name, start_row, end_row):
        """
        SUM(col_name) for rows [start_row, end_row] inclusive.
        O(1) with prefix sums vs O(n) without.
        """
        if col_name not in self._prefix_sums:
            self.build_prefix_sum(col_name)
        prefix = self._prefix_sums[col_name]
        return prefix[end_row + 1] - prefix[start_row]

    def range_avg(self, col_name, start_row, end_row):
        """AVG(col_name) for rows [start_row, end_row] inclusive. O(1)."""
        count = end_row - start_row + 1
        if count == 0:
            return None
        return self.range_sum(col_name, start_row, end_row) / count

    # ------------------------------------------------------------------
    # SECTION 6: Run-Length Encoding on Sorted Columns
    # ------------------------------------------------------------------

    def build_rle(self, col_name):
        """
        Run-length encode a column. Most effective when the column is sorted
        (or has long runs of repeated values).

        RLE replaces: ["Eng", "Eng", "Eng", "Sales", "Sales"]
        with:         [("Eng", 3), ("Sales", 2)]

        Space savings on a sorted column with V distinct values out of N rows:
        Original: O(N) entries
        RLE: O(V) entries
        When V << N (common for categorical data like department, country,
        status), this is massive compression.

        Bonus: COUNT(WHERE col = X) becomes O(log V) with binary search
        on the RLE values, instead of O(N) scanning every row.
        """
        col_data = self.columns[col_name]
        if not col_data:
            self._rle_data[col_name] = []
            return

        runs = []
        current_val = col_data[0]
        count = 1

        for i in range(1, self.row_count):
            if col_data[i] == current_val:
                count += 1
            else:
                runs.append((current_val, count))
                current_val = col_data[i]
                count = 1
        runs.append((current_val, count))

        self._rle_data[col_name] = runs

    def rle_count(self, col_name, value):
        """
        COUNT(*) WHERE col_name = value using RLE data.

        If the column is sorted, this is O(log V) where V = distinct values.
        Without RLE, it is O(N) scanning every row.
        """
        if col_name not in self._rle_data:
            self.build_rle(col_name)

        for val, count in self._rle_data[col_name]:
            if val == value:
                return count
        return 0

    def rle_stats(self, col_name):
        """Show compression statistics for an RLE-encoded column."""
        if col_name not in self._rle_data:
            self.build_rle(col_name)

        runs = self._rle_data[col_name]
        original_entries = self.row_count
        rle_entries = len(runs)
        ratio = original_entries / rle_entries if rle_entries > 0 else 0

        return {
            'original_entries': original_entries,
            'rle_entries': rle_entries,
            'compression_ratio': ratio,
            'runs': runs[:10]  # First 10 for display
        }


# ==========================================================================
# SECTION 7: Row Store for Comparison
# ==========================================================================

class RowTable:
    """
    A simple row-oriented table for benchmarking against ColumnTable.

    Each row is a dict stored in a list. This mirrors how most ORM-backed
    applications think about data: a list of records.

    For point lookups (get employee #42), this is fine.
    For analytics (average salary across 1M employees), this wastes
    cache bandwidth loading columns you never read.
    """

    def __init__(self, name, schema):
        self.name = name
        self.schema = schema
        self.rows = []

    def insert_row(self, row):
        self.rows.append(dict(row))

    def insert_rows(self, rows):
        for row in rows:
            self.rows.append(dict(row))

    def select(self, columns=None, where=None):
        if columns is None:
            columns = list(self.schema.keys())
        results = []
        for row in self.rows:
            if where is None or where(row):
                results.append({col: row[col] for col in columns})
        return results

    def aggregate(self, col_name, func, where=None):
        if where:
            values = [row[col_name] for row in self.rows if where(row)]
        else:
            values = [row[col_name] for row in self.rows]

        if not values:
            return None

        if func == 'SUM':
            return sum(values)
        elif func == 'AVG':
            return sum(values) / len(values)
        elif func == 'COUNT':
            return len(values)
        elif func == 'MIN':
            return min(values)
        elif func == 'MAX':
            return max(values)


# ==========================================================================
# SECTION 8: Demonstrations
# ==========================================================================

def demo_basic_operations():
    """
    Demonstrate creating a table, inserting data, and running queries.
    This is the column store equivalent of basic SQL.
    """
    print("=" * 70)
    print("DEMO 1: Basic Column Store Operations")
    print("=" * 70)

    # CREATE TABLE employees (id INT, name TEXT, dept TEXT, salary INT)
    employees = ColumnTable("employees", {
        'id': 'int', 'name': 'str', 'dept': 'str', 'salary': 'int'
    })

    # INSERT INTO employees VALUES (...)
    data = [
        {'id': 1, 'name': 'Alice',   'dept': 'Engineering', 'salary': 95000},
        {'id': 2, 'name': 'Bob',     'dept': 'Sales',       'salary': 72000},
        {'id': 3, 'name': 'Carol',   'dept': 'Engineering', 'salary': 88000},
        {'id': 4, 'name': 'Dave',    'dept': 'Marketing',   'salary': 67000},
        {'id': 5, 'name': 'Eve',     'dept': 'Engineering', 'salary': 102000},
        {'id': 6, 'name': 'Frank',   'dept': 'Sales',       'salary': 78000},
        {'id': 7, 'name': 'Grace',   'dept': 'Engineering', 'salary': 91000},
        {'id': 8, 'name': 'Heidi',   'dept': 'Marketing',   'salary': 71000},
        {'id': 9, 'name': 'Ivan',    'dept': 'Engineering', 'salary': 97000},
        {'id': 10, 'name': 'Judy',   'dept': 'Sales',       'salary': 82000},
    ]
    employees.insert_rows(data)

    # Show internal column layout
    print("\nInternal column layout (first 5 values per column):")
    for col_name, col_data in employees.columns.items():
        print(f"  {col_name:>8}: {col_data[:5]}")

    print(f"\nKey insight: each column is a SEPARATE contiguous list.")
    print(f"Aggregating 'salary' touches only the salary list — {len(employees.columns['salary'])} values,")
    print(f"not {len(employees.columns)} columns x {employees.row_count} rows = {len(employees.columns) * employees.row_count} values.\n")

    # SELECT * FROM employees WHERE dept = 'Engineering'
    print("SELECT name, salary FROM employees WHERE dept = 'Engineering':")
    results = employees.select(
        columns=['name', 'salary'],
        where=('dept', '==', 'Engineering')
    )
    for row in results:
        print(f"  {row['name']:>8}: ${row['salary']:,}")

    # SELECT AVG(salary) FROM employees
    avg_salary = employees.aggregate('salary', 'AVG')
    print(f"\nSELECT AVG(salary) FROM employees = ${avg_salary:,.0f}")

    # SELECT dept, AVG(salary) FROM employees GROUP BY dept
    print("\nSELECT dept, AVG(salary) FROM employees GROUP BY dept:")
    grouped = employees.group_by('dept', 'salary', 'AVG')
    for dept, avg in sorted(grouped.items()):
        print(f"  {dept:>12}: ${avg:,.0f}")

    # SELECT SUM(salary) FROM employees WHERE salary BETWEEN 80000 AND 100000
    total = employees.aggregate(
        'salary', 'SUM',
        where=('salary', 'BETWEEN', (80000, 100000))
    )
    print(f"\nSELECT SUM(salary) WHERE salary BETWEEN 80K-100K = ${total:,}")

    print()


def demo_sorted_index():
    """
    Demonstrate binary search on a sorted column index.
    Shows O(log n + k) range queries vs O(n) full scans.
    """
    print("=" * 70)
    print("DEMO 2: Sorted Index with Binary Search (Day 20)")
    print("=" * 70)

    # Generate a larger dataset to show the binary search advantage
    import random
    random.seed(42)

    table = ColumnTable("sales", {
        'id': 'int', 'amount': 'int', 'region': 'str'
    })

    n = 100_000
    regions = ['North', 'South', 'East', 'West']
    rows = [
        {'id': i, 'amount': random.randint(100, 10000), 'region': random.choice(regions)}
        for i in range(n)
    ]
    table.insert_rows(rows)

    # Range query WITHOUT index: O(n) scan
    start = time.perf_counter()
    result_scan = table.select(
        columns=['id', 'amount'],
        where=('amount', 'BETWEEN', (5000, 5100))
    )
    scan_time = time.perf_counter() - start

    # Range query WITH index: O(log n + k)
    start = time.perf_counter()
    table.build_sorted_index('amount')
    build_time = time.perf_counter() - start

    start = time.perf_counter()
    result_index = table.select_with_index(['id', 'amount'], 'amount', 5000, 5100)
    index_time = time.perf_counter() - start

    print(f"\nRange query: amount BETWEEN 5000 AND 5100 on {n:,} rows")
    print(f"  Full scan:     {len(result_scan):>5} rows found in {scan_time*1000:.2f} ms")
    print(f"  Index build:   {build_time*1000:.2f} ms (one-time cost)")
    print(f"  Index query:   {len(result_index):>5} rows found in {index_time*1000:.2f} ms")
    print(f"  Query speedup: {scan_time/index_time:.1f}x (amortizes over many queries)")

    print(f"\n  WHY: Binary search finds the range boundaries in O(log {n:,}) = ~{len(bin(n))-2} steps,")
    print(f"  then collects {len(result_index)} matching rows. The full scan checks all {n:,} rows.")
    print()


def demo_prefix_sums():
    """
    Demonstrate prefix sum indexes for O(1) range aggregation.
    """
    print("=" * 70)
    print("DEMO 3: Prefix Sum Index for O(1) Aggregation (Day 19)")
    print("=" * 70)

    table = ColumnTable("daily_revenue", {
        'day': 'int', 'revenue': 'int'
    })

    import random
    random.seed(123)

    n = 365  # One year of daily revenue
    rows = [
        {'day': i + 1, 'revenue': random.randint(50000, 200000)}
        for i in range(n)
    ]
    table.insert_rows(rows)

    # Build prefix sum index
    table.build_prefix_sum('revenue')

    # Various range queries — all O(1) after the prefix sum is built
    print(f"\nDaily revenue data: {n} days")
    print(f"Prefix sum built: {n + 1} entries, one-time O(n) cost\n")

    queries = [
        ("Q1 (days 1-90)", 0, 89),
        ("Q2 (days 91-181)", 90, 180),
        ("Q3 (days 182-273)", 181, 272),
        ("Q4 (days 274-365)", 273, 364),
        ("Full year", 0, 364),
        ("Last 30 days", 335, 364),
    ]

    for label, start, end in queries:
        total = table.range_sum('revenue', start, end)
        avg = table.range_avg('revenue', start, end)
        print(f"  {label:>20}: total=${total:>12,}  avg=${avg:>9,.0f}/day")

    print(f"\n  Each query above is O(1) — one subtraction: prefix[j+1] - prefix[i]")
    print(f"  Without prefix sums, each would scan O(days_in_range) values.\n")


def demo_rle_compression():
    """
    Demonstrate run-length encoding on sorted columns.
    """
    print("=" * 70)
    print("DEMO 4: Run-Length Encoding on Sorted Columns")
    print("=" * 70)

    import random
    random.seed(99)

    # Simulate a table with a low-cardinality column (few distinct values)
    table = ColumnTable("users", {
        'id': 'int', 'country': 'str', 'age': 'int'
    })

    # Distribution: US 40%, UK 20%, DE 15%, FR 15%, JP 10%
    countries = ['DE'] * 1500 + ['FR'] * 1500 + ['JP'] * 1000 + ['UK'] * 2000 + ['US'] * 4000
    # Already sorted — simulates a column that has been sorted for compression
    n = len(countries)
    rows = [
        {'id': i, 'country': countries[i], 'age': random.randint(18, 80)}
        for i in range(n)
    ]
    table.insert_rows(rows)

    # Build RLE on the sorted country column
    table.build_rle('country')
    stats = table.rle_stats('country')

    print(f"\n{n:,} rows, column 'country' (sorted, 5 distinct values)")
    print(f"\nBefore RLE: {stats['original_entries']:,} entries")
    print(f"After RLE:  {stats['rle_entries']} entries")
    print(f"Compression ratio: {stats['compression_ratio']:.0f}:1\n")

    print("RLE runs:")
    for val, count in stats['runs']:
        bar = '#' * (count // 100)
        print(f"  {val:>4}: {count:>5} rows  {bar}")

    # Query on RLE data
    print(f"\nCOUNT(*) WHERE country = 'US': {table.rle_count('country', 'US')}")
    print(f"COUNT(*) WHERE country = 'JP': {table.rle_count('country', 'JP')}")
    print(f"COUNT(*) WHERE country = 'BR': {table.rle_count('country', 'BR')}  (not found)")

    print(f"\n  WHY RLE works: sorted columns cluster identical values.")
    print(f"  5 distinct values compress 10,000 entries to 5 entries.")
    print(f"  COUNT queries scan 5 RLE entries instead of 10,000 rows.\n")


def demo_benchmark():
    """
    Head-to-head benchmark: column store vs row store.

    This is the money demo. It shows WHY column stores exist for analytics.
    The performance difference is not from better algorithms (both are O(n)
    for a full scan). It comes from cache utilization: the column store
    touches only the bytes it needs.
    """
    print("=" * 70)
    print("DEMO 5: Column Store vs Row Store Benchmark")
    print("=" * 70)

    import random
    random.seed(2024)

    n = 200_000
    num_cols = 20  # Wide table — makes the difference dramatic

    # Generate schema: col_0, col_1, ..., col_19 (all ints)
    schema = {f'col_{i}': 'int' for i in range(num_cols)}

    col_table = ColumnTable("col_bench", schema)
    row_table = RowTable("row_bench", schema)

    # Generate data
    print(f"\nGenerating {n:,} rows x {num_cols} columns...")
    rows = []
    for _ in range(n):
        row = {f'col_{i}': random.randint(1, 1000000) for i in range(num_cols)}
        rows.append(row)

    # Insert into both stores
    start = time.perf_counter()
    col_table.insert_rows(rows)
    col_insert_time = time.perf_counter() - start

    start = time.perf_counter()
    row_table.insert_rows(rows)
    row_insert_time = time.perf_counter() - start

    print(f"  Column store insert: {col_insert_time:.3f}s")
    print(f"  Row store insert:    {row_insert_time:.3f}s")

    # Benchmark 1: SUM of one column (analytics query)
    print(f"\nBenchmark 1: SUM(col_0) — single column aggregate")

    start = time.perf_counter()
    col_sum = col_table.aggregate('col_0', 'SUM')
    col_agg_time = time.perf_counter() - start

    start = time.perf_counter()
    row_sum = row_table.aggregate('col_0', 'SUM')
    row_agg_time = time.perf_counter() - start

    assert col_sum == row_sum, "Results must match!"
    print(f"  Column store: {col_agg_time*1000:.2f} ms  (sum={col_sum:,})")
    print(f"  Row store:    {row_agg_time*1000:.2f} ms  (sum={row_sum:,})")
    speedup = row_agg_time / col_agg_time if col_agg_time > 0 else float('inf')
    print(f"  Speedup: {speedup:.1f}x")

    # Benchmark 2: AVG with WHERE filter
    print(f"\nBenchmark 2: AVG(col_0) WHERE col_1 > 500000")

    start = time.perf_counter()
    col_avg = col_table.aggregate('col_0', 'AVG', where=('col_1', '>', 500000))
    col_filter_time = time.perf_counter() - start

    start = time.perf_counter()
    row_avg = row_table.aggregate('col_0', 'AVG', where=lambda r: r['col_1'] > 500000)
    row_filter_time = time.perf_counter() - start

    print(f"  Column store: {col_filter_time*1000:.2f} ms  (avg={col_avg:,.0f})")
    print(f"  Row store:    {row_filter_time*1000:.2f} ms  (avg={row_avg:,.0f})")
    speedup = row_filter_time / col_filter_time if col_filter_time > 0 else float('inf')
    print(f"  Speedup: {speedup:.1f}x")

    # Benchmark 3: SELECT * (full row retrieval — row store's strength)
    print(f"\nBenchmark 3: SELECT * WHERE col_0 = <specific value> (point lookup)")

    target = rows[n // 2]['col_0']  # Pick a value we know exists

    start = time.perf_counter()
    col_point = col_table.select(where=('col_0', '==', target))
    col_point_time = time.perf_counter() - start

    start = time.perf_counter()
    row_point = row_table.select(where=lambda r: r['col_0'] == target)
    row_point_time = time.perf_counter() - start

    print(f"  Column store: {col_point_time*1000:.2f} ms  ({len(col_point)} rows)")
    print(f"  Row store:    {row_point_time*1000:.2f} ms  ({len(row_point)} rows)")
    if row_point_time > 0 and col_point_time > 0:
        if col_point_time < row_point_time:
            print(f"  Column store {row_point_time/col_point_time:.1f}x faster")
        else:
            print(f"  Row store {col_point_time/row_point_time:.1f}x faster (expected for SELECT *)")

    print(f"\n  ANALYSIS:")
    print(f"  - Analytics (SUM, AVG on 1-2 cols): Column store wins because")
    print(f"    it loads only the columns it needs. On a {num_cols}-col table querying")
    print(f"    1 column, column store loads ~1/{num_cols}th the data.")
    print(f"  - Point lookups (SELECT * on 1 row): Row store can be competitive")
    print(f"    because all columns for a row are already co-located.")
    print()


def demo_sliding_window_on_columns():
    """
    Demonstrate sliding window (Day 18) on column data.
    Computes moving averages on a time series stored in column format.
    """
    print("=" * 70)
    print("DEMO 6: Sliding Window Moving Average (Day 18)")
    print("=" * 70)

    import random
    random.seed(77)

    table = ColumnTable("metrics", {
        'timestamp': 'int', 'cpu_usage': 'float'
    })

    # 60 seconds of CPU metrics
    n = 60
    base = 45.0
    rows = []
    for i in range(n):
        # Simulate CPU with a spike around t=30
        spike = 40.0 if 28 <= i <= 35 else 0.0
        noise = random.uniform(-5, 5)
        rows.append({
            'timestamp': i,
            'cpu_usage': round(base + spike + noise, 1)
        })
    table.insert_rows(rows)

    # Compute 5-second moving average using sliding window
    cpu = table.columns['cpu_usage']
    window_size = 5
    moving_avg = []

    # Initialize window sum with first window_size elements
    window_sum = sum(cpu[:window_size])
    moving_avg.append(window_sum / window_size)

    # Slide: add right element, remove left element — O(1) per step
    for i in range(window_size, n):
        window_sum += cpu[i] - cpu[i - window_size]
        moving_avg.append(window_sum / window_size)

    print(f"\nCPU usage: {n} samples, {window_size}-second moving average")
    print(f"(Sliding window: O(n) total, O(1) per step)\n")

    # Show a slice around the spike
    print(f"  {'Time':>4}  {'Raw CPU':>8}  {'Moving Avg':>10}  Visual")
    print(f"  {'----':>4}  {'-------':>8}  {'----------':>10}  ------")
    for i in range(20, 45):
        raw = cpu[i]
        avg = moving_avg[i - window_size + 1] if i >= window_size - 1 else None
        bar = '#' * int(raw / 2)
        avg_str = f"{avg:>10.1f}" if avg else f"{'N/A':>10}"
        print(f"  t={i:>2}  {raw:>8.1f}  {avg_str}  {bar}")

    print(f"\n  The moving average smooths the spike, showing the trend.")
    print(f"  Sliding window is O(n) vs O(n*k) for recomputing each window.\n")


# ==========================================================================
# MAIN
# ==========================================================================

if __name__ == "__main__":
    print()
    print("  DAY 21: IN-MEMORY COLUMN STORE")
    print("  Arrays as Database Primitives")
    print("  Tying together: arrays, binary search, prefix sums,")
    print("  sliding window, and two pointers from Week 3")
    print()

    demo_basic_operations()
    demo_sorted_index()
    demo_prefix_sums()
    demo_rle_compression()
    demo_benchmark()
    demo_sliding_window_on_columns()

    print("=" * 70)
    print("SUMMARY: What Each Week 3 Technique Contributed")
    print("=" * 70)
    print("""
  Day 15-16 (Arrays):
    Column store IS an array-based storage layout. Each column
    is a contiguous array, giving sequential access patterns
    that exploit CPU cache prefetching.

  Day 17 (Two Pointers):
    Merge-join on two sorted columns uses two pointers advancing
    through both arrays simultaneously — O(n+m) vs O(n*m) nested loops.

  Day 18 (Sliding Window):
    Moving averages on time-series columns use the sliding window
    technique — O(1) per step instead of recomputing the window.

  Day 19 (Prefix Sums):
    Pre-computed prefix sums on numeric columns give O(1) range
    aggregation — SUM/AVG over any row range in constant time.

  Day 20 (Binary Search):
    Sorted column indexes use binary search for O(log n) range
    boundary lookup, turning full scans into targeted retrievals.

  Together these five techniques form the core of every real
  analytics database engine.
""")
