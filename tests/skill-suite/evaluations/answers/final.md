# Final snapshot forward validation

Guidance: `/tmp/inet-skill-evaluation/project/doc/project/README.md` routes to `doc/project/policies/current.md`. That supplied policy governs: paths are unprotected, verification uses release mode, changed model source must be rebuilt, zero executed cases provides no evidence, baseline movement requires cause and explicit approval, ownership must be preserved on refusal and success, and independent statistical units are runs. No fixed report template is required.

## 1. aggregation-clean

No defect is established. The equally weighted mean of independent run estimates is `(10 + 20) / 2 = 15 ms`, with `n = 2`. Conditions, warm-up and durations match, and each state-vector estimate is already time weighted. The 1000 within-run observations are not claimed as independent repetitions. No confidence interval is claimed; there is no missing CI defect to report. This conclusion reviews the supplied reduction, not an independently executed extraction. No plot was rendered.

## 2. fingerprint

The updater reports `UPDATE`, changing Demo, run 0, seed 3 from `aaaa-bbbb` to `cccc-dddd`, with exit status 0. This establishes recorded expectation movement, not a passing behavioral comparison or correctness of the new fingerprint. Normalize this update as `INCONCLUSIVE`. The supplied context explicitly records neither a causal explanation nor baseline approval, so the new expected value cannot be accepted now. First explain the earliest divergence with directly related logs/event logs/captures/results, identify why the change is correct, obtain explicit approval for the exact baseline scope, and rerun the same scoped comparison under matching configuration, run, seed, mode and ingredients. No baseline was changed here.

## 3. ini-precedence

`[General]` supplies both assignments; no extends chain is given. For the supplied instantiated path `Lab.sender`, both `**.interval = 2s` and `Lab.sender.interval = 1s` match. Written-order first-match semantics make the wildcard assignment win, so the effective interval is **2 seconds**. The more specific later assignment does not override it, and the 5-second parameter default does not apply. This configuration therefore does not guarantee one-second sends. Put the specific assignment before the wildcard to select a one-second interval; actual send behavior beyond parameter resolution is outside the supplied evidence. No unresolved precedence ambiguity or simulator run is needed.

## 4. ownership

The defect is the early return after refusal: `Owner::accept` already owns the packet, and `enqueue(false)` retains that ownership, so returning without deleting leaks it.

Implementation contract: `Owner` owns disposal at the public `accept(Packet *)` entry point. The path is entry ownership -> `queue.enqueue` -> refusal deletion or successful transfer. Correct exactly the refusal branch in `Owner.cc`; the ownership contract in `Owner.h` remains valid. The known affected checks are `OwnerRefusal.test` and `OwnerAccepted.test`. On success the queue owns the packet until cleanup and must delete it exactly once. No callbacks or other consumers exist in this fixture; no timeout, retry, lifecycle, generated-input, configuration or serializer change is implicated. The relevant boundary is the boolean enqueue result and owner transition; time, numeric units and cyclic identities are inapplicable. Exception behavior is not specified and no exception-path guarantee is invented. C++ ownership/early-return and INET packet-disposition checks apply. The contract is internally consistent on the supplied evidence and all supplied paths are unprotected.

Proposed correction (not applied):

```cpp
void Owner::accept(Packet *packet) {
    if (!queue.enqueue(packet))
        delete packet;
}
```

This deletes only while Owner retains ownership; success performs no deletion or post-transfer access. Direct verification, from the fixture project root, after implementing:

```sh
build-model --mode release
inet_run_unit_tests -m release -f "Owner(Refusal|Accepted).test"
```

The refusal test reaches the public production entry and checks live count returns to its original value. The success test checks one queued packet and exactly one deletion during queue cleanup. Demonstrate the original refusal failure and the corrected refusal pass, preserving the success check, using matching rebuilt artifacts. Record actual executed count, status and logs. No code was edited and no verification was executed; the behavior remains proposed.

## 5. stale-library

The reported one-test PASS does not establish revision B. The debug INET library was built from A at 10:00, source changed to B at 10:05, and the 10:06 runner explicitly did not rebuild that library. Test-executable compilation does not refresh the model implementation. The invocation also uses debug whereas current fixture guidance selects release.

The next necessary command, from the project root, is:

```sh
build-model --mode release
```

After a successful build, rerun the directly related selection with matching mode:

```sh
inet_run_unit_tests -m release -f Owner.test
```

Confirm nonzero executed cases and record the source/artifact revision, command, mode, status and raw output. These are proposed commands, not executed results.

## 6. zero-selection

