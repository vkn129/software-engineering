"""
Day 56: Full-Text Search Engine
Combines: Trie (autocomplete) + Inverted Index (search) + TF-IDF (ranking)
"""

import math
import re
from collections import defaultdict
from dataclasses import dataclass, field

# ─── Reuse our Trie from Day 53 ──────────────────────────────────────────────

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'day-053'))
from trie import Trie


# ─── Data Types ───────────────────────────────────────────────────────────────

@dataclass
class Document:
    """A document in the search engine."""
    doc_id: str
    title: str
    content: str


@dataclass
class PostingEntry:
    """One document's entry in a term's posting list."""
    doc_id: str
    positions: list = field(default_factory=list)  # where the term appears
    term_frequency: float = 0.0  # tf = count / doc_length


@dataclass
class SearchResult:
    """A ranked search result."""
    doc_id: str
    title: str
    score: float
    snippet: str = ""


# ─── Tokenizer ────────────────────────────────────────────────────────────────

# Common English stop words — low-signal terms removed during indexing
STOP_WORDS = frozenset([
    "a", "an", "the", "is", "it", "in", "on", "at", "to", "of",
    "and", "or", "not", "for", "with", "as", "by", "this", "that",
    "from", "are", "was", "were", "be", "been", "being", "have",
    "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "but", "if", "so",
    "than", "too", "very", "just", "about", "up", "out", "no",
    "all", "each", "every", "both", "few", "more", "most", "other",
    "some", "such", "into", "over", "after", "before", "between",
])


