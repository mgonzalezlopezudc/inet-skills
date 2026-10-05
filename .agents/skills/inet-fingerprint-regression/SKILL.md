---
name: inet-fingerprint-regression
description: Diagnose INET fingerprint regression tests. Use for test execution, mismatch analysis, expected changes, or updates with evidence. Distinguish harmless simulation-event changes from behavioral regressions.
---

# INET fingerprint regression

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to find the active checkout's test guidance.
Read what a fingerprint establishes.
Determine the required test scope.
Check approval requirements before any recorded expectation changes.
This skill supplies the filtered runner procedure and the search for the first divergence.

After compiled INET source or generated-code inputs change, consult the discovered build guidance.
Select the required mode, freshness check, working directory, and build command.
This example applies when that guidance selects debug mode:

```sh
make MODE=debug -j$(nproc)
```

For that debug-mode example, run the wrapper from `tests/fingerprint`:

```sh
./fingerprinttest -d -m '<directly-related-regex>' -f 'tplx' -f '~tNl' -f '~tND'
```

The working directory is mandatory because default CSV expansion occurs before the wrapper's
directory option. Treat `Ran 0 tests` or `NO TESTS RAN` as invocation failure. Translate the
canonical test selection into `-m`/`-x` filters.
Never invoke this wrapper without a selection filter.
Use the build mode required by the active project guidance.
Record the mode with the run.

For a mismatch:

1. Record the test, configuration, run/seed, old/new fingerprints, and first mismatch.
2. Check expected changes to event ordering, timing, packets/tags, random streams, recordings, or topology.
3. Use logs, event logs, captures, or results to explain the first divergence.
4. If the divergence is accepted, follow the canonical baseline procedure.
5. Rerun only the same directly related fingerprint tests.

Keep the selected runner and library modes consistent within this invocation. Apply the comparison and
evidence rules discovered from the project entry point; any execution failure or zero-test
run remains incomplete tool output.

For a machine-readable handoff, preserve the raw runner output.
Use the skill-suite adapter `.agents/scripts/normalize_verification.py --runner fingerprint`.
Supply the exact command, working directory, mode, selector, configuration, run, seed, exit code, and artifacts.
Set changed-result expectation and approval from recorded facts.
The adapter leaves `UPDATE` or `INSERT` as `INCONCLUSIVE`.
It does not decide whether the new baseline is correct.
