---
name: inet-baseline-review
description: Review statistical and chart baseline changes across an INET commit range. Attribute each difference to the smallest justified source change. Use for staged baseline review, temporary reverse experiments, persistent review decisions, and preparation of separate baseline publications. Do not use for test execution alone or fingerprint refreshes.
---

# Review statistical and chart baselines

Produce a reviewable sequence of baseline changes from a pinned source history. Attribute each difference to the smallest source change that explains it. Show why each accepted step improves result correctness or preserves correctness under a justified representation change. A new baseline that makes a test pass supplies no correctness proof.

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) for the active checkout's baseline, test, result-analysis, diagnosis, and publication requirements. Resolve their scope for separate baseline repositories and current source history. Preserve current authorization. If a requirement conflicts with the requested publication, report the conflict before that action. Do not rewrite source history to resolve it without authorization.

Use [inet-statistical-tests](../inet-statistical-tests/SKILL.md) for scalar comparisons and their artifacts. Use [inet-chart-tests](../inet-chart-tests/SKILL.md) for image comparisons and their artifacts. Read each skill when its test type enters the scope. Read [review-record.md](references/review-record.md) before the first experiment. Keep that record sufficient for review and resumption without the conversation.

## Establish the range and first stage

Record the source repository, start SHA, end SHA, selected history, and both baseline repositories with their revisions and local changes. Record the relationship between the initial baselines and the source start. Verify that relationship with a control comparison. Treat an initial mismatch as a separate unresolved item.

List every selected commit in order. Identify merges and the comparison parent for each merge. Expose any history omitted by a first-parent selection. Distinguish a source commit from a baseline commit. A source commit can change expected output without any baseline file in its diff.

Agree on a bounded first stage before substantial execution. Offer approximately 10% of the selected history as an initial stage. Adjust the boundary for dependencies and test cost. Define the commit boundary, test scope, and a time or run limit. Record which limit ends the stage first. Do not interpret a small history fraction as a small execution cost.

Allow investigation to continue within that agreed limit while human decisions remain pending. At the limit, publish the checkpoint. Wait for further scope. Do not run the whole range under an open-ended interpretation of the task.

## Preserve controls and artifacts

Use a small set of task-owned worktrees for history comparisons and temporary experiments. Keep master and the user's active checkout intact. Keep original baseline revisions immutable. Store candidate baselines outside accepted baseline paths until the applicable approval permits replacement. Check runner output locations and repository links before execution. Separate worktrees can still share a baseline directory.

For each comparison, match configuration, run, seed, duration, build mode, and relevant tools. Build artifacts must match the tested source tree. Preserve commands, exit statuses, logs, environment versions, and result identities. If an old endpoint cannot use the current tools, record the incompatibility. Keep any compatibility patch separate from the behavior under review. Check whether that patch changes results before use as a control.

Retain old output, new output, candidate updates, and differences before another run can replace them. For statistics, identify every changed scalar by configuration, run, module, result name, and unit. Include old and new values with absolute differences and valid relative differences. For charts, retain old, new, and difference images with analysis file and chart identity. Link changed curves to their input results. Account for added, removed, and renamed results or charts.

Separate model behavior, scenario configuration, result collection, chart scripts, and export environment as possible causes. A font change does not prove a model improvement. A scalar comparison from one run does not establish statistical confidence. Use independent repetitions only when the correctness claim needs distributional evidence. State the limits of the selected evidence.

## Compile incrementally

Apply the shared [incremental build recipe](../../references/incremental-builds.md) throughout the review. Statistics and chart tests can share a successful build when their source inputs, mode, and toolchain match. Rebuild incrementally after application or removal of a reverse patch that changes compiled inputs.

## Find the smallest defensible cause

Start with a commit and its parent. Narrow each changed baseline to a source hunk when useful. If an intermediate commit cannot build or execute, use the smallest executable set of commits. Record the failure and why a smaller set cannot supply valid evidence. Do not combine unrelated causes for convenience.

Locate changes through scoped intermediate comparisons. Do not assume that baseline changes are monotonic across history. Two commits can change the same result in opposite directions. An unchanged final value can hide both changes. A binary search can locate a candidate, but it cannot prove complete attribution across the selected history.

For each baseline change, explain this causal chain:

1. State the initial scenario and the condition that triggers the behavior.
2. Name the component and the old action that affects the result.
3. Explain the source change and the new action.
4. Connect that action to the observed scalar or image difference.
5. Cite an independent correctness basis, such as a requirement, analytic result, or direct protocol evidence.
6. State what the comparison proves and what remains uncertain.

