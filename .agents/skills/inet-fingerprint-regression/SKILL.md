---
name: inet-fingerprint-regression
description: Diagnose and manage INET fingerprint regression tests. Use to run fingerprint tests, interpret fingerprint mismatches, decide whether changed fingerprints are expected, update fingerprints with evidence, or distinguish harmless simulation-event changes from behavioral regressions.
---

# INET fingerprint regression

A changed fingerprint means the simulation trajectory changed; it is not a fix or automatically harmless.

After compiled INET source or generated-code inputs change, build debug mode from the repository root:

```sh
make MODE=debug -j$(nproc)
```

Then run the wrapper from `tests/fingerprint`:

```sh
./fingerprinttest -d -f 'tplx' -f '~tNl' -f '~tND'
```

The working directory is mandatory because default CSV expansion occurs before the wrapper's directory option. Treat `Ran 0 tests` or `NO TESTS RAN` as invocation failure. Use `-m`/`-x` filters for a focused selection; use the unfiltered command for the final suite. Release mode or `tyf` coverage must be requested or justified separately.

For a mismatch:

1. Record the test, configuration, run/seed, old/new fingerprints, and first mismatch.
2. Check expected changes to event ordering, timing, packets/tags, random streams, recordings, or topology.
3. Use logs, event logs, captures, or results to explain the first divergence.
4. Update CSV expectations only after the change is accepted and the user explicitly approves it.
5. Rerun the same focused test, then any required final suite.

Keep debug runner and libraries consistent. Compare identical binaries, NED paths, seeds, overrides, and source state unless the difference is intentional. Any mismatch, execution failure, unavailable required suite, or zero-test run is incomplete validation.
