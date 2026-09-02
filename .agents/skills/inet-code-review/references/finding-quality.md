# Reviewer proof and correction techniques

Use the proof threshold, terminology, severity basis, and report order in
`doc/project/guide/review-a-code-change.md`. Load this reference only when a suspected defect needs
additional techniques for completing that proof or choosing a safe correction direction.

## Search beyond the changed line

High-value findings often live at the boundary between the hunk and its consumers. Use every selected review layer to inspect:

- callers and concrete implementations of the changed interface;
- the production path that should exercise a new helper;
- semantic sibling paths admitted or omitted by changed dispatch;
- asynchronous completion that can observe state different from the state used to begin the operation;
- terminal cleanup of all state owned by the completed or canceled operation.

Inspect the contract’s siblings and terminal paths before concluding the hunk is complete.

## Falsify the suspicion first

Before filing, verify each claim against the actual code path, not a pattern-matched suspicion:

- prove the trigger against the effective initialization, configuration, event, and protocol path;
- identify the current owner, transfer operation, destruction point, and later access before using "leak," "dangling," or "double free";
- verify normative or external claims against the applicable authoritative source;
- distinguish preserved cached state from decoded, mutated, copied, or reconstructed state;
- compare against the exact clean baseline before attributing a mismatch to the patch.

Do not file as defects: intentional behavior supported by contract and evidence; hypothetical
unsupported future consumers without reachability; bounded bookkeeping retention or ownership
transfer; performance concerns without evidence; unrelated pre-existing behavior; or stylistic
preferences without an applicable project rule.

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

## Choose a correction direction without overclaiming

Trace the earliest boundary at which the invariant can be restored and the smallest production-path
verification that distinguishes the defect. Prefer naming the owner, state transition, API contract,
or representation that must change. When multiple repairs remain plausible, explain the required
postcondition and leave the implementation choice open; do not present an untested local edit as the
only fix.
