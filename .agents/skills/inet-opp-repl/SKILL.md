---
name: inet-opp-repl
description: Run and normalize scoped opp_repl verification for INET workflows. Use to discover the active opp_repl interface, map changed paths through dependency data to configurations, distinguish test and baseline-update result semantics, and emit the shared verification envelope; use branch cleanup or rebase skills for history mutation and authorization.
---

# INET opp_repl verification

Own the shared `opp_repl` mechanics used by history and comparison workflows. The calling skill owns
the behavior claim, controls, approval gates, and correctness interpretation.

Choose the test category under `doc/project/rule/testing.md` and the directly related scope under
`TR-FOCUSED-EVIDENCE`. Read [workflow-contract.md](references/workflow-contract.md) before the first
invocation in a workflow.

For repeated history verification, read [incremental-builds.md](references/incremental-builds.md)
before the first build. Retain compatible artifacts in reusable worktrees and build incrementally;
fresh evidence at each stage does not require a clean rebuild.

## Capability and command discovery

1. Verify `command -v opp_repl` in the active environment and record the resolved executable.
2. Inspect the installed command/API help and the workflow's checked-in `.opp` entrypoints. Do not
   assume function names, keyword arguments, or result stores from another `opp_repl` version.
3. Resolve the active simulation project and build mode. Agent-run INET verification uses debug mode
   when required by `AGENTS.md`.
4. If the executable, required entrypoint, dependency store, or selected test data is unavailable,
   invoke the adapter with `--not-run-reason '<missing capability>'` and return `NOT_RUN`; do not
   improvise an unscoped substitute.

## Dependency mapping and scope

Use the active `dependency.json` and checked-out NED/package/feature graph to map:

```text
changed paths or commits -> NED packages -> features -> simulation configurations
```

Record the mapping evidence and select only directly related configurations, test types, runs or
seeds, and result ingredients. A missing mapping is a coverage gap. It does not justify an unrelated
full-suite run.

The calling workflow supplies the comparison controls and any union rule. Keep build mode,
configuration, run, seed, time limit, and result ingredients like-for-like across those controls.

## Result facts

- Test runners: `PASS` means the selected test reported its expected result; `FAIL` means it ran and
  reported a mismatch; `ERROR` means build/runner/simulation failure; zero executed cases is
  `NOT_RUN`.
- Update runners: `KEEP` records no baseline movement; `INSERT` and `UPDATE` record changed
  expectations; `ERROR` records a failed update. `INSERT` or `UPDATE` is not proof that the new value
  is correct and never supplies baseline approval.

For a machine-readable handoff, use the skill-suite
`.agents/scripts/normalize_verification.py --runner opp_repl` adapter. Supply command, working directory,
mode, selector, configuration, run, seed, exit code, artifacts, flaky status, and recorded
changed-result expectation/approval. The adapter normalizes facts to schema v1 and intentionally
does not judge correctness.

## Boundaries

Use `inet-fingerprint-regression` for fingerprint-specific first-divergence and baseline reasoning,
and the result skills for quantitative scalar/vector interpretation. Use `inet-branch-cleanup` or
`inet-branch-rebase` for branch construction, immutable refs, recovery, and human approval gates.

Return the resolved interface, dependency mapping, exact scoped invocation, normalized envelope,
raw artifacts, and any unavailable capability or coverage gap.
