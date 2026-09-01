---
name: inet-80211-regression-testing
description: Design, run, and interpret focused IEEE 802.11 regression tests in INET. Use to create or diagnose deterministic Wi-Fi reproductions, choose seeds, compare before/after behavior, validate HE/EHT or MAC/PHY fixes, add unit or simulation coverage, or avoid overfitting an 802.11 change to one run.
---

# IEEE 802.11 regression testing

Select the claim, test category, and WLAN obligations through `doc/project/rule/testing.md`,
`doc/project/design/test-anatomy.md`, and `doc/project/domain/ieee80211.md`. This skill adds the
Wi-Fi-specific reproduction and invariant choices.

1. State the behavior and protocol-visible invariant under test.
2. Build the smallest deterministic scenario that exercises it.
3. Compare before/after with identical seed, debug binaries, NED path, configuration, and overrides.
4. Record the invariant with the most direct source: assertion, PCAP, targeted log, event log, or result.
5. Expand seeds or parameters only after the narrow case is understood, especially for contention, interference, mobility, rate control, or randomized traffic.
6. Use `inet-fingerprint-regression` for trajectory changes and `inet-ned-ini-analysis` for configuration uncertainty.

Useful invariants include association state, expected ACK/retry/drop behavior, protection policy, sequence/retry evolution, QoS mapping, aggregation/Block Ack progress, receiver power/SNIR/error decisions, AP forwarding addresses, and active HE/EHT feature gates.

Use `inet-unit-tests` and `inet-fingerprint-regression` for the filtered commands selected by the
canonical test policy; orchestration owns the handoff gate when agents are delegated.

Do not accept throughput improvement as proof of the targeted mechanism or use an ideal radio as
final verification unless it is the intended abstraction. Handle fingerprints through the
canonical baseline procedure.
