# High-value flag checks for INET pull requests

Flags differ from bugs: a bug is a high-confidence defect supported by evidence, while a flag identifies something that warrants closer review or documents an important design question. State the uncertainty explicitly. If a standard clause, lifecycle order, or runtime effect has not been verified, mark it for investigation instead of presenting it as a confirmed defect.

All examples below are deliberately hypothetical. Their names, snippets, values, and scenarios are illustrative and do not refer to a particular branch, revision, or source file. This keeps the checks useful after any specific implementation issue has been changed or fixed.

Labels identify the knowledge needed to assess each flag:

- **C++** — language rules, APIs, ownership, object lifetime, or performance.
- **NED/INI** — NED declarations, module wiring, parameters, or configuration matching.
- **OMNeT++** — simulation lifecycle, signals, results, scheduling, RNGs, or fingerprints.
- **INET** — INET contracts, architecture, packet processing, compatibility, or conventions.
- **802.11** — IEEE 802.11 protocol behavior or standard interpretation.

## 1. Interface/contract changes that ripple silently

**Labels:** C++, NED/INI, INET, 802.11

When a virtual method signature or semantic contract changes, flag every implementation, caller, adapter, and replaceable module type for review. A successful in-tree build does not prove that all implementations adopted the new meaning.

**Hypothetical example:** An aggregation policy changes from `selectFrames(queue)` to `selectFrames(queue, eligibility, budget)`. One implementation may accept the new parameters but still select frames according to the old rules, while a NED-replaceable downstream implementation may no longer compile. Investigate both source compatibility and semantic compatibility.

## 2. Behavioral policy decisions worth confirming with the author

**Labels:** C++, INET

Flag plausible but observable policy changes so the author confirms that they are intentional. Do not call the new policy wrong merely because the old behavior differed.

**Hypothetical example:** A scheduler's aggregate-count query used to return `-1` when a provider could not report a count, but now throws an exception. Either contract may be defensible; flag the compatibility and operational consequences and ask which behavior is intended.

## 3. Spec-compliance claims

**Labels:** C++, INET, 802.11

Flag comments, constants, and algorithms that claim conformance to a particular standard rule. A domain reviewer should verify the cited revision, clause, qualifications, and units.

**Hypothetical example:** An ACK-timeout calculation adds SIFS, one slot, and a PHY receive-start delay, with a comment citing an IEEE clause. Treat the formula as an investigate item until the clause and its applicability to the modeled PHY and frame exchange have been checked.

## 4. Unbounded growth or resource accumulation

**Labels:** C++, INET, 802.11

Flag maps, buffers, caches, tombstones, and retry histories that lack an obvious bound or purge path. The issue may be bounded by a protocol invariant, configuration, or simulation lifetime, so establish that before calling it a leak.

**Hypothetical example:** A reassembly component stores incomplete fragment sets keyed by peer, traffic identifier, and sequence number, but removes entries only after successful completion or an explicit reset. Investigate whether loss, malicious traffic, or long simulations can create an unbounded number of incomplete entries.

## 5. Lifecycle and teardown asymmetry

**Labels:** C++, OMNeT++, INET, 802.11

Flag registration without corresponding unregistration, state created during initialization but not cleared during stop or crash, and raw callbacks whose owners may be destroyed first. Verify the actual OMNeT++ lifecycle and structural ownership before concluding that a dangling reference exists.

**Hypothetical example:** A channel-access component registers callbacks with a coordinator during a late initialization stage and has no explicit unregister operation. This may be safe if the coordinator always dies first, but that ordering and restart behavior should be confirmed.

## 6. Configuration parameter defaults and NED wiring

**Labels:** NED/INI, INET, 802.11

Flag new or changed parameters for default choice, unit, inheritance, wildcard precedence, propagation, and compatibility with existing configurations.

**Hypothetical example:** A radio introduces `operationMode = "mixed"`, and several submodules derive rate-selection and MAC behavior from it. Existing INI files override only bitrate, so they silently inherit the new mode. Investigate whether the default and wiring preserve expected behavior.

