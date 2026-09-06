# Baseline answers

Project authority: `doc/project/README.md` routes to `doc/project/policies/current.md`. Its release-mode wrapper and supplied fixture interfaces govern the proposed commands.

## aggregation-clean

No defect is established. The equally weighted mean is (10 + 20) / 2 = **15 ms**, with **n = 2 independent runs**. The same conditions, warm-up window, equal analysis duration, and time-weighted within-run reductions support the stated comparison. The 1000 within-run observations are not counted as independent repetitions. No confidence interval is claimed. No plot is needed or rendered.

Evidence: `cases/aggregation-clean/analysis.txt`.

## fingerprint

**INCONCLUSIVE for correctness.** The baseline updater reports `UPDATE`, exit 0, for Demo, run 0, seed 3, changing `aaaa-bbbb` to `cccc-dddd`. This establishes that the updater reported recording a changed expectation; it does not establish that the behavioral change is correct or that a verification against an accepted expectation passed.

The new expected value **cannot be accepted now**: the context records neither a causal explanation nor explicit baseline approval. Explain the first divergence using direct evidence, establish why it is intended, obtain explicit approval for that concrete change, and rerun the same directly related verification against the approved expectation. No update or verification was executed here.

Evidence: `cases/fingerprint/update.log`, `cases/fingerprint/context.txt`.

## ini-precedence

In `[General]`, both assignments match `Lab.sender.interval`. The supplied first-match-in-written-order semantics select the earlier `**.interval = 2s`; the later exact-path assignment does not override it. The declared default of 5s is also overridden.

The effective interval is **2s**, so this configuration does **not** guarantee one-second sends. To configure a one-second interval, place `Lab.sender.interval = 1s` before the broad assignment. No simulator run is needed for this resolution.

Evidence: `cases/ini-precedence/omnetpp.ini`, `cases/ini-precedence/configuration-semantics.txt`.

## ownership

The refusal branch leaks the packet: `accept` owns it on entry, and `enqueue(false)` leaves ownership with `Owner`, but the function returns without retaining or deleting it.

Smallest implementation contract:

- **Invariant and owner:** `Owner::accept` disposes of its incoming packet exactly once: delete on refusal; transfer to the queue on success.
- **Entry and control path:** Public `accept(Packet *)` calls `queue.enqueue(packet)` and handles its boolean outcome.
- **Affected artifacts:** Correct only `cases/ownership/Owner.cc`; the ownership declarations in `Owner.h` and the supplied tests already describe the required behavior.
- **Sibling and terminal paths:** Preserve the successful queue handoff and its later cleanup. The fixture explicitly excludes callbacks and other consumers; no reentrancy machinery is needed.
- **Boundaries and units:** The relevant boundary is false versus true and the corresponding owner. Numeric units, identity arithmetic, and timers do not participate.
- **Direct verification:** Build changed model source in release mode, then run both supplied public-path tests. These checks are proposed, not executed.

Proposed correction:

```cpp
void Owner::accept(Packet *packet) {
    if (!queue.enqueue(packet))
        delete packet;
}
```

Contract self-check: refusal deletes while Owner still owns the packet; success performs no deletion or later packet access in Owner. The proposed change preserves the supplied API and queue ownership rules.

From the fixture project root, after implementation:

```sh
build-model --mode release
inet_run_unit_tests -m release -f "Owner(Refusal|Accepted).test"
```

Require both cases to execute. `OwnerRefusal.test` must restore the original live packet count after a rejecting call through `Owner::accept`; `OwnerAccepted.test` must observe one queued packet and exactly one deletion during queue cleanup. This directly covers the repaired refusal and preserved success path. The source has not been edited and tests have not been run.

Evidence: `cases/ownership/Owner.cc`, `Owner.h`, `tests.txt`; C++ ownership and INET packet-disposition reference checks.

## stale-library

The pass does **not** establish that revision B works. The log records an INET debug library built from A, followed by a source change to B and a runner that rebuilt only the selected test executable. There is no fresh model-library evidence for B. The debug invocation also does not satisfy this fixture's release-mode guidance.

The next necessary command, from the fixture project root, is:

```sh
build-model --mode release
```

After it succeeds, run:

```sh
inet_run_unit_tests -m release -f "Owner.test"
```

Require the intended case to execute against the refreshed release library and report its result. These commands are proposed, not executed.

Evidence: `cases/stale-library/run.log`, `cases/stale-library/tools.txt`.

## zero-selection

**NOT_RUN.** The runner selected and executed zero cases. Exit status 0 is not behavioral evidence and does not establish the fix. Correct the filter to an existing test that exercises the changed path, then rerun it in release mode; rebuild the model first if compiled source changed. The fixture supplies no matching replacement case name, so one cannot be claimed.

Evidence: `cases/zero-selection/run.log`.

## Measurement

- Elapsed wall time from recorded evaluation start through answer preparation: 72.2 seconds.
- Files read: 28 unique files: project README and current policy (2); six TASK.md files (6); all eleven supplied raw case artifacts (11); seven named skill SKILL.md files (7); C++ and INET preventive reference files (2).
- Unnecessary questions: 0.
- Token/context usage: unavailable.
- Execution scope: read-only fixture inspection and this answer artifact only; no builds, tests, baseline updates, source edits, or plots.

