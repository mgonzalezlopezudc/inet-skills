---
name: inet-chart-tests
description: Run INET chart regression tests with opp_run_chart_tests and the media baseline repository. Use for chart selection, image differences, missing reference images, or chart CI failures. Do not use for new plots or scalar regression tests.
---

# INET chart tests

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to find the active checkout's test, build freshness, evidence, and baseline procedures. This skill supplies runner mechanics. Follow the discovered guidance when its required mode or scope differs from an example.

Chart tests run simulations for selected analysis files (`.anf`). The runner exports chart images through `omnetpp.scave` and compares them with reference PNG images. An image match supplies chart regression evidence. It does not establish protocol correctness or statistical confidence.

## Check the runner and environment

Read the active checkout's `inet.opp`, installation guide, and `.github/workflows/chart-tests.yml`. Check the project defaults, baseline locations, dependency source, and CI mode. Resolve the actual executable before execution:

```sh
command -v opp_run_chart_tests
opp_run_chart_tests --help
```

Current INET uses `opp_repl`. The earlier `inet_run_chart_tests` command can be absent. Do not substitute a legacy command without evidence that the active checkout requires it.

Set up the OMNeT++ environment. Load `setenv` from the intended INET root. Use the established Python environment. The chart workflow installs OMNeT++ Python requirements plus `opp_repl`; INET's earlier `python/requirements.txt` can be absent. Check the active workflow before an authorized dependency installation. Match its dependency versions for CI reproduction.

The current `inet.opp` selects release mode and the `showcases` filter for chart tests. It declares `media` as the baseline checkout and `doc/media` as the image path relative to each analysis directory. Per-showcase links connect these paths to the baseline checkout. Inspect those links when reference images are absent.

The baseline checkout belongs at `<INET-root>/media`. If it is absent, clone it from the INET root:

```sh
git clone https://github.com/inet-framework/media.git media
```

Do not clone over an existing directory. Inspect its contents first. Record both repository revisions and local changes before a comparison:

```sh
git status --short
git rev-parse HEAD
git -C media status --short
git -C media rev-parse HEAD
```

Keep the same baseline revision and Python environment for a base-versus-feature comparison. Do not refresh the baseline during that comparison.

## Select and run chart tests

Run from the INET root with its local project description. The runner builds by default. Use `--no-build` only when the binaries for the selected mode are current. This option does not disable simulations.

For the current showcase CI scope:

```sh
opp_run_chart_tests --load . -p inet -m release -f '^showcases/'
```

For example, select the error-rate showcase to check only its charts:

```sh
opp_run_chart_tests --load . -p inet -m release \
  -f '^showcases/wireless/errorrate(/|$)'
```

This command selects analysis files in that directory and runs their simulations before the image comparison.

Use an explicit `-f` path expression for a focused run. Quote regular expressions. Do not assume that a subdirectory or `-w` further restricts a project default filter. Earlier `opp_repl` versions let that default hide the directory restriction. Check the selected analysis files and actual chart count.

The common CLI exposes simulation filters such as `-c`, `-i`, and `-r`. These options do not necessarily select individual charts. Inspect the installed chart runner before a claim about chart selection or run coverage. The Python API can expose `chart_filter` when the CLI does not.

A dry run supplies no execution evidence. A zero-chart selection means that no chart comparison ran. Do not treat configuration discovery or a successful build as a chart test pass.

## Diagnose the result

Read each task's status, expected status, and reason. Check simulation outcomes as well as chart outcomes. Do not infer simulation success from an image alone.

- `PASS` means that the images match under the installed comparator's acceptance rule.
- `FAIL` can mean an image difference or an absent reference image.
- `SKIP` can mean that the chart has no `image_export_filename` property.
- `ERROR` can mean a chart script, export, dependency, or execution failure.

The inspected comparator uses a root mean square error metric with a default threshold of zero. It centers and pads images to a common size before comparison. Check the installed implementation before a claim about exact comparison semantics. Do not change the threshold to conceal an unexplained difference.

Differences normally retain `*-new.png` and `*-diff.png` beside the reference image. Matching images can lose their temporary export. The CI workflow collects these artifacts under `media`. Preserve existing artifacts before another run; the runner can replace them.

For a focused diagnosis, retain the same filter and mode:

```sh
opp_run_chart_tests --load . -p inet -m release \
  -f '^showcases/wireless/errorrate(/|$)' \
  --no-concurrent -l INFO -L INFO --log-file chart-errorrate.log
```

Inspect image differences to distinguish changed result data from changed fonts, layout, or export dependencies. State when the cause remains unknown. For an absent reference image, check the media revision, export filename, and directory links before a baseline update.

## Update only approved reference images

Follow the active checkout's baseline procedure. Present the affected charts, cause, candidate images, and correctness evidence before the required approval. Permission to run tests does not authorize replacement of reference images.

After approval, check `opp_update_chart_test_results --help`. Preserve the approved project, mode, filters, and simulation arguments. Supply explicit scope even if the updater supports project defaults. Inspect `git -C media diff --stat` and every changed image. Rerun the same chart tests after the update.

Updater statuses such as `KEEP`, `UPDATE`, and `INSERT` describe baseline actions. They do not establish that the chart or simulation is correct.

## Record evidence

Use the discovered project procedure for the execution record. Include chart identities, the media revision and local changes, image paths, and the Python environment. Retain simulation outcomes as well as chart outcomes. Separate expected skips from executed comparisons.
