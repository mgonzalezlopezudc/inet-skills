# Optional capability decisions — 2026-09-03

## opp_repl

Invocation frequency cannot be measured from this repository: it contains no usage telemetry or
prior behavioral-evaluation logs. That absence is recorded rather than replaced by search counts.

Both history workflows remain explicitly supported, `opp_repl` is installed in the evaluation
environment, and the cleanup/rebase references separately maintained overlapping command discovery,
dependency mapping, result semantics, baseline boundaries, and evidence fields. The decision gate
therefore admits `inet-opp-repl` as shared infrastructure even without a frequency estimate. Cleanup
and rebase remain distinct entrypoints because fixed-base reconstruction and upstream rebase have
different authorization, topology, and history guarantees.

Detailed rebase topology, per-stage mechanics, failure recovery, and final assembly now load from
phase-specific references rather than the top-level skill.

## Performance

No recurring performance/scalability request record or named maintenance owner is present. The
decision gate therefore defers `inet-performance-analysis`. A future observation period should log
actual requests and owners; only recurring demand should activate the proposed scope of repeatable
warm-up, wall-clock/memory measurement, profiling, before/after comparison, and `tests/speed`
integration.
