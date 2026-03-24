"""
Day 49: Ordered Key-Value Store with Range Queries
====================================================
A complete ordered key-value store backed by an AVL tree.

This is the same abstraction behind:
    Redis ZSET     — leaderboards, score ranges
    Database index — WHERE col BETWEEN x AND y
    Time-series DB — all events in a time window

Hash tables give O(1) point lookups but destroy key ordering.
BSTs preserve ordering, enabling range queries, rank, floor/ceil —
operations that would cost O(n) or O(n log n) with a hash table.

The AVL tree guarantees O(log n) for all operations via height
balancing. Nodes are augmented with subtree sizes for O(log n)
rank and select.

A transaction log records every mutation for crash recovery.
"""

import time


# ─── AVL Node ──────────────────────────────────────────────────────

class _AVLNode:
    """
    AVL tree node augmented with subtree size.

    The size field stores the count of nodes in this subtree (including self).
    This enables O(log n) rank and select without touching every node.

    Height field maintains the AVL invariant: |left.height - right.height| <= 1.
    """
    __slots__ = ('key', 'value', 'left', 'right', 'height', 'size')

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1   # leaf height is 1
        self.size = 1     # leaf has 1 node (itself)


# ─── AVL Tree (internal engine) ──────────────────────────────────

def _height(node):
    """Height of a node. None has height 0."""
    return node.height if node else 0


def _size(node):
    """Subtree size. None has size 0."""
    return node.size if node else 0


def _update(node):
    """Recompute height and size from children. Called after rotations."""
    node.height = 1 + max(_height(node.left), _height(node.right))
    node.size = 1 + _size(node.left) + _size(node.right)


def _balance_factor(node):
    """Left height minus right height. Must be in {-1, 0, 1} for AVL."""
    return _height(node.left) - _height(node.right)


def _rotate_right(y):
    """
    Right rotation around y:

        y             x
       / \           / \
      x   C  →     A    y
     / \                / \
    A   B              B   C
    """
    x = y.left
    b = x.right
    x.right = y
    y.left = b
    _update(y)
    _update(x)
    return x


def _rotate_left(x):
    """
    Left rotation around x:

        x             y
       / \           / \
      A   y   →    x    C
         / \      / \
        B   C    A   B
    """
    y = x.right
    b = y.left
    y.left = x
    x.right = b
    _update(x)
    _update(y)
    return y


def _rebalance(node):
    """
    Rebalance a node after insertion or deletion.

    Four cases based on balance factor and child balance:
        Left-Left   → single right rotation
        Left-Right  → left rotate child, then right rotate node
        Right-Right → single left rotation
        Right-Left  → right rotate child, then left rotate node
    """
    _update(node)
    bf = _balance_factor(node)

    # Left-heavy
    if bf > 1:
        if _balance_factor(node.left) < 0:
            # Left-Right case: straighten first
            node.left = _rotate_left(node.left)
        return _rotate_right(node)

    # Right-heavy
    if bf < -1:
        if _balance_factor(node.right) > 0:
            # Right-Left case: straighten first
            node.right = _rotate_right(node.right)
        return _rotate_left(node)

    return node


def _insert(node, key, value):
    """Insert key-value into subtree rooted at node. Returns new root."""
    if node is None:
        return _AVLNode(key, value)

    if key < node.key:
        node.left = _insert(node.left, key, value)
    elif key > node.key:
        node.right = _insert(node.right, key, value)
    else:
        # Key exists — update value in place
        node.value = value
        return node

    return _rebalance(node)


def _find_min(node):
    """Find the node with the smallest key in this subtree."""
    while node.left is not None:
        node = node.left
    return node


def _delete(node, key):
    """Delete key from subtree rooted at node. Returns new root."""
    if node is None:
        return None

    if key < node.key:
        node.left = _delete(node.left, key)
    elif key > node.key:
        node.right = _delete(node.right, key)
    else:
        # Found the node to delete
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        # Two children: replace with in-order successor (min of right subtree)
        successor = _find_min(node.right)
        node.key = successor.key
        node.value = successor.value
        node.right = _delete(node.right, successor.key)

    return _rebalance(node)


