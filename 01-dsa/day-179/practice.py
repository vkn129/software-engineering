"""
Day 179 Practice: Search engine building blocks (4 exercises).
"""

import math
import re
from collections import defaultdict


def try_or_sol(fn_name, *args, **kwargs):
    student_fn = globals().get(fn_name)
    sol_fn = globals().get(f"_sol_{fn_name}")
    if student_fn:
        r = student_fn(*args, **kwargs)
        if r is not None:
            return r
    return sol_fn(*args, **kwargs)


# ===================================================================
# Ex 1: Tokenize
# ===================================================================
# Lowercase, extract A-Z words, drop a hardcoded stopword list.

STOPWORDS = {'the', 'a', 'an', 'is', 'of', 'and'}
WORD_RE = re.compile(r"[A-Za-z]+")


def tokenize(text):
    """Return list of lowercased tokens with stopwords removed."""
    # TODO: implement
    pass


def _sol_tokenize(text):
    return [w.lower() for w in WORD_RE.findall(text)
            if w.lower() not in STOPWORDS]


# ===================================================================
# Ex 2: Build inverted index
# ===================================================================
# Returns dict: term -> sorted list of doc_ids that contain it.

def build_inverted_index(docs):
    """docs: dict doc_id -> text. Returns dict term -> sorted [doc_id]."""
    # TODO: implement
    pass


def _sol_build_inverted_index(docs):
    idx = defaultdict(set)
    for d, text in docs.items():
        for t in _sol_tokenize(text):
            idx[t].add(d)
    return {t: sorted(ds) for t, ds in idx.items()}


# ===================================================================
# Ex 3: Sorted list intersection (AND)
# ===================================================================

def intersect_sorted(a, b):
    """Both inputs are sorted. Return sorted intersection in O(|a|+|b|)."""
    # TODO: implement
    pass


def _sol_intersect_sorted(a, b):
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


# ===================================================================
# Ex 4: TF-IDF score
# ===================================================================
# tf = count of term in doc
# idf = log(N / df), where df = number of docs containing term.

def tfidf(query_terms, doc_terms, all_docs):
    """
    query_terms: list of terms in query
    doc_terms: list of terms in target doc
    all_docs: list of token lists, one per doc in corpus
    Returns total TF-IDF score for this doc.
    """
    # TODO: implement
    pass


def _sol_tfidf(query_terms, doc_terms, all_docs):
    N = len(all_docs)
    score = 0.0
    for t in query_terms:
        tf = doc_terms.count(t)
        if tf == 0:
            continue
        df = sum(1 for d in all_docs if t in d)
        if df == 0:
            continue
        score += tf * math.log(N / df)
    return score


# ===================================================================
# Tests
# ===================================================================

def run_tests():
    passed = failed = 0

    def check(name, got, expected, tol=0):
        nonlocal passed, failed
        ok = (got == expected) if tol == 0 else (abs(got - expected) < tol)
        if ok:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  expected={expected}  got={got}")
            failed += 1

    print("Exercise 1: Tokenize")
    check("basic", try_or_sol("tokenize", "The Quick Brown Fox"),
          ['quick', 'brown', 'fox'])
    check("strips punctuation",
          try_or_sol("tokenize", "Hello, world! Is this Python?"),
          ['hello', 'world', 'this', 'python'])

    print("\nExercise 2: Inverted Index")
    docs = {1: "apple banana", 2: "banana cherry", 3: "apple cherry"}
    idx = try_or_sol("build_inverted_index", docs)
    check("apple in 1,3", idx.get('apple'), [1, 3])
    check("banana in 1,2", idx.get('banana'), [1, 2])
    check("cherry in 2,3", idx.get('cherry'), [2, 3])

    print("\nExercise 3: Intersection")
    check("disjoint", try_or_sol("intersect_sorted", [1, 2], [3, 4]), [])
    check("overlap",
          try_or_sol("intersect_sorted", [1, 3, 5, 7], [3, 5, 9]),
          [3, 5])
    check("identical",
          try_or_sol("intersect_sorted", [1, 2, 3], [1, 2, 3]),
          [1, 2, 3])

    print("\nExercise 4: TF-IDF")
    # 3 docs: ['cat'], ['cat', 'dog'], ['dog', 'fish']
    docs = [['cat'], ['cat', 'dog'], ['dog', 'fish']]
    # 'cat' appears in 2/3 docs -> idf = log(3/2)
    # 'fish' appears in 1/3 docs -> idf = log(3/1)
    # score of query 'fish' against doc ['dog', 'fish'] = 1 * log(3)
    expected = math.log(3.0)
    check("rare term high score",
          try_or_sol("tfidf", ['fish'], ['dog', 'fish'], docs),
          expected, tol=1e-9)
    check("no match -> 0",
          try_or_sol("tfidf", ['python'], ['dog', 'fish'], docs),
          0.0, tol=1e-9)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print(f"{'='*50}")


if __name__ == "__main__":
    run_tests()
