---
name: inet-branch-rebase
description: Rebase an opp_repl-tested INET topic branch across approved upstream checkpoints while preserving forensic attempts and proving regression-safe points. Use for high-risk rebases onto changed upstream history; do not use for ordinary one-shot rebases or fixed-base history cleanup.
---

# INET branch rebase

Carry the commits in a pinned `base..topic` range onto a pinned `main` HEAD through approved commit
groups and adaptive upstream checkpoints. Keep the original refs immutable, preserve every attempt
branch, and deliver a clean target containing the approved rebased topic commits plus accepted
adaptation effects with recorded provenance and no stage-only scaffolding.

This is a repository-mutating workflow. Start it only when the user explicitly requests a high-risk
upstream rebase. Use `inet-branch-cleanup` when the base is fixed and the task is to split, squash,
or re-author history; use an ordinary Git workflow for a low-risk one-shot rebase.

Before grouping commits or assembling the final series, use `inet-pull-request-authoring` and read
`doc/project/rule/pull-request.md`. This workflow preserves whole input commits and does not itself
authorize splitting or squashing them. If the final series also needs history cleanup, report that
separate scope instead of silently combining the operations.

Before starting a rebase, read both [references/state-log.md](references/state-log.md) and
[references/opp-repl-contract.md](references/opp-repl-contract.md). They define the durable recovery
record and the evidence needed to promote a safe point.

An adaptation commit is a new production change, not merely conflict resolution. Before authoring
one, use `inet-code-authoring`; for semantic changes under `src/inet/`, first use
`inet-architectural-requirements` to resolve architecture, naming, exception-ledger, review, and
sealing requirements. Rebase authorization does not authorize an unrelated redesign or a baseline
update.

## Inputs and acceptance criteria

Resolve and record these inputs before creating any rebase branch:

- **`base`** — the exact commit delimiting the topic range. Verify that it is an ancestor of the
  pinned `topic` and `main` commits.
- **`topic`** — the original topic ref and pinned HEAD SHA. Never move or rewrite it.
- **`main`** — the upstream ref and pinned target SHA. Do not absorb later upstream movement.
- **`target`** — the new clean branch to deliver.
- **tests** — the directly related `opp_repl` categories, configurations, runs or seeds, build mode,
  scope mapping, and result controls.
- **integration mode** — exactly one of `parallel-end`, `lockstep`, or `serial`.

The rebase is complete only when:

1. Every commit in `base..topic` appears exactly once in a current group or in an explicitly
   approved `dropped` group.
2. Every current group reaches the pinned `main` SHA through promoted, tested safe points; every
   required combined integration state also passes; and every attempt and superseded grouping
   remains addressable by its immutable branch.
3. The clean target contains each non-dropped topic commit's rebased effect in approved order plus
   every accepted adaptation effect with recorded provenance, and contains no per-stage
   scaffolding.
4. Every commit in the final target series passes its applicable `PR-SERIES-BUILDS` and
   `PR-SERIES-ORDER` checks, the final directly related test contract passes, and every
   target-versus-control difference is attributed to upstream behavior, an intended topic effect,
   or an accepted adaptation.
5. `inet-pull-request-authoring` has audited the resulting series. A series that still requires
   unauthorized splitting, squashing, or re-authoring is not review-ready; obtain approval or hand
   it off to `inet-branch-cleanup` rather than silently rewriting it.

## Phase 0 — Analyze both sides

Read the complete upstream and topic histories and diffs. Record `git log` and diff statistics for
`base..main` and `base..topic`, categorize topic commits, map file and contract overlap, query the
`opp_repl` dependency store from changed paths through NED packages and features to configurations,
and predict conflict and regression surfaces.

Write this durable analysis to `ai-logs/executions/<date>_<rebase-name>.analysis.md`. Keep it
separate from the execution logbook and link it from that logbook.

## Phase 1 — Form commit groups

Partition `base..topic` into ordered groups:

- Whole commits are the atomic unit. Reordering is allowed; splitting and squashing are not.
- Assign every topic commit exactly once. Put a proposed removal in an explicit `dropped` group with
  its rationale and obtain approval before excluding it from the target.
- Prefer groups that minimize the diagnosis surface and have a coherent affected contract and test
  scope.
- If evidence later requires regrouping, preserve existing group branches, allocate fresh increasing
  group IDs, and retain the superseded entries with `superseded-by` links.

Obtain human approval for the initial groups and their commit order before execution.

## Phase 2 — Select topology and upstream stages

Choose and record one integration mode:

- **`parallel-end`** — advance each group independently over plain upstream checkpoints and combine
  the groups only after they reach pinned `main`.
- **`lockstep`** — advance all groups to each checkpoint, combine them there, and test their
  integration before moving to the next checkpoint.
- **`serial`** — complete one group across all checkpoints, then walk the next group across those
  checkpoints on the predecessor group's corresponding same-stage safe points.

For every group and stage, record two distinct inputs:

- the **stage anchor**, whose tree supplies the current upstream and earlier-group context but
  contains none of the current group's replay manifest; and
- the **replay manifest**, the ordered original topic commits in the group plus every approved
  adaptation assigned to that group.

Construct the attempt from the stage anchor and apply every manifest item exactly once. The previous
same-group safe point is a comparison and replay source, not the parent of the next attempt. Use
these topology-specific anchors:

- for `parallel-end` and each group's individual `lockstep` attempt, upstream checkpoint `Sj`;
- for serial group 1, upstream checkpoint `Sj`;
- for serial group `Gi`, where `i > 1`, group `G(i-1)`'s promoted safe point at the same checkpoint
  `Sj`.

Complete all checkpoints for serial group `G(i-1)` before starting `Gi`. Thus later serial groups
walk the same upstream checkpoints while retaining the tested effects of all predecessor groups.

For each group, choose ordered upstream commits `[S0=base, ..., Sk=main]`. Prefer checkpoints that
introduce a small, coherent upstream change and make a failure attributable. Record why each stage
exists and obtain approval for the mode and stage lists.

`stage-0` is the first tested application of a group's manifest, not an alias for `base`. Its anchor
is `base` for parallel, lockstep, and serial group 1; for later serial groups it is the predecessor
group's promoted `stage-0` safe point.

When a stage is too coarse, propose a subdivision. When plain upstream at a stage fails the selected
contract, do not attribute that failure to the topic group: preserve the control evidence and obtain
approval before replacing or skipping the stage.

## Phase 3 — Advance through forensic attempts

For every group and checkpoint:

1. Resolve the topology-specific stage anchor and the immutable replay-source refs. Create
   `rebase/group-<id>/attempt/<stage>-<attempt>` at the anchor and apply the group's replay manifest
   in its recorded order exactly once.
2. Before testing, prove that `Sj` is an ancestor of the attempt, the current group is absent from
   the anchor, and the linear segment from anchor to attempt maps one-to-one to the manifest. Record
   the anchor SHA, source SHAs, result SHAs, and tree comparison.
3. Run one directly related scoped `opp_repl` invocation using the topology-specific scope in the
   contract reference.
4. Preserve the attempt branch whether it passes or fails. Never amend, rebase, delete, or repoint a
   recorded attempt.
5. On a clean pass, pin the SHA as `rebase/group-<id>/stage-<stage>` and continue without an approval
   pause.

For `lockstep`, a set of individually passing group points is not an integration safe point. After
all groups reach `Sj`, create `rebase/integration/attempt/<stage>-<attempt>` from plain `Sj`, replay
all current group manifests once in the approved global order, and run the union scope. Preserve
every combined attempt. Promote a passing combined SHA to `rebase/integration/stage-<stage>`; do not
advance any group beyond `Sj` until this combined safe point exists. Assign an integration repair to
the causal group, or to an explicit approved cross-cutting manifest that is replayed at every later
combined checkpoint and in the final target.

