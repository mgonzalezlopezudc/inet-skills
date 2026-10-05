---
name: inet-branch-cleanup-simple
description: Rebuild a tested, linear INET topic branch on the same pinned base. Use when the squash, reorder, reword, or small split is clear. The task must need no new baseline change, semantic repair, temporary detour, or repeated group revision. Use inet-branch-cleanup for complex reconstruction or a detailed record of attempts.
---

# INET simple branch cleanup

Rebuild a simple topic branch as a reviewable commit series with the same final tree.
Construct the complete series first.
Verify every output commit in one sequential run.
The original topic remains immutable.

This mutates repository history. Start only when the user requested history reconstruction. Use
`inet-pull-request-authoring` alone when the request is only to plan or audit commits, and use
`inet-branch-cleanup` when this skill's admission contract is not satisfied.

## Admission contract

Use the shared [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to
discover the active project's current series, protection, baseline, and verification requirements.

Use this skill only when all of these are true:

- `base` and `topic` can be pinned, and `topic` is a linear branch on that unchanged base.
- The pinned topic already passes a directly related `opp_repl` test contract with reproducible
  evidence.
- One clear mapping from the topic commits or hunks to the intended output commits is visible after
  reading the complete `base..topic` log and diff.
- Cleanup needs no temporary content absent from both `base` and `topic`.
- Existing baseline changes satisfy the current baseline and series procedures, including any required approval and commit placement.
  Cleanup will not create or correct baseline values.

Before planning, use `inet-pull-request-authoring` and discover the active project's current series
guidance. Use
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

Create `clean` from the pinned base.
Build the approved series without a pause between commits.
Use the simplest fitting Git operation; hand-stage only a genuinely small split. Do not add
scaffolding or repair source behavior during cleanup.

Before verification, require all of the following:

```text
git diff --exit-code <topic-sha> <clean-sha> --
git rev-list --merges <base-sha>..<clean-sha>
```

The diff command must succeed, and the merge list must be empty. Tree equality covers baseline files
too; this fast path has no exception ledger. Also audit the constructed series against the applicable
project series and message guidance before spending time on the verification sweep.

## Verify in one sweep

Walk every output commit from oldest to newest in one uninterrupted sequential run. Reuse one
verification worktree with retained build artifacts so the `clean` ref remains pinned at its final
SHA. Apply the [incremental build recipe](../inet-opp-repl/references/incremental-builds.md);
dispose of the worktree only after verification and evidence collection are complete. For each commit:

1. Build the INET artifacts for the selected commit.
   Run its explicitly filtered, directly related `opp_repl` cases.
   Zero executed cases is not evidence.
2. Require behavior-preserving commits to retain the selected behavior signal. For a fix or feature,
   accept movement only in the predicted, already-approved scope.
3. Record one concise result row: commit SHA and subject, build command/status, test selector,
   `opp_repl` status, exit code, and artifact or normalized-envelope path.

Do not deliver a candidate until every commit satisfies the active per-commit build requirement. After the sweep, run the
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