Separate causal evidence from correctness evidence. A source change can cause a difference and still be wrong. A higher throughput value or a more attractive chart does not establish correctness. A fingerprint detects a trajectory change; it does not decide which trajectory is correct.

Prefer a smaller cause only when it retains a clear correctness argument. Record the tested scope of minimality. Do not claim a global minimum without evidence. If several changes interact, record their joint effect. Do not assume that separate numerical differences add to the combined difference.

## Use a temporary reverse experiment when useful

If the forward explanation remains difficult, try a minimal reverse patch when it can restore the relevant old behavior. Apply it to the new endpoint in an isolated worktree. Reverse only the responsible action. Preserve unrelated new code.

Save the exact patch, base SHA, and changed paths. A temporary local commit is optional. Never add this patch to master or a publication branch.

Predict the result before the reverse run. Explain which defect the patch restores and why that action is wrong. Compare the new endpoint with the reverse-patched endpoint under the same test conditions. Include a valid old control when available. Remove the patch. Verify that the restored tree produces the new result again.

If no valid old control exists, use independent evidence to establish the restored defect. State which historical result differences remain unverified. The absence of an old control does not itself invalidate the experiment.

Check the specific result and mechanism that the patch should restore. Do not require an entire old trajectory when other accepted changes prevent that match. Explain which differences the experiment reproduces and what remains uncertain. A compile failure or a convenient movement toward old values supplies no causal proof. If the reverse patch is invalid or cannot isolate the behavior, record the limit. Keep the attribution unresolved unless other evidence suffices.

For example, consider a hypothetical counter that counts one delivered frame twice. A source commit removes the second increment, so its scalar and chart decrease. A temporary reverse patch restores that increment and the excess count. An event trace shows one delivery with two increments, which explains why the reverse action is wrong. This supports the correction even though the lower count can appear worse in a chart.

## Expose progress and review decisions

Create a persistent review report before the first test. Present the selected history with links to each commit's baseline changes, artifacts, and explanation. Use an available interactive UI for the same records. Otherwise, publish the report path. Update the report at each completed comparison. Do not claim UI controls or background execution that the environment does not provide.

Keep investigation state separate from human acceptance. Mark untested commits explicitly. Mark a commit unchanged only within its executed scope. Store each human decision in its attribution record against exact evidence and candidate revisions. Derive the index and baseline chain views from those records.

A material change to the candidate, source patch, evidence, scope, or correctness claim invalidates the affected acceptance. Editorial corrections preserve acceptance when those facts remain unchanged. Preserve earlier decisions in the attribution record's history.

The agent can prepare later candidates within the agreed work limit while review continues. Keep candidates that depend on pending decisions provisional. If a decision rejects a prerequisite, identify every dependent candidate. Preserve their artifacts, but exclude them from the accepted sequence until review resolves the dependency. Silence is not acceptance. Acceptance of an explanation does not itself authorize a push.

At each checkpoint, show examined commits, explained differences, accepted differences, unresolved items, and the next bounded action. Keep these counts separate. Do not report completion from a percentage estimate alone.

## Reconcile and prepare publication

Maintain an ordered chain of candidate baselines for both statistics and charts. Identify each transition by source cause, predecessor baseline, new baseline, evidence, and decision. Keep transient differences even when a later commit restores the initial value. Group rows only when one mechanism explains every row. Retain the full row list.

Compare the accumulated candidates with a fresh scoped result at the pinned final source SHA. Verify all reviewed cases and affected interactions. Account for every final file and result difference. Include deletions in that account. Resolve unexplained differences, invalid decisions, and rejected dependencies before publication.

A detected regression blocks the affected update. Do not conceal it through a baseline replacement.

Prefer publication only to the separate statistics and media repositories. Preserve source master and its history. Prepare candidate commits and descriptions that map every baseline change to its source SHA or minimal source set. A temporary sub-hunk experiment can establish attribution without a source amendment. If the result needs a production fix, report that separate task. Keep this review within its authorized scope.

Apply the current project procedure before replacement of accepted baselines or publication. Present exact repositories, revisions, paths, candidate differences, and their attribution for any required approval.

After an authorized update, rerun the same scoped tests. Record their actual selection and results. Push only within current publication authorization. Verify remote revisions after a push. Keep statistics and chart publication status separate if only one succeeds.
