---
name: inet-opp-repl
description: Run scoped opp_repl verification for INET workflows. Use for interface discovery, dependency-based configuration selection, and the shared verification record. Distinguish test results from baseline-update results. Use branch cleanup or rebase skills for history changes and authorization.
---

# INET opp_repl verification

Use this skill for the shared `opp_repl` procedures in history and comparison workflows.
The workflow that requests verification owns the behavior claim, controls, approval gates, and correctness interpretation.

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's test category and directly related scope. Read [workflow-contract.md](references/workflow-contract.md) before the first
invocation in a workflow.

For repeated history verification, read [incremental-builds.md](references/incremental-builds.md)
before the first build.
Retain compatible artifacts in reusable worktrees.
Build incrementally.
Fresh evidence at each stage does not require a clean rebuild.

## Capability and command discovery

1. Verify `command -v opp_repl` in the active environment.
   Record the resolved executable.
2. Inspect the installed command/API help and the workflow's checked-in `.opp` entrypoints. Do not
   assume function names, keyword arguments, or result stores from another `opp_repl` version.
3. Resolve the active simulation project and build mode from the active project guidance.
   Record the selected mode.
4. If the executable, required entrypoint, dependency store, or selected test data is unavailable,
   invoke the adapter with `--not-run-reason '<missing capability>'`.
   Return `NOT_RUN`.
   Do not improvise an unscoped substitute.

## Dependency mapping and scope

Use the active `dependency.json` and checked-out NED/package/feature graph to map:

```text
changed paths or commits -> NED packages -> features -> simulation configurations
```

Record the mapping evidence.
Select only directly related configurations, test types, runs or seeds, and result ingredients.
A missing mapping is a coverage gap.
It does not justify an unrelated
full-suite run.

The calling workflow supplies the comparison controls and any union rule. Keep build mode,
configuration, run, seed, time limit, and result ingredients like-for-like across those controls.

## Result facts

| Runner | Result | Meaning |
| --- | --- | --- |
| Test | `PASS` | The selected test reported its expected result. |
| Test | `FAIL` | The selected test ran and reported a mismatch. |
| Test | `ERROR` | The build, runner, or simulation failed. |
| Test | `NOT_RUN` | No cases executed. |
| Update | `KEEP` | The baseline did not change. |
| Update | `INSERT`, `UPDATE` | The operation changed recorded expectations. |
| Update | `ERROR` | The update failed. |

An `INSERT` or `UPDATE` result does not prove that the new value is correct.
It never supplies baseline approval.

For a machine-readable handoff, use the skill-suite
`.agents/scripts/normalize_verification.py --runner opp_repl` adapter. Supply command, working directory,
mode, selector, configuration, run, seed, exit code, artifacts, flaky status, and recorded
changed-result expectation/approval. The adapter normalizes facts to schema v1 and intentionally
does not judge correctness.

## Boundaries

Use `inet-fingerprint-regression` for fingerprint-specific first-divergence and baseline reasoning,
and the result skills for quantitative scalar/vector interpretation. Use `inet-branch-cleanup` or
`inet-branch-rebase` for branch construction, immutable refs, recovery, and human approval gates.

Return the resolved interface, dependency mapping, exact scoped invocation, normalized verification record, and raw artifacts.
Report any unavailable capability or coverage gap.
