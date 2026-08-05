"""
Day 164: CRDTs — G-Counter, PN-Counter, LWW-Register

State-based CRDTs: each replica holds local state; merge(a, b) returns
the join (least upper bound). Associative, commutative, idempotent.

Demos show convergence under a simulated partition + heal cycle.
"""

from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# G-Counter — grow-only counter
# ---------------------------------------------------------------------------

class GCounter:
    """One slot per replica id. Increment own slot. value = sum. merge = elementwise max."""

    def __init__(self, replica_id: str):
        self.replica_id = replica_id
        self.counts = {replica_id: 0}

    def increment(self, n: int = 1) -> None:
        if n < 0:
            raise ValueError("G-Counter only grows")
        self.counts[self.replica_id] = self.counts.get(self.replica_id, 0) + n

    def value(self) -> int:
        return sum(self.counts.values())

    def merge(self, other: "GCounter") -> None:
        for rid, c in other.counts.items():
            self.counts[rid] = max(self.counts.get(rid, 0), c)

    def __repr__(self) -> str:
        return f"GCounter({self.replica_id}, {self.counts}, value={self.value()})"


# ---------------------------------------------------------------------------
# PN-Counter — positive minus negative
# ---------------------------------------------------------------------------

class PNCounter:
    """Two G-Counters. value = P - N."""

    def __init__(self, replica_id: str):
        self.replica_id = replica_id
        self.p = GCounter(replica_id)
        self.n = GCounter(replica_id)

    def increment(self, k: int = 1) -> None:
        self.p.increment(k)

    def decrement(self, k: int = 1) -> None:
        self.n.increment(k)

    def value(self) -> int:
        return self.p.value() - self.n.value()

    def merge(self, other: "PNCounter") -> None:
        self.p.merge(other.p)
        self.n.merge(other.n)


# ---------------------------------------------------------------------------
# LWW-Register — last-write-wins
# ---------------------------------------------------------------------------

@dataclass
class LWWRegister:
    """(value, timestamp, replica_id). Merge keeps the larger (ts, rid)."""
    replica_id: str
    value: Any = None
    ts: int = 0
    writer: str = ""

    def assign(self, value: Any, ts: int) -> None:
        # tie-break on replica id (lexicographic)
        if (ts, self.replica_id) > (self.ts, self.writer):
            self.value = value
            self.ts = ts
            self.writer = self.replica_id

    def merge(self, other: "LWWRegister") -> None:
        if (other.ts, other.writer) > (self.ts, self.writer):
            self.value = other.value
            self.ts = other.ts
            self.writer = other.writer


# ---------------------------------------------------------------------------
# Demos — partition / heal cycles
# ---------------------------------------------------------------------------

def demo_gcounter_partition():
    print("=" * 60)
    print("DEMO 1: G-Counter survives partition")
    print("=" * 60)
    A = GCounter("A")
    B = GCounter("B")
    C = GCounter("C")

    # Partition: each replica increments independently
    A.increment(3)
    B.increment(2)
    C.increment(5)
    print(f"  A solo: {A.value()},  B solo: {B.value()},  C solo: {C.value()}")

    # Heal: gossip merges in arbitrary order
    A.merge(B); A.merge(C)
    B.merge(C); B.merge(A)
    C.merge(A); C.merge(B)
    print(f"  After merge: A={A.value()}  B={B.value()}  C={C.value()}")
    assert A.value() == B.value() == C.value() == 10
    print("  CONVERGED")


def demo_gcounter_idempotent():
    print("\n" + "=" * 60)
    print("DEMO 2: Merge is idempotent (duplicate messages OK)")
    print("=" * 60)
    A = GCounter("A"); A.increment(5)
    B = GCounter("B"); B.increment(3)
    B.merge(A)
    v1 = B.value()
    B.merge(A); B.merge(A); B.merge(A)   # re-deliver A's state 3x
    print(f"  after 1 merge: {v1},  after 4 merges: {B.value()}  (same!)")


def demo_pncounter():
    print("\n" + "=" * 60)
    print("DEMO 3: PN-Counter — increments and decrements")
    print("=" * 60)
    A = PNCounter("A"); B = PNCounter("B")
    A.increment(10)
    A.decrement(2)
    B.increment(5)
    B.decrement(1)
    A.merge(B); B.merge(A)
    print(f"  A = {A.value()},  B = {B.value()}  (expected 12)")


def demo_lww_clock_skew():
    print("\n" + "=" * 60)
    print("DEMO 4: LWW-Register and clock skew failure")
    print("=" * 60)
    A = LWWRegister("A"); B = LWWRegister("B")

    # A writes at logical ts=10. B writes at ts=20. B wins.
    A.assign("alice@old.com", ts=10)
    B.assign("alice@new.com", ts=20)
    A.merge(B); B.merge(A)
    print(f"  honest: both = {A.value!r}")

    # Now show what skew does: A's clock is 60 ahead. A writes "stale"
    # data at ts=80 *after* B's correct ts=20 write.
    A2 = LWWRegister("A"); B2 = LWWRegister("B")
    B2.assign("alice@new.com", ts=20)
    A2.assign("alice@OLD-but-skewed", ts=80)   # A's clock is wrong
    A2.merge(B2); B2.merge(A2)
    print(f"  with skew: both = {A2.value!r}   <-- bad write wins")


def demo_convergence_order():
    print("\n" + "=" * 60)
    print("DEMO 5: Merge order doesn't matter (associativity test)")
    print("=" * 60)
    import random
    counters = [GCounter(f"r{i}") for i in range(5)]
    for i, c in enumerate(counters):
        c.increment(i + 1)   # 1, 2, 3, 4, 5
    # Two random merge orders
    a = GCounter("x"); b = GCounter("y")
    order1 = list(counters); random.shuffle(order1)
    order2 = list(counters); random.shuffle(order2)
    for c in order1:
        a.merge(c)
    for c in order2:
        b.merge(c)
    print(f"  order1 -> {a.value()},  order2 -> {b.value()}  (both expected 15)")


if __name__ == "__main__":
    demo_gcounter_partition()
    demo_gcounter_idempotent()
    demo_pncounter()
    demo_lww_clock_skew()
    demo_convergence_order()
