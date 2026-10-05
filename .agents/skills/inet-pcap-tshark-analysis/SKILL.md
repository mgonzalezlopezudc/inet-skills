---
name: inet-pcap-tshark-analysis
description: Analyze INET packet exchanges with PcapRecorder, Cmdenv, TShark, and capinfos. Use for capture setup, packet searches, protocol headers, TCP streams, retransmissions, or comparison across nodes and interfaces. Check whether an exchange occurred. Correlate captured packets with Cmdenv logs when necessary.
---

# Analyze INET packet captures

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's wire, observation, architecture, and evidence guidance. This skill adds recorder
placement, TShark inspection, and multi-point correlation mechanics.

## Workflow

1. Resolve the real node/interface paths and whether `numPcapRecorders` is supported.
2. Add narrow command-line recorder overrides. Prefer PCAPng and, for the first diagnostic run, computed checksum/FCS modes unless already effective.
3. Encode config, run, node, interface, and recorder in filenames.
4. Validate that each capture exists, is nonempty, and decodes:

   ```sh
   tshark -n -r <capture.pcapng> -c 10
   ```

5. Use offline display filters with `-Y` and `-T fields` for exact timelines/headers.
6. Record the observation points required by the canonical diagnosis guide in separate files.
7. Correlate `frame.time_epoch` with Cmdenv simulation time through the identifiers selected by that guide.

A recorder needs an observation point and a protocol representation.
The node-relative pattern `moduleNamePatterns` selects where it observes packets.
The parameter `dumpProtocols` selects the recorded representation.
A successful simulation does not prove that the recorder captured packets.

In a hypothetical example, a node contains `wlan[0]` and a recorder.
The pattern `wlan[0]` selects that interface relative to the node.
A change to `dumpProtocols` changes the representation, but the recorder still observes the selected interface.

Computed checksum/FCS modes may change packet processing.
Preserve those overrides.
Compare with the baseline when that distinction matters.
Preserve original captures before a filter or conversion changes them.

Read as needed:

- [capture-setup.md](references/capture-setup.md): recorder setup and capture-point selection.
- [tshark-inspection.md](references/tshark-inspection.md): fields, timelines, TCP analysis, and correlation.
- [comparison-diagnostics-reporting.md](references/comparison-diagnostics-reporting.md): multi-point comparison and empty/undecoded captures.

Interpret observation points and classify conclusions under the canonical diagnosis guide; report
TShark dissector heuristics explicitly.
