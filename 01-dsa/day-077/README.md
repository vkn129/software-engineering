# Day 77: Distributed Rate Limiter Mini-Project

## Week 11 Capstone — Tying Together Probabilistic Data Structures

### Why Rate Limiting Matters

Every production API needs rate limiting. Without it, three things happen:

1. **Abuse**: A single bad actor can monopolize your resources
2. **Unfair usage**: Heavy users crowd out everyone else
3. **Cascade failures**: One overloaded service brings down the entire system

Rate limiting is fundamentally a **counting problem under time constraints** — and that
connects directly to the probabilistic data structures we built in Weeks 9-10.

---

### Rate Limiting Algorithms

#### 1. Fixed Window Counter

Divide time into fixed intervals (e.g., 1-minute windows). Count requests per window.

```
Window: [00:00 - 01:00] -> count = 47/100
Window: [01:00 - 02:00] -> count = 0/100
```

**Pros**: Simple, low memory (one counter per window).
**Cons**: Boundary burst problem — 100 requests at 0:59 + 100 at 1:01 = 200 in 2 seconds.

#### 2. Sliding Window Log

Store the timestamp of every request. Count timestamps within the sliding window.

**Pros**: Exact counting, no boundary problem.
**Cons**: O(n) memory per user — stores every timestamp. Doesn't scale.

#### 3. Sliding Window Counter

Weighted combination of current and previous window:

```
rate = prev_window_count * overlap_fraction + current_window_count
```

**Pros**: Approximate but memory-efficient (two counters).
**Cons**: Not exact — but the error is bounded and predictable.

This is what most production systems use. The math:
- If window = 60s and we're 15s into the current window
- overlap_fraction = (60 - 15) / 60 = 0.75
- estimated_rate = prev_count * 0.75 + current_count

#### 4. Token Bucket

A bucket holds tokens. Each request consumes one token. Tokens refill at a constant rate.

```
bucket_size = 10      (max burst)
refill_rate = 2/sec   (sustained rate)
```

**Pros**: Allows controlled bursts, smooth rate limiting.
**Cons**: Slightly more state (token count + last refill time).

Used by: AWS API Gateway, many CDNs.

#### 5. Leaky Bucket

Requests enter a queue (bucket). The bucket "leaks" (processes) at a constant rate.
If the bucket is full, new requests are dropped.

```
bucket_size = 10     (queue capacity)
leak_rate = 2/sec    (constant output rate)
```

**Pros**: Perfectly smooth output rate — no bursts at all.
**Cons**: Doesn't accommodate legitimate burst traffic.

Used by: Network traffic shaping (e.g., ISP throttling).

---

### The Distributed Challenge

Single-server rate limiting is easy. Distributed rate limiting is hard because
**multiple servers must agree on counts**.

#### Approaches:

1. **Consistent hashing**: Route each user to the same server. That server owns the
   counter. Simple but creates hot spots if one user is heavy.

2. **Shared state (Redis)**: All servers read/write a central counter. Accurate but
   adds latency and a single point of failure.

3. **Local counting + periodic merge**: Each server maintains local state, periodically
   synchronizes. Approximate but fast and fault-tolerant.

#### Probabilistic Structures for Distributed Rate Limiting

This is where our Week 9-10 work pays off:

- **Count-Min Sketch (CMS)**: Approximate frequency counting across servers. Each
  server maintains a local CMS, periodically merges with others. Merge is just
  element-wise addition — CMS is a linear sketch.

- **Bloom Filter**: "Has this IP been seen in the last N minutes?" Fast membership
  test, no false negatives. Use time-bucketed Bloom filters (rotate every N minutes).

- **HyperLogLog**: "How many unique users hit this endpoint?" Cardinality estimation
  with ~2% error using only 12KB of memory. Perfect for monitoring dashboards.

---

### Real-World Systems

| System | Algorithm | Notes |
|--------|-----------|-------|
| **Cloudflare** | Sliding window | Per-IP, per-path rules at edge |
| **Stripe** | Token bucket | Per-API-key, generous burst for webhooks |
| **GitHub API** | Fixed window | 5000 req/hour per token, headers show remaining |
| **Redis** | Sorted sets | `ZRANGEBYSCORE` for sliding window log |
| **Nginx** | Leaky bucket | `limit_req` module, zone-based |

---

### Key Insight

Rate limiting is really about **approximate counting under time pressure**. You don't
need exact counts — you need "close enough, fast enough." That's exactly what
probabilistic data structures provide:

- CMS gives approximate counts in O(1) time and space
- Bloom filters give fast "seen before?" checks
- HyperLogLog gives cardinality with tiny memory

The error bounds are well-understood and configurable. A 1% false positive rate on
rate limiting is perfectly acceptable — it means 1 in 100 requests might be
unnecessarily throttled, which is far better than no rate limiting at all.

---

### Checkpoint Questions

1. **Why does the fixed window algorithm have a boundary burst problem, and how does
   the sliding window counter solve it?** (The transition between windows allows 2x
   the limit; weighting by overlap fraction smooths this.)

2. **When would you choose a token bucket over a leaky bucket?** (When you want to
   allow legitimate bursts — e.g., a user who saved up tokens. Leaky bucket enforces
   strict constant rate.)

3. **Why is CMS particularly well-suited for distributed rate limiting?** (Linear
   sketch — merging two CMS is just element-wise max/addition. Each server maintains
   local state, periodic merge gives global approximate counts.)

4. **What's the trade-off between centralized (Redis) and approximate (CMS-based)
   distributed rate limiting?** (Redis: exact but adds latency + SPOF. CMS: approximate
   but fast, fault-tolerant, no coordination needed.)

5. **How would you use time-bucketed Bloom filters for "has this IP been seen in the
   last 5 minutes"?** (Maintain one Bloom filter per minute. To check, query all 5.
   Every minute, discard the oldest and create a new empty one. Union of filters gives
   the sliding window.)

6. **If your rate limiter has a 1% false positive rate, what's the practical impact?**
   (1 in 100 legitimate requests gets throttled. For most APIs this is acceptable —
   the client retries with backoff. Much better than 0% rate limiting.)
