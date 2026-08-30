# High-value bug checks for INET pull requests

> Migration source, not an authoritative skill reference. The maintained review instructions live in the layer references under `.agents/skills/inet-code-review/references/`. Fixed importance labels and detailed correction recipes below are historical source material; reviewers must derive severity from proved reachability and consequence and follow the authoritative layer wording when it differs from an example here.

All examples below are deliberately hypothetical. Names and snippets are illustrative pseudocode rather than references to a particular branch, revision, or source file. This keeps each check useful even when a similar defect is fixed in the codebase.

Label meanings:

- `C++`: language, type, lifetime, container, arithmetic, or dispatch correctness.
- `NED/INI`: declarative module structure, parameter declaration/default/lookup, or configuration behavior.
- `OMNeT++`: simulator scheduling, ownership, signals, initialization, inspection, or generated-message semantics.
- `INET`: INET-specific packet, chunk, tag, queueing, lifecycle, protocol, or test contracts.
- `802.11`: IEEE 802.11 frame, state-machine, timing, addressing, aggregation, or management semantics.

Importance meanings:

- `CRITICAL`: can plausibly cause memory unsafety, undefined behavior, an unbounded run, or an immediate crash on ordinary valid input; address before continuing the review.
- `HIGH`: can silently produce wrong protocol state, packet contents, timing, ordering, or nondeterministic simulation behavior with meaningful blast radius.
- `MEDIUM`: a localized or configuration-dependent correctness defect that should be fixed but is usually bounded, diagnosable, or outside the principal protocol path.

Importance groups:

- `CRITICAL`: 1, 2, 3, 4, 5, 6, 7, 8, 9.
- `HIGH`: 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34.
- `MEDIUM`: 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48.

## 1. Packet/message ownership and memory lifecycle

**Labels:** `C++`, `OMNeT++`, `INET`

**Importance:** `CRITICAL`

Hypothetical example: a shared packet buffer evicts a `Packet *`, removes it from its container, notifies the packet's queue, takes OMNeT++ ownership, emits a drop signal, and deletes it. If the queue callback also deletes the packet, or a listener receives the signal after deletion, the path causes a double-delete or use-after-free. Verify every step's pre- and post-owner, notify observers only while the packet is alive, and make exactly one component responsible for final deletion.

## 2. Callback and signal registration/teardown symmetry

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `CRITICAL`

Hypothetical example: a receive coordinator stores raw `IChannelAccessCallback *` values registered by dynamically replaceable contention modules, but exposes no unregister operation. A contention module is deleted during reconfiguration, and the next medium-state notification calls its dangling pointer. Either couple the lifetimes structurally, unregister during teardown, or use a registration mechanism whose lifetime can be validated before dispatch.

## 3. Iterator invalidation during mutation

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `CRITICAL`

Hypothetical example: a Block Ack reorder buffer iterates through a `std::map`, deletes each entry's fragment packets, and calls `buffer.erase(it)` before the loop performs `++it`. The increment uses an invalid iterator. Use `it = buffer.erase(it)`, or collect keys first and erase them in a second pass. Verify every branch advances exactly once and that packet-count or byte-length accounting remains synchronized with the container.

## 4. Off-by-one and boundary errors in counters and indices

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `CRITICAL`

Hypothetical example: a Block Ack bitmap contains 64 sequence positions with 16 fragments each, and a helper maps 12-bit sequence numbers into a cyclic window. A loop uses `fragment <= 16`, writes one element past the bitmap, and treats sequence distance 2048 as unambiguously ordered. Test fragment 0 and 15, sequence 0 and 4095, `4095 + 1`, `0 - 1`, empty/full windows, invalid sentinels, and exactly half the cyclic range.

## 5. Null and not-found return handling

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `CRITICAL`

Hypothetical example: `findAgreement(peer, tid)` returns null for an unsolicited ADDBA response, but the caller immediately passes it to a policy that asserts non-null and later dereferences it. Exercise absent, duplicate, late, and already-cancelled entries. A missing result must be deliberately ignored, rejected, or reported according to the protocol contract rather than becoming a null dereference or an over-strong debug assertion.

