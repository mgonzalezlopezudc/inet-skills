---
name: omnetpp-result-plotting
description: Create reproducible, non-interactive plots and derived summaries from OMNeT++ .sca and .vec results with the native Python result-analysis API. Use to visualize scalar, vector, statistic, or histogram results; compare configurations or repetitions; compute confidence intervals, ECDFs, or time-weighted summaries; and generate plotting scripts and figure artifacts.
---

# Plot OMNeT++ results

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's current result-analysis guidance for observational units, conditions, comparisons,
derived metrics, uncertainty, and disclosures. This skill adds the native Python API and rendering
mechanics.

Load results with `from omnetpp.scave import results`; do not manually parse `.sca`/`.vec` files or substitute CSV loading. Run in the configured OMNeT++ environment.

## Workflow

1. Select exact input runs. Discover names, modules, units, and iteration variables with:

   ```sh
   python .agents/skills/omnetpp-result-plotting/scripts/inspect_results.py \
     <run.sca> <run.vec> [--filter '<result filter>']
   ```

2. Define the result type/filter, condition columns, independent repetition ID, module aggregation, time window/warm-up, units, per-run reduction, and plot type.
3. Query the native API with metadata:

   ```python
   results.set_inputs(input_files)
   frame = results.get_scalars(
       filter_expression,
       include_attrs=True,
       include_runattrs=True,
       include_itervars=True,
   )
   ```

   Use the matching vector/statistic/histogram method. Add config entries only when needed; bound large vector queries by time.
4. Reject empty results, missing columns, incompatible units, unexpected duplicates, invalid vector arrays/timestamps, or missing conditions/repetitions.
5. Reduce to one justified observational unit, then plot. Keep extraction, transformation, and rendering separate in the saved script.

Read [analysis-patterns.md](references/analysis-patterns.md) for implementations of confidence
intervals, vector reduction, time weighting, ECDFs, counter rates, or large-vector handling after
the canonical analysis contract is defined.

Choose plot geometry under the active result-analysis guidance; keep only the native Python rendering
implementation in this skill.

For a direct vector plot:

```sh
python .agents/skills/omnetpp-result-plotting/scripts/plot_vector.py <run.vec> \
  --filter '<filter>' --kind step --ylabel '<label [unit]>' --output <figure.png>
```

Save deterministic scripts/figures and document inputs, filters, run set, window, aggregation, uncertainty, units, missing data, and downsampling.
