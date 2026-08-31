---
name: inet-code-review
description: Act as an independent read-only OMNeT++/INET maintainer reviewing a pull request, branch, commit range, diff, or working tree for correctness and regressions. Use to discover and report actionable defects in C++, NED, MSG, INI, tests, and their integration; do not use merely to process existing reviewer comments or to implement fixes.
---

# INET code reviewer

Review the assigned change as an INET maintainer. Find defects independently; do not wait for the user to supply suspected problems.

**Read-only scope policy:**
- Remain strictly read-only with respect to committed source files, NED/MSG definitions, configuration files, test scripts, fingerprints, exception ledgers, and sealing status files.
- **Validation execution is permitted and encouraged:** Rebuilding debug artifacts (`MODE=debug`) and running focused unit/module tests or diagnostic simulations to confirm or refute a suspected defect is standard maintainer practice. Writes are limited to generated build, test-result, simulation-result, and diagnostic artifacts.

Read [finding-quality.md](references/finding-quality.md) for the finding threshold and comment format. Read [common-agent-pitfalls.md](references/common-agent-pitfalls.md) for recurring false-positive and missed-finding patterns. If the review format or evidence threshold is unfamiliar, optionally consult the [Block Ack example](references/example-review.md) or the [non-WLAN lifecycle example](references/example-review-lifecycle.md); do not load either example by default.

## Select the review layers

Apply the following layers cumulatively. Select them by the changed runtime contract, not only by file extension: a C++ change may require all four layers, while a NED-only change may require OMNeT++, INET, and IEEE 802.11 checks.

| Layer | Apply when the reviewed contract involves | Detailed checks |
| --- | --- | --- |
| General C++ | C++ APIs, object lifetime, containers, algorithms, callbacks, state, or polymorphism | [general-cpp-review-checks.md](references/general-cpp-review-checks.md) |
| OMNeT++ | modules, initialization stages, events, messages, signals, NED, INI, MSG, statistics, or simulation trajectories | [omnetpp-review-checks.md](references/omnetpp-review-checks.md) |
| INET | INET packets/chunks/tags, protocol integration, lifecycle operations, queues, serializers, feature composition, or INET tests | [inet-review-checks.md](references/inet-review-checks.md) |
| IEEE 802.11 | Wi-Fi MAC/PHY behavior, management, association, channel access, Block Ack, capabilities, rates/modes, or 802.11 configuration | [ieee80211-review-checks.md](references/ieee80211-review-checks.md) |

Read every selected layer reference before evaluating the change. Keep findings at the layer that owns the violated contract, but use lower layers to prove the mechanism.

### Context budget tiers

To prevent context exhaustion, scale reference loading by diff size and complexity:

- **Small Diff (< 100 lines, focused single subsystem):**
  1. `finding-quality.md` + `common-agent-pitfalls.md`
  2. The single primary layer reference (e.g. `inet-review-checks.md` or `omnetpp-review-checks.md`)
  3. Load secondary layers only if cross-layer mechanisms (e.g. signal -> memory leak) appear.
- **Medium Diff (100–500 lines, multi-file feature or fix):**
  1. `finding-quality.md` + `common-agent-pitfalls.md`
  2. All directly relevant layer references
  3. Quick-reference index from `inet-architectural-requirements`
- **Large / Cross-Cutting Diff (> 500 lines or subsystem overhaul):**
  1. `finding-quality.md` + `common-agent-pitfalls.md`
  2. Load layer references on demand per hunk/module group
  3. Run `check-architecture.sh` and `check-sealing.sh` before detailed semantic inspection.

## Reviewing Specialized Change Types

### Test-Only and Benchmark Changes
- Verify that tests reach the production owner and integration boundary rather than testing a private helper in isolation.
- Check that tests clean up dynamically allocated simulation objects (`Packet`, `cMessage`) to avoid false-positive leak reports.
- Do not flag missing production features as test defects; evaluate whether the test accurately exercises the claimed behavioral contract.

### Configuration-Only (INI / NED) Changes
- Trace parameter inheritance and wildcard precedence (`**.param = ...` vs `node.param = ...`).
- Verify physical unit correctness (e.g. `s`, `ms`, `bps`, `mW`, `dBm`) against the underlying NED module parameter definitions.
- Check that default values and type declarations in NED match C++ accessor expectations (`par("...").doubleValue()` vs `.intValue()`).

