# Day 137: Aho-Corasick (Multi-Pattern Matching)

## Why Aho-Corasick Matters

KMP and Z search for **one** pattern. Real systems need to scan text against
**thousands** of patterns at once:

- **Antivirus engines**: ClamAV scans files against ~10^6 malware signatures
- **Network IDS**: Snort/Suricata match packet payloads against rule sets
- **Spam filters**: keyword-based classification against blocklists
- **Bioinformatics**: locate any of 10^4 motifs in a genome
- **Web crawlers**: detect any of N "bad words" in scraped pages
- **DLP (data loss prevention)**: scan documents for credit cards, SSNs, etc.

Running KMP independently for each pattern gives O(n·k) — for 10^6 patterns
on a 10^9 byte file, that's 10^15 operations = impossible. Aho-Corasick scans
the text **once**, O(n + total_pattern_length + matches).

## The Idea

Aho-Corasick = **trie of patterns** + **failure links** (KMP-style).

1. Insert all patterns into a trie. Each node represents a prefix of some pattern.
2. Build failure links: from each node v, a `fail[v]` pointer to the longest
   proper suffix of "string spelled to v" that is also a node in the trie.
3. Scan text: at each character, follow trie or failure links. Emit matches
   when a terminal node (end of some pattern) is reachable via fail chain.

Result: each text character causes O(1) amortized state transitions. Total:
**O(n + sum(|p|) + #matches)**.

## Trie Construction

```
patterns = ["he", "she", "his", "hers"]

           (root)
          /  |  \
         h   s
        / \  |
       e   i s
       |   | |
       r   s h
       |     |
       s     e
```

Each node has:
- `goto[c]`: child for character c (None if absent)
- `fail`: failure link (computed in step 2)
- `output`: list of patterns ending at this node

## Failure Link Construction (BFS)

For depth-1 nodes, `fail = root` always.

For deeper node u with parent p and edge character c:
```
candidate = fail[p]
while candidate is not root and c not in goto[candidate]:
    candidate = fail[candidate]
if c in goto[candidate] and goto[candidate][c] != u:
    fail[u] = goto[candidate][c]
else:
    fail[u] = root
```

Build via BFS to ensure parent fail-links exist when processing child. O(total
pattern length).

## Matching Phase

```
state = root
for each char c in text:
    while state != root and c not in goto[state]:
        state = fail[state]
    if c in goto[state]:
        state = goto[state][c]
    # Emit all patterns ending at state or any fail-chain ancestor.
    temp = state
    while temp != root:
        for pattern in output[temp]:
            emit(pattern, current_position)
        temp = fail[temp]   # walk dictionary suffix link
```

Optimization: precompute **dictionary suffix links** (`dict_link`) — skip
nodes with no output. Cuts the emit walk from O(state-depth) to
O(matches-at-this-position).

## Failure Modes

### 1. Memory Blowup

Trie nodes use a dict or array per node. For 10^6 patterns over 256-char
alphabet stored as arrays, that's 256 MB per million nodes. ClamAV moves
to **double-array tries** or **succinct** representations in production.

### 2. Unbounded Output at One Position

If all patterns are suffixes of each other (`a`, `ba`, `cba`, `dcba`, ...),
each text position can emit O(k) matches. The "match count" term in the
complexity dominates. Adversarial input can blow up output volume.

### 3. Confusing Failure vs Goto

The classic bug: in the match loop, do you check `fail[state]` before or
after consuming the next character? Off-by-one here silently misses patterns
near node boundaries.

### 4. Dynamic Updates

Adding patterns after the structure is built is **hard** — you'd have to
rebuild failure links across the affected subtree. Real systems batch
updates and rebuild periodically.

### 5. Case Sensitivity / Unicode

Naive Aho-Corasick assumes byte-level matching. For case-insensitive
matching, lowercase patterns and text BEFORE building. For Unicode, normalize
via NFC/NFD; mixing forms causes silent misses.

## Variants

### Aho-Corasick with Wildcards

Extend the automaton with `?` (single-char wildcard) by branching every node.
Memory grows exponentially in the number of wildcards — used only for short
patterns with few wildcards (network rules, not arbitrary regex).

### Suffix Automaton

A different beast: for searching multiple patterns against a **fixed text**,
build the suffix automaton of the text once, then each pattern query is O(|p|).
Aho-Corasick is the dual: fixed patterns, scan many texts.

### Commentz-Walter (Multi-Pattern Boyer-Moore)

Aho-Corasick is BFS-style — never skips ahead. Commentz-Walter incorporates
BM-like skip heuristics for sublinear scanning when patterns are long. Used
in `grep -F` for many patterns.

## Real-World Example: Snort IDS

A single Snort rule looks like:
```
alert tcp any any -> any 80 (content: "GET /admin/"; content: "id=1' OR";)
```

Snort compiles all rule `content:` strings into one Aho-Corasick automaton.
Each packet payload is scanned once at line rate (10 Gbps+). Without
Aho-Corasick, packet inspection would require thousands of independent KMP
scans per packet = infeasible at network speeds.

## Complexity Summary

| Operation | Cost |
|-----------|------|
| Trie insert (all patterns) | O(sum |p_i|) |
| Failure link build (BFS) | O(sum |p_i| · |alphabet|) or O(sum |p_i|) with dict |
| Match phase | O(n + #matches) |

The `#matches` term is unavoidable — if all your patterns match at the same
position, the algorithm must report them all.

## Checkpoint Questions

1. Walk through failure link construction for patterns ["he", "she", "his", "hers"].
   What are `fail[h-e]`, `fail[s-h-e]`, `fail[h-e-r-s]`?
2. Why does the inner `while state != root` in the match phase terminate? What
   bounds the total work across the entire text?
3. If you add patterns one at a time, why is incremental rebuild expensive?
4. Show a pattern set + text where the **output emission** dominates the
   running time. What does this say about complexity bounds?
5. How would you adapt Aho-Corasick for case-insensitive matching with minimum
   memory overhead?
6. Compare worst-case memory for storing 10^6 patterns of average length 20:
   trie with dict children vs trie with array children (alphabet 256).
