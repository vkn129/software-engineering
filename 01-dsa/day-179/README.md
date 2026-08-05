# Day 179: Capstone Part B — Search Engine (Part 1/2)

## What This Is

A working **text search engine** with:

- A crawler (file-based — walks a directory tree).
- A tokenizer (lowercasing, punctuation stripping, stopword removal,
  simple stemming).
- An **inverted index** mapping term → posting list.
- **TF-IDF** ranked retrieval.
- Boolean queries (AND/OR/NOT).
- Phrase queries (positional postings).

Stdlib only. Run it:

```bash
python3 day-179/search_engine.py
```

It indexes ~12 in-memory documents (fake Wikipedia-style passages),
then runs queries and prints ranked results.

Day 180 extends the same engine with fuzzy matching (edit distance),
query expansion (stemming + synonyms), and a more sophisticated scoring
function (BM25 + field weights).

## Why Build This

Every Google query, every `grep`, every Elasticsearch cluster, every
LLM RAG pipeline — all of them are inverted-index searches at heart.
Building one from scratch reveals:

- **Why hashing is foundational** — the index is a hash from term to
  posting list.
- **Why merge-sorted lists matter** — Boolean AND of two terms is a
  sorted-list intersection.
- **Why TF-IDF works** — and where it breaks (long docs, rare terms).
- **Why fuzzy search is expensive** — and how production engines hack
  around it (trigrams, BK-trees).

This is the second capstone — pulls from Phase 4 (hashing), Phase 7
(merge), Phase 9 (DP for edit distance, in day 180).

## The Pipeline

```
documents -> tokenizer -> inverted index
                                |
                                v
                        +---------------+
                        | Query parser  |
                        +---------------+
                                |
                                v
                        +---------------+
                        | Score & rank  |
                        +---------------+
                                |
                                v
                        Ranked results
```

## The Inverted Index

```
   "python":  [(doc1, [pos3, pos17]),
               (doc4, [pos2]),
               (doc7, [pos5, pos9, pos44])]

   "lambda":  [(doc1, [pos5]),
               (doc7, [pos10])]
```

For each term, a list of `(doc_id, positions)` — the **posting list**.

- **Boolean AND**: intersect posting lists.
- **Boolean OR**: union posting lists.
- **Phrase "python lambda"**: intersect, then for each shared doc check
  that some position of "lambda" is exactly one after some position of
  "python".
- **TF-IDF score**: combine term frequency in this doc with inverse
  document frequency across the corpus.

## Why Posting Lists Are Sorted

We store `doc_id`s in sorted order. This gives:

- **Linear intersection.** Two sorted lists merge in `O(|A| + |B|)`.
- **Skip pointers** (not implemented here) further reduce to
  `O(min(|A|, |B|))` in many cases.
- **Streaming** — postings can be processed in chunks rather than
  loaded into memory.

Real systems (Lucene) store these on disk in compressed blocks. We use
plain Python lists for clarity.

## TF-IDF

```
tf(t, d)  = count of term t in doc d
df(t)     = number of docs containing t
idf(t)    = log(N / df(t))         where N = corpus size
tfidf(t,d) = tf(t,d) * idf(t)

score(q, d) = sum over t in q of tfidf(t, d)
```

Intuition:
- A term appearing often in `d` → relevant.
- A term appearing in most docs (`the`, `is`) → useless.
- Multiplying both punishes commonness, rewards specificity.

Production engines use **BM25** (day 180) — a saturated version that
prevents very long documents from dominating.

## Tokenization Choices

Even a "simple" tokenizer makes load-bearing decisions:

1. **Lowercasing**: `Python` and `python` match.
2. **Punctuation stripping**: `tree's` → `trees`.
3. **Stopword removal**: drop `the`, `is`, `of`, `and` — they're
   noise. (But "to be or not to be" becomes empty.)
4. **Stemming**: `running`, `ran`, `runs` → `run`. We use a tiny
   suffix-stripping stemmer; production uses Porter or Snowball.

Every choice has a recall/precision tradeoff.

## Failure Modes

1. **Index size explodes.** A naive inverted index over the web would
   be petabytes. Real engines compress (delta encoding, variable-byte,
   PForDelta).
2. **Updates are painful.** Adding one document means updating
   thousands of posting lists. Lucene solves this with immutable
   segments + periodic merging.
3. **Stopword removal kills phrase queries.** "to be or not to be" → ""
   after stopword removal. Production engines keep stopwords in the
   index but down-weight them.
4. **TF-IDF favors long documents.** A 10,000-word doc trivially has
   higher TF for any term. BM25 fixes this with length normalization.
5. **No semantic understanding.** "car" and "automobile" don't match.
   Modern systems combine inverted indexes with embedding-based
   retrieval (hybrid search).

## Checkpoint Questions

1. Why are posting lists kept sorted by doc_id? What operation
   becomes asymptotically faster?
2. Trace the intersection of `[1, 3, 5, 9]` and `[2, 3, 7, 9]` step by
   step. How many comparisons?
3. `idf(t) = log(N / df(t))`. What's `idf` when `df = N` (term in
   every doc)? Why is that the right behavior?
4. A user queries `python AND NOT java`. Sketch the algorithm using
   posting lists.
5. Stemming maps `running` to `run`. What's the precision/recall
   tradeoff vs not stemming?
6. Why do phrase queries need **positions** in the posting list,
   not just doc_ids?
