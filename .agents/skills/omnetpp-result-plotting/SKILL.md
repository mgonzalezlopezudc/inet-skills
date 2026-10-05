---
name: omnetpp-result-plotting
description: Create reproducible, non-interactive plots from OMNeT++ .sca and .vec results with the native Python result-analysis API. Use for scalar, vector, statistic, or histogram plots and comparisons across configurations or repetitions. Derive confidence intervals, empirical cumulative distribution functions (ECDFs), or summaries with time weighting. Save reproducible scripts and figures.
---

# Plot OMNeT++ results

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's current result-analysis guidance for observational units, conditions, comparisons,
derived metrics, uncertainty, and disclosures. This skill adds the native Python API and rendering
mechanics.

Load results with `from omnetpp.scave import results`.
Do not manually parse `.sca`/`.vec` files.
Do not substitute CSV loading.
Run in the configured OMNeT++ environment.

## Workflow

1. Select exact input runs. Discover names, modules, units, and iteration variables with:

   ```sh
   python .agents/skills/omnetpp-result-plotting/scripts/inspect_results.py \
     <run.sca> <run.vec> [--filter '<result filter>']
   ```

2. Define the analysis inputs and operations:
   - Result type and filter.
   - Condition columns and independent repetition ID.
   - Module aggregation and per-run reduction.
   - Time window, warm-up, and units.
   - Plot type.
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

   Use the method for the selected vector, statistic, or histogram type.
   Add configuration entries only when necessary.
   Bound large vector queries by time.
4. Reject empty results, missing columns, incompatible units, unexpected duplicates, invalid vector arrays/timestamps, or missing conditions/repetitions.
5. Define what one observation represents before the plot.
   Reduce the data to that observational unit under the selected analysis contract.
   Plot the reduced data.
   Keep extraction, transformation, and rendering separate in the saved script.

For example, a hypothetical comparison measures each run's mean queue length.
Each run supplies one observation after vector reduction.
The plot compares those run means, rather than treating every vector sample as an independent run.

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
