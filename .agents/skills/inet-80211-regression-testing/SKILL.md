---
name: inet-80211-regression-testing
description: Add IEEE 802.11-specific invariants, standards obligations, HE/EHT feature gates, and packet-exchange evidence to an INET regression design. Use with inet-regression-testing for Wi-Fi MAC/PHY behavior, management, retries, aggregation, Block Ack, association, or negotiated capability coverage; do not use for protocol-neutral regression design alone.
---

# IEEE 802.11 regression testing

First use `inet-regression-testing` for the behavior claim, invariant, category, minimal deterministic
reproduction, production-path evidence, and bounded campaign decision. This specialization adds only
the obligations that make that generic design valid for Wi-Fi.

Read `doc/project/domain/ieee80211.md`. For a normative claim, use `ieee80211-standards` to identify
the applicable standard revision, clause, role, and negotiated conditions before fixing the expected
exchange. Distinguish normative behavior from an intentional documented model limitation.

## WLAN invariant selection

Choose the smallest protocol-visible invariant that establishes the claim:

- management state and the corresponding request/response or timeout path;
- transmitter sequence/retry state and the expected ACK, Block Ack, retry, or drop outcome;
- QoS/TID mapping, aggregation window progress, reorder state, or fragment state;
- protection and channel-access decisions, including the relevant virtual/physical carrier sense;
- receiver power, SNIR, interference, synchronization, or error decision at the intended radio;
- AP forwarding address roles and duplicate-suppression identity;
- the negotiated HT/VHT/HE/EHT capability and operation elements that enable the mechanism.

For HE/EHT behavior, prove both the configured request and the active feature gate selected by the
effective NED/INI configuration. Under `AR-WLAN-STD-GATING`, show that the mode is standards-derived,
advertised or negotiated where required, and applied at the production decision point. A helper test
of a capability predicate is not evidence that the frame path uses it.

## Packet-exchange evidence

Prefer a module/protocol assertion when it directly observes the state transition. Use PCAP evidence
for transmitted frame roles, addresses, sequence control, ACK/Block Ack, aggregation, and retry
evolution; pair it with targeted logs or source-level evidence when the causal decision is internal
or a failed/corrupted reception is absent from the capture. Record capture point, simulation time
window, configuration, run, and seed.

Use `inet-ned-ini-analysis` when feature activation is uncertain,
`inet-80211-packet-debugging` when the exchange mechanism is unresolved, and
`inet-fingerprint-regression` only for unintended trajectory coverage under the canonical baseline
procedure.
