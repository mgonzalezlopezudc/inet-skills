---
name: inet-code-review
description: Act as an independent read-only OMNeT++/INET maintainer reviewing a pull request, branch, commit range, diff, or working tree for correctness and regressions. Use to discover and report actionable defects in C++, NED, MSG, INI, tests, and their integration; do not use merely to process existing reviewer comments or to implement fixes.
---

# INET code reviewer

Review the assigned change as an INET maintainer. Find defects independently; do not wait for the user to supply suspected problems. Remain read-only with respect to source, configuration, tests, fingerprints, ledgers, and seals.

Read [finding-quality.md](references/finding-quality.md) for the finding threshold and comment format. Read [omnetpp-inet-review-patterns.md](references/omnetpp-inet-review-patterns.md) for semantic failure patterns that ordinary line-by-line C++ review misses.

For any review under `src/inet/`, also use `inet-architectural-requirements` and emit its required checklist after correctness findings. Add subsystem skills when the review depends on effective NED/INI configuration, packet/tag semantics, IEEE 802.11 behavior, simulation causality, tests, or fingerprints.

## Establish the review target

Resolve the user-specified base, head, commit range, PR diff, or working-tree scope. If the request does not name one, infer the narrowest reviewable range from repository state and state that scope. Verify the range against current `HEAD`; do not review a stale line range or an assumed PR description.

Inventory changed files and classify each change by contract: API, lifecycle, protocol state, packet representation, configuration, serialization, timing, observability, build integration, or test behavior. Note generated inputs and feature gates before inspecting individual hunks.

Do not broaden into a repository-wide audit. Review pre-existing code only where the change calls it, depends on it, changes its contract, or makes an old defect newly material.

## Trace the changed contract

For every semantic change, inspect beyond the diff:

- declarations, callers, overrides, and sibling paths such as DCF/HCF, QoS/non-QoS, originator/recipient, AP/STA, and legacy/amendment variants;
- ownership and lifetime across queues, callbacks, signals, timers, returned packets, duplicates, and deferred cleanup;
- NED composition, INI inheritance, wildcard precedence, `typename`, parameters, gates, feature declarations, and custom configurations;
- `.msg` sources, serializers, printers, dissectors, generated consumers, field ranges, and round-trip behavior;
- existing unit, module, simulation, and fingerprint coverage, including what the assertions actually prove.

Follow the effective runtime path. A helper that looks correct does not establish that the production owner calls it, passes the right identity, or handles every terminal result.

## Hunt for failures

Challenge the change with boundary and alternate paths suggested by its contract:

- empty, singleton, full, overflow, wraparound, malformed, and unavailable state;
- initialization, stop/start, crash, dynamic deletion, and runtime reconfiguration;
- success, refusal, timeout, retry exhaustion, cancellation, stale/duplicate completion, and fragmentation;
- same peer, different peer, missing peer, sparse capability, and user-defined configuration;
- explicit override versus inferred default and every affected protocol/mode family;
- synchronous re-entry, observer callbacks, partial mutation, and exception cleanup.

Look especially for a change applied to one path but omitted from its semantic siblings, a new base interface without complete overrides, widened dispatch into unsupported subclasses, duplicated mutable state, or a test that exercises a helper while bypassing the production integration.

## Prove findings

Before reporting a defect, establish:

1. the invariant and its owner;
2. a reachable trigger in the reviewed scope;
3. the exact failure mechanism;
4. the user-visible, protocol, ownership, or trajectory consequence;
5. source plus runtime, configuration, standard, capture, result, or focused-test evidence appropriate to the claim;
6. the smallest credible correction and regression check.

Trace actual initialization order before claiming an invalid sentinel can escape. Trace the concrete ownership operation before calling retention a leak or a borrowed pointer a use-after-free. Verify normative claims against the applicable standard revision and clause. Distinguish an intentional change, optional hardening, unsupported future configuration, and unrelated pre-existing issue from a defect in the reviewed change.

Precision outranks finding count. Do not file speculative findings whose reachability or consequence is unproven. Use a question only when a concrete ambiguity requires maintainer judgment.

## Validate proportionally

Use read-only inspection first. When execution materially strengthens a finding or clears a realistic risk, rebuild matching debug artifacts and run only directly mapped checks with explicit filters:

- unit tests for pure algorithms, lookup, serialization, sequence arithmetic, and ownership boundaries;
- module tests for initialization, timers, callbacks, module calls, packet flow, and state-machine interleavings;
- one configuration/run/seed for runtime causality;
- directly related fingerprints only when the change may alter the event trajectory.

Do not substitute a broad suite for missing direct coverage. Do not change fingerprint CSVs. Treat a passing fingerprint as regression evidence, not proof of protocol correctness; explain the first divergence before attributing a mismatch to the change.

## Report as a reviewer

Put actionable findings first, ordered by severity. For each finding provide:

- severity and concise title;
- exact `file:line`;
- reachable trigger and violated invariant;
- failure mechanism and consequence;
- smallest correction direction and focused verification.

Write each finding so the author can understand and reproduce it without reading the rest of the review. Do not bury defects inside a general summary or checklist.

After findings, report reviewed scope, validation performed, and residual risks or untested paths. Put formal architecture/WLAN checklist output last. If no actionable findings remain, say so directly; do not invent low-value comments to avoid an empty review.
