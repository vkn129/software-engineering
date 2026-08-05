# Day 132: Stable Matching (Gale-Shapley / Deferred Acceptance)

## Why It Matters

Two groups must be paired up, and each side has opinions about the other.
No money changes hands, so price cannot clear the market. What clears it
instead is **stability**: an outcome nobody can improve on by quietly
defecting.

- **NRMP** — every US medical graduate is placed by deferred acceptance.
  Before 1952 the market unravelled into exploding offers made years early;
  the algorithm fixed it, and it has run annually ever since.
- **School choice** — New York City (since 2003) and Boston (since 2005)
  assign public-school seats this way. Roughly 100,000 NYC students a year.
- **Kidney exchange** — the same stability logic on a harder graph.
- **Ad auctions and cloud schedulers** — matching under preferences with no
  transferable price, wherever "just pay more" is not available.

Shapley and Roth took the 2012 Nobel in Economics for this: Shapley for the
theory (with Gale, 1962), Roth for making it work in real markets.

This is where the project's **Economics** thread is genuinely earned, not
decorated: the algorithm is short, and every interesting property is about
incentives rather than running time.

## The Definitions First

> **Blocking pair** — two people not matched to each other, each of whom
> prefers the other to their current partner. They can both walk out and be
> happier. A matching with none is **stable**.

Stability is not fairness, not efficiency, and not happiness. It is
precisely "no pair wants to defect". Everything else is a separate question.

## Deferred Acceptance

```
every proposer is free
while some free proposer p has anyone left on their list:
    r = the best receiver p has not yet asked
    if r is unmatched:                  r holds p
    elif r prefers p to whom she holds: r holds p, the old holder goes free
    else:                               p stays free
```

The word doing all the work is **deferred**. A receiver holding an offer is
engaged, never committed. She can always trade up later, so accepting early
costs her nothing — which is exactly why the process never has to back up.

**Termination.** A proposer never asks the same receiver twice, so there are
at most `n²` proposals in the one-to-one case. Every loop iteration consumes
one proposal, so the loop ends.

**Everyone ends up matched** (complete lists, equal-size sides). Suppose some
proposer `p` finished unmatched. Then `p` asked everyone. But a receiver, once
she holds anybody, holds somebody forever after — she only ever swaps
upwards. So every receiver `p` asked is matched, meaning all `n` receivers
are matched, meaning all `n` proposers are matched. Contradiction.

## Why No Blocking Pair Can Exist

Take any pair `(p, r)` not matched to each other and suppose `p` prefers `r`
to his own partner.

`p` works down his list in order, so he must have proposed to `r` *before*
reaching his final partner. `r` either rejected him or held him and later
dropped him. Either way, at that moment `r` held someone she liked at least
as much as `p`. And a receiver's holding only ever improves. So `r`'s final
partner is at least as good as `p` in her eyes.

Therefore `r` does not prefer `p`. The pair does not block. There is no
special case — this argument covers every pair, so the matching is stable.

Notice the shape of the argument: a **monotone quantity** (the receiver's
opinion of who she holds, which never falls) does all the work. That is the
standard way to prove a greedy-flavoured process correct.

## Proposer-Optimality

Stronger, and more surprising: deferred acceptance gives **every proposer
the best partner they could have in any stable matching at all**, all
simultaneously. There is no trade-off among proposers to resolve.

Sketch: call `r` *achievable* for `p` if some stable matching pairs them.
Claim: no proposer is ever rejected by an achievable receiver. Run the
algorithm and take the first time it happens — say `r` rejects `p` in favour
of `q`. Because it is the first such rejection, `q` has not yet been rejected
by anyone achievable for him, so `r` is at least as good as anything `q` can
stably get. Now take any stable matching `M` pairing `p` with `r`. In `M`,
`q` has someone he likes no better than `r`, and `r` prefers `q` to `p`. So
`(q, r)` blocks `M` — contradiction. Hence no achievable receiver ever
rejects, and each proposer lands on the best achievable one.

The mirror statement is the cost: the same matching is **receiver-pessimal**.
Each receiver gets the worst partner she has in any stable matching.

Two men, two women, and the asymmetry is already visible:

