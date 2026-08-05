# Day 175: NP-Completeness & Reductions

## Why It Matters

Every day so far has answered "how do I solve this fast?". This one answers a
different question: **when should I stop looking?**

Day 176 opens with "Some problems are NP-hard — no polynomial algorithm is known
and none is believed to exist" and then spends the day on approximation
algorithms. That sentence is doing enormous work. This day earns it.

The payoff is practical, not philosophical. When a problem lands on your desk:

- If you can **reduce a known NP-complete problem to it**, you have a proof that
  nobody has ever found a polynomial algorithm for it. Stop optimising. Start
  approximating (day 176), or restrict the input, or accept exponential time on
  small instances.
- If you can **reduce it to a problem you can already solve**, you are done —
  reductions are a solving technique, not only a hardness technique. Day 093
  reduced bipartite matching to max-flow. Same tool, opposite direction.

Reductions are the most reusable idea in this curriculum. You will use them to
solve problems far more often than to prove anything hard.

## The Vocabulary, Minimally

- **Decision problem** — a question with a yes/no answer. "Is there a clique of
  size >= k?", not "what is the largest clique?". The theory is built on
  decision problems because yes/no makes the definitions clean; the optimisation
  version is at most a `log n` factor harder (binary search on k).
- **P** — decidable in polynomial time.
- **NP** — a *yes* answer has a **certificate** checkable in polynomial time.
  Not "solvable by a nondeterministic machine" in any way you need to picture;
  just: someone hands you the answer, and you can check it fast.
- **NP-hard** — at least as hard as everything in NP. Formally: every problem in
  NP reduces to it in polynomial time.
- **NP-complete** — in NP *and* NP-hard. The hardest problems that are still
  checkable.

The certificate idea is the one that matters operationally. For SAT the
certificate is an assignment, and `verify_sat` checks it in `O(total literals)`.
For clique it is the vertex set. Finding the certificate looks exponential;
checking it is linear. **That gap is the entire subject.**

## What A Reduction Actually Is

A polynomial-time reduction `A ≤p B` is a function `f`, computable in polynomial
time, with:

```
x is a YES instance of A   <=>   f(x) is a YES instance of B
```

Read the `<=>` carefully. **Both directions are required.** A function that only
maps yes to yes proves nothing — the constant function sending everything to a
trivially-satisfiable instance does that.

The practical consequence, and the thing this day's code enforces: a reduction
must carry **certificates in both directions**.

- Forward: a solution to `x` must produce a solution to `f(x)`.
- Backward: a solution to `f(x)` must produce a solution to `x`.

If you cannot write both mapping functions, you do not have a reduction — you
have a hunch. `np_completeness.py` implements every certificate map explicitly
and asserts round-trips on small instances. That is not extra rigour; it is the
minimum bar.

### Direction Confusion — The Classic Mistake

To prove **B is hard**, reduce a known-hard **A to B** (`A ≤p B`): "if I could
solve B fast, I could solve A fast — but A is hard, contradiction."

Reducing B to A proves nothing about B's hardness. It proves B is *easy* (if A
is). Get the arrow backwards and you have proven the opposite of your claim.

Mnemonic: **the known-hard problem goes on the left.**

## The Chain

```
    SAT  (Cook-Levin: NP-complete, assumed here)
     |  clause padding / chaining
     v
   3-SAT
     |  literal-compatibility graph
     v
   CLIQUE
     |  complement the graph
     v
 VERTEX COVER
     |  complement the set
     v
INDEPENDENT SET
```

Each arrow is `≤p`, so everything below SAT inherits NP-hardness from it. All
five are in NP (certificates are assignments or vertex sets), so all five are
**NP-complete**.

### Step 0 — SAT Is NP-Complete (Cook-Levin, 1971)

Assumed, not proved. The proof encodes an arbitrary polynomial-time verifier's
computation as a boolean formula — a beautiful construction, and a long one. It
is the only place in the subject where anything is proved from scratch; every
other NP-completeness result in the literature is a chain of reductions back to
this one.

