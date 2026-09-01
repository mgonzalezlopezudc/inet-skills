---
name: inet-pull-request-authoring
description: Plan, write, or audit reviewable INET commits and pull requests. Use for commit boundaries, series order, commit messages, and pull request descriptions; do not use alone to reconstruct branch history or to review implementation correctness.
---

# INET pull request authoring

Prepare a change so that its commits are independently reviewable and its pull request explains the complete change. Before deciding commit boundaries or order, writing or revising commit messages, drafting a pull request description, or auditing any of those artifacts, read [references/pull-requests.md](references/pull-requests.md) in full. Treat that document as the authoritative policy and identify its requirements by their stable `PR-*` identifiers.

This skill owns the normative policy for INET commit content, commit-series structure, commit messages, and pull-request content. It may propose a better series, but it does not define or execute the mechanics for reconstructing existing history. When the user asks to split, merge, reorder, or re-author existing commits on a new branch, use `inet-branch-cleanup`; that skill consumes this policy.

The copied reference preserves links relative to its original `doc/architecture/` location. When a `PR-REQ-ARCH` check needs the linked architecture, naming, exception-ledger, or sealing policy, read the current project documents through `inet-architectural-requirements`; do not alter the reference copy to redirect those links.

## Establish the review surface

Determine the target branch and the exact change being prepared or audited. When commits already exist, inspect both the complete branch diff and every individual commit diff and message; aggregate branch state cannot establish per-commit compliance. When planning an uncommitted change, identify its independent decisions, prerequisites, mechanical operations, moves, behavior-preserving preparation, behavior changes, expected-result updates, and unrelated work before proposing boundaries.

Keep evidence scoped to the requested change. Do not create commits, update expected results, publish a pull request, or otherwise mutate the repository unless the user requested that mutation. Route requested history reconstruction through `inet-branch-cleanup`. Preserve any repository-specific approval requirements, especially those governing fingerprints, sealed paths, and exception ledgers.

## Plan or author the series

Apply the reference at all four levels: commit content, commit-series structure, commit messages, and pull-request content.

For a proposed series, provide each commit's:

- subject;
- single decision and rationale;
- dependency on earlier commits;
- expected file or component surface;
- directly applicable build and test evidence;
- expected behavior or baseline effect.

Order prerequisites before their consumers and ensure the tree after every proposed commit is coherent and testable. Draft message bodies from the reason and observable context for the change, not by narrating the diff. Draft the pull request description with the topic and motivation, reading order when needed, exact test commands and outcomes, architectural surface, baseline updates, exception identifiers, and sealing permission required by the reference and repository policy.

## Audit existing artifacts

Evaluate each commit separately before evaluating the series and pull request as a whole. Report only evidence-backed results. For every defect, cite the violated `PR-*` identifier, point to the commit, message, hunk, or missing pull-request section that establishes it, and give a concrete correction direction. Distinguish a policy violation from missing evidence and from an open question.

Finish with a concise compliance summary covering:

- commit boundaries and per-commit consistency;
- dependency order and linearity;
- message subjects and bodies;
- pull-request topic, story, architecture disclosures, tests, baselines, and cleanliness;
- approvals or evidence still required.

Do not substitute a pull-request-level summary or passing final tree for the reference's per-commit requirements.
