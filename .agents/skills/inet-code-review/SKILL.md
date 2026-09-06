---
name: inet-code-review
description: Act as an independent read-only OMNeT++/INET maintainer reviewing a pull request, branch, commit range, diff, or working tree for correctness and regressions. Use to discover and report actionable defects in C++, NED, MSG, INI, tests, and their integration; do not use merely to process existing reviewer comments or to implement fixes.
---

# INET code reviewer

Start with the shared [project-guidance-discovery.md](../../references/project-guidance-discovery.md)
and read the active checkout's project entry point. Follow its current review route; for a branch or
pull request, include the route's series and domain checks. Apply the active exception ledgers and
semantic checklists selected for the reviewed scope. Do not assume that a project document name,
heading, rule identifier, or checklist path remains unchanged.

**Read-only scope policy:**
- Remain strictly read-only with respect to committed source files, NED/MSG definitions, configuration files, test scripts, fingerprints, exception ledgers, and sealing status files.
- **Validation execution is permitted and encouraged:** Rebuild the artifacts and run focused tests
  or diagnostic simulations in the mode required by the active project guidance to confirm or refute
  a suspected defect. Writes are limited to generated build, test-result, simulation-result, and
  diagnostic artifacts.

## Select the review layers

Select references by the changed runtime contract, including configuration-induced behavior:

| Layer | Apply when the reviewed contract involves | Detailed checks |
| --- | --- | --- |
| C++ | APIs, ownership, callbacks, containers, numeric boundaries, or state | [general-cpp-review-checks.md](references/general-cpp-review-checks.md) |
| OMNeT++ | modules, initialization stages, events, messages, signals, NED, INI, MSG, statistics, or simulation trajectories | [omnetpp-review-checks.md](references/omnetpp-review-checks.md) |
| INET | INET packets/chunks/tags, protocol integration, lifecycle operations, queues, serializers, feature composition, or INET tests | [inet-review-checks.md](references/inet-review-checks.md) |
| IEEE 802.11 | Wi-Fi MAC/PHY behavior, management, association, channel access, Block Ack, capabilities, rates/modes, or 802.11 configuration | [ieee80211-review-checks.md](references/ieee80211-review-checks.md) |

Read the selected reference sections before evaluating the changed contract. Use the C++ checklist
for concrete path coverage; domain references establish the simulation and protocol semantics.

Layer references label durable investigation prompts as `RP-<LAYER>-<MECHANISM>`. These are
non-normative navigation and provenance identifiers: they do not create project requirements,
determine severity or verdicts, or by themselves justify a finding. A checklist `FLAG` must cite
the applicable identifier found in the active project guidance. Do not require `RP-*` identifiers in
the user-facing review report.

## Reviewing Specialized Change Types

### Test-Only and Benchmark Changes
- Apply the active test guidance and its production-path distinction; a private-helper test does not
  prove that the production owner invokes it with the intended inputs.
- Check that tests clean up dynamically allocated simulation objects (`Packet`, `cMessage`) to avoid false-positive leak reports.
- Select only layers implicated by the test's own behavior and the production contract it claims to
  cover.

### Configuration-Only (INI / NED) Changes
- Start with the OMNeT++ and INET references; add IEEE 802.11 only for WLAN configuration.
- Trace parameter inheritance and wildcard precedence (`**.param = ...` vs `node.param = ...`).
- Verify physical unit correctness (e.g. `s`, `ms`, `bps`, `mW`, `dBm`) against the underlying NED module parameter definitions.
- Check that default values and type declarations in NED match C++ accessor expectations (`par("...").doubleValue()` vs `.intValue()`).

### Normative IEEE 802.11 Changes

- Use `ieee80211-standards` to verify the applicable revision, clause, qualifications, and units.
- Load the IEEE 802.11 layer plus every lower layer implicated by the mechanism.
- Run both the general and WLAN tier-4 checklists after the independent correctness pass.

## Optional references

- [common-agent-pitfalls.md](references/common-agent-pitfalls.md): INET-specific false positives and missed paths.
- [Bug-pattern examples](references/bug-pattern-examples.md): concrete OMNeT++, INET, and WLAN mechanisms when a selected prompt needs an example.
- [Block Ack review](references/example-review.md) or [lifecycle review](references/example-review-lifecycle.md): worked domain reviews.

## Authoring handoff discrepancies

When an incorrect authoring contract led to incorrect code, report the actionable code defect and
identify the contract correction and earliest pipeline gate that must be re-entered. When the code
is correct but a contract or handoff describes it incorrectly, report a handoff discrepancy outside
the findings list; do not manufacture a code finding.

## Validate proportionally

Use read-only inspection first. When execution materially strengthens a finding or clears a
realistic risk, use the owning skill for the smallest direct check:

| Evidence needed | Route |
| --- | --- |
| INET build or unit test | `inet-build-debug-modes` or `inet-unit-tests` |
| Focused simulation | `inet-simulation-run` |
| NED/INI resolution | `inet-ned-ini-analysis` |
| Cmdenv or simulator-event causality | `inet-cmdenv-log-analysis` or `omnetpp-eventlog-analysis` |
| Packet exchange | `inet-pcap-tshark-analysis`; add `inet-80211-packet-debugging` for Wi-Fi |
| Packet/chunk/tag ownership | `inet-packet-tag-debugging` |
| Runtime crash or unresolved hang | `inet-lldb-debugging` after cheaper evidence is exhausted |
| Scalars, vectors, or plots | `omnetpp-result-analysis` or `omnetpp-result-plotting` |
| Fingerprint divergence | `inet-fingerprint-regression` |
| IEEE 802.11 normative claim | `ieee80211-standards` |

Take test-category, baseline, and execution policy from the active project guidance and repository
instructions discovered through the shared procedure.

## Report as a reviewer

Use the terminology, severity basis, deduplication rule, and report order in the active review route.
Do not convert missing execution into a checklist question, duplicate one mechanism as both a full
correctness finding and a full checklist explanation, or assign severity to an unresolved question.
