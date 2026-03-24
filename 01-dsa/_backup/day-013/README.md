# Day 13: Hash Tables Part 1 -- Hash Functions and Chaining

## Why This Exists

The hash table is the single most important data structure in practical programming. Databases use them for indexes. Compilers use them for symbol tables. Caches are hash tables. Sets are hash tables. Every time you write `dict[key] = value` in Python, `map[key] = value` in Go, or `HashMap.put(key, value)` in Java, you are using a hash table. If you understand one data structure deeply, make it this one.

The core promise is extraordinary: O(1) average-case lookup, insertion, and deletion. Arrays give you O(1) access by index, but only if you KNOW the index. Hash tables give you O(1) access by ANY key -- a string, a tuple, an object. They achieve this by converting arbitrary keys into array indices using a hash function, which is one of the most elegant ideas in computer science.

But the promise has a dark side. The birthday paradox guarantees that collisions -- two different keys mapping to the same index -- happen far sooner than intuition suggests. With only 23 people in a room, there is a 50% chance two share a birthday. With a hash table of 1000 slots, you only need about 38 insertions before a collision is more likely than not. How you handle collisions determines whether your O(1) promise holds or degrades to O(n).

Real-world failures from hash table misunderstanding are common. In 2011, a hash collision attack (HashDoS) was disclosed against PHP, Python, Java, Ruby, and ASP.NET. Attackers crafted inputs that all hashed to the same bucket, turning O(1) lookups into O(n) and taking down web servers with a single request. Python 3.3+ added hash randomization specifically to prevent this. Understanding hash tables is understanding both their power and their failure modes.

## Theory (40 min)

### 1. The Core Idea

Given a key (any type), we want to:
1. Compute an integer from the key: `h = hash(key)` -- the hash function
2. Map that integer to an array index: `index = h % table_size`
3. Store/retrieve the value at that index

```
  key "alice" --hash--> 7823491 --mod 8--> 3
  key "bob"   --hash--> 2940182 --mod 8--> 6

  Index:  0     1     2     3         4     5     6       7
  Array: [   ] [   ] [   ] ["alice"] [   ] [   ] ["bob"] [   ]
```

If every key maps to a unique index, we get O(1) everything. The problem is that the number of possible keys is infinite, but the array size is finite. Collisions are mathematically inevitable.

### 2. What Makes a Good Hash Function

A hash function must satisfy:
- **Deterministic**: Same key always produces the same hash
- **Uniform distribution**: Keys should spread evenly across the output space
- **Avalanche effect**: A small change in input causes a large change in output

```
  "cat" -> 8372193  (change one letter...)
  "bat" -> 1950274  (completely different hash -- good!)

  Bad hash: "cat" -> 3, "bat" -> 4  (predictable, linear -- attackable)
```

**Why uniform distribution matters**: If 80% of keys hash to 20% of buckets, those buckets become long chains and performance degrades. A good hash function makes this astronomically unlikely.

**Why avalanche matters**: If similar keys hash to similar values, real-world data (which is often clustered) will cause clustering in the table. The hash function must destroy any patterns in the input.

### 3. Hash Functions in Practice

**For integers**: Multiply by a large prime, then take modulo. Or use bit-mixing operations (shift, XOR, multiply) to spread bits around.

```python
def hash_int(key, table_size):
    # Knuth's multiplicative hash
    # The golden ratio constant spreads bits well
    A = 2654435769  # 2^32 / phi, truncated
    return ((key * A) >> 16) % table_size
```

**For strings**: Process each character, combining them in a way that depends on position (so "abc" != "bca").

```python
def hash_string(key, table_size):
    h = 0
    for char in key:
        h = h * 31 + ord(char)  # 31 is prime, used by Java
    return h % table_size
```

Why 31? It is prime (reduces collision patterns), it is one less than a power of 2 (so `h * 31 = h * 32 - h = (h << 5) - h`, which is fast), and empirically it distributes well for natural language strings.