## 6. Return-by-value versus dangling reference or pointer

**Labels:** `C++`, `INET`

**Importance:** `CRITICAL`

Hypothetical example: `getAddress(index)` returns `const Address&` into a `std::vector`. The caller saves it, then another operation appends and sorts addresses, reallocating the vector. The saved reference now dangles. Document invalidation rules, avoid retaining references across mutation, and return a small value or a lifetime-stable handle when callers cannot locally prove container stability.

## 7. Loop termination and progress guarantees

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `CRITICAL`

Hypothetical example: a repeating frame-sequence function recursively retries whenever its child produces no step, while its eligibility predicate remains true. A child that can never produce a frame causes unbounded recursion. Identify a monotonic progress measure, bound retries, or terminate with a defined result. Apply the same reasoning to scheduler loops whose providers all have zero weight or whose predicates never match.

## 8. Exception safety across ownership transfer

**Labels:** `C++`, `OMNeT++`, `INET`

**Importance:** `CRITICAL`

Hypothetical example: a buffer detaches three victim packets, then notifies their owning queues one by one before taking ownership and deleting them. The second callback throws, leaving the remaining detached packets still recorded by queues but by no buffer. Treat callbacks and signal listeners as exception boundaries, use RAII or a rollback-safe transaction where possible, and ensure every intermediate state has one clear owner and a valid cleanup path.

## 9. Event-loop livelock from zero-delay self-scheduling

**Labels:** `C++`, `OMNeT++`, `INET`

**Importance:** `CRITICAL`

Hypothetical example: a queue module receives a packet, finds the downstream module busy, and immediately sends the packet to itself as a zero-delay self-message retry. No backoff timer is used. The downstream module remains busy because it never receives processing time, creating an infinite chain of zero-delay self-messages at the same `simTime()`. The simulation appears to hang with simulation time frozen. This differs from check 7 (C++ loop termination): check 7 addresses unbounded loops within a single `handleMessage` invocation, while this check addresses unbounded chains of events across multiple invocations that never advance simulation time. Ensure every retry or re-scheduling path either advances simulation time by a nonzero amount, has a bounded retry count, or has a guaranteed exit condition that does not depend on other modules making progress during the same simulation time instant.

## 10. Timer scheduling: absolute vs. relative time

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: an agreement object computes `expiration = simTime() + inactivityPeriod` and passes it to `scheduleInactivityTimer(expiration)`. The callback implements that operation as `rescheduleAfter(expiration, timer)`, treating an absolute timestamp as a relative delay. At simulation time 10 s, an expiration of 12 s is therefore scheduled for 22 s. Review the entire call chain so absolute deadlines reach `scheduleAt`/`rescheduleAt`, while durations reach `scheduleAfter`/`rescheduleAfter`.

## 11. State-machine terminal-path completeness

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: an ADDBA manager inserts a `PENDING` agreement when it sends a request and removes it after rejection, timeout, or DELBA, but the transmit retry-limit path merely drops the request frame. The peer/TID remains permanently pending and cannot start another negotiation. For every stateful transaction—association, BA negotiation, authentication, scanning—enumerate the complete set of terminal paths: accepted response, rejected response, ACK failure, retry limit, timeout, explicit removal, cancellation, and module teardown. Every terminal path must advance or remove the transaction exactly once.

## 12. Fragmentation/reassembly identity, ordering, wrap, and expiry

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: a reassembly table is keyed only by sequence number and stores fragments in arrival order. Fragment 2 with the "last" bit arrives before fragments 0 and 1, while another transmitter uses the same sequence number. A naive implementation either joins frames from different senders or discards the early fragment when fragment 0 arrives. Key by every discriminating field, place fragments by fragment number, tolerate out-of-order and duplicate arrivals, handle sequence wrap, and expire incomplete entries. Exercise orders such as `2(last),0,1`, `1,0,2(last)`, duplicates, multiple peers/TIDs, and 4095-to-0 wrap.

