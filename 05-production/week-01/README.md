# Week 1 — Observability Foundations

Observability is the property of a system that lets you ask *new* questions
about its behavior without shipping new code. It is not a tool; it is a
discipline backed by three signal types — metrics, logs, traces — and a few
sharp ideas about cost, sampling, and what to measure.

This week builds the mental model. By Friday you will be able to argue, for any
given symptom, *which signal type would have caught it cheapest* and *why*.

## Learning Objectives

By end of week you can:

1. Distinguish metrics, logs, and traces by data model, cost, and query pattern.
2. Predict cardinality blow-up before it lands you a $40k/month bill.
3. Pick a sampling strategy that preserves the rare events that matter.
4. Apply USE and RED methods to design dashboards for any service.
5. Choose SLIs that actually correlate with user pain for different workload types.
6. Instrument a real HTTP service end-to-end and correlate signals on one request.

## Day Plan

| Day | Topic | File |
|-----|-------|------|
| [01](day-01/) | Three pillars — metrics vs logs vs traces | `three_pillars.py` |
| [02](day-02/) | Cardinality & retention — the cost model | `cardinality.py` |
| [03](day-03/) | Sampling — head, tail, adaptive | `sampling.py` |
| [04](day-04/) | USE + RED methods for dashboards | `use_red.py` |
| [05](day-05/) | SLI selection by workload type | `sli_selection.py` |
| [06](day-06/) | Mini-project: observability harness | `observability_harness.py` |

## How to Use This Week

For each day:

1. Read the `README.md` — concepts, failure modes, real-tool mapping.
2. Read the reference implementation in `<topic>.py`.
3. Solve `practice.py` exercises. Run `python practice.py` to see pass/fail.

The mini-project on day 6 ties the week together — a single HTTP request flows
through middleware that emits a metric, a structured log, and a trace span, all
correlated by a shared request ID.

## Checkpoint Questions (end-of-week)

1. You have a `user_id` label on an HTTP request counter with 10M users.
   Estimate the time-series count. Why is this a fireable offense?
2. A rare 500 error happens 1 in 100k requests. Head sampling at 1% will miss
   it 99% of the time. Sketch a tail sampler that catches it.
3. For a Kafka consumer, give one USE metric and one RED metric. Which method
   fits the workload better and why?
4. Your SLI is "p99 latency < 200ms." A deploy raises p99.9 to 5s but leaves p99
   unchanged. Did you violate the SLO? Did you hurt users?
