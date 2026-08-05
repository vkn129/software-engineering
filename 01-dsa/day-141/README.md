# Day 141: Levenshtein Automaton

## Why It Matters

Fuzzy search at scale needs O(n) per candidate, not O(n*m). The Levenshtein
automaton is a DFA (or NFA) that accepts exactly those strings within edit
distance k of a fixed pattern. Once built, every candidate streams through in
linear time — independent of pattern length.

- **Spell checkers**: scan a dictionary of 500k words for "did you mean X".
- **DNA matching**: approximate k-mer lookups in genomes.
- **Search-as-you-type**: Lucene/Elasticsearch use Levenshtein automata for the
  `~` fuzzy operator (Schulz & Mihov 2002).
- **OCR post-processing**: snap mangled tokens to a known vocabulary.

The naive DP is O(n*m); the automaton trades preprocessing for amortized O(n)
queries against the same pattern.

## The State Idea

For pattern P of length m and max distance k, a state is the column-vector of
DP values D[0..m]. But most values are >= k+1 (dead) — only entries within
k of the diagonal are "alive". So a state is a window of (offset, distance)
pairs around the active region.

We use a simpler encoding here: **state = full DP column, capped at k+1**.
This is correct but uses up to (k+2)^(m+1) states in the worst case. Real
implementations (Schulz-Mihov) compact to O(m * k) states by exploiting the
monotone structure.

## Transition Rule

From DP column `prev`, on input character `c`, the next column `nxt` is:

```
nxt[0] = prev[0] + 1                            # delete from candidate
nxt[i] = min(
    nxt[i-1]   + 1,                             # insert into candidate
    prev[i]    + 1,                             # delete from pattern
    prev[i-1]  + (0 if P[i-1] == c else 1),     # match or substitute
)
```

Cap every entry at k+1. Accept when `nxt[m] <= k`.

## NFA View

The classical construction is an NFA with states `(i, e)` where i is position
in pattern and e is edits used. Transitions:

- `(i, e) --c--> (i+1, e)`           if c == P[i]      (match)
- `(i, e) --*--> (i+1, e+1)`         substitute
- `(i, e) --eps-> (i+1, e+1)`        delete pattern char
- `(i, e) --*--> (i, e+1)`           insert candidate char

Subset construction converts this to a DFA. We implement the equivalent DP
column directly — simpler and avoids epsilon closures.

## Complexity

| Phase           | Time              | Space           |
|-----------------|-------------------|-----------------|
| Build DFA       | O(m * k * S)      | O(S * \|Σ\|)    |
| Query           | O(n)              | O(1)            |
| Naive DP (no automaton) | O(n * m)  | O(m)            |

S = number of distinct alive columns (small in practice, exponential worst case).

## Failure Modes

- **Unicode**: edit distance on grapheme clusters != codepoints != bytes. "é"
  may be 1 or 2 codepoints. Normalize first.
- **Transpositions**: standard Levenshtein costs 2 for swap. Use
  Damerau-Levenshtein if "teh" -> "the" should cost 1.
- **State explosion**: for k > 3 on long patterns, the cached-column DFA blows
  up. Use the Schulz-Mihov windowed representation.

## Checkpoint Questions

1. Why is the DFA O(n) per query but the DP O(n*m)?
2. What's the state in the NFA? Why does subset construction terminate?
3. Why cap DP entries at k+1?
4. When would you prefer trie + DP over a Levenshtein automaton?
5. How does Schulz-Mihov compact states to O(m*k)?
6. Why does Damerau-Levenshtein need a 2-column lookback instead of 1?
