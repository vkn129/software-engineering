# Day 105: Mini-Project — Sorting Benchmark Harness

## What We're Building

Days 99-104 built seven kinds of sort and made a lot of claims about them. This
day does not restate a single one. It **measures** them.

`sort_benchmark.py` loads every sibling day's module by file path, runs each
algorithm across seven input *shapes* at several sizes, verifies every result
before timing it, and reports medians and rankings. A missing day is skipped,
not fatal.

The subject of study is **the harness**, not the sorts. A benchmark is a
measuring instrument, and an instrument you have not calibrated is a rumour
generator.

## Architecture

```
  build_registry()
     |  loads day-099..day-104 via importlib.spec_from_file_location
     |  (directory names like `day-099` are not legal Python identifiers)
     v
  [ Algo(name, day, fn, domain, max_n) ]  x13, incl. sorted() as the baseline
     |
     v
  make_shape(kind, n, seed) ---> adapt(values, domain)
     |                              (int shapes -> unit floats for bucket_sort)
     v
  verify(fn, data)  --- problems? ---> record "crash"/"not sorted", DO NOT TIME
     |  clean
     v
  time_median(fn, data, repeats=3, warmup=1)
     |
     v
  rank_by(results)  ---> tables, rankings, growth ratios
```

## The Three Rules The Harness Enforces On Itself

**1. Verify before you time.** An incorrect sort is not a fast sort. `verify()`
checks two things, and the second is the one people forget:

- is the output non-decreasing?
- is the output a **permutation** of the input?

Sorted-ness alone is trivially gamed. `return []` is perfectly sorted. So is
`[min(a)] * len(a)`. Without the multiset check, the fastest algorithm in your
table is the one that threw the data away.

**2. Identical input for everything.** `make_shape(kind, n, seed)` is a pure
function of its arguments. Every algorithm gets the same list, freshly copied,
and the copy happens *outside* the timed region.

**3. Median, never mean.** One GC pause moves a mean. It does not move a median.
`warmup=1` discards the first run, which pays for allocator growth and cold
branch predictors — timing that measures the interpreter waking up.

## Shapes Matter More Than Sizes

"n = 100k random ints" is one data point. The interesting question is which
algorithms fall over on which **structure**:

| shape | why it is in the list |
|---|---|
| `random` | the baseline everyone quotes |
| `sorted` | worst case for a first-element pivot; best case for Timsort |
| `reverse` | worst case for naive insertion; one descending run for Timsort |
| `all_equal` | worst case for **Lomuto** partitioning — every element equals the pivot |
| `few_unique` | the realistic version of `all_equal` (status codes, category ids) |
| `nearly_sorted` | the common real-world case; the one Timsort was built for |
| `organ_pipe` | up then down — and, by day 104's definition, exactly a **bitonic** sequence |

Measured at n = 2000 (median ms on one machine — read the *shape of the table*,
not the digits):

| algorithm | random | sorted | all_equal | nearly_sorted |
|---|---|---|---|---|
| `quicksort_random` | 4.46 | 1.48 | **103.62** | 1.37 |
| `quicksort_median3` | 7.88 | 1.07 | **106.58** | 3.06 |
| `quicksort_unsafe` | 1.51 | **35.57** | **105.30** | 10.57 |
| `timsort` | 2.47 | **0.08** | **0.08** | 0.68 |
| `counting_sort` | 0.22 | 0.22 | 0.17 | 0.21 |
| `bitonic_sort` | 18.37 | 13.60 | 13.09 | 13.85 |
| `sorted()` [C] | 0.13 | 0.006 | 0.012 | 0.029 |

Four findings only a measurement produces:

- **`all_equal` is a ~70x cliff for every Lomuto quicksort**, including the one
  with a "safe" random pivot. Randomising the pivot defends against *sorted*
  input, not against *duplicate* input — different attacks, and only three-way
  partitioning fixes the second.
- **`quicksort_unsafe` is the fastest quicksort on random data and the slowest
  on sorted data.** Same algorithm, opposite verdicts, same n. Any benchmark
  reporting one number per algorithm is hiding this.
- **Timsort's presorted case is ~30x faster than its random case.** The
  adaptivity is real and it is large.
- **`bitonic_sort` is nearly flat across every shape.** That is not a weakness
  being hidden; it is day 104's entire thesis — data-oblivious means the shape
  cannot matter — showing up as a row of near-identical numbers.

## What The Harness Found Out About Itself

Two of its findings are about measurement, not about sorting.

**The code under test mutated the interpreter.** `day-099/comparison_sorts.py:12`
and `day-100/quicksort_deep.py:12` both call `sys.setrecursionlimit(10**6)` at
module scope. Importing them raises the limit process-wide, so a deep-recursion
failure a user *would* hit at the default limit of 1000 cannot happen inside the
harness. The first draft of `demo_pathology` asserted that `quicksort_unsafe`
raises `RecursionError` on large sorted input. It does not — verified at
n = 20000. The harness now snapshots the limit before loading anything and
prints the change as a warning.

