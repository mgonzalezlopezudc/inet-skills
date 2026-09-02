# General C++ review checks

Apply the relevant sections of `doc/project/rule/architecture.md`,
`doc/project/rule/quality.md`, and `doc/project/rule/testing.md` first. Also apply
`doc/project/rule/release.md` when the change crosses an external compatibility boundary. This
reference adds concrete C++ failure mechanics and investigation steps beyond those rule statements.

## API and polymorphism

- **[RP-CPP-API-CALLERS]** Trace declarations, definitions, callers, overrides, and every concrete implementation affected by a changed interface.
- **[RP-CPP-API-IMPLEMENTATIONS]** When a base class gains an operation, inspect every subclass and confirm that it either implements the operation correctly or is rejected explicitly at a supported boundary. A default that silently returns empty, false, or null may falsely advertise support; apply `doc/project/rule/architecture.md#ar-org-contracts` to the caller-visible semantics.
- **[RP-CPP-API-SIGNATURE-ENUM]** When a signature or enum changes, inspect qualifiers, overload sets, intended `override`s, and every switch, classifier, serializer, printer, and terminal-state predicate that consumes it. Do not let a stale overload silently hide the new contract, and use a default switch arm only when unknown numeric values are part of the contract. If an enum crosses serialization, reflection, NED, signal/result, persistence, logging, or external-analysis boundaries, confirm whether its numeric values are externally visible. Apply `doc/project/rule/release.md#rr-numeric-stable` to the external boundaries it names; log output alone establishes numeric stability only when it is a defined published or tooling interface.
- **[RP-CPP-VIRTUAL-DEFAULTS]** Compare default arguments across a virtual declaration and every override. Defaults bind to the caller's static type even though the function dispatches dynamically, so different defaults can invoke one override with different values; confirm under `doc/project/rule/architecture.md#ar-org-contracts` that defaults do not silently change caller-visible semantics, then align or remove them where that distinction is unintended.
- **[RP-CPP-DISPATCH-WIDENING]** When dispatch widens from a concrete type to a base type, enumerate the now-admitted subclasses. Test the most-derived type before a base type when runtime type tests overlap.
- **[RP-CPP-API-OUTCOMES]** Inspect preconditions, postconditions, sentinel values, and error propagation at both sides of a changed API. Apply `doc/project/rule/architecture.md#ar-org-contracts`; do not infer that a local null guard preserves the caller's semantic contract.
- **[RP-CPP-NULLABLE-RESULT]** For a nullable or optional public result, confirm under `doc/project/rule/architecture.md#ar-org-contracts` that the contract defines absence and that every implementation and caller agrees whether not-found returns empty, throws, or produces a default. Do not infer this semantic choice from one implementation.
- **[RP-CPP-OWNERSHIP-RETURN]** For a return that may also transfer ownership, trace the returned object and every input object on success, failure, null, and ignored-result paths. Confirm which object is stored, consumed, deleted, or still owned by the caller in each case under `doc/project/rule/quality.md#qr-object-ownership`.
- **[RP-CPP-ASSERT-BOUNDARY]** Use assertions for internal invariants, not assumptions about unusual but supported external input. A frame, message, or callback admitted by the public contract must be handled, rejected, or reported deliberately instead of aborting only because it arrived out of the expected order.
- **[RP-CPP-COMPATIBILITY-REACHABILITY]** After a refactor, investigate apparently unreachable helpers, names, switch arms, and compatibility scaffolding through generated callers, reflection, registration, tests, and extension points before treating them as dead code.
- **[RP-CPP-DIAGNOSTIC-CONTEXT]** For a new diagnostic or exception, confirm that its message identifies the offending value, parameter, packet, or operation and the expected alternatives needed to act on it. Account for context the runtime already supplies rather than repeating module details.
- **[RP-CPP-PRODUCTION-PATH]** Apply the production-path distinction in `doc/project/design/test-anatomy.md` and select evidence
  under `doc/project/rule/testing.md#tr-focused-evidence`. A helper-only test can pass while the real
  owner bypasses the helper or supplies the wrong identity.

