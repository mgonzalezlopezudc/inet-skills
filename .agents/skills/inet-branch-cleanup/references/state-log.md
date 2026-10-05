# INET cleanup analysis and state log

The cleanup must be resumable from disk alone. Keep two files under `ai-logs/executions/`, not `ai-logs/plans/`:

- `<date>_<cleanup-name>.analysis.md` — the durable analysis of the original branch;
- `<date>_<cleanup-name>.md` — the live execution logbook.

Use full ISO 8601 timestamps with seconds inside the files. Keep the date-only form in their names.

## Analysis file

Record the pinned `base` and `topic` SHAs and the total diff size in files, insertions, and deletions. Classify the diff at hunk or sub-hunk level into refactors, fixes, features, and chores. Map dependencies between those changes, including any region that may require a hand-authored intermediate state.

Also record how changed paths map to affected tests and configurations, the evidence behind that mapping, and the first grouping proposal. The state file should link to this analysis and summarize it rather than copy it.

## State file

Treat the state file as a logbook. Edit the current-state sections in place; keep the progress log append-only; write Finalization once.

The current-state sections are:

1. **Header** — pinned inputs, clean branch, analysis link, project information, exact build and test invocation, ordered test types, configurations, runs or seeds, baseline and dependency-store paths, and approval constraints.
2. **Total-diff analysis** — a concise summary of the hunk categories, affected areas, dependencies, and predicted test impact.
3. **Change groups** — ID, type, intent, files or hunks, independence and dependency notes, target commits, and any `superseded-by` link.
4. **Output-commit plan** — position, type, subject, feeding groups, and expected test effect. Update it in place after approved replanning.
5. **Coverage ledger** — initial size, material applied so far, raw remaining size, and each file marked `fully assigned`, `partially assigned`, or `untouched`. Keep approved baseline exceptions and open detours as explicit lists. Refresh this section after every commit.
6. **Progress and safe points** — every validated commit's SHA, subject, type, and test status; the latest safe point; the next action; and an approximate completion percentage such as `1 - remaining/total` by line volume. The percentage is an orientation aid, not the proof of completion.
7. **Open issues / next step** — pending approvals, unexplained evidence, planned regrouping, and the exact next action.
8. **Finalization** — written once when the cleanup is complete.

## Progress log

Append one entry for every output commit and every rework attempt. Record:

- timestamp, planned position and type, SHA, and subject;
- the groups or hunks absorbed and the resulting ledger movement;
- build result, test result (`PASS`, `FAIL`, or `ERROR`), exact scope, run or seed, exit status, and artifact paths when applicable;
- for a behavior-preserving commit, the previous safe point and confirmation that the selected behavior signal stayed identical;
- for a temporary detour, its ID, the scaffold added or removed, why ordering could not avoid it, and the expected ledger growth or shrinkage;
- for an approved test-red commit, the justification and the later commit expected to turn it green.

For every behavior-changing commit, add these four labelled fields in this order:

1. **What changed** — the code change and the precise test delta, including affected configurations and useful quantitative detail.
2. **Why the result changed** — the causal mechanism, tied to the lines introduced by this commit.
3. **Why it's acceptable** — why the new behavior is correct or intended, and why unrelated behavior should not have moved.
4. **Baseline update** — record the exact entries or artifacts, method, result codes, approval source, and commit SHA for the update.
   Link the causal source change or explain why no single source change caused the movement.
   Use the current baseline and series procedures to determine commit placement.

Detailed result files may be temporary. Before discarding them, preserve the exact invocation, decisive evidence, causal explanation, exit status, and any durable artifact paths in the logbook.

## Finalization

Record the final evidence:

- Ordered commit list and commit types.
- Exact tree-equality command and exit status.
- All permitted baseline differences.
- Confirmation that no material remains unassigned and no temporary detour remains open.
- Final test command and result.
- Checks of selected intermediate safe points.
- Each behavior-changing commit, its explanation, and its baseline update.
