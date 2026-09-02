# IEEE 802.11 review checks

Apply `doc/project/domain/ieee80211.md` and
`doc/project/enforcement/checklist/ieee80211.md` first. This reference adds concrete correctness
traps and high-value cases beyond those canonical WLAN rules.

## Semantic path coverage

- **[RP-WLAN-PATH-SIBLINGS]** Enumerate affected siblings explicitly: DCF/HCF, QoS/non-QoS, originator/recipient, AP/STA, infrastructure/ad hoc, unicast/group-addressed, and legacy/HT/VHT/HE/EHT paths as applicable.
- **[RP-WLAN-TERMINAL-PATHS]** Check success, refusal, timeout, retry exhaustion, cancellation, stale or duplicate completion, and reassociation while another relationship is current.
- **[RP-WLAN-FRAME-PATHS]** Exercise data, ACK, RTS/CTS, Block Ack, management, and control-frame terminal paths implicated by the change. Do not generalize evidence from one exchange to a sibling with a different owner or state machine.
- **[RP-WLAN-DISPATCH-VARIANTS]** Reject unsupported frame and primitive variants consistently at the dispatch boundary. A broader base-class match must not silently admit a specialized subtype.

## Association and transaction state

- **[RP-WLAN-ASSOCIATION-CURRENT-PENDING]** Keep current AP/peer state separate from a pending target. Reassociation or roaming cleanup must not erase the active relationship unless that is the intended transition.
- **[RP-WLAN-TRANSACTION-TIMERS]** Distinguish the whole transaction, individual transmission attempt, response wait, and inactivity timers. Verify retry, cancellation, and late callback behavior for each meaning.
- **[RP-WLAN-DEFERRED-COMMIT-SNAPSHOT]** When state commits after an ACK or later callback, retain the exact channel, capability, or management information advertised in the transmitted response. Do not recompute it from mutable MIB or radio state at completion.
- **[RP-WLAN-STATE-BEFORE-CALLBACK]** Establish negotiated state before emitting or invoking anything that can synchronously tear it down. Pair agreement-added and agreement-deleted observability exactly once. Example: clear or move the completing callback state before invoking it so a synchronously started replacement operation is not erased on return.
- **[RP-WLAN-TRANSACTION-IDENTITY]** Use protocol transaction identity or generation so a terminal event from an older exchange cannot complete a newer one with equal request parameters.

## Sequence, retry, and Block Ack state

- **[RP-WLAN-SEQUENCE-STATE-DOMAINS]** Exercise transmit acknowledgment, retry, receive duplicate detection, Block Ack agreement, reorder-window, and upward-delivery state independently. Verify that a transition in one does not incorrectly advance, clear, or reuse another state that follows different frames or events.
- **[RP-WLAN-SEQUENCE-WRAPAROUND]** Use 802.11 cyclic sequence ordering with the defined half-space. Test immediately before, at, and after the window boundary and across `4095 -> 0`; ordinary integer or map ordering is invalid there.
- **[RP-WLAN-STATE-CONTEXT]** Exercise simultaneous transmitter/receiver, TID, agreement, access-category, direction, or link contexts as applicable and verify that state from one context cannot affect another.
- **[RP-WLAN-DUPLICATE-IDENTITY]** Base duplicate detection on the specified identity, including retry, transmitter, sequence/fragment, TID, and exchange context as applicable—not only equal payload or request fields.
- **[RP-WLAN-FRAGMENT-REASSEMBLY]** For fragmentation and reassembly, derive the table key from every discriminating field, place fragments by fragment number, tolerate supported out-of-order and duplicate arrivals, and expire incomplete entries. Example: orders such as `2 (More Fragments clear), 0, 1` and `1, 0, 2 (More Fragments clear)` must not join fragments from different transmitters or complete before every required fragment is present.
- **[RP-WLAN-WINDOW-BOUNDARIES]** Exercise empty, singleton, full, overflow, fragmented, stale, and wraparound windows, plus retry exhaustion and agreement teardown.

## Capabilities, modes, and channels

- **[RP-WLAN-CAPABILITY-DIRECTION]** Treat negotiated capabilities as directional. A local transmit choice must use the peer receive capability and validate every required dimension: MCS, channel width, spatial streams, guard interval, coding, and PHY family as applicable.
- **[RP-WLAN-CAPABILITY-CONTEXT]** Exercise peers, TIDs, agreements, links, or directions with different capabilities and verify that a decision for one does not reuse another's state. Do not infer an exact MCS map or bitmap from a summary count.
- **[RP-WLAN-MODE-IDENTITY]** Prefer typed PHY family and fully qualified mode tuples over bitrate, vector order, first-entry, or stable-sort ties. Equal bitrates can represent semantically different modes.
- **[RP-WLAN-MODE-SETS]** Keep basic/default/selectable transmit modes separate from supplementary receive and per-packet decode support. Catalog membership, `supportsMode()`, mandatory-rate status, and semantic equivalence are different contracts.
- **[RP-WLAN-MODE-ATOMICITY]** Apply mode-set and current-mode changes atomically. Check all affected built-in PHY families plus a valid sparse/custom configuration, explicit overrides, width/GI mismatch, and unavailable peer capability.
- **[RP-WLAN-CHANNEL-SNAPSHOT]** Verify primary/secondary channel, bandwidth, and channel snapshot decisions against the state actually exchanged on the air.

## Management and wire elements

- **[RP-WLAN-MANAGEMENT-CONSISTENCY]** Vary capability and association state independently and verify that management information elements, MIB state, and configuration output remain mutually consistent and describe the state actually negotiated.
- **[RP-WLAN-MANDATORY-LEGACY-FIELDS]** Check mandatory legacy fields independently from amendment capabilities; do not encode unrelated capability data merely to satisfy a mandatory field.
- **[RP-WLAN-MANAGEMENT-PARSING]** For parsed and reconstructed management frames, verify body bounds, element counts/ranges, duplicate elements, unknown elements, trailing bytes, and required ordering preservation.
- **[RP-WLAN-UNKNOWN-ELEMENTS]** Distinguish byte preservation by an untouched chunk cache from decode/modify/encode behavior. Mutation may require ordered typed-plus-opaque elements to retain unknown extensions.

## Focused verification

Build the smallest deterministic exchange that distinguishes the suspected defect:

| Mechanism | High-value check |
| --- | --- |
| Path coverage | each affected MAC role/mode sibling and unsupported subtype |
| Association transaction | success, refusal, retry, timeout, cancellation, reassociation, stale completion |
| Fragment, Block Ack, or reorder | out-of-order/duplicate/expiry, before/at/after window, `4095 -> 0`, per-peer/TID state, teardown |
| Duplicate detection | retry/non-retry, fragment, same fields in a new generation or peer context |
| Capability selection | direction, sparse peer, width/NSS/GI mismatch, all affected PHY families |
| Mode lookup | equal bitrate, reordered catalog, explicit reference mode, custom mode set |
| Management serialization | untouched and modified round trips with unknown/duplicate elements |

Use packet captures, targeted logs, results, or a focused module/simulation test to prove the actual exchange. Start with one configuration and one run/seed; expand only when the first case is understood or a regression campaign is required.
