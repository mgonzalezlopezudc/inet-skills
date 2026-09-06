# INET review checks

Select project context by the changed INET contract using the shared discovery procedure. For packet,
chunk, tag, or serialization contracts, follow the active packet guidance. For protocol interaction,
lifecycle, queue, or configuration contracts, follow only the applicable current routes. Add another
canonical section only when the changed contract crosses into it. This reference adds concrete INET correctness traps not stated
there.

## Packets, chunks, and tags

- **[RP-INET-PACKET-DISPOSITION]** Under the active ownership guidance, inspect every accept, ignore, error, and early-return path for exactly one packet disposition. Moving a packet to a dropped or retirement list is not deletion. Example: if an eviction callback can delete a packet, establish container state and final ownership before notification and never access the packet afterward.
- **[RP-INET-TAG-PROPAGATION]** Decide whether packet-scope tags must propagate to replacement packets. Verify which request, indication, dispatch, interface, and protocol tags are sender-local, receiver-owned, or preserved across encapsulation. Example: a sender-local requested radio mode must not cross the wireless medium and be mistaken for a receiver-side indication; reconstruct receiver metadata from reception facts.
- **[RP-INET-REGION-TAG-OFFSETS]** For region tags, compute in absolute packet coordinates using the source front offset, copied interval, and target rebasing. When prepending or trimming chunks (e.g. adding or removing encapsulating headers), verify that region tag start and end offsets are correctly shifted or re-anchored. Exercise no-overlap, boundary-aligned, crossing, first-fragment, and final-fragment cases.
- **[RP-INET-RECEIVER-TAG-MUTATION]** When receiver processing clears sender-local tags, verify it mutates a duplicate or receiver-owned packet and then restores the metadata required by downstream dispatch.
- **[RP-INET-CHUNK-MUTABILITY]** Check immutable versus mutable chunk access and serializer-cache assumptions when decoded data is modified or reconstructed. Example: fragments that share one mutable MAC-header chunk can all observe the last fragment number written unless each modified header has independent ownership.
- **[RP-INET-TYPED-CHUNK-DISPATCH]** Before a typed `peekAtFront<T>()`, `popAtFront<T>()`, or equivalent operation, prove that the effective dispatch path admits `T`; otherwise inspect a common base or reject unsupported variants safely. Example: a path shared by data and management frames cannot assume `Ieee80211DataHeader` merely because most traffic is data.
- **[RP-INET-PACKET-LENGTH-CONSISTENCY]** After replacing, splitting, or recombining chunks, reconcile packet total length, every affected region-tag interval, and serialized byte count with each chunk's declared length. Example: replacing a 20-byte header with a 24-byte header must not leave a tag describing bytes 0–19 as the old header.

## Queues, providers, and protocol integration

- **[RP-INET-COLLECTION-INTERFACES]** When an INET collection, packet-provider, extractor, queue, buffer, gate, or scheduler interface changes, inspect every implementation and adapter. An older override that made a closed provider appear empty may not cover a new predicate operation.
- **[RP-INET-SHARED-BUFFER-REMOVAL]** With shared buffers, scope bulk removal to the owning queue and verify callbacks cannot delete excluded or currently processed packets.
- **[RP-INET-ORDERING-BARRIER]** Define the ordering barrier for every selector, aggregator, or scheduler and verify both selected output and residual queue order. Example: whether an eligible packet may bypass a temporarily blocked predecessor depends on the flow's ordering contract, not merely on forward-scan convenience.
- **[RP-INET-PROVIDER-OUTCOMES]** Apply the active provider-contract guidance: distinguish present-but-empty, absent optional capability, invalid provider/wiring, and out-of-range access, then confirm those outcomes remain consistent across count, peek, remove, clear, and predicate operations rather than collapsing them all into empty or null.
- **[RP-INET-UNSUPPORTED-VARIANTS]** Reject unsupported packet or primitive variants at a consistent boundary. Do not require a
  syntactic one-to-one `registerProtocol`/`registerService` pair when the effective dispatcher
  contract uses a different valid route.
- **[RP-INET-INHERITED-PRIMITIVE-DISPATCH]** When protocol message classes inherit from one another, make sure broader dispatch does not consume a specialized primitive and produce the wrong confirmation or indication.
- **[RP-INET-OPERATION-IDENTITY]** Duplicate or stale-operation detection must use the protocol identity and generation defined by the owning protocol, not merely equality of request fields.

