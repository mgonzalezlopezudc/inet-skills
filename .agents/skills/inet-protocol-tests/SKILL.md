---
name: inet-protocol-tests
description: Run INET protocol suites under tests/protocol with opp_run_protocol_tests and OMNeT++ opp_test. Use for test selection, execution, generated builds, shared protocoltest library failures, and expected-result interpretation. Do not use for unit/module tests, statistical baselines, or general regression design.
---

# Run INET protocol tests

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to resolve the active checkout's test scope, build freshness, evidence, and baseline-change obligations. This skill provides the protocol runner mechanics. Also follow the project map's standard-derived test guide for failure classification and eligibility for expected-failure declarations. Use its run-record requirements when updating model evidence; do not substitute a shorter runner summary.

For tests assigned by an implementation plan, discover any required companion artifacts through the current series and test routes. Complete those artifacts when the task includes their creation. Use the checkout's content and evidence requirements. Check that their explanations agree with the test source and observed results.

## Check the active implementation

Resolve `opp_run_protocol_tests` with `command -v`. Check its `--help` output. Inspect these sources when a command behaves unexpectedly:

- `inet.opp`: test folders, suite layout, and shared support library.
- The installed `opp_repl.test.opp` module: discovery, generation, compilation, and result parsing.
- The installed `opp_repl.main` module: CLI defaults, filters, logs, and exit status.
- `.github/workflows/protocol-tests.yml`: CI setup and command.
- `tests/protocol/`: actual suites, test names, shared library, and generated artifacts.

The current project description selects direct children of `tests/protocol/` as suite roots. The runner discovers `.test` files recursively and excludes generated `work/` directories. New suites need no manual registration. Discover available suites locally. Report absent infrastructure rather than select another branch automatically.

## Prepare the environment and library

From the intended INET root, use its established `.envrc` setup or:

```bash
source "$OMNETPP_ROOT/setenv"
source setenv
```

Confirm that `opp_run_protocol_tests`, `opp_test`, `opp_makemake`, and `make` resolve in this environment. Follow the installation guide and workflow for Python dependencies. Load the local project description with `--load . -p inet` from the INET root. Use `--load @opp` only when the checkout supplies no project description.

Apply the build-mode and freshness requirements from the project's gate procedure. The debug build command used with the examples below is:

```bash
make MODE=debug -j$(nproc)
```

The current runner builds INET by default. Use `--no-build` only when the matching INET binaries are current. This option does not disable required support builds or test compilation. For a manual release build, use `MODE=release`; select the same mode with `-m release`.

## Select and run tests

Prefer explicit project, mode, suite, and test filters in scripts. For a requested full suite:

```bash
opp_run_protocol_tests --load . -p inet -m debug
```

For one complete protocol suite:

```bash
opp_run_protocol_tests --load . -p inet -m debug -w wifi
```

Run only the suite relevant to the request. For a focused Wi-Fi selection:

```bash
# One test
opp_run_protocol_tests --load . -p inet -m debug -w wifi -f 'N_BlockAck\.test$'

# All Block Ack tests
opp_run_protocol_tests --load . -p inet -m debug -w wifi -f BlockAck

# Tests under the 802.11n subdirectory
opp_run_protocol_tests --load . -p inet -m debug -w wifi -f '/11n/'
```

`-w/--working-directory-filter` matches the test folder, suite root, or source directory. `-f/--filter` matches the full discovered `.test` path. Both use regular expressions with `re.search()` by default. Quote regexes; use `-w '^tests/protocol/wifi$'` for exact suite selection. Combine alternatives in a single `-f` expression when needed. Do not use simulation configuration or run-number switches as substitutes for protocol test-file selection.

Add `--dry-run` to the same invocation to preview selection before a costly run. Compare actual test counts with that scope and interpret empty selections and dry runs under the gate procedure.

Use explicit scope from the INET root. Directory defaults can vary with the installed runner and project selection. Use `-w wifi -f '/11n/'` for tests under that subdirectory without reliance on implicit scope.

## Understand generated builds and support libraries

For a test without a `%testprog` directive, the pipeline is:

```text
opp_test gen → opp_makemake → make MODE=<mode> → opp_test run
```

Generation extracts these tests into `<suite>/work/<test-basename>/`, even if the source `.test` lives in a nested directory. Compilation links against INET with the mode's library suffix (`_dbg` for debug). If nested tests with identical basenames interfere, inspect this shared output location.

A `%testprog` directive selects an external test program. The runner generates the test files but skips `opp_makemake` and compilation of a test executable. It extracts these tests into `<source-directory>/work/<test-basename>/`. For example, a nested TCP test with `%testprog` uses its source directory's `work/`, not the suite root's `work/`.

Treat `work/` as generated output. Fix the source `.test` or shared inputs, not extracted copies.

The current `inet.opp` selects `tests/protocol/lib` and library name `protocoltest` for protocol suites. The runner builds that support library before execution, including with `--no-build`. Inspect the loaded description when the support library differs. Preserve generated diagnostics before another run; the runner clears test work directories before execution.

For ordinary development, prefer the integrated runner over `tests/protocol/wifi/run-tests.sh`. Inspect a suite-specific script only when diagnosing differences or explicitly asked to use it.

## Diagnose and report results

Rerun the failing selection serially with command logging:

```bash
opp_run_protocol_tests --load . -p inet -m debug -w wifi -f 'N_BlockAck\.test$' \
    --no-concurrent -l INFO -L INFO --log-file protocol-blockack.log
```

Use `DEBUG` for both log levels if needed. Set `--log-file` explicitly to retain a diagnostic log. Preserve runner output and the relevant generated test artifacts. Enable `set -o pipefail` for output through `tee`.

Identify the first failed stage: environment/selection, INET library freshness, shared support build, `opp_test gen`, `opp_makemake`, test compilation, or `opp_test run` assertions. Generation and compilation errors do not establish a protocol behavior failure. Inspect the `.test` checks and generated stdout/stderr for runtime mismatches.

The runner parses `Aggregate result` from `opp_test`. A source marker `%# expected-result: FAIL` declares an expected failure. CLI success means outcomes matched expectations, which can include those failures; it does not prove every protocol obligation passed. Apply the project's failure-classification and baseline-change procedures before proposing any marker or expected-output change.

Populate the project's evidence record with the selected `.test` paths and counts, per-test observed/expected outcomes, failed pipeline stage, and log/generated-artifact paths. The existing unit/module verification normalizer is not a protocol adapter; do not label protocol output as unit or module evidence.
