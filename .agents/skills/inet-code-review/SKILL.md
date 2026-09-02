---
name: inet-code-review
description: Act as an independent read-only OMNeT++/INET maintainer reviewing a pull request, branch, commit range, diff, or working tree for correctness and regressions. Use to discover and report actionable defects in C++, NED, MSG, INI, tests, and their integration; do not use merely to process existing reviewer comments or to implement fixes.
---

# INET code reviewer

Review the assigned change as an INET maintainer. Find defects independently; do not wait for the user to supply suspected problems.

For every correctness review, follow `doc/project/guide/review-a-code-change.md`. For a pull request
or branch series, additionally follow `doc/project/guide/review-a-pull-request.md` for the
commit-by-commit `PR-*` audit and integrated branch pass. When the scope reaches `src/inet/`, apply
the canonical rules, exception ledgers, and general semantic checklist selected through
`doc/project/README.md`. For IEEE 802.11 production scope, also apply its domain rules and
`doc/project/enforcement/checklist/ieee80211.md`.

**Read-only scope policy:**
- Remain strictly read-only with respect to committed source files, NED/MSG definitions, configuration files, test scripts, fingerprints, exception ledgers, and sealing status files.
- **Validation execution is permitted and encouraged:** Rebuilding debug artifacts (`MODE=debug`) and running focused unit/module tests or diagnostic simulations to confirm or refute a suspected defect is standard maintainer practice. Writes are limited to generated build, test-result, simulation-result, and diagnostic artifacts.

The canonical guide owns the finding threshold, severity basis, terminology, and report order. Read
[finding-quality.md](references/finding-quality.md) only when a suspected defect needs additional
proof-expansion or correction-direction techniques. Read relevant sections of
[common-agent-pitfalls.md](references/common-agent-pitfalls.md) when its false-positive or
missed-path patterns match the change. If an unfamiliar mechanism warrants a worked example,
optionally consult the [Block Ack example](references/example-review.md) or the
[non-WLAN lifecycle example](references/example-review-lifecycle.md); do not load examples by
default.

If a selected `RP-*` prompt remains abstract or a realistic counterexample would materially help
challenge a reachable path, consult the [bug-pattern example index](references/bug-pattern-examples.md).
Use its routing table to load only the topical catalog that owns the primary mechanism unless the
mechanism genuinely crosses layers. These examples are non-normative illustrations: do not infer
severity, applicability, or a mandatory correction from them, and do not load the catalogs by
default.

## Select the review layers

Apply the following layers cumulatively. Select them by the changed runtime contract, not only by file extension: a C++ change may require all four layers, while a NED-only change may require OMNeT++, INET, and IEEE 802.11 checks.

| Layer | Apply when the reviewed contract involves | Detailed checks |
| --- | --- | --- |
| General C++ | C++ APIs, object lifetime, containers, algorithms, callbacks, state, or polymorphism | [general-cpp-review-checks.md](references/general-cpp-review-checks.md) |
| OMNeT++ | modules, initialization stages, events, messages, signals, NED, INI, MSG, statistics, or simulation trajectories | [omnetpp-review-checks.md](references/omnetpp-review-checks.md) |
| INET | INET packets/chunks/tags, protocol integration, lifecycle operations, queues, serializers, feature composition, or INET tests | [inet-review-checks.md](references/inet-review-checks.md) |
| IEEE 802.11 | Wi-Fi MAC/PHY behavior, management, association, channel access, Block Ack, capabilities, rates/modes, or 802.11 configuration | [ieee80211-review-checks.md](references/ieee80211-review-checks.md) |

Layer references label durable investigation prompts as `RP-<LAYER>-<MECHANISM>`. These are
non-normative navigation and provenance identifiers: they do not create project requirements,
determine severity or verdicts, or by themselves justify a finding. A checklist `FLAG` must cite
the applicable canonical project rule identifier. Do not require `RP-*` identifiers in the
user-facing review report.

