# Day 98: Mini-Project — Task Assigner

## What We're Building

A scheduler that takes a real staffing problem — people, jobs, prices, rules —
and returns the **provably cheapest legal plan**, or an honest "this cannot be
done, and here is exactly what is missing".

This day is reserved twice over. `day-092/README.md:100` promises "combines
matching with **cost**"; `day-096/README.md:125` promises "combines this with
**constraints**". Both, here, in one tool:

- **Cost** — day 96 gave us one-to-one minimum-cost matching.
- **Capacity** — a worker can take *k* tasks, not just one. Hungarian cannot say
  this natively; day 97's MCMF can.
- **Demand** — a task can need *k* distinct workers.
- **Eligibility** — an unpriced pair is not on offer at all.
- **Vetoes** — a forbidden pair, whatever it would have cost.
- **Pins** — a decision already made elsewhere that the optimiser must honour.
- **Infeasibility** — reported with the specific shortfall, never hidden.

No new algorithm appears in this file. **Every rule above is a capacity somewhere
in a flow network.** That translation is the whole lesson.

## Architecture

```
   add_worker / add_task / set_cost / forbid / require
                       |
                       v
        [ pins consumed first: capacity--, demand--, budget += ]
                       |
                       v
        source --cap=capacity, cost=0--> worker
                                           |
                                  cap=1, cost=C[w][t]      (eligible pairs only)
                                           v
        sink   <--cap=demand, cost=0--   task
                       |
                       v
          day-097 MinCostMaxFlow(source, sink, limit=sum(demand))
                       |
                       v
        AssignmentResult(feasible, total_cost, pairs, unfilled, worker_load)
```

Read the three capacities out loud and the model explains itself:

| Edge | Capacity | The business rule it encodes |
|---|---|---|
| `source -> worker` | worker's capacity | "you can absorb at most this much work" |
| `worker -> task` | **1** | "you may fill *one* slot of this task" |
| `task -> sink` | task's demand | "this needs this many people" |

The middle capacity is the subtle one. Setting it to 1 — rather than leaving it
unbounded — is what makes "a task needing 2 workers" mean **two different
people** instead of one person counted twice.

## Design Decisions, and Why

**Unpriced means ineligible, not free.** A missing `set_cost` produces no edge.
The alternative — defaulting to cost 0 — makes the optimiser enthusiastically
assign work to people who cannot do it, and the bug surfaces as a suspiciously
cheap plan rather than an error.

**A veto is a deleted edge, not a huge price.** `day-096/README.md:85-87` uses the
Big-M trick (`10**9`) because Hungarian needs a full square matrix. We do not:
we simply omit the edge. Big-M has a real failure mode — when the instance is
infeasible, the solver returns a plan built from `10**9` entries and calls it
optimal. Deleting the edge instead makes infeasibility *look* like
infeasibility.

**Pins are consumed before solving.** Encoding "this edge must carry flow" inside
a flow network needs lower bounds on edges, which is a genuinely harder problem.
Decrementing the capacity and demand by one and adding the cost up front is
equivalent, cheaper, and makes a self-contradictory pin (pinned *and* forbidden,
or pinned twice past capacity) raise immediately instead of quietly producing a
plan that ignores it.

**`feasible` is a separate field from `total_cost`.** A short flow is still a
flow, and it is always cheaper than the complete one. Any caller that reads the
cost without checking the flag will eventually ship a rota with an empty on-call
shift.

## What Could Go Wrong (and the check for each)

