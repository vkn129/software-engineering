"""
Day 178: Capstone Part A — Query Optimizer (Part 2/2)

Extends day-177's query engine with a cost-based optimizer:
  * Per-column statistics (row count, ndv, min, max).
  * Selectivity estimates for predicates.
  * Cost model for SeqScan/IndexScan/HashJoin/SortMergeJoin.
  * Plan enumeration: best access path per table.
  * System-R-style DP for join ordering.

Run me:
    python3 day-178/query_optimizer.py
"""

import math
import sys
import os

# Import day-177's engine. Folders use dashes so we go via path injection.
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', 'day-177')))

from query_engine import (  # noqa: E402
    Table, SeqScan, IndexScan, Filter, Project, HashJoin, SortMergeJoin,
    parse_sql, _compare,
)


# ===========================================================================
# 1. Statistics
# ===========================================================================

class TableStats:
    """Per-table statistics. Built once at load time (like ANALYZE)."""

    def __init__(self, table):
        self.row_count = len(table.rows)
        self.ndv = {}
        self.min = {}
        self.max = {}
        if not table.rows:
            return
        for col in table.columns:
            vals = [r[col] for r in table.rows]
            self.ndv[col] = len(set(vals))
            try:
                self.min[col] = min(vals)
                self.max[col] = max(vals)
            except TypeError:
                self.min[col] = None
                self.max[col] = None


def build_stats(catalog):
    return {name: TableStats(tbl) for name, tbl in catalog.items()}


# ===========================================================================
# 2. Selectivity
# ===========================================================================

def selectivity(stats, table_name, pred):
    """
    pred = ((tname, col), op, value)
    Returns fraction in [0,1] of rows expected to match.
    """
    (tname, col), op, val = pred
    s = stats.get(table_name)
    if not s or col not in s.ndv:
        return 0.5  # no info, guess half

    ndv = max(1, s.ndv[col])
    if op == '=':
        return 1.0 / ndv
    if op == '!=':
        return max(0.0, 1.0 - 1.0 / ndv)

    lo = s.min.get(col)
    hi = s.max.get(col)
    if lo is None or hi is None or hi == lo:
        # No range info → guess 1/3 (textbook fallback)
        return 1.0 / 3.0
    span = hi - lo
    if op == '<':
        return _clamp((val - lo) / span)
    if op == '<=':
        return _clamp((val - lo) / span)
    if op == '>':
        return _clamp((hi - val) / span)
    if op == '>=':
        return _clamp((hi - val) / span)
    return 1.0 / 3.0


def _clamp(x):
    return max(0.0, min(1.0, x))


def combined_selectivity(stats, table_name, preds):
    """Independence assumption: multiply selectivities of conjuncts."""
    s = 1.0
    for p in preds:
        s *= selectivity(stats, table_name, p)
    return s


# ===========================================================================
# 3. Cost Model
# ===========================================================================

# Tuning constants
COST_SEQ = 1.0          # per row scanned
COST_IDX = 4.0          # per row fetched via index (random I/O)
COST_HASH_JOIN = 2.0    # per row, both sides
COST_SORT_MERGE = 3.0   # per (n log n) term


def cost_seq_scan(n_rows):
    return COST_SEQ * max(1, n_rows)


def cost_index_scan(n_matched):
    return COST_IDX * max(1, n_matched)


def cost_hash_join(n_left, n_right):
    return COST_HASH_JOIN * (n_left + n_right)


def cost_sort_merge(n_left, n_right):
    return COST_SORT_MERGE * (
        n_left * math.log2(max(2, n_left)) + n_right * math.log2(max(2, n_right))
    )


# ===========================================================================
# 4. Access Path Selection (single table)
# ===========================================================================

class AccessPath:
    """One candidate scan over a single table, with cost + cardinality."""

    def __init__(self, op, est_rows, cost, applied_preds):
        self.op = op
        self.est_rows = est_rows
        self.cost = cost
        self.applied_preds = applied_preds  # preds pushed into the scan

    def __repr__(self):
        return f"AccessPath(rows={self.est_rows:.1f}, cost={self.cost:.1f}, op={self.op})"


def best_access_path(table, table_name, preds, stats):
    """
    Enumerate access paths and return the cheapest one wrapped in Filter
    for any non-pushed predicates.
    """
    s = stats[table_name]
    n = s.row_count
    sel_all = combined_selectivity(stats, table_name, preds)
    final_rows = max(1.0, sel_all * n)

    # Candidate 1: SeqScan + Filter
    seq_op = SeqScan(table, alias=table_name)
    if preds:
        seq_op = Filter(seq_op, preds)
    seq_cost = cost_seq_scan(n)
    seq_path = AccessPath(seq_op, final_rows, seq_cost, applied_preds=[])

    # Candidate 2: IndexScan on any indexed column with a usable predicate
    best = seq_path
    for p in preds:
        (tname, col), op, val = p
        if tname and tname != table_name:
            continue
        if not table.has_index(col):
            continue
        sel = selectivity(stats, table_name, p)
        matched = max(1.0, sel * n)
        idx_op = IndexScan(table, col, op, val, alias=table_name)
        remaining = [q for q in preds if q is not p]
        if remaining:
            idx_op = Filter(idx_op, remaining)
        idx_cost = cost_index_scan(matched)
        # The final post-filter rowcount is still final_rows.
        path = AccessPath(idx_op, final_rows, idx_cost, applied_preds=[p])
        if path.cost < best.cost:
            best = path
    return best


