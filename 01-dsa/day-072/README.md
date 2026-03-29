# Day 72: Count-Min Sketch

## Frequency Estimation in Streaming Data

The Count-Min Sketch (CMS) answers a deceptively hard question: **how many times has item x appeared?** — using fixed memory regardless of how many distinct items exist.

In a stream of N items, exact counting requires O(n) space (one counter per distinct item). CMS trades accuracy for space: it gives an *approximate* count using O(1) space per query and O(1) time per update.

## Structure

A CMS is a 2D array of counters with **d rows** and **w columns**, paired with **d independent hash functions** (one per row).

```
         col 0    col 1    col 2    ...    col w-1
row 0  [  0   ] [  0   ] [  0   ] [...] [  0   ]   <- hash_0(x) maps here
row 1  [  0   ] [  0   ] [  0   ] [...] [  0   ]   <- hash_1(x) maps here
  ...
row d-1[  0   ] [  0   ] [  0   ] [...] [  0   ]   <- hash_{d-1}(x) maps here
```

Each hash function maps an item to one column in its row. Different items may collide in the same cell (that's the source of error), but colliding in ALL d rows simultaneously is unlikely.

## Operations

### Increment: add(item)

Hash the item with each of the d hash functions. Increment the counter at `table[i][hash_i(item)]` for each row i.

```
For each row i in 0..d-1:
    j = hash_i(item) mod w
    table[i][j] += 1
```

Time: O(d) = O(log(1/delta))

### Query: estimate(item)

Hash the item with each hash function, read each counter, return the **minimum**.

```
return min( table[i][hash_i(item) mod w] for i in 0..d-1 )
```

Time: O(d) = O(log(1/delta))

### Why minimum?

Collisions can only *add* to a counter, never subtract. So every counter is >= the true count. The true count is a lower bound on every counter that item hashes to. Taking the minimum across rows minimizes the overcounting from collisions.

**Key property: CMS never undercounts. It can only overcount.**

## Error Bounds

For parameters epsilon (error rate) and delta (failure probability):

| Parameter | Formula | Controls |
|-----------|---------|----------|
| w (width) | ceil(e / epsilon) | Accuracy — larger w = less collision = less error |
| d (depth) | ceil(ln(1 / delta)) | Confidence — more rows = higher probability of good estimate |

The guarantee: for any item x,

```
true_count(x) <= estimate(x) <= true_count(x) + epsilon * N
```

with probability >= 1 - delta, where N is the total number of items added.

### Space Complexity

Total counters = w * d = O((1/epsilon) * log(1/delta))

This is *independent* of the number of distinct items. For epsilon=0.01, delta=0.01: ~272 * 5 = 1,360 counters. That's enough to approximate frequencies over billions of items.

## Why It Works (Intuition)

Each row is an independent experiment. In any single row, item x's counter might be inflated by collisions. But the probability that x collides with many high-frequency items in the *same* column decreases exponentially with more rows. Taking the minimum across d independent experiments drives the overcount down.

This is the same principle as Bloom filters: multiple independent hash functions make false positives exponentially unlikely.

## Comparison with Alternatives

| Approach | Space | Query Time | Exact? |
|----------|-------|------------|--------|
| Hash map (exact) | O(n) | O(1) | Yes |
| Count-Min Sketch | O(1/epsilon * log(1/delta)) | O(log(1/delta)) | No (overcounts) |
| Count Sketch | Same | Same | No (unbiased, can undercount) |
| Lossy Counting | O(1/epsilon * log(epsilon*N)) | O(1) | No |

## Real-World Uses

1. **Network traffic monitoring**: Count packets per source IP in a high-speed router. Exact counting at 10 Gbps is infeasible — CMS fits in SRAM.

2. **Trending topics detection**: Track word/hashtag frequencies in a social media firehose. Flag items whose estimated count exceeds a threshold (heavy hitters).

3. **Database query optimization**: PostgreSQL and other databases use frequency histograms to estimate selectivity. CMS can maintain these histograms on streaming data for adaptive query planning.

4. **Click fraud detection**: Estimate click counts per advertiser/IP pair. Flag anomalies without storing every pair.

5. **Natural language processing**: Approximate word frequency counts for large corpora that don't fit in memory.

## Conservative Update Optimization

Standard CMS increments all d counters. Conservative Update only increments counters that are at or below the current minimum estimate. This reduces overcounting because it avoids inflating counters that are already above the true count.

```
current_min = estimate(item)
for each row i:
    j = hash_i(item) mod w
    table[i][j] = max(table[i][j], current_min + count)
```

## Checkpoint Questions

1. **Why does CMS take the minimum across rows instead of the average?** Every counter is an overestimate (collisions only add). The minimum is the tightest upper bound. Averaging would include the overcounting from other rows.

2. **If you double epsilon, what happens to the sketch width and error bound?** Width halves (w = e/epsilon), so the sketch uses half the space. But the error bound doubles — estimates can be off by up to 2x more.

3. **Can a CMS tell you if an item has NEVER been seen?** No. If estimate(x) > 0, x might never have been added — the counters could be inflated entirely by collisions. CMS has no way to distinguish "seen once" from "collisions sum to 1." (Unlike Bloom filters, which are designed for membership testing.)

4. **Why is CMS mergeable, and why does that matter?** Two CMS with the same dimensions and hash functions can be merged by summing corresponding cells. This enables parallel/distributed counting: each node maintains its own sketch, then merge for a global view. Map-reduce friendly.

5. **How does Conservative Update reduce error without changing space?** It avoids incrementing counters already above the minimum estimate. Standard update blindly increments all d counters, inflating cells that already overcounted. Conservative Update keeps counters closer to the true count.

6. **When would you choose CMS over a simple hash map?** When the stream is unbounded or the number of distinct items is too large for memory. CMS uses fixed space regardless of cardinality. If you can afford O(n) space, exact counting is always better.
