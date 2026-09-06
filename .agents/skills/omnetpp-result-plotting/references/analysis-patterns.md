# Analysis patterns

Use the shared project-guidance discovery procedure to find the active result-analysis guidance
before choosing a pattern. Load only the sections needed to implement the selected derived metric or
parameter-study plot.

## Confidence intervals across runs

Pass the per-run table and full condition key defined by the canonical guide as `per_run` and
`condition_columns`.

```python
import numpy as np
import pandas as pd
from scipy.stats import t

def summarize_ci95(
    per_run: pd.DataFrame,
    condition_columns: list[str],
) -> pd.DataFrame:
    summary = (
        per_run.groupby(condition_columns, dropna=False)["value"]
        .agg(mean="mean", std="std", count="count")
        .reset_index()
    )
    summary["se"] = summary["std"] / np.sqrt(summary["count"])
    summary["ci95"] = np.where(
        summary["count"] > 1,
        t.ppf(0.975, summary["count"] - 1) * summary["se"],
        np.nan,
    )
    return summary
```

Check independent run counts separately:

```python
counts = (
    per_run.groupby(condition_columns, dropna=False)["runID"]
    .nunique()
    .reset_index(name="run_count")
)
```

Do not replace the undefined confidence interval for a single run with zero.

## Reduce vectors per run

For a metric whose canonical analysis definition calls for an arithmetic per-run reduction after a
warm-up, use:

```python
records = []
for _, row in vectors.iterrows():
    times = np.asarray(row["vectime"], dtype=float)
    values = np.asarray(row["vecvalue"], dtype=float)
    selected = values[times >= warmup]
    if selected.size:
        record = row.drop(labels=["vectime", "vecvalue"]).to_dict()
        record["value"] = float(selected.mean())
        record["sample_count"] = int(selected.size)
        records.append(record)
per_run = pd.DataFrame.from_records(records)
```

Perform any module aggregation selected by the canonical analysis definition before calling the
across-run summary.

## Time-weighted mean

Use for a piecewise-constant signal whose recorded value remains in effect until its next change:

```python
def time_weighted_mean(times, values, start, end):
    times = np.asarray(times, dtype=float)
    values = np.asarray(values, dtype=float)
    if len(times) != len(values) or end <= start:
        raise ValueError("Invalid vector or interval")

    boundaries = np.concatenate(
        ([start], times[(times > start) & (times < end)], [end])
    )
    interval_starts = boundaries[:-1]
    indices = np.searchsorted(times, interval_starts, side="right") - 1
    if np.any(indices < 0):
        raise ValueError("No recorded value at the interval start")

    durations = np.diff(boundaries)
    return float(np.average(values[indices], weights=durations))
```

The vector must define a value at `start`; do not silently extrapolate backward.

## ECDF and pooled samples

```python
def ecdf(values):
    x = np.sort(np.asarray(values, dtype=float))
    if x.size == 0:
        raise ValueError("Cannot compute an ECDF of empty data")
    return x, np.arange(1, x.size + 1) / x.size

x, probability = ecdf(values)
axis.step(x, probability, where="post")
```

Apply the canonical disclosure rule when selecting one-run, pooled, or balanced samples. This ECDF
function operates on exactly the values passed to it.

## Rate from a cumulative counter

```python
delta_time = np.diff(times)
delta_value = np.diff(counter_values)
valid = (delta_time > 0) & (delta_value >= 0)
rate = scale * delta_value[valid] / delta_time[valid]
rate_times = times[1:][valid]
```

Choose `scale` from the recorded counter unit, for example `8` for bytes to bits. Report counter resets instead of silently treating them as valid intervals.

## Large vectors

Restrict loading when possible:

```python
vectors = results.get_vectors(
    filter_expression,
    start_time=start_time,
    end_time=end_time,
    **query_options,
)
```

For display-only downsampling, select deterministic indices and compute statistics from the unreduced arrays:

```python
indices = np.linspace(0, len(times) - 1, max_points, dtype=int)
display_times = times[indices]
display_values = values[indices]
```

Uniform sampling is unsuitable for step plots when it would discard state transitions; narrow the time window or use a transition-preserving reduction instead.
