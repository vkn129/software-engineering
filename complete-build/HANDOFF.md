# complete-build — Handoff

**Written:** 2026-08-05. **Status:** decision recorded, nothing built yet.

This file exists because Claude Code deletes session transcripts after 30 days and this
project lost ~3 months of session history that way. Everything needed to resume is here.
Do not rely on a transcript existing.

---

## 1. The decision: what `complete-build` is

`complete-build/` is **a lens over the existing curriculum, not a second curriculum.**

It holds the **dependency graph, the visual layer, and the topic classification** across the
full computing ecosystem. It does **not** hold a copy of any content that already exists.

The failure this design exists to prevent: two parallel curricula that drift apart, so neither
is trustworthy and work gets lost between them.

---

## 2. The DSA question — settled

Three options were considered for `01-dsa` (180 days, 157 practice suites passing):

| Option | Verdict |
|---|---|
| **Copy** into `complete-build/01-dsa/` | **Never.** Two physical copies drift on first edit. This is the exact "mix up or lose" failure to avoid. |
| **Rewrite** to satisfy the doctrine | **Waste.** The existing days already do why-first — every README has `## Why It Matters` and `## Failure Modes`, and the root `CLAUDE.md` already mandates connecting to physics/mathematics/economics. Re-authoring 180 working days buys very little. |
| **Reference** | **Chosen.** `01-dsa/` stays exactly where it is. It is now committed at that path (commit `f112540`); moving it would rewrite 300+ paths in git for no benefit. |

### What `complete-build/01-dsa/` actually contains

No algorithm implementations. Six meta-layers that do not exist anywhere today — each one
*additive over* the existing content rather than a replacement for it:

| File | Purpose | Why it isn't just a hyperlink |
|---|---|---|
| `INDEX.md` | Entry point. First line must state: *no implementations here; the curriculum lives at `../../01-dsa/`* | Stops the copy confusion before it starts |
| `dag-node.md` | Where DSA sits in the ecosystem graph — what it **depends on** (discrete math, memory hierarchy), what **depends on it** (databases, distributed systems, AI infra) | The doctrine requires a dependency graph. A day-1-to-180 list encodes none of this |
| `classification.md` | All 180 days labelled **Fundamental / Derived / Premature** | Today every day looks equally required. They are not |
| `visuals/` | Diagrams the existing days lack: the pressure that forced each design, memory/latency drawn to true proportion, systems shown mid-break rather than at rest | Zero visual artifacts exist today. This is the single biggest gap |
| `coverage-map.md` | Which of the ecosystem layers each day actually touches | Surfaces days touching fewer than 3 layers — the doctrine's own test for "premature" |
| `absence-audit.md` | Which days answer *"what broke before this existed"* vs only *"why it matters"* | Audit first, then supplement the weak ones. Do not rewrite blindly |

Same pattern applies to the other sections, except they have no content to reference yet —
so for `02-systems` … `projects`, `complete-build` is where the content itself will live.

---

## 3. Current repo state (verified 2026-08-05)

- `01-dsa/`: **180/180 day dirs populated.** Practice suites: **157 PASS**, 14 FAIL, 8 ERROR,
  1 TIMEOUT. All pushed — `origin/main` at `f112540`.
- The 23 non-passing days are **not defects.** See the project memory note
  `project_dsa_curriculum_contracts` — two practice-file conventions coexist; ~85 older days
  are learner-TODO files with no `_sol_` fallback and fail by design until the learner
  implements them. **Do not "fix" them.**
- `02-systems`, `03-databases`, `04-architecture`, `05-production`, `experiments`, `projects`:
  ~16 seed files total, unverified, essentially unbuilt.
- `complete-build/`: 7 empty dirs. This file is its first content.

---

## 4. Two hard-won constraints — read before authoring anything

Discovered the expensive way while filling the 19 DSA gaps. A plan that ignored them had
**10 of 19 topic assignments wrong.**

**(a) The curriculum forward-reserves future day numbers.** An existing README will promise
that a later, unwritten day covers topic X. These are binding. Confirmed:
`day-095/README.md:162` → Day 97 = 2-SAT; `day-092/README.md:100` and `day-096/README.md:125`
→ Day 98 = task-assigner capstone; `day-136/README.md:129` → Day 140 = Manacher;
`day-160/README.md:68` → Day 161+ = parallel merge.

**(b) Duplicate-checking must cover `.py` files and the whole curriculum, not adjacent
READMEs.** Real collisions sat up to 90 days away and usually lived only in code — quickselect
and BFPRT in `day-100/quicksort_deep.py` and `day-061`, LRU/LFU in `day-070/cache.py:146`,
`manacher()` already in `day-120/palindrome_dp.py:107`, interval partitioning in
`day-127/greedy_intro.py:73`, matrix exponentiation in `day-150/fast_exponentiation.py:84`.

---

## 5. The doctrine

Two skill packages, currently **only in `~/Downloads/`** as zip archives misnamed `.md`.
Extracted copies at `~/Downloads/_skill_extract/`.

**Install them to `~/.claude/skills/<name>/SKILL.md` before the next session** — they are
skills, and they belong there, not in Downloads.

- `systems-inventor-mindset` — the cognitive layer. Friction is data, not noise. Reason from
  constraints, not capabilities. Design to be correctable, not correct. Extract the principle,
  not the fix.
- `distinguished-engineer-mentor` — extends it across 16 ecosystem layers. Why-first,
  absence-based, counterfactual. Never "what is X". Label every topic
  Fundamental/Derived/Premature. **"Use dependency graphs rather than linear syllabi."**
  Projects are experiments against reality, designed to break.

**The learner is a visual learner.** Diagrams are a requirement, not decoration. Mermaid in
Markdown renders natively on GitHub — no toolchain needed.

---

## 6. The one open question — needs a human answer first

**Breadth across all 16 ecosystem layers, or depth through one vertical slice end-to-end?**

The doctrine's own "Premature" rule argues for depth: one slice traced from physics through
hardware, OS, data structures, algorithms, database, distributed system, and cost model
teaches more than sixteen shallow starts. But this changes the entire shape of the build and
is the learner's call, not the agent's.

**Do not start authoring until this is answered.**

---

## 7. Known issues, deliberately not fixed

- `01-dsa/day-125/dp_optimization.py:165-244` (`building_bridges_min_cost`) — the docstring
  recurrence, the code at `:236`, and the naive comparator at `:264` describe three different
  problems. Its own demo is self-consistent and passes, so it is not breaking anything.
- `01-dsa/day-099/comparison_sorts.py:12` and `01-dsa/day-100/quicksort_deep.py:12` both call
  `sys.setrecursionlimit(10**6)` at module scope, mutating the interpreter process-wide for
  anything that imports them. Will bite any future cross-day harness.
- `.claude/worktrees/` holds 4 leftover agent worktrees (~35MB). Now gitignored. Remove with
  `git worktree remove` when convenient — `rm` is blocked by policy for the agent.
- `day-097` judgment call: `day-095:162` promised Day 97 = 2-SAT, but `day-087` already ships
  a complete Tarjan 2-SAT solver, so Day 97 was given Min-Cost Max-Flow with a README note
  pointing at day-087. Reversible cheaply if strict promise-keeping is preferred.