## Lifecycle, state, and configuration

- **[RP-INET-LIFECYCLE-OPERATIONS]** Trace lifecycle operations through the component's actual abstraction, such as `OperationalMixin` start/stop/crash handlers or `ILifecycle::handleOperationStage`. Exercise graceful asynchronous stop separately from crash teardown; verify that owned state, timers, messages, packets, and registrations are safe in the promised stopped/dead state and that supported restart re-establishes invariants without stale work.
- **[RP-INET-STATE-SCOPING]** Exercise two supported interfaces, peers, flows, agreements, or directions with different state and verify that activity in one cannot overwrite, clear, or misclassify the other. Let the architecture checklist own state-placement or ownership concerns that have no demonstrated behavioral consequence.
- **[RP-INET-TRANSACTION-GENERATIONS]** Verify current and pending transactions have distinct ownership and cancellation rules. A late callback from an old generation must not complete or clear the new one.
- **[RP-INET-TRANSACTION-MACHINERY]** When a narrow race fix adds several identities, generations, tags, counters, or re-entrancy guards, investigate which demonstrated stale, terminal, or lifecycle path each mechanism prevents. Confirm that the machinery is proportionate without assuming a smaller design covers protocol cases that have not been traced.
- **[RP-INET-NED-COMPOSITION]** Resolve INET NED composition, feature declarations, optional modules, radio/medium or protocol pairings, and custom configurations in addition to the underlying OMNeT++ precedence rules.
- **[RP-INET-NED-PARAMETER-CONTRACT]** For a new or changed NED parameter, confirm that its declaration makes purpose, unit, valid range, sentinel or zero meaning, and interactions with related parameters discoverable. Trace defaults and overrides through validation and C++ consumption, especially where individually valid values can produce invalid ordering, subtraction, expiry, or retry behavior together.

## Serialization and wire contracts

- **[RP-INET-MSG-CONSUMERS]** Trace changed `.msg` fields through generated types and existing consumers to find incorrect
  behavior; leave missing required introspection artifacts to the canonical architecture checklist.
- **[RP-INET-SERIALIZATION-VALIDATION]** Validate model/configuration invariants before serialization while keeping serializer field-range and body-bound checks strict.
- **[RP-INET-WIRE-LAYOUT]** For decode/modify/encode paths, check declared body/chunk length against bytes written and consumed, field order and bit width, reserved bits, protocol-defined byte order, field counts and ranges, duplicate elements, trailing bytes, and byte-exact round trips where required. Writer/reader symmetry is insufficient when both repeat the same layout error.
- **[RP-INET-UNIT-CONVERSION]** Trace units and conversion ownership across NED, C++, model fields, serializers, and wire encodings. Test zero, destination resolution, values not exactly representable, and overflow; apply the byte order and unit defined by the specific protocol rather than a universal network-order rule.
- **[RP-INET-UNKNOWN-EXTENSIONS]** Decide explicitly whether unknown protocol extensions must survive mutation. If order matters, typed known elements plus ordered opaque elements may be required; an untouched serializer cache does not prove reconstructed preservation.

## Focused verification

Choose the test category under the active project guidance, then use the smallest INET check that reaches the
production integration:

| Mechanism | High-value check |
| --- | --- |
| Packet ownership | accept, drop, refusal, callback, early return, teardown |
| Chunk and tag transformation | aligned, crossing, fragmented, type variant, changed length, duplicate-and-clear paths |
| Provider/queue API | empty, absent, invalid, out of range, closed/disabled provider, shared buffer |
| Ordering selector | first blocked item, legal bypass, selected output, residual queue order |
| Protocol dispatch | base and derived primitive, unsupported variant, stale generation |
| Lifecycle operation | start, stop, crash, restart, pending operation cleanup |
| Serialization | independent layout oracle, untouched and modified round trips, unit boundary, unknown extension |
| Feature composition | built-in default, feature off, explicit override, valid custom config |

Use the owning test or simulation skill for the selected check.

## Generated and external consumers

**[RP-CPP-COMPATIBILITY-REACHABILITY]** Changes to signatures or enums can reach generated callers, reflection, registration, serializers,
printers, NED, and external result-analysis tools. Check these consumers when assessing compatibility
or apparently dead code. For externally visible enum values, apply the active release guidance;
ordinary diagnostic logs establish numeric stability
only when they are a defined published or tooling interface.
