# Case answers

Applied guidance: `doc/project/README.md` → `doc/project/policies/current.md`. The supplied paths are unprotected; verification uses release mode, with a model rebuild before tests of changed model source. Commands below are proposed, not executed.

## aggregation-clean

No defect is established. The equal-weight mean of the two independent run estimates is `(10 + 20) / 2 = 15 ms`, with `n = 2` independent runs. The reductions are time weighted, use the same warm-up window and equal analysis duration, and compare fixed conditions. The 1000 within-run observations are correctly excluded from the independent repetition count. No confidence interval is claimed. No plot is needed or generated.

## fingerprint

The updater reports `UPDATE` for Demo, run 0, seed 3: `aaaa-bbbb` → `cccc-dddd`, with exit status 0. This establishes that the updater reported a replacement expected fingerprint; it does not establish behavioral correctness or a passing comparison against an independently justified expectation. Classification: `INCONCLUSIVE`.

The new expectation cannot be accepted now: both a recorded causal explanation and explicit baseline approval are absent. First explain the divergence using directly relevant evidence, obtain explicit approval for the justified expectation, and then rerun the same scoped fingerprint comparison. Exit status 0 alone does not authorize acceptance.

## ini-precedence

`Lab.sender.interval` resolves to **2s**. In `[General]`, both `**.interval = 2s` and `Lab.sender.interval = 1s` match. The supplied runtime uses written order and the first match wins, so the wildcard assignment wins despite the later assignment being more specific. The default of 5s is overridden. No inheritance chain is supplied beyond `[General]`.

This configuration does not guarantee one-second sends. To select a one-second interval under the supplied semantics, put `Lab.sender.interval = 1s` before `**.interval = 2s`. Actual sending behavior beyond parameter resolution is not provided by the fixture.

## ownership

Contract, self-validated against the supplied interfaces: `Owner::accept(Packet *)` takes ownership on entry and calls `queue.enqueue`. On refusal, enqueue retains caller ownership, so Owner must delete the packet exactly once before returning. On success, ownership transfers to the queue, and Owner must neither delete nor subsequently access it; queue cleanup supplies the terminal deletion. There are no callbacks or other consumers in this fixture. The current refusal return leaks the owned packet.

The smallest proposed change is confined to `cases/ownership/Owner.cc`; `Owner.h` supplies the unchanged contract, and `tests.txt` identifies the direct consumers used for verification. No signature, generated input, configuration, registration, or documentation change is indicated. Numeric boundaries, units, and protocol identities are N/A for this ownership-only branch; the relevant identity is the same packet pointer before disposition. The provided interface defines boolean outcomes, with no separate exception or null contract supplied.

```cpp
void Owner::accept(Packet *packet) {
    if (!queue.enqueue(packet))
        delete packet;
}
```

This covers both refusal and the successful sibling path without adding state. Direct verification, after applying the proposed change, is:

```sh
build-model --mode release
inet_run_unit_tests -m release -f "Owner(Refusal|Accepted).test"
```

Run from the active project root. Require both tests to execute and pass: `OwnerRefusal.test` reaches the public production entry with a rejecting queue and checks that live packet count returns to its original value; `OwnerAccepted.test` checks one queued packet and exactly one deletion during cleanup. These distinguish the leak fix from premature or duplicate deletion on success. C++ ownership-transition/disposition and INET packet-disposition checks support the contract. Code was not edited and verification was not run; runtime correctness remains unverified.

## stale-library

The reported one-test PASS does not establish that revision B works. The model library was built from revision A at 10:00; source changed at 10:05, and the 10:06 test build did not rebuild that library. Thus the recorded debug test does not verify the changed implementation. It also does not satisfy this project's required release-mode verification.

The next necessary command, from the project root, is:

```sh
build-model --mode release
```

After it succeeds, run:

```sh
inet_run_unit_tests -m release -f Owner.test
```

Require a fresh revision-B release library and a nonzero executed-case count before interpreting the behavioral result.

## zero-selection

Classification: **NOT_RUN**. `MissingCase.test` selected and executed zero tests. Exit status 0 reflects runner completion, not evidence that the fix works. Identify the intended existing direct test, correct the explicit filter, and rerun in release mode; if model source changed, rebuild with `build-model --mode release` first. No replacement test name can be established from this case's evidence.

## Measurement

- Elapsed wall time: 72 seconds measured from 10:23:12 UTC at initial inspection to 10:24:24 UTC after writing the answers (excluding this footer correction).
- Files read: 29 distinct files: 2 project guidance files, 6 task files, 11 raw case artifacts, 7 named SKILL.md files, the shared project-guidance-discovery reference, and the C++ and INET preventive reference files.
- Unnecessary questions: 0.
- Token/context usage: unavailable.
- Execution scope: read-only inspection plus writing this answer artifact; no builds, tests, simulator runs, baseline edits, or plots executed.
