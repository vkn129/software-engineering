# Day 143: Regex Engine via Thompson Construction

## Why It Matters

Most regex engines you've used (PCRE, Python's `re`, JavaScript) are
backtracking matchers — exponential worst case (`a?^n a^n` against `a^n`
trips them). Thompson's 1968 construction builds an NFA, then simulates it
with **all active states in parallel**. Worst case: O(n * m), n = input,
m = regex size. No catastrophic backtracking, ever.

This is how grep, awk, RE2, and Go's `regexp` work. Russ Cox's article
("Regular Expression Matching Can Be Simple And Fast") is the canonical
exposition.

## Operators Supported

- Concatenation: `ab` matches "ab"
- Alternation:   `a|b` matches "a" or "b"
- Kleene star:   `a*` matches zero or more "a"
- Optional:      `a?` matches "" or "a"
- Grouping:      `(...)`

## Pipeline

```
regex string  --shunting-yard-->  postfix tokens
postfix       --Thompson-->        NFA (states + epsilon edges)
NFA + input   --simulate-->        match / no match
```

### Step 1: Insert Concat Operator

Standard infix regex has implicit concatenation: `ab` really means `a.b` for
some explicit operator `.`. We pre-process the regex to insert `.` (here we
use `\x08` as sentinel to avoid clashing with literal '.').

### Step 2: Shunting Yard -> Postfix

Operator precedence (low to high): `|` < concat < `?` = `*`. Unary `*`/`?`
are post-fix, others are infix. Standard Dijkstra shunting yard produces
postfix.

### Step 3: Thompson's Construction

Each subexpression builds a small NFA fragment:

- **literal c**: state `--c--> state`
- **concat A.B**: A.out -> B.in (link epsilon)
- **alt A|B**: new start --eps--> A.in and B.in; A.out and B.out --eps--> new out
- **star A***: new start --eps--> A.in and out; A.out --eps--> A.in and out
- **? A?**: new start --eps--> A.in and out; A.out --eps--> out

Maintain a stack of fragments; pop & combine per postfix token.

### Step 4: Simulation

Run two sets of active states: `current` and `next`. For each input char:

```
for state in current:
    for next_state via char-edge labeled c:
        next.add(next_state via epsilon-closure)
current, next = epsilon_closure(next), set()
```

Epsilon closure: BFS over eps-edges from a state set. Accept if a final
state is in `current` after consuming all input.

## Complexity

| Phase     | Time          | Space            |
|-----------|---------------|------------------|
| Parse     | O(m)          | O(m)             |
| Build NFA | O(m)          | O(m) states      |
| Match     | O(n * m)      | O(m) state set   |

## Failure Modes

- **Backtracking traps**: do NOT do `if state.next.match(text[i:]): ...` —
  that's backtracking. Use the active-set simulation.
- **Epsilon cycle**: A* over an A that already matches empty (e.g., `(a?)*`)
  can loop in epsilon closure if you re-add states. Use a visited set per
  closure call.
- **Anchors, character classes, backreferences**: not supported by Thompson
  NFAs at all (backrefs make matching NP-hard). Real engines add features on
  top.
- **Unicode**: same as always — match on codepoints, or grapheme clusters?

## Checkpoint Questions

1. Why is Thompson's matcher O(n*m) but PCRE can be exponential?
2. What does each operator's Thompson fragment look like?
3. Why must epsilon closure use a visited set?
4. Can Thompson NFAs handle `(a+)+a` without blowing up? Try `a^30 b`.
5. Why are backreferences incompatible with this approach?
6. How would you add `+` to the operator set?
