"""
Day 98: Mini-Project — Task Assigner

Capstone for the matching arc. `day-092/README.md:100` and
`day-096/README.md:125` both point here: matching **with cost** and matching
**with constraints**. Day 97's min-cost max-flow is the engine; this file is the
modelling layer on top of it.

The whole job of this file is translation. Business rules in, one flow network
out, a provably optimal answer back. Nothing here is a new algorithm — every
constraint below turns out to be a capacity somewhere.

Standard library only.
"""

import heapq
import random
from itertools import permutations

INF = float("inf")


# ---------------------------------------------------------------------------
# Engine: day 97's min-cost max-flow, unchanged
# ---------------------------------------------------------------------------

class MinCostMaxFlow:
    """Reverse of edge i is edge i ^ 1. See day-097 for the derivation."""

    def __init__(self, n):
        self.n = n
        self.adj = [[] for _ in range(n)]
        self.edges = []

    def add_edge(self, u, v, cap, cost):
        idx = len(self.edges)
        self.adj[u].append(idx)
        self.edges.append([v, cap, cost])
        self.adj[v].append(idx + 1)
        self.edges.append([u, 0, -cost])
        return idx

    def flow_on(self, idx):
        return self.edges[idx ^ 1][1]

    def _potentials(self, source):
        pot = [INF] * self.n
        pot[source] = 0
        for _ in range(self.n - 1):
            changed = False
            for idx in range(0, len(self.edges), 2):
                v, cap, cost = self.edges[idx]
                if cap <= 0:
                    continue
                u = self.edges[idx ^ 1][0]
                if pot[u] < INF and pot[u] + cost < pot[v]:
                    pot[v] = pot[u] + cost
                    changed = True
            if not changed:
                break
        return pot

    def min_cost_flow(self, source, sink, limit=INF):
        pot = self._potentials(source)
        flow = total = 0
        while flow < limit:
            dist = [INF] * self.n
            prev = [-1] * self.n
            dist[source] = 0
            pq = [(0, source)]
            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u] or pot[u] == INF:
                    continue
                for idx in self.adj[u]:
                    v, cap, c = self.edges[idx]
                    if cap <= 0 or pot[v] == INF:
                        continue
                    nd = d + c + pot[u] - pot[v]
                    if nd < dist[v]:
                        dist[v] = nd
                        prev[v] = idx
                        heapq.heappush(pq, (nd, v))
            if dist[sink] == INF:
                break                      # no augmenting path: done
            for v in range(self.n):
                if dist[v] < INF and pot[v] < INF:
                    pot[v] += dist[v]
            push = limit - flow
            v = sink
            while v != source:
                idx = prev[v]
                push = min(push, self.edges[idx][1])
                v = self.edges[idx ^ 1][0]
            v = sink
            path_cost = 0
            while v != source:
                idx = prev[v]
                self.edges[idx][1] -= push
                self.edges[idx ^ 1][1] += push
                path_cost += self.edges[idx][2]
                v = self.edges[idx ^ 1][0]
            flow += push
            total += push * path_cost
        return flow, total


# ---------------------------------------------------------------------------
# Result object
# ---------------------------------------------------------------------------

