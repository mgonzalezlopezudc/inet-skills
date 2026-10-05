---
name: omnetpp-result-analysis
description: Analyze OMNeT++ scalar and vector results with opp_scavetool (export -F CSV-R or CSV-S). Use after a simulation produces .sca or .vec files. Also use for searches, comparisons, or extraction of recorded simulation statistics.
---

# Analyze OMNeT++ results

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's current comparison, measurement, reporting, and diagnosis guidance. This skill
adds `opp_scavetool` discovery and export mechanics.

Select `.sca`/`.vec` inputs by run metadata.
Verify that the selected inputs exist.
Do not assume every file in a directory belongs to the requested run.

```sh
opp_scavetool query -l -f '<filter>' <inputs>
opp_scavetool export -f '<filter>' -F CSV-R -o <output.csv> <inputs>
```

Use `-F CSV-R` for raw tabular data or `-F CSV-S` for a scalar summary.
The format `-F CSV` is invalid.
Quote filters.
Do not overwrite an analysis export unless the user requests it.

Before export, check the selected run IDs, module/result names, types, units, and run attributes.
Record match counts and the requested vector interval.
Report empty or ambiguous selections.
Do not silently broaden the filter.
An absent recording is not a measured zero.
Extraction-only agents return these facts.
The assigned analyst owns aggregation and causal interpretation.

Distinguish scalars, vectors, statistics, and histograms. Use timestamps with captures, logs, or
event logs when the canonical diagnosis guide requires causal correlation; aggregates alone may hide
the transition.
