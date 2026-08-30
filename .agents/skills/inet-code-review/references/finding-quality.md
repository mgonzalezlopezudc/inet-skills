# Reviewer finding quality

The reviewer’s job is to discover defects the author should act on. A local oddity, possible future improvement, or unexplained feeling is not yet a finding.

## Finding proof standard

Build the proof before writing the comment:

| Element | Required question |
| --- | --- |
| Invariant | What must remain true, and which component owns it? |
| Trigger | Which supported configuration, input, state, or event sequence reaches the path? |
| Mechanism | Which exact branch, lookup, transition, ownership transfer, or serialization step breaks it? |
| Consequence | What becomes observably wrong: packet behavior, state, timing, memory, output, or abort? |
| Scope | Was it introduced, exposed, or made contractually relevant by the reviewed change? |
| Verification | What smallest test or reproduction fails before and passes after the correction? |

A blocking finding needs all six. If evidence establishes a real defect but not its exact suggested remedy, report the defect and give a correction direction rather than prescribing an unsafe patch.

## Search beyond the changed line

High-value findings often live at the boundary between the hunk and its consumers. Use every selected review layer to inspect:

- callers and concrete implementations of the changed interface;
- the production path that should exercise a new helper;
- semantic sibling paths admitted or omitted by changed dispatch;
- asynchronous completion that can observe state different from the state used to begin the operation;
- terminal cleanup of all state owned by the completed or canceled operation.

Inspect the contract’s siblings and terminal paths before concluding the hunk is complete.

## Avoid false positives

Before filing, verify each claim against the actual code path, not a pattern-matched suspicion:

- prove the trigger against the effective initialization, configuration, event, and protocol path;
- identify the current owner, transfer operation, destruction point, and later access before using "leak," "dangling," or "double free";
- verify normative or external claims against the applicable authoritative source;
- distinguish preserved cached state from decoded, mutated, copied, or reconstructed state;
- compare against the exact clean baseline before attributing a mismatch to the patch.

Do not file as defects: intentional behavior supported by contract and evidence; hypothetical unsupported future consumers without reachability; bounded bookkeeping retention or ownership transfer; performance concerns without evidence; unrelated pre-existing behavior; or stylistic preferences without an applicable project rule.

See [common-agent-pitfalls.md](common-agent-pitfalls.md) for recurring false-positive patterns (e.g., retained state misidentified as leaks, cached chunk pointers, intentional tag clearing).

## Prefer contract-level corrections

The review comment should point toward the owning abstraction, not merely the symptom. Common durable directions include:

- one authoritative owner instead of duplicated state;
- an explicit semantic operation or result instead of incidental type, order, or observation;
- state stored at the granularity at which its contract varies;
- separate current and pending state when their lifecycle differs;
- stable identity and generation instead of equality of mutable request fields;
- explicit rejection of unsupported variants at the dispatch boundary;
- atomic mode/configuration transitions;
- a representation that preserves unknown data and ordering when a mutation contract requires it.

Do not demand that an adjacent independent correction be folded into the reviewed change merely because inspection exposed it. Report it separately when it changes unrelated trajectories or broadens the feature.

## Write an actionable review comment

Use this shape:

```text
[severity] Concise failure title

<file:line> now <mechanism>. When <reachable trigger>, <state/packet/control flow>
violates <invariant>, causing <consequence>. <Key evidence or comparison>.

Correct this at <owning contract/boundary>. Add <smallest regression that exercises
the production path and distinguishes the bad behavior>.
```

The title names the failure, not the implementation detail. The body explains why it happens and when. The correction direction is specific enough to guide the author but does not pretend an unverified one-line patch is necessarily correct.

## Calibrate severity

Use repository conventions if present. Otherwise calibrate by consequence and reachability:

- **Blocker/critical:** common or unavoidable corruption, crash, invalid wire behavior, or data loss with no safe fallback.
- **Major/high:** reachable incorrect protocol behavior, lifecycle corruption, ownership defect, or important regression in a supported configuration.
- **Moderate:** bounded defect in a less common but supported path, incorrect observability contract, or deterministic configuration failure.
- **Minor:** narrow correctness defect with limited consequence; still requires a concrete trigger and fix.

Optional hardening and questions are not disguised minor findings.

## Review completion

A review is complete when the changed contracts and their semantic siblings have been inspected, actionable findings meet the proof standard, directly relevant validation is reported, and residual gaps are explicit. Finding count is not a completion metric.
