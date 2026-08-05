"""
Day 179: Capstone Part B — Search Engine (Part 1/2)

Inverted index + TF-IDF ranking + Boolean and phrase queries.
Stdlib only.

Run me:
    python3 day-179/search_engine.py
"""

import math
import re
from collections import defaultdict


# ===========================================================================
# 1. Tokenizer
# ===========================================================================

STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'such',
    'that', 'the', 'their', 'then', 'there', 'these', 'they', 'this',
    'to', 'was', 'will', 'with', 'i', 'you', 'we',
}

# Tiny suffix-stripping stemmer. Production uses Porter — this is a toy.
_SUFFIXES = [
    'ational', 'tional', 'enci', 'anci', 'izer',
    'ization', 'ation', 'ator', 'iveness', 'fulness', 'ousness',
    'aliti', 'iviti', 'biliti',
    'ies', 'sses', 'ied', 'ing', 'ed', 'er', 'est', 'ly', 'es', 's',
]


def stem(word):
    for s in _SUFFIXES:
        if len(word) > len(s) + 2 and word.endswith(s):
            return word[: -len(s)]
    return word


_TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9']*")


def tokenize(text, *, do_stem=True, drop_stopwords=True):
    """Lowercase, split on word characters, drop stopwords, optionally stem."""
    out = []
    for m in _TOKEN_RE.finditer(text):
        w = m.group(0).lower().replace("'", "")
        if drop_stopwords and w in STOPWORDS:
            continue
        if do_stem:
            w = stem(w)
        out.append(w)
    return out


# ===========================================================================
# 2. Crawler (file-based)
# ===========================================================================

def crawl_strings(named_docs):
    """
    Build documents from a dict {doc_id: text}. Equivalent to a 'crawler'
    that already has docs in hand.
    """
    return [(doc_id, text) for doc_id, text in named_docs.items()]


def crawl_directory(root, extensions=('.txt', '.md')):
    """Walk a directory, read text files. Returns list[(path, text)]."""
    import os
    docs = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.endswith(extensions):
                full = os.path.join(dirpath, fn)
                try:
                    with open(full, 'r', encoding='utf-8') as f:
                        docs.append((full, f.read()))
                except OSError:
                    pass
    return docs


# ===========================================================================
# 3. Inverted Index
# ===========================================================================

class InvertedIndex:
    """
    Term -> sorted list of (doc_id, [positions]).

    Stores:
      - doc_lengths: total token count per doc (for TF-IDF / BM25).
      - doc_ids: list of all known doc ids.
    """

    def __init__(self):
        # term -> dict(doc_id -> list[int])
        self._postings = defaultdict(dict)
        self.doc_lengths = {}
        self.doc_ids = []
        self.doc_texts = {}

    def add(self, doc_id, text):
        tokens = tokenize(text)
        self.doc_lengths[doc_id] = len(tokens)
        self.doc_texts[doc_id] = text
        if doc_id not in self.doc_ids:
            self.doc_ids.append(doc_id)
        for pos, tok in enumerate(tokens):
            self._postings[tok].setdefault(doc_id, []).append(pos)

    # ------------ access ------------
    def df(self, term):
        return len(self._postings.get(term, {}))

    def tf(self, term, doc_id):
        return len(self._postings.get(term, {}).get(doc_id, ()))

    def postings(self, term):
        """Return sorted list of (doc_id, positions)."""
        d = self._postings.get(term, {})
        return sorted(d.items(), key=lambda x: x[0])

    def N(self):
        return len(self.doc_ids)

    def idf(self, term):
        n = self.N()
        df = self.df(term)
        if df == 0:
            return 0.0
        return math.log((n + 1) / df)

    # ------------ Boolean ops on posting lists ------------
    def doc_ids_for_term(self, term):
        return sorted(self._postings.get(term, {}).keys())

    @staticmethod
    def intersect(a, b):
        """Linear merge intersection of sorted lists."""
        i = j = 0
        out = []
        while i < len(a) and j < len(b):
            if a[i] == b[j]:
                out.append(a[i]); i += 1; j += 1
            elif a[i] < b[j]:
                i += 1
            else:
                j += 1
        return out

    @staticmethod
    def union(a, b):
        i = j = 0
        out = []
        while i < len(a) and j < len(b):
            if a[i] == b[j]:
                out.append(a[i]); i += 1; j += 1
            elif a[i] < b[j]:
                out.append(a[i]); i += 1
            else:
                out.append(b[j]); j += 1
        out.extend(a[i:])
        out.extend(b[j:])
        return out

    @staticmethod
    def difference(a, b):
        i = j = 0
        out = []
        while i < len(a) and j < len(b):
            if a[i] == b[j]:
                i += 1; j += 1
            elif a[i] < b[j]:
                out.append(a[i]); i += 1
            else:
                j += 1
        out.extend(a[i:])
        return out


# ===========================================================================
# 4. Boolean query
# ===========================================================================

