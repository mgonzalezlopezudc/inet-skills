# C++ contract checks

Use these compact prompts for implementation and review when the changed contract involves the
mechanism in the selected section. They support the canonical architecture, quality, and testing rules
in `doc/project/`; they are not additional project requirements or findings by themselves.

## API and dispatch

- **[RP-CPP-API-CALLERS]** Trace declarations, definitions, callers, concrete overrides, and sibling dispatch branches.
- **[RP-CPP-API-IMPLEMENTATIONS]** Check each affected implementation, including inherited defaults, for real support or explicit rejection at the supported boundary.
- **[RP-CPP-API-SIGNATURE-ENUM]** Check changed signatures and enums through overloads, overrides, switches, classifiers, serializers, and generated or external consumers; see the INET reference for compatibility boundaries.
- **[RP-CPP-VIRTUAL-DEFAULTS]** Compare virtual default arguments at each static call type; dynamic dispatch does not select the default argument.
- **[RP-CPP-DISPATCH-WIDENING]** Enumerate newly admitted derived types and check overlapping runtime type tests in most-derived-first order.
- **[RP-CPP-API-OUTCOMES]** Check preconditions, postconditions, sentinels, and errors on both sides; distinguish empty, not-found, invalid, and unsupported outcomes.
- **[RP-CPP-NULLABLE-RESULT]** Trace whether absence returns null/empty, throws, or supplies a default; callers and implementations must agree.
- **[RP-CPP-ASSERT-BOUNDARY]** Prove assertions exclude only inputs outside the supported contract, including unusual ordering admitted by the public API.

## Ownership and callbacks

- **[RP-CPP-OWNERSHIP-RETURN]** Trace returned and input objects on success, failure, null, and ignored-result paths, including any ownership transfer.
- **[RP-CPP-OWNERSHIP-TRANSITIONS]** Identify the owner before and after allocation, transfer, return, container mutation, callback, and deferred cleanup.
- **[RP-CPP-OWNERSHIP-DISPOSITION]** Check success, refusal, error, exception, early return, and terminal paths for exactly one disposition: deletion, transfer, or retained ownership.
- **[RP-CPP-BORROWED-LIFETIME]** Locate destruction and subsequent access for borrowed pointers/references retained in callbacks, containers, or deferred work.
- **[RP-CPP-CALLBACK-REGISTRATION-LIFETIME]** Trace unregistration or coupled lifetimes so a stored callback cannot outlive its target.
- **[RP-CPP-CALLBACK-REENTRANCY]** Check synchronous callbacks that remove the current object or a sibling, replace pending state, or delete the caller; inspect accesses after return.
- **[RP-CPP-CLEANUP-IDEMPOTENCE]** Check reachable repeated cleanup after timeout, cancellation, shutdown, or late/duplicate completion, including partially established state.
- **[RP-CPP-SELF-ALIASING]** Check self-copy, self-move, and source/destination aliasing where supported, especially if replacement destroys destination state first.
- **[RP-CPP-ATOMIC-STATE]** Establish consistent multi-field state before observers or synchronous callbacks can see it; detach completed state before notification where required.

## State and algorithms

- **[RP-CPP-STATE-GENERATIONS]** Distinguish current, pending, and historical state; a stale completion must not clear or complete a replacement generation.
- **[RP-CPP-COLLECTION-MUTATION]** Check empty, singleton, multi-item, and removal-during-iteration paths for invalidated iterators/references and changing loop bounds.
- **[RP-CPP-FINITE-PROGRESS]** Each nonterminal retry consumes input, advances state, or waits for an event that can occur; a permanently unavailable provider must not cause unbounded immediate retries.
- **[RP-CPP-NUMERIC-BOUNDARIES]** Check below/at/above limits, narrowing, signedness, overflow, and domain-specific cyclic ordering.
- **[RP-CPP-LOOKUP-ORDERING]** Check complete identities, missing/duplicate keys, ties, sparse inputs, and independent peers/flows against the ordering contract.
- **[RP-CPP-QUERY-PURITY]** A query must not silently insert state, consume a resource, or alter later behavior when repeated, skipped, or reordered.
- **[RP-CPP-RESOURCE-BOUNDS]** Trace retained state through lifetime and growth under traffic or identity churn; require a bound only where the supported domain and cleanup do not already provide one.

## Focused verification

For verification, choose the reachable case that distinguishes the failure, not every prompt by default.
**[RP-CPP-PRODUCTION-PATH]** Check the real caller when the claim includes integration; a helper
test alone cannot prove dispatch or input identity. Use the domain references for OMNeT++ ownership, INET generated consumers, and
protocol-specific ordering rather than inferring those contracts from C++ syntax.

Two useful callback/collection probes:

- A completion callback installs a replacement request. Cleanup after the callback must not clear
  that new request; detach the completed state before notification where the contract permits it.
- Removing the current map entry invalidates its iterator. Also check whether a synchronous
  callback can remove the entry or its sibling indirectly before the loop advances.
