---
name: inet-opp-repl
description: Run scoped opp_repl verification for INET workflows. Use for interface discovery, dependency-based configuration selection, and the shared verification record. Distinguish test results from baseline-update results. Use branch cleanup or rebase skills for history changes and authorization.
---

# INET opp_repl verification

Use this skill for the shared `opp_repl` procedures in history and comparison workflows. The workflow that requests verification owns the behavior claim, controls, approval gates, and correctness interpretation.

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the active checkout's test category and directly related scope. Read [workflow-contract.md](references/workflow-contract.md) before the first invocation in a workflow.

For repeated history verification, read [incremental-builds.md](references/incremental-builds.md) before the first build. Retain compatible artifacts in reusable worktrees. Build incrementally. Fresh evidence at each stage does not require a clean rebuild.

## Capability and command discovery

1. Verify `command -v opp_repl` in the active environment. Record the resolved executable.
2. Inspect the installed command/API help and the loaded `.opp` entrypoints. Check project descriptions supplied with `--load @opp` when no local entrypoint exists. Do not assume interfaces or stores from another version.
3. Resolve the active simulation project and build mode from the active project guidance. Record the selected mode.
4. If an executable, required option, entrypoint, required dependency store, or selected data is absent, report `NOT_RUN` through the adapter. Supply `--not-run-reason '<missing capability>'`. Do not substitute an unscoped run.

## Dependency mapping and scope

For selection from changed paths, use the active `dependency.json` and the checked-out NED/package/feature graph to map:

```text
changed paths or commits -> NED packages -> features -> simulation configurations
```

Record the mapping evidence. Select only directly related configurations, test types, runs or seeds, and result ingredients. A missing mapping is a coverage gap. It does not justify an unrelated full-suite run.

For explicitly named configurations, record the direct selection and its relation to the behavior claim. A fingerprint run does not inherently require dependency-based selection.

The calling workflow supplies the comparison controls and any union rule. Keep build mode, configuration, run, seed, time limit, and result ingredients like-for-like across those controls.

## Result facts

| Runner | Result | Meaning |
| --- | --- | --- |
| Test | `PASS` | The selected test reported success. Compare this result with its recorded expectation. |
| Test | `FAIL` | The selected test ran and reported a mismatch. |
| Test | `ERROR` | The build, runner, or simulation failed. |
| Test | `NOT_RUN` | No cases executed. |
| Update | `KEEP` | The baseline did not change. |
| Update | `INSERT`, `UPDATE` | The operation changed recorded expectations. |
| Update | `ERROR` | The update failed. |

An `INSERT` or `UPDATE` result does not prove that the new value is correct. It never supplies baseline approval.

Keep the observed result separate from whether the runner accepts it. Some cases expect `FAIL` or `ERROR`. Confirm that the cause matches the expected behavior before you use such a result as evidence.

For a machine-readable handoff, use the skill-suite `.agents/scripts/normalize_verification.py --runner opp_repl` adapter. Supply command, working directory, mode, selector, configuration, run, seed, exit code, artifacts, flaky status, and recorded changed-result expectation/approval. The adapter normalizes facts to schema v1 and intentionally does not judge correctness.

## Boundaries

Use `inet-fingerprint-regression` for fingerprint-specific first-divergence and baseline reasoning, and the result skills for quantitative scalar/vector interpretation. Use `inet-branch-cleanup` or `inet-branch-rebase` for branch construction, immutable refs, recovery, and human approval gates.

Return the resolved interface, scope evidence, exact scoped invocation, normalized verification record, and raw artifacts. Include the dependency mapping when it supplies the selection. Report any unavailable capability or coverage gap.
