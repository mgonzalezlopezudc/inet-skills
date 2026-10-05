---
name: inet-regression-testing
description: Design protocol-neutral INET regression coverage from a behavior claim and deterministic reproduction. Select the test category and direct evidence. Distinguish helper coverage from production-path proof. Define the required seed or parameter scope. Route execution to the relevant test or diagnostic skill. Use a domain specialization for protocol requirements.
---

# INET regression testing

Turn a reported or intended behavior into the smallest durable test that would fail if that behavior
regressed. Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to
discover the active checkout's category policy and the meaning and limits of each category; do not
restate or weaken that guidance.

## Design chain

Complete this chain in order:

1. **Behavior claim** — state one externally meaningful behavior, including the relevant input,
   boundary, and expected outcome.
2. **Invariant** — express the observation that must remain true. Separate exact sequence or value
   claims from statistical or performance claims.
3. **Matching category** — select the category defined by the active project guidance. A broad
   existing suite in the wrong category is not substitute evidence.
4. **Minimal deterministic reproduction** — retain only the modules, configuration, inputs, events,
   and time window needed to reach the owner and observation. Pin the configuration, run, seed, and
   relevant parameters.
5. **Direct evidence** — choose an assertion, expected exchange, recorded output, or result that
   observes the invariant through the claimed path. Record why the expectation is correct.
6. **Bounded campaign** — decide whether the fixed reproduction is sufficient or whether explicitly
   bounded seeds or parameter values are part of the claim.

Map the changed or failed path and symbol to the selected case.
Invoke that case with the explicit filter required by the active project guidance.
A zero-case selection is `NOT_RUN`, never a pass.

## Helper and production-path evidence

A helper-level unit test establishes the helper's computation or boundary contract. It does not
establish that a production module calls the helper with the intended identity or units.
It also does not establish that the result affects observable behavior.
When the claim includes integration, retain useful helper coverage.
Add a module or protocol test through the production gate, API, or configuration.
Observe the outcome through that path.

Do not copy production dispatch logic into a fixture as a substitute for integration evidence.
In a hypothetical example, a unit test supplies a duration of two seconds to a timer helper.
The helper passes, but the production caller supplies an absolute deadline instead of a duration.
A test through that caller must detect the incorrect expiry time.

## Select failure-path probes

Choose applicable probes from the changed mechanism:

- Ownership transfer on refusal or error.
- Callback re-entry that replaces or removes state.
- Timeout followed by late completion.
- Repeated cleanup.
- Mutation of empty, singleton, or multiple-item collections.
- Numeric limits or sequence wrap.
- Two independent peers or flows.

Establish reachability from the production entry point before you add a case.
Record which path each selected test reaches and what assertion would fail before the fix. A
successful command or a passing neighboring test does not establish that coverage.

## Seed and parameter scope

One fixed seed is enough when the invariant is deterministic, the reproduction reaches the exact
causal path, and the claim is about that path rather than probability, distribution, fairness, or
robustness. It is also enough to preserve a minimal reproduction of one known seeded failure.

Use a bounded campaign under any of these conditions:

- The claim depends on randomized contention, mobility, topology, loss, timing boundaries, a distribution, or supported parameter values.
- A fix may only move a failure to another seed.
- The investigation concerns suspected flakiness.

Name each varied dimension, finite values or seed count, stop/failure rule, and result aggregation method.
Extra seeds cannot repair an incorrect test category or replace direct evidence.

The same seed must reproduce the same trajectory. A different outcome on rerun is a determinism or
test defect; do not rerun until green.

## Execution routing

- Use `inet-unit-tests` for filtered unit and module runners.
- Use `inet-simulation-run` for protocol, network, and other simulation configurations.
- Use `inet-fingerprint-regression` only as the wide net for unintended trajectory changes; it is
  never the correctness proof for new behavior.
- Use `omnetpp-result-analysis` and `omnetpp-result-plotting` for recorded-value, statistical, and
  comparative result evidence.
- Use the focused configuration, log, event-log, PCAP, packet/tag, or LLDB skill only when the
  direct evidence cannot yet explain the first divergence.
- Add a domain regression skill when protocol standards, feature gates, exchanges, or domain
  invariants impose extra obligations.

Return the behavior claim, invariant, category and rationale, minimal scenario, direct evidence,
exact filter/run/seed, campaign decision, expected failure signal before the fix, and remaining
coverage gaps.
