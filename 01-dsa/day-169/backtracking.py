"""
Day 169: Backtracking Patterns — From Scratch

N-Queens with bitmask pruning, Sudoku with MRV + constraint propagation,
and a generalized backtracking template for CSPs.

Time: exponential worst case, but pruning kills most branches.
"""

import time


# ---------------------------------------------------------------------------
# 1. N-Queens (column + two diagonals as sets)
# ---------------------------------------------------------------------------

def solve_n_queens(n):
    """
    Return all solutions to the N-queens problem.
    Each solution is a list of column indices, one per row.
    """
    solutions = []
    cols = set()
    diag1 = set()  # r + c (anti-diagonal)
    diag2 = set()  # r - c (main diagonal)
    placement = [0] * n

    def backtrack(row):
        if row == n:
            solutions.append(placement[:])
            return
        for col in range(n):
            if col in cols or (row + col) in diag1 or (row - col) in diag2:
                continue
            cols.add(col)
            diag1.add(row + col)
            diag2.add(row - col)
            placement[row] = col
            backtrack(row + 1)
            cols.remove(col)
            diag1.remove(row + col)
            diag2.remove(row - col)

    backtrack(0)
    return solutions


def count_n_queens_bitmask(n):
    """
    Count N-queens solutions using bitmasks. ~5-10x faster than set version.
    """
    count = [0]

    def backtrack(row, cols, d1, d2):
        if row == n:
            count[0] += 1
            return
        # Bits set = columns BLOCKED. Flip and mask to n bits.
        available = ((1 << n) - 1) & ~(cols | d1 | d2)
        while available:
            bit = available & -available  # lowest set bit
            available ^= bit
            # Shift d1 left, d2 right for next row (diagonal propagation)
            backtrack(row + 1, cols | bit, (d1 | bit) << 1, (d2 | bit) >> 1)

    backtrack(0, 0, 0, 0)
    return count[0]


# ---------------------------------------------------------------------------
# 2. Sudoku Solver with MRV + Forward Checking
# ---------------------------------------------------------------------------

