---
name: inet-code-authoring
description: Design and implement semantic INET C++, NED, MSG, INI, and test changes with preventive correctness checks before writing and a focused self-audit afterward. Use for production fixes, features, and refactors; use inet-code-review for independent diff review.
---

# INET code authoring

Prevent defects while defining and implementing a change. Keep `inet-code-review` independent and read-only; reuse its maintained correctness references without adopting its finding format or reviewer role.

## Implementation Workflow Sequence

Follow this 4-step sequence in order for any change under `src/inet/`:

```mermaid
graph LR
    Step1[1. Sealing & Arch Guard] --> Step2[2. Pre-Write Contract]
    Step2 --> Step3[3. Implement against Contract]
    Step3 --> Step4[4. Self-Audit & Focused Test]
```

1. **Sealing Guard:** Run `check-sealing.sh` to confirm target files are unsealed. If sealed, STOP and request explicit permission.
2. **Implementation Contract:** Define the pre-write contract (full or lightweight template) before modifying files.
3. **Implementation:** Code against the contract adhering to modern INET conventions.
4. **Self-Audit & Verification:** Audit stable diff against `common-agent-pitfalls.md` and run directly mapped debug-mode tests.

## Load the preventive checks

Read [common-agent-pitfalls.md](../inet-code-review/references/common-agent-pitfalls.md) for every semantic production change. Select additional layers by the changed runtime contract, not only by file extension, and read every selected reference before editing:

| Layer | Select when the change involves | Preventive checks |
| --- | --- | --- |
| General C++ | APIs, ownership, lifetime, containers, algorithms, callbacks, state, or polymorphism | [general-cpp-review-checks.md](../inet-code-review/references/general-cpp-review-checks.md) |
| OMNeT++ | modules, initialization, events, messages, signals, NED, INI, MSG, statistics, or simulation trajectories | [omnetpp-review-checks.md](../inet-code-review/references/omnetpp-review-checks.md) |
| INET | packets, chunks, tags, protocol integration, lifecycle operations, queues, serializers, feature composition, or INET tests | [inet-review-checks.md](../inet-code-review/references/inet-review-checks.md) |
| IEEE 802.11 | Wi-Fi MAC/PHY behavior, management, association, channel access, Block Ack, capabilities, rates, modes, or configuration | [ieee80211-review-checks.md](../inet-code-review/references/ieee80211-review-checks.md) |

Apply layers cumulatively when a higher-layer behavior relies on lower-layer contracts. For normative IEEE 802.11 behavior, also use `ieee80211-standards` and identify the applicable revision and clause before choosing the implementation.

## Define the implementation contract

Before editing, write a compact working contract or return it in the parent handoff. Study [example-contract.md](references/example-contract.md) for complete worked examples of both full and lightweight contracts.

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

### Lightweight Contract Template (Trivial / Bounded Fixes Only)

Use this fast-track template only when the change meets the trivial-change criteria (single file, <= 5 lines, no state-machine/API/lifecycle changes):

```text
### Lightweight Pre-Write Contract
- Target: <file:line>
- Bug / Invariant: <one-line bug description and preserved invariant>
- Change: <exact minimal change to apply>
- Affected Siblings: <confirmation that sibling paths are clean or unshared>
- Direct Verification: <smallest test or build check command>
```

Resolve uncertainty about the mechanism or effective configuration before writing. Do not turn unsupported hypotheses, optional hardening, or unrelated pre-existing issues into patch scope.

## Implement against the contract

- **Modern INET conventions**: use `Packet`, `Chunk`, and `Tag` APIs instead of deprecated `cMessage` encapsulation; use `IntrusivePtr`/`SharedPtr` (`makeShared`) for chunk/packet memory instead of raw owning pointers; route lifecycle states through `handleLifecycleOperation` (`ILifecycle`) ensuring clean cancellation of timers and reset on `LF_STOP`/`LF_CRASH` and restoration on `LF_START`.
- **Simulation determinism**: use OMNeT++ RNG infrastructure (`getRNG(k)`, `cRNG`) and `simTime()`; never iterate over pointer-keyed unordered containers (`std::unordered_map<T*, ...>`) when order affects simulation events or protocol state.
- **Multi-stage initialization**: when implementing `initialize(int stage)`, always override `numInitStages() const` returning `std::max(stage + 1, Base::numInitStages())` to prevent higher stages from being silently skipped.
- Make the smallest coherent change that updates every affected semantic path and consumer.
- Preserve exactly one owner and disposition across normal, early-return, failure, exception, callback, and teardown paths. Establish externally observable state before re-entrant callbacks or signals, and make shared terminal cleanup idempotent when paths can converge.
- Keep current and pending state, peers, interfaces, flows, TIDs, directions, links, and generations separate according to the owning protocol. Use complete identity tuples and domain-correct boundary or wrap semantics.
- Keep absolute deadlines distinct from relative durations and preserve units and conversion ownership across NED, C++, model fields, serializers, and wire encodings.
- Change generated-code inputs rather than generated outputs, and keep C++, NED, MSG, configuration, registration, serialization, feature, documentation, and test artifacts consistent where the contract requires them.
- Make tests reach the production owner and integration boundary; helper-only coverage does not prove the real caller supplies the right identity or handles every terminal result.

## Self-audit and hand off

Once the diff is stable, inspect it against the implementation contract, `common-agent-pitfalls.md`, and every selected layer reference. Trace the effective runtime path again, confirm all identified siblings and terminal paths, and verify that each required consumer and artifact changed consistently.

Use the owning build, test, simulation, packet, result, and fingerprint skills. Follow `AGENTS.md`: use debug mode and explicit filters, run only directly mapped checks, report a coverage gap instead of broadening the suite, and never update fingerprints without explicit user approval.

Return the behavior claim, changed paths, selected layers and high-risk paths checked, focused verification evidence, and residual risks. This self-audit improves the implementation but does not replace an independent `inet-reviewer` when orchestration routes the stable diff to review.
