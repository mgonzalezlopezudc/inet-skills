---
name: inet-agent-orchestration
description: Route and coordinate project-scoped specialist agents across Codex, Antigravity, and Kimi for nontrivial OMNeT++/INET and IEEE 802.11 work. Use for multi-stage debugging, standards-to-implementation analysis, C++/NED/MSG changes, Wi-Fi packet or PHY/MAC investigations, regression design, result analysis, patch review, or any task with multiple independent evidence lanes or specialist handoffs.
---

# INET agent orchestration

Keep requirements, decisions, and synthesis in the root thread. Delegate bounded evidence or execution outcomes when independent lanes reduce risk or latency.

For production changes and pull-request reviews, obtain project policy and gate order from
`doc/project/guide/contribute-a-change.md` or `doc/project/guide/review-a-pull-request.md`. This
skill adds agent routing, ownership, and handoff mechanics only.

## Architecture and Workflow Pipeline

```mermaid
graph TD
    Root[Root Thread / Orchestrator] -->|1. Seal & Target| ArchGuard[inet-architectural-requirements]
    ArchGuard -->|Sealed: Request Approval / Unsealed: OK| Contract[inet-code-authoring: Pre-Write Contract]
    Contract -->|Returned & Validated by Orchestrator| Implement[Single Implementer: Write Code]
    Implement -->|Stable Diff| Test[Focused Verification: Unit / Module / Debug Run]
    Test -->|Evidence Gathered| Review[inet-code-review + Checklist Verdicts]
    Review -->|Findings Resolved & Approved| Conclude[Conclude / Persist]
```

## Constraints

- Keep depth at one; specialists must not delegate.
- Use at most one production-code writer.
- Do not duplicate assignments or delegate work simpler than the handoff.
- Do not let extraction-only agents infer causality, normative meaning, or correctness.
- Stop opening lanes once decisive evidence exists.

Use a soft evidence budget rather than a fixed invocation or token limit. Start with the smallest lane set that can answer the current unresolved questions. Run a lane only when its prompt states both the unresolved question and the evidence expected to resolve it. Parallelize lanes that are already required and independent; run contingent lanes sequentially after reviewing the evidence that determines whether they are needed. Before adding a lane, reuse a suitable active specialist or explain why the existing evidence cannot close the question.

## Tiers and agents

| Tier | Appropriate work | Specialist agent |
| --- | --- | --- |
| Chimp 🐒 | Ambiguous standards/MAC/PHY reasoning, difficult runtime causality, final review | `inet-wifi-specialist`, `inet-simulation-detective`, `inet-reviewer` |
| Dog 🐕 | Cross-file architecture and NED/INI tracing | `inet-navigator` |
| Fish 🐟 | Production implementation, established regression and result-analysis workflows | `inet-implementer`, `inet-regression-guard`, `inet-results-analyst` |
| Ant 🐜 | Explicit searches, inventories, filtering, and structured extraction | `inet-evidence-miner` |

For active tier assignments, consult [MODELS.md](../../../MODELS.md). For platform-specific runner configurations across Codex, Antigravity, and Kimi, see [platform-bindings.md](references/platform-bindings.md).

## Routing

- **Architecture/configuration:** use `inet-navigator`; add `inet-reviewer` for a formal compliance verdict and `inet-wifi-specialist` only when 802.11 semantics matter.
- **Standards/model gap:** use `inet-wifi-specialist`; add `inet-navigator` when the implementation path is broad or unclear.
- **Runtime failure:** lead with `inet-simulation-detective`; add configuration, Wi-Fi, or extraction lanes only for distinct questions.
- **Patch review:** use `inet-reviewer`, which must use `inet-code-review` for every pull request, branch, commit-range, diff, or working-tree review. It additionally uses `inet-architectural-requirements` for `src/inet/` scope. For a formal architecture, naming, or sealing audit without a concrete correctness diff, use the architecture skill as primary and add code review only if correctness review is also requested.
- **Production change:** establish the mechanism and change surface, then assign exactly one `inet-implementer`. For a semantic `src/inet/` change, first assign the implementer read-only contract completion using `inet-code-authoring`; require it to return the completed, self-validated contract without writing. Validate that handoff against the authoring checklist, then explicitly authorize the same implementer to write. Use `inet-regression-guard` for behavior changes and `inet-reviewer` on the stable verified diff for architecture-sensitive, nontrivial, or 802.11 changes.
- **Results/plots:** use `inet-results-analyst`; use `inet-evidence-miner` only for bounded metadata inventory.