For `parallel-end`, create the same kind of combined integration attempt after all groups reach
`main`, using `rebase/integration/attempt/final-<attempt>` and `rebase/integration/final`. For
`serial`, the last group's safe point at a checkpoint is already the combined accumulated state;
test the accumulated scope before promoting it.

The separate `attempt/` and `stage-` namespaces are required because a Git ref cannot be both a leaf
and a directory. Use branches, not tags, as the authoritative attempt and safe-point references,
and treat their names as immutable after creation or promotion.

## Diagnose and adapt failures

For `FAIL` or `ERROR`, compare the attempt with every applicable control. After `stage-0`, these are
normally four distinct comparison roles:

- the original pinned `topic`, representing the pre-rebase topic behavior;
- the topology-specific stage anchor, including the predecessor group's same-stage safe point in
  serial mode;
- plain upstream at the current checkpoint; and
- the group's previous promoted safe point, or the previous combined integration safe point for a
  combined lockstep transition.

At `stage-0`, the anchor and plain-upstream control may both be `base`, and no previous same-group
safe point exists; record the collapsed roles instead of inventing redundant evidence.

Explain the first causal divergence rather than only the final symptom. Preserve the failed attempt,
create a fresh attempt branch, and represent each semantic adaptation as a new fix commit. Re-run
the same scoped check first so the before/after evidence remains comparable. If mechanical conflict
resolution must be folded into a cherry-pick, record that fact and the adapted input commit in the
same fix schema used for a separate commit.

When an adapted attempt passes, obtain human approval before promoting it to a safe point. On
persistent failure, stop with evidence-backed choices such as stage subdivision, group split or
merge, integration-mode revision, or human-led investigation; do not silently broaden the rebase or
discard the failing history.

## Maintain resumable state

Use `ai-logs/executions/<date>_<rebase-name>.md` as the execution logbook. Keep its current-status
sections curated and its attempt log append-only. Record every branch and SHA needed to resume from
disk without conversation history, including control evidence, safe points, superseded topology,
accepted fixes, pending approvals, and the exact next action.

Ask for human input before the initial topology, any fix promotion, regrouping, stage subdivision or
replacement or skip, integration-mode change, baseline update, and final delivery. Do not pause for
a clean stage advance that matches the approved topology and evidence contract.

## Finalize

After every current group reaches pinned `main`:

1. Assemble the clean target from pinned `main`, the rebased equivalents of all non-dropped topic
   commits in approved order, and every accepted adaptation effect. Exclude per-stage scaffolding.
   Keep an adaptation as its own commit only when it is an independently valid prerequisite placed
   before its first consumer. Otherwise fold it into the causal rebased commit while retaining the
   immutable forensic attempt that proved the repair. If this re-authoring exceeds the approved
   rebase scope, obtain approval or hand off to `inet-branch-cleanup` before calling the result
   review-ready.
2. Prove the commit-coverage mapping and confirm that historical attempt, integration, and safe-point
   refs still resolve to their recorded SHAs.
3. Check out and test every final target commit in order with its directly applicable build/test
   scope. A later fix commit does not excuse a broken earlier commit. Then run the final union
   `opp_repl` contract. Use the original topic and plain pinned upstream as controls where they
   distinguish intended upstream movement from a rebase regression.
4. Use `inet-pull-request-authoring` to audit commit boundaries, order, messages, per-commit evidence,
   and the final branch story under the applicable `PR-*` rules.
5. If the user requested a push or pull request, follow `doc/project/guide/run-the-gates.md` before
   publication and record the required debug/release and enforcement results. For local-only
   delivery, explicitly record that publication gates were not run and do not publish.
6. Finish the logbook with the target SHA, group/stage completion, exact per-commit and final test
   evidence, every explained delta, and each adaptation mapped to the topic and upstream changes
   that required it.

Request final delivery approval. Draft or publish a pull request only when the user explicitly asks
for that additional action.
