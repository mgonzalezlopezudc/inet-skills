# INET review checks

Apply these checks to INET framework contracts built on OMNeT++. Use the OMNeT++ layer for kernel mechanics and the IEEE 802.11 layer for Wi-Fi-specific invariants.

## Packets, chunks, and tags

- Follow each `Packet` and `Chunk` operation precisely: duplicate, peek, pop, insert, remove, trim, return, enqueue, drop, or defer. Record ownership and mutability after every operation.
- Check every accept, ignore, error, and early-return path for exactly one packet disposition. Moving a packet to a dropped or retirement list is not deletion. Example: if an eviction callback can delete a packet, establish container state and final ownership before notification and never access the packet afterward.
- Decide whether packet-scope tags must propagate to replacement packets. Verify which request, indication, dispatch, interface, and protocol tags are sender-local, receiver-owned, or preserved across encapsulation. Example: a sender-local requested radio mode must not cross the wireless medium and be mistaken for a receiver-side indication; reconstruct receiver metadata from reception facts.
- For region tags, compute in absolute packet coordinates using the source front offset, copied interval, and target rebasing. Exercise no-overlap, boundary-aligned, crossing, first-fragment, and final-fragment cases.
- When receiver processing clears sender-local tags, verify it mutates a duplicate or receiver-owned packet and then restores the metadata required by downstream dispatch.
- Check immutable versus mutable chunk access and serializer-cache assumptions when decoded data is modified or reconstructed. Example: fragments that share one mutable MAC-header chunk can all observe the last fragment number written unless each modified header has independent ownership.
- Before a typed `peekAtFront<T>()`, `popAtFront<T>()`, or equivalent operation, prove that the effective dispatch path admits `T`; otherwise inspect a common base or reject unsupported variants safely. Example: a path shared by data and management frames cannot assume `Ieee80211DataHeader` merely because most traffic is data.
- After replacing, splitting, or recombining chunks, reconcile packet total length, every affected region-tag interval, and serialized byte count with each chunk's declared length. Example: replacing a 20-byte header with a 24-byte header must not leave a tag describing bytes 0–19 as the old header.

## Queues, providers, and protocol integration

- When an INET collection, packet-provider, extractor, queue, buffer, gate, or scheduler interface changes, inspect every implementation and adapter. An older override that made a closed provider appear empty may not cover a new predicate operation.
- With shared buffers, scope bulk removal to the owning queue and verify callbacks cannot delete excluded or currently processed packets.
- Define the ordering barrier for every selector, aggregator, or scheduler and verify both selected output and residual queue order. Example: whether an eligible packet may bypass a temporarily blocked predecessor depends on the flow's ordering contract, not merely on forward-scan convenience.
- Distinguish present-but-empty, absent optional capability, invalid provider/wiring, and out-of-range access. Apply those outcomes consistently to count, peek, remove, clear, and predicate operations rather than collapsing them all into empty or null.
- Trace protocol registration and dispatch, service/protocol primitives, gates, and request/indication tags through the effective runtime path. Reject unsupported packet or primitive variants at a consistent boundary. Do not require a syntactic one-to-one `registerProtocol`/`registerService` pair when the effective dispatcher contract uses a different valid route.
- When protocol message classes inherit from one another, make sure broader dispatch does not consume a specialized primitive and produce the wrong confirmation or indication.
- Duplicate or stale-operation detection must use the protocol identity and generation defined by the owning protocol, not merely equality of request fields.

## Lifecycle, state, and configuration

- Trace INET lifecycle operations separately from OMNeT++ construction and deletion. Derive required stop, crash, and restart postconditions from the operations the component supports; do not assume that every operation performs graceful notification, deletes every timer, or recreates construction state. Exercise cleanup of current and pending state against those postconditions.
- Exercise two supported interfaces, peers, flows, agreements, or directions with different state and verify that activity in one cannot overwrite, clear, or misclassify the other. Let the architecture checklist own state-placement or ownership concerns that have no demonstrated behavioral consequence.
- Verify current and pending transactions have distinct ownership and cancellation rules. A late callback from an old generation must not complete or clear the new one.
- Resolve INET NED composition, feature declarations, optional modules, radio/medium or protocol pairings, and custom configurations in addition to the underlying OMNeT++ precedence rules.

## Serialization and wire contracts

- Trace changed `.msg` fields through generated types and every existing serializer, printer, dissector, protocol-registration, and reconstruction path to find incorrect consumers. Let `AR-OBS-INTROSPECTION` own whether a new protocol is required to ship missing introspection artifacts when no behavioral defect is otherwise proven.
- Validate model/configuration invariants before serialization while keeping serializer field-range and body-bound checks strict.
- For decode/modify/encode paths, check declared body/chunk length against bytes written and consumed, field order and bit width, reserved bits, protocol-defined byte order, field counts and ranges, duplicate elements, trailing bytes, and byte-exact round trips where required. Writer/reader symmetry is insufficient when both repeat the same layout error.
- Trace units and conversion ownership across NED, C++, model fields, serializers, and wire encodings. Test zero, destination resolution, values not exactly representable, and overflow; apply the byte order and unit defined by the specific protocol rather than a universal network-order rule.
- Decide explicitly whether unknown protocol extensions must survive mutation. If order matters, typed known elements plus ordered opaque elements may be required; an untouched serializer cache does not prove reconstructed preservation.

## Focused verification

Choose the smallest INET check that reaches the production integration:

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

Use focused unit tests for packet/serializer algorithms and filtered module or simulation tests for module calls, packet flow, lifecycle, and integration. Do not replace missing direct coverage with a broad suite.