### Trivial change fast-track
For mechanically obvious changes meeting all of the following:
1. Total diff <= 5 lines in a single file;
2. No behavioral contract, protocol state machine, or API signature modified;
3. No sibling dispatch branches or lifecycle interactions affected;
4. Path is unsealed under `doc/project/audit/seal-list.md` (the source-path helper in
   `inet-architectural-requirements` may resolve it);

the orchestrator or implementer may skip formal multi-agent routing and use the lightweight contract flow in `inet-code-authoring`.

In a single-agent session, follow the canonical contribution workflow in the root thread and add
the pre-write contract and self-audit from `inet-code-authoring`.

## Assignments and gates

Every delegated prompt must say to follow `AGENTS.md` and the applicable repository skills, not spawn sub-agents, and return to the parent. Specify one deliverable, exact scope and inputs, write authority, exclusions, required evidence, definition of done, and concise return shape. Include paths, symbols, configuration, run/seed, and artifacts when relevant. For semantic `src/inet/` implementation, do not combine unresolved contract completion and write authority in one assignment. First provide the available `inet-code-authoring` evidence in a read-only contract assignment; after the implementer returns a complete self-validation, the orchestrator validates it and sends a separate follow-up that authorizes the first write. Reuse that implementer for the authorized implementation and related follow-up work.

Gate handoffs as follows:

1. Diagnose → contract: demonstrated mechanism, bounded change surface, architecture/seal decision, any required approval, and the available evidence for every applicable `inet-code-authoring` contract field.
2. Contract → implement: the implementer has returned every field complete and self-validated; the orchestrator has independently checked the authoring validation checklist, recorded the result, and explicitly authorized the first write. An unresolved field returns to diagnosis.
3. Implement → verify: stable diff and explicit behavior claim.
4. Verify → review or conclude: evidence selected under `doc/project/rule/testing.md` and the
   execution constraints in `AGENTS.md`. When review is required, pass the stable diff, behavior
   claim, contract, implementation report, and evidence to the reviewer.
5. Correctness review → conclude: for changes routed to `inet-reviewer`, all actionable `inet-code-review` findings are confirmed resolved by the same reviewer after focused reverification, or explicitly accepted by the user with the residual risk recorded. Report reviewed scope, validation, and residual risks.
6. Architecture review → conclude: required fitness checks and the exact semantic verdict format from
   the applicable canonical checklist.
7. Baseline or sealing change: the procedure and authorization required by `doc/project/` plus any
   additional approval required by `AGENTS.md`.

Gates may move backward when new evidence invalidates an earlier assumption. Preserve the working diff and artifacts while returning to the earliest affected gate; do not use destructive Git reset as recovery. For a build or focused-test failure, remain in verification when an identified runner or artifact problem caused it, return to implementation when the contract remains valid and the diff caused it, or return to diagnosis/contract definition when it exposes a wrong mechanism, owner, change surface, invariant, or verification mapping. Freeze further writes when evidence invalidates the mechanism or contract, revise and revalidate the affected handoff, then resume forward progress. Reverify every downstream claim made stale by the correction.

When context pressure threatens a safe handoff, checkpoint before continuing or transferring ownership. Record the current gate; verified facts and their evidence; working-diff and artifact state; approvals already obtained; invalidated evidence; unresolved questions; and the exact next action or command. Context pressure may reduce optional commentary or defer contingent lanes, but it never waives sealing, contract, focused-verification, approval, or required-review gates.

## Dispute Escalation and Deadlock Resolution

When specialists disagree or findings conflict:

1. **Implementation causality:** For claims about what the checked-out model currently does, prefer `reproducible runtime/debugger evidence > packet captures/event logs/results > effective INI/NED > checked-out source > agent hypothesis`.
2. **Normative authority:** For claims about required IEEE 802.11 behavior, the applicable standard revision and clause are authoritative. Runtime and source evidence establish whether INET implements that requirement; they cannot override it.
3. **Intentional divergence:** Verify an apparent standards divergence against explicit model documentation, a recorded model limitation, or a user-approved design decision. Architecture and naming exception ledgers govern project structure and naming; do not use them as a standards-deviation ledger.
4. **Escalation Protocol:**
   - Define a minimal reproduction (1 node/pair, 1 seed, shortest time) that isolates the contested behavior.
   - Run in debug mode (`MODE=debug`, `opp_run_dbg`) with targeted tracing.
   - A concrete trace or assertion can resolve implementation causality. Resolve normative ambiguity from the applicable standard text; if the intended model behavior remains ambiguous, record a `QUESTION` for user decision rather than guessing.