## 7. Test coverage gaps for new branches

**Labels:** C++, INET, 802.11

Flag newly added terminal paths, exceptions, fallback cases, and protocol branches that have no identified focused test. Phrase the finding as a coverage question unless the full relevant test inventory has been checked.

**Hypothetical example:** An acknowledgment policy adds a `NO_EXPLICIT_ACK` branch and a new retry-exhaustion path. If no focused test exercises either path, flag them for coverage rather than asserting that the entire feature is untested.

## 8. Ownership-transfer semantics in return types

**Labels:** C++, OMNeT++, INET, 802.11

Flag APIs whose return value transfers ownership, may return null, or changes the ownership of an input object. Check every success, failure, and ignored-return path.

**Hypothetical example:** A reassembler exposes `Packet *addFragment(Packet *fragment)` and may return the original packet, a newly assembled packet, or null. The interface should make clear whether it stores, deletes, or returns ownership of `fragment` in each case; otherwise callers can leak, double-delete, or use a consumed packet.

## 9. Predicates and callbacks evaluated in hot paths

**Labels:** C++, OMNeT++, INET, 802.11

Flag predicates used by scheduling, channel access, or queue selection when their cost or side effects are unclear. A query that is cheap in one implementation may scan or mutate substantial state in another.

**Hypothetical example:** `hasFrameToTransmit(accessCategory)` scans every queued frame, evaluates an eligibility callback, and rebuilds bookkeeping when nothing qualifies. Because channel access may query it frequently, investigate complexity, caching, reentrancy, and whether a nominal predicate is allowed to emit signals or change state.

## 10. Is transaction machinery proportionate to the problem?

**Labels:** C++, INET, 802.11

Flag solutions that add several identity layers, tags, counters, and guards to address a narrow race. Ask for evidence of the failure modes each mechanism prevents; do not assume that the smaller design is sufficient without checking protocol and lifecycle cases.

**Hypothetical example:** A stale-response fix introduces local transaction IDs, object generations, packet tags, per-category counters, and reentrancy guards. Investigate whether on-wire dialog-token plus peer-and-traffic matching covers the demonstrated cases, and which additional races require the surrounding machinery.

## 11. Interface segregation and abstraction leakage

**Labels:** C++, INET, 802.11

Flag generic interfaces that acquire concepts motivated by one protocol or consumer. The additions may be broadly useful, but their abstraction level and dependency direction should be reviewed.

**Hypothetical example:** A generic packet-queue contract gains link-layer-specific removal reasons and eligibility callbacks solely to support Wi-Fi transaction cleanup. Ask whether these belong in the base queue interface, an optional extension, or a protocol-local adapter.

## 12. Backward-compatibility surface for downstream users

**Labels:** C++, NED/INI, INET, 802.11

Flag changes to exported interfaces, replaceable module contracts, parameter names, and signal names even when every in-tree user has been updated. Downstream models may implement or configure them independently.

**Hypothetical example:** Pure virtual methods in queue, aggregation, and reassembly contracts gain parameters. The repository builds, but external implementations and NED types declared `like` those interfaces will fail or require semantic changes. Flag migration notes and compatibility expectations.

## 13. Magic numbers and hard-coded constants

**Labels:** C++, INET, 802.11

Flag unexplained protocol limits, timing values, sizes, and reason codes where a named constant, unit-bearing type, or standard citation would make the intent auditable. A literal is not automatically incorrect.

**Hypothetical example:** Code uses literals such as `1024` for a time-unit conversion, `2007` for an identifier limit, `39` for a status code, and `33 us` for a PHY delay. Investigate whether each value is invariant, mode-dependent, configurable, or already represented by a named protocol constant.

## 14. Tests that assert behavior versus implementation details

**Labels:** C++, OMNeT++, INET, 802.11

Flag tests that bind tightly to callback order, private state, event numbers, or logging when observable protocol behavior would be sufficient. Some unit tests appropriately inspect internals, so judge this according to the test's scope.

