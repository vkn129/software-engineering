# Day 53: Tries (Prefix Trees) — Why Autocomplete is O(k)

## Why This Exists

Hash tables give O(1) lookup by exact key. BSTs give O(log n) lookup with ordering. But what if you need to find **all keys that start with a given prefix**? Hash tables can't do it (hashing destroys prefix relationships). BSTs can do it in O(log n + m) where m = matches, but there's a better structure.

A **trie** (from re**trie**val) stores keys character by character along tree edges. Every node represents a prefix. To find all keys with prefix "app", walk down a→p→p and return everything below. The lookup time is O(k) where k = length of the search key — **independent of how many keys are stored**.

This is not a theoretical curiosity. Tries power:
- **Autocomplete**: Phone keyboards, search bars, IDE code completion
- **Spell checkers**: Is "hte" close to any dictionary word?
- **IP routing**: Longest prefix match on 32-bit addresses
- **Genome search**: Find all DNA sequences starting with "ACGT..."
- **Dictionary compression**: LZW algorithm uses a trie

The key trade-off: tries use more memory than hash tables (one node per character in the worst case) but enable prefix operations that hash tables fundamentally cannot.

## Theory (40 min)

### Structure

```
Words: apple, app, apt, bat, bar

Root
├── a
│   ├── p
│   │   ├── p [end]
│   │   │   └── l
│   │   │       └── e [end]
│   │   └── t [end]
│
└── b
    └── a
        ├── t [end]
        └── r [end]
```

Each path from root to an `[end]` node spells out a stored word.

### Complexity

| Operation | Time | Why |
|-----------|------|-----|
| insert(key) | O(k) | Walk/create k nodes |
| search(key) | O(k) | Walk k nodes |
| starts_with(prefix) | O(p + m) | Walk p nodes, collect m matches |
| delete(key) | O(k) | Walk + cleanup empty branches |

Where k = key length, p = prefix length, m = number of matches.

Space: O(ALPHABET_SIZE × N × k) worst case, where N = number of keys. In practice, shared prefixes compress this significantly.

### TrieNode Design

Two common implementations for children:
1. **Dictionary** (`dict`): Flexible alphabet, space-efficient for sparse nodes
2. **Array** (`[None] * 26`): Fixed alphabet, O(1) child lookup, cache-friendly

## Practice (20 min)

See `practice.py` — 6 exercises from basic operations to autocomplete with ranking.

## Daily Project

`trie.py` implements a full Trie with insert, search, prefix search, delete, autocomplete, and longest common prefix.

## Checkpoint Questions

1. Why can't hash tables support prefix queries efficiently?
2. What's the worst-case space complexity of a trie with n keys of average length k?
3. When would you use an array-based trie node vs. a dict-based one?
4. How does a trie relate to a DFA (deterministic finite automaton)?
5. Why is trie lookup O(k) independent of the number of stored keys?
6. How would you implement a spell-checker with edit distance 1 using a trie?
