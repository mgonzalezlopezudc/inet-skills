# Persistent record for baseline review

Use the project report location when the current procedure defines one. Otherwise, use a durable directory outside experiment outputs and accepted baseline paths. Keep the report and artifacts available across stages. Follow any required project report format. The fields below support causal review and resumption. They do not replace project policy.

## Review header

Record these inputs before execution:

- The review identifier, report path, and source repository path.
- Full start and end SHAs, selected history, merge parents, and omitted history.
- Statistics and media repository paths, initial SHAs, local changes, and source compatibility controls.
- Test scope, configurations, actual runs, seeds, duration, build mode, and tool versions.
- Current stage boundary, time or run limit, continuation authority, and publication authority.
- Worktrees, isolated candidate paths, logs, artifacts, and current project guidance sources.

For each build workspace, record the last successful source tree and build configuration. Keep its build command, status, and log with the experiment record. Record artifact reuse or the reason for invalidation when the workspace changes state.

## Baseline inventory fields

The procedure and table layout belong to [baseline-inventory.md](baseline-inventory.md). Store these fields during inventory:

- Requested INET area, selected cases, selection evidence, and exclusions.
- Pinned INET source end, baseline repository revisions, local changes, and committed file identities.
- Grouped baseline tables with full commit IDs and author and committer timestamps in the stored data.
- Documented source origins with their evidence, or explicit unknown origins.
- Recovery limit, work consumed, sources checked, and unresolved items at the checkpoint.
- Proposed oldest source start, ancestry evidence, and any range exclusions.

Add control revisions, tested conditions, and comparison outcomes when experiments execute. Keep these results separate from the historical origin fields.

## History index

Create one row for every selected commit. Link each row to its attribution records. Use full SHAs in the stored record. The display can use short SHAs if they are unambiguous.

| Commit, original subject, and author date | Comparison parent | Investigation state | Attribution records |
| --- | --- | --- | --- |
| Source SHA, subject, and date | Parent SHA | untested / partial / unchanged in tested scope / changed / blocked | Links to each baseline change |

Derive any decision summary from the linked attribution records. A commit can contain both accepted and rejected changes. Keep those decisions separate.

A set of commits can share an attribution record when individual execution is impossible. Keep each commit visible in the index. Name the exact set and the failed smaller controls. A partial source patch belongs to an experiment record, not to rewritten source history.

## Attribution record

Assign a stable identifier to each distinct cause. Record these fields:

1. **Identity:** source SHA or exact source set, comparison endpoint, relevant paths, and source hunks.
2. **Scope:** affected statistics or charts, exact case identities, runs, units, result names, and chart identifiers.
3. **Baseline transition:** predecessor candidate or initial revision, new candidate, and artifact hashes or immutable revisions.
4. **Observed difference:** old and new values or images, difference artifacts, additions, deletions, and unchanged controls.
5. **Mechanism:** initial condition, trigger, responsible component, old action, new action, and observed data change.
6. **Correctness basis:** requirement, calculation, direct observation, or other evidence independent of the proposed baseline.
7. **Minimality:** tested smaller scopes, failed endpoints, dependencies, and limits of the attribution.
8. **Experiment:** commands, source tree identity, patch identity, environment, exit statuses, actual selection, and artifact paths.
9. **Reverse control (only for reverse experiments):** predicted effect, exact patch, observed effect, restored forward control, and available old control.
10. **Limits:** unresolved causes, result scope, environment effects, and unverified claims.
11. **Review:** the authoritative decision history, as specified below.
12. **Dependencies:** prerequisite records and later candidates that depend on this record.

The explanation must stand alone. Artifact links support it. An attachment list does not explain the mechanism or correctness.

For a relative numerical difference, record its formula. Treat a zero old value explicitly. Do not report a finite percentage without a valid definition. Distinguish an absent result from zero. For chart changes, distinguish input data differences from export differences.

## Candidate chain

Maintain a separate ordered chain for each baseline repository. Connect records that share one source cause across both chains.

| Transition | Attribution record | Predecessor | Candidate |
| --- | --- | --- | --- |
| Stable identifier | Link to the cause and its evidence | Initial baseline or prior candidate | Immutable artifact or tree |

Derive decisions and dependencies from the linked attribution records. Do not maintain separate copies in the candidate chains.

When two changes cancel numerically, retain both transitions. When changes interact, retain a joint record. Explain why separate effects do not compose. A later candidate can depend on a pending candidate, but the accepted chain cannot contain an unresolved prerequisite.

## Decisions and progress

Each attribution record owns its append-only decision history. Record evidence revision, candidate identity, human decision, reason, time, and source in that history. Derive the current decision from the latest applicable entry. Do not copy decision state into the index or candidate chains. Preserve a rejected candidate's evidence. Do not infer a decision from an absent reply or an agent's correctness assessment.

When a material change invalidates acceptance, append an invalidation entry. Mark the affected revision stale until a new human decision applies. Editorial corrections do not require another decision when the candidate, source patch, evidence, scope, and correctness claim remain unchanged.

If an interactive UI supports decisions, use the same stable record identifiers and evidence revisions. Persist decisions outside transient UI state. If the UI is unavailable, record explicit human decisions from the supported channel. Do not add approval controls that only change a display without a durable decision record.

Update progress after each completed comparison. Show these counts separately:

- Commits examined and commits still untested.
- Baseline differences with causal explanations.
- Baseline differences with human acceptance.
- Rejected, stale, blocked, and unresolved records.
- Work consumed against the agreed limit.

At a checkpoint, record the last completed comparison and the next exact action. Include work that can continue under current authority. Pause at the agreed limit even if some decisions remain pending. A new stage needs an explicit work limit or current authority that defines it.

## Final reconciliation

Record the fresh final-source comparison, its scope, and the candidate chain it validates. Map every changed baseline path to an accepted attribution record. Account for transient changes that leave no final diff. State any untested history or cases. Do not present partial coverage as complete.

Record candidate baseline commits separately from source commits. Include the source master revision before and after review. For publication, record the approved scope, post-update test results, pushed baseline revisions, verified remote revisions, and any incomplete repository publication.