def boolean_query(index, expr):
    """
    expr supports `term`, `t1 AND t2`, `t1 OR t2`, `t1 AND NOT t2`.
    Parses left-to-right; no precedence beyond NOT binding tighter than AND.
    Returns sorted list of doc_ids.
    """
    tokens = expr.split()
    # First operand
    if not tokens:
        return []
    if tokens[0] == 'NOT':
        # Tricky; not supported as leading operator. Treat as 'all - X'.
        all_docs = sorted(index.doc_ids)
        result = InvertedIndex.difference(
            all_docs, index.doc_ids_for_term(stem(tokens[1].lower())))
        i = 2
    else:
        result = index.doc_ids_for_term(stem(tokens[0].lower()))
        i = 1
    while i < len(tokens):
        op = tokens[i].upper()
        if op == 'AND':
            i += 1
            if i < len(tokens) and tokens[i].upper() == 'NOT':
                i += 1
                term = stem(tokens[i].lower())
                result = InvertedIndex.difference(result, index.doc_ids_for_term(term))
            else:
                term = stem(tokens[i].lower())
                result = InvertedIndex.intersect(result, index.doc_ids_for_term(term))
        elif op == 'OR':
            i += 1
            term = stem(tokens[i].lower())
            result = InvertedIndex.union(result, index.doc_ids_for_term(term))
        else:
            # bare term — treat as AND
            term = stem(op.lower())
            result = InvertedIndex.intersect(result, index.doc_ids_for_term(term))
        i += 1
    return result


# ===========================================================================
# 5. Phrase query (positional intersection)
# ===========================================================================

def phrase_query(index, phrase):
    """
    Returns sorted list of doc_ids where the tokenized phrase occurs
    consecutively. Stopwords are dropped from the phrase (just like indexing).
    """
    terms = tokenize(phrase)
    if not terms:
        return []
    # Start with postings of the first term
    candidates = index.postings(terms[0])  # list of (doc_id, [positions])
    # For each subsequent term, keep only docs where some position aligns.
    for offset, t in enumerate(terms[1:], start=1):
        next_postings = dict(index.postings(t))
        survived = []
        for doc_id, positions in candidates:
            other = next_postings.get(doc_id)
            if not other:
                continue
            other_set = set(other)
            new_positions = [p for p in positions if (p + 1) in other_set]
            if new_positions:
                # advance positions by one to keep alignment for next loop
                survived.append((doc_id, [p + 1 for p in new_positions]))
        candidates = survived
    return sorted(d for d, _ in candidates)


# ===========================================================================
# 6. TF-IDF ranking
# ===========================================================================

def tfidf_score(index, query_terms, doc_id):
    score = 0.0
    for t in query_terms:
        tf = index.tf(t, doc_id)
        if tf == 0:
            continue
        idf = index.idf(t)
        score += tf * idf
    return score


def search(index, query, top_k=5):
    """
    Free-text query. Returns list of (doc_id, score) ranked descending.
    """
    terms = tokenize(query)
    if not terms:
        return []
    # candidate docs = union of postings
    candidate_ids = set()
    for t in terms:
        candidate_ids.update(index.doc_ids_for_term(t))
    scored = [(d, tfidf_score(index, terms, d)) for d in candidate_ids]
    scored.sort(key=lambda x: (-x[1], x[0]))
    return scored[:top_k]


# ===========================================================================
# 7. Demo corpus
# ===========================================================================

CORPUS = {
    "doc1": "Python is a high-level programming language known for clean syntax.",
    "doc2": "The Python programming language was created by Guido van Rossum.",
    "doc3": "Java is a class-based object-oriented programming language.",
    "doc4": "Machine learning models can be implemented in Python or in Java.",
    "doc5": "Lambda calculus is a formal system for expressing computation.",
    "doc6": "A Python lambda is an anonymous function that takes any arguments.",
    "doc7": "Functional programming languages emphasize immutability and pure functions.",
    "doc8": "Inverted indexes power most modern text search engines.",
    "doc9": "Search engines rank documents using TF-IDF or BM25 algorithms.",
    "doc10": "The Google search engine indexes billions of web pages.",
    "doc11": "A B-tree is a self-balancing tree data structure used in databases.",
    "doc12": "Functional programming and lambda calculus are deeply connected.",
}


def build_index():
    idx = InvertedIndex()
    for doc_id, text in crawl_strings(CORPUS).__iter__() if False else CORPUS.items():
        idx.add(doc_id, text)
    return idx


def short(idx, doc_id, n=80):
    t = idx.doc_texts.get(doc_id, '')
    return t if len(t) <= n else t[:n] + '...'


def demo():
    idx = build_index()
    print("=" * 60)
    print(f"DEMO: Indexed {idx.N()} documents")
    print("=" * 60)

    print("\n--- TF-IDF ranked search ---")
    for q in ["python lambda", "search engine", "functional programming",
              "java", "tree database"]:
        print(f"\nquery: {q!r}")
        results = search(idx, q, top_k=4)
        for d, s in results:
            print(f"  {d}  score={s:.3f}  {short(idx, d, 70)}")

    print("\n--- Boolean queries ---")
    for q in ["python AND java",
              "python AND NOT java",
              "lambda OR functional"]:
        print(f"\nquery: {q!r}")
        docs = boolean_query(idx, q)
        for d in docs:
            print(f"  {d}  {short(idx, d, 70)}")

    print("\n--- Phrase queries ---")
    for q in ["programming language",
              "machine learning"]:
        print(f"\nphrase: {q!r}")
        docs = phrase_query(idx, q)
        for d in docs:
            print(f"  {d}  {short(idx, d, 70)}")

    print("\n--- Index statistics ---")
    sample_terms = ['python', 'lambda', 'program', 'search']
    for t in sample_terms:
        st = stem(t)
        print(f"  term={t!r:>10} stem={st!r:<10} "
              f"df={idx.df(st):>2}  idf={idx.idf(st):.3f}")


if __name__ == "__main__":
    demo()
