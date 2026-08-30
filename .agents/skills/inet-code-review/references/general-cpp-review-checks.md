# General C++ review checks

Apply these checks to C++ contracts regardless of OMNeT++, INET, or protocol semantics. Use higher-layer references to establish how a path is reached; keep the defect here when the violated invariant is a language, API, lifetime, or algorithm contract.

## API and polymorphism

- Trace declarations, definitions, callers, overrides, and every concrete implementation affected by a changed interface.
- When a base class gains an operation, verify that every subclass either implements it correctly or is rejected explicitly at a supported boundary. A default that silently returns empty, false, or null may falsely advertise support.
- When a signature or enum changes, inspect qualifiers, overload sets, intended `override`s, and every switch, classifier, serializer, printer, and terminal-state predicate that consumes it. Do not let a stale overload silently hide the new contract, and use a default switch arm only when unknown numeric values are part of the contract.
- When dispatch widens from a concrete type to a base type, enumerate the now-admitted subclasses. Test the most-derived type before a base type when runtime type tests overlap.
- Check preconditions, postconditions, sentinel values, and error propagation at both sides of a changed API. Do not infer that a local null guard preserves the caller's semantic contract.
- Use assertions for internal invariants, not assumptions about unusual but supported external input. A frame, message, or callback admitted by the public contract must be handled, rejected, or reported deliberately instead of aborting only because it arrived out of the expected order.
- Verify that tests reach the production caller and integration boundary. A helper-only test can pass while the real owner bypasses the helper or supplies the wrong identity.

## Ownership and lifetime

- Identify the owner before and after every allocation, transfer, return, container insertion/removal, callback, duplicate, and deferred cleanup.
- Check every success, ignore, error, exception, and early-return path for exactly one disposition. Distinguish deletion, transfer, borrowed access, and retained ownership.
- A borrowed pointer or reference must not escape its promised lifetime. Verify captures, stored callbacks, asynchronous work, and containers for accidental retention.
- For registered callbacks, listeners, and other stored targets, trace who unregisters them and whether target teardown can precede registry teardown. A structurally coupled lifetime, explicit removal, or another validated lifetime mechanism must prevent dispatch to a destroyed target.
- Treat callbacks as potentially synchronous unless the API proves otherwise. Check iterator invalidation, re-entrant removal, deletion of the current object, and access after notification.
- Make shared cleanup idempotent when multiple terminal paths can call it. Check partial construction and partial mutation before exception or failure cleanup.
- Check self-copy, self-move, and source/destination aliasing when assignment or replacement first destroys destination-owned state. Require self-safety only where the type's contract or a reachable production path permits the alias.

Do not label retention as a leak until the current owner and every cleanup point are traced. Do not label a pointer dangling until a reachable destruction precedes a subsequent access.

## State and algorithms

- Identify one authoritative owner for each fact. When fields mirror one value, verify every writer and reader or derive secondary state from the authority.
- Keep current, pending, and historical state distinct when they have different transition rules. Check stale completion after a new generation begins.
- Challenge containers and loops with empty, singleton, several-element, full, and removal-during-iteration cases. Snapshot a shrinking bound or drain explicitly when removals change the collection size.
- For loops, recursion, retry chains, and selectors, identify a monotonic progress measure. Every nonterminal branch must change it or terminate; eligibility remaining true is not progress. Example: a frame selector that recursively retries while its child can never produce a frame is unbounded even if each individual call is small.
- Check integer boundaries, narrowing, signedness, overflow, underflow, and wraparound against the represented domain. Use domain ordering rather than ordinary integer ordering for cyclic spaces.
- Check lookup and ordering logic for duplicate keys, ties, unstable iteration order, missing values, and user-provided sparse inputs. Do not let container order stand in for semantic identity.
- Keep predicates and read-like queries observational with respect to simulation and owned object state: repeated, skipped, reordered, or short-circuited evaluation must not change the result of later work. Avoid default-inserting lookups such as `operator[]` when absence is semantically different from a default value. Example: an eligibility predicate that consumes a retry token makes queue inspection alter later transmission behavior.
- Verify that multi-field state changes are atomic from every observer's perspective, including synchronous callbacks.

## Focused verification

Map each suspected mechanism to the smallest check that distinguishes the bad behavior:

| Mechanism | High-value check |
| --- | --- |
| Interface or dispatch change | every concrete implementation and overlapping derived type |
| Signature or enum change | intended overrides, overload sets, and every exhaustive consumer |
| Ownership transfer | success, refusal, error, exception, and re-entrant callback |
| Collection mutation | zero, one, two, and several elements; remove current and sibling |
| Loop or retry chain | productive, temporarily unproductive, and permanently ineligible child/provider |
| Numeric boundary | below, at, and above each boundary; overflow or wrap point |
| State transition | success, failure, cancellation, stale completion, repeated cleanup |
| Selector or lookup | missing key, duplicate/tied values, reordered input, sparse input, repeated query |

Prefer a focused unit test for a pure C++ contract. If reachability depends on simulation or protocol behavior, use the corresponding higher-layer validation rather than mocking away the production path.
