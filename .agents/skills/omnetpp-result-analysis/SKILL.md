---
name: omnetpp-result-analysis
description: Inspect, filter, query, and export OMNeT++ scalar and vector result files using opp_scavetool (export -F CSV-R or CSV-S). Use after a simulation has generated .sca or .vec files, or when asked to find, compare, or extract recorded simulation statistics.
---

# Analyze OMNeT++ results

Apply `doc/project/guide/analyze-simulation-results.md` for comparison, measurement, and reporting
rules. For causal investigations, also apply `doc/project/guide/diagnose-a-simulation.md`. This skill
adds `opp_scavetool` discovery and export mechanics.

Select `.sca`/`.vec` inputs by run metadata and verify they exist. Do not assume every file in a directory belongs to the requested run.

```sh
opp_scavetool query -l -f '<filter>' <inputs>
opp_scavetool export -f '<filter>' -F CSV-R -o <output.csv> <inputs>
```

Use `-F CSV-R` for raw tabular data or `-F CSV-S` for scalar summary; `-F CSV` is invalid. Quote filters and do not overwrite an analysis export unless requested.

1. Identify configuration/run and input files.
2. Discover actual module/result names, types, units, and run attributes.
3. Apply the narrowest selection and report ambiguous or empty matches.
4. Export only required items and vector intervals.

Distinguish scalars, vectors, statistics, and histograms. Use timestamps with captures, logs, or
event logs when the canonical diagnosis guide requires causal correlation; aggregates alone may hide
the transition.