## 13. Stale-response and transaction-identity correlation

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: station A starts ADDBA transaction token 7 with station B, times out, and starts a replacement with token 8 for the same TID. A delayed response carrying token 7 then arrives. If lookup uses only peer address and TID, the response mutates the token-8 agreement. Match every response against the current transaction's full identity—such as peer, TID, dialog token, and local generation—and reject stale or unsolicited responses.

## 14. Re-entrancy from callbacks and synchronous signals

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: a contention object invokes `callback->channelAccessGranted()` and then sets its member `callback` to null. The callback synchronously starts a new contention and installs a new callback, which the old handler then erases on return. Clear or move the completed state before invoking external code, guard forbidden re-entry explicitly, and ensure a nested callback cannot be mistaken for the operation currently completing.

## 15. Serialization/deserialization round-trip and byte layout

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: an ADDBA serializer declares a nine-byte action body but writes category, action, dialog token, packed parameters, timeout, and sequence control using ten bytes because one field is emitted at the wrong width. Its paired reader appears to round-trip locally because it repeats the same mistake, yet external peers see an invalid frame. Check declared length, bytes written and consumed, independent field order, bit widths, reserved bits, byte order, and unit conversion against the wire format—not only writer/reader symmetry. Pay particular attention to endianness: INET serializers must write multi-byte fields in network byte order, and confusing `writeUint16` (host order) with `writeUint16Be` (big-endian / network order) is a common source of silent corruption.

## 16. Default-parameter and initialization gaps

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: an ADDBA response builder sets receiver, TID, buffer size, and timeout but leaves `statusCode` and `dialogToken` untouched. Generated-message defaults make simple tests pass with token 1, but a request using token 9 receives the unchanged generated default rather than the copied request token. Give every field a deliberate default or set it on every construction path, and test nondefault tokens, rejection responses, copied objects, and factory-created objects.

## 17. Comparison and matching logic completeness

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: an ACK-state map is keyed by receiver address, TID, sequence number, and fragment number. When a BAR is transmitted, a loop compares only TID and sequence/fragment before setting entries to `WAITING_FOR_BLOCK_ACK`. Frames for another receiver with coincidentally equal numbers are changed too. Derive the required identity tuple explicitly and compare every component on every lookup, update, and erase path.

## 18. Copy versus shared-pointer aliasing of packets and chunks

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: a fragmenter gives every output packet the same shared MAC-header chunk and then mutates its fragment number for each packet. All fragments end up observing the last assigned number. Duplicate or make the chunk exclusively owned before mutation, preserve immutable shared payload where appropriate, and verify that deleting source packets cannot invalidate fragment or reassembled data. Check region tags as byte ranges rather than blindly cloning packet-wide metadata.

## 19. Tag lifetime and sender-local versus packet-domain scope

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: a transmitter adds a local `RequestedWifiModeTag` used to configure its radio. The simulated wireless medium duplicates the packet without clearing tags, so the receiver mistakes that request for an indication of the mode it actually decoded. Strip sender-local request tags at the transmission boundary, retain only explicitly packet-domain metadata, and reconstruct receiver indications once from receiver-side reception facts.

## 20. Floating-point and `simtime_t` equality comparisons

**Labels:** `C++`, `OMNeT++`, `INET`

**Importance:** `HIGH`

Hypothetical example: a receiver independently computes `expectedEnd = start + bits / bitrate` using a `double`, while a timer was scheduled from a quantized `simtime_t` duration. The handler checks `simTime() == expectedEnd` and misses the transition by one simulation tick. Trace the provenance of both operands: exact equality is sound when both reuse the same stored `simtime_t` timestamp, but independently calculated or floating-point-derived times usually need ordering, explicit quantization, or a justified tolerance.

## 21. Unit consistency: time, rate, and length

