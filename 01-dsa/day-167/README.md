# Day 167: Rate Limiting

## Why Rate Limiting Exists

Every public API gets abused: scrapers, runaway scripts, accidental
infinite retry loops, DDoS, neighbors-of-noisy-neighbors on shared
infra. Without enforcement:

- A single client can saturate CPU, sockets, DB connections.
- Costs explode (egress, LLM API per-token billing, S3 GET fees).
- SLOs collapse for legitimate users.

Rate limiting answers: "is this request allowed *right now*?" in O(1)
with a bounded amount of per-client state.

Four canonical algorithms, each with different burst / smoothness /
memory trade-offs.

## 1. Token Bucket

Bucket holds up to `B` tokens. Refill at `R` tokens/sec. Each request
costs 1 token (or more for heavier ops).

- If `tokens >= cost`: deduct, allow.
- Else: deny (or queue).

**Bursty traffic OK** up to bucket size B. Long-run rate capped at R.

Used by AWS API Gateway, Stripe, GitHub (the famous 5000/hour limit is
token bucket).

## 2. Leaky Bucket

Bucket fills at any rate, but drains at constant rate D. If bucket would
overflow, deny.

Smooths bursts into a constant outflow. Used in network traffic shaping
(token bucket is bursty; leaky bucket is paced). Classic in QoS gear and
old-school telecom.

## 3. Fixed Window Counter

Count requests per `(client, current_window)`. Reset at window boundary.

Simple but **double-burst at boundaries**: 100 requests at second 59.999
of one window + 100 more at second 0.001 of the next = 200 in <1ms even
though the "limit" is 100/min.

Use when: low-cost, low-precision (e.g. spam protection on signup forms).

## 4. Sliding Window Counter

Approximate fix to fixed-window. Keep counts for current and previous
window. Weight the previous window by `(1 - elapsed_fraction)`.

```
elapsed = 30s into a 60s window
allowed = current_count + prev_count * (1 - 30/60)
        = current_count + prev_count * 0.5
```

Cheap (two counters per client) and avoids the boundary double-burst.
Used by Cloudflare's docs example, Stripe internally.

## 5. Sliding Window Log

Store timestamps of every request in the last window. To check, drop
timestamps older than (now - window), count remaining.

**Most accurate.** Memory grows with request rate per client. Used when:
small client count + high precision required (e.g. fraud, payment APIs).

Redis sorted sets implement this naturally.

## Comparison

| Algorithm | Burst | Memory/client | Accuracy | Smoothing |
|-----------|-------|---------------|----------|-----------|
| Token bucket | yes, up to B | O(1) | exact | none |
| Leaky bucket | no | O(1) | exact | yes |
| Fixed window | huge spikes | O(1) | poor at edges | none |
| Sliding window counter | small | O(1) | approx | none |
| Sliding window log | configurable | O(rate * window) | exact | none |

## Distributed Rate Limiting

Single-machine algorithms are easy. With N nodes behind a load balancer:

1. **Sticky session** to a single node: simple but loses on failure.
2. **Centralized store** (Redis): atomic INCR + EXPIRE. Network hop per
   request. Used by Stripe, GitHub.
3. **Token bucket replicated**: bucket state in a quorum store. Expensive.
4. **Optimistic local + reconciliation**: each node has a quota slice;
   sync occasionally. Cheaper, less precise.

## Failure Modes

1. **Clock skew**: server clocks drift. Sliding window with `now()` can
   admit or reject incorrectly. Use monotonic time where possible.
2. **Header trust**: `X-Forwarded-For` can be spoofed. Limit on a value
   you can authenticate (API key, session id).
3. **Retry storms**: client retries on 429 with no backoff. Always
   return `Retry-After`. Implement client-side exponential backoff with
   jitter.
4. **Cardinality explosion**: limiting by URL path with high cardinality
   blows up your key count. Normalize.

## Real Systems

| System | Algorithm |
|--------|-----------|
| **Stripe API** | Token bucket per API key (100 req/s, burst 25) |
| **GitHub API** | Token bucket: 5000/hour authenticated |
| **Cloudflare** | Sliding window counter |
| **AWS API Gateway** | Token bucket (per-account or per-key) |
| **NGINX `limit_req`** | Leaky bucket |
| **Redis `rate.limit`** | Token bucket via Lua |
| **gRPC** | Per-channel token bucket built in |

## Checkpoint Questions

1. Token bucket vs leaky bucket: which one allows bursts? Why?
2. Sketch the boundary bug in fixed-window counter. How does sliding
   window counter fix it?
3. What's the memory cost of sliding window log vs sliding window counter
   at 1M req/s with a 60-second window?
4. Why is `Retry-After` important when returning 429?
5. In a 3-node cluster with a token bucket per user, what happens if
   each node has its own copy of the bucket?
6. Why not just use 429 = "drop" for everything? When would you queue
   instead?
