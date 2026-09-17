---
name: inet-statistical-tests
description: Run, scope, and diagnose INET statistical result regression tests using inet_run_statistical_tests and the separate statistics baseline repository. Use for scalar baseline comparisons, missing baselines, statistical CI failures, and worktree verification; not for the legacy R-based tests/statistical/*.test harness or hypothesis-test design.
---

# INET statistical result regression tests

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to resolve the
active checkout's test category, build mode and freshness, selection, evidence, and baseline-change
obligations. Follow the project map's test-anatomy and result-analysis routes for what scalar
regression evidence can establish. This skill adds runner mechanics; its example mode must follow
the discovered guidance when that guidance differs.

## Establish the runner and its meaning

Check the active checkout rather than assuming every branch matches upstream master:

- `python/inet/test/statistical.py`: task selection, conversion, comparison, and artifacts.
- `python/inet/main.py`: common CLI, filters, logging, and defaults.
- `python/inet/simulation/task.py`: simulation selection and run-number handling.
- `python/inet/project/inet.py`: baseline location (`statistics`, relative to the INET root).
- `.github/workflows/statistical-tests.yml`: CI setup and command.

The inspected implementation converts relevant scalar/vector results through `opp_scavetool`
before comparing scalar dataframes with stored `.sca` files. Use the project's test-anatomy
guidance to interpret that comparison; distributional analysis follows its result-analysis guide.

Legacy `tests/statistical/*.test` files can contain `%postrun-command: Rscript check.r`.
They belong to a different harness; filtering this Python runner by a `.test` filename does not
establish that the legacy test ran. Inspect that harness separately when it is the requested target.

## Prepare the worktree

Run setup from the intended INET worktree root. Use its established environment, for example
`source .envrc` when that file provides the local setup, or:

```bash
source "$OMNETPP_ROOT/setenv"
source setenv
```

Install dependencies in the active Python environment if missing:

```bash
python3 -m pip install -r python/requirements.txt
```

The separate baseline checkout must be at `<INET-root>/statistics`. If absent:

```bash
git clone https://github.com/inet-framework/statistics.git statistics
```

Before using an existing checkout, inspect its state and record both revisions:

```bash
git rev-parse HEAD
git -C statistics status --short
git -C statistics rev-parse HEAD
```

Use the baseline revision selected under the project's comparison procedure. A checkout newer than
the branch point can explain differences unrelated to the feature. Inspect it before refreshing;
`git -C statistics pull --ff-only` is the command for an intentional fast-forward refresh.

For the library build required by the discovered freshness guidance, the debug command is:

```bash
make MODE=debug -j$(nproc)
```

Focused examples below use debug mode. To reproduce statistical CI, use `MODE=release` for the
build and `-m release` for the runner; verify the active checkout's workflow command.

## Preview and run the selected cases

For a requested full statistical CI reproduction, invoke from the INET root after the release build:

```bash
inet_run_statistical_tests -m release --dry-run
inet_run_statistical_tests -m release
```

For focused verification, preview and execute the same explicit selection:

```bash
inet_run_statistical_tests -m debug -w '^examples/wireless(/|$)' --dry-run
inet_run_statistical_tests -m debug -w '^examples/wireless(/|$)' --no-concurrent
```

With no filters and no explicit project selection, the CLI restricts selection to the current
directory recursively. Running from `examples/wireless` therefore scopes discovery to that subtree.
**Supplying any filter disables this automatic directory filter.** Include `-w` explicitly when
combining subtree scope with another filter.

| Option | Selection |
| --- | --- |
| `-w`, `--working-directory-filter` | Simulation working directory |
| `-i`, `--ini-file-filter` | INI filename |
| `-c`, `--config-filter` | INI configuration name |
| `-r`, `--run-number-filter` | Run-number filter; see caveat below |
| `-f`, `--filter` | Generic simulation filter |

Filters are regular expressions; quote them and anchor exact names when needed. For example:

```bash
inet_run_statistical_tests -m debug \
    -w '^examples/wireless(/|$)' -i '^omnetpp\.ini$' -c '^MyConfig$' --dry-run
```

Replace `MyConfig` with a discovered configuration. Check the preview and executed-case count
against the selected scope, then interpret empty selections and dry runs under the gate procedure.

The common CLI accepts `-r`, but in the inspected implementation statistical task selection passes
`run_number=0`, and `get_simulation_tasks` applies run-number filters only when `run_number` is
`None`. Do not assume `-r` selects other runs or creates a repetition campaign. Check the local
implementation and actual selected tasks before making any multi-run claim.

## Diagnose failures

Keep the same filters and serialize the failing selection with more logging:

```bash
inet_run_statistical_tests -m debug -w '^examples/wireless(/|$)' \
    --no-concurrent -l INFO --external-command-log-level INFO
```

Use `DEBUG` for both log levels if INFO is insufficient. Defaults are concurrent execution,
`Cmdenv`, and `statistical_tests.log` in the invocation directory. Preserve logs before rerunning;
`--log-file` can give each invocation a distinct filename. Preserve exit status when using `tee`
by enabling `set -o pipefail`.

Expected scalars live under
`statistics/<simulation-directory>/<ini-file>-<config>-#<run>.sca`.
Differences normally produce `.diff` and `.csv` diagnostics beside that baseline. Empty current
or stored data is `FAIL`; a missing expected `.sca` is `ERROR`. Other simulation, build, or
conversion errors need their own diagnosis. The comparator uses exact dataframe/value checks,
with result-filter handling; the CSV's relative-error column is diagnostic, not a significance
threshold. Inspect the task reason as well as its status.

Conversion can remove current `.vec`/`.vci` files, and comparison normally removes the current
`.sca`; do not promise those raw artifacts survive. Inspect existing diagnostics first, and use a
separate scoped simulation run if raw result evidence is needed.

Use the project's gate procedure for baseline comparability and outcome reporting, its diagnosis
guide when a scalar difference needs a causal explanation, and its baseline-change procedure for
any proposed expectation update. Supply the runner-specific evidence to those procedures: statistics
checkout state, selected configurations and actual runs, per-task reasons, and log/diff/CSV paths.
