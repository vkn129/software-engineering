# Experiments

Quick, focused investigations. Each experiment answers **one question** about how a system actually behaves — usually by measuring it on this machine rather than trusting a textbook number.

Not curriculum-bound. Not progressive. Cross-cuts the 01-05 layers. If you finished a topic and thought *"but does that actually happen on real hardware?"* — that's an experiment.

## Why Experiments Exist Separately From `01-dsa/` etc.

The numbered layers are a **learning path**: they teach concepts in dependency order. Experiments are a **lab bench**: you wander in with a hypothesis and walk out with a number.

| Layer dirs (01-05) | experiments/ |
|---|---|
| Curriculum-driven | Curiosity-driven |
| One concept per day | One question per folder |
| Builds on prior days | Standalone |
| README explains *what was learned* | README states a hypothesis, results.md reports the answer |

## Folder Structure Convention

Every experiment lives in its own folder:

```
experiments/
  <kebab-case-experiment-name>/
    README.md           # hypothesis, why it matters, how to run
    <script>            # runnable, stdlib only unless noted
    results.md          # actual measurements on this machine (filled in after running)
```

Optional additions: `data/`, `plots/`, `notes.md`.

## Naming Rules

- Kebab-case folders: `cache-line-size-detection`, not `CacheLineSize` or `cache_line_size`.
- Verb-object or topic-question: `python-vs-c-sort-benchmark`, `tcp-nagle-vs-nodelay-latency`.
- No dates in folder names — git history is the timeline.

## What Makes a Good Experiment

1. **One question.** "Does X actually beat Y?" or "What's the real value of Z on this hardware?" If the README has two questions, split it.
2. **Falsifiable hypothesis.** Write down what you expect *before* running. If results match exactly, you probably didn't measure carefully enough.
3. **Runnable in one command.** `python script.py` or `./script`. No 6-step setup. Stdlib only by default.
4. **Real output.** Numbers, not vibes. Save them in `results.md`.
5. **Failure modes documented.** What does the experiment *not* measure? What confounders exist (thermal throttling, background processes, ASLR, etc.)?
6. **Connects to a constraint.** Physics (cache lines, light-speed latency), Math (algorithmic complexity), or Economics (memory price, dev-time cost).

## Sample Experiments Table

| Folder | Question | Tier |
|---|---|---|
| `cache-line-size-detection` | What's L1 cache line size on this CPU, measured via stride? | hardware |
| `python-vs-c-sort-benchmark` | Why does CPython's `sorted()` beat a hand-rolled merge sort? | language runtime |
| `memory-allocator-comparison` | How much fragmentation does first-fit produce vs best-fit? | allocator strategy |
| `tcp-nagle-vs-nodelay-latency` | What's the latency cost of Nagle's algorithm for tiny writes? | networking |
| `mmap-vs-read-throughput` | When does mmap beat read() for sequential scan? | OS / I/O |
| `branch-predictor-cost` | How many cycles does a mispredicted branch cost? | CPU pipeline |
| `python-gc-pause-distribution` | What's the tail latency of CPython's cyclic GC? | runtime |
| `hash-collision-attack-cost` | How slow does a dict get under adversarial keys? | security / DS |

(Folders that don't exist yet are future work — add them as you have questions.)

## Running an Experiment

```bash
cd experiments/<name>/
python <script>.py          # or compile + run if C
# fill in results.md with what you measured
```

## Convention: results.md Has a Schema

```markdown
# Results — <experiment name>

## Machine
- CPU:
- RAM:
- OS:
- Python / compiler version:

## Run 1 (date)
- Parameters:
- Output:
- Notes (anomalies, thermal, background load):

## Interpretation
- Did the hypothesis hold?
- What surprised you?
- What's the next experiment this suggests?
```

Keep results.md honest. If the experiment was noisy, say so. Negative results count.
