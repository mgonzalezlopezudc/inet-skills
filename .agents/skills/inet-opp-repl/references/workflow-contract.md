# Shared opp_repl workflow contract

Read this reference once when defining a cleanup, rebase, comparison, or baseline-update invocation.
Recheck active help whenever the installed `opp_repl` revision changes.

For cleanup/rebase stages and repeated controls, apply [incremental-builds.md](incremental-builds.md)
to the build recipe and workspace lifecycle before execution.

## Invocation record

Record before execution:

- resolved executable and loaded `.opp` entrypoint;
- simulation project, working directory, and debug/release build mode;
- test type and exact selector;
- configurations, runs or seeds, time limits, and result ingredients;
- dependency-store path and the path/package/feature/configuration mapping used for scope;
- comparison controls and their pinned SHAs or result directories;
- output log and result/baseline artifact paths.

Run one scoped invocation for one declared comparison or update operation. Preserve its exit code and
raw output before interpreting the result.

## Test and update modes

Do not conflate a test operation with an update operation. A test operation compares current output
with an expectation or control and reports test results such as `PASS`, `FAIL`, or `ERROR`. An update
operation writes a store and reports facts such as `KEEP`, `INSERT`, `UPDATE`, or `ERROR`.

An update requires the exact scope, cause, correctness reason, and explicit approval required by the
active baseline procedure. Run the same scoped test after an approved update. Record
the affected entries or files and keep the update with its causal source change unless the canonical
procedure permits a standalone baseline commit.

Treat `fingerprint.json`, baseline `.sca` files, `dependency.json`, raw logs, and result directories
as artifacts. A dependency-store change can alter selection and must be explained separately from a
simulation-result change.

## Comparison discipline

Compare identical configuration/run/seed/mode/ingredient tuples. When controls collapse to the same
SHA or result set, record the shared role instead of running duplicate work. When a control itself
fails, preserve that evidence and do not attribute the failure to the candidate.

Detailed result directories may be temporary. Before removing them, persist the exact command,
normalized result envelope, first decisive divergence, causal account supplied by the owning skill,
exit status, and every durable artifact path.