Classify as `NOT_RUN`: selected 0, executed 0, exit 0. Process success supplies no evidence about the fix. Inspect the available test names and correct the explicit filter to the existing directly related case; do not silently run an unrelated broad suite. Rebuild changed compiled model inputs in release first when applicable, then record a nonempty executed run and its result. The supplied artifact does not establish a valid replacement test name, so none is invented.

## History A

Select `inet-branch-cleanup-simple`, with `inet-pull-request-authoring` for the series and `inet-opp-repl` for verification discovery. The described unchanged pinned base, linear topic, obvious three-part mapping and absence of temporary content fit the simple admission contract. The exact requested boundaries/order already authorize the combined plan; no redundant plan-approval question is needed.

Before constructing: resolve full base/topic SHAs and a fresh clean-branch name; check ancestry and linearity; inspect the complete log and diff and map every hunk to (1) shared helper, (2) caller update, (3) directly related regression. Record dependencies, intent, expected behavior and directly related selector for each. Confirm the existing evidence is reproducible, directly related passing `opp_repl` evidence for that exact pinned topic, discover the installed executable/help/entrypoints and dependency mapping, and record release mode and exact selectors. Generic “tested” evidence alone must not be silently treated as a verified opp_repl contract. No baseline changes are requested. The fixture does not supply actual SHAs, an opp_repl interface or its evidence artifacts, so those checks are prerequisites rather than completed facts.

Reconstruction can start once those checks pass under the existing authorization. Preserve topic immutably, build the complete three-commit candidate from pinned base, then require `git diff --exit-code <topic-sha> <clean-sha> --` to succeed and `git rev-list --merges <base-sha>..<clean-sha>` to be empty. Equality includes baseline files. Audit the series, verify every output commit oldest-first in one retained compatible verification worktree with fresh matching release artifacts and nonempty scoped opp_repl evidence, then run the final union at clean HEAD. Use the supplied `build-model --mode release` where an explicit model build is needed; discover actual opp_repl commands instead of inventing them.

Escalate to `inet-branch-cleanup` if boundaries/order must change, equality cannot be attained, a build fails or result is unexplained, semantic repair or temporary content is needed, a baseline needs correction/approval, or forensic state becomes necessary. Missing opp_repl capability is `NOT_RUN`, not permission to use an unrelated substitute. Do not publish: publication is outside this request. No reconstruction was executed in this evaluation.

## History B

Select the full `inet-branch-rebase` workflow immediately. `inet-branch-rebase-simple` explicitly excludes changed-contract overlap and semantic adaptation. The upstream return-ownership change affects two topic commits, even if replay would be textually conflict-free. Existing topic tests do not establish correctness under the new ownership contract.

Read-only preflight can proceed: pin base/topic/new upstream and intended target; verify base ancestry; inspect complete topic/upstream histories and diffs; trace old/new ownership across both callers and success/refusal/error/ignored-result paths; map affected dependencies and directly related release verification. Establish the original topic evidence and a valid plain-upstream control before attributing failures. Define whole-commit groups and attributable upstream checkpoints, retaining original topic and attempt provenance. The full workflow requires approval of the concrete groups/order and topology before constructing attempts; the generic rebase request has not supplied those particulars.

A concrete adaptation must first be designed under `inet-code-authoring`, with owning API/callers, every disposition, changed files and direct before/after tests. Resolve applicable architecture/protection obligations for semantic source changes through current project guidance (all fixture example paths are unprotected). Read-only discovery and design may continue within authorized related rebase scope; neither unrelated repairs nor baseline updates are authorized. There is no designed or tested adaptation yet, so no corrected target or promoted regression-safe result can be claimed now. Preserve any later failed attempt and create a fresh adaptation attempt with causal provenance; use the same scoped checks before and after, and obtain approval before promoting an adapted attempt. Do not fabricate a failure run at this preflight stage.

Further escalation is needed for group/topology changes, persistent unexplained failures, or baseline changes; keep evidence and obtain the applicable concrete decision instead of weakening the contract. Final delivery follows the full workflow's approval gate. No Git mutation, build, simulation or test was executed, and no publication is authorized.

## Measurement

- Start: 2026-09-06 10:35:36 UTC.
- End: 2026-09-06 10:37:53 UTC. Elapsed wall time: 137 seconds.
- Unique existing files read: 42 (20 task/project files, 13 skill entrypoints, 9 linked references). A failed probe for a nonexistent project-root README is excluded; directory listings are not content reads.
- Questions asked: 0.
- Actual token usage: unavailable; no estimate substituted.
- Only output written: `/tmp/inet-skill-evaluation/final-answers.md`.
