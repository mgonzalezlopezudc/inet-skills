---
name: inet-branch-rebase
description: Rebase an opp_repl-tested INET topic branch across approved upstream checkpoints while preserving forensic attempts and proving regression-safe points. Use for high-risk rebases onto changed upstream history; do not use for ordinary one-shot rebases or fixed-base history cleanup.
---

# INET branch rebase

Carry a pinned `base..topic` range onto pinned `main` through approved commit groups and upstream
checkpoints. Preserve every attempt branch and deliver a clean target containing approved topic and
adaptation effects, with no stage-only scaffolding.

This mutates history. Start only when the user explicitly requests a high-risk upstream rebase. Use
`inet-branch-cleanup` for fixed-base split/squash/re-authoring, and ordinary Git for a low-risk
one-shot rebase. Rebase authorization does not authorize unrelated redesign, baseline movement, a
push, or a pull request.

Use `inet-pull-request-authoring` and `doc/project/rule/pull-request.md` before grouping commits. This
workflow preserves whole input commits; splitting or squashing is separate authorized scope.

## Progressive references

- Always read [state-log.md](references/state-log.md) so the work is resumable from disk.
- Use [inet-opp-repl](../inet-opp-repl/SKILL.md) and read
  [opp-repl-contract.md](references/opp-repl-contract.md) when defining verification scope.
- After the groups are approved, read
  [topology-and-stages.md](references/topology-and-stages.md) before choosing mode or executing a
  stage.
- Read [failure-recovery.md](references/failure-recovery.md) only after a failure or when an
  adaptation is required.
- Read [finalization.md](references/finalization.md) only when every group has reached pinned `main`.

## Pinned inputs and acceptance

Record before creating a branch:

- `base` SHA, verified ancestor of pinned `topic` and `main`;
- original `topic` ref/SHA, which never moves;
- upstream `main` ref/SHA, without absorbing later movement;
- new clean `target` branch;
- directly related `opp_repl` categories, configurations, filters, runs/seeds, mode, stores, and
  comparison controls;
- one integration mode: `parallel-end`, `lockstep`, or `serial`.

Completion requires:

1. Every `base..topic` commit appears once in a current group or an explicitly approved `dropped`
   group.
2. Every group reaches pinned `main` through tested promoted safe points; required combined states
   pass; attempt and superseded-group branches remain immutable and addressable.
3. The clean target contains approved rebased effects and adaptation provenance without stage-only
   scaffolding.
4. Every final commit satisfies applicable `PR-SERIES-BUILDS` and `PR-SERIES-ORDER` checks, the final
   directly related contract passes, and every material difference is attributed.
5. `inet-pull-request-authoring` audits the resulting series; unauthorized cleanup remains a
   separate handoff.

## Workflow gates

1. **Analyze both sides.** Record complete upstream/topic logs and diffs, commit categories, overlap,
   dependency mappings, and predicted regression surfaces in
   `ai-logs/executions/<date>_<name>.analysis.md`.
2. **Approve groups.** Partition whole topic commits into ordered, coherent groups. Preserve
   superseded group records under fresh IDs and obtain approval for groups, order, and any drop.
3. **Approve topology.** Select the mode and attributable upstream checkpoints using
   `topology-and-stages.md`; record stage anchors separately from replay manifests.
4. **Advance immutably.** Build fresh attempt branches, prove ancestry and one-to-one replay, run the
   scoped `opp_repl` contract, preserve all attempts, and promote only supported safe points.
5. **Adapt under a new contract.** On failure, freeze the failed attempt and use
   `failure-recovery.md`. A semantic adaptation requires `inet-code-authoring`; semantic `src/inet/`
   scope also requires architecture/seal resolution. Promote a repaired attempt only after approval.
6. **Finalize.** Use `finalization.md` to assemble and prove the clean series, test each commit and
   final union, audit the series, and record local-only or publication-gate status.

Maintain `ai-logs/executions/<date>_<name>.md` throughout. Keep curated current state plus an
append-only attempt log containing branches, SHAs, anchors, manifests, controls, normalized results,
approvals, superseded topology, and exact next action.

Ask for human input before initial groups/topology, a fix promotion, regrouping, checkpoint
subdivision/replacement/skip, integration-mode change, baseline update, and final delivery. A clean
stage matching the approved topology advances without another pause.
