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

High-value findings often live at the boundary between the hunk and its consumers:

- a reference-mode change works for HT but makes VHT fall through to zero;
- a new extractor interface bypasses a gate because its subclasses override the older collection API only;
- a correct helper is never exercised by the production HCF path;
- broader base-class dispatch admits an unsupported frame subclass;
- a response is built from one channel/capability snapshot but commits later mutable state after ACK;
- a timer or teardown deletes one object while leaving its reorder, retry, pending-ID, or peer state alive.

Inspect the contract’s siblings and terminal paths before concluding the hunk is complete.

## Avoid false positives

Before filing:

- trace initialization stages, subscription/publication order, and whether an event can actually run between them;
- identify the current owner and every cleanup point before using “leak,” “dangling,” or “double free”;
- distinguish packet movement to a retirement list from deletion and from lost ownership;
- verify current IEEE text instead of relying on remembered or obsolete field semantics;
- resolve effective NED/INI values and supported custom configurations instead of reasoning only from type names;
- distinguish untouched serializer-cache round trips from decode-modify-encode or reconstructed objects;
- compare against exact clean `HEAD` before attributing an existing fingerprint mismatch to the patch;
- inspect whether a test’s earlier actions mutate fixture state or whether it would still pass with the changed integration removed.

Do not file as defects:

- intentional behavior already supported by the contract and direct evidence;
- a hypothetical unsupported future consumer without current reachability;
- bounded bookkeeping retention mislabeled as a leak;
- performance concern without path frequency, operation count, or profiling evidence;
- unrelated pre-existing behavior not made material by the change;
- stylistic preference without an applicable INET naming or architecture rule.

## Prefer contract-level corrections

The review comment should point toward the owning abstraction, not merely the symptom. Common durable directions include:

- one authoritative owner instead of duplicated state;
- typed operation, PHY family, or transaction result instead of RTTI, vector order, bitrate ties, or observation signals;
- per-peer, per-TID, or per-agreement capability instead of a station-wide assumption;
- separate current and pending lifecycle cleanup;
- protocol identity and generation instead of equality of request fields;
- explicit rejection of unsupported variants at the dispatch boundary;
- atomic mode/configuration transitions;
- ordered typed-plus-opaque wire elements when mutation must preserve unknown extensions.

Do not demand that an adjacent independent standards correction be folded into the reviewed change merely because inspection exposed it. Report it separately when it changes unrelated trajectories or broadens the feature.

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
