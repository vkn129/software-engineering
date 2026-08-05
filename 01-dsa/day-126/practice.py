"""
Day 126 Practice: Sequence Alignment (Needleman-Wunsch, Smith-Waterman, Gotoh)

6 exercises. Implement TODOs, then run: python practice.py
"""

NEG = float("-inf")
GAP = "-"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


def _sub(x, y, match, mismatch):
    return match if x == y else mismatch


# ---------------------------------------------------------------------------
# Exercise 1: Re-score a finished alignment under the affine model
# ---------------------------------------------------------------------------

def score_affine_alignment(aligned_a, aligned_b, match=2, mismatch=-1,
                           gap_open=3, gap_extend=1):
    """
    Score two equal-length aligned strings. A run of L consecutive gaps in one
    sequence costs gap_open + L*gap_extend (both given as positive penalties).
    """
    # TODO: track whether you are CONTINUING a gap run or starting one
    pass


def _sol_score_affine_alignment(aligned_a, aligned_b, match=2, mismatch=-1,
                                gap_open=3, gap_extend=1):
    total = 0
    run_in_a = run_in_b = False
    for ca, cb in zip(aligned_a, aligned_b):
        if ca == GAP:
            total -= gap_extend if run_in_a else (gap_open + gap_extend)
            run_in_a, run_in_b = True, False
        elif cb == GAP:
            total -= gap_extend if run_in_b else (gap_open + gap_extend)
            run_in_a, run_in_b = False, True
        else:
            total += _sub(ca, cb, match, mismatch)
            run_in_a = run_in_b = False
    return total


# ---------------------------------------------------------------------------
# Exercise 2: Needleman-Wunsch score (global, linear gaps)
# ---------------------------------------------------------------------------

def nw_score(a, b, match=1, mismatch=-1, gap=-2):
    """Global alignment score with a flat per-character gap penalty."""
    # TODO: mind the borders — dp[i][0] is NOT 0
    pass


def _sol_nw_score(a, b, match=1, mismatch=-1, gap=-2):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    # Aligning a prefix against nothing costs one gap per character.
    for i in range(1, m + 1):
        dp[i][0] = i * gap
    for j in range(1, n + 1):
        dp[0][j] = j * gap
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = max(
                dp[i - 1][j - 1] + _sub(a[i - 1], b[j - 1], match, mismatch),
                dp[i - 1][j] + gap,
                dp[i][j - 1] + gap,
            )
    return dp[m][n]


# ---------------------------------------------------------------------------
# Exercise 3: Smith-Waterman score (local, linear gaps)
# ---------------------------------------------------------------------------

def sw_score(a, b, match=2, mismatch=-1, gap=-2):
    """Best local alignment score. Never negative — the empty alignment scores 0."""
    # TODO: two changes from Needleman-Wunsch, and only two
    pass


def _sol_sw_score(a, b, match=2, mismatch=-1, gap=-2):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    best = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # The 0 means "abandon this prefix and start fresh here".
            dp[i][j] = max(
                0,
                dp[i - 1][j - 1] + _sub(a[i - 1], b[j - 1], match, mismatch),
                dp[i - 1][j] + gap,
                dp[i][j - 1] + gap,
            )
            best = max(best, dp[i][j])
    return best


# ---------------------------------------------------------------------------
# Exercise 4: Gotoh global score (affine gaps, three matrices)
# ---------------------------------------------------------------------------

