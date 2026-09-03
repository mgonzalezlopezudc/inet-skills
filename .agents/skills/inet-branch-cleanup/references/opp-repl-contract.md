# Cleanup-specific opp_repl contract

Use [inet-opp-repl](../../inet-opp-repl/SKILL.md) for command discovery, dependency mapping, common
result semantics, baseline-update boundaries, and the structured verification envelope. This
reference adds the cleanup comparison and commit-type oracle.

## Scope and controls

Select the directly related configurations for each output commit from that commit's assigned
coverage-ledger slice. Unless the approved cleanup contract requires otherwise, start with
fingerprints and run 0; add statistical, chart, seed, or parameter coverage only when the behavior
claim requires it.

Use these controls for a surprising result:

- `topic` — the pinned intended final behavior;
- `base` — the pinned starting behavior;
- `clean@prev` — the previous promoted clean safe point, isolating the current commit.

## Commit-type oracle

- **Refactor / chore / docs** — the selected behavior signal remains identical to the previous safe
  point. A mismatch means the commit is misclassified or defective. Stop and investigate; do not
  re-record a baseline to preserve the label.
- **Fix / feature** — the signal may change only in predicted configurations and for the explained
  behavior claim. Unrelated selected configurations remain identical.

Run one scoped build-and-test invocation per output commit. A zero-case selection cannot promote a
safe point. Persist the normalized envelope and concise causal account in the cleanup logbook before
discarding temporary details.

## Final acceptance

Run the union of every directly related configuration mapped to a change in the reconstructed
branch, retaining explicit filters. Compare with the pinned topic and base where they distinguish
missing material from intended behavior. Baseline artifacts may differ from `topic` only through the
approved canonical procedure; source and other non-baseline files must remain tree-identical.
