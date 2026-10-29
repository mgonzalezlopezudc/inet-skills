---
name: inet-unit-tests
description: Run focused INET C++ unit tests or OMNeT++ module tests. Use for the required build, test selection, execution, diagnosis, and result reports. This includes IEEE 802.11 HE coverage.
---

# Build and run INET unit tests

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the active checkout's test category, scope, freshness, and gate obligations. This skill adds filtered runner mechanics.

Run from the INET root with `opp_run_unit_tests`. Check the resolved executable and its `--help` output. Read the local `inet.opp` and unit/module workflows for the test folders, mode, and installation source. Load the local description with `--load . -p inet`. Use `--load @opp` only when the checkout supplies no project description.

Select freshness requirements and build mode from the current project guidance. This example shows a build and a test when that guidance selects debug mode:

```sh
opp_run_unit_tests --load . -p inet -m debug -f '<regex>'
```

Record the selected mode. The current runner builds the INET project by default and compiles selected test executables. Use `--no-build` only when the matching INET binaries are current. This option does not disable compilation of individual tests or required support libraries.

The `-f` option accepts one regex. Combine groups with alternation. Quote the expression:

```sh
opp_run_unit_tests --load . -p inet -m debug -f '(First|Second|Third).*\.test'
```

For focused module tests, use the same selected mode and an explicit filter. This example uses debug mode:

```sh
opp_run_module_tests --load . -p inet -m debug -f '<directly-related-filter>'
```

For focused verification, use an explicit `-f` regex for the selected tests. For a requested full unit or module suite, omit the filter. Keep the explicit project selection to avoid implicit directory scope. For a pipeline through `tee`, preserve the runner's exit status with `pipefail`.

Classify the first failure as INET-library build, test-executable build, runner/setup, or test assertion. Record the executed-case count and the failed case. A zero-case selection is `NOT_RUN`. A setup failure provides no evidence about the behavior under test.

For a machine-readable handoff, preserve the raw runner output. Normalize it with `.agents/scripts/normalize_verification.py --runner unit` or `--runner module` from the skill suite. Supply the exact command, working directory, selected build mode, filter, exit code, and artifact paths. The v1 verification record uses `NOT_RUN` for a zero-test selection. The adapter records facts only. Interpret the cause in the test investigation.
