---
name: inet-branch-cleanup-simple
description: Quickly rebuild a tested, linear INET topic branch on the same pinned base when the desired squash, reorder, reword, or small split is obvious and needs no new baseline movement, semantic repair, temporary detour, or iterative regrouping; use inet-branch-cleanup for complex or forensic reconstruction.
---

# INET simple branch cleanup

Rebuild a straightforward topic branch as a reviewable commit series without changing its final
tree. This is the fast path: construct the complete series first, then verify every output commit in
one sequential sweep. The original topic remains immutable.

This mutates repository history. Start only when the user requested history reconstruction. Use
`inet-pull-request-authoring` alone when the request is only to plan or audit commits, and use
`inet-branch-cleanup` when this skill's admission contract is not satisfied.

## Admission contract

Use this skill only when all of these are true:

- `base` and `topic` can be pinned, and `topic` is a linear branch on that unchanged base.
- The pinned topic already passes a directly related `opp_repl` test contract with reproducible
  evidence.
- One clear mapping from the topic commits or hunks to the intended output commits is visible after
  reading the complete `base..topic` log and diff.
- Cleanup needs no temporary content absent from both `base` and `topic`.
- Existing baseline changes, if any, are already approved and can remain with their causal source
  change. Cleanup will not create or correct baseline values.

Before planning, use `inet-pull-request-authoring` and read `doc/project/rule/pull-request.md`. Use
`inet-opp-repl` to discover the active interface, map directly related configurations, and normalize
the verification results.

## Pin and approve once

Resolve and record the full SHAs of `base` and `topic`, the new `clean` branch name, and the exact
build mode and test selectors. Never modify or repoint `topic`, and do not absorb later movement of
the base ref.

Present one ordered table containing each proposed commit's subject, single intent, source commits
or hunks, dependencies, expected behavior effect, and directly related test selector. Obtain one
approval for that combined plan before creating `clean`, unless the user's reconstruction request
already specified the same exact order and boundaries.

## Construct before testing

Create `clean` from the pinned base and build the approved series without pausing between commits.
Use the simplest fitting Git operation; hand-stage only a genuinely small split. Do not add
scaffolding or repair source behavior during cleanup.

Before verification, require all of the following:

```text
git diff --exit-code <topic-sha> <clean-sha> --
git rev-list --merges <base-sha>..<clean-sha>
```

The diff command must succeed, and the merge list must be empty. Tree equality covers baseline files
too; this fast path has no exception ledger. Also audit the constructed series against the applicable
`PR-SPLIT-*`, `PR-SERIES-ORDER`, and `PR-MSG-*` rules before spending time on the verification sweep.

## Verify in one sweep

Walk every output commit from oldest to newest in one uninterrupted sequential run. Reuse one
verification worktree with retained build artifacts so the `clean` ref remains pinned at its final
SHA. Apply the [incremental build recipe](../inet-opp-repl/references/incremental-builds.md);
dispose of the worktree only after verification and evidence collection are complete. For each commit:

1. Build the matching INET artifacts and run its explicitly filtered, directly related `opp_repl`
   cases. Zero executed cases is not evidence.
2. Require behavior-preserving commits to retain the selected behavior signal. For a fix or feature,
   accept movement only in the predicted, already-approved scope.
3. Record one concise result row: commit SHA and subject, build command/status, test selector,
   `opp_repl` status, exit code, and artifact or normalized-envelope path.

Do not deliver a candidate until every commit satisfies `PR-SERIES-BUILDS`. After the sweep, run the
union of the directly related selectors at `clean` HEAD and record its result. Do not repeat
middle-commit spot checks when the sweep already tested those exact trees and no commit was rewritten
afterward.

Keep a single compact execution record under `ai-logs/executions/` only when the work must survive
across turns; otherwise the combined plan and final report are sufficient.

## Escalate instead of expanding

Stop this fast path and hand the pinned inputs, approved plan, candidate branch, and evidence to
`inet-branch-cleanup` when any of these occurs:

- a planned boundary or order must change;
- final tree equality cannot be reached by the approved mapping;
- a commit fails to build, produces an unexplained result, or needs semantic repair;
- a baseline needs correction or new approval;
- a temporary detour, detailed coverage ledger, checkpoint branch, or forensic resumability becomes
  necessary.

Do not weaken the test contract to keep the cleanup on the fast path. Publishing a branch or pull
request remains separate scope and requires an explicit user request.