**Labels:** `C++`, `NED/INI`, `OMNeT++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: a NED parameter stores an inactivity timeout in TUs (Time Units, 1 TU = 1024 μs), C++ reads it as microseconds, and the serializer divides it by 1024 again before writing a 16-bit TU field. The effective timeout becomes 1024 times too small. The TU ↔ μs conversion is the single most common unit trap in 802.11 code. Annotate units at interfaces, use unit-aware quantities where available, and test zero, minimum and maximum encoded values, overflow, and values not exactly representable at the destination resolution.

## 22. Concurrency of events and overlapping self-messages

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: starting association schedules an `associationTimeout`; a retry path allocates and schedules a second timeout without cancelling the first. A response and the stale timeout arrive at the same simulation time, and event insertion order decides whether the station becomes associated or reports failure. Maintain at most one scheduled timeout for the transaction, cancel or reschedule deliberately, clear timer state on every terminal path, and define deterministic handling for same-time response and timeout events.

## 23. Error and reject paths leaving partial state

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: an AP reserves an association ID and inserts a station record before validating the station's required PHY capabilities. Validation fails and a rejection is sent, but the reservation and partial record remain. Define each reject path's postcondition and unwind every mutation that is not intentionally retained; a later valid request must not inherit phantom authentication, association, resource, or timer state.

## 24. Signed/unsigned mismatch and underflow

**Labels:** `C++`, `INET`

**Importance:** `HIGH`

Hypothetical example: cleanup code executes `numPending--` on an unsigned counter after receiving the same terminal callback twice. Zero wraps to a huge value and permanently makes the queue appear nonempty. Guard decrements with invariants, pair increments and decrements one-to-one, and test zero boundaries. Reverse loops such as `for (size_t i = last; i >= 0; --i)` also need an explicit zero break or an iterator-based formulation.

## 25. Idempotency of terminal handlers

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: a DELBA transmit completion and an inactivity timeout both call `terminateAgreement(peer, tid)` for the same entry. The first call erases and deletes it; the second dereferences the now-missing lookup and emits a second deletion signal. Terminal handlers should tolerate repeated or reordered delivery: find before use, erase once, make later calls no-ops, and ensure signals and accounting reflect one transition.

## 26. Ordering guarantees preserved through a new path

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: an A-MSDU builder scans queue order `[eligible A, temporarily blocked B, compatible C]` and skips B to include C. The aggregate bypasses an earlier packet from the same ordered flow. Define the ordering barrier and stop the forward scan at the first packet that cannot be bypassed; tests must verify both selected aggregate members and the residual queue order.

## 27. Backward compatibility of persisted or exchanged formats

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: a management-frame reader starts requiring a newly supported optional HT element. Legacy peers omit it, so the reader consumes the following bytes as that element or rejects an otherwise valid frame. Test old and new encodings, optional absence, reordered elements where permitted, and unknown vendor elements. Mandatory fields must decode identically, and adding writer support must not imply that every peer sends the field.

## 28. Hidden virtuals and signature shadowing after contract changes

**Labels:** `C++`, `INET`

**Importance:** `HIGH`

Hypothetical example: a base queue changes `virtual Packet *remove(Packet *)` to `virtual Packet *remove(const Packet *)`. A derived class retains the old signature without `override`, so it declares a different function and calls through the base interface no longer reach it. Put `override` on every intended override, consider `using Base::method` when extending overload sets, and compile every concrete implementer after changing an interface's parameters, qualifiers, defaults, or return type.

## 29. `.msg`-generated defaults, sentinels, and enum base values

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: a generated `ConfigureRadioCommand` uses channel 0 as the default, while the handler interprets every nonnegative channel as an explicit request. Constructing the command only to change bitrate unintentionally moves the radio to channel 0. Give optional generated fields explicit out-of-domain sentinels or presence flags, initialize transaction/generation identifiers deliberately, and verify setting one field changes only the intended property.

## 30. Lifecycle operation handling: start, stop, and crash

**Labels:** `C++`, `OMNeT++`, `INET`

**Importance:** `HIGH`

Hypothetical example: a routing module cancels its hello timer in `handleStopOperation` but not in `handleCrashOperation`. After a crash-restart cycle, the timer pointer is stale and `cancelEvent()` is never called, causing a dangling self-message that fires with invalid module state. Every module using `OperationalMixin` or `ILifecycle` must handle all three lifecycle transitions. `handleStopOperation` should perform an orderly shutdown: cancel timers, send goodbye messages, and release resources. `handleCrashOperation` must perform abrupt cleanup without sending any messages—cancel and delete all self-messages, clear queued packets, and reset state to initial values. Verify that a stop-start and crash-start cycle each produce a module indistinguishable from a freshly initialized one, and that no stale association, route, or timer state leaks across the boundary.

## 31. Packet/chunk length accounting consistency

**Labels:** `C++`, `INET`

**Importance:** `HIGH`

Hypothetical example: a protocol encapsulator removes a 20-byte header with `removeAtFront` and inserts a 24-byte replacement with `insertAtFront`, but a preceding region tag still maps bytes 0–19 as the original header region. Downstream dissection reads four bytes of payload as header trailer. When replacing or wrapping chunks, verify that (a) the sum of all chunk lengths equals the packet's `getTotalLength()`, (b) region tags are updated to reflect the new byte offsets, (c) serialized byte count matches `getChunkLength()` for every chunk in the packet, and (d) removing a header and re-inserting it at a different size does not leave orphaned tag regions or phantom bytes.

## 32. Already-scheduled self-message rescheduling

**Labels:** `C++`, `OMNeT++`, `INET`

**Importance:** `HIGH`

Hypothetical example: a beacon generator schedules `beaconTimer` in `handleStartOperation`. A parameter-change callback also calls `scheduleAt(nextBeaconTime, beaconTimer)` without checking `beaconTimer->isScheduled()`. If the parameter changes before the first beacon fires, OMNeT++ aborts with "Cannot schedule message: it is currently scheduled." Always call `cancelEvent(timer)` before `scheduleAt`, or use `rescheduleAt`/`rescheduleAfter` which handle the cancel-and-reschedule atomically. When two independent code paths can schedule the same self-message object, define a single scheduling authority, or guard every scheduling call with an `isScheduled()` check.

## 33. Chunk type assumptions after `peekAtFront`

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: a statistics filter calls `packet->peekAtFront<Ieee80211DataHeader>()` to extract the TID field. A management frame traverses the same code path, and `peekAtFront` fails with a runtime `check_and_cast` error because the front chunk is an `Ieee80211MgmtHeader`. The crash occurs only when management traffic is present. Before calling `peekAtFront<T>()`, verify the chunk type with `dynamicPtrCast` and a null check, or guard the call with a type test on the packet's protocol or a preceding `peekAtFront` to a common base type. When both data and management frames share a path, use `Ieee80211MacHeader` (the common base) and downcast only after inspecting the frame type field.

## 34. Default NED parameter values changing existing scenarios

**Labels:** `NED/INI`, `INET`, `802.11`

**Importance:** `HIGH`

Hypothetical example: a Wi-Fi interface adds `string opMode = default("ht")` and propagates it through `**.opMode`. Existing INI files set only bitrate, so networks that previously used legacy mode silently switch to HT and produce different timing and fingerprints. Resolve inheritance and wildcard precedence, identify every scenario that inherits the new default, and either preserve previous effective behavior or document and test the intended migration.

## 35. Fingerprint regression analysis

**Labels:** `C++`, `NED/INI`, `OMNeT++`, `INET`, `802.11`

**Importance:** `MEDIUM`

Before accepting a new fingerprint, determine whether the change reflects a real behavioral divergence or only a change in the hashing inputs while simulated behavior remains equivalent.

Hypothetical example (behavioral): a TXOP-budget calculation changes from subtracting the last frame duration to subtracting the complete exchange duration. A focused Wi-Fi scenario now sends one fewer frame in a TXOP and its fingerprint changes. Do not accept a new fingerprint solely because the new value is stable: identify the first divergent event, relate it to the intended behavioral change, and use a directly mapped test or packet/event trace to rule out accidental changes.

Hypothetical example (ingredient): an empty helper submodule is inserted into a compound module. Packet delivery and timing remain identical, but module IDs and event numbers change, so a fingerprint containing those ingredients changes. Determine which ingredients diverged before claiming a behavioral regression—the simulation may be equivalent despite a different hash.

## 36. Enum/switch exhaustiveness after adding cases

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `MEDIUM`

Hypothetical example: `AckStatus` gains `BLOCK_ACK_NOT_ARRIVED`, but `getStatusString()` and `isTerminal()` still handle only the older values. Logging throws for the new status while the state machine silently treats it as nonterminal. Audit every switch and classification expression when an enum changes. Prefer compiler-visible exhaustive handling; use a `default` only when unknown numeric values are genuinely part of the contract.

## 37. Signal emission correctness

**Labels:** `C++`, `NED/INI`, `OMNeT++`, `INET`, `802.11`

**Importance:** `MEDIUM`

Hypothetical example: a MAC emits `agreementAdded` whenever it receives an ADDBA request, even when policy rejects the request or it is a duplicate of an existing agreement. A NED statistic calculates active agreements as additions minus deletions, so the count drifts upward. Emit lifecycle signals exactly once, with a live and correct payload, only after a real transition; retries, duplicates, rejections, and no-op deletion attempts must not alter the statistic.

## 38. `INITSTAGE` ordering dependencies

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `MEDIUM`

Hypothetical example: a MAC writes its address into a shared MIB during `INITSTAGE_NETWORK_INTERFACE_CONFIGURATION`, while a management module reads the address during `INITSTAGE_LINK_LAYER`. It works because those stages happen to be registered in that order, but no dependency expresses the requirement. Declare or otherwise enforce the dependency, and test initialization with optional modules and alternate compositions so consumers cannot observe a default address or null service. For reference, the typical INET stage ordering is: `INITSTAGE_LOCAL` → `INITSTAGE_PHYSICAL_ENVIRONMENT` → `INITSTAGE_PHYSICAL_LAYER` → `INITSTAGE_LINK_LAYER` → `INITSTAGE_NETWORK_LAYER` → `INITSTAGE_NETWORK_ADDRESS_ASSIGNMENT` → `INITSTAGE_NETWORK_CONFIGURATION` → `INITSTAGE_NETWORK_INTERFACE_CONFIGURATION` → `INITSTAGE_STATIC_ROUTING` → `INITSTAGE_ROUTING_PROTOCOLS` → `INITSTAGE_TRANSPORT_LAYER` → `INITSTAGE_APPLICATION_LAYER` → `INITSTAGE_LAST`. Verify which stage your module uses and which stages its dependencies initialize in.

## 39. Gate and connection-discovery assumptions

**Labels:** `C++`, `NED/INI`, `OMNeT++`, `INET`, `802.11`

**Importance:** `MEDIUM`

Hypothetical example: a MAC follows `upperLayerOut->getNextGate()`, takes the owner module, and `check_and_cast`s it to an LLC interface. A custom NED network leaves the gate unconnected or inserts a relay module, causing initialization to abort with an opaque cast error. Validate connectivity before traversal, define whether intermediate channels/modules are allowed, and report the expected gate, path, and interface in configuration errors.

## 40. `check_and_cast` versus `dynamic_cast` failure modes

**Labels:** `C++`, `NED/INI`, `OMNeT++`, `INET`

**Importance:** `MEDIUM`

Hypothetical example: a scheduler uses `dynamic_cast<IPacketCollection *>` for each connected provider and stores null on failure. One query treats null as "unknown count," while another blindly dereferences it. Decide whether the wrong provider type is a configuration error or a supported optional capability. Use `check_and_cast` for the former; for the latter, use `dynamic_cast` and handle null consistently in every operation.

## 41. Predicate purity: const-correctness, side effects, and short-circuit safety

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `MEDIUM`

Functions used as predicates in searches, scheduling, or frame-sequence selection must be observational: free of mutation, safe under repeated, skipped, or differently ordered evaluation, and const-correct through the complete call chain.

Hypothetical example (side effect): `isFrameEligible(packet)` decrements a retry token when called. A query expression calls it twice for one packet, while a short-circuit branch skips it entirely for another; merely inspecting the queue therefore changes which packet can later transmit.

Hypothetical example (const violation): a queue search accepts `function<bool(const Packet *)>`, but an adapter casts away constness and asks a downstream consumer whether it can accept the packet. That query attaches a routing tag to the packet, mutating an object still owned by the queue.

Keep search predicates read-only through the complete call chain; if mutation is required, perform it only after ownership transfers and expose that behavior in a non-const contract. Predicates must not rely on evaluation order or count.

## 42. Map default construction through `operator[]`

**Labels:** `C++`, `INET`, `802.11`

**Importance:** `MEDIUM`

Hypothetical example: an AP asks whether `stations[address] == ASSOCIATED`. For an unknown address, `operator[]` inserts a default `NOT_AUTHENTICATED` entry, so a read-only query creates a station that later cleanup and notification logic treats as real. Use `find()`, `contains()`, or `at()` when absence differs from the mapped type's default state; reserve `operator[]` for intentional insertion.

## 43. Assertion and invariant strength

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `MEDIUM`

Hypothetical example: reassembly code applies `ASSERT(fragmentNumber == nextExpected)` to every received fragment. A legal out-of-order fragment aborts a debug simulation even though it should be buffered or rejected through normal protocol handling. Assertions should protect internal invariants, not assumptions about externally supplied frame order. Handle unusual but valid input deliberately and use controlled runtime errors only when the model's documented contract is violated.

## 44. Correct handling of empty collections

**Labels:** `C++`, `OMNeT++`, `INET`

**Importance:** `MEDIUM`

Hypothetical example: a priority scheduler treats a connected but empty packet collection as if the provider did not implement the collection interface and throws a configuration error. Elsewhere, a missing collection is treated as having zero packets, hiding invalid wiring. Define distinct semantics for present-but-empty, absent optional capability, invalid provider type, and out-of-range access, then apply them consistently to count, peek, remove, and clear operations.

## 45. Self-comparison and self-assignment

**Labels:** `C++`, `INET`

**Importance:** `MEDIUM`

Hypothetical example: a cache entry's move-assignment deletes its owned reception objects, copies raw pointers from the source, and clears the source. For `entry = std::move(entry)`, source and destination are identical, so the operation reads pointers it just deleted. Guard self-copy/self-move or implement assignment through a technique that is naturally self-safe. Agreement replacement code should likewise avoid moving an object into the slot from which it was obtained.

## 46. String and parameter lookup typos in NED wiring

**Labels:** `C++`, `NED/INI`, `OMNeT++`, `INET`, `802.11`

**Importance:** `MEDIUM`

Hypothetical example: NED declares `double addbaResponseTimeout`, while C++ reads `par("addbaReponseTimeout")`; an INI override uses the correctly spelled name. Everything compiles, but initialization fails only when that module type is instantiated. Treat the NED declaration, C++ lookup string, relative module path, conditional `typename`, parent assignment, and INI override as one contract, and exercise every optional configuration branch.

## 47. WATCH/inspection and logging referencing freed state

**Labels:** `C++`, `OMNeT++`, `INET`, `802.11`

**Importance:** `MEDIUM`

Hypothetical example: a `WATCH_PTRVECTOR(droppedFrames)` vector retains a packet pointer while cleanup deletes the packet and emits a synchronous signal before erasing the vector element. An inspector or signal listener dereferences the watched stale pointer only in verbose or interactive runs. Remove or null observable references before external callbacks, and log packet fields while the packet is still alive.

## 48. Protocol/service registration and dispatch mismatch

**Labels:** `C++`, `NED/INI`, `INET`

**Importance:** `MEDIUM`

Hypothetical example: a new transport protocol registers itself via `registerProtocol(Protocol::myProto, gate("ipOut"))` but the corresponding `MessageDispatcher` has no matching registration for incoming packets. Packets from the network layer addressed to `myProto` are dropped with a "no matching service" error that appears only when a specific configuration enables the protocol. Verify that every `registerProtocol` call has a matching `registerService` at the receiving dispatcher, that gate names match the NED wiring, and that both directions (request and indication/confirm) are registered. Test with minimal configurations that exercise each protocol path independently.
