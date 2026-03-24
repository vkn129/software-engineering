"""
Day 56 Practice: Full-Text Search Engine Extensions

These exercises extend the search engine with production-relevant features.
Each one teaches a concept used in real search systems (Elasticsearch, Lucene, Solr).
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from search_engine import SearchEngine, tokenize, STOP_WORDS

# ─── Exercise 1: BM25 Scoring ─────────────────────────────────────────────────
#
# TF-IDF has a flaw: if a term appears 100 times vs 50 times, TF doubles the
# score — but the document isn't twice as relevant. BM25 adds saturation:
# after a point, more occurrences barely increase the score.
#
# BM25(t, d) = idf(t) * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * |d|/avgdl))
#
# k1 controls TF saturation (typical: 1.2-2.0)
# b  controls document length normalization (typical: 0.75)
# avgdl = average document length across corpus

def bm25_search(engine: SearchEngine, query: str, top_k: int = 10,
                k1: float = 1.5, b: float = 0.75) -> list[tuple[str, float]]:
    """
    Rank documents using BM25 instead of raw TF-IDF.

    Returns: list of (doc_id, score) sorted by score descending.

    Hint: You have access to engine.idx (the InvertedIndex) which gives you:
    - engine.idx.get_postings(term) → {doc_id: PostingEntry}
    - entry.term_frequency (already normalized by doc length)
    - entry.positions (raw count = len(positions))
    - engine.idx.idf(term)
    - engine.idx.doc_lengths[doc_id]
    - engine.idx.doc_count

    For BM25, use raw term count (len(entry.positions)), not normalized TF.
    """
    # TODO: Implement BM25 scoring
    # 1. Tokenize query
    # 2. Compute avgdl (average document length)
    # 3. For each query term:
    #    a. Get IDF
    #    b. For each document in posting list:
    #       - Get raw tf = len(entry.positions)
    #       - Get doc_len = engine.idx.doc_lengths[doc_id]
    #       - Compute BM25 term score
    #       - Accumulate into document scores
    # 4. Sort by score descending, return top_k
    pass


# ─── Exercise 2: Proximity Search ─────────────────────────────────────────────
#
# Phrase search requires exact consecutive positions. Proximity search relaxes
# this: find documents where terms appear within N positions of each other.
# "cat NEAR/3 dog" means cat and dog within 3 words.

def proximity_search(engine: SearchEngine, term1: str, term2: str,
                     max_distance: int) -> list[tuple[str, int]]:
    """
    Find documents where term1 and term2 appear within max_distance positions.

    Returns: list of (doc_id, min_distance) sorted by distance ascending.

    Hint: For each document containing both terms, find the minimum distance
    between any position of term1 and any position of term2. Use the sorted
    nature of position lists for an efficient two-pointer merge.
    """
    # TODO: Implement proximity search
    # 1. Get posting lists for both terms
    # 2. Find documents in both lists (intersection)
    # 3. For each common document:
    #    a. Get positions for term1 and term2
    #    b. Find minimum distance using two-pointer technique:
    #       - i, j = 0, 0
    #       - While both pointers valid:
    #         - dist = abs(positions1[i] - positions2[j])
    #         - Track minimum distance
    #         - Advance the pointer with the smaller position
    #    c. If min_distance <= max_distance, include in results
    # 4. Sort by distance ascending
    pass


# ─── Exercise 3: Field Boosting ───────────────────────────────────────────────
#
# In real search engines, a match in the title is worth more than a match in
# the body. This is "field boosting" — different fields have different weights.

def field_boosted_search(engine: SearchEngine, query: str,
                         title_boost: float = 3.0,
                         top_k: int = 10) -> list[tuple[str, float]]:
    """
    Search with title matches boosted over content matches.

    Returns: list of (doc_id, score) sorted by score descending.

    Hint: For each query token, check if it appears in the document's title
    (engine.idx.documents[doc_id].title). If yes, multiply that term's
    contribution by title_boost.
    """
    # TODO: Implement field-boosted search
    # 1. Tokenize query
    # 2. For each query term:
    #    a. Get postings and IDF
    #    b. For each document:
    #       - Base score = tf * idf
    #       - If term appears in tokenize(doc.title): multiply by title_boost
    #       - Accumulate
    # 3. Sort by score descending, return top_k
    pass


# ─── Exercise 4: Highlight Matches ────────────────────────────────────────────
#
# Search results should highlight matching terms. This requires finding
# the original (pre-tokenized) positions in the raw text.

def highlight_matches(content: str, query: str,
                      before: str = "**", after: str = "**") -> str:
    """
    Return content with query terms wrapped in before/after markers.

    Example: highlight_matches("The cat sat on the mat", "cat mat")
             → "The **cat** sat on the **mat**"

    Hint: Find each query token in the lowercased content, but preserve
    original casing in the output. Be careful not to double-highlight
    overlapping matches.
    """
    # TODO: Implement match highlighting
    # 1. Tokenize query to get search terms
    # 2. Find all match positions in content (case-insensitive)
    # 3. Sort positions, merge overlapping spans
    # 4. Build output string with markers inserted
    pass


# ─── Exercise 5: Index Compression ────────────────────────────────────────────
#
# Posting lists store document IDs. If sorted, we can store gaps (deltas)
# instead: [1, 5, 8, 15] → [1, 4, 3, 7]. Smaller numbers compress better.
# This is how Lucene stores millions of posting lists efficiently.

def delta_encode(posting_ids: list[int]) -> list[int]:
    """
    Delta-encode a sorted list of IDs.
    [1, 5, 8, 15] → [1, 4, 3, 7]
    """
    # TODO: Implement delta encoding
    pass


def delta_decode(deltas: list[int]) -> list[int]:
    """
    Decode delta-encoded IDs back to original.
    [1, 4, 3, 7] → [1, 5, 8, 15]
    """
    # TODO: Implement delta decoding
    pass


def compression_ratio(posting_ids: list[int]) -> float:
    """
    Compute the compression ratio of delta encoding using variable-byte encoding.

    Variable-byte: each number uses ceil(log2(n+1) / 7) bytes (7 data bits per byte).
    Compare total bytes for original IDs vs delta-encoded IDs.

    Returns: ratio = original_bytes / delta_bytes (>1 means compression helped)
    """
    # TODO: Implement compression ratio calculation
    # 1. Delta encode the IDs
    # 2. For each number (original and delta), compute vbyte size:
    #    vbyte_size(n) = max(1, ceil(n.bit_length() / 7))
    # 3. Return sum(original_sizes) / sum(delta_sizes)
    pass


# ─── Solutions ────────────────────────────────────────────────────────────────

def _bm25_search_solution(engine, query, top_k=10, k1=1.5, b=0.75):
    tokens = tokenize(query)
    if not tokens:
        return []

    # Average document length
    if not engine.idx.doc_lengths:
        return []
    avgdl = sum(engine.idx.doc_lengths.values()) / len(engine.idx.doc_lengths)

    scores = {}
    for token in tokens:
        postings = engine.idx.get_postings(token)
        idf = engine.idx.idf(token)

        for doc_id, entry in postings.items():
            tf = len(entry.positions)  # raw count
            doc_len = engine.idx.doc_lengths[doc_id]

            # BM25 formula
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * doc_len / avgdl)
            bm25_score = idf * numerator / denominator

            scores[doc_id] = scores.get(doc_id, 0) + bm25_score

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return ranked[:top_k]


def _proximity_search_solution(engine, term1, term2, max_distance):
    t1 = tokenize(term1)
    t2 = tokenize(term2)
    if not t1 or not t2:
        return []
    t1, t2 = t1[0], t2[0]

    postings1 = engine.idx.get_postings(t1)
    postings2 = engine.idx.get_postings(t2)

    common_docs = set(postings1.keys()) & set(postings2.keys())
    results = []

    for doc_id in common_docs:
        pos1 = postings1[doc_id].positions
        pos2 = postings2[doc_id].positions

        # Two-pointer to find minimum distance
        i, j = 0, 0
        min_dist = float('inf')
        while i < len(pos1) and j < len(pos2):
            dist = abs(pos1[i] - pos2[j])
            min_dist = min(min_dist, dist)
            if pos1[i] < pos2[j]:
                i += 1
            else:
                j += 1

        if min_dist <= max_distance:
            results.append((doc_id, min_dist))

    return sorted(results, key=lambda x: x[1])


def _field_boosted_search_solution(engine, query, title_boost=3.0, top_k=10):
    tokens = tokenize(query)
    if not tokens:
        return []

    scores = {}
    for token in tokens:
        postings = engine.idx.get_postings(token)
        idf = engine.idx.idf(token)

        for doc_id, entry in postings.items():
            base_score = entry.term_frequency * idf
            doc = engine.idx.documents[doc_id]
            title_tokens = tokenize(doc.title)
            if token in title_tokens:
                base_score *= title_boost
            scores[doc_id] = scores.get(doc_id, 0) + base_score

    ranked = sorted(scores.items(), key=lambda x: -x[1])
    return ranked[:top_k]


def _highlight_matches_solution(content, query, before="**", after="**"):
    tokens = set(tokenize(query))
    if not tokens:
        return content

    import re as _re
    # Find all match spans
    spans = []
    content_lower = content.lower()
    for token in tokens:
        start = 0
        while True:
            # Find word boundaries
            pattern = r'\b' + _re.escape(token) + r'\b'
            match = _re.search(pattern, content_lower[start:])
            if not match:
                break
            spans.append((start + match.start(), start + match.end()))
            start += match.end()

    if not spans:
        return content

    # Merge overlapping spans
    spans.sort()
    merged = [spans[0]]
    for s, e in spans[1:]:
        if s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))

    # Build highlighted string
    result = []
    prev_end = 0
    for s, e in merged:
        result.append(content[prev_end:s])
        result.append(before + content[s:e] + after)
        prev_end = e
    result.append(content[prev_end:])

    return "".join(result)


def _delta_encode_solution(posting_ids):
    if not posting_ids:
        return []
    result = [posting_ids[0]]
    for i in range(1, len(posting_ids)):
        result.append(posting_ids[i] - posting_ids[i - 1])
    return result


def _delta_decode_solution(deltas):
    if not deltas:
        return []
    result = [deltas[0]]
    for i in range(1, len(deltas)):
        result.append(result[-1] + deltas[i])
    return result


def _compression_ratio_solution(posting_ids):
    import math as _math
    if not posting_ids:
        return 1.0

    def vbyte_size(n):
        if n == 0:
            return 1
        return max(1, _math.ceil(n.bit_length() / 7))

    deltas = _delta_encode_solution(posting_ids)
    original_bytes = sum(vbyte_size(x) for x in posting_ids)
    delta_bytes = sum(vbyte_size(x) for x in deltas)
    return original_bytes / delta_bytes if delta_bytes > 0 else 1.0


# ─── Test Runner ──────────────────────────────────────────────────────────────

def _build_test_engine():
    """Build a search engine with test documents."""
    engine = SearchEngine()
    engine.index_document("doc1", "Binary Trees",
        "A binary tree is a tree data structure where each node has at most two children. "
        "Binary search trees maintain sorted order enabling logarithmic search. "
        "AVL trees and red black trees are self balancing binary search trees.")
    engine.index_document("doc2", "Hash Tables",
        "A hash table maps keys to values using a hash function. "
        "Collisions are resolved by chaining or open addressing. "
        "Hash tables provide constant average lookup but linear worst case.")
    engine.index_document("doc3", "Graph Algorithms",
        "Graphs represent relationships between objects. BFS explores level by level "
        "while DFS goes deep before backtracking. Dijkstra finds shortest paths. "
        "Topological sort orders directed acyclic graphs.")
    engine.index_document("doc4", "Sorting Algorithms",
        "Merge sort divides and conquers. Quicksort is fast on average but quadratic "
        "worst case. Heap sort uses a binary heap for sorting. "
        "Comparison sorts cannot beat n log n lower bound.")
    engine.index_document("doc5", "Tree Balancing",
        "Self balancing trees prevent degradation to linear linked lists. "
        "AVL trees maintain strict balance with rotations after every insert. "
        "Red black trees allow slight imbalance for faster inserts. "
        "B trees balance for disk access not memory.")
    return engine


def run_tests():
    engine = _build_test_engine()
    passed = 0
    failed = 0

    def check(name, fn, *args, validator=None, **kwargs):
        nonlocal passed, failed
        try:
            result = fn(*args, **kwargs)
            if result is None:
                print(f"  ⬜ {name} — not implemented yet")
                return
            if validator:
                assert validator(result), f"Validation failed: {result}"
            print(f"  ✅ {name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name} — {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("Day 56 Practice Tests")
    print("=" * 60)

    # Exercise 1: BM25
    print("\n📝 Exercise 1: BM25 Scoring")
    check("BM25 returns results", bm25_search, engine, "binary tree",
          validator=lambda r: len(r) > 0)
    check("BM25 top result is tree-related", bm25_search, engine, "binary tree",
          validator=lambda r: r[0][0] in ("doc1", "doc5"))
    check("BM25 scores are positive", bm25_search, engine, "hash table",
          validator=lambda r: all(s > 0 for _, s in r))

    # Exercise 2: Proximity
    print("\n📝 Exercise 2: Proximity Search")
    check("Proximity finds near terms", proximity_search, engine, "binary", "tree", 3,
          validator=lambda r: len(r) > 0)
    check("Proximity distance is correct", proximity_search, engine, "binary", "tree", 1,
          validator=lambda r: all(d <= 1 for _, d in r))
    check("Proximity excludes distant terms", proximity_search, engine, "hash", "graph", 1,
          validator=lambda r: len(r) == 0)

    # Exercise 3: Field Boosting
    print("\n📝 Exercise 3: Field Boosting")
    check("Boosted search returns results", field_boosted_search, engine, "tree",
          validator=lambda r: len(r) > 0)
    check("Title match ranked higher", field_boosted_search, engine, "binary tree",
          validator=lambda r: r[0][0] == "doc1")  # "Binary Trees" title

    # Exercise 4: Highlighting
    print("\n📝 Exercise 4: Match Highlighting")
    check("Highlights single term",
          highlight_matches, "The cat sat on the mat", "cat",
          validator=lambda r: "**cat**" in r)
    check("Highlights multiple terms",
          highlight_matches, "The cat sat on the mat", "cat mat",
          validator=lambda r: "**cat**" in r and "**mat**" in r)
    check("Preserves original casing",
          highlight_matches, "The Cat SAT on the Mat", "cat mat",
          validator=lambda r: "**Cat**" in r and "**Mat**" in r)

    # Exercise 5: Compression
    print("\n📝 Exercise 5: Index Compression")
    check("Delta encode",
          delta_encode, [1, 5, 8, 15],
          validator=lambda r: r == [1, 4, 3, 7])
    check("Delta decode",
          delta_decode, [1, 4, 3, 7],
          validator=lambda r: r == [1, 5, 8, 15])
    check("Round-trip encode/decode",
          lambda ids: delta_decode(delta_encode(ids)), [3, 10, 20, 100, 500],
          validator=lambda r: r == [3, 10, 20, 100, 500])
    check("Compression ratio > 1 for large gaps",
          compression_ratio, list(range(0, 10000, 100)),
          validator=lambda r: r > 1.0)
    check("Empty list handling",
          delta_encode, [],
          validator=lambda r: r == [])

    print(f"\n{'─' * 60}")
    print(f"Results: {passed} passed, {failed} failed, "
          f"{5 * 3 - passed - failed} not implemented")


if __name__ == "__main__":
    run_tests()
