# OMNeT++ and INET review patterns

Use these lenses to hunt for defects in the assigned change. They capture recurring failure mechanisms that ordinary line-by-line C++ review misses.

## Lifecycle, events, and module interaction

### Initialization and signals

Trace the initialization stage that subscribes, the stage that publishes, field defaults, and whether a scheduled event can run between them. Check abnormal lifecycle paths and runtime reconfiguration separately from normal initialization.

Separate state needed by configurators from negotiated or cross-node state. Registration, identity, and addresses may need to exist at an earlier initialization stage, while peer state may belong to actual lifecycle start. Exercise stop/start, crash, dynamic deletion, and restart rather than validating initialization only once.

When two fields mirror one fact, identify the authority and verify every writer. Derive management elements, MIB state, and configuration output from that authority instead of relying on synchronized sentinels.

### Observation versus control

Signals are normally observation interfaces. Flag protocol correctness that depends on a listener seeing an observation signal, especially when listener ordering or registration controls state transitions. Prefer an explicit typed call or message owned by the protocol state machine.

For synchronous calls across modules, verify gate/module discovery direction, method-entry requirements such as `Enter_Method`, and whether the callee may delete or retain arguments.

### Timers, retries, and terminal events

Name the timer semantics: whole transaction, latest attempt, inactivity, or response wait. Then verify arming, restart, cancellation, and stale expiry against that meaning.

Exercise ACK success, data failure, RTS/CTS failure, retry exhaustion, timeout, cancellation, and module shutdown. Terminal cleanup must be exactly once even when a late callback or timer arrives.

Keep “current” and “pending” state distinct. Reassociation can have a current AP and a different target; generic cleanup must not cancel both unless that is the explicit transition.

When a transaction commits only after a later ACK/callback, retain the state actually advertised in the response. Do not recompute from mutable current MIB/radio state at completion; a channel or capability change between construction and ACK can otherwise commit information the peer never received.

For statistics and semantic signals, verify paired event contracts. Emit “deleted” only for an object that previously emitted “added,” and order state establishment before a re-entrant operation that could synchronously tear it down.

Respect OMNeT++ deletion order. Cleanup that traverses child modules may be safe in `finish()` or `preDelete()` but unsafe in a destructor after descendants have already been destroyed. Make cleanup idempotent when multiple lifecycle hooks share it.

## Packet, queue, and callback ownership

### Movement is not deletion

Follow the concrete operation: duplicate, insert, pop, detach, move to a dropped list, return upward, delete, or defer to a destructor. Record who owns the packet after each step and the lifetime promised to synchronous callbacks. A borrowed pointer must not escape its callback unless the contract transfers ownership.

Check every accept, ignore, error, and early-return path for exactly one disposition. Packet loss, stale pointers, double deletion, and retention often live in the less interesting branch rather than the main path.

### Re-entrant notifications

OMNeT++ signal/callback handlers can synchronously re-enter the producer. When notifications can remove related packets, use a detach-all/mutate-all phase before notifying. Verify that excluded/current victims cannot be deleted underneath the outer loop.

### Collection interfaces

When a base class acquires a new collection or extractor interface, inspect every gate, queue, buffer, and scheduler subclass. An override set that made a closed gate appear empty may be incomplete for a newly added predicate extractor.

Beware loops whose bound shrinks as elements are removed. Snapshot the count or drain until empty, and test more than one or two elements. With shared buffers, verify that bulk removal is scoped to the owning queue.

If an interface is advertised but some providers cannot implement it, choose an explicit boundary contract: validate at initialization or provide a correct fallback. A null guard that silently reports “no packet” can be semantically wrong.

### Packet and region tags

Decide whether packet-scope tags should propagate to every replacement packet. For region tags, reason in absolute packet coordinates and copied interval length: source front offset plus fragment offset, exact fragment length, then rebase into the target region.

When a receiver clears sender-local tags, verify that it operates on a duplicate and restores or adds receiver-owned protocol metadata. Do not infer mutation of the transmitted packet from a local `clearTags()` call.

## Protocol state and variant coverage

### Single authority and independent windows

Avoid two mutable copies of association, sequence, retry, Block Ack, reorder, channel, or capability state. Related windows can have different owners and advance on different events: packet acknowledgment state is not the same as upward-delivery/reordering state.

