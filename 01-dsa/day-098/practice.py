"""
Day 98 Practice: Task Assigner capstone

6 exercises. Implement the TODOs, then run: python3 practice.py

Shared input shape for every exercise:
    workers : {name -> capacity}          how many tasks this person can take
    tasks   : {name -> demand}            how many DISTINCT people this needs
    costs   : {(worker, task) -> cost}    an unpriced pair is not eligible
"""

import heapq
from itertools import permutations

INF = float("inf")


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def try_or_sol(fn_name, *args, **kwargs):
    student = globals().get(fn_name)
    sol = globals().get(f"_sol_{fn_name}")
    if student:
        result = student(*args, **kwargs)
        if result is not None:
            return result
    return sol(*args, **kwargs)


# ---------------------------------------------------------------------------
# Shared engine (day 97's MCMF) + shared model builder
# ---------------------------------------------------------------------------

class _MCMF:
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

    def run(self, source, sink, limit=INF):
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
                break
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


def _model(workers, tasks, costs, forbidden=()):
    """
    Build the standard three-layer network and solve it.

    source -> worker  (cap = capacity, cost 0)   "how much work you can absorb"
    worker -> task    (cap = 1,        cost c)   "you may fill one slot of it"
    task   -> sink    (cap = demand,   cost 0)   "how many people this needs"

    Returns (sent, needed, cost, pairs).
    """
    forbidden = set(forbidden)
    ws = sorted(workers)
    ts = sorted(tasks)
    wi = {w: i for i, w in enumerate(ws)}
    ti = {t: len(ws) + j for j, t in enumerate(ts)}
    src, snk = len(ws) + len(ts), len(ws) + len(ts) + 1

    g = _MCMF(snk + 1)
    for w in ws:
        g.add_edge(src, wi[w], workers[w], 0)
    for t in ts:
        g.add_edge(ti[t], snk, tasks[t], 0)
    edge = {}
    for (w, t), c in costs.items():
        if w in workers and t in tasks and (w, t) not in forbidden:
            edge[(w, t)] = g.add_edge(wi[w], ti[t], 1, c)

    needed = sum(tasks.values())
    sent, cost = g.run(src, snk, needed)
    pairs = sorted(p for p, idx in edge.items() if g.flow_on(idx) > 0)
    return sent, needed, cost, pairs


# ---------------------------------------------------------------------------
# Exercise 1: cost-minimising assignment
# ---------------------------------------------------------------------------

def assign(workers, tasks, costs):
    """
    Return (feasible, total_cost, pairs) with pairs sorted.

    `feasible` is False when some task slot could not be staffed. The cost is
    still reported — it is the cost of the partial plan, and it will look
    misleadingly good.
    """
    # TODO: build source->worker->task->sink and run min-cost max-flow
    pass


def _sol_assign(workers, tasks, costs):
    sent, needed, cost, pairs = _model(workers, tasks, costs)
    return sent == needed, cost, pairs


# ---------------------------------------------------------------------------
# Exercise 2: forbidden pairs
# ---------------------------------------------------------------------------

def assign_forbidden(workers, tasks, costs, forbidden):
    """
    Same as `assign`, but every pair in `forbidden` is off the table no matter
    how cheap it is. Return (feasible, total_cost, pairs).
    """
    # TODO: a veto is not a large cost — it is a missing edge
    pass


def _sol_assign_forbidden(workers, tasks, costs, forbidden):
    # Deleting the edge, rather than pricing it at 10**9, is what keeps
    # "impossible" distinguishable from "very expensive" in the result.
    sent, needed, cost, pairs = _model(workers, tasks, costs, forbidden)
    return sent == needed, cost, pairs


# ---------------------------------------------------------------------------
# Exercise 3: pinned pairs
# ---------------------------------------------------------------------------

def assign_pinned(workers, tasks, costs, pinned):
    """
    Same as `assign`, but every pair in `pinned` MUST appear in the answer.
    Return (feasible, total_cost, pairs), pairs including the pinned ones.
    Return (False, 0, []) if a pin is impossible (unpriced, or no capacity).
    """
    # TODO: spend the pinned capacity and budget first, optimise the remainder
    pass


def _sol_assign_pinned(workers, tasks, costs, pinned):
    cap = dict(workers)
    demand = dict(tasks)
    fixed_cost = 0
    for w, t in pinned:
        if (w, t) not in costs or cap.get(w, 0) <= 0 or demand.get(t, 0) <= 0:
            return False, 0, []
        cap[w] -= 1
        demand[t] -= 1
        fixed_cost += costs[(w, t)]
    # A pinned pair has been consumed, so remove it from what the optimiser may
    # still choose — otherwise the same pair can be selected a second time.
    rest = {k: v for k, v in costs.items() if k not in set(pinned)}
    sent, needed, cost, pairs = _model(cap, demand, rest)
    return sent == needed, fixed_cost + cost, sorted(list(pinned) + pairs)


# ---------------------------------------------------------------------------
# Exercise 4: where the plan falls short
# ---------------------------------------------------------------------------

