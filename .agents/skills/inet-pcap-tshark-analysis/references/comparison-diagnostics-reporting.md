## Contents

* Compare observation points
* Account for duplicate observations
* Diagnose empty or undecoded captures
* Build automated assertions

Apply the observation-boundary, evidence-classification, and reporting rules in
`doc/project/guide/diagnose-a-simulation.md`. This reference adds capture comparison and TShark
diagnostic mechanics.

## Compare observation points

Once the canonical guide identifies the required observation points, use separate files for each
node and interface.

Do not match packets by `frame.number`; each capture has independent numbering. Correlate with the strongest available identity:

* Addresses, ports, and protocol.
* IP fragmentation fields or transport sequence numbers.
* ICMP or application identifiers.
* Payload length or contents.
* Simulation timestamp.

Add an intermediate capture, targeted log, result counter, or event log when the selected observation
points do not locate the first missing transition.

## Account for duplicate observations

One logical packet may appear several times because recorders observe transmission and reception signals, multiple interfaces, encapsulation boundaries, forwarding, multicast copies, or retransmissions. Distinguish observations using the capture point, direction metadata, headers, sequence identifiers, length, and simulation time.

## Diagnose empty or undecoded captures

For an empty capture, verify task artifacts and configuration rather than tool installation:

1. Confirm the file exists and is nonempty.
2. Confirm the node path is instantiated and supports `numPcapRecorders`.
3. Confirm `moduleNamePatterns` matches a relative interface path crossed by packets.
4. Check `dumpProtocols`, `packetFilter`, the simulation interval, and link-type conversion.
5. Run once with recorder verbosity and targeted recorder logging.

For undecoded frames, inspect the encapsulation, protocol hierarchy, one full frame, the selected dump protocol, and whether a dissector exists. An empty decoded field is not evidence for a header value.

## Build automated assertions

Use a decoded field export and test its match count. Keep the display filter and capture point in the failure message. A zero count means only that no matching decoded frame exists in that capture.

When writing a filtered capture, preserve the original and validate the derived file before using it as evidence:

```sh
tshark -n -r "$PCAP" -Y "$FILTER" -w "$FILTERED"
test -s "$FILTERED"
capinfos "$FILTERED"
```

Add capture points and files, recorder options that affect interpretation, filters, matching frames
and `frame.time_epoch` values, packet identifiers, observation-point differences, decoding
limitations, and TShark heuristics to the canonical diagnosis report.

## Walkthrough Tables for IEEE 802.11 Examples

Route any request to generate or publish walkthrough tables through
`inet-80211-walkthrough-writer`. Its capability and canonical-placement gate must pass before any
analyzer command is used. If the active checkout lacks the tracked analyzer and README, report that
the workflow is unsupported; do not reconstruct it or substitute direct TShark output for the
script-owned presentation.
