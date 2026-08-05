"""
Day 126 Mini-Project: Sequence Alignment

Four aligners, two scoring models:

                     linear gaps            affine gaps (Gotoh)
    global           needleman_wunsch       gotoh_global
    local            smith_waterman         gotoh_local

Linear gaps charge `gap` per gap character. Affine gaps charge
`gap_open + L * gap_extend` for a run of length L, which is what real
biology wants: one splice event that removes 30 bases is a single accident,
not 30 independent ones.

`gap_open` and `gap_extend` are given as POSITIVE penalties; the code
subtracts them. `match`/`mismatch` are signed scores (match positive).

Standard library only.
"""

NEG = float("-inf")  # "this state is unreachable", not "a very bad score"

GAP = "-"


def _sub(x, y, match, mismatch):
    return match if x == y else mismatch


# ---------------------------------------------------------------------------
# Scorers — independent of the DP, so they can referee it
# ---------------------------------------------------------------------------

def score_linear_alignment(aligned_a, aligned_b, match=1, mismatch=-1, gap=-2):
    """Re-score a finished alignment under the linear-gap model."""
    if len(aligned_a) != len(aligned_b):
        raise ValueError("aligned strings must have equal length")
    total = 0
    for ca, cb in zip(aligned_a, aligned_b):
        if ca == GAP and cb == GAP:
            raise ValueError("a column of two gaps is not an alignment column")
        if ca == GAP or cb == GAP:
            total += gap
        else:
            total += _sub(ca, cb, match, mismatch)
    return total


def score_affine_alignment(aligned_a, aligned_b, match=2, mismatch=-1,
                           gap_open=3, gap_extend=1):
    """
    Re-score a finished alignment under the affine model.

    This exists so the tests can check the DP against something that never
    saw the DP. A traceback that disagrees with an independent re-score is a
    traceback bug, and traceback bugs are the ones that hide.
    """
    if len(aligned_a) != len(aligned_b):
        raise ValueError("aligned strings must have equal length")
    total = 0
    run_in_a = False   # currently extending a gap run inside sequence a
    run_in_b = False
    for ca, cb in zip(aligned_a, aligned_b):
        if ca == GAP and cb == GAP:
            raise ValueError("a column of two gaps is not an alignment column")
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
# 1. Needleman-Wunsch — global, linear gaps
# ---------------------------------------------------------------------------