class SudokuSolver:
    """
    9x9 Sudoku with three optimizations:
      - MRV: pick the cell with fewest candidates next
      - Forward checking: prune peer domains on assignment
      - Naked singles: fill forced cells before branching
    """

    def __init__(self, board):
        self.board = [row[:] for row in board]
        # Candidates for each empty cell
        self.candidates = [[set() for _ in range(9)] for _ in range(9)]
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    self.candidates[r][c] = self._init_candidates(r, c)

    def _init_candidates(self, r, c):
        used = set()
        for i in range(9):
            used.add(self.board[r][i])
            used.add(self.board[i][c])
        br, bc = (r // 3) * 3, (c // 3) * 3
        for i in range(3):
            for j in range(3):
                used.add(self.board[br + i][bc + j])
        return set(range(1, 10)) - used

    def _peers(self, r, c):
        peers = set()
        for i in range(9):
            peers.add((r, i))
            peers.add((i, c))
        br, bc = (r // 3) * 3, (c // 3) * 3
        for i in range(3):
            for j in range(3):
                peers.add((br + i, bc + j))
        peers.discard((r, c))
        return peers

    def _pick_mrv(self):
        """Return (r, c) of the empty cell with fewest candidates."""
        best = None
        best_size = 10
        for r in range(9):
            for c in range(9):
                if self.board[r][c] == 0:
                    size = len(self.candidates[r][c])
                    if size < best_size:
                        best_size = size
                        best = (r, c)
                        if size <= 1:
                            return best
        return best

    def _assign(self, r, c, v):
        """Assign v to (r,c). Return list of (pr, pc, v) removed from peers,
        or None if a peer becomes empty (forward-check failure)."""
        self.board[r][c] = v
        removed = []
        for pr, pc in self._peers(r, c):
            if self.board[pr][pc] == 0 and v in self.candidates[pr][pc]:
                self.candidates[pr][pc].discard(v)
                removed.append((pr, pc))
                if not self.candidates[pr][pc]:
                    return None  # dead end
        return removed

    def _unassign(self, r, c, v, removed):
        self.board[r][c] = 0
        for pr, pc in removed:
            self.candidates[pr][pc].add(v)

    def solve(self):
        cell = self._pick_mrv()
        if cell is None:
            return True  # filled
        r, c = cell
        for v in sorted(self.candidates[r][c]):
            saved = self.candidates[r][c]
            self.candidates[r][c] = set()
            removed = self._assign(r, c, v)
            if removed is not None and self.solve():
                return True
            self._unassign(r, c, v, removed or [])
            self.candidates[r][c] = saved
        return False


def solve_sudoku(board):
    """Solve a 9x9 Sudoku in place (0 = empty). Return True if solvable."""
    solver = SudokuSolver(board)
    if solver.solve():
        for r in range(9):
            for c in range(9):
                board[r][c] = solver.board[r][c]
        return True
    return False


# ---------------------------------------------------------------------------
# 3. Generalized Backtracking Template (CSP)
# ---------------------------------------------------------------------------

def csp_backtrack(variables, domains, constraints):
    """
    Generic CSP solver.
      variables: list of variable names
      domains: dict var -> list of values
      constraints: list of (var_tuple, predicate) — predicate(values) -> bool

    Returns a dict assignment, or None if unsatisfiable.
    """
    assignment = {}

    def consistent(var, value):
        assignment[var] = value
        ok = True
        for vars_t, pred in constraints:
            if all(v in assignment for v in vars_t):
                if not pred(*[assignment[v] for v in vars_t]):
                    ok = False
                    break
        del assignment[var]
        return ok

    def select():
        # MRV: pick unassigned variable with smallest remaining domain
        unassigned = [v for v in variables if v not in assignment]
        return min(unassigned, key=lambda v: len(domains[v]))

    def backtrack():
        if len(assignment) == len(variables):
            return dict(assignment)
        var = select()
        for value in domains[var]:
            if consistent(var, value):
                assignment[var] = value
                result = backtrack()
                if result is not None:
                    return result
                del assignment[var]
        return None

    return backtrack()


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_n_queens():
    print("=" * 60)
    print("DEMO 1: N-Queens")
    print("=" * 60)
    for n in [4, 8, 10]:
        sols = solve_n_queens(n)
        print(f"  N={n}: {len(sols)} solutions")
    print("\n  First 4-queens solution (one queen per row):")
    sol = solve_n_queens(4)[0]
    for r in range(4):
        row = ["Q" if sol[r] == c else "." for c in range(4)]
        print("    " + " ".join(row))


def demo_n_queens_speed():
    print("\n" + "=" * 60)
    print("DEMO 2: Set vs Bitmask N-Queens")
    print("=" * 60)
    n = 12
    t1 = time.perf_counter()
    sols = solve_n_queens(n)
    set_time = time.perf_counter() - t1
    t1 = time.perf_counter()
    count = count_n_queens_bitmask(n)
    bm_time = time.perf_counter() - t1
    print(f"  N={n}: {len(sols)} solutions")
    print(f"    Set-based:   {set_time:.3f}s")
    print(f"    Bitmask:     {bm_time:.3f}s  (count={count})")
    print(f"    Speedup:     {set_time/bm_time:.1f}x")


def demo_sudoku():
    print("\n" + "=" * 60)
    print("DEMO 3: Sudoku with MRV + Forward Checking")
    print("=" * 60)
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]
    t1 = time.perf_counter()
    ok = solve_sudoku(puzzle)
    dt = time.perf_counter() - t1
    print(f"  Solved: {ok} in {dt*1000:.2f} ms")
    for row in puzzle:
        print("    " + " ".join(str(v) for v in row))


def demo_csp():
    print("\n" + "=" * 60)
    print("DEMO 4: Generalized CSP — Map Coloring")
    print("=" * 60)
    # Australia map coloring: WA NT SA Q NSW V T
    variables = ["WA", "NT", "SA", "Q", "NSW", "V", "T"]
    domains = {v: ["R", "G", "B"] for v in variables}
    neighbors = [("WA", "NT"), ("WA", "SA"), ("NT", "SA"), ("NT", "Q"),
                 ("SA", "Q"), ("SA", "NSW"), ("SA", "V"), ("Q", "NSW"),
                 ("NSW", "V")]
    constraints = [(pair, lambda a, b: a != b) for pair in neighbors]
    sol = csp_backtrack(variables, domains, constraints)
    print(f"  Assignment: {sol}")


if __name__ == "__main__":
    demo_n_queens()
    demo_n_queens_speed()
    demo_sudoku()
    demo_csp()
