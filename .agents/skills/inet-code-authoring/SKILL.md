---
name: inet-code-authoring
description: Implement INET C++, NED, MSG, INI, and test changes after design checks. Check the result against the design after each change. Use for production fixes, features, and refactors. Use inet-code-review for independent diff review.
---

# INET code authoring

Prevent defects before and during implementation.
Keep `inet-code-review` independent and read-only.
Reuse its correctness references.
Do not adopt its finding format or reviewer role.

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to find the active checkout's contribution, protection, rule, gate, and test guidance.
Read that guidance before its application.
This skill adds a
pre-write correctness contract and a post-write self-audit; it does not repeat project policy.

For a requested implementation plan, use `inet-project-guidance` to follow the current plan route before implementation.
The working contract below does not replace a plan or grant approval.

If the project entry point provides a changed-contract inventory, use it as a preventive self-audit
aid.
Do not adopt reviewer verdicts, finding severity, or report formats.

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

Read the selected reference sections before you complete the implementation contract.
Revisit those sections during the self-audit.
The C++ checklist supplies explicit failure-path probes for implementers.
Use domain references for the actual INET and protocol contracts.

The `RP-*` labels in these references identify non-normative investigation prompts, not new
authoring requirements. Use them to name preventive checks when useful; take every implementation
obligation from the applicable canonical project rule.

Apply layers cumulatively only when a higher-layer behavior actually relies on lower-layer
contracts in the changed control path. For normative IEEE 802.11 behavior, also use
`ieee80211-standards`.
Identify the applicable revision and clause before the implementation decision.

Find the current quality guidance for minimal design through the project map. Apply it before you add state, stronger invariants, or defensive branches. Use its guidance on state lifetime before you choose additional state. Check event effects before you defer work or repeat a calculation. Trace the actual failure path before you select a preventive check. A checklist example does not establish that the failure can occur in this implementation.

## Define the implementation contract

Before an edit, explain the requirement, responsible owner, affected path, proposed change, and verification.
Reuse an existing plan or handoff when it already contains that information and matches the current code.
Use the templates below only where they help explain the change and its risks.
Load a worked example only when the contract fields remain unclear.

### Full contract template

Use this template when multiple owners, event boundaries, or interacting contracts need separate explanation.

```text
### Pre-Write Implementation Contract Template
- Invariant & Owner: <intended behavior, preserved invariants, owning class/module>
- Entry Point & Control Path: <effective production caller, entry point, data flow>
- Affected Consumers & Artifacts: <C++, NED, MSG, serializers, registrations, gates>
- Siblings & Terminal Paths: <error, timeout, cancellation, lifecycle STOP/START, retry>
- Boundaries & Units: <identities/TIDs, absolute vs relative time, units, wrap arithmetic>
- Mapped Verification: <smallest direct unit/module/fingerprint test command>
```

### Lightweight contract template

Use this template for a local change with a clear owner, understood callers, and focused verification. A behavior change can qualify when these fields explain its requirements and affected paths. Add relevant boundary or lifecycle details when necessary. Use the full template if the compact form hides an important interaction. Diff size alone does not determine the choice.

```text
### Lightweight Pre-Write Contract
- Target: <file:line>
- Bug / Invariant: <one-line bug description and preserved invariant>
- Change: <exact minimal change to apply>
- Affected Siblings: <confirmation that sibling paths are clean or unshared>
- Direct Verification: <smallest test or build check command>
```

For a wide mechanical change, use the contract and checks in `mechanical-migrations.md`. For changes to API behavior, dispatch, registration, or generated semantics, explain the affected runtime contracts. Choose the amount of detail from those interactions, not the file type or edit category.

### Validate the contract before the first write

Do not start implementation until the contract passes all of these checks:

- Claims about current behavior have source or configuration evidence. Proposed changes and tests are clearly identified. No unresolved assumption controls the implementation decision.
- The owner and effective entry/control path match the current tree.
  The contract lists every known affected production, generated-input, configuration, registration, documentation, and test path.
- Commands and filters for existing checks resolve to the intended tests.
  Label new tests and their commands as proposed until they exist.
  For a proposed test, name its trigger, production path, and expected result.
  Verify its command and selection after implementation, before you report execution evidence.
  If no direct check exists or is proposed, record the precise coverage gap.
  Do not present a build or nearby test as behavioral proof.
