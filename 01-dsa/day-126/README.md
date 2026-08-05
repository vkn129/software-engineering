# Day 126: Mini-Project — Sequence Alignment

## What We're Building

A working aligner, four ways, and a referee that proves it right:

- **Needleman-Wunsch** — global alignment, linear gaps. Every character of
  both sequences ends up in the output.
- **Smith-Waterman** — local alignment, linear gaps. Finds the best-scoring
  pair of *substrings* and ignores the rest.
- **Gotoh** — the same two problems with **affine gap penalties**, using the
  three-matrix M/Ix/Iy formulation. This is the new content.
- **Exhaustive referee** — enumerate every alignment of two tiny strings,
  score them all, and check the DP found the maximum.

Day 117 owns plain edit distance (every edit costs 1). Here the model gets
richer in exactly one way: **a run of gaps costs less per character than the
first character of the run**.

## Why Affine Gaps Exist

Under a linear model, deleting 30 consecutive bases costs 30 × gap. But in
biology one splicing event removes a whole exon in a single accident. Charging
it 30 times over-penalises the true history and pushes the aligner into
scattering 30 separate one-base gaps instead — visually wrong, biologically
wrong.

Affine says: a gap run of length `L` costs `gap_open + L × gap_extend`.
Open is expensive, extending is cheap.

```
             linear (-4/base)          affine (open 3, extend 1)
gap of 1        -4                        -4
gap of 4       -16                        -7
gap of 30     -120                       -33
```

Everything downstream inherits this: BLAST, ClustalW, MAFFT, `diff`, and
`git merge` all use gap models shaped like this. `diff` is literally a global
alignment over lines with an affine-flavoured cost.

## Architecture

```
  score_linear_alignment  ─┐
  score_affine_alignment  ─┴─> re-score a finished alignment (referee)

  needleman_wunsch ──> 1 matrix ──> traceback ──> (score, aligned_a, aligned_b)
  smith_waterman   ──> 1 matrix + 0-floor ──> traceback from argmax

  _gotoh_tables ──> M, Ix, Iy ──> _gotoh_traceback (carries a STATE)
        │                              │
        ├─ gotoh_global (local=False)  ├─ global: start at (m, n)
        └─ gotoh_local  (local=True)   └─ local:  start at argmax of M

  all_alignments ──> brute_global_affine / brute_local_affine  (ground truth)
```

## The Three Matrices

Splitting the DP by **what the last column looks like** is the whole idea.
One matrix cannot answer "is this gap new?"; three can.

| Matrix | Last column of the alignment |
|---|---|
| `M[i][j]` | `a[i-1]` paired with `b[j-1]` |
| `Ix[i][j]` | `a[i-1]` against a gap (a deletion in `b`) |
| `Iy[i][j]` | a gap against `b[j-1]` (an insertion into `b`) |

```
M[i][j]  = s(a[i-1], b[j-1]) + max( M[i-1][j-1], Ix[i-1][j-1], Iy[i-1][j-1] )

Ix[i][j] = max( M[i-1][j]  - (open + extend),     # start a new gap run
                Ix[i-1][j] - extend,              # continue the run
                Iy[i-1][j] - (open + extend) )

Iy[i][j] = max( M[i][j-1]  - (open + extend),
                Iy[i][j-1] - extend,
                Ix[i][j-1] - (open + extend) )
```

Final global score = `max(M[m][n], Ix[m][n], Iy[m][n])`.

The `Ix → Iy` and `Iy → Ix` transitions are included. Such an alignment is
legal (a gap in one sequence directly followed by a gap in the other) and
never optimal under sane scores, but including it keeps the DP's answer equal
to "the maximum over all legal alignments", which is exactly what the
exhaustive referee computes. Gotoh's 1982 paper omits them; texts differ.
Ours agrees with the referee, which is the standard we can actually check.

## The Initialization Off-By-One

The bug this project exists to make you feel:

```
Ix[0][0] = NEG                             # NOT -gap_open
Ix[i][0] = -(gap_open + i * gap_extend)    # for i >= 1
Iy[0][j] = -(gap_open + j * gap_extend)    # for j >= 1
M[0][0]  = 0,  M[i][0] = M[0][j] = NEG     # a global alignment of a prefix
                                           # against nothing has no paired column
```

Write the `Ix` border with a loop that starts at `i = 0` and you have charged
`gap_open` for a gap of length **zero**. Nothing crashes. Every global affine
score comes out `gap_open` too low, uniformly — so ranking two candidates
still works, all your relative tests still pass, and the absolute numbers are
silently wrong. That is the worst kind of bug: consistent.

`NEG` here is `float("-inf")`, meaning *unreachable*, not *very bad*. Using a
large negative integer instead invites the DP to "escape" through it when
penalties are large.

For **local** alignment the borders flip: `M[i][0] = M[0][j] = 0` (starting
anywhere is free) and `Ix`/`Iy` borders stay `NEG`, because a local alignment
never begins with a gap — trimming that gap would raise the score.

## Complexity

| Aligner | Time | Space | Space with band/linear tricks |
|---|---|---|---|
| Needleman-Wunsch | O(mn) | O(mn) | O(min(m,n)) score-only, O(m+n) with Hirschberg |
| Smith-Waterman | O(mn) | O(mn) | same |
| Gotoh global | O(mn) | O(mn) ×3 | O(min(m,n)) ×3 score-only |
| Gotoh local | O(mn) | O(mn) ×3 | same |
| Exhaustive referee | O(D(m,n)) | O(m+n) | — |

`D(m,n)` is the Delannoy number — 321 alignments for two 4-character strings,
and it explodes from there. Tests only.

Affine costs 3× the memory of linear and roughly 3× the arithmetic, for the
same asymptotic O(mn). That constant is why BLAST does seed-and-extend
heuristics instead of a full Smith-Waterman against a whole genome.

## What Could Go Wrong (and the Test for Each)

1. **Traceback disagrees with the DP score.** Re-score the returned alignment
   strings with `score_affine_alignment` and compare. This catches every
   state-transition mistake in the traceback, which the score alone cannot.
2. **DP is not actually the maximum.** Compare against `brute_global_affine`
   on 3–4 character strings. A DP that is internally consistent but wrong
   fails only here.
3. **Border off-by-one.** Align a string against the empty string. The score
   must be exactly `-(gap_open + len × gap_extend)`.
4. **Local alignment returns a negative score.** It must floor at 0 — the
   empty alignment is always available.
5. **Local starts or ends with a gap.** Trimming would improve the score, so
   the returned alignment must not.
6. **Affine and linear disagree when they shouldn't.** With
   `gap_open = 0`, affine degenerates to linear with `gap = -gap_extend`.
   The two aligners must produce equal scores.

## Checkpoint Questions

1. Why does the affine model need three matrices instead of one plus a "was
   the last move a gap?" flag?
2. `Ix[0][0] = -gap_open` instead of `NEG`. Which alignments become mis-scored,
   and by how much?
3. Set `gap_open = 0`. Show that Gotoh reduces to Needleman-Wunsch with
   `gap = -gap_extend`.
4. Why is it enough for local alignment to scan only `M` for the maximum,
   rather than all three matrices?
5. Smith-Waterman floors every cell at 0. What is the equivalent statement
   about the alignment being built?
6. You must align two 100,000-character sequences. `O(mn)` space is 10^10
   cells. What are your two options, and what does each cost you?
7. `diff` aligns lines, not characters. What changes in the scoring model,
   and why does that make the substitution score almost irrelevant?