**Python's hash()**: Uses SipHash (since 3.4), a cryptographic-strength hash that prevents collision attacks. It includes a random seed generated at interpreter startup, so `hash("hello")` gives different values in different Python sessions.

### 4. The Birthday Paradox and Collisions

In a room of n people, the probability of a birthday collision exceeds 50% when n ~ 23 (for 365 days). Generalizing: for a hash table of size m, expect the first collision after roughly sqrt(pi * m / 2) insertions.

For a table of 1000 slots: first collision around insertion 39. For a table of 1,000,000 slots: first collision around insertion 1,177. Collisions are NOT edge cases -- they are the common case.

This is why collision resolution is not optional. It is the heart of hash table design.

### 5. Chaining (Separate Chaining)

The simplest collision resolution: each bucket holds a linked list of all entries that hash to that index.

```
  Index 0: -> ("eve", 30) -> None
  Index 1: -> None
  Index 2: -> ("alice", 25) -> ("charlie", 35) -> None
  Index 3: -> ("bob", 28) -> None
  Index 4: -> None
  ...
```

**Lookup**: Hash the key, go to that bucket, walk the linked list comparing keys. Average chain length = n/m (load factor), so average lookup is O(1 + n/m).

**Insert**: Hash the key, walk the chain to check for duplicates, insert at the head (O(1) if no duplicate check needed).

**Delete**: Hash the key, walk the chain, remove the node. O(1 + n/m) average.

### 6. Load Factor

The load factor alpha = n/m (number of entries / number of buckets) determines performance.

- alpha < 1: Most buckets have 0 or 1 entries. Fast.
- alpha = 1: On average, each bucket has 1 entry. Still OK.
- alpha = 2: Average chain length is 2. Slowing down.
- alpha = 10: Average chain length is 10. Now it is a linked list with extra steps.

With chaining, the hash table still WORKS at any load factor -- it just gets slower. Most implementations resize (double the array) when alpha exceeds a threshold (commonly 0.75 for Java's HashMap, ~0.67 for Python's dict).

### 7. Resize Operation

When load factor exceeds the threshold:
1. Allocate a new array, typically 2x the size
2. Rehash every existing entry (because `h % new_size != h % old_size`)
3. Insert all entries into the new array

This is O(n) work, but it happens infrequently. Amortized over all insertions, each insertion is still O(1). Same amortization argument as dynamic arrays.

### 8. Why Hash Tables Power Everything

- **Python dict / set**: Hash table with open addressing (Day 14)
- **Database indexes**: Hash indexes for equality lookups (O(1) vs. B-tree O(log n))
- **Caches (memcached, Redis)**: Distributed hash tables
- **Compilers**: Symbol tables mapping variable names to types/locations
- **Network routing**: IP address lookup tables
- **Deduplication**: Seen-set for detecting duplicates in streams

## Practice (20 min)

Work through `practice.py`. Build hash functions, analyze their collision behavior, and understand why distribution quality matters. Implement chaining collision resolution.

## Daily Project

Run `hash_table_chaining.py` to see a complete hash table built from scratch with separate chaining. It includes collision statistics, load factor monitoring, automatic resizing, and benchmarks against Python's built-in dict. Study how collisions increase with load factor and how resize keeps performance bounded.

## Checkpoint Questions

1. Why does Python randomize hash seeds between interpreter sessions? What attack does this prevent, and why was it serious enough to change the language?

2. If you have a hash table with 1000 buckets and you insert 500 keys with a perfect hash function, how many collisions do you expect? (Hint: birthday paradox formula.)

3. The load factor threshold for resize is a trade-off. What happens if you set it too low (e.g., 0.1)? Too high (e.g., 5.0)? What is being traded?

4. Why does rehashing require recomputing every entry's position, not just the entries in overloaded buckets? What would go wrong if you skipped this?

5. Could you use a hash table to implement a sorted data structure (e.g., iterate keys in order)? Why or why not? What does this tell you about when to use a hash table vs. a balanced BST?