class AssignmentResult:
    """
    What the solver hands back.

    `feasible` is kept separate from `total_cost` on purpose. A partially
    staffed plan has a low cost precisely BECAUSE it left work undone —
    reporting that number without the flag is how an optimiser lies to you.
    """

    def __init__(self, feasible, total_cost, pairs, unfilled, worker_load):
        self.feasible = feasible
        self.total_cost = total_cost
        self.pairs = pairs              # sorted list of (worker, task)
        self.unfilled = unfilled        # {task: slots still unstaffed}
        self.worker_load = worker_load  # {worker: tasks taken}

    def __repr__(self):
        state = "FEASIBLE" if self.feasible else "INFEASIBLE"
        return (f"<AssignmentResult {state} cost={self.total_cost} "
                f"pairs={len(self.pairs)} unfilled={self.unfilled}>")

    def report(self):
        lines = ["  feasible : " + ("yes" if self.feasible else "NO"),
                 f"  cost     : {self.total_cost}"]
        for w, t in self.pairs:
            lines.append(f"    {w:<10} -> {t}")
        if self.unfilled:
            lines.append(f"  UNFILLED : {self.unfilled}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# The modelling layer
# ---------------------------------------------------------------------------

class TaskAssigner:
    """
    Assign workers to tasks at minimum total cost, subject to:

      * worker capacity  — a worker takes at most `capacity` tasks
      * task demand      — a task needs `demand` DISTINCT workers
      * eligibility      — a pair is offered only if it has been priced
      * forbidden pairs  — an explicit veto that beats any price
      * pinned pairs     — a decision already taken outside the optimiser

    Every one of those is a capacity in the flow network. That is the trick.
    """

    def __init__(self):
        self.worker_capacity = {}
        self.task_demand = {}
        self.cost = {}            # (worker, task) -> cost
        self.forbidden = set()
        self.pinned = []          # [(worker, task)]

    # -- model construction --------------------------------------------------

    def add_worker(self, name, capacity=1):
        if capacity < 0:
            raise ValueError(f"worker {name!r}: capacity must be >= 0")
        self.worker_capacity[name] = capacity
        return self

    def add_task(self, name, demand=1):
        if demand < 0:
            raise ValueError(f"task {name!r}: demand must be >= 0")
        self.task_demand[name] = demand
        return self

    def set_cost(self, worker, task, cost):
        """Price a pair. An UNPRICED pair is ineligible — silence means no."""
        if worker not in self.worker_capacity:
            raise KeyError(f"unknown worker {worker!r}")
        if task not in self.task_demand:
            raise KeyError(f"unknown task {task!r}")
        self.cost[(worker, task)] = cost
        return self

    def forbid(self, worker, task):
        """Veto a pair regardless of price (missing clearance, conflict, ...)."""
        self.forbidden.add((worker, task))
        return self

    def require(self, worker, task):
        """Pin a pair. The optimiser routes around it; it does not revisit it."""
        self.pinned.append((worker, task))
        return self

    def _eligible(self, worker, task):
        return ((worker, task) in self.cost
                and (worker, task) not in self.forbidden)

    # -- solving -------------------------------------------------------------

    def solve(self):
        """Return an AssignmentResult. Never raises on mere infeasibility."""
        cap = dict(self.worker_capacity)
        demand = dict(self.task_demand)
        fixed_pairs = []
        fixed_cost = 0

        # Pinned pairs are settled before the optimiser sees the problem: spend
        # the capacity and the budget up front, then optimise what is left. That
        # is strictly cheaper than encoding "must use this edge" in the network,
        # and it makes a self-contradictory pin fail loudly instead of quietly.
        for w, t in self.pinned:
            if (w, t) in self.forbidden:
                raise ValueError(f"pair ({w!r}, {t!r}) is both pinned and forbidden")
            if (w, t) not in self.cost:
                raise ValueError(f"pinned pair ({w!r}, {t!r}) has no cost")
            if cap.get(w, 0) <= 0:
                raise ValueError(
                    f"pinned pair ({w!r}, {t!r}): {w!r} has no capacity left")
            if demand.get(t, 0) <= 0:
                raise ValueError(
                    f"pinned pair ({w!r}, {t!r}): {t!r} needs no more workers")
            cap[w] -= 1
            demand[t] -= 1
            fixed_cost += self.cost[(w, t)]
            fixed_pairs.append((w, t))

        workers = sorted(cap)
        tasks = sorted(demand)
        w_index = {w: i for i, w in enumerate(workers)}
        t_index = {t: len(workers) + j for j, t in enumerate(tasks)}
        source = len(workers) + len(tasks)
        sink = source + 1

        g = MinCostMaxFlow(sink + 1)
        for w in workers:
            g.add_edge(source, w_index[w], cap[w], 0)
        for t in tasks:
            g.add_edge(t_index[t], sink, demand[t], 0)

        fixed_set = set(fixed_pairs)
        pair_edge = {}
        for w in workers:
            for t in tasks:
                if (w, t) in fixed_set:
                    continue        # already spent; must not be taken twice
                if self._eligible(w, t):
                    # Capacity 1: a worker fills at most ONE slot of a given
                    # task, so "2 distinct workers" really means 2 people.
                    pair_edge[(w, t)] = g.add_edge(
                        w_index[w], t_index[t], 1, self.cost[(w, t)]
                    )

        needed = sum(demand.values())
        sent, cost = g.min_cost_flow(source, sink, needed)

        pairs = list(fixed_pairs)
        filled = {t: 0 for t in tasks}
        for w, t in fixed_pairs:
            filled[t] = filled.get(t, 0) + 1
        for (w, t), idx in pair_edge.items():
            if g.flow_on(idx) > 0:
                pairs.append((w, t))
                filled[t] += 1
        pairs.sort()

        unfilled = {t: self.task_demand[t] - filled.get(t, 0)
                    for t in self.task_demand
                    if self.task_demand[t] > filled.get(t, 0)}
        worker_load = {}
        for w, _ in pairs:
            worker_load[w] = worker_load.get(w, 0) + 1

        return AssignmentResult(
            feasible=(sent == needed),
            total_cost=fixed_cost + cost,
            pairs=pairs,
            unfilled=unfilled,
            worker_load=worker_load,
        )

    # -- ground truth --------------------------------------------------------

    def brute_force_cost(self):
        """
        Exhaustive optimum for tiny instances. Returns None if infeasible.

        Slot expansion mirrors the network exactly: a task of demand d becomes d
        slots, a worker of capacity c becomes c slots, and a (worker, task) pair
        may be used at most once. If this and `solve()` ever disagree, the MODEL
        is wrong — the flow algorithm itself is verified on day 97.
        """
        task_slots = []
        for t in sorted(self.task_demand):
            task_slots.extend([t] * self.task_demand[t])
        worker_slots = []
        for w in sorted(self.worker_capacity):
            worker_slots.extend([w] * self.worker_capacity[w])
        if len(task_slots) > len(worker_slots):
            return None

        pinned = list(self.pinned)
        best = INF
        for combo in permutations(range(len(worker_slots)), len(task_slots)):
            total = 0
            used = set()
            ok = True
            for slot_i, ws_i in enumerate(combo):
                w = worker_slots[ws_i]
                t = task_slots[slot_i]
                if not self._eligible(w, t) or (w, t) in used:
                    ok = False
                    break
                used.add((w, t))
                total += self.cost[(w, t)]
            if ok and all(p in used for p in pinned):
                best = min(best, total)
        return None if best == INF else best


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def _basic():
    a = TaskAssigner()
    for w in ("ana", "ben", "cara"):
        a.add_worker(w)
    for t in ("deploy", "oncall", "review"):
        a.add_task(t)
    prices = {
        ("ana", "deploy"): 4, ("ana", "review"): 1, ("ana", "oncall"): 3,
        ("ben", "deploy"): 2, ("ben", "review"): 0, ("ben", "oncall"): 5,
        ("cara", "deploy"): 3, ("cara", "review"): 2, ("cara", "oncall"): 2,
    }
    for (w, t), c in prices.items():
        a.set_cost(w, t, c)
    return a


def demo_cost():
    print("=" * 60)
    print("DEMO 1: matching WITH COST (what day 92 promised)")
    print("=" * 60)
    a = _basic()
    res = a.solve()
    truth = a.brute_force_cost()
    print("\n" + res.report())
    print(f"\n  brute-force optimum: {truth}  "
          f"[{'OK' if res.total_cost == truth else 'MISMATCH'}]")


def demo_capacity():
    print("\n" + "=" * 60)
    print("DEMO 2: capacity — one worker takes two tasks")
    print("=" * 60)
    a = TaskAssigner()
    a.add_worker("ana", capacity=2).add_worker("ben", capacity=1)
    a.add_task("deploy").add_task("oncall").add_task("review")
    for t, c in (("deploy", 1), ("review", 1), ("oncall", 9)):
        a.set_cost("ana", t, c)
    for t, c in (("deploy", 8), ("review", 8), ("oncall", 2)):
        a.set_cost("ben", t, c)
    res = a.solve()
    truth = a.brute_force_cost()
    print("\n" + res.report())
    print(f"  load: {res.worker_load}")
    print(f"\n  brute-force optimum: {truth}  "
          f"[{'OK' if res.total_cost == truth else 'MISMATCH'}]")


def demo_constraints():
    print("\n" + "=" * 60)
    print("DEMO 3: constraints (what day 96 promised)")
    print("=" * 60)
    a = _basic()
    base = a.solve()
    print(f"\n  unconstrained cost = {base.total_cost}  pairs = {base.pairs}")

    # Veto a pair the optimum actually WANTED, or the demo proves nothing.
    a2 = _basic()
    a2.forbid("ana", "review")     # ana lacks review rights
    r2 = a2.solve()
    print(f"  forbid ana/review  -> cost = {r2.total_cost}  pairs = {r2.pairs}")
    print(f"     brute force = {a2.brute_force_cost()}")

    a3 = _basic()
    a3.require("ana", "oncall")    # already promised to the customer
    r3 = a3.solve()
    print(f"  pin ana/oncall     -> cost = {r3.total_cost}  pairs = {r3.pairs}")
    print(f"     brute force = {a3.brute_force_cost()}")
    print("\n  Constraints can only make the plan worse or equal — never better.")


def demo_infeasible():
    print("\n" + "=" * 60)
    print("DEMO 4: infeasibility is reported, not hidden")
    print("=" * 60)
    a = TaskAssigner()
    a.add_worker("ana")
    a.add_task("deploy").add_task("review")
    a.set_cost("ana", "deploy", 1).set_cost("ana", "review", 1)
    res = a.solve()
    print("\n  1 worker, 2 tasks:")
    print(res.report())
    print("\n  The cost is LOW precisely because work was left undone.")
    print("  Reading total_cost without checking .feasible is the classic bug.")

    b = TaskAssigner()
    b.add_worker("ana").add_worker("ben")
    b.add_task("deploy", demand=2)
    b.set_cost("ana", "deploy", 5).set_cost("ben", "deploy", 7)
    print("\n  a task needing 2 distinct workers:")
    print(b.solve().report())


def demo_optimality_fuzz():
    print("\n" + "=" * 60)
    print("DEMO 5: fuzzing the model against brute force")
    print("=" * 60)
    rng = random.Random(98)
    agree = both_infeasible = disagree = 0
    for _ in range(200):
        nw = rng.randint(1, 4)
        nt = rng.randint(1, 3)
        a = TaskAssigner()
        for i in range(nw):
            a.add_worker(f"w{i}", capacity=rng.randint(1, 2))
        for j in range(nt):
            a.add_task(f"t{j}", demand=rng.randint(1, 2))
        for i in range(nw):
            for j in range(nt):
                if rng.random() < 0.8:
                    a.set_cost(f"w{i}", f"t{j}", rng.randint(0, 9))
        res = a.solve()
        truth = a.brute_force_cost()
        if truth is None and not res.feasible:
            both_infeasible += 1
        elif truth is not None and res.feasible and res.total_cost == truth:
            agree += 1
        else:
            disagree += 1
    print(f"\n  agreed with brute force : {agree}")
    print(f"  infeasible (both agree) : {both_infeasible}")
    print(f"  DISAGREEMENTS           : {disagree}")


if __name__ == "__main__":
    demo_cost()
    demo_capacity()
    demo_constraints()
    demo_infeasible()
    demo_optimality_fuzz()
