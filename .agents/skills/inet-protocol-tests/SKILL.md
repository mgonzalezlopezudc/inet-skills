---
name: inet-protocol-tests
description: Run, filter, and diagnose INET protocol suites under tests/protocol using inet_run_protocol_tests and OMNeT++ opp_test. Use for protocol-test execution, generated test builds, shared protocoltest library failures, and expected-result interpretation; not for unit/module tests, statistical baselines, or general regression design.
---

# Run INET protocol tests

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to resolve the
active checkout's test scope, build freshness, evidence, and baseline-change obligations. This
skill provides the protocol runner mechanics. Also follow the project map's standard-derived test
guide for failure classification and eligibility for expected-failure declarations. Use its run-record
requirements when updating model evidence; do not substitute a shorter runner summary.

## Check the active implementation

Use `inet_run_protocol_tests` as the integrated entry point. Check these local sources when a
branch differs or a command behaves unexpectedly:

- `python/inet/test/all.py`, `get_protocol_test_tasks`: suite discovery and framework selection.
- `python/inet/test/opp.py`: recursive discovery, generation, compilation, and result parsing.
- `python/inet/main.py`: CLI defaults, directory selection, logging, and exit status.
- `python/inet/common/util.py`, `matches_filter`: regular-expression matching.
- `tests/protocol/`: actual suites, test names, shared library, and generated artifacts.

The inspected runner discovers suites from direct children of `tests/protocol/` containing `.test`
files at any depth, excluding each suite's generated `work/` directory. New suites need no manual
registration. Discover available names locally; do not assume a historical topic branch is needed,
or that every older checkout has the current infrastructure. If it is absent, report the missing
capability rather than selecting a different branch automatically.

## Prepare the environment and library

From the intended INET root, use its established `.envrc` setup or:

```bash
source "$OMNETPP_ROOT/setenv"
source setenv
```

INET's `setenv` exposes `bin/` on `PATH` and `python/` on `PYTHONPATH`. Confirm that
`inet_run_protocol_tests`, `opp_test`, `opp_makemake`, and `make` resolve in this environment.

Apply the build-mode and freshness requirements from the project's gate procedure. The debug
build command used with the examples below is:

```bash
make MODE=debug -j$(nproc)
```

The runner builds test executables and applicable support libraries, but its support-library build
hook does not rebuild INET itself. For release verification, use both `MODE=release` and `-m release`.

## Select and run tests

Prefer explicit project, mode, suite, and test filters in scripts. For a requested full suite:

```bash
inet_run_protocol_tests -p inet -m debug
```

For one complete protocol suite:

```bash
inet_run_protocol_tests -p inet -m debug -w wifi
inet_run_protocol_tests -p inet -m debug -w tcp
inet_run_protocol_tests -p inet -m debug -w ipv6
```

Run only the suite relevant to the request. For a focused Wi-Fi selection:

```bash
# One test
inet_run_protocol_tests -p inet -m debug -w wifi -f 'N_BlockAck\.test$'

# All Block Ack tests
inet_run_protocol_tests -p inet -m debug -w wifi -f BlockAck

# Tests under the 802.11n subdirectory
inet_run_protocol_tests -p inet -m debug -w wifi -f '/11n/'
```

`-w/--working-directory-filter` matches the suite path, such as `tests/protocol/wifi`.
`-f/--filter` matches the full discovered `.test` path. Both use regular expressions with
`re.search()` by default. Quote regexes; use `-w '^tests/protocol/wifi$'` for exact suite selection.
Combine alternatives in a single `-f` expression when needed. Do not use simulation configuration
or run-number switches as substitutes for protocol test-file selection.

Add `--dry-run` to the same invocation to preview selection before a costly run. Compare actual
test counts with that scope and interpret empty selections and dry runs under the gate procedure.

Without `-p` or any filter, the CLI uses the current directory as its working-directory filter:

```bash
cd tests/protocol/wifi
inet_run_protocol_tests -m debug
```

Adding `-p` or any filter disables that implicit scope. Supply `-w` when combining filters.
The protocol runner matches suite roots, so entering a deeper directory such as `wifi/11n` does
not provide recursive sub-suite selection; use `-w wifi -f '/11n/'` instead.

## Understand generated builds and support libraries

For each selected test, the normal pipeline is:

```text
opp_test gen → opp_makemake → make MODE=<mode> → opp_test run
```

Generation extracts a test into `<suite>/work/<test-basename>/`, even if its source `.test` lives
in a nested directory. Compilation links against INET with the mode's library suffix (`_dbg` for
debug). Treat `work/` as generated output; fix the source `.test` or shared inputs, not extracted
copies. If nested tests with identical basenames interfere, inspect this shared output location.

Framework detection scans all tests in a suite for the literal `#include "ProtocolTest.h"`.
When found, the suite uses `tests/protocol/lib` and links `protocoltest`; detection is not limited
to the selected individual tests. Otherwise, the generic runner can use a suite-local `lib/`.
The normal build-enabled invocation builds applicable support libraries before the suite runs.
`--no-build` skips that support build; it does not skip generation and compilation of each test.

For ordinary development, prefer the integrated runner over `tests/protocol/wifi/run-tests.sh`.
Inspect a suite-specific script only when diagnosing differences or explicitly asked to use it.

## Diagnose and report results

Rerun the failing selection serially with command logging:

```bash
inet_run_protocol_tests -p inet -m debug -w wifi -f 'N_BlockAck\.test$' \
    --no-concurrent -l INFO --external-command-log-level INFO
```

Use `DEBUG` for both log levels if needed. The default CLI log is `protocol_tests.log` in the
invocation directory; use `--log-file` for distinct rerun logs. Preserve runner output and the
relevant generated test artifacts. Enable `set -o pipefail` if piping through `tee`.

Identify the first failed stage: environment/selection, INET library freshness, shared support
build, `opp_test gen`, `opp_makemake`, test compilation, or `opp_test run` assertions. Generation
and compilation errors do not establish a protocol behavior failure. Inspect the `.test` checks
and generated stdout/stderr for runtime mismatches.

The runner parses `Aggregate result` from `opp_test`. A source marker
`%# expected-result: FAIL` declares an expected failure. CLI success means outcomes matched
expectations, which can include those failures; it does not prove every protocol obligation
passed. Apply the project's failure-classification and baseline-change procedures before proposing
any marker or expected-output change.

Populate the project's evidence record with the selected `.test` paths and counts, per-test
observed/expected outcomes, failed pipeline stage, and log/generated-artifact paths.
The existing unit/module verification normalizer is not a protocol adapter; do not label protocol
output as unit or module evidence.