# ===========================================================================
# 5. Join Strategy Selection
# ===========================================================================

def best_join(left_path, right_path, left_key, right_key):
    """Pick hash join vs sort-merge based on cost; return new AccessPath."""
    nl, nr = left_path.est_rows, right_path.est_rows
    h_cost = left_path.cost + right_path.cost + cost_hash_join(nl, nr)
    sm_cost = left_path.cost + right_path.cost + cost_sort_merge(nl, nr)

    # Estimate output rows: simple primary-key-style estimate.
    # Output ≈ (nl * nr) / max(ndv). With no info, use min(nl, nr) * fanout.
    est_out = min(nl, nr) * 2.0  # rough

    if h_cost <= sm_cost:
        op = HashJoin(left_path.op, right_path.op, left_key, right_key)
        return AccessPath(op, est_out, h_cost, applied_preds=[])
    op = SortMergeJoin(left_path.op, right_path.op, left_key, right_key)
    return AccessPath(op, est_out, sm_cost, applied_preds=[])


# ===========================================================================
# 6. Optimizer entry point
# ===========================================================================

def optimize(ast, catalog, stats):
    """
    Build a physical plan minimizing estimated cost.
    Supports single-table queries and 2-table joins (as in day-177).
    """
    from_clause = ast['from']
    where = ast['where'] or []

    if from_clause['kind'] == 'table':
        tname = from_clause['name']
        tbl = catalog[tname]
        path = best_access_path(tbl, tname, where, stats)
        return Project(path.op, ast['select']), path

    # 2-way join
    lname = from_clause['left']
    rname = from_clause['right']
    l_qual, r_qual = from_clause['on']
    l_preds = [p for p in where if (p[0][0] in (None, lname))
               and p[0][1] in catalog[lname].columns]
    r_preds = [p for p in where if p[0][0] == rname
               or (p[0][0] is None and p[0][1] in catalog[rname].columns
                   and p[0][1] not in catalog[lname].columns)]
    # post-join preds: anything left over (we keep simple)
    used = set(id(p) for p in l_preds + r_preds)
    post = [p for p in where if id(p) not in used]

    l_path = best_access_path(catalog[lname], lname, l_preds, stats)
    r_path = best_access_path(catalog[rname], rname, r_preds, stats)

    lk = f"{l_qual[0]}.{l_qual[1]}"
    rk = f"{r_qual[0]}.{r_qual[1]}"
    join_path = best_join(l_path, r_path, lk, rk)

    op = join_path.op
    if post:
        op = Filter(op, post)
    return Project(op, ast['select']), join_path


# ===========================================================================
# 7. N-way join ordering (System-R DP)
# ===========================================================================

def best_join_order(table_names, join_conditions, stats):
    """
    Bottom-up DP over subsets of tables. Returns (best_order, est_cost).
    join_conditions: dict frozenset({t1, t2}) -> (col1, col2) join keys.
    """
    n = len(table_names)
    if n == 0:
        return [], 0.0
    name_to_idx = {t: i for i, t in enumerate(table_names)}

    # Base case: single tables
    best = {}  # frozenset -> (cost, est_rows, order_tuple)
    for t in table_names:
        rows = stats[t].row_count
        best[frozenset([t])] = (cost_seq_scan(rows), rows, (t,))

    for size in range(2, n + 1):
        from itertools import combinations
        for subset in combinations(table_names, size):
            S = frozenset(subset)
            best_cost = math.inf
            best_entry = None
            # Try every split S = L ∪ R
            for k in range(1, size):
                for L_tup in combinations(subset, k):
                    L = frozenset(L_tup)
                    R = S - L
                    if L not in best or R not in best:
                        continue
                    # Need an applicable join condition crossing L/R
                    crossing = False
                    for pair in join_conditions:
                        a, b = tuple(pair)
                        if (a in L and b in R) or (b in L and a in R):
                            crossing = True
                            break
                    if not crossing:
                        continue
                    cl, rl, _ = best[L]
                    cr, rr, _ = best[R]
                    join_c = cost_hash_join(rl, rr)
                    total = cl + cr + join_c
                    if total < best_cost:
                        best_cost = total
                        out_rows = min(rl, rr) * 2.0  # crude
                        best_entry = (total, out_rows,
                                      best[L][2] + best[R][2])
            if best_entry:
                best[S] = best_entry

    full = frozenset(table_names)
    if full not in best:
        return list(table_names), math.inf
    cost, _, order = best[full]
    return list(order), cost


