# INET `opp_repl` cleanup test contract

Use `opp_repl` as the per-commit oracle: it checks whether a commit behaves as its label claims.

## Choose the test scope

Choose the test category under `doc/project/rule/testing.md`; this reference adds only the
`opp_repl` mechanics for the selected cleanup contract.

Record the requested test types in priority order. Unless the cleanup specifies otherwise, use fingerprint tests first, statistical tests second, and run number 0 only. Add chart tests or more runs only when the task opts in or directly related coverage requires them.

Use `dependency.json` to map:

```text
changed files -> NED packages -> features -> simulation configurations
```

This mapping predicts which configurations each change group can affect and therefore scopes its per-commit test. If no directly related test can be identified, report the coverage gap; do not substitute an unrelated broad suite.

Run one scoped `opp_repl` invocation per output commit, with the build folded into that step:

- **ERROR** — the build or execution failed, or no valid test ran;
- **FAIL** — the test ran but the observed behavior did not match the expectation;
- **PASS** — the build succeeded and the result matched the declared commit effect.

## Use the test as the type oracle

- **Refactor / chore / docs** — the fingerprint must be identical to the previous clean safe point on every affected configuration. A mismatch means that behavior leaked into the commit or that the change is mislabeled. Stop and investigate; never re-record the baseline merely to make it pass.
- **Fix / feature** — the fingerprint or statistics may change, but only in the predicted configurations and for an intended, explained reason. Unrelated selected configurations must remain identical.

When a result is surprising, compare it with three controls:

- `results_topic` — the intended final behavior;
- `results_base` — the starting behavior;
- `results_clean@prev` — the previous output commit, which isolates what the current commit changed.

## Update baselines

Follow `doc/project/guide/change-a-baseline.md`, including its approval requirement, before updating
any recorded expectation.

- **Fingerprint** — call `update_fingerprint_test_results(...)`. It uses `FingerprintStore.update_fingerprint`, writes `fingerprint.json`, and reports `INSERT`, `UPDATE`, or `KEEP`. Record the affected entries and result codes.
- **Statistical** — call `update_statistical_test_results(...)`. It copies the current `.sca` result into the baseline directory. Record the exact files and quantify the delta.

Treat `fingerprint.json`, baseline `.sca` files, and `dependency.json` as test artifacts when comparing `clean` with `topic`.

Put an approved baseline delta in the same commit as the source change that caused it. Rerun the
same scoped test on that commit and record the causal behavior change and reason in its message. Use
a standalone baseline commit only when no single source commit caused the movement, as required by
the canonical procedure.

Detailed results are temporary: use them to write the causal account in the logbook, then discard them unless repository policy requires retention.

## Final acceptance

Run the selected contract across every configuration mapped to any change in the branch, using run 0 or the explicitly approved wider run set. “Full” means full coverage of the branch's directly related contract; keep explicit filters and do not expand into unrelated INET suites.
