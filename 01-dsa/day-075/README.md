# Day 75: Locality-Sensitive Hashing (LSH)

## The Problem: Finding Similar Items at Scale

Given a billion documents, find all near-duplicate pairs. Brute force compares every pair: O(n^2) comparisons. With n = 10^9, that is 5 * 10^17 comparisons. Even at 10^9 comparisons/sec, that takes ~16 years.

**LSH solves this**: hash similar items to the same bucket with high probability, dissimilar items to different buckets. Then only compare items within the same bucket. This turns O(n^2) into roughly O(n).

## Core Idea

Traditional hash functions spread similar items far apart (a single bit flip changes the hash completely). LSH does the opposite: **similar inputs produce the same hash with high probability**.

This is a deliberate violation of the "avalanche effect" that cryptographic hashes optimize for. We want collisions -- but only for similar items.

## MinHash for Jaccard Similarity

**Jaccard similarity** between sets A and B: J(A,B) = |A intersect B| / |A union B|

**MinHash insight**: apply a random permutation to the universe of elements, then take the minimum element in each set. The probability that the minimums match equals the Jaccard similarity:

```
P(min(pi(A)) == min(pi(B))) = J(A, B)
```

Why? The minimum of the union falls in the intersection with probability |intersection|/|union|.

**In practice**: we don't actually permute. We use k independent hash functions h_1, ..., h_k. For each set S, the signature is [min(h_i(x) for x in S) for i in 1..k]. The fraction of positions where two signatures agree estimates the Jaccard similarity.

## Banding Technique

A MinHash signature of length k = b * r is divided into **b bands** of **r rows** each. Two items are candidate pairs if they match in **all r rows of at least one band**.

The probability that two items with Jaccard similarity s become candidates:

```
P(candidate) = 1 - (1 - s^r)^b
```

This creates an S-curve threshold. With b=20 bands of r=5 rows:
- s = 0.2: P = 0.006 (almost never flagged)
- s = 0.5: P = 0.47
- s = 0.8: P = 0.9996 (almost always flagged)

**Tuning**: more bands (larger b) catches more true pairs but increases false positives. More rows per band (larger r) reduces false positives but misses some true pairs.

## Random Hyperplane LSH (Cosine Similarity)

For vectors, use random hyperplanes to partition space:

1. Generate a random vector r from a standard normal distribution
2. Hash(v) = sign(v dot r): 1 if positive, 0 if negative
3. P(hash match) = 1 - theta/pi, where theta is the angle between vectors

Multiple random hyperplanes give a multi-bit hash. Vectors with small angle (high cosine similarity) will agree on most bits.

## Why This Works: Geometry

A random hyperplane through the origin divides space in two. Two vectors on the same side of the hyperplane have a small angle between them. The probability of being on the same side is exactly proportional to how similar their directions are.

For MinHash, the "geometry" is set-theoretic: the probability of collision is governed by the overlap of the two sets, which is exactly the Jaccard similarity.

## Real-World Applications

- **Google News**: cluster near-duplicate articles. Millions of articles per day; LSH finds duplicates without all-pairs comparison.
- **Spotify**: song recommendation. Songs as feature vectors; LSH finds similar songs in a catalog of millions.
- **Plagiarism detection**: shingling (k-grams of text) + MinHash + LSH. Used by MOSS, Turnitin.
- **Genome assembly**: find overlapping DNA reads among billions of short sequences.
- **Ad deduplication**: detect near-duplicate ad creatives across an ad network.

## Trade-offs

| Parameter | Increase Effect | Decrease Effect |
|-----------|----------------|-----------------|
| Num hash functions (k) | Better accuracy, slower | Faster, noisier estimate |
| Num bands (b) | Higher recall, more false positives | Lower recall, fewer false positives |
| Rows per band (r) | Higher precision, lower recall | Lower precision, higher recall |
| Num hash tables | Higher recall, more memory | Less memory, lower recall |

## Checkpoint Questions

1. Why can't we use a standard hash function (like SHA-256) for finding similar items? What property of cryptographic hashes makes them unsuitable?

2. If two documents have Jaccard similarity 0.6 and we use 100 independent MinHash functions, approximately how many signature positions will match? What is the standard deviation of this estimate?

3. With b=10 bands and r=5 rows per band, what is the probability that two documents with Jaccard similarity 0.4 become candidate pairs? What about similarity 0.8?

4. Why does random hyperplane LSH measure cosine similarity specifically, rather than Euclidean distance? What geometric property of hyperplanes through the origin causes this?

5. A system uses LSH to deduplicate 100 million documents. The LSH step produces 500,000 candidate pairs. If the false positive rate is 10%, how many pairs need full comparison? What is the time savings compared to brute force?

6. You need to find all pairs of documents with Jaccard similarity > 0.7 with at least 95% recall. How would you choose b and r? What is the trade-off you are making?
