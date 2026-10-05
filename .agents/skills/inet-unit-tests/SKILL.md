---
name: inet-unit-tests
description: Build INET and run focused unit or module tests in this repository. Use when asked to build for, execute, filter, diagnose, or report INET C++ unit tests or OMNeT++ module tests, including IEEE 802.11 HE coverage.
---

# Build and run INET unit tests

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's test category, scope, freshness, and gate obligations. This skill adds filtered
runner mechanics.

Run from the repository root with `inet_run_unit_tests`; do not infer a runner from another project.

Select freshness requirements and build mode from the current project guidance.
This example shows a build and a test when that guidance selects debug mode:

```sh
make MODE=debug -j$(nproc)
inet_run_unit_tests -m debug -f '<regex>'
```

Use the build mode required by the active project guidance and record it with the runner. The test
runner builds selected test executables but does not
rebuild the INET library. Apply the discovered freshness procedure to test definitions and compiled support inputs.

`-f` accepts one regex. Combine groups with alternation and quote it:

```sh
inet_run_unit_tests -m debug -f '(First|Second|Third).*\.test'
```

For module tests, use the same selected mode and an explicit filter.
This example uses debug mode:

```sh
inet_run_module_tests -m debug -f '<directly-related-filter>'
```

The runner invocation must carry an explicit `-f` regex for the set selected under the canonical
test rule. When piping through `tee`, preserve the runner's exit status with `pipefail`.

Classify the first failure as INET-library build, test-executable build, runner/setup, or test
assertion. Record the executed-case count and the failing case; a zero-case selection is `NOT_RUN`,
and a setup failure provides no evidence about the behavior under test.

For a machine-readable handoff, preserve the raw runner output and normalize it with the skill-suite
`.agents/scripts/normalize_verification.py --runner unit` or `--runner module` adapter. Supply the exact
command, working directory, selected build mode, filter, exit code, and artifact paths. The v1 envelope
uses `NOT_RUN` for a zero-test selection and records facts only; interpret the cause here, not in the
adapter.
