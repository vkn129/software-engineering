"""
Day 177: Capstone Part A — Database Query Engine (Part 1/2)

A working SQL query engine. Stdlib only. From scratch.

Pipeline:
  SQL text -> tokens -> AST -> logical plan -> physical plan -> rows

Operators: SeqScan, IndexScan, Filter, Project, HashJoin, SortMergeJoin.

Run me:
    python3 day-177/query_engine.py
"""

import re
import bisect
from collections import defaultdict


# ===========================================================================
# 1. Storage: in-memory tables + a simple sorted-key index
# ===========================================================================

class Table:
    """Row-oriented in-memory table. Columns are named; rows are dicts."""

    def __init__(self, name, columns, rows):
        self.name = name
        self.columns = columns
        self.rows = list(rows)
        # column -> sorted list of (value, row_index) pairs (acts as B-tree leaf)
        self.indexes = {}

    def build_index(self, column):
        idx = [(row[column], i) for i, row in enumerate(self.rows)]
        idx.sort(key=lambda p: p[0])
        self.indexes[column] = idx

    def has_index(self, column):
        return column in self.indexes

    def index_range(self, column, op, value):
        """Use sorted index to return matching row indices."""
        idx = self.indexes[column]
        keys = [p[0] for p in idx]
        if op == '=':
            lo = bisect.bisect_left(keys, value)
            hi = bisect.bisect_right(keys, value)
            return [idx[i][1] for i in range(lo, hi)]
        if op == '<':
            hi = bisect.bisect_left(keys, value)
            return [idx[i][1] for i in range(0, hi)]
        if op == '<=':
            hi = bisect.bisect_right(keys, value)
            return [idx[i][1] for i in range(0, hi)]
        if op == '>':
            lo = bisect.bisect_right(keys, value)
            return [idx[i][1] for i in range(lo, len(idx))]
        if op == '>=':
            lo = bisect.bisect_left(keys, value)
            return [idx[i][1] for i in range(lo, len(idx))]
        if op == '!=':
            lo = bisect.bisect_left(keys, value)
            hi = bisect.bisect_right(keys, value)
            return ([idx[i][1] for i in range(0, lo)] +
                    [idx[i][1] for i in range(hi, len(idx))])
        raise ValueError(f"bad op: {op}")


# ===========================================================================
# 2. Tokenizer
# ===========================================================================

TOKEN_RE = re.compile(
    r"\s*(?:"
    r"(?P<num>-?\d+(?:\.\d+)?)|"
    r"(?P<str>'[^']*')|"
    r"(?P<op><=|>=|!=|=|<|>)|"
    r"(?P<sym>[(),.*])|"
    r"(?P<ident>[A-Za-z_][A-Za-z0-9_]*)"
    r")"
)


def tokenize(sql):
    toks = []
    pos = 0
    while pos < len(sql):
        m = TOKEN_RE.match(sql, pos)
        if not m:
            if sql[pos].isspace():
                pos += 1
                continue
            raise SyntaxError(f"bad char at {pos}: {sql[pos]!r}")
        pos = m.end()
        for kind in ('num', 'str', 'op', 'sym', 'ident'):
            val = m.group(kind)
            if val is not None:
                if kind == 'num':
                    val = float(val) if '.' in val else int(val)
                elif kind == 'str':
                    val = val[1:-1]
                toks.append((kind, val))
                break
    return toks


# ===========================================================================
# 3. AST + Parser (recursive descent)
# ===========================================================================