```
A: X > Y        X: B > A
B: Y > X        Y: A > B

men proposing    -> A-X, B-Y      (both men get their first choice)
women proposing  -> A-Y, B-X      (both women get their first choice)
```

Both are stable. Which one you get depends entirely on who does the asking.

## The Mechanism-Design Angle

An algorithm run on reported preferences is a **mechanism**, and the honest
question is: does anyone gain by lying to it?

- **Proposers: no.** Deferred acceptance is strategy-proof for the proposing
  side. Reporting truthfully is a dominant strategy — no lie can ever help,
  whatever anyone else does.
- **Receivers: yes.** In the example above, `X` gets her *worst* partner when
  the men propose. If she simply truncates her list to `[B]` — declaring `A`
  unacceptable — the algorithm hands her `B`, her first choice. She gained by
  lying.

**Roth's impossibility (1982): no stable matching mechanism is strategy-proof
for both sides.** So the design question is not "which mechanism is
manipulation-free" but **whose truthfulness matters more**. NRMP runs
applicant-proposing, deliberately: applicants are many, uncoordinated, and
have the most at stake in getting the report right.

This is why Boston abandoned its old "immediate acceptance" system in 2005.
That mechanism punished families who ranked an over-subscribed school first
and lost, so parents played strategy games with their children's education.
Deferred acceptance removed the game for the proposing side.

## Many-to-One: Hospitals and Residents

Same algorithm, one change: a hospital with `k` seats holds the best `k`
offers instead of the best 1. Everything above survives — stability,
proposer-optimality, one-sided strategy-proofness.

One extra fact worth knowing, the **Rural Hospitals Theorem** (Roth 1986):
the *set* of matched agents is identical in every stable matching, and any
hospital that ends up under-subscribed gets exactly the same residents in
every stable matching. Rural hospitals that go unfilled cannot be fixed by
picking a different stable matching — the shortage is real, not an artefact
of the algorithm. Policy conclusions follow from that, which is the point.

## Complexity

| Operation | Time | Space |
|---|---|---|
| `gale_shapley` (one-to-one, n per side) | O(n²) | O(n²) for the rank tables |
| `find_blocking_pairs` | O(n²) | O(n²) |
| `all_stable_matchings` (brute force) | O(n! · n²) | O(n · #stable) |
| `hospital_residents` | O(total list length) | O(total list length) |

`O(n²)` is tight: some instances really do need `n²` proposals, and the input
itself is `n²` numbers, so you cannot do better than reading it.

## Failure Modes

- **Ties in preferences.** The whole argument assumes strict rankings. With
  ties, "stable" splits into weak/strong/super-stable, and finding a maximum
  stable matching becomes NP-hard for some variants.
- **Incomplete lists.** Legal, but "everyone gets matched" stops holding.
  Code must handle an unmatched agent instead of assuming a partner exists.
- **Couples.** Two residents who want to be placed in the same city break the
  theory: with couples a stable matching may not exist at all, and deciding
  whether one exists is NP-complete. NRMP uses a heuristic and admits it.
- **Assuming symmetry.** Running it "the other way around" silently changes
  who wins. A code review that does not name which side proposes has missed
  the only decision that matters.
- **Believing stability implies fairness.** The receiver-pessimal outcome is
  perfectly stable and can be badly lopsided.
- **Preference lists that reference unknown names.** Real deployments get
  malformed lists constantly. Validate, or a typo becomes a silent rejection.

## Checkpoint Questions

1. State the blocking-pair definition precisely, then explain why "no
   blocking pair" does not mean "everyone is happy".
2. Where exactly does the proof of stability use the fact that a receiver's
   held partner only improves?
3. Give the 2×2 instance with two distinct stable matchings and show both.
4. Why is the proposing side's truthfulness a dominant strategy, while the
   receiving side's is not?
5. If a receiver truncates her list and it backfires, what happens to her?
   What does that tell you about the risk of the manipulation?
6. In hospitals/residents, why does holding the best `k` offers preserve the
   stability argument unchanged?
7. What does the Rural Hospitals Theorem rule out as a policy fix, and why
   is that a useful thing to know before you propose one?
