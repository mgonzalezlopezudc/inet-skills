---
name: inet-architectural-requirements
description: Apply current INET architecture, naming, exception, enforcement, and source-protection guidance to changes under src/inet. Use for C++, NED, MSG, configuration, build, or package work. This covers design, implementation, refactoring, audits, reviews, and sealing decisions.
---

# INET architectural requirements

Start with [project-guidance-discovery.md](../../references/project-guidance-discovery.md).
Read the active checkout's project entry point.
Follow the route for the requested change.
Apply the current architecture, naming, audit, enforcement, and source-protection guidance.
Do not use policy copies from this package.
Do not rely on remembered document names and identifiers.

## Route the task

Use the project map to find the current guidance for:

- a source change, including ownership, composition, contracts, lifecycle, packet representation,
  observability, configuration, and naming;
- a pull-request or branch review, including its review checklists and commit-series requirements;
- an audit or sealing task, including protection status, exception ledgers, and audit evidence.

If a route is absent, search the current project documentation for the task terms.
Report the search.
Preserve the project documents' current terminology in the report.
Do not replace it with a fixed checklist from this skill.

The technical routing index below identifies useful investigation dimensions. It is a task aid, not
a copy of project requirements; the active project guidance decides which checks apply.

| Change | Inspect the implementation for |
| --- | --- |
| New NED module or compound node | Check composition, replaceable components, ownership, configuration, and names. Confirm that reported state matches actual state. |
| New protocol or application | Check integration boundaries, registration, dispatch, socket contracts, and provider outcomes. |
| Serializer, dissector, `.msg`, packet, chunk, or tag | Check how model fields map to protocol bytes. Inspect field ownership, metadata flow, error paths, and round trips. |
| Lifecycle operation | Check stage order, inherited stage count, paired start/stop behavior, and terminal paths. |
| Queue, scheduler, shaper, or cross-module coordination | Check role ownership, direct interaction, bounded progress, and streaming behavior. |
| Simulation signal, statistic, or visualization | Confirm that observations describe actual state with correct units and event boundaries. Keep observation code separate from protocol decisions. |
| Configuration, parameter, dependency, include, build, or feature | Check effective precedence, declared dependencies, feature isolation, and reproducible builds. |
| Test or recorded expectation | Match the behavior claim to the test category. Check production-path reachability, determinism, and the baseline's source. |
| IEEE 802.11 frame, MAC, PHY, management, or capability behavior | Check frame representation, state ownership, negotiated feature gates, timing, and the applicable standard. |

For example, a hypothetical model stores a timeout in seconds, but its protocol field uses milliseconds.
The review traces the conversion from model value to field bytes.
A round trip must preserve the permitted value at the protocol's resolution.

Use `inet-code-review` as well when an independent correctness review is requested. Keep semantic
findings separate from project checklist findings.
Report each defect once.

## Run project enforcement

Use the project map and its current contributor or review route to discover the required commands,
working directory, scopes, supported modes, and exit-status meanings. Confirm each command exists in
the active checkout before execution.
Do not substitute a similarly named checker from this skill package.
Do not infer that a missing command authorizes the change.

For each selected gate, record the command, scope, mode, exit status, findings, required approval, and unresolved capability gap.
Record how the applicable exception ledger addresses each finding.
A protected path or unit requires the permission specified by the active guidance.
A checker result cannot grant that permission.

## Report

Return the reviewed scope, guidance sources, technical checks, commands, and statuses.
Include findings, exception-ledger decisions, required approvals, and final compliance status.
State explicitly when required guidance or an executable gate was unavailable.