| # | Failure | Where it is caught |
|---|---|---|
| 1 | Plan looks cheap because work was dropped | `demo_infeasible` prints cost 1 beside `feasible: NO` and the unfilled task |
| 2 | Two "distinct" workers are the same person | `worker -> task` capacity 1; `brute_force_cost` mirrors it via slot expansion; test "demand 2 needs two distinct workers" |
| 3 | A veto is ignored because the pair was cheap | `demo_constraints` forbids a pair the free optimum actually wanted; cost moves 5 → 6 |
| 4 | A pin is silently dropped | `assign_pinned` returns `(False, 0, [])` on an impossible pin; `TaskAssigner.solve` raises on a contradictory one |
| 5 | A pinned pair is *also* chosen by the optimiser (double-counted) | the pinned edge is removed from the pool before solving; test "no worker doubled up" |
| 6 | The model is subtly wrong but plausible | `demo_optimality_fuzz` — 200 random instances checked against exhaustive enumeration, **0 disagreements** |
| 7 | A constraint accidentally *improves* the plan | test "a constraint cannot lower the cost" asserts `constrained >= free` |
| 8 | The output violates a rule the solver was meant to enforce | `validate()` re-checks a finished plan from scratch; the solver's own output is fed back through it |

Rows 6 and 8 are the ones that matter. Exercise 6 in `practice.py` is a
brute-force optimum by slot expansion; exercise 5 is an independent legality
checker. **A model you cannot verify independently is a model you are trusting on
vibes** — day 97 proves the flow *algorithm* is correct, which says nothing at all
about whether your *translation* of the business rules was right.

## Where Hungarian Stops Being Enough

Try expressing these with a square cost matrix and `day-096/hungarian.py`:

| Requirement | Hungarian | This tool |
|---|---|---|
| one worker, one task | yes, natively | yes |
| worker takes 3 tasks | pad with 3 clones of the worker | `capacity=3` |
| task needs 2 workers | pad with 2 clones of the task | `demand=2` |
| forbidden pair | Big-M sentinel, then re-check the answer | edge omitted |
| pinned pair | not expressible; re-solve and hope | capacity consumed up front |
| more workers than tasks | pad to square with zeros | falls out naturally |
| honest infeasibility | must be inferred from Big-M entries in the result | `feasible` flag + `unfilled` map |

The clone tricks work, and on a fixed square problem Hungarian's `O(n^3)` beats
MCMF comfortably. But every clone multiplies the matrix, and Big-M collapses
"impossible" into "expensive" — a distinction production code has to keep.

## Comparison to Real Systems

| Concept | Our impl | Production |
|---|---|---|
| Engine | successive shortest paths + Johnson potentials | network simplex, or a full MIP solver (CP-SAT, Gurobi) |
| Objective | one linear cost | multi-objective: cost, fairness, preference, overtime |
| Constraints | capacity, demand, veto, pin | plus time windows, rest rules, union agreements, legal caps |
| Scale | tens of nodes | dispatch-scale: 10^5 pairs, re-solved every few seconds |
| Re-solving | from scratch | warm-started from the previous solution |
| Infeasibility | flag + shortfall map | soft constraints with penalty weights, so *something* always ships |

That last row is the big production divergence. Real schedulers rarely return "no
solution" — they make hard constraints soft, attach a penalty, and return the
least-bad plan. Which is the same network with one extra high-cost edge from
every task straight to the sink: "leave it unstaffed, and charge us for it."

## Checkpoint Questions

1. Trace exactly which capacity in the network enforces "a task needing 2 workers
   gets 2 *different* people". What breaks if that capacity is raised?
2. Why is an unpriced pair modelled as a missing edge instead of a cost-0 edge?
   Describe the specific wrong plan the cost-0 version would return.
3. Big-M (`10**9`) versus deleting the edge: construct an instance where Big-M
   returns a "solution" that is actually infeasible.
4. Pins are handled by decrementing capacity and demand before solving. Argue
   that this yields the same optimum as forcing the edge to carry flow. Where
   would the equivalence break down?
5. A caller reads `result.total_cost` and ignores `result.feasible`. Sketch the
   incident report.
6. Fuzzing found 0 disagreements over 200 instances. What class of modelling bug
   would that fuzz still miss, and how would you extend it to catch that class?
7. Add the rule "worker `w` and worker `v` must not share a task." Can this be
   expressed as a capacity in *any* flow network? Justify your answer.
8. The costs are floats (predicted minutes). Name two things that go wrong, and
   give the fix used everywhere else in this phase.
