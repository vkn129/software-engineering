"""
Day 180: Capstone Part B — Search Refinement (Part 2/2)

Extends day-179's search engine with:
  * Levenshtein edit distance + trigram-filtered fuzzy term lookup.
  * Query expansion (synonyms + fuzzy matches).
  * BM25 scoring with length normalization.

Run me:
    python3 day-180/search_refinement.py
"""

import math
import os
import sys
from collections import defaultdict


HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', 'day-179')))

from search_engine import (  # noqa: E402
    InvertedIndex, tokenize, stem, CORPUS, short,
)


# ===========================================================================
# 1. Levenshtein edit distance (DP)
# ===========================================================================

def edit_distance(a, b):
    """Classic O(|a|·|b|) DP. Returns min insertions+deletions+substitutions."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            cur[j] = min(
                cur[j - 1] + 1,        # insertion
                prev[j] + 1,           # deletion
                prev[j - 1] + cost,    # substitution
            )
        prev = cur
    return prev[-1]


# ===========================================================================
# 2. Trigram index for fuzzy matching
# ===========================================================================

def trigrams(s):
    """Return the set of character trigrams in s (with $ padding)."""
    padded = '$' + s + '$'
    if len(padded) < 3:
        return {padded}
    return {padded[i:i + 3] for i in range(len(padded) - 2)}


class TrigramIndex:
    """trigram -> set of terms containing that trigram."""

    def __init__(self, vocab):
        self.idx = defaultdict(set)
        for term in vocab:
            for tg in trigrams(term):
                self.idx[tg].add(term)

    def candidates(self, term):
        """Return union of terms sharing any trigram with `term`."""
        out = set()
        for tg in trigrams(term):
            out |= self.idx.get(tg, set())
        return out


def fuzzy_terms(query_term, trigram_index, max_distance=None):
    """
    Return set of vocab terms with edit_distance(query_term, t) <= max_distance.
    Trigram filter first, then full edit-distance verification.
    """
    if max_distance is None:
        max_distance = 2 if len(query_term) >= 5 else 1
    cands = trigram_index.candidates(query_term)
    out = set()
    for t in cands:
        if abs(len(t) - len(query_term)) > max_distance:
            continue
        if edit_distance(query_term, t) <= max_distance:
            out.add(t)
    return out


# ===========================================================================
# 3. BM25
# ===========================================================================

def bm25_score(index, query_terms, doc_id, k1=1.5, b=0.75, term_weights=None):
    """
    Standard BM25 scoring. term_weights: optional dict term -> weight in [0,1].
    """
    N = index.N()
    if N == 0:
        return 0.0
    total_len = sum(index.doc_lengths.values())
    avgdl = total_len / N
    dl = index.doc_lengths.get(doc_id, 0)
    score = 0.0
    for t in query_terms:
        tf = index.tf(t, doc_id)
        if tf == 0:
            continue
        df = index.df(t)
        # BM25 idf variant (positive even when df > N/2)
        idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
        norm = tf + k1 * (1 - b + b * dl / max(1.0, avgdl))
        contribution = idf * tf * (k1 + 1) / norm
        if term_weights:
            contribution *= term_weights.get(t, 1.0)
        score += contribution
    return score


# ===========================================================================
# 4. Query expansion
# ===========================================================================

# Toy synonym dictionary. Production uses WordNet.
SYNONYMS = {
    'language': ['lang'],
    'engine':   ['system'],
    'search':   ['lookup', 'find'],
    'function': ['method', 'procedure'],
    'document': ['file', 'page'],
    'tree':     ['hierarchy'],
}

EXPANSION_WEIGHTS = {
    'exact':   1.0,
    'synonym': 0.7,
    'fuzzy':   0.5,
}


def expand_query(query_text, index, trigram_index, *, use_fuzzy=True,
                 use_synonyms=True):
    """
    Return (expanded_terms_list, term_weights_dict).
    Expanded terms include the original (stemmed) tokens plus fuzzy and
    synonym variants, each weighted appropriately.
    """
    base = tokenize(query_text)
    expanded = list(base)
    weights = {t: EXPANSION_WEIGHTS['exact'] for t in base}

    if use_synonyms:
        for t in base:
            # Also try the un-stemmed variant in the synonym map
            for raw_key, syns in SYNONYMS.items():
                key = stem(raw_key)
                if t == key:
                    for s in syns:
                        ss = stem(s)
                        if ss not in weights:
                            expanded.append(ss)
                            weights[ss] = EXPANSION_WEIGHTS['synonym']

    if use_fuzzy:
        for t in list(base):
            for fz in fuzzy_terms(t, trigram_index):
                if fz not in weights:
                    expanded.append(fz)
                    weights[fz] = EXPANSION_WEIGHTS['fuzzy']

    return expanded, weights


# ===========================================================================
# 5. Top-level search
# ===========================================================================

def search_refined(index, trigram_index, query, *, top_k=5,
                   use_fuzzy=True, use_synonyms=True, scorer='bm25'):
    terms, weights = expand_query(
        query, index, trigram_index,
        use_fuzzy=use_fuzzy, use_synonyms=use_synonyms,
    )
    candidates = set()
    for t in terms:
        candidates.update(index.doc_ids_for_term(t))
    scored = []
    for d in candidates:
        if scorer == 'bm25':
            s = bm25_score(index, terms, d, term_weights=weights)
        else:  # plain tfidf with weights
            s = 0.0
            for t in terms:
                tf = index.tf(t, d)
                if tf == 0:
                    continue
                s += tf * index.idf(t) * weights.get(t, 1.0)
        if s > 0:
            scored.append((d, s))
    scored.sort(key=lambda x: (-x[1], x[0]))
    return scored[:top_k], terms, weights


# ===========================================================================
# 6. Demo
# ===========================================================================

def build_everything():
    idx = InvertedIndex()
    for doc_id, text in CORPUS.items():
        idx.add(doc_id, text)
    vocab = set()
    for term_dict in idx._postings.values():
        pass
    vocab = set(idx._postings.keys())
    tri = TrigramIndex(vocab)
    return idx, tri


def demo():
    idx, tri = build_everything()

    print("=" * 60)
    print("DEMO 1: Edit distance & fuzzy lookup")
    print("=" * 60)
    pairs = [('kitten', 'sitting'), ('python', 'pyhton'),
             ('search', 'serach'), ('engine', 'engin')]
    for a, b in pairs:
        print(f"  edit_distance({a!r:>10}, {b!r:>10}) = {edit_distance(a, b)}")

    print("\n  Fuzzy lookup for misspelled queries:")
    for typo in ['pyhton', 'lamba', 'serach', 'progamming']:
        matches = fuzzy_terms(typo, tri)
        print(f"    {typo!r} -> {sorted(matches)}")

    print("\n" + "=" * 60)
    print("DEMO 2: Plain TF-IDF vs BM25 (no expansion)")
    print("=" * 60)
    query = "python programming language"
    print(f"\nquery: {query!r}")
    for scorer in ('tfidf', 'bm25'):
        results, _, _ = search_refined(
            idx, tri, query, top_k=4, use_fuzzy=False, use_synonyms=False,
            scorer=scorer)
        print(f"\n  [{scorer}] rankings:")
        for d, s in results:
            print(f"    {d}  score={s:.3f}  len={idx.doc_lengths[d]}  "
                  f"{short(idx, d, 60)}")

    print("\n" + "=" * 60)
    print("DEMO 3: Fuzzy match — typo recovery")
    print("=" * 60)
    for q in ["pyhton lamba", "serach engin"]:
        print(f"\nquery: {q!r}")
        # First without fuzzy: probably empty
        no_fz, _, _ = search_refined(
            idx, tri, q, use_fuzzy=False, use_synonyms=False)
        print(f"  no fuzzy:    {len(no_fz)} results")
        # With fuzzy
        with_fz, terms, weights = search_refined(
            idx, tri, q, use_fuzzy=True, use_synonyms=False)
        print(f"  with fuzzy:  {len(with_fz)} results")
        print(f"    expanded terms: {sorted(set(terms))}")
        for d, s in with_fz[:3]:
            print(f"    {d}  score={s:.3f}  {short(idx, d, 60)}")

    print("\n" + "=" * 60)
    print("DEMO 4: Synonym expansion")
    print("=" * 60)
    q = "search engine"
    for use_syn in (False, True):
        results, terms, _ = search_refined(
            idx, tri, q, use_fuzzy=False, use_synonyms=use_syn)
        print(f"\n  synonyms={use_syn}: {len(results)} results, "
              f"terms={sorted(set(terms))}")
        for d, s in results[:3]:
            print(f"    {d}  score={s:.3f}  {short(idx, d, 60)}")

    print("\n" + "=" * 60)
    print("DEMO 5: Full pipeline (fuzzy + synonyms + BM25)")
    print("=" * 60)
    for q in ["python lambda", "tree database", "serach engin"]:
        print(f"\nquery: {q!r}")
        results, _, _ = search_refined(idx, tri, q, top_k=3)
        for d, s in results:
            print(f"    {d}  score={s:.3f}  {short(idx, d, 60)}")


if __name__ == "__main__":
    demo()