def tokenize(text: str) -> list[str]:
    """
    Convert text to normalized tokens.

    Steps:
    1. Lowercase
    2. Split on non-alphanumeric characters
    3. Remove stop words
    4. Remove empty strings and single characters

    Simple but effective — production engines add stemming (running → run),
    lemmatization, and synonym expansion.
    """
    words = re.findall(r'[a-z0-9]+', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


# ─── Inverted Index ──────────────────────────────────────────────────────────

class InvertedIndex:
    """
    Maps terms to posting lists (documents + positions).

    The core data structure of every search engine — from Lucene to Elasticsearch
    to Google. An inverted index flips the document→words relationship:
    instead of asking "what words are in doc X?", you ask "which docs contain word Y?"
    """

    def __init__(self):
        # term → {doc_id: PostingEntry}
        self.index: dict[str, dict[str, PostingEntry]] = defaultdict(dict)
        # doc_id → Document (forward store for snippets/titles)
        self.documents: dict[str, Document] = {}
        # Total document count (for IDF calculation)
        self.doc_count: int = 0
        # doc_id → number of tokens (for TF normalization)
        self.doc_lengths: dict[str, int] = {}

    def add_document(self, doc: Document) -> None:
        """
        Index a document: tokenize, record positions, compute TF.

        Time: O(n) where n = number of tokens in the document.
        """
        self.documents[doc.doc_id] = doc
        self.doc_count += 1

        tokens = tokenize(doc.content)
        self.doc_lengths[doc.doc_id] = len(tokens)

        # Build position list for each term in this document
        term_positions: dict[str, list[int]] = defaultdict(list)
        for pos, token in enumerate(tokens):
            term_positions[token].append(pos)

        # Create posting entries with TF
        for term, positions in term_positions.items():
            tf = len(positions) / len(tokens) if tokens else 0
            self.index[term][doc.doc_id] = PostingEntry(
                doc_id=doc.doc_id,
                positions=positions,
                term_frequency=tf,
            )

    def remove_document(self, doc_id: str) -> None:
        """Remove a document from the index."""
        if doc_id not in self.documents:
            return
        del self.documents[doc_id]
        del self.doc_lengths[doc_id]
        self.doc_count -= 1

        # Remove from all posting lists
        empty_terms = []
        for term, postings in self.index.items():
            if doc_id in postings:
                del postings[doc_id]
                if not postings:
                    empty_terms.append(term)
        for term in empty_terms:
            del self.index[term]

    def get_postings(self, term: str) -> dict[str, PostingEntry]:
        """Get the posting list for a term."""
        return self.index.get(term, {})

    def idf(self, term: str) -> float:
        """
        Inverse Document Frequency: log(N / df).

        Measures how "informative" a term is. Rare terms (appearing in few docs)
        get high IDF. Common terms get low IDF.

        Uses log(1 + N / (1 + df)) to avoid division by zero and log(0).
        """
        df = len(self.index.get(term, {}))
        return math.log(1 + self.doc_count / (1 + df))

    def vocabulary_size(self) -> int:
        """Number of unique terms in the index."""
        return len(self.index)

    def terms(self) -> list[str]:
        """All indexed terms (for trie population)."""
        return list(self.index.keys())


# ─── Search Engine ────────────────────────────────────────────────────────────

class SearchEngine:
    """
    Full-text search engine combining:
    - InvertedIndex for term→document lookup
    - TF-IDF for relevance scoring
    - Trie for autocomplete suggestions

    This is a simplified version of what Lucene/Elasticsearch do.
    Production engines add:
    - BM25 scoring (improved TF-IDF)
    - Field boosting (title matches > body matches)
    - Fuzzy matching (handle typos)
    - Sharding (distribute index across machines)
    """

    def __init__(self):
        self.idx = InvertedIndex()
        self.autocomplete = Trie()

    def index_document(self, doc_id: str, title: str, content: str) -> None:
        """Add a document to the search engine."""
        doc = Document(doc_id=doc_id, title=title, content=content)
        self.idx.add_document(doc)

        # Add all unique tokens to autocomplete trie
        for token in set(tokenize(content + " " + title)):
            self.autocomplete.insert(token)

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """
        Search for documents matching the query, ranked by TF-IDF.

        Algorithm:
        1. Tokenize the query
        2. For each query term, look up its posting list
        3. Score each document using TF-IDF: score += tf(term, doc) * idf(term)
        4. Return top-k results sorted by score descending

        Time: O(q * avg_posting_len + k * log(k))
              q = query terms, k = result count
        """
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        # Accumulate scores per document
        scores: dict[str, float] = defaultdict(float)

        for token in query_tokens:
            postings = self.idx.get_postings(token)
            idf = self.idx.idf(token)

            for doc_id, entry in postings.items():
                scores[doc_id] += entry.term_frequency * idf

        # Build results sorted by score
        results = []
        for doc_id, score in sorted(scores.items(), key=lambda x: -x[1]):
            doc = self.idx.documents[doc_id]
            snippet = self._make_snippet(doc.content, query_tokens)
            results.append(SearchResult(
                doc_id=doc_id,
                title=doc.title,
                score=round(score, 4),
                snippet=snippet,
            ))
            if len(results) >= top_k:
                break

        return results

    def boolean_and(self, query: str) -> list[str]:
        """
        Boolean AND query: return doc_ids containing ALL query terms.

        Uses posting list intersection — iterate the shortest list and
        check membership in all others. O(min(posting_lengths) * num_terms).
        """
        tokens = tokenize(query)
        if not tokens:
            return []

        # Get posting sets for each term, sorted by size (smallest first)
        posting_sets = []
        for token in tokens:
            postings = self.idx.get_postings(token)
            if not postings:
                return []  # one term missing → no results
            posting_sets.append(set(postings.keys()))

        posting_sets.sort(key=len)

        # Intersect all sets starting from smallest
        result = posting_sets[0]
        for ps in posting_sets[1:]:
            result &= ps
            if not result:
                return []

        return sorted(result)

    def boolean_or(self, query: str) -> list[str]:
        """Boolean OR query: return doc_ids containing ANY query term."""
        tokens = tokenize(query)
        result = set()
        for token in tokens:
            result |= set(self.idx.get_postings(token).keys())
        return sorted(result)

    def phrase_search(self, phrase: str) -> list[str]:
        """
        Phrase search: find documents where query terms appear consecutively.

        This is why the inverted index stores positions, not just document IDs.

        Algorithm:
        1. Tokenize the phrase
        2. Get posting lists for all terms
        3. For documents in ALL posting lists (AND), check if positions
           are consecutive: pos[term_i+1] = pos[term_i] + 1

        Example: phrase "cat sat" in doc with positions cat:[1], sat:[2]
                 → 2 - 1 = 1 ✓ (consecutive)
        """
        tokens = tokenize(phrase)
        if not tokens:
            return []

        # Get AND candidates first
        candidates = self.boolean_and(phrase)
        if not candidates:
            return []

        results = []
        for doc_id in candidates:
            # Get position lists for each term in this document
            position_lists = []
            for token in tokens:
                entry = self.idx.get_postings(token).get(doc_id)
                if not entry:
                    break
                position_lists.append(entry.positions)
            else:
                # Check for consecutive positions
                if self._has_consecutive_positions(position_lists):
                    results.append(doc_id)

        return results

    def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        """Autocomplete: return terms starting with the given prefix."""
        prefix = prefix.lower()
        return self.autocomplete.autocomplete(prefix, limit)

    # ─── Private helpers ──────────────────────────────────────────────────

    def _has_consecutive_positions(self, position_lists: list[list[int]]) -> bool:
        """
        Check if there exists a sequence of positions where each term's
        position is exactly 1 more than the previous term's position.

        Uses pointer-based merge: for each starting position of term 0,
        check if term 1 has pos+1, term 2 has pos+2, etc.
        """
        if not position_lists:
            return False

        for start_pos in position_lists[0]:
            found = True
            for i in range(1, len(position_lists)):
                expected = start_pos + i
                # Binary search would be faster, but linear scan is clearer
                if expected not in set(position_lists[i]):
                    found = False
                    break
            if found:
                return True
        return False

    def _make_snippet(self, content: str, query_tokens: list[str], window: int = 60) -> str:
        """Extract a snippet around the first query term match."""
        content_lower = content.lower()
        best_pos = len(content)

        for token in query_tokens:
            pos = content_lower.find(token)
            if pos != -1 and pos < best_pos:
                best_pos = pos

        if best_pos == len(content):
            return content[:window * 2] + "..."

        start = max(0, best_pos - window)
        end = min(len(content), best_pos + window)
        snippet = content[start:end]

        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def stats(self) -> dict:
        """Engine statistics."""
        return {
            "documents": self.idx.doc_count,
            "vocabulary": self.idx.vocabulary_size(),
            "index_terms": len(self.idx.index),
        }


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    engine = SearchEngine()

    # Index some documents about data structures
    docs = [
        ("doc1", "Binary Trees",
         "A binary tree is a tree data structure where each node has at most two children. "
         "Binary search trees maintain sorted order, enabling O(log n) search. "
         "AVL trees and red-black trees are self-balancing binary search trees."),

        ("doc2", "Hash Tables",
         "A hash table maps keys to values using a hash function. "
         "Collisions are resolved by chaining or open addressing. "
         "Hash tables provide O(1) average lookup but O(n) worst case with many collisions. "
         "Python dictionaries and Java HashMaps are hash table implementations."),

        ("doc3", "Graph Algorithms",
         "Graphs represent relationships between objects. BFS explores level by level, "
         "while DFS goes deep before backtracking. Dijkstra finds shortest paths in "
         "weighted graphs. Topological sort orders directed acyclic graphs."),

        ("doc4", "Sorting Algorithms",
         "Merge sort divides and conquers in O(n log n) guaranteed. Quicksort is "
         "O(n log n) average but O(n^2) worst case. Heap sort uses a binary heap "
         "for in-place O(n log n) sorting. Comparison sorts cannot beat O(n log n)."),

        ("doc5", "Tree Balancing",
         "Self-balancing trees prevent degradation to O(n) linked lists. "
         "AVL trees maintain strict balance with rotations after every insert. "
         "Red-black trees allow slight imbalance for faster inserts. "
         "B-trees balance for disk I/O, not memory — each node fits a disk page."),

        ("doc6", "Dynamic Programming",
         "Dynamic programming solves problems by breaking them into overlapping "
         "subproblems. The key insight: if you've solved a subproblem before, "
         "don't solve it again — cache the result. Memoization (top-down) and "
         "tabulation (bottom-up) are the two DP approaches."),

        ("doc7", "Tries and Text Search",
         "A trie stores strings character by character in a tree structure. "
         "Autocomplete systems use tries for prefix matching. Suffix arrays "
         "enable fast substring search. Inverted indexes power search engines "
         "by mapping terms to documents containing them."),
    ]

    print("=" * 70)
    print("FULL-TEXT SEARCH ENGINE — Trie + Inverted Index + TF-IDF")
    print("=" * 70)

    print("\n📄 Indexing documents...")
    for doc_id, title, content in docs:
        engine.index_document(doc_id, title, content)
    print(f"   Stats: {engine.stats()}")

    # ── TF-IDF Ranked Search ──
    print("\n" + "─" * 70)
    print("🔍 TF-IDF Ranked Search: 'binary search tree'")
    print("─" * 70)
    results = engine.search("binary search tree")
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r.doc_id}] {r.title} (score: {r.score})")
        print(f"     {r.snippet}")

    # ── Boolean AND ──
    print("\n" + "─" * 70)
    print("🔍 Boolean AND: 'sort heap'")
    print("─" * 70)
    and_results = engine.boolean_and("sort heap")
    print(f"  Documents containing BOTH terms: {and_results}")

    # ── Boolean OR ──
    print("\n" + "─" * 70)
    print("🔍 Boolean OR: 'trie suffix'")
    print("─" * 70)
    or_results = engine.boolean_or("trie suffix")
    print(f"  Documents containing EITHER term: {or_results}")

    # ── Phrase Search ──
    print("\n" + "─" * 70)
    print("🔍 Phrase Search: 'binary search tree'")
    print("─" * 70)
    phrase_results = engine.phrase_search("binary search tree")
    print(f"  Documents with exact phrase: {phrase_results}")

    # ── Autocomplete ──
    print("\n" + "─" * 70)
    print("🔍 Autocomplete: 'sor'")
    print("─" * 70)
    suggestions = engine.suggest("sor")
    print(f"  Suggestions: {suggestions}")

    print("\n" + "─" * 70)
    print("🔍 Autocomplete: 'tre'")
    print("─" * 70)
    suggestions = engine.suggest("tre")
    print(f"  Suggestions: {suggestions}")

    # ── IDF Analysis ──
    print("\n" + "─" * 70)
    print("📊 IDF Analysis — which terms are most informative?")
    print("─" * 70)
    sample_terms = ["tree", "sort", "hash", "binary", "trie", "dynamic", "graph"]
    idf_scores = [(t, engine.idx.idf(t)) for t in sample_terms]
    idf_scores.sort(key=lambda x: -x[1])
    for term, idf in idf_scores:
        df = len(engine.idx.get_postings(term))
        print(f"  {term:12s}  df={df}  idf={idf:.3f}")

    print("\n✅ Full-text search engine operational")