## Establish the review target

Resolve the user-specified base, head, commit range, PR diff, or working-tree scope. If the request does not name one, infer the narrowest reviewable range from repository state and state that scope:
- Working tree vs. HEAD: `git diff HEAD`
- Staged changes only: `git diff --cached`
- Topic branch vs. base branch: `git diff <base-branch>...HEAD`
- Specific commit: `git show <commit-hash>`

Verify the range against current `HEAD`; do not review a stale line range or an assumed PR description.

Treat a supplied pre-write contract, behavior claim, or implementation report as evidence and a hypothesis to test, not as authority. The actual user requirements, checked-out source and effective configuration, runtime evidence, and applicable standards and project contracts govern the review. When an incorrect authoring contract led to incorrect code, report the actionable code defect and identify the contract correction and earliest pipeline gate that must be re-entered. When the code is correct but the contract or handoff describes it incorrectly, report a handoff discrepancy outside the findings list; do not manufacture a code finding.

Inventory changed files and assign the applicable review layers. Classify each change by contract: API, lifecycle, protocol state, packet representation, configuration, serialization, timing, observability, build integration, or test behavior. Note generated inputs and feature gates before inspecting individual hunks.

Do not broaden into a repository-wide audit. Review pre-existing code only where the change calls it, depends on it, changes its contract, or makes an old defect newly material.

## Trace the changed contract

For every semantic change, use the selected layer checks to inspect beyond the diff. Trace declarations and consumers, the owner of each invariant, semantic siblings, failure and terminal paths, generated inputs and consumers, effective configuration, and what existing tests actually prove.

Follow the effective runtime path. A helper that looks correct does not establish that the production owner calls it, passes the right identity, or handles every terminal result.

## Hunt for failures

Challenge the change with the boundary, alternate, failure, re-entrant, lifecycle, configuration, and variant paths named by each selected layer. Look especially for a change applied to one semantic path but omitted from its siblings, duplicated authority, partial state transitions, and tests that exercise a helper while bypassing production integration.

## Prove findings

Before reporting a defect, establish:

1. the invariant and its owner;
2. a reachable trigger in the reviewed scope;
3. the exact failure mechanism;
4. the user-visible, protocol, ownership, or trajectory consequence;
5. source plus runtime, configuration, standard, capture, result, or focused-test evidence appropriate to the claim;
6. the smallest credible correction and regression check.

Trace actual initialization order before claiming an invalid sentinel can escape. Trace the concrete ownership operation before calling retention a leak or a borrowed pointer a use-after-free. Verify normative claims against the applicable standard revision and clause. Distinguish an intentional change, optional hardening, unsupported future configuration, and unrelated pre-existing issue from a defect in the reviewed change.

Precision outranks finding count. Do not file speculative findings whose reachability or consequence is unproven. Classify items strictly:
- **Actionable finding (`FLAG`)**: proven defect with reachable trigger, broken invariant, and observable consequence.
- **Maintainer question (`QUESTION`)**: used sparingly only when a concrete standard or behavioral ambiguity genuinely requires maintainer clarification, not for unverified hunches.

## Validate proportionally

Use read-only inspection first. When execution materially strengthens a finding or clears a realistic risk, rebuild matching debug artifacts and run only directly mapped checks with explicit filters. Choose the smallest layer-appropriate unit, module, simulation, packet, or fingerprint check described in the selected references. Start runtime validation with one configuration and one run/seed.

Do not substitute a broad suite for missing direct coverage. A missing required companion test is not a standalone correctness finding: when architecture review applies, report it only in the checklist under `AR-QUAL-TESTS`; otherwise report it as residual risk. Do not change fingerprint CSVs. Treat a passing fingerprint as regression evidence, not proof of protocol correctness; explain the first divergence before attributing a mismatch to the change.

## Report as a reviewer

Put actionable findings first, ordered by severity. For each finding provide:

- severity and concise title;
- exact `file:line`;
- reachable trigger and violated invariant;
- failure mechanism and consequence;
- smallest correction direction and focused verification.

Write each finding so the author can understand and reproduce it without reading the rest of the review. Do not bury defects inside a general summary or checklist.

After findings, report reviewed scope, validation performed, and residual risks or untested paths. Put formal architecture/WLAN checklist output last (with `N/A` used for genuinely inapplicable rules). If no actionable findings remain, say so directly; do not invent low-value comments to avoid an empty review.
