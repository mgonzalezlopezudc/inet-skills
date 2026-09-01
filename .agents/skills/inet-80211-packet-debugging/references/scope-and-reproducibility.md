# Scope and reproducibility

Apply the canonical amendment-gating and model-evidence distinctions in
`doc/project/domain/ieee80211.md`, and the reproducibility rules in
`doc/project/guide/diagnose-a-simulation.md`. This reference adds instantiated-model inspection and
diagnostic artifact mechanics.

## Inspect the instantiated model

Reason from the effective NED and INI configuration, not from a similarly named example. Identify only the components involved in the question:

* Wireless interface, MAC, management, agent, queue, classifier, and radio types.
* Radio-medium and analog representation.
* Mode set, channel, frequency, and bandwidth.
* Protection, ACK, retry, fragmentation, aggregation, Block Ack, and rate-control policies.
* Sender, receiver, AP, and relevant intermediate module paths.

Use `inet-ned-ini-analysis` when inheritance, wildcard precedence, or `typename` selection is unclear. Treat the checked-out INET source as authoritative for implemented behavior.

## Establish feature gates

Apply `AR-WLAN-STD-GATING` from `doc/project/domain/ieee80211.md`. Use `ieee80211-standards` for its
normative-evidence lane, `inet-ned-ini-analysis` for its effective-configuration lane, and source
inspection for the checked-out implementation lane.

## Preserve comparable runs

Use command-line overrides for temporary capture, logging, event-log, and result diagnostics. Create a dedicated debug configuration only when repeated investigation would otherwise be error-prone.

Name generated captures, logs, event logs, and result files by configuration and run, then report
them through the canonical diagnosis guide.