- The contract is internally consistent: its invariant, change surface, siblings, boundary semantics, and verification all describe the same behavior claim.

In single-agent mode, validate the contract before the first edit.
Record that result.
In delegated work, the implementer checks the assignment's contract against the current tree before the first edit.
Use a separate contract handoff when unresolved design facts prevent an implementation assignment.
The parent validates that result before it grants write authority.
An initial assignment with a validated contract and explicit write authority needs no second approval turn.
Resolve any missing fact that affects the implementation decision before the dependent edit.
An explicitly proposed test does not need to exist before implementation starts.

When a completed field remains unclear, read the optional [verified non-WLAN contract example](references/example-contract.md).
Recheck its paths and facts against the active checkout before reuse.

## Implement against the contract

- Apply the packet, lifecycle, determinism, artifact, and testing guidance discovered in the active
  checkout.
  For the called packet API, establish its concrete `Packet *` ownership transfer and its
  `take`/`drop`/`send`/delete contract; use `Ptr`/`makeShared` only where the checked API requires it.
- For multi-stage initialization, use the active lifecycle guidance. As the preventive trace,
  identify the highest named stage handled by the class and compare it with the effective inherited
  `numInitStages()`;
  add or update a local override only when that effective count does not cover the stage.
- Derive state distinctions and identity fields from the applicable protocol and supported callers. Add generations only when the traced completion or lifecycle path requires them. Use the protocol's boundary and wrap semantics.
- Keep absolute deadlines distinct from relative durations.
  Preserve units and conversion ownership across NED, C++, model fields, serializers, and wire encodings.
- Select and report tests under the active test guidance. Apply its production-path distinction:
  helper-only coverage does not
  prove that the real caller invokes the helper, supplies the intended identity, or handles every
  terminal result.

### Handle related scope expansion

When implementation reveals a related target or behavior outside the validated contract, pause before an edit to that new target.
Preserve the current work.
Do not reset it merely to revisit the contract.

1. Classify the discovery as **required** for the behavior claim or **optional** hardening/follow-up. Keep optional work out of the patch.
2. Add required owners, paths, consumers, sibling/terminal behavior, and any contract deviation to the working contract.
3. Rerun source-protection and applicable architecture checks for every new target.
   Remap the smallest direct verification and explicit filters.
4. Check whether the expansion materially exceeds the requested scope, existing authority, or delegated ownership.
   If it does, return the updated contract to the user, parent, or orchestrator before further work.
   Otherwise, revalidate the contract.
   Resume within that validated scope.

## Self-audit and hand off

Once the diff is stable, complete this checklist against the implementation contract and every
selected domain reference:

- [ ] Stable diff matches the validated behavior claim; every deviation and required scope expansion is recorded.
- [ ] Effective owner/control path, affected consumers, siblings, and terminal paths were retraced in the resulting tree.
- [ ] Applicable project rules and relevant preventive checks were assessed. Record exclusions only where their absence could mislead the reader.
- [ ] Focused commands reach the production behavior and have recorded exit status and artifacts;
      gaps and approval needs are explicit.

Use the owning build, test, simulation, packet, result, and fingerprint skills. Obtain project test
and baseline policy through the shared discovery procedure. Apply any additional execution
constraints discovered from the active checkout's repository instructions.

Use the report format required by the active project guidance. Otherwise, report the result, verification, and material gaps in proportion to the change. Reuse the design explanation instead of repeating it. The optional template below helps with a complex handoff; omit irrelevant fields.

```text
### Implementation Report
- Behavior claim: <what the resulting tree now guarantees>
- Changed paths: <complete path list>
- Contract deviations / scope changes: <none, or old -> new scope and authorization>
- Selected layers / high-risk checks: <references and applicable checks completed>
- Focused evidence:
  - Command: <exact command>
  - Working directory: <path>
  - Mode / filter: <discovered build mode and explicit filter>
  - Exit status: <status>
  - Artifacts: <paths or none>
- Residual risks / coverage gaps: <remaining uncertainty, unrun checks, or none>
```

This self-audit improves the implementation but does not replace an independent `inet-reviewer` when orchestration routes the stable diff to review.
