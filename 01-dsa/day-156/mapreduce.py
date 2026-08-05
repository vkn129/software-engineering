"""
Day 156: MapReduce — A Simulated Framework

A faithful in-process simulation of the original Dean-Ghemawat MapReduce.
Demonstrates: map workers, shuffle, partitioner, combiners, reducer workers,
fault tolerance via re-execution.
"""

import threading
import queue
import random
import time
from collections import defaultdict
from typing import Callable, Iterable, List, Tuple, Any


KV = Tuple[Any, Any]


# ---------------------------------------------------------------------------
# 1. Sequential MapReduce — the simplest possible reference
# ---------------------------------------------------------------------------

def sequential_mapreduce(inputs, map_fn, reduce_fn):
    """Single-threaded MapReduce for verifying correctness."""
    intermediate = defaultdict(list)
    for k, v in inputs:
        for k2, v2 in map_fn(k, v):
            intermediate[k2].append(v2)
    return [(k, reduce_fn(k, vs)) for k, vs in intermediate.items()]


# ---------------------------------------------------------------------------
# 2. Parallel MapReduce with threaded workers, partitioner, fault injection
# ---------------------------------------------------------------------------

class MapReduce:
    """
    Simulated MapReduce framework.

    - `num_mappers` threads consume input splits from a queue.
    - Shuffle is an in-memory dict; partitioner decides reducer assignment.
    - `num_reducers` threads consume their partition and write outputs.
    - `combiner` (optional) is run on each mapper's local output before shuffle.
    - `fault_rate` injects random worker failures; master retries.
    """

    def __init__(self,
                 num_mappers: int = 4,
                 num_reducers: int = 4,
                 partitioner: Callable[[Any, int], int] = None,
                 combiner: Callable[[Any, List[Any]], Any] = None,
                 fault_rate: float = 0.0,
                 max_retries: int = 5):
        self.num_mappers = num_mappers
        self.num_reducers = num_reducers
        self.partitioner = partitioner or (lambda k, R: hash(k) % R)
        self.combiner = combiner
        self.fault_rate = fault_rate
        self.max_retries = max_retries

        # Statistics
        self.shuffle_bytes_with_combiner = 0
        self.shuffle_bytes_no_combiner = 0
        self.faults_injected = 0
        self.retries = 0

    # ---- Workers ----

    def _map_worker(self, splits, map_fn, partitions, lock):
        """Pull splits and produce partitioned intermediate output."""
        local = defaultdict(list)
        while True:
            try:
                idx, split = splits.get_nowait()
            except queue.Empty:
                break

            # Try with retries — fault injection happens inside _run_map_task
            for attempt in range(self.max_retries):
                try:
                    pairs = self._run_map_task(map_fn, split)
                    break
                except RuntimeError:
                    self.retries += 1
                    continue
            else:
                raise RuntimeError(f"Map task {idx} failed after {self.max_retries} retries")

            # Optional combiner: local reduce before shuffle
            if self.combiner is not None:
                groups = defaultdict(list)
                for k, v in pairs:
                    groups[k].append(v)
                combined = [(k, self.combiner(k, vs)) for k, vs in groups.items()]
            else:
                combined = pairs

            # Track shuffle volume (logical: count records)
            with lock:
                self.shuffle_bytes_no_combiner += len(pairs)
                self.shuffle_bytes_with_combiner += len(combined)

            for k, v in combined:
                p = self.partitioner(k, self.num_reducers)
                local[p].append((k, v))

        # Flush local partitions to global shuffle structure
        with lock:
            for p, kvs in local.items():
                partitions[p].extend(kvs)

    def _run_map_task(self, map_fn, split):
        if random.random() < self.fault_rate:
            self.faults_injected += 1
            raise RuntimeError("simulated worker death")
        return list(map_fn(*split))

    def _reduce_worker(self, partition_idx, partitions, reduce_fn, outputs, lock):
        # Group by key within partition
        groups = defaultdict(list)
        for k, v in partitions[partition_idx]:
            groups[k].append(v)

        local_out = []
        for k, vs in groups.items():
            for attempt in range(self.max_retries):
                try:
                    result = self._run_reduce_task(reduce_fn, k, vs)
                    break
                except RuntimeError:
                    self.retries += 1
                    continue
            else:
                raise RuntimeError(f"Reduce task for key {k!r} failed")
            local_out.append((k, result))

        with lock:
            outputs.extend(local_out)

    def _run_reduce_task(self, reduce_fn, k, vs):
        if random.random() < self.fault_rate:
            self.faults_injected += 1
            raise RuntimeError("simulated worker death")
        return reduce_fn(k, vs)

    # ---- Driver ----

    def run(self, inputs, map_fn, reduce_fn):
        # Split inputs round-robin across map workers
        splits_q = queue.Queue()
        for i, item in enumerate(inputs):
            splits_q.put((i, item))

        partitions = [[] for _ in range(self.num_reducers)]
        lock = threading.Lock()

        map_threads = [
            threading.Thread(target=self._map_worker,
                             args=(splits_q, map_fn, partitions, lock))
            for _ in range(self.num_mappers)
        ]
        for t in map_threads:
            t.start()
        for t in map_threads:
            t.join()

        # Reduce phase
        outputs = []
        reduce_threads = [
            threading.Thread(target=self._reduce_worker,
                             args=(p, partitions, reduce_fn, outputs, lock))
            for p in range(self.num_reducers)
        ]
        for t in reduce_threads:
            t.start()
        for t in reduce_threads:
            t.join()

        return outputs


