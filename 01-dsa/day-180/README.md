# Day 180: Capstone Part B — Search Refinement (Part 2/2)

## Continuation of Day 179

This day extends the search engine from
`day-179/search_engine.py` with the three things that separate a toy
search from a useful one:

1. **Fuzzy matching** — handle typos via edit distance.
2. **Query expansion** — synonyms, stemming reach, plurals.
3. **Better ranking** — BM25 instead of plain TF-IDF.

Same engine, same documents, same index. New retrieval and scoring
layer on top.

```bash
python3 day-180/search_refinement.py
```

## Why Refinement Matters

Plain TF-IDF on an exact-match inverted index has three blind spots:

- **Typos kill recall.** "pyhton" returns zero documents.
- **Synonymy kills recall.** "vehicle" doesn't match "car".
- **Long documents win unfairly.** TF accumulates linearly; a 10,000-
  word page beats a focused 300-word page on most queries.

All three are real failure modes that broke early search engines.
Google's PageRank story is famous, but the technical leap that made
search engines *useful* (mid-90s) was query expansion + BM25 + better
tokenization.

## Fuzzy Matching via Edit Distance

**Levenshtein distance** between strings `s` and `t`:

```
ed(s, t) = min number of insertions, deletions, substitutions
           that transform s into t
```

Computed in `O(|s| · |t|)` via dynamic programming.

For each query term `q`, look up all index terms within edit distance
≤ `k` (we use `k = 2` for terms of length ≥ 5, `k = 1` otherwise).
This is the **fuzzy expansion set**.

**Problem:** scanning every index term is O(|vocab|). For a real index
that's 10M+ terms. Solutions:

- **Trigram index.** Index each term by its character trigrams. To
  match query `python`, look up postings for trigrams `pyt`, `yth`,
  `tho`, `hon`. Candidates that share enough trigrams are checked
  with full edit distance.
- **BK-tree.** Tree where each edge is labeled with edit distance.
  Lookup of all terms within `k` of `q` is `O(log |vocab|)` average.
- **Levenshtein automaton.** For fixed `k`, build a DFA that accepts
  all strings within `k` edits of `q`; intersect with the term
  dictionary trie.

We implement **trigram filtering** + full edit-distance verification.
Production engines use Levenshtein automata (Lucene since 2011).

## BM25

```
BM25(t, d) = idf(t) * (tf(t, d) * (k1 + 1))
                       --------------------------------
                       tf(t, d) + k1 * (1 - b + b * |d|/avgdl)
```

Where:
- `k1` ∈ [1.2, 2.0] controls term frequency saturation. Higher k1 →
  more weight to repeated occurrences.
- `b` ∈ [0, 1] controls length normalization. b = 1 → fully
  normalized by length; b = 0 → no normalization.
- `|d|` is the doc length; `avgdl` is the average doc length.

Defaults `k1 = 1.5, b = 0.75` (Lucene's choice).

**Why BM25 beats TF-IDF:**

- TF saturates. A term appearing 100 times isn't 100× as relevant as
  appearing once — BM25 caps the gain.
- Length is normalized. Long docs don't dominate by sheer wordcount.
- Empirically, BM25 wins on every major IR benchmark (TREC, MS MARCO,
  BEIR).

## Query Expansion

For each token in the query, also include:

1. **Stemmed form.** Already done at index time, but if the user
   types unstemmed we need to stem.
2. **Synonyms.** A hardcoded synonym dict for the demo. Production
   uses WordNet or learned embeddings.
3. **Fuzzy matches.** Index terms within edit distance ≤ k.

Each expanded term enters the query at a downweighted score
(`fuzzy_weight = 0.5`, `synonym_weight = 0.7`) so exact matches still
dominate when they exist.

## The Three Knobs and Their Tradeoffs

| Knob | Recall ↑ | Precision ↓ | Cost ↑ |
|---|---|---|---|
| Fuzzy threshold k | Yes | Some | Big — every term checked |
| Synonym list | Yes | Often | Tiny lookup |
| BM25 vs TF-IDF | Same | More accurate | Same |

Refinement is mostly *recall* work — making sure no relevant doc is
missed. Precision is then restored via ranking.

## Failure Modes

1. **Fuzzy too aggressive.** `k=2` matches `dog` to `bag`, `dot`, `hog`,
   `cot`, `dot`... at some point you're returning everything. Production
   systems gate fuzzy on term frequency — common words don't get fuzzy
   expansion.
2. **Synonyms drift.** A synonym dict trained on news data gives wrong
   answers on code search. Domain-specific synonym lists are critical.
3. **BM25 has tuned constants.** Lucene defaults work for general
   English. Code search, log search, and multilingual search each want
   different k1/b.
4. **Trigram filter false positives.** Two unrelated terms can share
   trigrams; we still need a full edit-distance check. Cost = filter
   cost + verification cost. Tuning the trigram threshold is its own
   problem.
5. **Cold start.** Edit-distance computation is O(|q| · |t|). For 10M
   terms × 10 chars × 10 chars, that's 10^9 operations per query — way
   too slow without filtering.

## Checkpoint Questions

1. Compute edit distance between `kitten` and `sitting`. (Classic
   example. Answer is in the demo.)
2. BM25's `b` parameter controls length normalization. What does
   `b = 0` mean physically? What does `b = 1` mean?
3. Why does trigram filtering help fuzzy search? Estimate the
   speedup vs scanning every term.
4. A user types `pyhton`. Walk through the fuzzy expansion: which
   index terms match at edit distance ≤ 2?
5. Why is recall typically prioritized over precision in the initial
   retrieval stage? What restores precision?
6. Hybrid search (BM25 + neural embeddings) is now standard. What
   does BM25 contribute that embeddings struggle with?

## The Whole Capstone B in One Sentence

A search engine is **an inverted index + a smart query expander + a
saturated ranker**. The data structure is the index; the algorithms
are tokenization, edit distance, and BM25. Everything else (relevance
feedback, neural re-ranking, learning to rank) is layered on top.
