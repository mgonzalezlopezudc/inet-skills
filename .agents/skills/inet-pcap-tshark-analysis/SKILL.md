---
name: inet-pcap-tshark-analysis
description: Record and analyze packet exchanges in INET simulations using PcapRecorder, Cmdenv, TShark, and capinfos. Use when asked to find packets, inspect protocol headers, analyze TCP streams or retransmissions, compare captures from different nodes or interfaces, verify whether an exchange occurred, or correlate network packets with Cmdenv simulation logs.
---

# Analyze INET packet captures

Use the wire and observation boundary in `doc/project/design/packet-anatomy.md` and
`doc/project/rule/architecture.md`. This skill adds recorder placement, TShark inspection, and
multi-point correlation.

## Workflow

1. Resolve the real node/interface paths and whether `numPcapRecorders` is supported.
2. Add narrow command-line recorder overrides. Prefer PCAPng and, for the first diagnostic run, computed checksum/FCS modes unless already effective.
3. Encode config, run, node, interface, and recorder in filenames.
4. Validate that each capture exists, is nonempty, and decodes:

   ```sh
   tshark -n -r <capture.pcapng> -c 10
   ```

5. Use offline display filters with `-Y` and `-T fields` for exact timelines/headers.
6. Capture both endpoints when delivery, loss, or retransmission is disputed.
7. Correlate `frame.time_epoch` with Cmdenv simulation time and event numbers; never equate event numbers with `frame.number`.

`moduleNamePatterns` is relative to the recorder's node; `dumpProtocols` selects representation, not observation point. A successful simulation does not prove that recording occurred.

Computed checksum/FCS modes may change packet processing. Preserve those overrides and compare with the baseline when that distinction matters. Preserve original captures when filtering or converting.

Read as needed:

- [capture-setup.md](references/capture-setup.md): recorder setup and capture-point selection.
- [tshark-inspection.md](references/tshark-inspection.md): fields, timelines, TCP analysis, and correlation.
- [comparison-diagnostics-reporting.md](references/comparison-diagnostics-reporting.md): multi-point comparison and empty/undecoded captures.

Do not claim delivery from a sender capture or loss from absence at one point. Label direct packet evidence, dissector heuristics, correlated evidence, and inference.
