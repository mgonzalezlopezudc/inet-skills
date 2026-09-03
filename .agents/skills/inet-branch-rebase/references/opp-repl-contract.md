# Rebase-specific opp_repl contract

Use [inet-opp-repl](../../inet-opp-repl/SKILL.md) for command discovery, dependency mapping, common
result semantics, baseline boundaries, and the structured verification envelope. This reference
adds topology-derived scope and comparison controls.

## Stage scope

Select the test category under the canonical test policy, then derive each directly related scope:

- an individual `parallel-end` or `lockstep` group uses the union of the current upstream checkpoint
  transition and that group's dependency mapping;
- serial group `Gi` uses the union of the checkpoint transition and accumulated groups `G1..Gi`;
- a combined lockstep checkpoint or final parallel integration uses the union of every current group,
  the checkpoint transition, and cross-cutting adaptation mappings.

No mapping is a reported coverage gap, not permission to substitute an unrelated suite. Run one
scoped build-and-test invocation per attempt with the debug-mode constraints from `AGENTS.md`.

## Comparison controls

Use the applicable roles:

- original pinned `topic` for pre-rebase topic behavior;
- topology-specific stage anchor, including a predecessor group's same-stage point in serial mode;
- plain upstream stage without the current topic group;
- previous same-group or combined integration safe point.

At `stage-0`, the anchor and plain-upstream role may both be `base`, and no previous same-group point
exists. Record the collapsed roles rather than fabricating duplicate evidence. Establish a valid
plain-upstream control before attributing a stage failure to the topic.

## Promotion and final acceptance

A safe point requires a nonempty selected run with no unexplained regression. Raw equality is not
required when upstream intentionally changes behavior, but every difference needs an evidence-backed
attribution. Preserve the raw log and normalized envelope with the attempt record.

For final acceptance, run every final target commit with its directly applicable build/test scope,
then the union scope across every current group, relevant upstream transition, and accepted
adaptation. Compare the clean target with original topic and pinned plain upstream where useful.
Explain every material delta as upstream movement, an intended topic effect, or an accepted
adaptation.
