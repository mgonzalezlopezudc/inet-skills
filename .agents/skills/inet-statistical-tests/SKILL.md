---
name: inet-statistical-tests
description: Run INET statistical regression tests with opp_run_statistical_tests and the separate statistics baseline repository. Use for test scope, scalar baseline comparisons, missing baselines, statistical CI failures, or worktree verification. Do not use for the legacy R-based tests/statistical/*.test harness or hypothesis-test design.
---

# INET statistical result regression tests

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to resolve the active checkout's test category, build mode and freshness, selection, evidence, and baseline-change obligations. Follow the project map's test-anatomy and result-analysis routes for what scalar regression evidence can establish. This skill adds runner mechanics; its example mode must follow the discovered guidance when that guidance differs.

## Establish the runner and its meaning

Check the active checkout rather than assuming every branch matches upstream master:

- `inet.opp`: project defaults, run selection, and baseline location.
- The installed `opp_repl.test.statistical` module: task selection, conversion, comparison, and artifacts.
- The installed `opp_repl.main` and `opp_repl.simulation.task` modules: CLI filters and simulation selection.
- `.github/workflows/statistical-tests.yml`: CI setup and command.

The inspected implementation converts relevant scalar/vector results through `opp_scavetool` before comparing scalar dataframes with stored `.sca` files. Use the project's test-anatomy guidance to interpret that comparison; distributional analysis follows its result-analysis guide.

Legacy `tests/statistical/*.test` files can contain `%postrun-command: Rscript check.r`. They belong to a different harness; filtering this Python runner by a `.test` filename does not establish that the legacy test ran. Inspect that harness separately when it is the requested target.

## Prepare the worktree

Run setup from the intended INET worktree root. Use its established environment, for example `source .envrc` when that file provides the local setup, or:

```bash
source "$OMNETPP_ROOT/setenv"
source setenv
```

Check the actual runner before execution:

```bash
command -v opp_run_statistical_tests
opp_run_statistical_tests --help
```

Use the installation source and Python requirements from the active checkout's installation guide and statistical workflow. Current INET uses `opp_repl`; its earlier `python/requirements.txt` can be absent. Load the local project description with `--load . -p inet` from the INET root. Use `--load @opp` only when the checkout supplies no project description.

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

Use the baseline revision selected under the project's comparison procedure. A checkout newer than the branch point can explain differences unrelated to the feature. Inspect it before refreshing; `git -C statistics pull --ff-only` is the command for an intentional fast-forward refresh.

For the library build required by the discovered freshness guidance, the debug command is:

```bash
make MODE=debug -j$(nproc)
```

Focused examples below use debug mode. For statistical CI, read the active workflow's command and mode. Use that mode for both the build and the runner.

## Preview and run the selected cases

For a requested full statistical CI reproduction, use the active workflow's scope and mode. This example applies when that workflow selects release mode:

```bash
opp_run_statistical_tests --load . -p inet -m release --dry-run
opp_run_statistical_tests --load . -p inet -m release
```

For focused verification, preview and execute the same explicit selection:

```bash
opp_run_statistical_tests --load . -p inet -m debug -w '^examples/wireless(/|$)' --dry-run
opp_run_statistical_tests --load . -p inet -m debug -w '^examples/wireless(/|$)' --no-concurrent
```

Use explicit `-w` scope from the INET root. Directory defaults can vary with the installed runner and project selection. Do not assume that the current directory restricts a command with explicit filters or project selection.

| Option | Selection |
| --- | --- |
| `-w`, `--working-directory-filter` | Simulation working directory |
| `-i`, `--ini-file-filter` | INI filename |
| `-c`, `--config-filter` | INI configuration name |
| `-r`, `--run-number-filter` | Run-number filter; see caveat below |
| `-f`, `--filter` | Generic simulation filter |

Filters are regular expressions; quote them and anchor exact names when needed. For example:

```bash
opp_run_statistical_tests --load . -p inet -m debug \
    -w '^examples/wireless(/|$)' -i '^omnetpp\.ini$' -c '^MyConfig$' --dry-run
```

Replace `MyConfig` with a discovered configuration. Check the preview and executed-case count against the selected scope, then interpret empty selections and dry runs under the gate procedure.

The current `inet.opp` pins statistical tests to run 0. A `-r` filter does not necessarily override that fixed run. Check the loaded defaults and actual selected tasks before a claim about other runs. One run does not establish statistical confidence.

## Diagnose failures

Keep the same filters. Run the selected failed cases one at a time with more logs:

```bash
opp_run_statistical_tests --load . -p inet -m debug -w '^examples/wireless(/|$)' \
    --no-concurrent -l INFO -L INFO --log-file statistical-wireless.log
```

Use `DEBUG` for both log levels if INFO is insufficient. The runner uses concurrent execution and `Cmdenv` by default. Set `--log-file` explicitly to retain a diagnostic log. Preserve existing logs before another run. Preserve exit status through `tee` with `set -o pipefail`.

Expected scalars live under `statistics/<simulation-directory>/<ini-file>-<config>-#<run>.sca`. Differences normally produce `.diff` and `.csv` diagnostics beside that baseline. Empty current or stored data is `FAIL`; a missing expected `.sca` is `ERROR`. Other simulation, build, or conversion errors need their own diagnosis. The comparator uses exact dataframe/value checks, with result-filter handling; the CSV's relative-error column is diagnostic, not a significance threshold. Inspect the task reason as well as its status.

Conversion can remove current `.vec`/`.vci` files, and comparison normally removes the current `.sca`; do not promise those raw artifacts survive. Inspect existing diagnostics first, and use a separate scoped simulation run if raw result evidence is needed.

Use the project's gate procedure for baseline comparability and outcome reporting, its diagnosis guide when a scalar difference needs a causal explanation, and its baseline-change procedure for any proposed expectation update. Supply the runner-specific evidence to those procedures: statistics checkout state, selected configurations and actual runs, per-task reasons, and log/diff/CSV paths.
