# INET `opp_repl` rebase contract

Use `opp_repl` to decide whether a group remains correct as upstream history is introduced. A safe
point means that the selected evidence contains no unexplained regression; it does not require raw
equality when the upstream checkpoint intentionally changes behavior.

## Choose and record the scope

Choose the test category under `doc/project/rule/testing.md`. Record the requested test types in
priority order. Unless the rebase specifies otherwise, use fingerprint tests first, statistical
tests second, and run number 0 only. Add chart tests or more runs only when the task opts in or the
directly related contract requires them.

Use `dependency.json` to map:

```text
changed commits and paths -> NED packages -> features -> simulation configurations
```

Derive the stage scope from the topology:

- for an individual `parallel-end` or `lockstep` group, use the union of the current upstream
  checkpoint transition and that group's mappings;
- for serial group `Gi`, use the union of the checkpoint transition and accumulated groups
  `G1..Gi`;
- for a combined lockstep checkpoint or final parallel integration, use the union of the checkpoint
  transition and every current group and cross-cutting adaptation mapping.

If no directly related case can be identified, report the coverage gap; an unrelated broad suite is
not substitute evidence.

Run one scoped invocation per attempt with the matching build folded into it. Follow the debug-mode
execution constraints in `AGENTS.md`.

- **`ERROR`** — the build or execution failed, or the selection ran no valid test.
- **`FAIL`** — the check ran but exposed an unexplained difference or violated expectation.
- **`PASS`** — the build succeeded and every selected result matched or had an established,
  accepted explanation.

Record the working directory, exact command, build mode, configuration, run or seed, filter, exit
status, and decisive artifact paths.

## Maintain comparison controls

Use these controls when diagnosing a failed or surprising attempt:

- **topic** — the original topic on its original base, establishing the pre-rebase topic behavior;
- **stage anchor** — the exact parent used for the attempt, including the predecessor group's
  same-stage safe point for a later serial group;
- **plain upstream stage** — behavior introduced by upstream without the topic group;
- **previous safe point** — the immediately preceding promoted same-group state, or previous
  combined integration safe point, isolating the current stage transition.

At `stage-0`, the stage anchor and plain upstream may both resolve to `base`, and a previous
same-group point does not yet exist. Record this explicitly; do not fabricate duplicate runs merely
to claim four distinct results.

Establish or reuse a valid plain-upstream result before blaming a group for a stage failure. Compare
like-for-like configurations, runs, seeds, build modes, and result ingredients. Explain upstream-only
movement separately from topic/upstream interaction and from an adaptation's effect.

Detailed result artifacts may be temporary. Before discarding them, preserve the exact invocation,
first decisive divergence, causal explanation, exit status, and any durable artifact path in the
logbook.

## Baseline changes

Diagnostic result comparison does not authorize rewriting tracked expectations. Follow
`doc/project/guide/change-a-baseline.md`, including its explicit approval requirement, before any
baseline update. Put an approved update in the causal source or adaptation commit; use a standalone
baseline commit only when no single source commit caused the movement.

Never re-record a baseline merely to promote a rebase attempt. Re-run the same focused check after
an approved update and record which behavior moved, why the new expectation is correct, and which
unrelated configurations remained unchanged.

## Final acceptance

Run the selected contract across every configuration mapped to any current group, relevant upstream
checkpoint, or accepted adaptation, using run 0 or the explicitly approved wider set. “Full” means
full coverage of this directly related contract; retain explicit filters and do not expand into
unrelated INET suites.

Run the same comparable contract on the clean target and use the original topic and pinned plain
upstream as controls where useful. Completion requires an explanation for every material delta: the
upstream change that causes it, the intended topic effect it preserves, or the accepted adaptation
that resolves their interaction.

Before the final union run, check every commit in the clean target series in order using the build
and directly applicable tests required by `PR-SERIES-BUILDS` and `PR-SERIES-ORDER`. Record a result
for each commit. Do not treat a passing branch tip as evidence that an earlier commit was usable on
its own, and do not leave a knowingly broken intermediate commit for a later adaptation to repair.