class Parser:
    """Tiny SQL subset: SELECT cols FROM t [JOIN t2 ON ...] [WHERE ...]."""

    KEYWORDS = {'select', 'from', 'where', 'join', 'on', 'and'}

    def __init__(self, tokens):
        self.toks = tokens
        self.pos = 0

    def peek(self):
        if self.pos >= len(self.toks):
            return (None, None)
        k, v = self.toks[self.pos]
        # Lowercase identifiers for case-insensitive keyword matching
        if k == 'ident' and isinstance(v, str):
            return (k, v.lower())
        return (k, v)

    def eat(self, kind=None, val=None):
        if self.pos >= len(self.toks):
            raise SyntaxError("unexpected EOF")
        k, v = self.toks[self.pos]
        if kind and k != kind:
            raise SyntaxError(f"expected {kind}, got {k}={v!r}")
        if val is not None and (isinstance(v, str) and v.lower() != val):
            raise SyntaxError(f"expected {val!r}, got {v!r}")
        self.pos += 1
        # Normalize identifiers to lowercase (SQL case-insensitive)
        if k == 'ident' and isinstance(v, str):
            return v.lower()
        return v

    def parse(self):
        self.eat('ident', 'select')
        cols = self.parse_columns()
        self.eat('ident', 'from')
        from_clause = self.parse_from()
        where = None
        if self.peek() == ('ident', 'where'):
            self.eat('ident', 'where')
            where = self.parse_predicates()
        return {'select': cols, 'from': from_clause, 'where': where}

    def parse_columns(self):
        if self.peek() == ('sym', '*'):
            self.eat('sym')
            return ['*']
        cols = [self.parse_qualified()]
        while self.peek() == ('sym', ','):
            self.eat('sym')
            cols.append(self.parse_qualified())
        return cols

    def parse_qualified(self):
        """Parse `name` or `table.name`."""
        name = self.eat('ident')
        if self.peek() == ('sym', '.'):
            self.eat('sym')
            col = self.eat('ident')
            return (name, col)
        return (None, name)

    def parse_from(self):
        t1 = self.eat('ident')
        if self.peek() == ('ident', 'join'):
            self.eat('ident', 'join')
            t2 = self.eat('ident')
            self.eat('ident', 'on')
            left = self.parse_qualified()
            self.eat('op')  # must be '='
            right = self.parse_qualified()
            return {'kind': 'join', 'left': t1, 'right': t2,
                    'on': (left, right)}
        return {'kind': 'table', 'name': t1}

    def parse_predicates(self):
        """Parse predicate AND predicate AND ... — each is `qual op literal`."""
        preds = [self.parse_predicate()]
        while self.peek() == ('ident', 'and'):
            self.eat('ident', 'and')
            preds.append(self.parse_predicate())
        return preds

    def parse_predicate(self):
        col = self.parse_qualified()
        op = self.eat('op')
        kind, val = self.peek()
        if kind in ('num', 'str'):
            self.eat(kind)
            return (col, op, val)
        raise SyntaxError(f"predicate rhs must be literal, got {kind}")


def parse_sql(sql):
    return Parser(tokenize(sql)).parse()


# ===========================================================================
# 4. Logical & Physical Plan (Volcano-style iterators)
# ===========================================================================

class SeqScan:
    def __init__(self, table, alias=None):
        self.table = table
        self.alias = alias or table.name

    def __iter__(self):
        for row in self.table.rows:
            yield {f"{self.alias}.{k}": v for k, v in row.items()}

    def __repr__(self):
        return f"SeqScan({self.table.name})"


class IndexScan:
    def __init__(self, table, column, op, value, alias=None):
        self.table = table
        self.column = column
        self.op = op
        self.value = value
        self.alias = alias or table.name

    def __iter__(self):
        for ri in self.table.index_range(self.column, self.op, self.value):
            row = self.table.rows[ri]
            yield {f"{self.alias}.{k}": v for k, v in row.items()}

    def __repr__(self):
        return f"IndexScan({self.table.name}.{self.column} {self.op} {self.value})"


class Filter:
    def __init__(self, child, preds):
        self.child = child
        self.preds = preds  # list of (qual_col, op, value)

    def __iter__(self):
        for row in self.child:
            if all(self._match(row, p) for p in self.preds):
                yield row

    @staticmethod
    def _match(row, pred):
        col, op, val = pred
        key = f"{col[0]}.{col[1]}" if col[0] else col[1]
        # If unqualified, search any column ending with .col
        if col[0] is None:
            cand = [k for k in row if k.endswith('.' + col[1])]
            if not cand:
                return False
            key = cand[0]
        lhs = row.get(key)
        if lhs is None:
            return False
        return _compare(lhs, op, val)

    def __repr__(self):
        return f"Filter({self.preds}, {self.child})"