For cyclic sequence spaces, use protocol-order comparisons with the defined half-space and test wraparound. Never rely on ordinary integer or map order across `4095 -> 0`.

### Capability direction and granularity

Negotiated capabilities are directional. A local-transmit decision must use the peer-receive side and validate all relevant dimensions, such as MCS, channel width, spatial streams, and guard interval. Do not infer an exact bitmap from a summary count.

Store capability at the granularity at which it varies: peer, TID, agreement, access category, or link. A station-wide flag is unsafe in a heterogeneous network.

### Dispatch and unsupported variants

If dispatch broadens from a concrete frame to a base class, enumerate every current and future subclass. Reject unsupported variants consistently at the boundary; do not let one path throw deep in processing while another silently returns an empty result.

When protocol messages inherit from one another, test the most-derived type before the base type. A base `dynamic_cast` can silently consume association/reassociation or other specialized primitives and emit the wrong confirmation.

Duplicate detection must use protocol identity—retry bit, transmitter, sequence/fragment, transaction or generation—not merely equal request parameters. Keep stale terminal events harmless after a new generation begins.

### Stable semantic selectors

Order-dependent lookup is fragile when catalogs contain equal bitrates or appended variants. Review first-entry, stable-sort tie, slowest-rate, and concrete-mode assumptions. Prefer explicit reference entries, typed PHY families, or fully qualified tuples when behavior depends on bandwidth, NSS, GI, band, or amendment.

Keep selectable/default modes separate from supplementary receive capability and per-packet decode support. Membership in an operational catalog, `supportsMode()`, and semantic equivalence are different contracts. Apply mode-set and current-mode changes atomically so no observer sees a tuple from the old set combined with the new set.

Test all built-in families and at least one valid custom/sparse configuration. A built-in invariant does not prove user-defined mode sets are safe.

## Serialization, generated types, and configuration

Validate wire invariants before serialization when they express model configuration, while keeping serializer range checks strict. Do not encode unrelated capability data merely to satisfy a mandatory legacy field.

For deserialize/reserialize changes, check exact body bounds, unknown information elements, trailing bytes, duplicate elements, field count/range, and byte-exact round trips. Decide explicitly whether unknown extensions must be preserved. Distinguish an untouched chunk whose serializer cache preserves original bytes from decode-modify-encode, parsim unpack, or reconstruction into a fresh object; only an ordered typed-plus-opaque element model can preserve arbitrary unknown-IE interleaving through mutation.

Trace `.msg` ownership through generated types, serializers, printers, and dissectors. Change the `.msg`, never generated `_m.h` or `_m.cc` files directly.

For NED/INI changes, resolve inherited defaults, wildcard precedence, `typename`, gate/vector paths, radio/medium pairing, and feature-off behavior. Review reference documentation as generated output of NED truth, not an independent configuration source.

## Regression design

Derive tests from the proof chain:

| Mechanism | High-value checks |
| --- | --- |
| Empty or removed state | empty bitmap/queue, one element, several elements, full boundary |
| Cyclic sequence logic | just before/at/after window, half-space boundary, wraparound |
| Fragmentation | no overlap, boundary-aligned, crossing tag, first/final fragment |
| Transaction lifecycle | success, retry, timeout, cancellation, stale/duplicate terminal event |
| Peer classification | current peer, pending target, same target, unrelated peer, missing peer |
| Mode/capability selection | every built-in family, sparse peer, width/GI mismatch, explicit override |
| Synchronous callback | valid borrowed lifetime, no retention, re-entrant deletion of siblings |
| Initialization | normal publication, delayed/unavailable value, stop/start, crash, runtime change |
| Polymorphic dispatch | base and every derived primitive, refused/success subtype, unknown variant |
| Observability | paired added/deleted events, exactly-once removal/drop, observer neutrality |

When a fix affects event trajectories, identify exact fingerprint rows and ingredients. Never assume an unexecuted ingredient remains valid because another ingredient was updated. Conversely, do not treat a changed fingerprint as correctness evidence without explaining the first causal divergence.

Run focused debug-mode checks owned by the relevant testing skills. Do not replace missing direct coverage with a broad suite; report the gap.