def unfilled(workers, tasks, costs):
    """
    Return {task: number of slots left unstaffed}, omitting fully staffed
    tasks. An empty dict means the plan is complete.
    """
    # TODO: solve, then count how many slots of each task received flow
    pass


def _sol_unfilled(workers, tasks, costs):
    _, _, _, pairs = _model(workers, tasks, costs)
    got = {}
    for _w, t in pairs:
        got[t] = got.get(t, 0) + 1
    return {t: tasks[t] - got.get(t, 0) for t in tasks if tasks[t] > got.get(t, 0)}


# ---------------------------------------------------------------------------
# Exercise 5: validate a proposed plan
# ---------------------------------------------------------------------------

def validate(workers, tasks, costs, pairs, forbidden=()):
    """
    Check a plan someone else produced. Return a SORTED list of violation
    strings; an empty list means the plan is legal.

    Emit exactly these strings:
      "unknown worker: <w>"          worker not in `workers`
      "unknown task: <t>"            task not in `tasks`
      "unpriced pair: <w>/<t>"       pair has no cost
      "forbidden pair: <w>/<t>"      pair is vetoed
      "duplicate pair: <w>/<t>"      the same pair appears twice
      "over capacity: <w>"           worker took more tasks than capacity
      "wrong demand: <t>"            task got more or fewer workers than demand

    An UNKNOWN worker never also gets "over capacity" — it already has its own
    violation, and stacking a derived error on top only buries the real one.

    A solver you cannot check is a solver you cannot trust.
    """
    # TODO: accumulate every violation; do not stop at the first one
    pass


def _sol_validate(workers, tasks, costs, pairs, forbidden=()):
    forbidden = set(forbidden)
    problems = set()
    load = {}
    filled = {}
    seen = set()
    for w, t in pairs:
        if w not in workers:
            problems.add(f"unknown worker: {w}")
        if t not in tasks:
            problems.add(f"unknown task: {t}")
        if (w, t) in seen:
            problems.add(f"duplicate pair: {w}/{t}")
        seen.add((w, t))
        if (w, t) in forbidden:
            problems.add(f"forbidden pair: {w}/{t}")
        elif (w, t) not in costs:
            problems.add(f"unpriced pair: {w}/{t}")
        load[w] = load.get(w, 0) + 1
        filled[t] = filled.get(t, 0) + 1
    for w, n in load.items():
        # Only known workers can be OVER capacity; an unknown one already got
        # its own violation and has no capacity to exceed. Reporting both just
        # buries the real problem.
        if w in workers and n > workers[w]:
            problems.add(f"over capacity: {w}")
    # Under-staffing is as much a violation as over-staffing: a plan that
    # quietly drops a task is not a cheaper plan, it is a different one.
    for t, need in tasks.items():
        if filled.get(t, 0) != need:
            problems.add(f"wrong demand: {t}")
    return sorted(problems)


# ---------------------------------------------------------------------------
# Exercise 6: brute-force ground truth
# ---------------------------------------------------------------------------

def brute_force_cost(workers, tasks, costs, forbidden=()):
    """
    Exhaustive optimum for tiny instances, or None if no legal plan exists.

    Expand each task into `demand` slots and each worker into `capacity` slots,
    then try every injective map from task slots to worker slots. A
    (worker, task) pair may be used at most once — mirroring the capacity-1
    edge in the network.
    """
    # TODO: expand to slots, permute, keep the cheapest legal total
    pass


