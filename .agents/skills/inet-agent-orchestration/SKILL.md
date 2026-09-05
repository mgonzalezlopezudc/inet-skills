---
name: inet-agent-orchestration
description: Coordinate project-scoped specialist agents across Codex, Antigravity, and Kimi when OMNeT++/INET work requires delegation, multiple independent evidence lanes, or formal specialist handoffs. Use for genuinely multi-lane diagnosis, standards-to-implementation analysis, delegated implementation and verification, or independent specialist review; do not use merely because a single-agent task is nontrivial.
---

# INET agent orchestration

Keep requirements, decisions, and synthesis in the root thread. Delegate bounded evidence or execution outcomes when independent lanes reduce risk or latency.

For production changes and pull-request reviews, obtain project policy and gate order from
`doc/project/guide/contribute-a-change.md` or `doc/project/guide/review-a-pull-request.md`. This
skill adds agent routing, ownership, and handoff mechanics only.

## Execution paths

Choose by change invariant and handoff need, not by raw line count.

1. **Localized path** — a trivial, bounded change with an understood owner and no delegation need.
   Keep it in one agent and use the lightweight contract in `inet-code-authoring`. Resolve seals and
   run the smallest direct check. Any API, state-machine, lifecycle, protocol, configuration, or
   generated-input behavior change is not localized, however small its diff.
2. **Mechanical path** — a repetitive, behavior-preserving transformation whose invariant can be
   stated before editing and independently checked afterward. It may span many files. Examples are
   a collision-free rename, a format-preserving migration, or regeneration from an unchanged
   semantic input. Use the mechanical-change reference in `inet-code-authoring`; inventory the full
   surface, check the invariant and generated artifacts, resolve seals, and run focused
   verification. If correctness depends on interpreting runtime behavior, use the semantic path.
3. **Semantic path** — a change to behavior, ownership, API contracts, state, protocol decisions,
   effective configuration, lifecycle, timing, or observability. Use the full contract pipeline
   below. Delegate only when independent evidence or a formal specialist handoff improves the task;
   otherwise run the same safety gates in the root thread.

The first two paths are classification rules, not permission shortcuts. Uncertainty about whether
behavior is preserved selects the semantic path.

## Semantic contract pipeline

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

## Specialist classes

| Class | Appropriate work | Specialist agent |
| --- | --- | --- |
| Reasoning | Ambiguous standards/MAC/PHY reasoning, difficult runtime causality, final review | `inet-wifi-specialist`, `inet-simulation-detective`, `inet-reviewer` |
| Navigation | Cross-file architecture and NED/INI tracing | `inet-navigator` |
| Implementation | Production implementation, established regression and result-analysis workflows | `inet-implementer`, `inet-regression-guard`, `inet-results-analyst` |
| Extraction | Explicit searches, inventories, filtering, and structured extraction | `inet-evidence-miner` |

Use the three Codex model tiers in [MODELS.md](../../../MODELS.md): reasoning first, navigation second, and implementation and extraction third. Select the tier by specialist class. For platform-specific runner configurations across Codex, Antigravity, and Kimi, see [platform-bindings.md](references/platform-bindings.md).

## Routing

- **Architecture/configuration:** use `inet-navigator`; add `inet-reviewer` for a formal compliance verdict and `inet-wifi-specialist` only when 802.11 semantics matter.
- **Standards/model gap:** use `inet-wifi-specialist`; add `inet-navigator` when the implementation path is broad or unclear.
- **Runtime failure:** lead with `inet-simulation-detective`; add configuration, Wi-Fi, or extraction lanes only for distinct questions.
- **Patch review:** use `inet-reviewer`, which must use `inet-code-review` for every pull request, branch, commit-range, diff, or working-tree review. It additionally uses `inet-architectural-requirements` for `src/inet/` scope. For a formal architecture, naming, or sealing audit without a concrete correctness diff, use the architecture skill as primary and add code review only if correctness review is also requested.
- **Production change:** establish the mechanism and change surface, then assign exactly one `inet-implementer`. For a semantic `src/inet/` change, first assign the implementer read-only contract completion using `inet-code-authoring`; require it to return the completed, self-validated contract without writing. Validate that handoff against the authoring checklist, then explicitly authorize the same implementer to write. Use `inet-regression-guard` for behavior changes and `inet-reviewer` on the stable verified diff for architecture-sensitive, nontrivial, or 802.11 changes.
- **Results/plots:** use `inet-results-analyst`; use `inet-evidence-miner` only for bounded metadata inventory.

For either single-agent path, follow the canonical contribution workflow in the root thread and use
the matching pre-write contract and self-audit from `inet-code-authoring`. Do not activate this
orchestration skill solely to classify or execute such a change.

## Assignments and gates

Every delegated prompt must say to follow `AGENTS.md` and the applicable repository skills, not spawn sub-agents, and return to the parent. Specify one deliverable, exact scope and inputs, write authority, exclusions, required evidence, definition of done, and concise return shape. Include paths, symbols, configuration, run/seed, and artifacts when relevant. For semantic `src/inet/` implementation, do not combine unresolved contract completion and write authority in one assignment. First provide the available `inet-code-authoring` evidence in a read-only contract assignment; after the implementer returns a complete self-validation, the orchestrator validates it and sends a separate follow-up that authorizes the first write. Reuse that implementer for the authorized implementation and related follow-up work.

For implementation, regression, and extraction assignments, include the applicable skill/reference
sections and the concrete evidence to return. A model binding or high reasoning effort does not
replace the contract checks: the implementer must load the selected authoring references, the
regression agent must identify the exercised failure path, and the extractor must report empty or
ambiguous selections without interpreting them as a pass. Keep causal and normative judgments in
the specialist classes assigned those responsibilities above.

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
