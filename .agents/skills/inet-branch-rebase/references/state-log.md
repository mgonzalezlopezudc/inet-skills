# INET rebase analysis and state log

The rebase must be resumable from disk alone. Keep two files under `ai-logs/executions/`, not
`ai-logs/plans/`:

- `<date>_<rebase-name>.analysis.md` — the durable analysis of upstream and topic history;
- `<date>_<rebase-name>.md` — the live execution logbook.

Use full ISO 8601 timestamps with seconds inside the files. Keep the date-only form in their names.

## Analysis file

Record pinned `base`, `topic`, and `main` SHAs; upstream and topic log/diff statistics; topic commit
categories; file and contract overlap; `opp_repl` dependency-store mappings; and predicted conflicts
or regression surfaces. Include the first grouping, integration-mode, and stage proposal with the
evidence behind each choice.

## Curated state

Edit these current-state sections in place:

1. **Header** — immutable inputs, target branch, analysis link, repository paths, integration mode,
   exact test contract, build mode, configurations, runs or seeds, result-control locations, and
   approval constraints.
2. **Groups** — current and superseded IDs, ordered input commits, intent, affected contracts,
   replay manifest, expected test scope, current stage and branch, and any `superseded-by`
   relationship. Include an explicitly approved `dropped` group when applicable.
3. **Stages per group** — ordered upstream SHAs and rationales, including approved subdivisions,
   replacements, skips, and the evidence for a bad plain-upstream checkpoint. For every stage,
   record the topology-specific anchor SHA and immutable replay-source SHAs separately.
4. **Progress** — per-group and overall completion estimates plus the latest scoped invocation and
   status. Estimates aid orientation; branch and test evidence establish completion.
5. **Latest regression-safe branches** — one row per current group naming its newest promoted stage
   branch, SHA, and proof status.
6. **Safe points** — every promoted `rebase/group-<id>/stage-<stage>` branch with immutable SHA,
   anchor, manifest mapping, scope, command, status, and evidence location. `stage-0` contains the
   group's first tested replay: use pinned `base` as its anchor except for later serial groups, whose
   anchor is the predecessor group's promoted `stage-0` point.
7. **Accepted adaptations** — fix SHA or folded-conflict marker, adapted topic commits, causing
   upstream change, approving decision, and the safe points and final target that contain it.
8. **Combined integration state** — every lockstep integration attempt and safe point, or the final
   parallel integration attempt and safe point, with anchor, complete ordered manifest, union scope,
   command, result, and evidence location. For serial mode, identify the last-group safe point that
   represents each accumulated integration state.
9. **Open issues / next action** — pending regressions, approvals, topology changes, and the exact
   command or decision required to continue.
10. **Finalization** — write once after completion.

## Append-only attempt log

Append one entry for every attempt, including clean passes. Record timestamp, group, stage
transition, attempt number, branch and SHA, stage anchor, replay-source SHAs, ordered manifest,
one-to-one manifest mapping, ancestry/tree assertions, exact scope and invocation, control results,
status, and resulting safe-point or next action. Use the same schema for combined integration
attempts, replacing the single-group manifest with the approved global manifest.

A clean pass may use one concise entry. For a failed or repaired attempt, include the diagnosis and
one sub-entry per adaptation in application order, using these fields:

1. **Fix commit** — SHA and subject plus the adapted topic commit or `infrastructure / cross-cutting`;
   if folded into conflict resolution, write `folded into cherry-pick of <SHA>`.
2. **What failed before** — precise build error, test/configuration/run, or quantified result delta;
   include only the shortest output excerpt that identifies it.
3. **How it got better after** — the same check after the adaptation, including any remaining
   accepted divergence.
4. **Why the fix is correct** — the upstream/topic interaction, restored API or data-flow contract,
   affected call sites, and any non-obvious invariant supporting the conclusion.

Also record the authoring, architecture, sealing, test, review, and baseline evidence or approvals
required for the adaptation. The approval summary must be a condensed view of this durable entry,
not a separate source of truth.

Never edit or remove an earlier attempt entry. When regrouping or changing stages, append the reason
and update only the curated topology and next-action sections.

## Finalization

Record the clean target branch and SHA; approved commit coverage and order; every current group's
last stage; proof that attempt and safe-point refs retain their recorded SHAs; exact final test
commands and results for every target commit and the final union; every material delta and
explanation; and each adaptation mapped to the topic and upstream changes that required it. Record
whether each adaptation remained an independently valid prerequisite or was folded into its causal
rebased commit. Include the final `PR-*` audit, publication-gate evidence or explicit local-only
status, and any residual issue outside the authorized rebase scope.
