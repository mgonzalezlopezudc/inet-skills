---
name: inet-architectural-requirements
description: Apply the active INET checkout's architecture, naming, exception, enforcement, and source-protection guidance to C++, NED, MSG, configuration, build, or package changes under src/inet; use for design, implementation, refactoring, audits, reviews, or sealing decisions.
---

# INET architectural requirements

Start with the shared [project-guidance-discovery.md](../../references/project-guidance-discovery.md)
and read the active checkout's project entry point. Follow the route for the requested change and
apply the current architecture, naming, audit, enforcement, and source-protection guidance. Do not
use policy copies from this package or rely on remembered document names and identifiers.

## Route the task

Use the project map to find the current guidance for:

- a source change, including ownership, composition, contracts, lifecycle, packet representation,
  observability, configuration, and naming;
- a pull-request or branch review, including its review checklists and commit-series requirements;
- an audit or sealing task, including protection status, exception ledgers, and audit evidence.

If a route is absent, search the current project documentation for the task terms and report the
search. Preserve the project documents' current terminology in the report instead of translating it
into a fixed skill-side checklist.

The technical routing index below identifies useful investigation dimensions. It is a task aid, not
a copy of project requirements; the active project guidance decides which checks apply.

| Change | Inspect the implementation for |
| --- | --- |
| New NED module or compound node | composition, pluggability, ownership, configuration, naming, and observable truth |
| New protocol or application | integration boundaries, registries/dispatch, socket contracts, and provider outcomes |
| Serializer, dissector, `.msg`, packet, chunk, or tag | wire/model duality, field ownership, metadata flow, error paths, and round trips |
| Lifecycle operation | stage ordering, inherited stage count, start/stop symmetry, and terminal paths |
| Queue, scheduler, shaper, or cross-module coordination | role ownership, direct interaction, bounded progress, and streaming behavior |
| Signal, statistic, or visualization | source-of-truth observability, units, event boundaries, and separation from protocol logic |
| Configuration, parameter, dependency, include, build, or feature | effective precedence, declared dependencies, feature isolation, and reproducible builds |
| Test or recorded expectation | claim-to-test-category match, production-path reachability, determinism, and baseline provenance |
| IEEE 802.11 frame, MAC, PHY, management, or capability behavior | frame representation, state ownership, negotiated gates, timing, and standards traceability |

Use `inet-code-review` as well when an independent correctness review is requested. Keep semantic
findings separate from project checklist findings and avoid reporting one defect twice.

## Run project enforcement

Use the project map and its current contributor or review route to discover the required commands,
working directory, scopes, supported modes, and exit-status meanings. Confirm each command exists in
the active checkout before invoking it. Do not substitute a similarly named checker from this skill
package, and do not infer that a missing command authorizes the change.

For each selected gate, record the discovered command, scope, mode, exit status, findings, ledger
disposition, required approval, and unresolved capability gap. A protected path or unit remains a
hard stop until the active guidance grants the required permission; a checker result cannot grant
that permission.

## Report

Return the reviewed scope, project guidance sources discovered, technical dimensions inspected,
commands and statuses, findings and ledger dispositions, required approvals, and final compliance
status. State explicitly when required guidance or an executable gate was unavailable.