def _compare(a, op, b):
    if op == '=':
        return a == b
    if op == '!=':
        return a != b
    if op == '<':
        return a < b
    if op == '<=':
        return a <= b
    if op == '>':
        return a > b
    if op == '>=':
        return a >= b
    raise ValueError(op)


class Project:
    def __init__(self, child, cols):
        self.child = child
        self.cols = cols  # list of (table_or_None, col), or ['*']

    def __iter__(self):
        for row in self.child:
            if self.cols == ['*']:
                yield dict(row)
                continue
            out = {}
            for tbl, col in self.cols:
                if tbl:
                    out[f"{tbl}.{col}"] = row.get(f"{tbl}.{col}")
                else:
                    cand = [k for k in row if k.endswith('.' + col)]
                    if cand:
                        out[col] = row[cand[0]]
            yield out

    def __repr__(self):
        return f"Project({self.cols}, {self.child})"


class HashJoin:
    """Equi-join. Builds hash on left input, probes with right."""

    def __init__(self, left, right, left_key, right_key):
        self.left = left
        self.right = right
        self.left_key = left_key  # 'table.col'
        self.right_key = right_key

    def __iter__(self):
        ht = defaultdict(list)
        for row in self.left:
            ht[row[self.left_key]].append(row)
        for r in self.right:
            for l in ht.get(r[self.right_key], ()):
                merged = dict(l)
                merged.update(r)
                yield merged

    def __repr__(self):
        return f"HashJoin({self.left_key}={self.right_key}, {self.left}, {self.right})"


class SortMergeJoin:
    """Equi-join via sort + merge."""

    def __init__(self, left, right, left_key, right_key):
        self.left = left
        self.right = right
        self.left_key = left_key
        self.right_key = right_key

    def __iter__(self):
        L = sorted(self.left, key=lambda r: r[self.left_key])
        R = sorted(self.right, key=lambda r: r[self.right_key])
        i = j = 0
        while i < len(L) and j < len(R):
            lk, rk = L[i][self.left_key], R[j][self.right_key]
            if lk < rk:
                i += 1
            elif lk > rk:
                j += 1
            else:
                # gather all equal on both sides, cross-product
                i_end = i
                while i_end < len(L) and L[i_end][self.left_key] == lk:
                    i_end += 1
                j_end = j
                while j_end < len(R) and R[j_end][self.right_key] == rk:
                    j_end += 1
                for a in range(i, i_end):
                    for b in range(j, j_end):
                        merged = dict(L[a])
                        merged.update(R[b])
                        yield merged
                i, j = i_end, j_end

    def __repr__(self):
        return f"SortMergeJoin({self.left_key}={self.right_key}, {self.left}, {self.right})"


# ===========================================================================
# 5. Planner: AST -> physical plan
# ===========================================================================

def plan(ast, catalog, join_strategy='hash'):
    """Build a physical plan from AST. catalog: name -> Table."""
    from_clause = ast['from']
    where = ast['where'] or []

    if from_clause['kind'] == 'table':
        tbl = catalog[from_clause['name']]
        plan_node = _scan_with_pushdown(tbl, where, tbl.name)
        remaining_preds = [p for p in where
                           if not _pushed(p, tbl, tbl.name)]
        if remaining_preds:
            plan_node = Filter(plan_node, remaining_preds)
    else:
        # join
        left_tbl = catalog[from_clause['left']]
        right_tbl = catalog[from_clause['right']]
        l_qual, r_qual = from_clause['on']
        # split where preds by table
        left_preds = [p for p in where if p[0][0] == left_tbl.name]
        right_preds = [p for p in where if p[0][0] == right_tbl.name]
        other_preds = [p for p in where
                       if p[0][0] not in (left_tbl.name, right_tbl.name)]

        l_scan = _scan_with_pushdown(left_tbl, left_preds, left_tbl.name)
        l_remaining = [p for p in left_preds
                       if not _pushed(p, left_tbl, left_tbl.name)]
        if l_remaining:
            l_scan = Filter(l_scan, l_remaining)

        r_scan = _scan_with_pushdown(right_tbl, right_preds, right_tbl.name)
        r_remaining = [p for p in right_preds
                       if not _pushed(p, right_tbl, right_tbl.name)]
        if r_remaining:
            r_scan = Filter(r_scan, r_remaining)

        lk = f"{l_qual[0]}.{l_qual[1]}"
        rk = f"{r_qual[0]}.{r_qual[1]}"
        if join_strategy == 'sort_merge':
            plan_node = SortMergeJoin(l_scan, r_scan, lk, rk)
        else:
            plan_node = HashJoin(l_scan, r_scan, lk, rk)
        if other_preds:
            plan_node = Filter(plan_node, other_preds)

    return Project(plan_node, ast['select'])