def needleman_wunsch(a, b, match=1, mismatch=-1, gap=-2):
    """
    Global alignment: every character of both sequences appears.
    Returns (score, aligned_a, aligned_b).

    Initialization is the whole story: dp[i][0] = i*gap says "aligning a
    prefix of a against nothing costs one gap per character". Leaving those
    cells at 0 is the classic bug — it silently makes leading gaps free,
    which turns a global aligner into a semi-global one.
    """
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        dp[i][0] = i * gap
    for j in range(1, n + 1):
        dp[0][j] = j * gap

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = max(
                dp[i - 1][j - 1] + _sub(a[i - 1], b[j - 1], match, mismatch),
                dp[i - 1][j] + gap,   # a[i-1] against a gap
                dp[i][j - 1] + gap,   # b[j-1] against a gap
            )

    out_a, out_b = [], []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + _sub(
                a[i - 1], b[j - 1], match, mismatch):
            out_a.append(a[i - 1])
            out_b.append(b[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + gap:
            out_a.append(a[i - 1])
            out_b.append(GAP)
            i -= 1
        else:
            out_a.append(GAP)
            out_b.append(b[j - 1])
            j -= 1
    return dp[m][n], "".join(reversed(out_a)), "".join(reversed(out_b))


# ---------------------------------------------------------------------------
# 2. Smith-Waterman — local, linear gaps
# ---------------------------------------------------------------------------

def smith_waterman(a, b, match=2, mismatch=-1, gap=-2):
    """
    Local alignment: the best-scoring pair of substrings.
    Returns (score, aligned_a, aligned_b, start_a, start_b).

    Two changes from Needleman-Wunsch and that is all:
      1. the borders are 0 (starting anywhere is free)
      2. every cell is floored at 0 (a prefix that has gone negative is
         abandoned rather than carried forward)
    """
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    best, bi, bj = 0, 0, 0

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = max(
                0,
                dp[i - 1][j - 1] + _sub(a[i - 1], b[j - 1], match, mismatch),
                dp[i - 1][j] + gap,
                dp[i][j - 1] + gap,
            )
            if dp[i][j] > best:
                best, bi, bj = dp[i][j], i, j

    out_a, out_b = [], []
    i, j = bi, bj
    while i > 0 and j > 0 and dp[i][j] > 0:
        if dp[i][j] == dp[i - 1][j - 1] + _sub(a[i - 1], b[j - 1], match, mismatch):
            out_a.append(a[i - 1])
            out_b.append(b[j - 1])
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i - 1][j] + gap:
            out_a.append(a[i - 1])
            out_b.append(GAP)
            i -= 1
        else:
            out_a.append(GAP)
            out_b.append(b[j - 1])
            j -= 1
    return best, "".join(reversed(out_a)), "".join(reversed(out_b)), i, j


# ---------------------------------------------------------------------------
# 3. Gotoh — three matrices, affine gaps
# ---------------------------------------------------------------------------

def _gotoh_tables(a, b, match, mismatch, gap_open, gap_extend, local):
    """
    Build M / Ix / Iy.

      M[i][j]  best score for a[:i] vs b[:j] whose LAST column pairs
               a[i-1] with b[j-1]
      Ix[i][j] ... whose last column is a[i-1] against a gap
      Iy[i][j] ... whose last column is a gap against b[j-1]

    Splitting by "what the last column looks like" is the entire trick: only
    then does the DP know whether a gap here CONTINUES a run (pay extend) or
    STARTS one (pay open + extend).

    Initialization off-by-one, the classic bug on this page:
      Ix[i][0] = -(gap_open + i*gap_extend)   for i >= 1
      Ix[0][0] = NEG  -- NOT -gap_open
    A zero-length gap has not been opened. Writing the border with a loop
    that starts at i = 0 charges an open for a gap that does not exist, and
    every global affine score comes out gap_open too low.
    """
    m, n = len(a), len(b)
    M = [[NEG] * (n + 1) for _ in range(m + 1)]
    Ix = [[NEG] * (n + 1) for _ in range(m + 1)]
    Iy = [[NEG] * (n + 1) for _ in range(m + 1)]

    M[0][0] = 0
    if local:
        # Starting anywhere is free, but a local alignment never begins with
        # a gap, so Ix/Iy borders stay unreachable.
        for i in range(m + 1):
            M[i][0] = 0
        for j in range(n + 1):
            M[0][j] = 0
    else:
        for i in range(1, m + 1):
            Ix[i][0] = -(gap_open + i * gap_extend)
        for j in range(1, n + 1):
            Iy[0][j] = -(gap_open + j * gap_extend)

    open_cost = gap_open + gap_extend
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            s = _sub(a[i - 1], b[j - 1], match, mismatch)
            best_prev = max(M[i - 1][j - 1], Ix[i - 1][j - 1], Iy[i - 1][j - 1])
            M[i][j] = max(0, s + best_prev) if local else s + best_prev
            Ix[i][j] = max(
                M[i - 1][j] - open_cost,
                Ix[i - 1][j] - gap_extend,      # continuing the run: extend only
                Iy[i - 1][j] - open_cost,
            )
            Iy[i][j] = max(
                M[i][j - 1] - open_cost,
                Iy[i][j - 1] - gap_extend,
                Ix[i][j - 1] - open_cost,
            )
    return M, Ix, Iy


def _gotoh_traceback(a, b, M, Ix, Iy, i, j, state,
                     match, mismatch, gap_open, gap_extend, local):
    """
    Walk backwards, remembering WHICH matrix we are in. The state is what
    tells us whether the previous column was a gap of the same kind (extend)
    or something else (open).
    """
    open_cost = gap_open + gap_extend
    out_a, out_b = [], []

    while True:
        if local and state == "M" and (i == 0 or j == 0 or M[i][j] <= 0):
            break
        if not local and i == 0 and j == 0:
            break

        if state == "M":
            if i == 0 or j == 0:
                break
            out_a.append(a[i - 1])
            out_b.append(b[j - 1])
            target = M[i][j] - _sub(a[i - 1], b[j - 1], match, mismatch)
            i -= 1
            j -= 1
            if M[i][j] == target:
                state = "M"
            elif Ix[i][j] == target:
                state = "Ix"
            elif Iy[i][j] == target:
                state = "Iy"
            else:
                break  # only reachable via the local 0-floor: fresh start
        elif state == "Ix":
            if i == 0:
                break
            out_a.append(a[i - 1])
            out_b.append(GAP)
            v = Ix[i][j]
            i -= 1
            if Ix[i][j] - gap_extend == v:
                state = "Ix"
            elif M[i][j] - open_cost == v:
                state = "M"
            elif Iy[i][j] - open_cost == v:
                state = "Iy"
            else:
                break
        else:  # Iy
            if j == 0:
                break
            out_a.append(GAP)
            out_b.append(b[j - 1])
            v = Iy[i][j]
            j -= 1
            if Iy[i][j] - gap_extend == v:
                state = "Iy"
            elif M[i][j] - open_cost == v:
                state = "M"
            elif Ix[i][j] - open_cost == v:
                state = "Ix"
            else:
                break

    return "".join(reversed(out_a)), "".join(reversed(out_b)), i, j


def gotoh_global(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    """
    Global alignment with affine gaps. Returns (score, aligned_a, aligned_b).
    A gap run of length L costs gap_open + L * gap_extend.
    """
    m, n = len(a), len(b)
    M, Ix, Iy = _gotoh_tables(a, b, match, mismatch, gap_open, gap_extend, local=False)
    best = max(M[m][n], Ix[m][n], Iy[m][n])
    if best == M[m][n]:
        state = "M"
    elif best == Ix[m][n]:
        state = "Ix"
    else:
        state = "Iy"
    out_a, out_b, _, _ = _gotoh_traceback(
        a, b, M, Ix, Iy, m, n, state, match, mismatch, gap_open, gap_extend, False)
    return best, out_a, out_b


def gotoh_local(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    """
    Local alignment with affine gaps (Smith-Waterman-Gotoh).
    Returns (score, aligned_a, aligned_b, start_a, start_b).

    The best local alignment always begins and ends with a paired column —
    trimming a leading or trailing gap can only raise the score — so it is
    enough to scan M for the maximum.
    """
    m, n = len(a), len(b)
    M, Ix, Iy = _gotoh_tables(a, b, match, mismatch, gap_open, gap_extend, local=True)
    best, bi, bj = 0, 0, 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if M[i][j] > best:
                best, bi, bj = M[i][j], i, j
    if best <= 0:
        return 0, "", "", 0, 0
    out_a, out_b, i, j = _gotoh_traceback(
        a, b, M, Ix, Iy, bi, bj, "M", match, mismatch, gap_open, gap_extend, True)
    return best, out_a, out_b, i, j


# ---------------------------------------------------------------------------
# 4. Brute force referee (tiny inputs only)
# ---------------------------------------------------------------------------

def all_alignments(a, b):
    """
    Every way to align a and b. The count is the Delannoy number D(m,n) —
    321 for 4x4, and it explodes fast. Tests only.
    """
    if not a and not b:
        yield "", ""
        return
    if a and b:
        for ra, rb in all_alignments(a[1:], b[1:]):
            yield a[0] + ra, b[0] + rb
    if a:
        for ra, rb in all_alignments(a[1:], b):
            yield a[0] + ra, GAP + rb
    if b:
        for ra, rb in all_alignments(a, b[1:]):
            yield GAP + ra, b[0] + rb


def brute_global_affine(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    """Max affine score over every alignment. Ground truth."""
    return max(
        score_affine_alignment(ra, rb, match, mismatch, gap_open, gap_extend)
        for ra, rb in all_alignments(a, b)
    )


def brute_local_affine(a, b, match=2, mismatch=-1, gap_open=3, gap_extend=1):
    """Max affine score over every substring pair, floored at 0."""
    best = 0
    for i in range(len(a) + 1):
        for i2 in range(i, len(a) + 1):
            for j in range(len(b) + 1):
                for j2 in range(j, len(b) + 1):
                    sub_a, sub_b = a[i:i2], b[j:j2]
                    if not sub_a and not sub_b:
                        continue
                    v = brute_global_affine(sub_a, sub_b, match, mismatch,
                                            gap_open, gap_extend)
                    if v > best:
                        best = v
    return best


# ---------------------------------------------------------------------------
# Pretty printing
# ---------------------------------------------------------------------------

def render(aligned_a, aligned_b, width=60):
    """Three-line view: sequence, match ruler, sequence."""
    lines = []
    for start in range(0, len(aligned_a), width):
        top = aligned_a[start:start + width]
        bot = aligned_b[start:start + width]
        mid = "".join(
            "|" if x == y and x != GAP else (" " if GAP in (x, y) else ".")
            for x, y in zip(top, bot)
        )
        lines.extend([top, mid, bot])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_linear():
    print("=" * 66)
    print("DEMO 1: Linear gaps — Needleman-Wunsch and Smith-Waterman")
    print("=" * 66)
    a, b = "GATTACA", "GCATGCU"
    score, ra, rb = needleman_wunsch(a, b)
    print(f"\n  global '{a}' vs '{b}'  score={score}")
    print(render(ra, rb))
    assert score == score_linear_alignment(ra, rb)

    a, b = "TTAGGCCTGAT", "GGCCTA"
    score, ra, rb, si, sj = smith_waterman(a, b)
    print(f"\n  local '{a}' vs '{b}'  score={score} starts a[{si}] b[{sj}]")
    print(render(ra, rb))


def demo_affine_vs_linear():
    print("\n" + "=" * 66)
    print("DEMO 2: Why affine gaps change the answer")
    print("=" * 66)
    a = "ACGTACGTACGT"
    b = "ACGTACGT"          # b is a with a 4-base chunk removed
    print(f"\n  a = {a}\n  b = {b}   (one deletion of length 4)")

    lin_score, lra, lrb = needleman_wunsch(a, b, match=2, mismatch=-1, gap=-4)
    print(f"\n  linear gap=-4  score={lin_score}")
    print(render(lra, lrb))

    aff_score, ara, arb = gotoh_global(a, b, match=2, mismatch=-1,
                                       gap_open=3, gap_extend=1)
    print(f"\n  affine open=3 extend=1  score={aff_score}")
    print(render(ara, arb))
    print("\n  Affine charges 3 + 4*1 = 7 for the whole 4-base deletion.")
    print("  Linear at -4 per base charges 16 for the same biological event.")
    assert aff_score == score_affine_alignment(ara, arb, 2, -1, 3, 1)


def demo_gotoh_local():
    print("\n" + "=" * 66)
    print("DEMO 3: Gotoh local — finding a conserved region")
    print("=" * 66)
    a = "TTTTTACGTACGTAAAAA"
    b = "GGGGACGTTTACGTCCCC"
    score, ra, rb, si, sj = gotoh_local(a, b, match=3, mismatch=-2,
                                        gap_open=4, gap_extend=1)
    print(f"\n  a = {a}\n  b = {b}")
    print(f"  local affine score={score}, starts a[{si}] b[{sj}]")
    print(render(ra, rb))
    assert score == score_affine_alignment(ra, rb, 3, -2, 4, 1)


def demo_referee():
    print("\n" + "=" * 66)
    print("DEMO 4: Checked against exhaustive enumeration")
    print("=" * 66)
    pairs = [("ACGT", "AGT"), ("AAG", "AGGA"), ("", "AC"), ("GC", "")]
    for a, b in pairs:
        dp, ra, rb = gotoh_global(a, b)
        brute = brute_global_affine(a, b)
        n_alignments = sum(1 for _ in all_alignments(a, b))
        print(f"  '{a}' vs '{b}': gotoh={dp} brute={brute} "
              f"over {n_alignments} alignments")
        assert dp == brute, f"{dp} != {brute}"
        assert dp == score_affine_alignment(ra, rb), "traceback disagrees with DP"


if __name__ == "__main__":
    demo_linear()
    demo_affine_vs_linear()
    demo_gotoh_local()
    demo_referee()
    print("\nAll day-126 demos complete.")
