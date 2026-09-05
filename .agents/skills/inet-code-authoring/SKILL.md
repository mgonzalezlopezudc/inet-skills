---
name: inet-code-authoring
description: Design and implement semantic INET C++, NED, MSG, INI, and test changes with preventive correctness checks before writing and a focused self-audit afterward. Use for production fixes, features, and refactors; use inet-code-review for independent diff review.
---

# INET code authoring

Prevent defects while defining and implementing a change. Keep `inet-code-review` independent and read-only; reuse its maintained correctness references without adopting its finding format or reviewer role.

Follow `doc/project/guide/contribute-a-change.md` and its canonical seals, rules, gates, and test
policy. This skill adds a pre-write correctness contract and a post-write self-audit; it does not
repeat project policy.

Use the changed-contract inventory in `doc/project/guide/review-a-code-change.md` as a preventive
self-audit aid, without adopting reviewer verdicts, finding severity, or report formatting.

For a wide behavior-preserving transformation, use
[mechanical-migrations.md](references/mechanical-migrations.md).

The preventive references are maintained by `inet-code-review`; this skill depends on that skill's
reference package but does not adopt its independent-review role or finding format.

Select layers by the changed runtime contract, not only by file extension:

| Layer | Select when the change involves | Preventive checks |
| --- | --- | --- |
| C++ | APIs, ownership, callbacks, containers, numeric boundaries, or state | [general-cpp-review-checks.md](../inet-code-review/references/general-cpp-review-checks.md) |
| OMNeT++ | modules, initialization, events, messages, signals, NED, INI, MSG, statistics, or simulation trajectories | [omnetpp-review-checks.md](../inet-code-review/references/omnetpp-review-checks.md) |
| INET | packets, chunks, tags, protocol integration, lifecycle operations, queues, serializers, feature composition, or INET tests | [inet-review-checks.md](../inet-code-review/references/inet-review-checks.md) |
| IEEE 802.11 | Wi-Fi MAC/PHY behavior, management, association, channel access, Block Ack, capabilities, rates, modes, or configuration | [ieee80211-review-checks.md](../inet-code-review/references/ieee80211-review-checks.md) |

Read the selected reference sections before completing the implementation contract, then revisit
them during the self-audit. The C++ checklist supplies explicit failure-path probes for implementers;
use domain references for the actual INET and protocol contracts.

The `RP-*` labels in these references identify non-normative investigation prompts, not new
authoring requirements. Use them to name preventive checks when useful; take every implementation
obligation from the applicable canonical project rule.

Apply layers cumulatively only when a higher-layer behavior actually relies on lower-layer
contracts in the changed control path. For normative IEEE 802.11 behavior, also use
`ieee80211-standards` and identify the applicable revision and clause before choosing the
implementation.

## Define the implementation contract

Before editing, write a compact working contract or return it in the parent handoff. Use the templates below directly; do not load a worked example unless the contract fields are genuinely unclear.

### Full Contract Template (Default for Semantic Changes)

```text
### Pre-Write Implementation Contract Template
- Invariant & Owner: <intended behavior, preserved invariants, owning class/module>
- Entry Point & Control Path: <effective production caller, entry point, data flow>
- Affected Consumers & Artifacts: <C++, NED, MSG, serializers, registrations, gates>
- Siblings & Terminal Paths: <error, timeout, cancellation, lifecycle STOP/START, retry>
- Boundaries & Units: <identities/TIDs, absolute vs relative time, units, wrap arithmetic>
- Mapped Verification: <smallest direct unit/module/fingerprint test command>
```

### Lightweight Contract Template (Localized Changes Only)

Use this template only for a trivial bounded, behavior-preserving change with an understood owner
and no externally observable effect. Any change to a computation, algorithm, ownership, API,
serialization, timing, state machine, lifecycle, protocol decision, configuration, generated-input
meaning, or observability requires the full semantic contract. Diff size alone cannot qualify a
change.

```text
### Lightweight Pre-Write Contract
- Target: <file:line>
- Bug / Invariant: <one-line bug description and preserved invariant>
- Change: <exact minimal change to apply>
- Affected Siblings: <confirmation that sibling paths are clean or unshared>
- Direct Verification: <smallest test or build check command>
```

For a wide mechanical change, use the contract and checks in `mechanical-migrations.md`. The full
semantic template remains mandatory for behavioral API migrations, renames that change dispatch or
registration, and generated-input changes that alter runtime meaning.