**Stability must be measured with a compare-only object.** The obvious way to
test it — sort `(key, index)` tuples — is self-deceiving: tuple comparison falls
through to the index, so an unstable sort still comes out looking stable. The
`KeyOnly` class compares on `key` and ignores `tag`. Measured:

| stable | not stable | n/a |
|---|---|---|
| `merge_sort`, `external_sort`, `timsort`, `sorted()` | `heap_sort`, all four quicksorts, `bitonic_sort` | `counting_sort`, `radix_sort_lsd`, `bucket_sort` |

`n/a` is not a gap in the harness. Those three **read** the values — as array
indices or digits — rather than merely comparing them, so they cannot accept a
compare-only object at all. Stability is not a well-posed question for an input
the algorithm cannot represent.

## Domains: Why Some Comparisons Are Not Fair

`counting_sort` and `radix_sort_lsd` accept only non-negative integers.
`bucket_sort` accepts only floats in `[0, 1)`. Racing them against Timsort on
arbitrary data is not a fair fight, it is a category error — so every `Algo`
carries a `domain`, and `adapt()` projects each shape into it while preserving
order. The linear-time sorts look fastest *because they are solving a smaller
problem*, and the harness records exactly which one.

## What Could Go Wrong (and the check for each)

| # | Failure | Where it is caught |
|---|---|---|
| 1 | A wrong sort posts a fast time | `verify()` runs before any timing: sorted-ness **and** multiset |
| 2 | "Sorted" output that dropped elements | `same_multiset`; practice exercise 3 tests `lambda a: []` explicitly |
| 3 | A crash silently recorded as 0 ms | `verify()` catches every exception and stores its class name |
| 4 | Cold-start cost attributed to the algorithm | `warmup=1` untimed run before sampling |
| 5 | One GC pause distorts a result | median of `repeats`, never a mean |
| 6 | Copy cost counted as sort cost | the copy happens outside the `perf_counter` window |
| 7 | Two runs not comparable | `make_shape` is a pure function of `(kind, n, seed)` |
| 8 | Ranking reshuffles between runs | `rank_by` breaks ties by name; crashes sort last, never first |
| 9 | Unfair cross-domain comparison | per-`Algo` `domain` + `adapt()` |
| 10 | Importing the subject changes the environment | recursion limit snapshotted and diffed in DEMO 1 |
| 11 | Stability test fooled by the tie-break | `KeyOnly` compares on key only |
| 12 | A missing day kills the run | `load_day` returns `None`; the registry skips it |

## Why The Tests Assert No Timings

`practice.py` has seven exercises and not one wall-clock assertion. Timings
depend on machine, load, thermal state, and whatever the OS scheduler felt like
doing — `assert t < 0.05` is a test that fails for reasons nobody can fix, and a
flaky test is worse than no test because it trains you to ignore red.

What *is* testable is everything around the clock: `is_sorted`, `same_multiset`,
`verify_sort`, the determinism of `make_shape`, stability detection, `median` (a
pure function of a literal list), and the **ordering properties** of `rank_by` —
ties by name, crashes last, reproducible.

The measurements belong in the demos. The invariants belong in the tests.

## Comparison to Real Systems

| Concept | Our harness | Production (`pyperf`, `criterion`, JMH) |
|---|---|---|
| Sample count | 3 + 1 warmup | hundreds, until the confidence interval converges |
| Statistic | median | median + MAD + outlier classification |
| Noise control | none | CPU pinning, turbo off, isolated cores |
| Environment | whatever you have | fixed image, ASLR / hash-seed control |
| Regression | eyeball the table | stored baselines, automatic significance testing |
| Warm-up | 1 run | until steady state is detected (essential on a JIT) |

The gap that matters most is noise control. Our numbers are honest about
*ordering* and unreliable about *absolute values* — which is exactly why the
report says to read the ranking, not the milliseconds.

## Checkpoint Questions

1. A sort returns `[min(a)] * len(a)`. Which check catches it, and why is
   `is_sorted` alone insufficient?
2. Why report the median rather than the mean? Construct the sample that
   separates them.
3. Why is the input copy outside the timed region? What would including it do to
   the ranking of the linear-time sorts specifically?
4. `quicksort_random` is 70x slower on `all_equal` than on `random`. Explain via
   Lomuto's partition, and name the fix.
5. `quicksort_unsafe` is the fastest quicksort on random input and the slowest on
   sorted input. What does that imply about single-number benchmark reports?
6. `bitonic_sort` is nearly flat across all seven shapes. Strength or weakness?
   Answer using day 104's argument.
7. Importing the code under test raised the recursion limit to 10^6. Name two
   other ways a module import could invalidate a benchmark.
8. Why does measuring stability with `(key, index)` tuples always report
   "stable"? Write the two-element counter-example.
9. `counting_sort` is fastest in almost every column. Why is that not a
   recommendation to use it?
10. Design one additional shape that would break an algorithm none of the current
    seven break. Which one, and why?
