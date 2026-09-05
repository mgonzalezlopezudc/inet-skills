---
name: inet-branch-rebase-simple
description: Quickly rebase an already-tested linear INET topic once onto one pinned upstream target when commits replay one-to-one without conflicts, changed-contract overlap, semantic adaptations, commit restructuring, or new baseline movement; use ordinary Git when no INET evidence is required and inet-branch-rebase for staged or forensic work.
---

# INET simple branch rebase

Replay a straightforward topic once onto a pinned upstream target, then verify the final series in a
single sequential sweep. This is the evidence-backed middle path between an ordinary Git rebase and
the staged forensic `inet-branch-rebase` workflow. The original topic never moves.

This mutates repository history. Start only when the user requested a rebase with INET verification.
Use ordinary Git when no special `opp_repl` evidence is required. Use `inet-branch-rebase` when this
skill's admission contract is not satisfied.

## Admission contract

Use this skill only when all of these are true:

- Pinned `base` is an ancestor of both pinned `topic` and pinned `main`; `topic` is linear.
- Every `base..topic` commit will be replayed once, in its original order, with no split, squash,
  drop, reword, or other history cleanup.
- The pinned topic already passes a directly related `opp_repl` contract with reproducible evidence,
  and a valid pinned-main control for upstream-existing selectors is available or can be run once.
- Complete topic and upstream diffs plus dependency mapping show no overlapping changed contract or
  predicted behavioral coupling. Disjoint file paths alone are not sufficient evidence.
- Replay is expected to apply without conflicts; this fast path accepts no conflict resolution.
- Existing baseline changes, if any, are already approved and remain in their causal topic commit.
  The rebase will not create or correct baseline values.

Before planning, use `inet-pull-request-authoring` and read `doc/project/rule/pull-request.md`. Use
`inet-opp-repl` for command discovery, dependency mapping, scoped execution, and normalized results.

## Pin and approve once

Record full `base`, `topic`, and `main` SHAs, the new `target` branch, the ordered topic commit list,
build mode, and directly related selectors. Never modify or repoint `topic`, and do not absorb later
movement of any input ref.

Inspect both `base..topic` and `base..main`. Present one table mapping each topic commit to its target
position, intent, expected upstream interaction, and test selector. Include the pinned-main control
and final union scope. Obtain one approval for this replay-and-test plan unless the user's request
already specified the same pinned inputs and exact one-to-one replay.

Verify ancestry and linearity before replay:

```text
git merge-base --is-ancestor <base-sha> <topic-sha>
git merge-base --is-ancestor <base-sha> <main-sha>
git rev-list --merges <base-sha>..<topic-sha>
```

The ancestry commands must succeed and the merge list must be empty. Run the applicable directly
related control scope on pinned `main` unless equivalent current evidence already proves it. Identify
selectors introduced by the topic instead of attempting to treat zero cases on `main` as a control.

## Replay once and prove equivalence

Create `target` from the immutable topic in a disposable worktree, then rebase only `target` onto
pinned `main`. Abort immediately on a conflict; do not resolve it on this fast path.

Before simulation verification, require all of the following:

```text
git merge-base --is-ancestor <main-sha> <target-sha>
git rev-list --merges <main-sha>..<target-sha>
git rev-list --count <base-sha>..<topic-sha>
git rev-list --count <main-sha>..<target-sha>
git range-diff <base-sha>..<topic-sha> <main-sha>..<target-sha>
```

The ancestry command must succeed, the merge list must be empty, the counts must match, and every
range-diff row must be an equal one-to-one pair in the original order. Any added, removed, reordered,
or patch-changed commit is outside this skill. Audit the candidate against applicable
`PR-SERIES-ORDER`, `PR-SERIES-LINEAR`, and `PR-MSG-*` rules before starting expensive tests.

## Verify the final series once

Walk every target commit from oldest to newest in one uninterrupted sequential run, using a
reusable verification worktree so `target` remains pinned at its final SHA. Retain build artifacts
under the [incremental build recipe](../inet-opp-repl/references/incremental-builds.md) throughout
the sweep; dispose of the worktree only after verification and evidence collection. For each commit:

1. Build matching INET artifacts and run explicitly filtered, directly related `opp_repl` cases.
   Zero executed cases is not evidence.
2. Attribute the selected result to the pinned-main control, the corresponding topic effect, or
   their non-overlapping combination. Any unexplained movement leaves the fast path.
3. Record one concise row with source and target SHAs, subject, build command/status, selector,
   `opp_repl` status, exit code, and artifact or normalized-envelope path.

Do not deliver until every target commit satisfies `PR-SERIES-BUILDS`. Then run the approved final
union at `target` HEAD and perform the final `PR-*` audit. Do not repeat checkpoint or middle-commit
tests when the sweep already tested those exact trees and nothing was rewritten afterward.

Keep one compact execution record under `ai-logs/executions/` only when the work must survive across
turns; otherwise the approved table and final report are sufficient.

## Escalate instead of adapting

Stop and hand the pinned inputs, plan, target candidate, range-diff, controls, and test evidence to
`inet-branch-rebase` when any of these occurs:

- dependency mapping is missing, uncertain, or shows changed-contract overlap;
- pinned `main` fails its required control;
- replay conflicts or the range-diff is not one-to-one and equal;
- any target commit fails or produces an unexplained result;
- a baseline update, semantic adaptation, commit restructuring, grouping, checkpoint, or forensic
  attempt history becomes necessary.

Do not repair conflicts, change source behavior, or weaken the test contract to remain on the fast
path. Publishing the target or a pull request is separate scope and requires an explicit user
request.
