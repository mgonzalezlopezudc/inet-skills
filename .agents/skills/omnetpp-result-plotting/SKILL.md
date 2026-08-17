---
name: omnetpp-result-plotting
description: Create reproducible, non-interactive plots and derived summaries from OMNeT++ .sca and .vec results with the native Python result-analysis API. Use to visualize scalar, vector, statistic, or histogram results; compare configurations or repetitions; compute confidence intervals, ECDFs, or time-weighted summaries; and generate plotting scripts and figure artifacts.
---

# Plot OMNeT++ results

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

## Statistical rules

- Treat independent runs—not packets, nodes, or samples—as repetitions.
- Preserve one estimate per run before confidence intervals.
- Include every varying experiment parameter in the condition key.
- Use time-weighted means for piecewise-constant event signals.
- Do not invent warm-up periods or units; use configuration and metadata.
- Aggregate modules only with a metric-defined operation.
- State weighting, exclusions, conversions, uncertainty, and display-only downsampling.

Read [analysis-patterns.md](references/analysis-patterns.md) for confidence intervals, vector reduction, time weighting, ECDFs, counter rates, or large-vector handling.

Choose line plots for continuous samples, steps for piecewise-constant state, scatter for per-event samples, uncertainty summaries for parameter studies, and ECDF/histogram for distributions. Do not connect categorical or unrelated observations.

For a direct vector plot:

```sh
python .agents/skills/omnetpp-result-plotting/scripts/plot_vector.py <run.vec> \
  --filter '<filter>' --kind step --ylabel '<label [unit]>' --output <figure.png>
```

Save deterministic scripts/figures and document inputs, filters, run set, window, aggregation, uncertainty, units, missing data, and downsampling.