## Ownership and lifetime

Apply `doc/project/rule/quality.md#qr-object-ownership` while tracing the detailed ownership and
lifetime mechanics in this section.

- **[RP-CPP-OWNERSHIP-TRANSITIONS]** Identify the owner before and after every allocation, transfer, return, container insertion/removal, callback, duplicate, and deferred cleanup.
- **[RP-CPP-OWNERSHIP-DISPOSITION]** Check every success, ignore, error, exception, and early-return path for exactly one disposition. Distinguish deletion, transfer, borrowed access, and retained ownership.
- **[RP-CPP-BORROWED-LIFETIME]** A borrowed pointer or reference must not escape its promised lifetime. Verify captures, stored callbacks, asynchronous work, and containers for accidental retention.
- **[RP-CPP-CALLBACK-REGISTRATION-LIFETIME]** For registered callbacks, listeners, and other stored targets, trace who unregisters them and whether target teardown can precede registry teardown. A structurally coupled lifetime, explicit removal, or another validated lifetime mechanism must prevent dispatch to a destroyed target.
- **[RP-CPP-CALLBACK-REENTRANCY]** Treat callbacks as potentially synchronous unless the API proves otherwise. Check iterator invalidation, re-entrant removal, deletion of the current object, and access after notification.
- **[RP-CPP-CLEANUP-IDEMPOTENCE]** Make shared cleanup idempotent when multiple terminal paths can call it. Check partial construction and partial mutation before exception or failure cleanup.
- **[RP-CPP-SELF-ALIASING]** Check self-copy, self-move, and source/destination aliasing when assignment or replacement first destroys destination-owned state. Require self-safety only where the type's contract or a reachable production path permits the alias.

Do not label retention as a leak until the current owner and every cleanup point are traced. Do not label a pointer dangling until a reachable destruction precedes a subsequent access.

## State and algorithms

- **[RP-CPP-STATE-GENERATIONS]** Keep current, pending, and historical state distinct when they have different transition rules. Check stale completion after a new generation begins.
- **[RP-CPP-COLLECTION-MUTATION]** Challenge containers and loops with empty, singleton, several-element, full, and removal-during-iteration cases. Snapshot a shrinking bound or drain explicitly when removals change the collection size.
- **[RP-CPP-FINITE-PROGRESS]** For loops, recursion, retry chains, and selectors, identify a monotonic progress measure. Every nonterminal branch must change it or terminate; eligibility remaining true is not progress. Example: a frame selector that recursively retries while its child can never produce a frame is unbounded even if each individual call is small.
- **[RP-CPP-NUMERIC-BOUNDARIES]** Check integer boundaries, narrowing, signedness, overflow, underflow, and wraparound against the represented domain. Use domain ordering rather than ordinary integer ordering for cyclic spaces.
- **[RP-CPP-LOOKUP-ORDERING]** Check lookup and ordering logic for duplicate keys, ties, missing values, and user-provided sparse
  inputs after applying the canonical determinism rule.
- **[RP-CPP-QUERY-PURITY]** Keep predicates and read-like queries observational with respect to simulation and owned object state: repeated, skipped, reordered, or short-circuited evaluation must not change the result of later work. Avoid default-inserting lookups such as `operator[]` when absence is semantically different from a default value. Example: an eligibility predicate that consumes a retry token makes queue inspection alter later transmission behavior.
- **[RP-CPP-RESOURCE-BOUNDS]** For each long-lived map, buffer, cache, tombstone set, or retry history keyed by external identity (peer, address, packet, transaction, flow), investigate whether supported cardinality provides a real bound under repeated traffic or churn. Require eviction, expiry, or explicit capacity only when growth is otherwise unbounded; an intentional registry whose domain and lifetime are demonstrably bounded is not resource accumulation.
- **[RP-CPP-ATOMIC-STATE]** Verify that multi-field state changes are atomic from every observer's perspective, including synchronous callbacks.

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