def gotoh_global_score(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    """Global alignment score under the affine model."""
    # TODO: build M / Ix / Iy. Ix[0][0] must be unreachable, not -gap_open.
    pass


def _sol_gotoh_tables(a, b, match, mismatch, gap_open, gap_extend, local):
    m, n = len(a), len(b)
    M = [[NEG] * (n + 1) for _ in range(m + 1)]
    Ix = [[NEG] * (n + 1) for _ in range(m + 1)]
    Iy = [[NEG] * (n + 1) for _ in range(m + 1)]
    M[0][0] = 0
    if local:
        for i in range(m + 1):
            M[i][0] = 0
        for j in range(n + 1):
            M[0][j] = 0
    else:
        # Start at 1: a gap of length zero has not been opened, so charging
        # gap_open at [0][0] would shift every score by gap_open.
        for i in range(1, m + 1):
            Ix[i][0] = -(gap_open + i * gap_extend)
        for j in range(1, n + 1):
            Iy[0][j] = -(gap_open + j * gap_extend)

    open_cost = gap_open + gap_extend
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            s = _sub(a[i - 1], b[j - 1], match, mismatch)
            prev = max(M[i - 1][j - 1], Ix[i - 1][j - 1], Iy[i - 1][j - 1])
            M[i][j] = max(0, s + prev) if local else s + prev
            Ix[i][j] = max(M[i - 1][j] - open_cost,
                           Ix[i - 1][j] - gap_extend,
                           Iy[i - 1][j] - open_cost)
            Iy[i][j] = max(M[i][j - 1] - open_cost,
                           Iy[i][j - 1] - gap_extend,
                           Ix[i][j - 1] - open_cost)
    return M, Ix, Iy


def _sol_gotoh_global_score(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    m, n = len(a), len(b)
    M, Ix, Iy = _sol_gotoh_tables(a, b, match, mismatch, gap_open, gap_extend, False)
    return max(M[m][n], Ix[m][n], Iy[m][n])


# ---------------------------------------------------------------------------
# Exercise 5: Gotoh global alignment with traceback
# ---------------------------------------------------------------------------

def gotoh_global_align(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    """Return (score, aligned_a, aligned_b) under the affine model."""
    # TODO: the traceback must remember WHICH matrix it is in
    pass


def _sol_gotoh_global_align(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    m, n = len(a), len(b)
    M, Ix, Iy = _sol_gotoh_tables(a, b, match, mismatch, gap_open, gap_extend, False)
    best = max(M[m][n], Ix[m][n], Iy[m][n])
    state = "M" if best == M[m][n] else ("Ix" if best == Ix[m][n] else "Iy")
    open_cost = gap_open + gap_extend
    out_a, out_b = [], []
    i, j = m, n
    while i > 0 or j > 0:
        if state == "M":
            out_a.append(a[i - 1])
            out_b.append(b[j - 1])
            target = M[i][j] - _sub(a[i - 1], b[j - 1], match, mismatch)
            i -= 1
            j -= 1
            state = ("M" if M[i][j] == target
                     else "Ix" if Ix[i][j] == target else "Iy")
        elif state == "Ix":
            out_a.append(a[i - 1])
            out_b.append(GAP)
            v = Ix[i][j]
            i -= 1
            state = ("Ix" if Ix[i][j] - gap_extend == v
                     else "M" if M[i][j] - open_cost == v else "Iy")
        else:
            out_a.append(GAP)
            out_b.append(b[j - 1])
            v = Iy[i][j]
            j -= 1
            state = ("Iy" if Iy[i][j] - gap_extend == v
                     else "M" if M[i][j] - open_cost == v else "Ix")
    return best, "".join(reversed(out_a)), "".join(reversed(out_b))


# ---------------------------------------------------------------------------
# Exercise 6: Gotoh local score
# ---------------------------------------------------------------------------

def gotoh_local_score(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    """Best local alignment score under the affine model. Never negative."""
    # TODO: flip the borders and floor M at 0
    pass


def _sol_gotoh_local_score(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    m, n = len(a), len(b)
    M, _, _ = _sol_gotoh_tables(a, b, match, mismatch, gap_open, gap_extend, True)
    best = 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # Only M matters: an optimal local alignment ends with a paired
            # column, since trimming a trailing gap can only raise the score.
            if M[i][j] > best:
                best = M[i][j]
    return best


# ---------------------------------------------------------------------------
# Exhaustive referee — ground truth for tiny inputs
# ---------------------------------------------------------------------------

def _all_alignments(a, b):
    if not a and not b:
        yield "", ""
        return
    if a and b:
        for ra, rb in _all_alignments(a[1:], b[1:]):
            yield a[0] + ra, b[0] + rb
    if a:
        for ra, rb in _all_alignments(a[1:], b):
            yield a[0] + ra, GAP + rb
    if b:
        for ra, rb in _all_alignments(a, b[1:]):
            yield GAP + ra, b[0] + rb


def _brute_global(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    return max(_sol_score_affine_alignment(ra, rb, match, mismatch,
                                           gap_open, gap_extend)
               for ra, rb in _all_alignments(a, b))


def _brute_local(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    best = 0
    for i in range(len(a) + 1):
        for i2 in range(i, len(a) + 1):
            for j in range(len(b) + 1):
                for j2 in range(j, len(b) + 1):
                    if not a[i:i2] and not b[j:j2]:
                        continue
                    best = max(best, _brute_global(a[i:i2], b[j:j2], match,
                                                   mismatch, gap_open, gap_extend))
    return best


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    print("Exercise 1: score_affine_alignment")
    check("perfect match", try_or_sol("score_affine_alignment", "ACGT", "ACGT"), 8)
    # 4 matches (8) minus one run of 2 gaps (3 + 2*1 = 5)
    check("one gap run of 2",
          try_or_sol("score_affine_alignment", "AC--GT", "ACTTGT"), 3)
    # Two separate runs pay the open twice: 2 - 4 - 4
    check("two runs pay open twice",
          try_or_sol("score_affine_alignment", "A-C", "AT-"), -6)
    check("single mismatch", try_or_sol("score_affine_alignment", "A", "T"), -1)

    print("\nExercise 2: nw_score")
    check("GATTACA/GCATGCU", try_or_sol("nw_score", "GATTACA", "GCATGCU"), -1)
    check("identical", try_or_sol("nw_score", "ABC", "ABC"), 3)
    # Border check: empty vs length 3 must be 3*gap, not 0.
    check("empty vs ABC", try_or_sol("nw_score", "", "ABC"), -6)
    check("AAAA vs AA", try_or_sol("nw_score", "AAAA", "AA"), -2)

    print("\nExercise 3: sw_score")
    check("shared GGCCT", try_or_sol("sw_score", "TTAGGCCTGAT", "GGCCTA"), 10)
    check("nothing in common", try_or_sol("sw_score", "AAA", "TTT"), 0)
    check("identical", try_or_sol("sw_score", "ACGT", "ACGT"), 8)
    check("empty input", try_or_sol("sw_score", "", "ACGT"), 0)

    print("\nExercise 4: gotoh_global_score")
    # Border: aligning "" to "AC" is one gap run of length 2 -> -(3 + 2*1)
    check("empty vs AC", try_or_sol("gotoh_global_score", "", "AC"), -5)
    # 8 matches (16) minus one 4-long gap run (3 + 4) = 9
    check("one 4-base deletion",
          try_or_sol("gotoh_global_score", "ACGTACGTACGT", "ACGTACGT"), 9)
    small = [("ACGT", "AGT"), ("AAG", "AGGA"), ("AC", "CA"), ("TAC", "ATC")]
    check("matches exhaustive search",
          all(try_or_sol("gotoh_global_score", a, b) == _brute_global(a, b)
              for a, b in small), True)
    # With gap_open = 0 the affine model IS the linear model.
    check("gap_open=0 degenerates to linear",
          all(try_or_sol("gotoh_global_score", a, b, 2, -1, 0, 1)
              == _sol_nw_score(a, b, 2, -1, -1)
              for a, b in [("GATTACA", "GCATGCU"), ("AAAA", "AA"), ("", "ACG")]),
          True)

    print("\nExercise 5: gotoh_global_align")
    score, ra, rb = try_or_sol("gotoh_global_align", "ACGTACGTACGT", "ACGTACGT")
    check("score agrees with exercise 4", score, 9)
    check("alignment strings are equal length", len(ra) == len(rb), True)
    check("re-scoring the traceback reproduces the score",
          _sol_score_affine_alignment(ra, rb), score)
    # Strip the gaps and you must get the originals back — a traceback that
    # drops or duplicates a character fails right here.
    check("traceback preserves both sequences",
          (ra.replace(GAP, ""), rb.replace(GAP, "")),
          ("ACGTACGTACGT", "ACGTACGT"))
    consistent = True
    for a, b in small:
        s, x, y = try_or_sol("gotoh_global_align", a, b)
        if s != _sol_score_affine_alignment(x, y) or x.replace(GAP, "") != a \
                or y.replace(GAP, "") != b:
            consistent = False
    check("consistent on every small pair", consistent, True)

    print("\nExercise 6: gotoh_local_score")
    check("nothing in common", try_or_sol("gotoh_local_score", "AAA", "TTT"), 0)
    check("never negative", try_or_sol("gotoh_local_score", "A", "T") >= 0, True)
    check("conserved region",
          try_or_sol("gotoh_local_score", "TTTTTACGTACGTAAAAA",
                     "GGGGACGTTTACGTCCCC", 3, -2, 4, 1), 22)
    check("matches exhaustive local search",
          all(try_or_sol("gotoh_local_score", a, b) == _brute_local(a, b)
              for a, b in small), True)
    # Local can never score below global on the same input: the global
    # alignment is one of the candidates local is allowed to trim down to.
    check("local >= global",
          all(try_or_sol("gotoh_local_score", a, b)
              >= _sol_gotoh_global_score(a, b) for a, b in small), True)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
