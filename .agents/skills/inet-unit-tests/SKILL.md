---
name: inet-unit-tests
description: Build INET and run unit tests in this repository. Use when asked to build for, execute, filter, diagnose, or report INET C++ unit tests, including IEEE 802.11 HE tests.
---

# Build and run INET unit tests

Run from the repository root with `inet_run_unit_tests`; do not infer a runner from another project.

After compiled INET source or generated-code inputs change, rebuild INET explicitly in the same mode as the tests:

```sh
make MODE=release -j$(nproc)
inet_run_unit_tests -m release -f '<regex>'
```

Use `MODE=debug` with `-m debug` when required. The test runner builds selected test executables but does not rebuild `src/libINET.so` or `src/libINET_dbg.so`. A `.test`-only change needs no INET rebuild unless compiled support inputs changed.

`-f` accepts one regex. Combine groups with alternation and quote it:

```sh
inet_run_unit_tests -m release -f '(First|Second|Third).*\.test'
```

For module tests, use `inet_run_module_tests` with the same build/mode rule. When piping through `tee`, preserve the runner's exit status with `pipefail`.

Run the smallest relevant filter first. When `inet-agent-orchestration` requires final full-suite validation, use the repository-supported no-filter invocation on the final build; a focused filter is not a substitute. A build/test failure or unavailable required suite is incomplete validation.

Distinguish INET-library build failures, test-executable build failures, and assertion failures. Report the first relevant failure rather than counting cascades as independent causes.
