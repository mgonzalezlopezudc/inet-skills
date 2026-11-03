---
name: inet-pull-request-authoring
description: Plan, write, or audit reviewable INET commits and pull requests. Use for commit boundaries, series order, commit messages, and pull request descriptions. Do not use alone for branch reconstruction or implementation correctness review.
---

# INET pull request authoring

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) before a commit or pull request task. Follow the active checkout's current series, review, and contribution routes. Read its documentation route for the audience and explanatory style of commit messages and PR descriptions. Those routes provide the authority for project policy.

This skill adds planning and reporting structure. It does not reconstruct history: route fixed-base requests to split, merge, reorder, or re-author existing commits through `inet-branch-cleanup`, and route high-risk `opp_repl`-backed rebases onto changed upstream history through `inet-branch-rebase`.

## Establish the review surface

Determine the target branch and exact review surface. For existing history, preserve both the whole branch diff and the per-commit diffs/messages as evidence. For an uncommitted change, inventory the independent decisions and dependencies before you propose boundaries.

Keep evidence scoped to the requested change. Do not create commits, change baselines, publish a pull request, or otherwise mutate the repository unless the user requested that mutation. Resolve baselines and architecture/sealing disclosures through the current project routes discovered above.

## Plan or author the series

Apply the active project policy at all four levels: commit content, series structure, messages, and the pull-request description.

For a proposed series, provide each commit's:

- subject;
- single decision and rationale;
- dependency on earlier commits;
- expected file or component surface;
- planned verification, with executed evidence identified separately;
- expected behavior or baseline effect.

The proposed fields are an output schema, not a second policy. Derive their contents and ordering from the applicable current guidance. Cite its identifiers in an audit when that guidance uses them.

For an implementation plan, assess commit boundaries and artifact assignments under the discovered series and test requirements. For an implemented series, compare those assignments with the actual commits. Take required artifact content and any exclusions from the active checkout's rules.

Before completion, read each message and description without the diff or conversation. Check whether its explanation connects the problem, cause, change, and result under the discovered prose guidance. Keep required evidence and review fields in their prescribed places. Apply the current message guidance to the subject and the distinction between behavior before and after the change. Select the comparison from the state of the work:

| State of the work | Required comparison |
| --- | --- |
| Existing commit | Compare the commit with its parent. |
| Uncommitted implementation | Compare the selected changes with their actual base. State which changes and base the comparison covers. |
| Proposed change | Verify current behavior from the available source and evidence. Label the new behavior as proposed. Identify its planned verification. |

For a later proposed commit, label the assumed effects of earlier proposed commits. Do not present those assumptions as verified current behavior. A reader must not need the diff to tell which version performs each action. Use the current project guidance's worked examples when the distinction between a message, description, and plan remains unclear.

Check paragraph layout in the actual message text before a commit. Apply the discovered rules for line breaks and blank lines. Check the stored message after a commit. Do not let terminal display width determine paragraph layout.

## Write descriptions for human review

Write short PR descriptions that a human reviewer can easily understand. Keep the explanation complete without the diff or conversation. Explain the problem, resulting behavior, responsible component, mechanism, and relevant limits. Explain the mechanism before API names. Use a concrete scenario to connect the trigger, old result, changed action, and new result. Remove repeated facts and implementation details that do not help the reviewer assess the change.

For a PR, start with the problem and resulting behavior. Include as many diagrams as needed to explain the change clearly. Select diagrams that clarify a flow, interaction, or state change. Do not impose a fixed diagram count. Use Mermaid when the host supports it. Each diagram must agree with the source and the stated limits. Keep enough prose for the reader to understand what each diagram shows.

List all commits in review order with links and a short explanation of what each commit contributes. Explain each contribution instead of repeating its subject. Distinguish preparation, behavior changes, tests, and documentation. Where appropriate, name and link the protocol tests associated with each commit. Explain which behavior each test checks. Use a compact table or list that lets the reviewer connect each contribution to its tests. Preserve the parent comparison described below without repeating shared setup in every row.

Put detailed commands and execution records after the explanation, in a collapsible section when useful. Preserve the active project's required structure and evidence fields. Before completion, check that the summary explains the result and the commit list explains each contribution and its associated tests.

### Explain each protocol test against the parent

In both the PR description and the responsible commit's body, explain each protocol test through the same concrete scenario:

- Name the test and its input, initial condition, and required observation.
- Explain which component causes the parent to fail and which assertion or required event detects that failure.
- Explain the changed action and why the new commit satisfies that same assertion or event.
- State the relevant limits, including any behavior that the test does not establish.

Compare the responsible commit with its immediate parent, including earlier commits in the series. Use the responsible commit's fixture and expectations on both versions. The parent's older fixture can expect different behavior and therefore cannot establish the comparison. Distinguish separate changes that extend the same test.

Check fixture compatibility with the parent before claiming a behavioral failure. A missing API, test compilation error, or build failure does not demonstrate the claimed runtime defect. Describe any required fixture adaptation and its effect on the comparison. If the parent already passes, state that result and the test's role as a control or added coverage. Do not invent a parent failure.

For example, a hypothetical test supplies three MPDUs with a malformed middle delimiter. The parent returns one MPDU, so the assertion for two outputs fails. The new commit searches for the next valid delimiter and returns the first and final MPDUs. Their count and content satisfy the assertions. This test establishes extraction; it does not establish MAC acceptance.

Keep the causal explanation in the commit body. Put exact revisions, commands, modes, seeds, execution status, and logs in the PR evidence or its linked comparison record. Distinguish test expectations from observed results. Label source-based comparisons explicitly. State when fresh executions of the exact parent and commit remain unverified. Earlier runs on different revisions do not establish that exact comparison.

This description workflow does not authorize test execution, history changes, or publication. Follow the task's existing scope for those actions.

## Audit existing artifacts

For each defect, cite the violated identifier from the active series guidance. Identify the commit, message, hunk, or missing description section that establishes the defect. Give a concrete correction. Distinguish a violation from missing evidence and from an open question.

Use the current review procedure's explanation and report order. Retain a result for every applicable requirement, with its evidence and any gaps or approvals.

Do not substitute a pull-request-level summary or passing final tree for the active per-commit requirements.
