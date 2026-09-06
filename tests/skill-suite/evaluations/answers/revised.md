# Revised-skill case answers

Authority: `doc/project/README.md` routes to `doc/project/policies/current.md`. That current guidance supplies release mode, explicit model rebuilds, ownership preservation, baseline approval, and independent-run comparison rules. All supplied example paths are unprotected.

## aggregation-clean

No defect is established. The equally weighted mean is (10 + 20) / 2 = **15 ms**, with **n = 2 independent runs**. The same warm-up window, equal analysis durations, and time-weighted state-vector reductions support the stated calculation. Within-run observations are not counted as independent repetitions, and no confidence interval is claimed. No plot or raw-result extraction is needed for this review of the supplied reduction.

## fingerprint

The updater reports changing the expected fingerprint for **Demo, run 0, seed 3**, from `aaaa-bbbb` to `cccc-dddd`, with `UPDATE` and exit status 0. This establishes a reported baseline update, not a passing comparison or proof that the behavior is correct. Its correctness classification is **INCONCLUSIVE**.

The new expectation **cannot be accepted now**: `context.txt` records neither a causal explanation nor baseline approval. Explain the first divergence using relevant behavior evidence, obtain explicit approval for the explained change, and then rerun the same directly related comparison against the approved expectation. No update or test was executed during this assessment.

## ini-precedence

In `omnetpp.ini`, `[General]` supplies both matching assignments for `Lab.sender.interval`. Under the supplied first-match-in-written-order semantics, `**.interval = 2s` wins. The later `Lab.sender.interval = 1s` does not override it, and the 5s parameter default is unused.

The effective interval is **2s**, so this configuration does **not** guarantee one-second sends. Placing `Lab.sender.interval = 1s` before the wildcard would select 1s under these semantics. There is no unresolved precedence ambiguity and no simulator run is needed.

## ownership

The defect is a leak on refusal: `accept` owns the packet on entry, and a false `enqueue` result leaves ownership with `Owner`; the existing early return loses its final disposition.

Implementation contract:

- **Invariant and owner:** `Owner::accept` gives every input packet exactly one disposition: delete on refusal or transfer to the queue on success.
- **Entry and control path:** public `Owner::accept(Packet *)` calls `queue.enqueue(packet)` once. False retains Owner ownership; true transfers ownership to the queue.
- **Affected paths and consumers:** proposed source change only in `cases/ownership/Owner.cc`; `Owner.h` documents the existing contract. The supplied fixture states there are no other consumers or callbacks. No API, generated input, configuration, or serializer changes are needed.
- **Terminal paths:** refusal deletes once; success leaves the packet queued for its existing cleanup. Callback/reentrancy work is unnecessary under the stated contract. No additional exception or lifecycle behavior is supplied, so none is invented.
- **Boundaries and units:** the relevant boundary is the boolean enqueue outcome; no timing, numeric, or identity arithmetic changes apply.
- **Direct verification:** use the existing public-API refusal test and the accepted-path queue cleanup test, after rebuilding the model in release mode.

Smallest proposed correction:

```cpp
void Owner::accept(Packet *packet) {
    if (!queue.enqueue(packet))
        delete packet;
}
```

On false, Owner still owns the packet and deletes it. On true, Owner does not delete or access the transferred packet. The contract is self-validated against the supplied declarations, implementation, and test descriptions; no edits were made.

Proposed verification from the project root, after applying the correction:

```sh
build-model --mode release
inet_run_unit_tests -m release -f "Owner(Refusal|Accepted).test"
```

Require execution of both `OwnerRefusal.test` (live count returns to its initial value through the public API) and `OwnerAccepted.test` (one queued packet and exactly one deletion at cleanup). These are direct behavioral checks; a successful build alone is insufficient. Commands were not run; exit statuses and generated artifacts are unavailable. No scope expansion is proposed. Selected preventive checks cover C++ ownership transitions/disposition and INET packet disposition; remaining evidence gap is execution of these tests on the corrected implementation.

## stale-library

The reported pass does **not** establish that revision B works. The INET library was built from revision A at 10:00; source changed to B at 10:05, and the test runner explicitly did not rebuild that library. Rebuilding only the selected test executable does not test the changed model implementation. The recorded debug invocation also does not meet this fixture's release verification requirement.

The next necessary command, from the project root, is:

```sh
build-model --mode release
```

After it succeeds, run the supported filtered release check:

```sh
inet_run_unit_tests -m release -f Owner.test
```

Record the actual executed cases and outcomes using the refreshed release library. These commands are proposed, not executed.

## zero-selection

**NOT_RUN.** The runner selected and executed **0 tests** with `-m release -f MissingCase.test`. Exit status 0 does not establish the fix or any behavioral evidence. Correct the selector using the available test inventory and rerun a directly relevant test with an explicit filter; require a nonzero executed-case count. No actual replacement test name is supplied, so none is invented.

## Measurements

- Elapsed wall time from initial timestamp to artifact preparation: 92.9 seconds.
- Files read: 29 unique files (listed below). Directory inventories were also inspected.
- Unnecessary questions: 0.
- Token/context usage: unavailable.
- Actual activity: file discovery, file reads, clock queries, and this answer artifact write only; no builds, tests, simulator runs, baseline mutations, or plots.

- `doc/project/README.md`
- `doc/project/policies/current.md`
- `cases/aggregation-clean/TASK.md`
- `cases/aggregation-clean/analysis.txt`
- `cases/fingerprint/TASK.md`
- `cases/fingerprint/context.txt`
- `cases/fingerprint/update.log`
- `cases/ini-precedence/TASK.md`
- `cases/ini-precedence/configuration-semantics.txt`
- `cases/ini-precedence/omnetpp.ini`
- `cases/ownership/Owner.cc`
- `cases/ownership/Owner.h`
- `cases/ownership/TASK.md`
- `cases/ownership/tests.txt`
- `cases/stale-library/TASK.md`
- `cases/stale-library/run.log`
- `cases/stale-library/tools.txt`
- `cases/zero-selection/TASK.md`
- `cases/zero-selection/run.log`
- `/tmp/inet-skill-evaluation/revised/.agents/skills/omnetpp-result-analysis/SKILL.md`
- `/tmp/inet-skill-evaluation/revised/.agents/skills/omnetpp-result-plotting/SKILL.md`
- `/tmp/inet-skill-evaluation/revised/.agents/skills/inet-fingerprint-regression/SKILL.md`
- `/tmp/inet-skill-evaluation/revised/.agents/skills/inet-ned-ini-analysis/SKILL.md`
- `/tmp/inet-skill-evaluation/revised/.agents/skills/inet-code-authoring/SKILL.md`
- `/tmp/inet-skill-evaluation/revised/.agents/skills/inet-build-debug-modes/SKILL.md`
- `/tmp/inet-skill-evaluation/revised/.agents/skills/inet-unit-tests/SKILL.md`
- `/tmp/inet-skill-evaluation/revised/.agents/references/project-guidance-discovery.md`
- `/tmp/inet-skill-evaluation/revised/.agents/skills/inet-code-review/references/general-cpp-review-checks.md`
- `/tmp/inet-skill-evaluation/revised/.agents/skills/inet-code-review/references/inet-review-checks.md`
