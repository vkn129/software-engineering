"""
Day 21 Practice: In-Memory Column Store
=========================================
Build on the column store from column_store.py.
"""


# =============================================================================
# Exercise 1: Add WHERE clause filtering
# =============================================================================
def select_where(columns, col_name, operator, value):
    """
    Filter rows where column meets condition.

    TODO: Implement
    - operator is one of: '=', '!=', '<', '>', '<=', '>='
    - Return list of row indices matching the condition
    - For sorted columns, use binary search for '<', '>', '<=', '>='

    Example:
        columns = {'age': [25, 30, 35, 40], 'name': ['alice', 'bob', 'charlie', 'dave']}
        select_where(columns, 'age', '>', 30) → [2, 3]
    """
    pass


# =============================================================================
# Exercise 2: Aggregation functions
# =============================================================================
def aggregate(column, func, indices=None):
    """
    Compute aggregate over a column (optionally filtered by indices).

    TODO: Implement SUM, AVG, COUNT, MIN, MAX
    - func is one of: 'SUM', 'AVG', 'COUNT', 'MIN', 'MAX'
    - If indices is provided, only aggregate those rows
    """
    pass


# =============================================================================
# Exercise 3: Run-Length Encoding for sorted columns
# =============================================================================
def rle_encode(column):
    """
    Compress a sorted column using run-length encoding.

    TODO: Implement
    Returns list of (value, count) tuples.

    Example: [1, 1, 1, 2, 2, 3] → [(1, 3), (2, 2), (3, 1)]

    Why this matters: sorted columns in databases often have long runs
    of repeated values. RLE can compress 1M rows into thousands of runs.
    """
    pass


def rle_decode(encoded):
    """Decompress RLE back to original column."""
    pass


# =============================================================================
# Exercise 4: Column store vs Row store benchmark
# =============================================================================
def benchmark_column_vs_row(num_rows, num_cols):
    """
    Compare access patterns for column store vs row store.

    TODO: Implement
    - Create row store: list of dicts [{col1: v, col2: v, ...}, ...]
    - Create column store: dict of lists {col1: [...], col2: [...], ...}
    - Time: sum of one column (column store wins — sequential access)
    - Time: access one full row (row store wins — one lookup)
    - Return timing results
    """
    pass


# =============================================================================
# SOLUTIONS
# =============================================================================

def _sol_select_where(columns, col_name, operator, value):
    col = columns[col_name]
    ops = {
        '=': lambda x: x == value,
        '!=': lambda x: x != value,
        '<': lambda x: x < value,
        '>': lambda x: x > value,
        '<=': lambda x: x <= value,
        '>=': lambda x: x >= value,
    }
    return [i for i, x in enumerate(col) if ops[operator](x)]


def _sol_aggregate(column, func, indices=None):
    data = [column[i] for i in indices] if indices else column
    if not data:
        return 0
    if func == 'SUM':
        return sum(data)
    elif func == 'AVG':
        return sum(data) / len(data)
    elif func == 'COUNT':
        return len(data)
    elif func == 'MIN':
        return min(data)
    elif func == 'MAX':
        return max(data)


def _sol_rle_encode(column):
    if not column:
        return []
    runs = []
    current, count = column[0], 1
    for i in range(1, len(column)):
        if column[i] == current:
            count += 1
        else:
            runs.append((current, count))
            current, count = column[i], 1
    runs.append((current, count))
    return runs


def _sol_rle_decode(encoded):
    return [val for val, count in encoded for _ in range(count)]


def run_tests():
    print("=" * 60)
    print("Day 21 Practice Tests: Column Store")
    print("=" * 60)

    columns = {'age': [25, 30, 35, 40], 'name': ['alice', 'bob', 'charlie', 'dave']}
    assert _sol_select_where(columns, 'age', '>', 30) == [2, 3]
    assert _sol_select_where(columns, 'age', '=', 25) == [0]
    print("✓ Exercise 1: WHERE clause filtering")

    assert _sol_aggregate([10, 20, 30], 'SUM') == 60
    assert _sol_aggregate([10, 20, 30], 'AVG') == 20.0
    assert _sol_aggregate([10, 20, 30], 'COUNT', [0, 2]) == 2
    print("✓ Exercise 2: Aggregation functions")

    encoded = _sol_rle_encode([1, 1, 1, 2, 2, 3])
    assert encoded == [(1, 3), (2, 2), (3, 1)]
    assert _sol_rle_decode(encoded) == [1, 1, 1, 2, 2, 3]
    print("✓ Exercise 3: Run-length encoding")

    print("\nAll tests passed!")


if __name__ == "__main__":
    run_tests()
