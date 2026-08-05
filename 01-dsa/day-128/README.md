# Day 128: Huffman Coding — Optimal Prefix Codes

## The Problem

You have a stream of symbols (characters in a file, tokens in a stream).
Some are frequent, some are rare. You want to encode them as binary so the
**total encoded length is minimum**.

Fixed-length codes (ASCII: 8 bits each) waste bits. If `e` appears 1000
times and `z` appears 3 times, why pay 8 bits for both?

**Goal**: assign each symbol a binary code such that:
1. No code is a prefix of another (otherwise decoding is ambiguous).
2. The expected length `Σ p(c) * len(c)` is minimum.

Huffman (1952, as a grad-student term paper at MIT) solved this exactly,
greedily, in O(n log n).

## Why "Prefix" Matters

If `a = 0` and `b = 01`, then `01` is ambiguous — it could be `b` or `ab`.
A **prefix code** forbids this: no codeword is a prefix of any other.

Prefix codes correspond exactly to **leaves of a binary tree**. Walk left =
0, walk right = 1. Each leaf is a symbol; its code is the root-to-leaf path.
No prefixes possible because internal nodes are never symbols.

## The Greedy Construction

```
1. Build a min-heap of (frequency, symbol) pairs.
2. Pop the two smallest. Combine into a new internal node with
   frequency = sum of children.
3. Push the new node back.
4. Repeat until one node remains. That node is the root.
5. Codes = root-to-leaf paths (left=0, right=1).
```

The two least-frequent symbols become **siblings at the deepest level**.
This is intuitive: low-frequency symbols can afford long codes; high-
frequency symbols stay shallow (short codes).

## Correctness — Exchange Argument

**Claim**: An optimal prefix code tree has the two least-frequent symbols
as siblings at maximum depth.

**Proof sketch**: Let `x, y` be the two least-frequent symbols, and let `T`
be any optimal tree. Let `a, b` be siblings at the deepest level of `T`.

Then `freq(a) >= freq(x)` and `freq(b) >= freq(y)` (since `x, y` are the
two smallest). Swap `a <-> x` and `b <-> y`. The cost change is:

`Δcost = (freq(x) - freq(a)) * (depth(a) - depth(x))`
        `+ (freq(y) - freq(b)) * (depth(b) - depth(y))`

Both terms are `<= 0` because `freq(x) <= freq(a)` and `depth(a) >= depth(x)`,
similarly for `y, b`. So the swapped tree is no worse → still optimal,
and now `x, y` are deepest siblings.

By induction on the merged sub-symbol, Huffman's greedy is optimal.

## Information-Theoretic Lower Bound

**Shannon's source coding theorem**: For a source with symbol distribution
`p`, the average code length of any prefix code satisfies:

`L >= H(p) = -Σ p(c) * log2(p(c))`     (entropy, in bits/symbol)

Huffman achieves:

`H(p) <= L_huffman < H(p) + 1`

So Huffman is within 1 bit of entropy. To close the gap further you need
**arithmetic coding** (codes fractional bits) — that's a different story.

### Why the gap? Integer codeword lengths.

If a symbol's optimal code length is `-log2(p)` (e.g., 2.5 bits), Huffman
must round to an integer. With block-coding (encode `k` symbols at once),
the rounding penalty shrinks to `1/k`, but you pay in code-table size.

## A Worked Example

Symbols and frequencies:
```
a: 45    b: 13    c: 12    d: 16    e: 9    f: 5
```

Total = 100.

Build:
```
Step 1: pop f(5), e(9) → merge fe(14)
Step 2: pop c(12), b(13) → merge cb(25)
Step 3: pop fe(14), d(16) → merge fed(30)
Step 4: pop cb(25), fed(30) → merge cbfed(55)
Step 5: pop a(45), cbfed(55) → merge root(100)
```

Tree (one valid shape; left=0, right=1):
```
                root(100)
               /         \
            a(45)        cbfed(55)
                        /         \
                    cb(25)       fed(30)
                   /     \      /      \
                 c(12) b(13) fe(14)  d(16)
                            /     \
                          f(5)   e(9)
```

Codes:
```
a = 0           (1 bit)
c = 100         (3 bits)
b = 101         (3 bits)
f = 1100        (4 bits)
e = 1101        (4 bits)
d = 111         (3 bits)
```

Average: `0.45*1 + 0.12*3 + 0.13*3 + 0.05*4 + 0.09*4 + 0.16*3 = 2.24 bits/symbol`

Entropy: `H = -(0.45*log2(0.45) + ...) ≈ 2.27 bits/symbol`

Wait — Huffman's average (2.24) is **less** than the entropy I just gave?
That's a rounding artifact in the entropy estimate. The real entropy here
is `≈ 2.184`. Recheck:

`H ≈ 0.45·1.152 + 0.16·2.644 + 0.13·2.943 + 0.12·3.059 + 0.09·3.474 + 0.05·4.322`
`  ≈ 2.184`

Huffman gives 2.24 → within 1 bit (well within: 0.056 above entropy).

## Practical Encoding/Decoding

**Encoding**: walk the tree once to build a `symbol -> bitstring` table.
Then concat all bitstrings.

**Decoding**: walk the tree bit-by-bit. At each leaf, emit the symbol and
restart at root.

**Storage of the tree**: you must send the tree (or frequency table) with
the encoded data, else the decoder can't reconstruct. Common formats:
- Send freq table (one int per symbol used) — simple
- Send canonical Huffman tree (just code lengths, sorted) — compact
- Adaptive Huffman: tree evolves with the stream, no header needed

## Where Huffman Lives in the Real World

| System | Use |
|--------|-----|
| **DEFLATE** (gzip, zlib, PNG) | Huffman on top of LZ77 dictionary compression |
| **JPEG** | Huffman on quantized DCT coefficients |
| **MP3** | Huffman on quantized frequency bins |
| **HTTP/2 HPACK** | Huffman for header field values (canonical static table) |
| **TIFF, BMP RLE** | Sometimes Huffman as final stage |

Modern compressors (zstd, brotli) use Huffman + arithmetic-coding hybrids
called **ANS** (Asymmetric Numeral Systems) — faster than arithmetic,
closer to entropy than Huffman.

## Failure Modes / Sharp Edges

1. **Single symbol input**: Huffman gives code length 0. You must special-case
   to assign length 1.
2. **Identical frequencies**: tree shape is non-unique → different
   implementations produce different codes for the same input.
3. **Stream not in training distribution**: if you trained on English and
   compress Chinese, expected length explodes. Adaptive Huffman fixes this
   at the cost of decode complexity.
4. **Header overhead**: for small files, the tree header can be larger than
   the data savings. zlib uses heuristics to switch between Huffman, fixed,
   and stored modes per block.

## Checkpoint

1. Why must codes be prefix-free? Construct an ambiguous decoding example.
2. State the exchange argument that proves the two least-frequent symbols
   are siblings at maximum depth in some optimal tree.
3. What is the lower bound on average code length? Why can't Huffman reach
   it exactly?
4. When is Huffman exactly optimal (matches entropy)? Hint: powers of 2.
5. In DEFLATE, why is Huffman applied **after** LZ77 rather than before?
6. Implement a single-pass adaptive Huffman in your head. What's the
   bookkeeping cost per symbol?