def _pushed(pred, table, alias):
    """Was this pred pushed into an IndexScan?"""
    (tname, col), op, val = pred
    if tname and tname != alias:
        return False
    return table.has_index(col)


def _scan_with_pushdown(table, preds, alias):
    for p in preds:
        (tname, col), op, val = p
        if (tname is None or tname == alias) and table.has_index(col):
            return IndexScan(table, col, op, val, alias)
    return SeqScan(table, alias)


# ===========================================================================
# 6. Execute
# ===========================================================================

def execute(sql, catalog, join_strategy='hash', explain=False):
    ast = parse_sql(sql)
    physical = plan(ast, catalog, join_strategy=join_strategy)
    if explain:
        print(f"  PLAN: {physical}")
    return list(physical)


# ===========================================================================
# 7. Demo
# ===========================================================================

def sample_catalog():
    emps = Table('emp', ['id', 'name', 'dept_id', 'salary'], [
        {'id': 1, 'name': 'Alice',   'dept_id': 10, 'salary': 90000},
        {'id': 2, 'name': 'Bob',     'dept_id': 20, 'salary': 60000},
        {'id': 3, 'name': 'Carol',   'dept_id': 10, 'salary': 75000},
        {'id': 4, 'name': 'Dan',     'dept_id': 30, 'salary': 45000},
        {'id': 5, 'name': 'Eve',     'dept_id': 20, 'salary': 110000},
        {'id': 6, 'name': 'Frank',   'dept_id': 10, 'salary': 55000},
        {'id': 7, 'name': 'Grace',   'dept_id': 40, 'salary': 95000},
    ])
    emps.build_index('salary')
    emps.build_index('dept_id')

    depts = Table('dept', ['id', 'name'], [
        {'id': 10, 'name': 'Engineering'},
        {'id': 20, 'name': 'Sales'},
        {'id': 30, 'name': 'Support'},
        {'id': 40, 'name': 'Research'},
    ])
    depts.build_index('id')
    return {'emp': emps, 'dept': depts}


def demo():
    cat = sample_catalog()

    print("=" * 60)
    print("DEMO: Day 177 Query Engine")
    print("=" * 60)

    queries = [
        "SELECT name, salary FROM emp WHERE salary > 60000",
        "SELECT name FROM emp WHERE dept_id = 10",
        "SELECT * FROM emp WHERE salary >= 90000",
        "SELECT emp.name, dept.name FROM emp JOIN dept ON emp.dept_id = dept.id",
        "SELECT emp.name, dept.name FROM emp JOIN dept ON emp.dept_id = dept.id WHERE emp.salary > 70000",
    ]

    for sql in queries:
        print(f"\nSQL: {sql}")
        rows = execute(sql, cat, explain=True)
        for r in rows:
            print(f"    {r}")

    # Compare join strategies on the same query
    print("\n" + "=" * 60)
    print("Compare Hash Join vs Sort-Merge Join")
    print("=" * 60)
    sql = "SELECT emp.name, dept.name FROM emp JOIN dept ON emp.dept_id = dept.id"
    for strat in ('hash', 'sort_merge'):
        rows = execute(sql, cat, join_strategy=strat, explain=True)
        print(f"  [{strat}] -> {len(rows)} rows")


if __name__ == "__main__":
    demo()