**Hypothetical example:** A transaction test asserts an exact sequence of internal callback names even though its real requirement is that a DATA frame is followed by the proper acknowledgment and state transition. Flag whether the internal trace makes harmless refactoring unnecessarily expensive.

## 15. Dead or newly unreachable code after refactoring

**Labels:** C++, INET, 802.11

Flag obsolete names, unreferenced helpers, switch arms that can no longer be reached, and compatibility scaffolding whose purpose is unclear. Confirm generated calls, reflection, and extension points before declaring code dead.

**Hypothetical example:** After dispatch moves frame types into separate serializers, a remaining serializer still contains a switch over every historical frame type even though its caller passes only one constant kind. Investigate whether the other cases are extension hooks, tests' entry points, or removable remnants.

## 16. Signal and statistic contracts for observers

**Labels:** C++, NED/INI, OMNeT++, INET, 802.11

Flag signal renames, payload changes, lifecycle splits, and recording-path changes. They can silently invalidate statistics and external result-analysis scripts without causing compilation failures.

**Hypothetical example:** One `agreementChanged` signal is replaced by separate `agreementAdded`, `agreementUpdated`, and `agreementDeleted` signals, while a NED statistic derives a live count from additions and deletions. Investigate migration of recorders and downstream scalar/vector consumers.

## 17. Nullable returns not documented in the contract

**Labels:** C++, INET, 802.11

Flag pointer-like or optional results when the not-found case is absent from the public contract. Implementations and callers otherwise may disagree between returning null, throwing, or manufacturing a default object.

**Hypothetical example:** `findAgreement(peer, tid)` returns null when no agreement exists, but the interface comment describes only a successful lookup. A second implementation might reasonably throw instead. Flag the missing contract and caller assumptions.

## 18. Enum value stability for serialized or persisted enums

**Labels:** C++, NED/INI, OMNeT++, INET, 802.11

Flag implicitly numbered enums that cross serialization, reflection, NED, logging, signal, scalar, vector, or external-analysis boundaries. Reordering may silently reinterpret stored ordinals.

**Hypothetical example:** A contention-state enum uses implicit values and is recorded as an integer statistic. Inserting a new member in the middle changes all later ordinals. Investigate whether consumers use names or numbers and whether explicit stable values are needed.

## 19. Default-parameter drift in overridden virtual methods

**Labels:** C++, INET

Flag different default arguments on base and overridden virtual declarations. In C++, virtual dispatch selects the function dynamically, but default arguments are chosen from the static type at the call site.

**Hypothetical example:** A base interface declares `dropPacket(packet, limit = -1)`, while an override declares `limit = 0`. Calls through the interface and concrete type invoke the same override with different values. Investigate whether the defaults should be identical or removed.

## 20. Naming and semantic clarity of overlapping identities

**Labels:** C++, INET, 802.11

Flag multiple counters or identifiers whose scopes and lifetimes are easy to confuse. Document which are on-wire, local, per-peer, per-flow, reusable, or monotonic.

**Hypothetical example:** A block-ack path uses `sequenceNumber`, `startingSequence`, `dialogToken`, `transactionId`, and `generation`. Investigate whether each identity's domain and wrap/reuse rules are explicit enough to prevent a future comparison between unrelated values.

## 21. Thread of responsibility for association-identifier lifecycle

**Labels:** C++, OMNeT++, INET, 802.11

Flag resource lifecycles split across management, MIB, and transmission callbacks when no single owner visibly maintains reserve/commit/cancel invariants.

**Hypothetical example:** A MIB reserves an association identifier while a response is constructed, the access-point manager commits it after an acknowledgment, and a failed transmission has no obvious release site. Investigate which component owns the reservation on every timeout, retry, rejection, stop, and disconnect path.

## 22. Configuration-parameter interactions and conflicting defaults

**Labels:** C++, NED/INI, OMNeT++, INET, 802.11

Flag parameters whose individually reasonable defaults interact through timer ordering, subtraction, retry scheduling, or protocol expiry. Check validation and document intended relationships.