def _sol_brute_force_cost(workers, tasks, costs, forbidden=()):
    forbidden = set(forbidden)
    task_slots = []
    for t in sorted(tasks):
        task_slots.extend([t] * tasks[t])
    worker_slots = []
    for w in sorted(workers):
        worker_slots.extend([w] * workers[w])
    if len(task_slots) > len(worker_slots):
        return None
    best = INF
    for combo in permutations(range(len(worker_slots)), len(task_slots)):
        total = 0
        used = set()
        ok = True
        for si, wi in enumerate(combo):
            w, t = worker_slots[wi], task_slots[si]
            if (w, t) not in costs or (w, t) in forbidden or (w, t) in used:
                ok = False
                break
            used.add((w, t))
            total += costs[(w, t)]
        if ok:
            best = min(best, total)
    return None if best == INF else best


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def run_tests():
    passed = 0
    failed = 0

    def check(name, got, expected):
        nonlocal passed, failed
        if got == expected:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name}  got={got}  expected={expected}")
            failed += 1

    W = {"ana": 1, "ben": 1, "cara": 1}
    T = {"deploy": 1, "oncall": 1, "review": 1}
    C = {
        ("ana", "deploy"): 4, ("ana", "review"): 1, ("ana", "oncall"): 3,
        ("ben", "deploy"): 2, ("ben", "review"): 0, ("ben", "oncall"): 5,
        ("cara", "deploy"): 3, ("cara", "review"): 2, ("cara", "oncall"): 2,
    }

    print("Exercise 1: assign")
    feasible, cost, pairs = try_or_sol("assign", W, T, C)
    check("feasible", feasible, True)
    check("optimal cost", cost, 5)
    check("every task staffed",
          sorted(t for _w, t in pairs), ["deploy", "oncall", "review"])
    check("every worker used once",
          sorted(w for w, _t in pairs), ["ana", "ben", "cara"])
    # An unpriced pair is ineligible, so this instance cannot be staffed at all.
    check("unpriced pair is not offered",
          try_or_sol("assign", {"ana": 1}, {"deploy": 1}, {})[0], False)

    print("\nExercise 2: assign_forbidden")
    f1, c1, p1 = try_or_sol("assign_forbidden", W, T, C, [("ana", "review")])
    check("still feasible", f1, True)
    check("vetoed pair absent", ("ana", "review") in p1, False)
    check("cost rose to 6", c1, 6)
    # Constraints never help: the constrained optimum is >= the free optimum.
    check("a constraint cannot lower the cost", c1 >= cost, True)
    f2, _c2, _p2 = try_or_sol(
        "assign_forbidden", {"ana": 1}, {"deploy": 1},
        {("ana", "deploy"): 1}, [("ana", "deploy")])
    check("vetoing the only option is infeasible", f2, False)

    print("\nExercise 3: assign_pinned")
    f3, c3, p3 = try_or_sol("assign_pinned", W, T, C, [("ana", "oncall")])
    check("pin honoured", ("ana", "oncall") in p3, True)
    check("feasible with the pin", f3, True)
    check("pinned cost", c3, 6)
    check("no worker doubled up", len(set(w for w, _t in p3)), 3)
    f4, _c4, _p4 = try_or_sol("assign_pinned", W, T, C, [("ana", "nonesuch")])
    check("impossible pin reported", f4, False)

    print("\nExercise 4: unfilled")
    check("complete plan has nothing unfilled", try_or_sol("unfilled", W, T, C), {})
    check("one worker, two tasks",
          try_or_sol("unfilled", {"ana": 1}, {"deploy": 1, "review": 1},
                     {("ana", "deploy"): 1, ("ana", "review"): 1}),
          {"review": 1})
    # Capacity 5 does not help: demand 2 needs two DIFFERENT people.
    check("demand 2 with only one eligible worker",
          try_or_sol("unfilled", {"ana": 5}, {"deploy": 2},
                     {("ana", "deploy"): 1}),
          {"deploy": 1})

    print("\nExercise 5: validate")
    good = [("ana", "review"), ("ben", "deploy"), ("cara", "oncall")]
    check("legal plan has no violations", try_or_sol("validate", W, T, C, good), [])
    check("over capacity caught",
          try_or_sol("validate", W, T, C,
                     [("ana", "review"), ("ana", "deploy"), ("cara", "oncall")]),
          ["over capacity: ana"])
    check("under-staffed task caught",
          try_or_sol("validate", W, T, C, [("ana", "review"), ("ben", "deploy")]),
          ["wrong demand: oncall"])
    check("forbidden pair caught",
          try_or_sol("validate", W, T, C, good, [("ana", "review")]),
          ["forbidden pair: ana/review"])
    check("unpriced pair caught",
          try_or_sol("validate", {"ana": 1}, {"deploy": 1}, {},
                     [("ana", "deploy")]),
          ["unpriced pair: ana/deploy"])
    check("unknown worker caught",
          try_or_sol("validate", {"ana": 1}, {"deploy": 1},
                     {("ana", "deploy"): 1}, [("zed", "deploy")]),
          ["unknown worker: zed", "unpriced pair: zed/deploy"])
    check("the solver's own output validates clean",
          try_or_sol("validate", W, T, C, pairs), [])

    print("\nExercise 6: brute_force_cost")
    check("matches the flow answer", try_or_sol("brute_force_cost", W, T, C), 5)
    check("matches under a veto",
          try_or_sol("brute_force_cost", W, T, C, [("ana", "review")]), 6)
    check("infeasible returns None",
          try_or_sol("brute_force_cost", {"ana": 1},
                     {"deploy": 1, "review": 1},
                     {("ana", "deploy"): 1, ("ana", "review"): 1}),
          None)
    # Capacity 2 lets one worker cover two tasks — the flow model and the
    # slot-expansion model must agree about that.
    W2 = {"ana": 2, "ben": 1}
    T2 = {"deploy": 1, "oncall": 1, "review": 1}
    C2 = {("ana", "deploy"): 1, ("ana", "review"): 1, ("ana", "oncall"): 9,
          ("ben", "deploy"): 8, ("ben", "review"): 8, ("ben", "oncall"): 2}
    check("capacity 2 handled", try_or_sol("brute_force_cost", W2, T2, C2), 4)
    check("flow agrees with brute force on capacity 2",
          try_or_sol("assign", W2, T2, C2)[1], 4)
    # Demand 2 must be filled by two DIFFERENT people.
    W3 = {"ana": 5, "ben": 5}
    T3 = {"deploy": 2}
    C3 = {("ana", "deploy"): 5, ("ben", "deploy"): 7}
    check("demand 2 needs two distinct workers",
          try_or_sol("brute_force_cost", W3, T3, C3), 12)
    check("flow agrees on distinctness", try_or_sol("assign", W3, T3, C3)[1], 12)

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    print('='*50)


if __name__ == "__main__":
    run_tests()
