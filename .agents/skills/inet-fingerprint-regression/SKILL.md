---
name: inet-fingerprint-regression
description: Diagnose and manage INET fingerprint regression tests. Use to run fingerprint tests, interpret fingerprint mismatches, decide whether changed fingerprints are expected, update fingerprints with evidence, or distinguish harmless simulation-event changes from behavioral regressions.
---

# INET fingerprint regression

Read `doc/project/design/test-anatomy.md` for what a fingerprint establishes and
`doc/project/guide/change-a-baseline.md` before changing recorded expectations. This skill adds the
filtered runner and first-divergence workflow.

After compiled INET source or generated-code inputs change, build debug mode from the repository root:

```sh
make MODE=debug -j$(nproc)
```

Then run the wrapper from `tests/fingerprint`:

```sh
./fingerprinttest -d -m '<directly-related-regex>' -f 'tplx' -f '~tNl' -f '~tND'
```

The working directory is mandatory because default CSV expansion occurs before the wrapper's directory option. Treat `Ran 0 tests` or `NO TESTS RAN` as invocation failure. Map each selected row to a changed path, symbol, or behavioral contract, and use `-m`/`-x` filters so only those directly related fingerprint tests run. Never run the wrapper without a test-selection filter or broaden it to an unrelated suite. If no row maps directly to the change, report the coverage gap instead of running the full set. Always use `-d`; release-mode fingerprint runs are prohibited.

For a mismatch:

1. Record the test, configuration, run/seed, old/new fingerprints, and first mismatch.
2. Check expected changes to event ordering, timing, packets/tags, random streams, recordings, or topology.
3. Use logs, event logs, captures, or results to explain the first divergence.
4. If the divergence is accepted, follow the canonical baseline procedure and any additional
   approval requirement in `AGENTS.md`.
5. Rerun only the same directly related fingerprint tests.

Keep debug runner and libraries consistent. Compare identical binaries, NED paths, seeds, overrides, and source state unless the difference is intentional. Any mismatch, execution failure, unavailable required suite, or zero-test run is incomplete validation.
