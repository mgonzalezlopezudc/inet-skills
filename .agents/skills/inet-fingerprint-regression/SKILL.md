---
name: inet-fingerprint-regression
description: Run and diagnose INET fingerprint regression tests with opp_repl and the JSON baseline. Use for scoped execution, mismatch analysis, or approved baseline updates. Distinguish simulation differences from correctness evidence.
---

# INET fingerprint regression

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to find the active checkout's test guidance. A fingerprint compares selected simulation properties with a stored expectation. A match does not establish protocol correctness.

## Check the interface and baseline

Check the resolved test executable with `command -v opp_run_fingerprint_tests`. Inspect its options with `--help`. For an update, also check `opp_update_fingerprint_test_results`. Read the active checkout's migration guide and fingerprint workflow for the required installation source. Check each executable's Python interpreter when multiple Python environments exist. An update through `python3 -m pip` can leave an earlier executable in `PATH`.

Prefer the active checkout's project description. From its root, use `--load . -p inet`. Use the bundled description through `--load @opp -p inet` only when the checkout supplies none. For that fallback, confirm that `INET_ROOT` selects the intended checkout. Check the loaded description for the baseline path, ingredients, and time limits.

The current INET baseline is `tests/fingerprint/store.json`. Each entry identifies the directory, INI file, configuration, run number, simulation time limit, ingredients, fingerprint, and expected result. The project description selects `tplx`, `~tNl`, and `~tND` by default. These select event properties, packet lengths between network nodes, and packet data between network nodes, respectively. Both packet selections also include event times and node paths.

The CSV files, `fingerprinttest`, and INET's earlier Python fingerprint commands no longer supply the current workflow. Do not fall back to those tools when required options are absent. Report the missing capability as `NOT_RUN`. Use the installation source specified by the active checkout for an authorized environment update. Do not assume that the newest package release supports this workflow.

## Select and run cases

Set up the OMNeT++ environment. Load `setenv` from the intended INET root. Use the build mode required by the discovered project guidance. Rebuild the matching library after compiled source or generated-code inputs change. The runner builds by default; use `--no-build` only when the matching binaries are current.

Run from the INET root with an explicit selection. This example applies when the project guidance selects debug mode:

```sh
opp_run_fingerprint_tests --load . -p inet -m debug \
  -f '<directly-related-regex>'
```

Use `-w` for directories, `-i` for INI files, and `-c` for configurations. Use `-r` for run numbers. Quote regular expressions. Anchor exact configuration names. Run 0 alone does not establish coverage of other seeds.

The option meanings differ from `fingerprinttest`: `-f` selects cases, `-m` selects the build mode, and `--ingredients` selects fingerprint ingredients. Use the migration guide for other replacements. If `--append-args` is necessary, put it last; it passes all subsequent arguments to `opp_run`.

The runner executes simulations in parallel by default. Use `--no-concurrent` for one simulation at a time. A dry run or zero-test selection supplies no execution evidence. A dry run can require the matching INET library for configuration discovery.

The supplied INET description selects the shortest stored simulation time limit for each run and ingredient. It does not check every stored limit when multiple limits exist. Record the actual limits in the evidence.

## Diagnose results

`PASS` means that the fingerprint matches. `FAIL` means that the comparison fails. `ERROR` means that execution or fingerprint extraction fails. Compare each result with its stored expected result. The command exits zero only when all results are expected. A shared `PASS` substring does not establish success for all cases.

For example, a stored case can expect `ERROR`. If the expected simulation error occurs, the runner can accept that result. This establishes the expected failure behavior, not successful simulation execution. Confirm the error cause before this interpretation. An infrastructure failure supplies no evidence for the expected simulation error, even if the runner accepts its status.

For a mismatch:

1. Record the configuration, run/seed, mode, time limit, ingredients, old/new fingerprints, and first mismatch.
2. Check changes to event order, event times, packets/tags, random streams, recorded results, or topology.
3. Use logs, event logs, captures, or results to explain the first divergence.

## Update an approved baseline

Follow the active checkout's baseline procedure before an update. State the exact scope, cause, and reason that the new behavior is correct. Obtain the approval required by that procedure. Source approval alone does not authorize a baseline update.

Before an update, confirm that `opp_update_fingerprint_test_results` is available and supports the required options. Preserve every test filter, ingredient, build mode, and simulation argument within the approved scope. If the test specifies `--ingredients tplx`, retain that option in the update command. Do not restore the default ingredients unless approval covers them.

For the test example above, which uses the project defaults, the update command is:

```sh
opp_update_fingerprint_test_results --load . -p inet -m debug \
  -f '<directly-related-regex>'
git diff -- tests/fingerprint/store.json
```

The command writes directly to the JSON store. It replaces the earlier `.UPDATED` workflow.

`KEEP` means no change. `UPDATE` replaces an expectation. `INSERT` adds an expectation. None of these results establishes correctness. Explain every changed entry. Keep baseline changes with their causal source change under the discovered commit rules.

By default, the update command processes every selected stored limit. Thus, identical test and update filters do not guarantee identical coverage. After an update, rerun the selected tests with the same mode, ingredients, and simulation arguments. Compare the executed limits with the changed entries. Use a verified API selection for additional limits, or report those entries as unverified.

For an approved new configuration, use `--no-stored-only` with exact directory, INI, and configuration filters plus `-r 0`. New entries use the INI simulation time limit. Confirm that this limit exists. Omit `--no-stored-only` from the subsequent test command to check the stored expectations.

## Record evidence

Preserve the raw runner output and exit code. For a machine-readable handoff, use the skill-suite adapter `.agents/scripts/normalize_verification.py --runner fingerprint`. Supply the exact command, working directory, mode, selector, configuration, run, seed, exit code, and artifacts. Include the actual time limits and ingredients in the retained artifacts. Set changed-result expectation and approval from recorded facts. The adapter leaves `UPDATE` or `INSERT` as `INCONCLUSIVE`. It does not decide whether the new baseline is correct.
