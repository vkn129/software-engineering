# 05 — Production Systems

Production is where physics meets your code. Hardware fails, networks partition,
disks fill up, certificates expire, queues back up, and the on-call engineer's
phone rings at 3 AM. This module teaches the discipline of operating real systems
under real failure — **observability, incident response, and reliability
engineering from first principles**.

The thesis: you cannot operate what you cannot see, and you cannot improve what
you cannot measure. Every concept here is implemented from scratch — no
Prometheus, no Datadog, no OpenTelemetry SDK — so that when you reach for those
tools you understand *what they do* and *why*, not just *how* to configure them.

## Why First Principles Here?

Most production tooling is a thin layer over four primitives:

1. **A time-series store** — append-only numbers with labels and timestamps.
2. **A log pipeline** — structured events flushed to durable storage.
3. **A trace context** — a propagated ID that stitches spans across services.
4. **A rules engine** — predicates over time-series that emit alerts.

If you build each from scratch once, every commercial tool becomes a known
quantity. You stop debating "Prometheus vs InfluxDB" and start asking the real
questions: *what's the retention cost, what's the cardinality budget, what's the
sample bias, what's the alerting latency?*

## Physics & Economics Constraints

| Constraint | Implication |
|---|---|
| **Speed of light** | A distributed trace cannot be assembled in real time; tail sampling needs buffering |
| **Disk IOPS** | High-cardinality metrics blow up storage cost super-linearly |
| **Network bandwidth** | Sampling is not optional — it's a budget allocation problem |
| **Human attention** | Alert fatigue is a cognitive constraint; SLOs encode it |
| **Mean time to detect** | MTTR is dominated by MTTD; observability buys you minutes per incident |

## 8-Week Curriculum

| Week | Topic | Core Question |
|------|-------|---------------|
| [01](week-01/) | Observability Foundations | What's the minimum signal set for a running system? |
| [02](week-02/) | Metrics & Monitoring | How do you store and query numbers over time, cheaply? |
| [03](week-03/) | Logging | How do you produce, ship, parse, and query structured events at scale? |
| [04](week-04/) | Distributed Tracing | How do you reconstruct a single request across N services? |
| [05](week-05/) | Alerting & On-Call | How do you wake the right human at the right time without crying wolf? |
| [06](week-06/) | Incident Response | How do you coordinate humans under uncertainty in real time? |
| [07](week-07/) | Postmortems & RCA | How do you turn one outage into permanent learning? |
| [08](week-08/) | Reliability Engineering | How do you trade development velocity for reliability with intent? |

## Structure

Each week is 5 days of focused topics + 1 mini-project day:

```
week-NN/
├── README.md            # Week overview, learning objectives, day plan
├── day-01/
│   ├── README.md        # Why this matters, concepts, failure modes
│   ├── <topic>.py       # Reference implementation
│   └── practice.py      # 5-6 exercises with TODO + _sol_ + run_tests
├── ...
└── day-06/              # Mini-project applying the week's concepts
```

## Conventions

- **Stdlib only.** No external packages. `http.server`, `json`, `threading`,
  `time`, `collections`, `sqlite3` are fair game.
- **Failure-first.** Every implementation has a "what breaks" section.
- **Cite real tools** (Prometheus, Grafana, Honeycomb, Jaeger, Datadog, PagerDuty)
  but do not use them. Show the primitive, then map to the tool.
- **Tests run.** `python practice.py` must pass with the `_sol_*` fallbacks even
  before you fill in TODOs.

## Tools Referenced (Not Used)

| Concept | Real Tool |
|---|---|
| Time-series DB | Prometheus, InfluxDB, VictoriaMetrics, M3DB |
| Log pipeline | Loki, Elasticsearch, Splunk, Vector |
| Tracing backend | Jaeger, Tempo, Honeycomb, Lightstep |
| Dashboards | Grafana, Datadog, Kibana |
| Alerting | Alertmanager, PagerDuty, Opsgenie |
| Standards | OpenTelemetry, OpenMetrics, W3C Trace Context |

## Prerequisites

- 01-dsa Phase 1-3 (arrays, hash maps, trees) — used for time-series indexes
- Comfort with `threading`, `socket`, and HTTP
- Basic statistics (quantiles, histograms, exponentially-weighted moving average)
