---
name: inet-unit-tests
description: Build INET and run unit tests in this repository. Use when asked to build for, execute, filter, diagnose, or report INET C++ unit tests, including IEEE 802.11 HE tests.
---

# Build and run INET unit tests

Run from the repository root with `inet_run_unit_tests`; do not infer a runner from another project.

After compiled INET source or generated-code inputs change, rebuild INET explicitly in debug mode before running tests:

```sh
make MODE=debug -j$(nproc)
inet_run_unit_tests -m debug -f '<regex>'
```

Always use `MODE=debug` and `-m debug`; release-mode builds and test runs are prohibited. The test runner builds selected test executables but does not rebuild `src/libINET_dbg.so`. A `.test`-only change needs no INET rebuild unless compiled support inputs changed.

`-f` accepts one regex. Combine groups with alternation and quote it:

```sh
inet_run_unit_tests -m debug -f '(First|Second|Third).*\.test'
```

For module tests, use the same explicit debug mode and filtering rule:

```sh
inet_run_module_tests -m debug -f '<directly-related-filter>'
```

Before invoking either runner, map each selected test to a changed path, symbol, or behavioral contract. Run only that directly related set with an explicit `-f` filter; never omit the filter or broaden it to an unrelated directory or suite. Tests added or modified by the change are directly related. If no existing test can be mapped to the change, report the coverage gap instead of running a broader selection. When piping through `tee`, preserve the runner's exit status with `pipefail`.

A build/test failure or unavailable directly related test is incomplete validation.

Distinguish INET-library build failures, test-executable build failures, and assertion failures. Report the first relevant failure rather than counting cascades as independent causes.
