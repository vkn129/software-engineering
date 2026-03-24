# Day 69: Hash Attacks and Defenses

## Why This Exists

A hash table promises O(1) average-case lookup. That word "average" hides a dangerous assumption: that keys distribute uniformly across buckets. If an attacker controls the inputs — which they do on any web server accepting POST parameters, JSON keys, or HTTP headers — and they know your hash function, they can craft inputs that ALL hash to the same bucket.

When every key lands in one bucket, the hash table degenerates into a linked list. Every insert and lookup becomes O(n). Send a web server 100,000 carefully chosen POST parameters, and each insertion scans all previous ones: that is 100,000 * 100,000 / 2 = 5 billion operations. A single HTTP request can pin a CPU core for minutes.

This is the **HashDoS attack** (algorithmic complexity attack), and it is not theoretical.

## The 2011 HashDoS Incident

In December 2011, Alexander Klink and Julian Waelde demonstrated that PHP, Java, Python, Ruby, ASP.NET, and V8 (Node.js) all used deterministic hash functions for their built-in dictionaries. An attacker could:

1. Read the language's open-source hash function
2. Precompute thousands of strings that collide under that function
3. Send them as POST parameter names in a single HTTP request
4. Watch the server burn CPU parsing the request

A single 1MB POST body could consume **hours** of CPU time. The attack required no authentication, no special privileges, and worked against any application that parsed user input into a hash table — which is essentially every web application.

Every major language scrambled to patch:
- **Python** added `PYTHONHASHSEED` randomization (default since 3.3)
- **Ruby** switched to SipHash
- **Perl** added hash randomization
- **Java** added a treeification threshold (buckets become red-black trees after 8 collisions in Java 8)

## The Defense: Randomized Hashing

The core insight: if the attacker cannot predict the hash function, they cannot craft collisions.

**Keyed hashing** uses a secret random key (seed) chosen at process startup. The same string produces a different hash value in every process. The attacker would need to know the seed to craft collisions, and the seed is never exposed.

```
naive_hash("attack") = 42          # same every time, predictable
keyed_hash(seed, "attack") = ???   # different per process, unpredictable
```

### Why Not Cryptographic Hashes?

SHA-256 is collision-resistant, so why not use it for hash tables?

**Speed.** SHA-256 processes data in 64-byte blocks with 64 rounds of mixing. For short keys (8-32 bytes, typical of hash table usage), SHA-256 is 10-50x slower than a well-designed non-cryptographic hash. Hash tables perform billions of lookups; that overhead is unacceptable.

You do not need collision *resistance* (infeasible to find any collision). You need collision *unpredictability* (cannot find collisions without knowing the key). This is a weaker requirement that can be met by a much faster algorithm.

## SipHash: The Right Tool

SipHash was designed in 2012 by Jean-Philippe Aumasson and Daniel J. Bernstein specifically for hash table defense. It is:

- **Fast**: ~1 cycle per byte for short inputs (competitive with non-cryptographic hashes)
- **Keyed**: 128-bit key makes collision crafting infeasible without the key
- **PRF**: Provably a pseudorandom function (strong theoretical guarantees)
- **Simple**: ~100 lines of C, easy to audit

### How SipHash Works (SipHash-2-4)

The name "SipHash-2-4" means 2 rounds per message block, 4 finalization rounds.

**State**: Four 64-bit words (v0, v1, v2, v3), initialized from the 128-bit key.

**SipRound** (the core mixing operation):
```
v0 += v1;  v1 = rotl(v1, 13);  v1 ^= v0;  v0 = rotl(v0, 32);
v2 += v3;  v3 = rotl(v3, 16);  v3 ^= v2;
v0 += v3;  v3 = rotl(v3, 21);  v3 ^= v0;
v2 += v1;  v1 = rotl(v1, 17);  v1 ^= v2;  v2 = rotl(v2, 32);
```

**Processing**:
1. Initialize v0-v3 from key
2. For each 8-byte block of input: XOR into v3, apply 2 SipRounds, XOR into v0
3. Pad the last block with the message length
4. XOR a constant into v2, apply 4 finalization SipRounds
5. Return v0 ^ v1 ^ v2 ^ v3

### Who Uses SipHash

- **Python** (since 3.4): default string hash
- **Rust**: default `HashMap` hasher
- **Redis**: hashing keys
- **Linux kernel**: hash table defense
- **Ruby**, **Haskell**, **Swift**: default hash functions

## The Avalanche Effect

A good hash function has the **avalanche property**: flipping one input bit should flip approximately 50% of output bits. This ensures similar inputs scatter to different buckets.

Simple sum-based hashes fail catastrophically: changing one character changes the hash by at most the character range (~100). SipHash's mixing ensures a single bit flip cascades through all 64 output bits.

## Checkpoint Questions

1. **Why does a deterministic hash function enable HashDoS?** If the attacker can compute the same hash function, they can precompute inputs that all map to the same bucket. Randomization breaks this because the attacker does not know the per-process key.

2. **Why did the 2011 HashDoS affect web frameworks specifically?** Web frameworks parse HTTP POST parameters into dictionaries. Attackers control the parameter names (the dictionary keys), providing a direct channel to inject chosen keys into the hash table.

3. **Why is SHA-256 unsuitable for hash tables even though it prevents collision attacks?** SHA-256 is 10-50x slower than non-cryptographic hashes on short keys. Hash tables need speed; they do not need full collision resistance, only keyed unpredictability.

4. **What is the difference between collision resistance and a PRF?** Collision resistance means nobody can find any two inputs with the same output. A PRF (pseudorandom function) means the output is indistinguishable from random to anyone who does not know the key. A PRF is sufficient for hash tables and can be achieved with much less computation.

5. **Why does Python randomize hash seeds per process rather than per dictionary?** Per-dictionary seeds would require storing and using a different seed for every dict operation. Per-process seeds are simpler: one global seed, applied to all hashing. Since the attacker cannot read another process's memory, per-process randomization is sufficient.

6. **Why does Java 8 treeify buckets instead of (or in addition to) using randomized hashing?** Java's `hashCode()` contract is part of the public API — existing code depends on deterministic hash values. Changing the hash function would break serialization, caching, and distributed systems that rely on consistent hashing. Treeification is a defense that does not change the hash function: it limits worst-case per-bucket cost to O(log n) instead of O(n).
