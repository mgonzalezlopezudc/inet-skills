---
name: git-regression-safe-rebase
description: Rebase a long-lived topic branch through approved commit groups and adaptive upstream stages while preserving every attempt, proving regression-free safe points, and maintaining a cold-resumable audit log. Use for high-risk opp_repl-backed rebases; do not use for ordinary one-shot rebases.
---

# Regression-safe staged rebase

Carry `base..topic` onto `main` without rewriting the forensic work history. The deliverable is a clean target branch; attempt and safe-point branches remain as an audit trail.

## Establish the contract

Record the resolved SHAs for `base`, `topic`, and `main` HEAD before creating rebase branches. Also record:

- the selected opp_repl test types and scope hints; default to fingerprint plus statistical tests and run number 0 only unless the task opts into more runs;
- one integration mode: **parallel-end** (groups advance independently on plain `main`), **lockstep** (all groups are combined and tested at every stage), or **serial** (each completed group becomes the base for the next);
- project paths and the exact test invocation.

First write `ai-logs/executions/<date>_<rebase-name>.analysis.md`. Include both upstream and topic logs/diff stats, topic commit categories, file overlap, opp_repl dependency-store mappings from commits through NED packages/features/configurations, and predicted conflicts. Keep this analysis separate from the execution logbook.

## Obtain approval for the rebase topology

Partition every commit in `base..topic` exactly once into ordered groups of whole commits. Reordering is allowed; splitting or squashing input commits is not. Put proposed removals in an explicit `dropped` group with a rationale.

Choose each group's ordered upstream checkpoints `[S0=base, ..., Sk=main HEAD]` from dependency overlap and expected diagnosis surface. Prefer checkpoints that introduce a small coherent upstream change. Before execution, obtain human approval for both the grouping and each group's stages.

If later evidence requires regrouping, retain the old group branches, allocate monotonically increasing new group IDs, and record `superseded-by`. If a stage is too coarse, request approval before subdividing it. If plain `main@Sj` fails the selected regression test, do not attribute that failure to the topic group; log and either replace/skip the checkpoint with approval or escalate.

## Advance through forensic attempts

For every group/stage transition:

1. Start from the previous proven safe point required by the integration mode.
2. Create `rebase/group-<i>/attempt/<j>-<k>`, apply the group's commits, and run one scoped opp_repl invocation. Treat build failure as `ERROR`; treat a zero-test selection as invalid validation.
3. Preserve the attempt branch whether it passes or fails. Never amend, rebase, delete, or repoint forensic attempt history.
4. On a clean pass, pin the SHA as `rebase/group-<i>/stage-<j>` and advance without an approval pause.

The separate `attempt/` and `stage-` namespaces are intentional: Git cannot store a ref as both a leaf and a directory.

Per-stage tests cover only configurations the dependency store marks as affected by that group, using run 0 by default. Consume detailed result artifacts during diagnosis and retain concise evidence in the logbook; reserve the unscoped regression run for finalization.

## Diagnose and adapt failures

For `FAIL` or `ERROR`, compare the current attempt with all four controls:

- the original `topic`, representing intended behavior;
- `base`, the pre-divergence reference;
- plain `main@Sj`, the upstream-stage control;
- the group's previous safe point, isolating the current transition.

Explain the first causal divergence, not only the terminal symptom. Preserve the failed attempt, create the next attempt branch, and add each adaptation as a new fix commit; never amend or rewrite an input commit. Re-run the same scoped test first.

When a fix passes, pause for human approval before promoting its SHA to a safe point. The approval summary must be a condensed view of the durable fix record. On persistent failure, stop and present evidence-backed choices such as stage subdivision, group split/merge, or human-led investigation.

## Maintain a cold-resumable logbook

Use `ai-logs/executions/<date>_<rebase-name>.md`. Use full ISO 8601 timestamps with seconds inside the file. Edit curated status sections in place, but keep the attempt log append-only.

The curated head must identify:

- immutable input SHAs, analysis-file link, integration mode, paths, and test contract;
- current and superseded groups, ordered commits, intent, current stage, and current branch;
- stages with their rationales, subdivisions, skips, or replacements;
- completion estimates and the latest scoped invocation per group;
- the latest regression-free branch per current group;
- every safe point with SHA and proof status, initialized with each group at `stage-0` on `base`;
- open issues and the exact next action.

Append one progress entry for every attempt. A clean pass may be one line containing timestamp, transition, attempt, branch SHA, scope, and result. A failed or repaired attempt must include the diagnosis and one sub-entry per fix, in application order, with these exact fields:

1. **Fix commit** — SHA, subject, and adapted topic commit(s), or `infrastructure / cross-cutting`.
2. **What failed before** — precise error, failing test/config/run, or quantified fingerprint/statistical delta; quote only the output fragment that identifies it.
3. **How it got better after** — the result of the same check after the fix, including any remaining explained divergence.
4. **Why the fix is correct** — the causing upstream/topic change, restored API or data-flow contract, affected call sites, and any non-obvious invariant supporting the conclusion.

If conflict resolution folds an adaptation into a cherry-pick, still create the fix record and write `Fix commit: folded into cherry-pick of <SHA>`.

## Finalize without scaffolding

After all groups reach `main` HEAD, assemble a clean target containing the original topic commits in approved application order plus accepted fix commits. Do not include per-stage scaffolding; retain all historical branches separately.

Run the full unscoped regression contract on both the clean target and the original topic. Completion requires matching results or an explanation for every delta in the logbook. Finish the logbook with each fix mapped to the topic commit it adapts and the diagnosis that required it, then request final delivery approval.
