---
name: inet-code-authoring
description: Design and implement semantic INET C++, NED, MSG, INI, and test changes with preventive correctness checks before writing and a focused self-audit afterward. Use for production fixes, features, and refactors; use inet-code-review for independent diff review.
---

# INET code authoring

Prevent defects while defining and implementing a change. Keep `inet-code-review` independent and read-only; reuse its maintained correctness references without adopting its finding format or reviewer role.

For any write under `src/inet/`, first use `inet-architectural-requirements` for sealing, applicable requirement identifiers, naming, ledgers, required artifacts, and architecture constraints. Do not write a sealed target without the file-specific approval that skill requires.

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

Before editing, write a compact working contract or return it in the parent handoff. Include:

1. the intended behavior change, preserved behavior, invariant, and authoritative owner;
2. the effective production entry point and control/data path that reaches the owner;
3. affected declarations, callers, implementations, C++/NED/MSG/configuration artifacts, generated inputs and consumers, serializers, registrations, and feature gates;
4. affected semantic siblings and every success, refusal, error, timeout, cancellation, retry-exhaustion, stale/duplicate, re-entrant, lifecycle, teardown, configuration, and supported-variant path;
5. relevant ownership transitions, identity and generation tuples, units, numeric or cyclic boundaries, timer meaning, and scheduling semantics;
6. the smallest unit, module, simulation, packet, or fingerprint checks that directly exercise the changed production contract.

Resolve uncertainty about the mechanism or effective configuration before writing. Do not turn unsupported hypotheses, optional hardening, or unrelated pre-existing issues into patch scope.

## Implement against the contract

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
