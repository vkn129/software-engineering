# Day 139: Regular Expressions via Thompson NFA

## Why NFA-Based Regex Matters

Every popular regex engine in the world — PCRE, Perl, Python's `re`, Java,
JavaScript — uses **backtracking**. This makes them vulnerable to **ReDoS**
(Regular Expression Denial of Service): a single carefully-crafted input can
take exponential time.

Real outages caused by ReDoS:

- **Cloudflare 2019**: `.*(?:.*=.*)` against a long URL took 27 seconds per
  worker thread. Took down 23% of internet traffic for ~30 minutes.
- **Stack Overflow 2016**: a regex in their input sanitizer hung the site
  for 34 minutes.
- **Visa Inc. v. JPMorgan**: a regex DoS bug in fraud detection.

Thompson NFA-based regex (used by `grep`, RE2 from Google, `ripgrep`) is
**immune to ReDoS** — provably linear-time `O(nm)`. It trades back-references
(which require backtracking) for safety.

## The Theory

Three steps:

1. **Parse** regex into a syntax tree.
2. **Compile** to an NFA (Thompson's construction).
3. **Simulate** the NFA on the input — track all possible states simultaneously.

Each step is straightforward; together they give a linear-time matcher.

## Thompson's Construction

Build an NFA recursively, with the property that **every sub-NFA has exactly
one start and one accept state**.

- **Single char `c`**: start --c--> accept
- **Concatenation `AB`**: connect A.accept --ε--> B.start
- **Alternation `A|B`**: new start --ε--> A.start, --ε--> B.start;
  A.accept --ε--> new accept, B.accept --ε--> new accept
- **Star `A*`**: new start --ε--> A.start AND --ε--> new accept;
  A.accept --ε--> A.start AND --ε--> new accept
- **Plus `A+`**: A.accept --ε--> A.start, --ε--> new accept (one mandatory pass)
- **Optional `A?`**: new start --ε--> A.start AND --ε--> new accept

ε ("epsilon") transitions consume no input. Result: an NFA with O(m) states
(linear in regex length).

## Simulation (The Trick That Avoids Backtracking)

Maintain a **set of active states** at each input position. For each input
character, compute the next set in O(|states|) work. Never branch and
backtrack — always carry all possibilities forward in parallel.

```
def matches(nfa, text):
    states = epsilon_closure({nfa.start})
    for c in text:
        next_states = set()
        for s in states:
            for transition_char, target in s.transitions:
                if transition_char == c:
                    next_states.add(target)
        states = epsilon_closure(next_states)
    return nfa.accept in states
```

Each input character processes at most |states| = O(m) states.
Total: **O(nm)** — linear in text length, linear in regex length.

## Backtracking vs NFA Simulation

### Pathological Regex: `(a+)+$`

On input `"aaaaaaaaaa!"` (10 a's + bad char):

- **Backtracking** (Python's `re`): tries every partition of 10 a's into groups.
  Number of partitions = 2^9 = 512. With 30 a's: 2^29 ≈ 5×10^8. Hang.
- **NFA simulation**: O(n·m) = O(11·6) = 66 transitions. Instant.

This regex `(a+)+$` is **trivially equivalent** to `a+$` semantically — but
backtracking engines can't see that.

### Why Backtracking Wins (Sometimes)

Back-references (`\1`) and look-arounds make a language non-regular. NFA
simulation can't handle them. So:

- **Perl / Python / Java / PCRE**: support back-refs, use backtracking,
  pay the ReDoS price.
- **RE2 / Google / ripgrep**: forbid back-refs, use NFA, guaranteed linear time.

Production rule: if you accept user-supplied regex (e.g., search box in
an admin panel), **use RE2-equivalent**, not Python's `re`.

## Failure Modes

### 1. Catastrophic Backtracking (ReDoS)

Classic vulnerable patterns:

- `(a+)+$` — nested quantifiers
- `(a|a)*` — alternation with overlap
- `(a|ab)*c` — ambiguous alternation
- `(.*a){10,}` — repeated capturing of `.*`

Test your regex with: pick the prefix that can match, repeat it, then add
a char that forces fail. If runtime explodes, you have ReDoS.

### 2. Epsilon Closure Blowup

Naive epsilon closure that doesn't memoize can visit the same state
multiple times per closure call. Use BFS with a visited set: O(|states| + |epsilon edges|).

### 3. Anchors and Greedy/Lazy

Pure NFA simulation matches any substring (returns true if **any** position
in text reaches accept). Adding `^`/`$` anchors changes start/accept conditions.
Greedy vs lazy quantifiers don't change accept/reject — they only matter for
**capturing groups** (which require more state).

### 4. Memory: O(m) States, O(m^2) Edges Worst Case

For deeply nested expressions like `a*a*a*...a*`, the NFA has O(m) states
but O(m) edges per state in the worst case. Still polynomial space.

### 5. UTF-8

NFA over Unicode requires either:
- Transition on byte (handle multi-byte sequences explicitly), or
- Transition on code point (decode first, slower).

RE2 does both — fast path for ASCII, slow path for full Unicode.

## Implementation Sketch

```
Parse regex -> AST
AST -> NFA via Thompson's construction
NFA + text -> simulate via O(nm) state set tracking
```

Our implementation supports: literals, `.`, `*`, `+`, `?`, `|`, `(`, `)`.
No character classes (`[...]`), no anchors (`^`, `$`), no back-refs.

## Real-World: RE2 vs Python's `re`

```
Python re:    (a+)+$ on "a^30 !"  -> hangs (~minutes)
RE2 / NFA:    (a+)+$ on "a^30 !"  -> O(30) microseconds
```

RE2 is what powers Google search, BigQuery LIKE patterns, and `ripgrep`. The
linear-time guarantee matters when you process untrusted regex or untrusted
text at scale.

## Checkpoint Questions

1. Why does Thompson construction give an NFA with exactly 2m states for a
   regex of size m? (Sketch the counting argument.)
2. Show how `(a|ab)*c` causes catastrophic backtracking. Trace what happens
   on "abababx".
3. Why does NFA simulation give O(nm)? What invariant on |states| holds?
4. Convert the regex `a*b` into a Thompson NFA by hand. Draw states and
   transitions.
5. Why can't NFA simulation handle `(a*)\1` (i.e., back-reference)? What
   formal language class does that put you in?
6. ReDoS audit: scan a real codebase (your own or open-source) for the
   patterns `(.+)+`, `(.*)*`, `(.|.)*`. How many do you find? Are any
   user-input-driven?
