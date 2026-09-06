---
name: omnetpp-result-analysis
description: Inspect, filter, query, and export OMNeT++ scalar and vector result files using opp_scavetool (export -F CSV-R or CSV-S). Use after a simulation has generated .sca or .vec files, or when asked to find, compare, or extract recorded simulation statistics.
---

# Analyze OMNeT++ results

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's current comparison, measurement, reporting, and diagnosis guidance. This skill
adds `opp_scavetool` discovery and export mechanics.

Select `.sca`/`.vec` inputs by run metadata and verify they exist. Do not assume every file in a directory belongs to the requested run.

```sh
opp_scavetool query -l -f '<filter>' <inputs>
opp_scavetool export -f '<filter>' -F CSV-R -o <output.csv> <inputs>
```

Use `-F CSV-R` for raw tabular data or `-F CSV-S` for scalar summary; `-F CSV` is invalid. Quote filters and do not overwrite an analysis export unless requested.

Before export, check the selected run IDs, module/result names, types, units, and run attributes.
Record match counts and the requested vector interval. Report empty or ambiguous selections rather
than broadening the filter silently; an absent recording is not a measured zero. Extraction-only
agents return these facts and leave aggregation or causal interpretation to the assigned analyst.

Distinguish scalars, vectors, statistics, and histograms. Use timestamps with captures, logs, or
event logs when the canonical diagnosis guide requires causal correlation; aggregates alone may hide
the transition.