# ===========================================================================
# 8. Demo
# ===========================================================================

def make_catalog():
    # Reuse the schema from day-177 but with more rows for the optimizer to
    # have something to chew on.
    emps = Table('emp', ['id', 'name', 'dept_id', 'salary'], [
        {'id': i, 'name': f'E{i}', 'dept_id': (i % 5) + 10,
         'salary': 30000 + (i * 1731) % 100000}
        for i in range(1, 201)
    ])
    emps.build_index('salary')
    emps.build_index('dept_id')

    depts = Table('dept', ['id', 'name'], [
        {'id': 10, 'name': 'Engineering'},
        {'id': 11, 'name': 'Sales'},
        {'id': 12, 'name': 'Support'},
        {'id': 13, 'name': 'Research'},
        {'id': 14, 'name': 'Marketing'},
    ])
    depts.build_index('id')

    projects = Table('proj', ['id', 'dept_id', 'name'], [
        {'id': i, 'dept_id': 10 + (i % 5), 'name': f'P{i}'}
        for i in range(1, 31)
    ])
    projects.build_index('dept_id')

    return {'emp': emps, 'dept': depts, 'proj': projects}


def run_optimized(sql, catalog, stats, *, show_plan=True):
    ast = parse_sql(sql)
    plan_op, path = optimize(ast, catalog, stats)
    if show_plan:
        print(f"  OPT PLAN: {plan_op}")
        print(f"  est cost: {path.cost:.1f}   est rows: {path.est_rows:.1f}")
    return list(plan_op)


def demo():
    cat = make_catalog()
    stats = build_stats(cat)

    print("=" * 60)
    print("DEMO 1: Single-table — selectivity drives plan choice")
    print("=" * 60)

    # Selective predicate → index wins
    sql1 = "SELECT name FROM emp WHERE salary > 120000"
    print(f"\nSQL: {sql1}")
    print(f"  stats: emp.salary min={stats['emp'].min['salary']} "
          f"max={stats['emp'].max['salary']} ndv={stats['emp'].ndv['salary']}")
    rows = run_optimized(sql1, cat, stats)
    print(f"  -> {len(rows)} rows")

    # Non-selective predicate → seq scan wins (most rows match)
    sql2 = "SELECT name FROM emp WHERE salary > 35000"
    print(f"\nSQL: {sql2}")
    rows = run_optimized(sql2, cat, stats)
    print(f"  -> {len(rows)} rows")

    print("\n" + "=" * 60)
    print("DEMO 2: Two-way join — optimizer picks hash vs sort-merge")
    print("=" * 60)
    sql3 = "SELECT emp.name, dept.name FROM emp JOIN dept ON emp.dept_id = dept.id"
    print(f"\nSQL: {sql3}")
    rows = run_optimized(sql3, cat, stats)
    print(f"  -> {len(rows)} rows")

    # Same join but with a selective predicate on emp — should still pick
    # the cheaper join.
    sql4 = ("SELECT emp.name, dept.name FROM emp JOIN dept ON emp.dept_id = dept.id "
            "WHERE emp.salary > 100000")
    print(f"\nSQL: {sql4}")
    rows = run_optimized(sql4, cat, stats)
    print(f"  -> {len(rows)} rows")

    print("\n" + "=" * 60)
    print("DEMO 3: Join-order DP (System-R style)")
    print("=" * 60)
    # 3 tables: emp(200) JOIN dept(5) JOIN proj(30) on dept_id
    tables = ['emp', 'dept', 'proj']
    conds = {
        frozenset({'emp', 'dept'}): ('dept_id', 'id'),
        frozenset({'dept', 'proj'}): ('id', 'dept_id'),
    }
    order, cost = best_join_order(tables, conds, stats)
    print(f"\nTables: {tables}")
    print(f"  Optimal order: {order}")
    print(f"  Estimated cost: {cost:.1f}")
    print("  (Smaller tables joined earlier reduces intermediate cardinality.)")

    print("\n" + "=" * 60)
    print("DEMO 4: Cost model in action")
    print("=" * 60)
    # Show the math for one decision
    n_left = 200
    n_right = 5
    hc = cost_hash_join(n_left, n_right)
    sm = cost_sort_merge(n_left, n_right)
    print(f"  Join 200 x 5:")
    print(f"    hash_join:       {hc:.1f}")
    print(f"    sort_merge_join: {sm:.1f}")
    print(f"    optimizer picks: {'hash' if hc <= sm else 'sort-merge'}")


if __name__ == "__main__":
    demo()