Day 087 already gave the contrast that makes SAT's hardness vivid: **2-SAT is
solvable in `O(V+E)`** via strongly connected components
(`day-087/README.md:99` — "This gives an O(V + E) SAT solver for 2-SAT —
remarkable since 3-SAT is NP-complete"). Two literals per clause: linear time.
Three literals per clause: NP-complete. The cliff is that sharp.

### Step 1 — SAT ≤p 3-SAT

Make every clause exactly three literals.

- **1 literal** `(l)` → two fresh variables `y1, y2`, emit all four clauses
  `(l, ±y1, ±y2)`. Whatever `y1, y2` are, one clause forces `l`.
- **2 literals** `(l1, l2)` → one fresh `y`: `(l1, l2, y)`, `(l1, l2, ¬y)`.
- **3 literals** → unchanged.
- **k > 3 literals** `(l1, ..., lk)` → chain with `k-3` fresh variables:

```
(l1, l2, y1)
(¬y1, l3, y2)
(¬y2, l4, y3)
...
(¬y_{k-3}, l_{k-1}, l_k)
```

**Why the chain works, both ways.** The `y` variables act as a carry. If some
`l_t` is true, set `y_1..y_{t-2}` true and the rest false — every clause is
satisfied. Conversely, if *no* `l_t` is true, the first clause forces `y_1`
true, which forces `y_2` true, and so on down the chain; the last clause
`(¬y_{k-3}, l_{k-1}, l_k)` then has all three literals false. Unsatisfiable.
The fresh variables cannot rescue an unsatisfiable clause — which is exactly the
`⟸` half of the equivalence.

Size: `O(L)` for `L` total literals. Backward certificate map: **restrict the
assignment to the original variables** — the simplest possible map, which is why
this is the reduction to learn first.

### Step 2 — 3-SAT ≤p CLIQUE

The one where something interesting happens.

Given `m` clauses, build a graph:

- **Vertex** for every (clause, literal) pair — `3m` vertices, in `m` triples.
- **Edge** between two vertices iff they are in **different clauses** *and*
  their literals are **not complementary** (not `x` and `¬x`).

Then: **the formula is satisfiable ⟺ the graph has a clique of size `m`.**

- **(⟹)** Take a satisfying assignment. Pick one true literal per clause. No two
  are complementary (both are true), and they sit in different clauses, so all
  pairs are adjacent: a clique of size `m`.
- **(⟸)** Take a clique of size `m`. No edge joins two vertices of the same
  clause, so the clique has exactly one vertex per clause. No two of its
  literals are complementary, so setting all of them true is consistent. Every
  clause then has a true literal. (Variables appearing in no chosen literal go
  anywhere.)

Both directions are constructive, which is why `np_completeness.py` can map a
clique back to an assignment and re-verify it against the original formula.

Notice what the graph is doing: **edges encode compatibility**, and a clique is a
set of pairwise-compatible choices. That is the reusable pattern.

### Step 3 — CLIQUE ≤p VERTEX COVER

Pure complementation, near-trivial once seen.

> `C` is a clique of size `k` in `G`  ⟺  `V \ C` is a vertex cover of size
> `n - k` in the **complement** graph `Ḡ`.

Why: an edge `(u,v)` is in `Ḡ` exactly when it is absent from `G`. `C` being a
clique in `G` means no such pair lies inside `C` — i.e. every edge of `Ḡ` has an
endpoint outside `C`, which is the definition of `V \ C` being a cover.

Certificate maps both ways: set complement. Involutive, so the round-trip is the
identity.

### Step 4 — VERTEX COVER ≤p INDEPENDENT SET

Same graph, no transformation at all:

> `S` is a vertex cover of `G`  ⟺  `V \ S` is an independent set of `G`.

If `S` covers every edge, no edge has both endpoints outside `S`, so `V \ S` is
independent — and conversely. Minimum vertex cover and maximum independent set
are literally the same problem, read twice.

### Why The Chain Closes

Steps 3 and 4 compose to: independent set of size `k` in `Ḡ` ⟺ clique of size
`k` in `G`. The chain returns to where it started. Worth noticing, because it
tells you the *real* content is in step 2. Steps 3 and 4 are bookkeeping; the
3-SAT-to-clique graph is where logic becomes combinatorics.

## Where These Problems Are Easy

NP-completeness is a statement about the **general** case. Restrict the input and
the cliff often disappears — and this curriculum has already crossed three such
bridges:

| Problem | Hard in general | Easy when... | Where |
|---|---|---|---|
| SAT | 3+ literals per clause | 2 literals per clause: `O(V+E)` via SCC | `day-087/scc.py:176` |
| Vertex cover | any graph | bipartite: König, `= max matching` | `day-089/README.md:60`, `day-092/practice.py:189` |
| Independent set | any graph | bipartite: `n - max matching` | `day-092/practice.py:204` |
| Clique | any graph | planar (max clique <= 4), interval graphs | |

So "this is NP-complete" is never the end of the analysis. The next question is
always: *what does my actual input look like?* Real inputs are frequently
bipartite, planar, bounded-treewidth, or just small — and then a polynomial
algorithm exists and you should use it.

## What NP-Completeness Does Not Mean

1. **Not "no algorithm exists".** Brute force always exists. The claim is only
   that no *polynomial* one is known.
2. **Not "every instance is hard".** SAT solvers routinely dispatch industrial
   instances with millions of variables. Hardness is worst-case. Random 3-SAT is
   easy except near a clause/variable ratio of ~4.26.
3. **Not "P ≠ NP".** That is open. All five problems here become polynomial if
   P = NP. The honest statement is "no polynomial algorithm is *known*, and one
   would collapse the whole class".
4. **Not "approximation is hopeless".** Vertex cover has a clean 2-approximation
   (day 176). Independent set — the *same problem complemented* — has no
   constant-factor approximation unless P = NP. Complementation preserves exact
   equivalence and destroys approximation ratios. That single fact is the bridge
   into day 176's warning that "reduction != approximation".

## Complexity

| Operation | Cost | Notes |
|---|---|---|
| `verify_sat` | `O(L)` | the certificate check — this is why SAT ∈ NP |
| `brute_force_sat` | `O(2^n · L)` | the thing hardness is about |
| `sat_to_3sat` | `O(L)`, adds `< L` variables | polynomial, as required |
| `three_sat_to_clique` | `O(m^2)` edges, `3m` vertices | |
| `clique_to_vertex_cover` | `O(n^2)` | builds the complement graph |
| `vertex_cover_to_independent_set` | `O(n)` | set complement, same graph |
| `max_clique_bruteforce` | `O(2^n · n^2)` | reference oracle only, `n <= ~15` |
| Certificate map, any step | `O(instance size)` | must be polynomial or the reduction is void |

A reduction is only useful if `f` itself is polynomial. An exponential-time
"reduction" proves nothing — you could have solved the original problem in that
budget.

## Failure Modes

1. **Reducing in the wrong direction.** To show B hard, reduce known-hard A
   **to** B. Reducing B to A proves B is easy. The single most common error in
   the subject.

2. **Proving only one direction.** `x YES ⟹ f(x) YES` is not a reduction. You
   must also show `f(x) YES ⟹ x YES`, which is where a broken construction gets
   caught — usually because fresh variables let the target instance be satisfied
   when the source is not.

3. **Forgetting to prove membership in NP.** NP-hard + in NP = NP-complete. Skip
   the membership half and you may have something *harder* than NP-complete (the
   halting problem is NP-hard and not in NP).

4. **A reduction that is not polynomial.** Blowing up the instance exponentially
   voids the argument. Check the output size of `f` explicitly.

5. **Confusing the decision and optimisation versions.** "Is there a clique of
   size >= k" is in NP. "Is `k` the *maximum* clique size" is not obviously in NP
   — a certificate for "no larger clique exists" is not a vertex set. Read the
   quantifiers.

6. **Assuming NP-hard means "give up".** Options remain: exact exponential
   algorithms on small `n`, parameterised algorithms (vertex cover is FPT in `k`:
   `O(2^k · n)`), ILP/SAT solvers, restricted input classes, or approximation
   (day 176). "NP-complete" is a routing decision, not a wall.

7. **Assuming a reduction preserves approximability.** It does not. Vertex cover
   ↔ independent set are the same problem under complementation, yet one has a
   2-approximation and the other has none. Day 176 names this directly
   (`day-176/README.md:116`). Approximation-preserving reductions (L-reductions)
   are a separate, stricter tool.

8. **Trusting a chain you never tested.** Four composed reductions with
   hand-derived index arithmetic is exactly the shape of code that is quietly
   wrong. Round-trip certificates on small instances against a brute-force
   oracle, every time — that is what `np_completeness.py` does, and what makes
   its claims believable.

## Checkpoint Questions

1. Define NP using certificates, without mentioning nondeterministic machines.
   What is the certificate for CLIQUE, and how fast can you check it?
2. You want to prove problem `B` is NP-hard. Do you reduce SAT to `B`, or `B` to
   SAT? Explain what the wrong direction would actually prove.
3. In the SAT → 3-SAT chain construction, show that if no original literal `l_t`
   is true then the chain forces every `y_i` true and the final clause fails.
   Why is this the direction that matters?
4. In the 3-SAT → clique graph, why is there never an edge between two vertices
   from the same clause? Which half of the equivalence does that fact prove?
5. Given a clique of size `m` in that graph, construct a satisfying assignment.
   What do you do with variables appearing in no chosen literal?
6. Prove: `C` is a clique in `G` ⟺ `V \ C` is a vertex cover in `Ḡ`. Then explain
   why the CLIQUE → VC → IS chain returns to CLIQUE.
7. 2-SAT is `O(V+E)` (day 087) and 3-SAT is NP-complete. What breaks in the SCC
   algorithm when a clause has three literals?
8. Vertex cover is NP-complete in general but polynomial on bipartite graphs via
   König (day 092). Does that contradict NP-completeness? Explain precisely.
9. Vertex cover has a 2-approximation; independent set has no constant-factor
   approximation unless P = NP. They are the same problem complemented. Resolve
   the apparent paradox — what does complementation do to a ratio?
10. Your input is 40 vertices and you need an exact maximum independent set —
    NP-complete. What do you actually do? Give two concrete strategies and the
    condition under which each is right.
