---
name: inet-pull-request-authoring
description: Plan, write, or audit reviewable INET commits and pull requests. Use for commit boundaries, series order, commit messages, and pull request descriptions. Do not use alone for branch reconstruction or implementation correctness review.
---

# INET pull request authoring

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) before a commit or pull request task.
Follow the active checkout's current series, review, and contribution routes.
Those routes provide the authority for project policy.

This skill adds planning and reporting structure. It does not reconstruct history: route fixed-base
requests to split, merge, reorder, or re-author existing commits through `inet-branch-cleanup`, and
route high-risk `opp_repl`-backed rebases onto changed upstream history through
`inet-branch-rebase`.

## Establish the review surface

Determine the target branch and exact review surface. For existing history, preserve both the whole
branch diff and the per-commit diffs/messages as evidence. For an uncommitted change, inventory the
independent decisions and dependencies before you propose boundaries.

Keep evidence scoped to the requested change. Do not create commits, change baselines, publish a
pull request, or otherwise mutate the repository unless the user requested that mutation. Resolve
baselines and architecture/sealing disclosures through the current project routes discovered above.

## Plan or author the series

Apply the active project policy at all four levels: commit content, series structure, messages, and
the pull-request description.

For a proposed series, provide each commit's:

- subject;
- single decision and rationale;
- dependency on earlier commits;
- expected file or component surface;
- directly applicable build and test evidence;
- expected behavior or baseline effect.

The proposed fields are an output schema, not a second policy. Derive their contents and ordering
from the applicable current guidance.
Cite its identifiers in an audit when that guidance uses them.

## Audit existing artifacts

For each defect, cite the violated identifier from the active series guidance.
Identify the commit, message, hunk, or missing description section that establishes the defect.
Give a concrete correction.
Distinguish a violation from missing evidence and from an open question.

Finish with a concise result for every applicable requirement, followed by missing evidence or
approvals.

Do not substitute a pull-request-level summary or passing final tree for the active per-commit
requirements.