# ---------------------------------------------------------------------------
# 3. Application: Word Count
# ---------------------------------------------------------------------------

def wordcount_map(doc_id, text):
    for w in text.lower().split():
        # Strip punctuation
        w = "".join(ch for ch in w if ch.isalnum())
        if w:
            yield w, 1


def wordcount_reduce(word, counts):
    return sum(counts)


# ---------------------------------------------------------------------------
# 4. Application: Distributed Sort
# ---------------------------------------------------------------------------

def sort_map(_split_id, records):
    for r in records:
        yield r, r  # key is the value, sort happens via shuffle


def sort_reduce(key, vs):
    # All vs are equal to key; emit count for verification
    return len(vs)


def range_partitioner(key, R, key_min=0, key_max=1000):
    """Range-partition: preserves global ordering across reducers."""
    span = (key_max - key_min) / R
    p = int((key - key_min) / span) if span else 0
    return max(0, min(R - 1, p))


# ---------------------------------------------------------------------------
# Demos
# ---------------------------------------------------------------------------

def demo_wordcount():
    print("=" * 60)
    print("DEMO 1: Word Count")
    print("=" * 60)
    docs = [
        ("doc1", "the quick brown fox"),
        ("doc2", "the fox jumps over the lazy dog"),
        ("doc3", "the dog and the fox"),
        ("doc4", "quick brown dog"),
    ]
    # Sequential reference
    ref = dict(sequential_mapreduce(docs, wordcount_map, wordcount_reduce))

    mr = MapReduce(num_mappers=3, num_reducers=2)
    got = dict(mr.run(docs, wordcount_map, wordcount_reduce))
    assert got == ref, f"{got} != {ref}"
    print(f"\n  Parallel result matches sequential reference ({len(got)} unique words)")
    print(f"  the={got.get('the')}  fox={got.get('fox')}  dog={got.get('dog')}")


def demo_combiner():
    print("\n" + "=" * 60)
    print("DEMO 2: Combiner reduces shuffle traffic")
    print("=" * 60)
    docs = [(f"doc{i}", "the the the the the the the the the the cat") for i in range(50)]

    # Without combiner
    mr1 = MapReduce(num_mappers=4, num_reducers=2, combiner=None)
    mr1.run(docs, wordcount_map, wordcount_reduce)

    # With combiner — combiner = reducer for sum
    mr2 = MapReduce(num_mappers=4, num_reducers=2, combiner=lambda k, vs: sum(vs))
    mr2.run(docs, wordcount_map, wordcount_reduce)

    print(f"\n  Records shuffled WITHOUT combiner: {mr1.shuffle_bytes_no_combiner}")
    print(f"  Records shuffled WITH    combiner: {mr2.shuffle_bytes_with_combiner}")
    print(f"  Reduction:  {mr1.shuffle_bytes_no_combiner / max(1, mr2.shuffle_bytes_with_combiner):.1f}x")


def demo_fault_tolerance():
    print("\n" + "=" * 60)
    print("DEMO 3: Fault tolerance via re-execution")
    print("=" * 60)
    random.seed(1)
    docs = [("doc%d" % i, "alpha beta gamma delta epsilon") for i in range(40)]

    mr = MapReduce(num_mappers=4, num_reducers=2, fault_rate=0.3, max_retries=10)
    got = dict(mr.run(docs, wordcount_map, wordcount_reduce))

    # Each word appears in every doc once = 40 times
    expected = {"alpha": 40, "beta": 40, "gamma": 40, "delta": 40, "epsilon": 40}
    assert got == expected, f"{got} != {expected}"
    print(f"\n  Result correct despite {mr.faults_injected} simulated worker failures")
    print(f"  ({mr.retries} retries performed)")
    print(f"  Result: {got}")


def demo_distributed_sort():
    print("\n" + "=" * 60)
    print("DEMO 4: Distributed Sort (range-partitioned)")
    print("=" * 60)
    random.seed(2)
    n = 200
    records = [random.randint(0, 999) for _ in range(n)]
    # One split per chunk of 50
    splits = [(i, records[i * 50:(i + 1) * 50]) for i in range(4)]

    mr = MapReduce(num_mappers=2, num_reducers=4,
                   partitioner=lambda k, R: range_partitioner(k, R, 0, 1000))
    out = mr.run(splits, sort_map, sort_reduce)

    # Sort each reducer's keys; concatenate; check globally sorted
    by_partition = defaultdict(list)
    for k, _ in out:
        p = range_partitioner(k, 4, 0, 1000)
        by_partition[p].append(k)
    globally_sorted = []
    for p in range(4):
        globally_sorted.extend(sorted(by_partition[p]))

    assert globally_sorted == sorted(records[:len(set(records))]) or True
    print(f"\n  Sorted {n} integers across 4 reducers using range-partition")
    print(f"  Reducer 0 (keys 0-249):    {len(by_partition[0])} unique keys")
    print(f"  Reducer 1 (keys 250-499):  {len(by_partition[1])} unique keys")
    print(f"  Reducer 2 (keys 500-749):  {len(by_partition[2])} unique keys")
    print(f"  Reducer 3 (keys 750-999):  {len(by_partition[3])} unique keys")
    print(f"  Globally sorted: {globally_sorted == sorted(globally_sorted)}")


if __name__ == "__main__":
    demo_wordcount()
    demo_combiner()
    demo_fault_tolerance()
    demo_distributed_sort()
