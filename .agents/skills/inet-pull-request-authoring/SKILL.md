---
name: inet-pull-request-authoring
description: Plan, write, or audit reviewable INET commits and pull requests. Use for commit boundaries, series order, commit messages, and pull request descriptions; do not use alone to reconstruct branch history or to review implementation correctness.
---

# INET pull request authoring

Read `doc/project/rule/pull-request.md` in the active INET checkout before planning, authoring, or
auditing commits or a pull request. It is the sole authority for `PR-*` policy. Use
`doc/project/guide/review-a-pull-request.md` for an existing series and
`doc/project/guide/contribute-a-change.md` when preparing a new change.

This skill adds planning and reporting structure. It does not reconstruct history: route requests
to split, merge, reorder, or re-author existing commits through `inet-branch-cleanup`.

## Establish the review surface

Determine the target branch and exact review surface. For existing history, preserve both the whole
branch diff and the per-commit diffs/messages as evidence. For an uncommitted change, inventory the
independent decisions and dependencies before proposing boundaries.

Keep evidence scoped to the requested change. Do not create commits, change baselines, publish a
pull request, or otherwise mutate the repository unless the user requested that mutation. Resolve
baselines through `doc/project/guide/change-a-baseline.md` and architecture/sealing disclosures
through the documents referenced by the applicable `PR-*` rule.

## Plan or author the series

Apply the canonical policy at all four levels: commit content, series structure, messages, and the
pull-request description.

For a proposed series, provide each commit's:

- subject;
- single decision and rationale;
- dependency on earlier commits;
- expected file or component surface;
- directly applicable build and test evidence;
- expected behavior or baseline effect.

The proposed fields are an output schema, not a second policy. Derive their contents and ordering
from the applicable `PR-*` identifiers, and cite those identifiers in an audit.

## Audit existing artifacts

Report only evidence-backed results. For each defect, cite the violated `PR-*` identifier, point to
the commit, message, hunk, or missing description section that establishes it, and give a concrete
correction direction. Distinguish a violation from missing evidence and from an open question.

Finish with a concise result for every applicable `PR-*` identifier, followed by missing evidence or
approvals.

Do not substitute a pull-request-level summary or passing final tree for the canonical per-commit
requirements.
