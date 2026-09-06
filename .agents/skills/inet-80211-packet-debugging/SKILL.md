---
name: inet-80211-packet-debugging
description: Debug IEEE 802.11 PHY and MAC packet exchanges in OMNeT++/INET using reproducible evidence. Use for Wi-Fi packet generation, channel access, transmission, reception, ACK/RTS/CTS/Block Ack, aggregation, retransmission, association, roaming, AP forwarding, PHY interference, rate control, or packet-drop investigations using captures, logs, results, source inspection, or LLDB.
---

# Debug IEEE 802.11 packet exchanges

Use the shared [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to
discover the active checkout's current WLAN boundaries, owners, and verification obligations. This
skill adds the evidence path for locating a runtime divergence.

Find the first divergent transition:

```text
upper packet → management/data service → queue/QoS → DCF/EDCA
→ frame exchange → PHY construction → radio medium/channel
→ receiver decision → recipient MAC → upper delivery
```

Use the owning skills for simulation execution, NED/INI resolution, Cmdenv logs, PCAP/TShark, results, event logs, LLDB, and standards. This skill adds the Wi-Fi evidence model.

## Workflow

1. Record the configuration, run/seed, relevant packet/flow, and time or event interval.
2. Resolve instantiated AP/station, management, MAC, radio, and radio-medium types plus relevant feature gates.
3. Capture the smallest useful sender/receiver exchange. For a first PCAPng diagnostic, use computed checksum and FCS modes unless already effective.
4. Inspect frame type, addresses, Retry bit, sequence/fragment numbers, TID, ACK policy, aggregation, timing, and PHY metadata as relevant.
5. Add targeted logs, results, or a narrow event log for the first unexplained transition.
6. Inspect checked-out source for the exact policy/state-machine decision.
7. Use LLDB only after identifying a suspicious module, event, packet, or source path.

Use `ieee80211-standards` for normative questions and checked-out source plus observed runs for
implementation questions. Do not assume a standard feature is implemented or enabled.

## References

Load only what the question needs:

- [scope-and-reproducibility.md](references/scope-and-reproducibility.md): instantiated types, feature gates, and comparisons.
- [frame-model.md](references/frame-model.md): frame fields, addresses, sequence/fragment state, NAV, FCS, and errors.
- [phy-carrier-sense-and-timing.md](references/phy-carrier-sense-and-timing.md): radio compatibility, thresholds, interference, decoding, carrier sense, and timing.
- [mac-retry-aggregation-and-rate-control.md](references/mac-retry-aggregation-and-rate-control.md): coordination, protection, ACK/retry, fragmentation, aggregation, Block Ack, and rates.
- [management-forwarding-and-feature-gates.md](references/management-forwarding-and-feature-gates.md): association, roaming, AP forwarding, power save, and HT/VHT/HE/EHT gates.
- [evidence-tools.md](references/evidence-tools.md): 802.11 capture fields and source searches.
- [lldb-80211-breakpoints.md](references/lldb-80211-breakpoints.md): Wi-Fi breakpoint targets.
- [scenario-playbooks.md](references/scenario-playbooks.md): common failure investigations.

Do not infer PHY reception from a MAC capture, collision or drop from a missing ACK, final destination from Address 1, or airtime from nominal bitrate. Separate direct evidence by source from inference.