### Validate the contract before the first write

Do not start implementation until the contract passes all of these checks:

- Every field contains source- or configuration-backed facts, or a reasoned `N/A`; no `TBD`, placeholder, or unsupported assertion remains.
- The named owner and effective entry/control path were checked in the current tree, and every presently known affected production, generated-input, configuration, registration, documentation, and test path is listed.
- Every named verification command and explicit filter exists, and any command offered as behavioral evidence reaches the claimed behavior. If no direct check exists, record the precise coverage gap and do not represent a build or neighboring test as behavioral proof.
- The contract is internally consistent: its invariant, change surface, siblings, boundary semantics, and verification all describe the same behavior claim.

In single-agent mode, self-validate and record the result before writing. In delegated work, the implementer self-validates before handoff and the parent or orchestrator validates the handoff before authorizing the first write. If a field cannot yet pass, return to discovery instead of weakening the field.

When a filled-in field remains unclear, read the optional [verified non-WLAN contract example](references/example-contract.md). Recheck its paths and facts against the active checkout before adapting it.

## Implement against the contract

- Apply the packet, lifecycle, determinism, artifact, and testing rules selected from `doc/project/`.
  For the called packet API, establish its concrete `Packet *` ownership transfer and its
  `take`/`drop`/`send`/delete contract; use `Ptr`/`makeShared` only where the checked API requires it.
- For multi-stage initialization, apply
  `doc/project/rule/architecture.md#ar-life-stages`. As the preventive trace, identify the highest
  named stage handled by the class and compare it with the effective inherited `numInitStages()`;
  add or update a local override only when that effective count does not cover the stage.
- Keep current and pending state, peers, interfaces, flows, TIDs, directions, links, and generations separate according to the owning protocol. Use complete identity tuples and domain-correct boundary or wrap semantics.
- Keep absolute deadlines distinct from relative durations and preserve units and conversion ownership across NED, C++, model fields, serializers, and wire encodings.
- Select and report tests under `doc/project/rule/testing.md#tr-focused-evidence`. Apply the
  production-path distinction in `doc/project/design/test-anatomy.md`: helper-only coverage does not
  prove that the real caller invokes the helper, supplies the intended identity, or handles every
  terminal result.

### Handle related scope expansion

When implementation reveals a related target or behavior not covered by the validated contract, pause before modifying that new target. Preserve the current work; do not reset it merely to revisit the contract.

1. Classify the discovery as **required** for the behavior claim or **optional** hardening/follow-up. Keep optional work out of the patch.
2. Add required owners, paths, consumers, sibling/terminal behavior, and any contract deviation to the working contract.
3. Rerun sealing and applicable architecture checks for every newly added target, then remap the smallest direct verification and explicit filters.
4. If the expansion materially exceeds the requested scope, existing authority, or delegated ownership, return the updated contract to the user, parent, or orchestrator before continuing. Otherwise revalidate it and resume.

## Self-audit and hand off

Once the diff is stable, complete this checklist against the implementation contract and every
selected domain reference:

- [ ] Stable diff matches the validated behavior claim; every deviation and required scope expansion is recorded.
- [ ] Effective owner/control path, affected consumers, siblings, and terminal paths were retraced in the resulting tree.
- [ ] The applicable canonical project rules and selected preventive references are each checked or
      recorded as reasoned `N/A`.
- [ ] Focused commands reach the production behavior and have recorded exit status and artifacts;
      gaps and approval needs are explicit.

Use the owning build, test, simulation, packet, result, and fingerprint skills. Obtain project test
and baseline policy from `doc/project/rule/testing.md` and
`doc/project/guide/change-a-baseline.md`; apply the additional execution constraints in `AGENTS.md`.

Return this plain-text envelope. Use `None` only when supported by the audit; do not omit fields.

```text
### Implementation Report
- Behavior claim: <what the resulting tree now guarantees>
- Changed paths: <complete path list>
- Contract deviations / scope changes: <none, or old -> new scope and authorization>
- Selected layers / high-risk checks: <references and applicable checks completed>
- Focused evidence:
  - Command: <exact command>
  - Working directory: <path>
  - Mode / filter: <debug mode and explicit filter>
  - Exit status: <status>
  - Artifacts: <paths or none>
- Residual risks / coverage gaps: <remaining uncertainty, unrun checks, or none>
```

This self-audit improves the implementation but does not replace an independent `inet-reviewer` when orchestration routes the stable diff to review.
