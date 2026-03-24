# Day 56: Full-Text Search Engine — Tries + Inverted Index

## Why This Exists

Every time you type a query into Google, VS Code's Cmd+Shift+F, or grep a codebase, a search engine runs underneath. This project builds one from scratch, combining three data structures we've already implemented:

- **Trie** (Day 53) — powers autocomplete suggestions
- **Radix tree** (Day 54) — memory-efficient prefix matching for large vocabularies
- **Suffix array** (Day 55) — enables substring search within documents

The missing piece is the **inverted index** — the data structure that makes search *fast*. Instead of scanning every document for a query term (O(total_chars)), an inverted index maps each word to the documents containing it, enabling O(1) lookup per term.

## Theory (40 min)

### The Inverted Index

A forward index maps documents → words:
```
doc1: ["the", "cat", "sat", "on", "the", "mat"]
doc2: ["the", "dog", "chased", "the", "cat"]
```

An inverted index flips this — words → documents:
```
"the"    → {doc1: [0, 4], doc2: [0, 3]}
"cat"    → {doc1: [1],    doc2: [4]}
"sat"    → {doc1: [2]}
"dog"    → {doc2: [1]}
"chased" → {doc2: [2]}
"mat"    → {doc1: [5]}
"on"     → {doc1: [3]}
```

Each entry stores not just *which* documents, but *where* in each document (positional index). This enables:
- **Boolean queries**: "cat AND dog" → intersection of posting lists
- **Phrase queries**: "the cat" → check positions are consecutive
- **Proximity queries**: "cat NEAR dog" → check position distance

### TF-IDF Scoring

Not all matches are equal. "the" appears everywhere (low signal), "cat" is more specific (high signal).

**Term Frequency (TF)**: How often a term appears in *this* document.
```
tf(t, d) = count(t in d) / len(d)
```

**Inverse Document Frequency (IDF)**: How rare the term is across *all* documents.
```
idf(t) = log(N / df(t))
```
where N = total documents, df(t) = documents containing term t.

**TF-IDF** = tf × idf — high when a term is frequent in this doc but rare overall.

### Architecture

```
┌─────────────────────────────────────────────────┐
│                  Search Engine                    │
│                                                   │
│  ┌──────────┐  ┌──────────────┐  ┌────────────┐ │
│  │ Tokenizer │  │Inverted Index│  │   Trie     │ │
│  │           │→ │              │  │(autocomplete│ │
│  │ normalize │  │ term → docs  │  │ vocabulary) │ │
│  │ stem      │  │ + positions  │  │            │ │
│  │ stopwords │  │ + tf-idf     │  └────────────┘ │
│  └──────────┘  └──────────────┘                   │
│                                                   │
│  Query Pipeline:                                  │
│  query → tokenize → lookup terms → score → rank  │
└─────────────────────────────────────────────────┘
```

### Complexity

| Operation | Time | Why |
|-----------|------|-----|
| Index one document | O(n) | n = tokens in document |
| Boolean AND query | O(min(p1, p2)) | Intersection of sorted posting lists |
| Boolean OR query | O(p1 + p2) | Union of sorted posting lists |
| Phrase query | O(p + m) | p = positions to check, m = phrase length |
| TF-IDF ranking | O(k × avg_p) | k = query terms, avg_p = avg posting list length |
| Autocomplete | O(prefix_len + results) | Trie prefix walk + DFS collection |

### Why Not Just grep?

grep scans every byte of every file — O(total_bytes). For 1M documents:
- grep: scan all 1M docs every query → O(N × avg_doc_size)
- Inverted index: look up the term → O(1) then score k matching docs → O(k)

The inverted index pays upfront (indexing time) to make queries instant. This is the fundamental **build once, query many** trade-off of all search systems.

## Checkpoint Questions

1. Why does the inverted index store positions, not just document IDs?
2. Why does IDF use logarithm — what would happen without it?
3. How would you handle a query like `"machine learning" AND python` (phrase + boolean)?
4. Why do search engines remove stop words during indexing, and when does this backfire?
5. What happens to TF-IDF scores when you add millions of near-duplicate documents?
6. How would you update the inverted index when a document is edited — what's the cost?
