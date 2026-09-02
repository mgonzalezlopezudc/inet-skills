# INET bug-pattern examples

These hypothetical examples illustrate the named `RP-*` prompts. They are not findings by
themselves; establish the actual contract, reachable trigger, failure mechanism, and consequence in
the reviewed change.

## 1. Packet eviction has two possible final owners

**Related prompts:** `RP-INET-PACKET-DISPOSITION`, `RP-CPP-OWNERSHIP-TRANSITIONS`, `RP-CPP-OWNERSHIP-DISPOSITION`, `RP-OMNET-SIGNAL-PAYLOAD`

A shared buffer removes an evicted packet, notifies its queue, takes OMNeT++ ownership, emits a drop
signal, and deletes it. If the queue callback can also delete the packet, or the signal is emitted
after deletion, the same sequence contains a double disposition or use-after-free.

## 18. Several packets share a header that is later mutated

**Related prompts:** `RP-INET-CHUNK-MUTABILITY`, `RP-INET-REGION-TAG-OFFSETS`

A fragmenter inserts the same shared MAC-header chunk into every output packet and then changes the
fragment number for each output. All fragments observe the last value written, while blindly copied
region tags may also describe the wrong byte intervals.

## 19. A sender-local request becomes a receiver indication

**Related prompts:** `RP-INET-TAG-PROPAGATION`, `RP-INET-RECEIVER-TAG-MUTATION`

A transmitter attaches a requested Wi-Fi mode tag for its own radio. The medium duplicates the
packet without removing sender-local metadata, and the receiver later interprets the request as the
mode it actually decoded.

## 21. A protocol unit is converted twice

**Related prompts:** `RP-INET-UNIT-CONVERSION`, `RP-INET-NED-PARAMETER-CONTRACT`

A NED timeout ultimately represents 802.11 time units, C++ treats its numeric value as microseconds,
and the serializer divides by 1024 again when encoding the integer field. The timeout is scaled
incorrectly because no interface owns the single conversion between representations.

## 23. A rejected operation leaves reserved state behind

**Related prompts:** `RP-CPP-ATOMIC-STATE`, `RP-INET-TRANSACTION-GENERATIONS`, `RP-WLAN-TERMINAL-PATHS`

An AP reserves an association identifier and inserts a station record before validating required
capabilities. Validation rejects the request, but the reservation and partial record survive, so a
later valid request inherits state from an operation that never committed.

## 26. Aggregation bypasses an ordering barrier

**Related prompts:** `RP-INET-ORDERING-BARRIER`

An A-MSDU selector sees `[eligible A, temporarily blocked B, compatible C]`, skips B, and aggregates
C. If B is an ordering barrier for that flow, the newly added path transmits C ahead of B even
though every selected packet is individually eligible.

## 27. New writer support becomes an unintended reader requirement

**Related prompts:** `RP-INET-UNKNOWN-EXTENSIONS`, `RP-INET-WIRE-LAYOUT`, `RP-WLAN-MANAGEMENT-PARSING`, `RP-WLAN-UNKNOWN-ELEMENTS`

A management-frame writer gains an optional HT element, and the reader begins assuming the element
is always present. A legacy peer omits it, so the reader rejects a valid frame or consumes following
bytes as the missing element.

## 30. Stop and crash paths leave different stale work

**Related prompts:** `RP-INET-LIFECYCLE-OPERATIONS`, `RP-OMNET-LIFECYCLE-PHASES`, `RP-OMNET-TERMINAL-EVENTS`

A routing module handles its hello timer during graceful stop but overlooks it during crash. If the
component supports restart, the stale scheduled message later runs against dead or newly initialized
state. The required cleanup and notification behavior still depends on the component's actual stop,
crash, and restart contracts.

## 31. Replacing a chunk leaves lengths and tag offsets inconsistent

**Related prompts:** `RP-INET-PACKET-LENGTH-CONSISTENCY`, `RP-INET-REGION-TAG-OFFSETS`, `RP-INET-WIRE-LAYOUT`

An encapsulator replaces a 20-byte header with a 24-byte header, but a region tag still describes
bytes 0–19 as the old header. Packet length, chunk length, serialized byte count, and the affected
tag intervals no longer describe the same layout.

## 33. A shared path assumes one front-chunk subtype

**Related prompts:** `RP-INET-TYPED-CHUNK-DISPATCH`, `RP-WLAN-DISPATCH-VARIANTS`

A statistics filter unconditionally peeks an `Ieee80211DataHeader` to read TID. A management frame
uses the same path, so the typed peek fails even though the broader MAC-header contract admits that
frame subtype.

## 34. A new NED default silently changes old configurations

**Related prompts:** `RP-INET-NED-PARAMETER-CONTRACT`, `RP-INET-NED-COMPOSITION`, `RP-OMNET-OPTIONAL-CONFIGURATION`

A Wi-Fi interface introduces `opMode = default("ht")` and propagates it through wildcard
assignments. Existing configurations that set only bitrate inherit the new default and silently
change PHY timing and fingerprints.

## 46. NED and C++ disagree on a parameter name

**Related prompts:** `RP-INET-NED-COMPOSITION`, `RP-INET-NED-PARAMETER-CONTRACT`, `RP-OMNET-OPTIONAL-CONFIGURATION`

NED declares `addbaResponseTimeout`, while C++ looks up `addbaReponseTimeout`. Compilation succeeds,
but initialization fails only when the optional module type and configuration branch instantiate
the mismatched lookup.

## 48. Registration does not match the effective dispatch route

**Related prompts:** `RP-INET-UNSUPPORTED-VARIANTS`, `RP-INET-INHERITED-PRIMITIVE-DISPATCH`, `RP-INET-NED-COMPOSITION`

A new protocol registers its outgoing path, but the receiving dispatcher has no effective route for
the corresponding incoming packet or primitive in one optional composition. The defect is the
unreachable supported direction, not the absence of a syntactically paired registration call when
another valid routing mechanism exists.
