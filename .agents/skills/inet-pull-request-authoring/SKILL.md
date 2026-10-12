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

Before completion, read each message and description without the diff or conversation. Check whether its explanation connects the problem, cause, change, and result under the discovered prose guidance. Keep required evidence and review fields in their prescribed places. Apply the current message guidance to the subject and the distinction between behavior before and after the change. Select the comparison from the state of the work:

| State of the work | Required comparison |
| --- | --- |
| Existing commit | Compare the commit with its parent. |
| Uncommitted implementation | Compare the selected changes with their actual base. State which changes and base the comparison covers. |
| Proposed change | Verify current behavior from the available source and evidence. Label the new behavior as proposed. Identify its planned verification. |

For a later proposed commit, label the assumed effects of earlier proposed commits. Do not present those assumptions as verified current behavior. A reader must not need the diff to tell which version performs each action. Use the current project guidance's worked examples when the distinction between a message, description, and plan remains unclear.

## Audit existing artifacts

For each defect, cite the violated identifier from the active series guidance. Identify the commit, message, hunk, or missing description section that establishes the defect. Give a concrete correction. Distinguish a violation from missing evidence and from an open question.

Use the current review procedure's explanation and report order. Retain a result for every applicable requirement, with its evidence and any gaps or approvals.

Do not substitute a pull-request-level summary or passing final tree for the active per-commit requirements.
