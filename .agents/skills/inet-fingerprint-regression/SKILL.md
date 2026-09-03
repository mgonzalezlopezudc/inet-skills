---
name: inet-fingerprint-regression
description: Diagnose and manage INET fingerprint regression tests. Use to run fingerprint tests, interpret fingerprint mismatches, decide whether changed fingerprints are expected, update fingerprints with evidence, or distinguish harmless simulation-event changes from behavioral regressions.
---

# INET fingerprint regression

Read `doc/project/design/test-anatomy.md` for what a fingerprint establishes,
`doc/project/rule/testing.md` for scope, and `doc/project/guide/change-a-baseline.md` before changing
recorded expectations. This skill adds the filtered runner and first-divergence workflow.

After compiled INET source or generated-code inputs change, build debug mode from the repository root:

```sh
make MODE=debug -j$(nproc)
```

Then run the wrapper from `tests/fingerprint`:

```sh
./fingerprinttest -d -m '<directly-related-regex>' -f 'tplx' -f '~tNl' -f '~tND'
```

The working directory is mandatory because default CSV expansion occurs before the wrapper's
directory option. Treat `Ran 0 tests` or `NO TESTS RAN` as invocation failure. Translate the
canonical test selection into `-m`/`-x` filters and never invoke this wrapper without a selection
filter. The agent-run command uses `-d` under the debug execution constraint in `AGENTS.md`; it does
not satisfy the contributor's release-mode gate.

For a mismatch:

1. Record the test, configuration, run/seed, old/new fingerprints, and first mismatch.
2. Check expected changes to event ordering, timing, packets/tags, random streams, recordings, or topology.
3. Use logs, event logs, captures, or results to explain the first divergence.
4. If the divergence is accepted, follow the canonical baseline procedure.
5. Rerun only the same directly related fingerprint tests.

Keep the debug runner and libraries consistent within this invocation. Apply the comparison and
evidence rules in `doc/project/guide/diagnose-a-simulation.md`; any execution failure or zero-test
run remains incomplete tool output.

For a machine-readable handoff, preserve the raw runner output and use the skill-suite
`.agents/scripts/normalize_verification.py --runner fingerprint` adapter with the exact command, working
directory, mode, selector, configuration, run, seed, exit code, and artifacts. Set changed-result
expectation and approval from recorded facts; the adapter deliberately leaves `UPDATE` or `INSERT`
as `INCONCLUSIVE` and does not decide whether the new baseline is correct.
