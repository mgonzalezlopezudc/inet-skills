# Rebase topology and stage execution

Read this reference after the input commit groups are approved and before proposing integration mode
or upstream checkpoints.

## Integration mode

Choose exactly one mode:

- **`parallel-end`** — advance each group independently across plain upstream checkpoints and combine
  all groups only at pinned `main`.
- **`lockstep`** — advance every group to one checkpoint, assemble and test their combined state,
  then continue.
- **`serial`** — finish one group across every checkpoint, then walk the next group across the same
  checkpoints on predecessor-group same-stage safe points.

Record the choice and why it bounds conflicts and regression diagnosis. Obtain approval for the mode
and each group's ordered checkpoint list before execution.

## Anchors and replay manifests

For every group/stage, record separately:

- **stage anchor** — supplies current upstream and earlier-group context but contains none of the
  current group's replay manifest;
- **replay manifest** — ordered original topic commits plus each approved adaptation assigned to the
  group.

Create each attempt from the anchor and apply every manifest item exactly once. The previous
same-group safe point is a comparison/replay source, not the parent of the next attempt.

Use plain upstream checkpoint `Sj` as the anchor for `parallel-end`, individual `lockstep` attempts,
and serial group 1. For serial `Gi` where `i > 1`, use `G(i-1)`'s promoted safe point at `Sj`.
Complete all checkpoints for the predecessor before starting the next serial group.

`stage-0` is the first tested replay, not an alias for `base`. Its anchor is `base` except for later
serial groups, where the predecessor's promoted `stage-0` point is the anchor.

## Attempts and safe points

Keep the build workspaces reusable under the
[incremental build recipe](../../inet-opp-repl/references/incremental-builds.md). Immutable attempt
refs and evidence survive independently of the worktree used to compile and test them.

For each group/checkpoint:

1. Create immutable `rebase/group-<id>/attempt/<stage>-<attempt>` at the resolved anchor and apply the
   manifest once in recorded order.
2. Prove the checkpoint is an ancestor, the current group is absent from the anchor, and the linear
   segment maps one-to-one from source manifest SHAs to result SHAs. Record the tree comparison.
3. Run the scope defined by `references/opp-repl-contract.md` and preserve its normalized result.
4. Keep the attempt branch whether it passes or fails. Never amend, rebase, delete, or repoint a
   recorded attempt.
5. Promote a clean SHA to `rebase/group-<id>/stage-<stage>` and continue without a new pause.

The `attempt/` and `stage-` namespaces are separate because a Git ref cannot be both a leaf and a
directory. Branches, not tags, are authoritative.

For lockstep, assemble `rebase/integration/attempt/<stage>-<attempt>` from plain `Sj`, replay all
current manifests once in approved order, and test the union scope. Promote only a passing combined
SHA to `rebase/integration/stage-<stage>`; no group advances before it exists. For parallel-end, do
the same at `main` using `final` names. In serial mode, the last group's tested safe point is the
combined accumulated state.

When plain upstream fails, preserve the control evidence and obtain approval before subdividing,
replacing, or skipping that checkpoint. When any attempt fails, keep it and read
`failure-recovery.md`.