def _search(node, key):
    """Find node with given key. Returns None if not found."""
    while node is not None:
        if key < node.key:
            node = node.left
        elif key > node.key:
            node = node.right
        else:
            return node
    return None


def _floor_node(node, key):
    """
    Find the node with the largest key <= given key.

    Algorithm: walk down the tree. When we go right, the current node
    is a candidate (it's <= key). When we go left, it's too big.
    """
    result = None
    while node is not None:
        if key == node.key:
            return node
        elif key < node.key:
            node = node.left
        else:
            # node.key < key — this node is a candidate
            result = node
            node = node.right
    return result


def _ceil_node(node, key):
    """
    Find the node with the smallest key >= given key.

    Mirror of floor: when we go left, the current node is a candidate.
    """
    result = None
    while node is not None:
        if key == node.key:
            return node
        elif key > node.key:
            node = node.right
        else:
            # node.key > key — this node is a candidate
            result = node
            node = node.left
    return result


def _range_collect(node, lo, hi, result):
    """
    Collect all (key, value) pairs where lo <= key <= hi.

    Uses in-order traversal with pruning:
    - If node.key > lo, there may be valid keys in the left subtree
    - If lo <= node.key <= hi, include this node
    - If node.key < hi, there may be valid keys in the right subtree
    """
    if node is None:
        return
    if node.key > lo:
        _range_collect(node.left, lo, hi, result)
    if lo <= node.key <= hi:
        result.append((node.key, node.value))
    if node.key < hi:
        _range_collect(node.right, lo, hi, result)


def _rank(node, key):
    """
    Count keys strictly less than given key.

    Uses subtree sizes: when going right past a node, all keys in its
    left subtree (plus the node itself) are smaller than our target.
    """
    count = 0
    while node is not None:
        if key < node.key:
            node = node.left
        elif key > node.key:
            # Everything in left subtree + this node is less than key
            count += _size(node.left) + 1
            node = node.right
        else:
            # Found the key — left subtree size is the rank
            count += _size(node.left)
            break
    return count


def _select(node, k):
    """
    Find the kth smallest key (0-indexed).

    Uses subtree sizes to navigate:
    - If k < left_size, the answer is in the left subtree
    - If k == left_size, this node is the answer
    - If k > left_size, search right with adjusted k
    """
    while node is not None:
        left_size = _size(node.left)
        if k < left_size:
            node = node.left
        elif k == left_size:
            return node
        else:
            k -= left_size + 1
            node = node.right
    return None


def _inorder(node, result):
    """Collect all keys via in-order traversal (sorted order)."""
    if node is None:
        return
    _inorder(node.left, result)
    result.append(node.key)
    _inorder(node.right, result)


# ─── Ordered Key-Value Store ─────────────────────────────────────

