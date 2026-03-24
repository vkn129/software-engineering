"""
Day 53 Practice: Trie Exercises
================================
Run: python practice.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from trie import Trie


# ─── Exercise 1: Word Search in Grid ───────────────────────────────
#
# Given a 2D board of characters and a list of words, find all words
# that exist in the board. A word is formed by adjacent cells (up/down/
# left/right), each cell used at most once per word.
#
# Approach: build a trie of all words. DFS from each cell, checking
# the trie to prune paths that can't form any word.
#
# Example:
#   board = [['o','a','n'], ['e','t','a'], ['i','h','k']]
#   words = ["oath", "eat", "eta", "oat"]
#   → ["oath", "eat", "eta"]

def word_search(board, words):
    # TODO: return list of found words
    pass


# ─── Exercise 2: Autocomplete with Ranking ─────────────────────────
#
# Build an autocomplete system where each word has a frequency score.
# When querying a prefix, return the top-k words by frequency.
#
# Example:
#   insert("apple", 5), insert("app", 3), insert("application", 1)
#   search("app", k=2) → ["apple", "app"]

class RankedAutocomplete:
    def __init__(self):
        # TODO: initialize
        pass

    def insert(self, word, frequency):
        # TODO: insert word with frequency
        pass

    def search(self, prefix, k=5):
        # TODO: return top-k words by frequency matching prefix
        pass


# ─── Exercise 3: Longest Common Prefix of Array ────────────────────
#
# Find the longest common prefix among all strings in an array.
# Use a trie: insert all strings, then walk down single-child path.
# Example: ["flower", "flow", "flight"] → "fl"

def longest_common_prefix(strs):
    # TODO: implement using a trie
    pass


# ─── Exercise 4: Replace Words with Roots ──────────────────────────
#
# Given a dictionary of root words and a sentence, replace each word
# in the sentence with its shortest root.
# Example: roots = ["cat", "bat", "rat"]
#          sentence = "the cattle was rattled by the battery"
#          → "the cat was rat by the bat"

def replace_words(roots, sentence):
    # TODO: implement
    pass


# ─── Exercise 5: Count Distinct Substrings ─────────────────────────
#
# Count the number of distinct substrings of a string using a trie.
# Insert all suffixes into a trie. The number of nodes = number of
# distinct substrings (+1 for empty string).
# Example: "abc" → substrings: a, ab, abc, b, bc, c → 6

def count_distinct_substrings(s):
    # TODO: return count of distinct non-empty substrings
    pass


# ─── Exercise 6: Map Sum (Prefix Sum) ──────────────────────────────
#
# Design a map where:
#   insert(key, val) — inserts/updates key with value
#   sum(prefix) — returns sum of values of all keys starting with prefix
#
# Example: insert("apple", 3), insert("app", 2), sum("ap") → 5

class MapSum:
    def __init__(self):
        # TODO: initialize
        pass

    def insert(self, key, val):
        # TODO: implement
        pass

    def sum_prefix(self, prefix):
        # TODO: return sum of all values with keys starting with prefix
        pass


# ════════════════════════════════════════════════════════════════════
# SOLUTIONS
# ════════════════════════════════════════════════════════════════════

def _sol_word_search(board, words):
    if not board or not board[0] or not words:
        return []

    trie = Trie()
    for w in words:
        trie.insert(w)

    rows, cols = len(board), len(board[0])
    found = set()

    def dfs(r, c, node, path):
        if r < 0 or r >= rows or c < 0 or c >= cols:
            return
        char = board[r][c]
        if char == '#' or char not in node.children:
            return

        node = node.children[char]
        path.append(char)

        if node.is_end:
            found.add(''.join(path))

        board[r][c] = '#'  # Mark visited
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            dfs(r + dr, c + dc, node, path)
        board[r][c] = char  # Unmark
        path.pop()

    for r in range(rows):
        for c in range(cols):
            dfs(r, c, trie.root, [])

    return sorted(found)


class _SolRankedAutocomplete:
    def __init__(self):
        self.trie = Trie()

    def insert(self, word, frequency):
        self.trie.insert(word, frequency)

    def search(self, prefix, k=5):
        node = self.trie._find_node(prefix)
        if node is None:
            return []
        results = []
        self._collect(node, list(prefix), results)
        results.sort(key=lambda x: -x[1])
        return [word for word, freq in results[:k]]

    def _collect(self, node, path, results):
        if node.is_end:
            results.append((''.join(path), node.value or 0))
        for char in sorted(node.children):
            path.append(char)
            self._collect(node.children[char], path, results)
            path.pop()


def _sol_longest_common_prefix(strs):
    if not strs:
        return ""
    trie = Trie()
    for s in strs:
        if not s:
            return ""
        trie.insert(s)
    return trie.longest_common_prefix()


def _sol_replace_words(roots, sentence):
    trie = Trie()
    for r in roots:
        trie.insert(r)

    words = sentence.split()
    result = []
    for word in words:
        # Find shortest root
        node = trie.root
        replaced = False
        for i, char in enumerate(word):
            if char not in node.children:
                break
            node = node.children[char]
            if node.is_end:
                result.append(word[:i + 1])
                replaced = True
                break
        if not replaced:
            result.append(word)

    return ' '.join(result)


def _sol_count_distinct_substrings(s):
    trie = Trie()
    count = 0
    for i in range(len(s)):
        node = trie.root
        for j in range(i, len(s)):
            char = s[j]
            if char not in node.children:
                node.children[char] = type(node)()
                count += 1
            node = node.children[char]
    return count


class _SolMapSum:
    def __init__(self):
        self.trie = Trie()
        self.map = {}

    def insert(self, key, val):
        self.map[key] = val
        self.trie.insert(key, val)

    def sum_prefix(self, prefix):
        node = self.trie._find_node(prefix)
        if node is None:
            return 0
        total = [0]

        def walk(n):
            if n.is_end:
                total[0] += (n.value or 0)
            for child in n.children.values():
                walk(child)

        walk(node)
        return total[0]


# ─── Test Runner ────────────────────────────────────────────────────

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            passed += 1
            print(f"  ✓ {name}")
        else:
            failed += 1
            print(f"  ✗ {name}: got {got}, expected {expected}")

    # Exercise 1
    print("\nExercise 1: Word Search")
    board = [['o', 'a', 'n'], ['e', 't', 'a'], ['i', 'h', 'k']]
    words = ["oath", "eat", "eta", "oat"]
    for fn in [word_search, _sol_word_search]:
        if fn is word_search and fn(board, words) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}", fn([row[:] for row in board], words), ["eat", "eta", "oath"])

    # Exercise 2
    print("\nExercise 2: Ranked Autocomplete")
    for Cls in [RankedAutocomplete, _SolRankedAutocomplete]:
        ac = Cls()
        if not hasattr(ac, 'insert'):
            print("  (skipped — not implemented)")
            break
        ac.insert("apple", 5)
        ac.insert("app", 3)
        ac.insert("application", 1)
        r = ac.search("app", 2)
        if r is None:
            print("  (skipped — not implemented)")
            break
        check(f"{Cls.__name__} top-2", r, ["apple", "app"])

    # Exercise 3
    print("\nExercise 3: Longest Common Prefix")
    for fn in [longest_common_prefix, _sol_longest_common_prefix]:
        if fn is longest_common_prefix and fn(["a"]) is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}(flower,flow,flight)", fn(["flower", "flow", "flight"]), "fl")
        check(f"{fn.__name__}(dog,racecar,car)", fn(["dog", "racecar", "car"]), "")

    # Exercise 4
    print("\nExercise 4: Replace Words")
    for fn in [replace_words, _sol_replace_words]:
        if fn is replace_words and fn(["a"], "a") is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}",
              fn(["cat", "bat", "rat"], "the cattle was rattled by the battery"),
              "the cat was rat by the bat")

    # Exercise 5
    print("\nExercise 5: Count Distinct Substrings")
    for fn in [count_distinct_substrings, _sol_count_distinct_substrings]:
        if fn is count_distinct_substrings and fn("a") is None:
            print("  (skipped — not implemented)")
            break
        check(f"{fn.__name__}('abc')", fn("abc"), 6)
        check(f"{fn.__name__}('aaa')", fn("aaa"), 3)

    # Exercise 6
    print("\nExercise 6: Map Sum")
    for Cls in [MapSum, _SolMapSum]:
        ms = Cls()
        if not hasattr(ms, 'insert'):
            print("  (skipped — not implemented)")
            break
        ms.insert("apple", 3)
        ms.insert("app", 2)
        r = ms.sum_prefix("ap")
        if r is None:
            print("  (skipped — not implemented)")
            break
        check(f"{Cls.__name__} sum('ap')", r, 5)
        check(f"{Cls.__name__} sum('apple')", ms.sum_prefix("apple"), 3)

    print(f"\n{'=' * 40}")
    print(f"Results: {passed} passed, {failed} failed")


if __name__ == "__main__":
    run_tests()