**Hypothetical example:** A scan policy defaults `probeDelay` to 100 ms, `minimumChannelTime` to 150 ms, and `maximumChannelTime` to 300 ms, while one timer is scheduled for `maximum - minimum`. Investigate invalid orderings, whether probe delay is included, and how zero or negative configured values are handled.

## 23. Spec-version pinning

**Labels:** INET, 802.11

Flag mixed or unversioned standard references. Clause and table numbers move between revisions even when the underlying rule remains similar.

**Hypothetical example:** One change cites a clause from an older IEEE 802.11 revision, another cites a newer revision, and a third mentions only a table number. Ask that references be pinned consistently and that intentional cross-revision differences be explained.

## 24. Test determinism and RNG seeding

**Labels:** C++, NED/INI, OMNeT++, INET, 802.11

Flag tests that depend on random contention, stochastic traffic, simultaneous events, or unspecified RNG-stream mapping while asserting exact event or frame order.

**Hypothetical example:** A scenario uses random backoff and uniformly distributed packet generation, then asserts which station transmits first without fixing the seed and RNG assignment. Investigate whether the result is deterministic across configurations, platforms, and unrelated RNG consumers.

## 25. Fingerprint update justification

**Labels:** OMNeT++, INET, 802.11

Flag broad fingerprint regeneration without a per-class explanation of the first divergence and why the changed event trajectory is expected. A stable new hash proves repeatability, not correctness.

**Hypothetical example:** A timing fix changes roughly fifty fingerprint rows across examples and tutorials. Request a rationale that separates intentional protocol behavior, changed serialization bytes, initialization-order effects, and unrelated drift instead of accepting a blanket regeneration.

## 26. Coupling of the management layer to MAC internals

**Labels:** C++, OMNeT++, INET, 802.11

Flag management logic that depends on concrete MAC callback types, private transaction steps, or frame-transmission sequencing rather than a stable service contract.

**Hypothetical example:** Management subscribes to a “frame sequence finished” callback, downcasts its context, and assumes the last two internal steps were transmission and acknowledgment before committing association state. Investigate whether a MAC refactor could violate that assumption without changing the management-level outcome.

## 27. Error-message quality

**Labels:** C++, OMNeT++, INET, 802.11

Flag new exceptions whose messages omit the value, parameter, packet, or operation needed to diagnose the failure. Also check what module context OMNeT++ already supplies before requesting redundant text.

**Hypothetical example:** A parser throws `Unknown FCS mode`, or a queue throws `Cannot find packet`. Investigate whether the message should include the offending mode, packet identity, configured parameter, and expected alternatives.

## 28. Symmetry of add/remove signal emission

**Labels:** C++, NED/INI, OMNeT++, INET, 802.11

Flag lifecycle signals when every creation path does not visibly pair with every destruction path. First establish whether signals represent object lifetime, protocol messages, or selected transitions.

**Hypothetical example:** An agreement emits `added` after successful negotiation and `deleted` after receiving a teardown frame, but may also disappear through inactivity expiry, local teardown, replacement, or module stop. Investigate whether observers deriving a live count can drift and whether all removals are intended to be observable.

## 29. Protocol-time unit exposure at the NED boundary

**Labels:** C++, NED/INI, OMNeT++, INET, 802.11

Flag parameters that cross between NED time quantities, simulation time, and protocol-specific integer units. Their range, rounding, saturation, and zero semantics should be explicit.

**Hypothetical example:** A lifetime is configured in seconds, stored as `simtime_t`, and serialized into a 16-bit field measured in time units. Investigate how non-integral values are rounded, what happens on overflow, and whether zero means immediate expiry, disabled expiry, or a protocol-defined special case.

## 30. Documentation completeness for new NED parameters

**Labels:** NED/INI, INET, 802.11

Flag parameters whose declaration and default do not explain purpose, unit, valid range, sentinel values, or interaction with related settings. A module-level summary may not be enough for users configuring one parameter.

**Hypothetical example:** A block-ack policy adds response timeout, retry backoff, and maximum-window parameters with defaults but no per-parameter description. Investigate whether users can tell which timer starts when, whether zero disables a feature, and which combinations are valid.