class OrderedKVStore:
    """
    An ordered key-value store backed by an AVL tree.

    Supports all point operations (put, get, delete) plus order-aware
    operations (min, max, floor, ceil, range, rank, select) that are
    impossible to do efficiently with a hash table.

    Includes a transaction log for crash recovery demonstration.
    """

    def __init__(self):
        self._root = None
        self._log = []   # transaction log: list of (operation, key, value) tuples

    # ── Point Operations ──

    def put(self, key, value):
        """Insert or update a key-value pair. O(log n)."""
        self._log.append(("put", key, value))
        self._root = _insert(self._root, key, value)

    def get(self, key):
        """
        Retrieve the value for a key. Returns None if not found. O(log n).

        A hash table does this in O(1), but cannot do anything below.
        """
        node = _search(self._root, key)
        return node.value if node else None

    def delete(self, key):
        """Remove a key from the store. O(log n). No-op if key absent."""
        self._log.append(("delete", key, None))
        self._root = _delete(self._root, key)

    def contains(self, key):
        """Check if key exists. O(log n)."""
        return _search(self._root, key) is not None

    # ── Order Operations ──

    def min_key(self):
        """Return the smallest key. O(log n). Raises ValueError if empty."""
        if self._root is None:
            raise ValueError("Store is empty")
        node = self._root
        while node.left is not None:
            node = node.left
        return node.key

    def max_key(self):
        """Return the largest key. O(log n). Raises ValueError if empty."""
        if self._root is None:
            raise ValueError("Store is empty")
        node = self._root
        while node.right is not None:
            node = node.right
        return node.key

    def floor(self, key):
        """
        Return the largest key <= given key, or None if no such key.

        Example: keys = {1, 3, 5, 7}
            floor(4) = 3   (largest key not exceeding 4)
            floor(5) = 5   (exact match counts)
            floor(0) = None (nothing <= 0)

        Hash tables cannot do this without sorting all keys: O(n log n).
        AVL tree does it in O(log n) by walking down the tree.
        """
        node = _floor_node(self._root, key)
        return node.key if node else None

    def ceil(self, key):
        """
        Return the smallest key >= given key, or None if no such key.

        Example: keys = {1, 3, 5, 7}
            ceil(4) = 5   (smallest key not less than 4)
            ceil(5) = 5   (exact match counts)
            ceil(8) = None (nothing >= 8)
        """
        node = _ceil_node(self._root, key)
        return node.key if node else None

    def range_query(self, lo, hi):
        """
        Return all (key, value) pairs where lo <= key <= hi, in sorted order.

        This is THE operation that justifies using a tree over a hash table.
        Complexity: O(log n + k) where k is the number of results.
        A hash table would need O(n) to scan all keys.

        Use cases:
            - "All users with scores between 90 and 100"
            - "All events between 2pm and 5pm"
            - "All products priced $10-$50"
        """
        result = []
        _range_collect(self._root, lo, hi, result)
        return result

    def rank(self, key):
        """
        Return the number of keys strictly less than given key. O(log n).

        Uses augmented subtree sizes — no traversal needed.

        Example: keys = {A, C, E, G}
            rank(A) = 0   (nothing less than A)
            rank(D) = 2   (A, C are less than D)
            rank(Z) = 4   (all 4 keys are less than Z)
        """
        return _rank(self._root, key)

    def select(self, k):
        """
        Return the kth smallest key (0-indexed). O(log n).

        Uses augmented subtree sizes to navigate directly.

        Example: keys = {A, C, E, G}
            select(0) = A  (smallest)
            select(2) = E  (3rd smallest)
            select(3) = G  (largest)

        Raises IndexError if k is out of range.
        """
        if k < 0 or k >= self.size():
            raise IndexError(f"select({k}) out of range for store of size {self.size()}")
        node = _select(self._root, k)
        return node.key

    # ── Utility ──

    def size(self):
        """Number of key-value pairs in the store."""
        return _size(self._root)

    def is_empty(self):
        """True if the store has no keys."""
        return self._root is None

    def keys(self):
        """Return all keys in sorted order. O(n) — full in-order traversal."""
        result = []
        _inorder(self._root, result)
        return result

    # ── Transaction Log ──

    def get_log(self):
        """Return the transaction log (list of operation tuples)."""
        return list(self._log)

    @classmethod
    def replay(cls, log):
        """
        Rebuild a store from a transaction log.

        This is crash recovery: if the process dies, the log (persisted to disk
        in a real system) contains every operation needed to reconstruct state.

        Real-world equivalents:
            Redis AOF  — append-only file replayed on restart
            PostgreSQL WAL — write-ahead log replayed after crash
            Kafka — event log replayed to rebuild state
        """
        store = cls()
        store._log = []  # fresh log during replay
        for entry in log:
            op = entry[0]
            if op == "put":
                store.put(entry[1], entry[2])
            elif op == "delete":
                store.delete(entry[1])
        return store

    # ── Performance Comparison ──

    @staticmethod
    def benchmark(n=50000):
        """
        Compare ordered store vs Python dict performance.

        Measures ops/sec for insert, lookup, and demonstrates operations
        that are fast on the ordered store but slow on a dict.
        """
        import random

        keys = list(range(n))
        random.shuffle(keys)

        print(f"Benchmark: {n} operations\n")

        # ── Insert ──
        store = OrderedKVStore()
        t0 = time.perf_counter()
        for k in keys:
            store.put(k, k * 10)
        t_store_insert = time.perf_counter() - t0

        d = {}
        t0 = time.perf_counter()
        for k in keys:
            d[k] = k * 10
        t_dict_insert = time.perf_counter() - t0

        print(f"Insert {n} keys:")
        print(f"  OrderedKVStore: {n / t_store_insert:>12,.0f} ops/sec")
        print(f"  Python dict:    {n / t_dict_insert:>12,.0f} ops/sec")
        print(f"  Dict is {t_store_insert / t_dict_insert:.1f}x faster (expected — hash vs tree)\n")

        # ── Lookup ──
        random.shuffle(keys)
        t0 = time.perf_counter()
        for k in keys:
            store.get(k)
        t_store_lookup = time.perf_counter() - t0

        t0 = time.perf_counter()
        for k in keys:
            _ = d.get(k)
        t_dict_lookup = time.perf_counter() - t0

        print(f"Lookup {n} keys:")
        print(f"  OrderedKVStore: {n / t_store_lookup:>12,.0f} ops/sec")
        print(f"  Python dict:    {n / t_dict_lookup:>12,.0f} ops/sec")
        print(f"  Dict is {t_store_lookup / t_dict_lookup:.1f}x faster\n")

        # ── Operations dict CANNOT do efficiently ──
        print("Order-aware operations (dict cannot do these in O(log n)):\n")

        t0 = time.perf_counter()
        for _ in range(1000):
            store.min_key()
        t_min = time.perf_counter() - t0
        print(f"  min_key (1000x):     {1000 / t_min:>10,.0f} ops/sec")

        t0 = time.perf_counter()
        for _ in range(1000):
            min(d.keys())
        t_min_dict = time.perf_counter() - t0
        print(f"  min(dict) (1000x):   {1000 / t_min_dict:>10,.0f} ops/sec")
        print(f"  Ordered store is {t_min_dict / t_min:.1f}x faster for min\n")

        t0 = time.perf_counter()
        for _ in range(1000):
            store.range_query(n // 4, n // 2)
        t_range = time.perf_counter() - t0
        range_size = len(store.range_query(n // 4, n // 2))
        print(f"  range_query [{n//4}, {n//2}] ({range_size} results, 1000x): {1000 / t_range:>8,.0f} ops/sec")

        t0 = time.perf_counter()
        for _ in range(1000):
            [(k, d[k]) for k in sorted(d) if n // 4 <= k <= n // 2]
        t_range_dict = time.perf_counter() - t0
        print(f"  dict range (sort+filter, 1000x):                {1000 / t_range_dict:>8,.0f} ops/sec")
        print(f"  Ordered store is {t_range_dict / t_range:.1f}x faster for range queries\n")

        t0 = time.perf_counter()
        for _ in range(1000):
            store.rank(n // 2)
        t_rank = time.perf_counter() - t0
        print(f"  rank({n//2}) (1000x):  {1000 / t_rank:>10,.0f} ops/sec")

        t0 = time.perf_counter()
        for _ in range(1000):
            sum(1 for k in d if k < n // 2)
        t_rank_dict = time.perf_counter() - t0
        print(f"  dict rank (1000x):    {1000 / t_rank_dict:>10,.0f} ops/sec")
        print(f"  Ordered store is {t_rank_dict / t_rank:.1f}x faster for rank\n")

    def __repr__(self):
        if self.is_empty():
            return "OrderedKVStore(empty)"
        keys = self.keys()
        if len(keys) <= 10:
            return f"OrderedKVStore({dict(self.range_query(keys[0], keys[-1]))})"
        return f"OrderedKVStore(size={self.size()}, min={keys[0]}, max={keys[-1]})"


# ─── Demo ─────────────────────────────────────────────────────────

def demo_leaderboard():
    """
    Realistic use case: a game leaderboard.

    Players have scores. We need:
    - Add/update player scores
    - Top N players (select from the end)
    - Player rank
    - Score range queries
    - Floor/ceil for "nearest score" lookups

    A hash table (player_name -> score) cannot do rank or range queries
    efficiently. We key by score for ordering, but this means we need
    unique keys — so we use (score, player_name) tuples as keys.
    Tuples compare lexicographically: first by score, then by name.
    """
    print("=" * 60)
    print("LEADERBOARD DEMO")
    print("=" * 60)

    store = OrderedKVStore()

    # Add player scores — key is (score, name) for unique ordering
    players = [
        (1500, "Alice"), (1350, "Bob"), (1720, "Charlie"),
        (1450, "Diana"), (1600, "Eve"), (1280, "Frank"),
        (1550, "Grace"), (1680, "Hank"), (1400, "Ivy"),
        (1750, "Jack"),
    ]

    print("\nAdding players to leaderboard...")
    for score, name in players:
        store.put((score, name), {"name": name, "score": score})
        print(f"  {name}: {score}")

    print(f"\nLeaderboard size: {store.size()}")
    print(f"Lowest score:  {store.min_key()[0]} ({store.min_key()[1]})")
    print(f"Highest score: {store.max_key()[0]} ({store.max_key()[1]})")

    # Top 3 players (3 highest scores)
    print("\n--- Top 3 Players ---")
    for i in range(store.size() - 1, max(store.size() - 4, -1), -1):
        key = store.select(i)
        val = store.get(key)
        rank = store.size() - i
        print(f"  #{rank}: {val['name']} — {val['score']} pts")

    # Range query: all players with scores between 1400 and 1600
    print("\n--- Players scoring 1400-1600 ---")
    results = store.range_query((1400, ""), (1600, "~"))  # ~ sorts after all letters
    for key, val in results:
        print(f"  {val['name']}: {val['score']} pts")

    # Rank of a specific player
    target = (1550, "Grace")
    r = store.rank(target)
    print(f"\nGrace's rank from bottom: {r + 1} (out of {store.size()})")
    print(f"Grace's rank from top:    {store.size() - r}")

    # Floor: highest score <= 1500
    f = store.floor((1500, "~"))
    print(f"\nHighest score <= 1500: {f[1]} ({f[0]})")

    # Ceil: lowest score >= 1500
    c = store.ceil((1500, ""))
    print(f"Lowest score >= 1500:  {c[1]} ({c[0]})")

    # Transaction log and crash recovery
    print("\n--- Crash Recovery Demo ---")
    log = store.get_log()
    print(f"Transaction log has {len(log)} entries")

    # Simulate crash: rebuild from log
    recovered = OrderedKVStore.replay(log)
    print(f"Recovered store size: {recovered.size()}")
    print(f"Recovery matches original: {recovered.keys() == store.keys()}")

    # Show sorted leaderboard
    print("\n--- Full Leaderboard (sorted) ---")
    for i, key in enumerate(reversed(store.keys())):
        val = store.get(key)
        print(f"  #{i+1:2d}. {val['name']:>8s}  {val['score']} pts")


def demo_timeseries():
    """
    Realistic use case: time-series event store.

    Events keyed by timestamp. Range queries find all events in a window.
    """
    print("\n" + "=" * 60)
    print("TIME-SERIES DEMO")
    print("=" * 60)

    store = OrderedKVStore()

    events = [
        (1000, "server_start"),
        (1005, "db_connected"),
        (1010, "first_request"),
        (1012, "cache_miss"),
        (1015, "cache_populated"),
        (1020, "spike_detected"),
        (1025, "autoscale_triggered"),
        (1030, "new_instance_up"),
        (1045, "spike_resolved"),
        (1060, "health_check_ok"),
    ]

    print("\nRecording events...")
    for ts, event in events:
        store.put(ts, event)

    # Query: all events between t=1010 and t=1030
    print("\nEvents between t=1010 and t=1030:")
    for ts, event in store.range_query(1010, 1030):
        print(f"  t={ts}: {event}")

    # What event happened just before t=1018?
    f = store.floor(1018)
    print(f"\nEvent just before t=1018: t={f} → {store.get(f)}")

    # What event happened just after t=1018?
    c = store.ceil(1018)
    print(f"Event just after t=1018:  t={c} → {store.get(c)}")

    # How many events before t=1020?
    print(f"\nEvents before t=1020: {store.rank(1020)}")
    print(f"Total events: {store.size()}")


if __name__ == "__main__":
    demo_leaderboard()
    demo_timeseries()

    print("\n" + "=" * 60)
    print("PERFORMANCE BENCHMARK")
    print("=" * 60)
    OrderedKVStore.benchmark(n=20000)
