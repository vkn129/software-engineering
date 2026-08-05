# 04 — Architecture

System design from first principles. Every architectural rule of thumb derived
from physics (speed of light, disk seek time), economics (cost per request,
capacity vs utilization), and math (queueing theory, CAP, FLP).

## Why This Layer Exists

Most "system design" content is folklore: cargo-culted patterns repeated until
they sound true. This layer rejects that. Every recommendation here is either:

1. Derived from a measurable physical constant (latency of light in fiber,
   spinning-disk seek time, DRAM access time).
2. Backed by a mathematical theorem (Amdahl, USL, Little's law, CAP, FLP).
3. Tied to a documented incident (S3 2017, Knight Capital 2012, Cloudflare
   regex 2019, GitHub 2018, Slack DNSSEC 2022).

If you cannot point to one of these for a design decision, it is taste, not
engineering. State it as taste.

## How To Use This Layer

Each week is conceptual but not hand-wavy. The Python files here are
**simulations and calculators** — they let you plug numbers into formulas and
see what falls out. Implementations are short by design; the leverage is in
the derivations.

- Read the day's `README.md` first.
- Read and run the topic file (`latency.py`, `capacity_estimation.py`, ...).
- Solve `practice.py` (TODOs); fall back to `_sol_*` only after trying.
- Run `python practice.py` until all tests pass.

## 8-Week Curriculum

### Week 1 — First Principles of System Design
Latency numbers, capacity estimation, bottleneck analysis, SLOs, trade-off
frameworks (CAP/PACELC/FLP). Ends with a mini-project: a JSON-driven design
doc generator.

### Week 2 — Communication Patterns
Request/response vs publish/subscribe vs streaming. Sync vs async. RPC vs
REST vs GraphQL vs gRPC. Backpressure. Idempotency. Retries with jitter.
Connection pooling. The thundering herd problem.

### Week 3 — Data & State
Stateful vs stateless. Caching hierarchies (L1/L2/CDN/app/DB). Cache
invalidation (Phil Karlton's "two hard things"). Read-through, write-through,
write-back. Consistency models (linearizable → eventual). Materialized views.

### Week 4 — Reliability & Failure
Failure modes by component (disk, NIC, switch, region). Bulkheads, circuit
breakers, timeouts, deadlines. Chaos engineering. Recovery: RPO, RTO. Blast
radius. The S3 2017 outage decomposed.

### Week 5 — Scale & Sharding
Vertical vs horizontal. Hash-based vs range-based sharding. Consistent
hashing. Hot keys. Rebalancing. The N+1 query problem at scale. CDN edge
strategies. Read replicas vs write fan-out.

### Week 6 — Coordination & Consensus
Leader election. Paxos (sketch), Raft (full). Two-phase commit and why it
blocks. Saga pattern. Distributed locks (Redlock controversy). Clock skew.
Vector clocks. CRDTs. The Jepsen test catalog.

### Week 7 — Architectural Styles
Monolith → modular monolith → SOA → microservices → serverless →
event-driven. When each makes sense (and when it does not — Segment's
"goodbye microservices" 2018). Conway's Law. Strangler fig migration.

### Week 8 — Case Studies
Reconstruct real systems from public postmortems: S3, Dynamo, Spanner,
Kafka, Cassandra. For each: requirements → constraints → trade-offs →
design → failure modes that bit them in production.

## Format

Mirrors `01-dsa/` exactly:

```
week-NN/
  README.md         # week overview, day-by-day topic plan
  day-NN/
    README.md       # 100-180 lines, concept + derivation + real incident
    <topic>.py      # 100-300 lines, reference implementation / calculator
    practice.py     # 100-250 lines, 5-6 TODO + _sol_* + run_tests
```

## Status

- Week 1: complete
- Weeks 2-8: placeholder day-by-day plans only

Build them in order. Skipping ahead defeats the point — week 5 sharding
makes no sense without week 1 capacity estimation.
