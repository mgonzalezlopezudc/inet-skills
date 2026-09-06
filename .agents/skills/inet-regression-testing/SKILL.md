---
name: inet-regression-testing
description: Design protocol-neutral INET regression coverage from a behavior claim through a deterministic reproduction and direct evidence. Use to choose the matching test category, distinguish helper coverage from production-path proof, decide whether one seed or a bounded campaign is needed, and route execution to the owning test or debugging skill; use a domain specialization for protocol-specific obligations.
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

Map the changed or failing path and symbol to the selected case and invoke it with the explicit
filter required by the active project guidance. A zero-case selection is `NOT_RUN`, never a pass.

## Helper and production-path evidence

A helper-level unit test establishes the helper's computation or boundary contract. It does not
establish that a production module calls the helper, passes the intended identity or units, or lets
the result affect observable behavior. When the claim includes integration, keep useful helper
coverage and add a module or protocol test that enters through the production gate, API, or
configuration and observes the outcome. Do not copy production dispatch logic into a fixture and
call that integration evidence.

## Select failure-path probes

Use the changed mechanism to choose applicable probes: ownership transfer on refusal/error;
callback re-entry that replaces or removes state; timeout followed by late completion; repeated
cleanup; empty/singleton/multiple-item mutation; numeric limits or sequence wrap; and two independent
peers or flows. Establish reachability from the production entry point before adding a case.
Record which path each selected test reaches and what assertion would fail before the fix. A
successful command or a passing neighboring test does not establish that coverage.

## Seed and parameter scope

One fixed seed is enough when the invariant is deterministic, the reproduction reaches the exact
causal path, and the claim is about that path rather than probability, distribution, fairness, or
robustness. It is also enough to preserve a minimal reproduction of one known seeded failure.

Use a bounded campaign when the claim itself depends on randomized contention, mobility, topology,
loss, timing boundaries, a distribution, or a range of supported parameter values; when a fix may
only move a failure to another seed; or when investigating suspected flakiness. Name each varied
dimension, the finite values or seed count, the stop/failure rule, and how results are aggregated.
Adding seeds cannot repair a mismatched test category or replace direct evidence.

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
