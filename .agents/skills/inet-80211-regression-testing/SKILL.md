---
name: inet-80211-regression-testing
description: Add IEEE 802.11 invariants, standards requirements, HE/EHT feature gates, and frame-exchange evidence to an INET regression design. Use with inet-regression-testing for Wi-Fi MAC/PHY, management, retries, aggregation, Block Ack, association, or negotiated capabilities. Do not use for protocol-neutral regression design alone.
---

# IEEE 802.11 regression testing

First use `inet-regression-testing` for the behavior claim, invariant, category, minimal deterministic
reproduction, production-path evidence, and bounded campaign decision. This specialization adds only
the obligations that make that generic design valid for Wi-Fi.

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's current WLAN guidance. For a normative claim, use `ieee80211-standards` to identify
the applicable standard revision, clause, role, and negotiated conditions.
Define the expected exchange from that evidence.
Distinguish normative behavior from an intentional documented model limitation.

## WLAN invariant selection

Choose the smallest protocol-visible invariant that establishes the claim:

- management state and the corresponding request/response or timeout path;
- transmitter sequence/retry state and the expected ACK, Block Ack, retry, or drop outcome;
- QoS/TID mapping, aggregation window progress, reorder state, or fragment state;
- protection and channel-access decisions, including the relevant virtual/physical carrier sense;
- receiver power, SNIR, interference, synchronization, or error decision at the intended radio;
- AP forwarding address roles and duplicate-suppression identity;
- the negotiated HT/VHT/HE/EHT capability and operation elements that enable the mechanism.

For HE/EHT behavior, prove the configured request and the active feature gate selected by the effective NED/INI configuration.
Use the discovered project guidance and source evidence to establish these conditions:

- The mode follows the applicable standard.
- Advertisement or negotiation occurs where required.
- The production decision uses the mode.

A helper test of a capability predicate does not establish that the frame path uses it.

## Frame-exchange evidence

Prefer a module/protocol assertion when it directly observes the state transition.
Use PCAP evidence for transmitted frame roles, addresses, sequence control, ACK/Block Ack, aggregation, and retry changes.
Add targeted logs or source-level evidence when the causal decision is internal.
Add the same evidence when a failed or corrupted reception is absent from the capture.
Record capture point, simulation time window, configuration, run, and seed.

Use the relevant diagnostic skill:

- Use `inet-ned-ini-analysis` when feature activation is uncertain.
- Use `inet-80211-packet-debugging` when the exchange mechanism is unresolved.
- Use `inet-fingerprint-regression` for unintended simulation-trajectory changes under the current baseline procedure.