Read every selected layer reference before evaluating that contract. Do not load unselected layer
references. Keep findings at the layer that owns the violated contract, but use lower layers to
prove the mechanism.

### Context budget tiers

To prevent context exhaustion, scale reference loading by diff size and complexity:

- **Small Diff (< 100 lines, focused single subsystem):**
  1. The canonical review guide and the single primary layer reference.
  2. Load secondary layers only if a cross-layer mechanism appears.
  3. Load finding techniques, pitfalls, or examples only when the actual mechanism calls for them.
- **Medium Diff (100–500 lines, multi-file feature or fix):**
  1. The canonical review guide and all directly relevant layer references.
  2. Applicable canonical project rule and checklist sections.
  3. Relevant finding-technique or pitfall sections on demand.
- **Large / Cross-Cutting Diff (> 500 lines or subsystem overhaul):**
  1. Load selected layer references on demand per hunk or module group.
  2. Run the gates selected by `doc/project/guide/run-the-gates.md` before detailed semantic
     inspection.
  3. Reconcile the groups through the canonical integrated-contract pass before reporting.

When a specialized change type below names an explicit layer set, that set overrides the small-diff
single-primary default. Load the named set and no unrelated layers.

## Reviewing Specialized Change Types

### Test-Only and Benchmark Changes
- Apply `doc/project/rule/testing.md#tr-focused-evidence` and the production-path distinction in
  `doc/project/design/test-anatomy.md`; a private-helper test does not prove that the production owner
  invokes it with the intended inputs.
- Check that tests clean up dynamically allocated simulation objects (`Packet`, `cMessage`) to avoid false-positive leak reports.
- Do not flag missing production features as test defects; evaluate whether the test accurately exercises the claimed behavioral contract.
- Select only layers implicated by the test's own behavior and the production contract it claims to
  cover.

### Configuration-Only (INI / NED) Changes
- Start with the OMNeT++ and INET references; add IEEE 802.11 only for WLAN configuration. Do not
  load the General C++ layer unless the effective configuration exposes a changed C++ contract.
- Trace parameter inheritance and wildcard precedence (`**.param = ...` vs `node.param = ...`).
- Verify physical unit correctness (e.g. `s`, `ms`, `bps`, `mW`, `dBm`) against the underlying NED module parameter definitions.
- Check that default values and type declarations in NED match C++ accessor expectations (`par("...").doubleValue()` vs `.intValue()`).

### Normative IEEE 802.11 Changes

- Use `ieee80211-standards` to verify the applicable revision, clause, qualifications, and units.
- Load the IEEE 802.11 layer plus every lower layer implicated by the mechanism.
- Run both the general and WLAN tier-4 checklists after the independent correctness pass.

## Establish and test the review hypothesis

Resolve and record the target exactly as required by the canonical review guide. Treat a supplied
pre-write contract, behavior claim, pull-request description, or implementation report as evidence
and a hypothesis to test, not as authority. The checked-out source, effective configuration,
runtime evidence, applicable standards, and project contracts govern the review.

When an incorrect authoring contract led to incorrect code, report the actionable code defect and
identify the contract correction and earliest pipeline gate that must be re-entered. When the code
is correct but a contract or handoff describes it incorrectly, report a handoff discrepancy outside
the findings list; do not manufacture a code finding.

## Trace and prove the changed contract

Inspect beyond each hunk through the selected layer checks. Challenge boundary, alternate,
re-entrant, lifecycle, and supported-variant paths. Use the optional finding-technique reference
only when the canonical proof elements need help resolving ownership, reachability, or the safest
correction boundary.

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

Take test-category and baseline policy from `doc/project/rule/testing.md` and
`doc/project/guide/change-a-baseline.md`; apply the additional execution constraints in `AGENTS.md`.

## Report as a reviewer

Use the terminology, severity basis, deduplication rule, and report order in
`doc/project/guide/review-a-code-change.md`. Do not convert missing execution into a checklist
`QUESTION`, duplicate one mechanism as both a full correctness finding and a full checklist
explanation, or assign severity to an unresolved question.
