# Week 1 — First Principles of System Design

Before any pattern, any framework, any "best practice," you need the
physics. This week is the foundation every later week assumes.

## Why Start Here

Most engineers reach for patterns (microservices, event sourcing, CQRS)
before understanding the constraints those patterns work around. The
constraints come first:

- **Light is slow.** 200 km / ms in fiber. A round trip from US-East to
  EU-West is ~80 ms, and there is no engineering you can do to fix it.
- **Disks are slow.** A spinning-disk seek is ~10 ms — 10,000,000 times
  slower than an L1 cache hit. SSDs help (~100 us) but the gap is still
  100,000x.
- **Sequential is fast.** Reading 1 MB sequentially from SSD is ~50 us;
  the same data scattered as 1000 random reads is ~100 ms.
- **Networks fail.** TCP retransmits, packets drop, BGP routes flap.
- **Humans are the bottleneck.** A page at 3 am has an MTTR floor set
  by human reaction time.

Every architectural decision is, ultimately, a negotiation with these.

## Day-by-Day

| Day | Topic | Filename | Anchor incident |
|-----|-------|----------|------------------|
| 01 | Latency numbers every programmer should know | `latency.py` | Jeff Dean's 2009 table; AWS cross-region latency budgets |
| 02 | Capacity estimation (QPS, storage, bandwidth) | `capacity_estimation.py` | Twitter fail whale (2007-2010); Pokemon Go launch (2016) |
| 03 | Bottleneck analysis — CPU/mem/IO/net; Amdahl & USL | `bottleneck_analysis.py` | Knight Capital (2012); GitHub MySQL saturation (2018) |
| 04 | SLAs, SLOs, error budgets — math of nines | `slo_calculator.py` | AWS S3 2017 (99.99% violated); Google SRE error budget |
| 05 | CAP, PACELC, FLP — trade-off framework | `tradeoff_framework.py` | DynamoDB AZ partition 2015; MongoDB Jepsen reports |
| 06 | Mini-project: first-principles design doc generator | `system_designer.py` | Combine days 1-5 into a JSON-driven design tool |

## Outcomes

By Friday you can:

1. Estimate the QPS, storage, and bandwidth budget of any system on a
   napkin in under 10 minutes — and defend each number.
2. Identify the single bottleneck in a proposed design before writing
   code, using Amdahl's law and queueing theory.
3. Translate a business SLA into an engineering SLO with a concrete
   error budget in seconds-per-month.
4. Name the consistency / availability / latency trade-off a given
   design is making, using PACELC vocabulary.
5. Generate a design doc skeleton from a JSON spec that is rigorous
   enough to debate, not just nod at.

## Format Reminder

Each day:
- `README.md` — 100-180 lines, derivation + real-world incident.
- `<topic>.py` — 100-300 lines, runnable calculator/simulation.
- `practice.py` — 100-250 lines, 5-6 TODOs with `_sol_*` and `run_tests`.

Run `python practice.py` at the end of each day. Every test must pass.
