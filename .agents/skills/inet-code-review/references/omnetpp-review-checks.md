# OMNeT++ review checks

Apply these checks to OMNeT++ simulation-kernel contracts and model configuration. Keep INET packet and protocol semantics in the INET layer and Wi-Fi behavior in the IEEE 802.11 layer.

## Module lifecycle and initialization

- Trace the exact initialization stage that establishes each field, subscription, module reference, and published value. Resolve the checked-out version's registered stage dependencies; do not infer order from declaration order or a remembered stage list. Determine whether an event or synchronous call can observe partially initialized state.
- When overriding `initialize(int stage)`, verify that `numInitStages() const` is also overridden and returns `std::max(stage + 1, Base::numInitStages())`. If `numInitStages()` is omitted or returns a smaller count, higher initialization stages will silently never execute.
- Check `initialize()` staging, `finish()`, dynamic module creation/deletion, and destructor behavior separately. Do not assume normal end-of-simulation order matches runtime deletion.
- Respect OMNeT++ deletion order. Cleanup that traverses child modules may be safe in `finish()` or `preDelete()` but unsafe in a destructor after descendants have been destroyed.
- For cross-module calls, verify module/gate discovery direction, method-entry requirements such as `Enter_Method`, and whether the callee may retain or delete arguments.
- Check runtime parameter changes or rebuilt module relationships when the model supports them; do not validate initialization only once.

## Simulation determinism and randomness

- Enforce deterministic container iteration. Iterating over `std::unordered_map` or `std::unordered_set` with raw pointer keys (`T*`) introduces non-deterministic iteration order across architectures, allocators, and executions. When iteration order affects packet transmission, queue selection, tie-breaking, or state transitions, use ordered containers (`std::map`, `std::vector`) or sort using stable semantic keys (module ID, sequence number, interface index).
- Use OMNeT++ RNG streams (`getRNG(k)`, `cRNG`, distribution functions) for all stochastic decisions. Bypassing OMNeT++ with raw `rand()`, `std::random_device`, or host system time breaks reproducibility across seeds and runs.
- Keep wall-clock time (`std::chrono`, `time()`) out of simulation mechanics. Use `simTime()` exclusively for simulation timestamps, timeouts, and intervals; restrict wall-clock time to non-simulation diagnostic profiling.
- Treat adding, removing, or reordering an RNG draw as a first-class cause of wholesale trajectory divergence: every downstream stochastic decision in that stream re-syncs. When a fingerprint mismatch accompanies such a change, check RNG-draw order before attributing behavioral divergence to the modified logic.

## Events, messages, and timers

- State what each self-message or timer means: whole transaction, latest attempt, inactivity, delayed work, or response wait. Verify scheduling, rescheduling, cancellation, ownership, and stale delivery against that meaning. Distinct roles may need distinct timers; require at most one live timer per role and generation rather than one timer for an entire transaction.
- Trace absolute deadlines and relative durations through the complete call chain. Absolute values must reach `scheduleAt`/`rescheduleAt`, while durations must reach `scheduleAfter`/`rescheduleAfter`. Example: passing `simTime() + timeout` to a helper that reschedules *after* its argument delays expiry by the current simulation time a second time.
- For a reused self-message, decide whether a second scheduling request replaces, retains, or rejects the existing event. Use scheduling and rescheduling APIs consistently with that decision; an `isScheduled()` guard that silently ignores a new deadline is not automatically correct.
- Prove finite progress for loops inside one event and for zero-delay event chains across events. A same-time chain is valid only when each event advances a bounded progress measure and ordering is deterministic; same-instant sibling coordination may separately violate `AR-COM-DIRECT`. Example: if a busy downstream module becomes available only at a later simulation time, unbounded immediate self-message retries can prevent time from reaching that event.
- Compare `simtime_t` or floating-derived timestamps by their provenance. Exact equality is sound when both operands reuse the same stored, quantized timestamp; independently calculated values require a justified ordering, quantization, or tolerance. Example: a timer scheduled from quantized `simtime_t` duration need not equal an end time recomputed through `double` bitrate arithmetic.
- Exercise every terminal route: success, error, timeout, cancellation, shutdown, and late or duplicate events. Cleanup and completion must happen exactly once.
- Trace event ordering when correctness depends on which same-time event executes first. Do not infer ordering from source layout. Example: a response and a stale timeout at the same simulation time must not let insertion order decide whether a transaction succeeds.
- Verify that a handler cannot access a message after sending, scheduling, deleting, or transferring it, and that canceled messages retain the ownership the cleanup path expects.

## Signals, callbacks, and observability

- Test protocol or state-machine behavior when an observation listener is absent, registered later, or invoked in a different order. Report a correctness finding only when a supported behavior changes; route observer-neutrality noncompliance without a proven behavioral consequence to `AR-OBS-SIGNALS`.
- Assume signal listeners and callbacks can synchronously re-enter the emitter. Establish state or detach all affected objects before notifying when a listener can remove them.
- Verify paired semantic signal contracts. Emit removal only for an object whose addition was observable, preserve exactly-once counts, and order state establishment before re-entrant emission.
- Check signal type, source module, subscription scope, details object lifetime, and whether emitted pointers remain valid for the documented callback duration.
- Keep raw pointers retained for WATCH, inspection, deferred logging, or observer payloads live for every permitted access, and clear stale references before destroying their targets. Capture fields needed after deletion by value. Example: a watched packet pointer left in a vector during deletion can become observable only in verbose or interactive runs.
- Review recorded statistics for the actual signal path and recorder expression, not merely for a declaration in NED.

## NED, INI, and MSG integration

- Resolve NED inheritance, default expressions, gate/vector paths, parameters, `typename`, and submodule replacement against the instantiated network.
- Respect the evaluation semantics of `volatile` parameters. Caching a `volatile` parameter in a member during `initialize()` silently freezes a value defined to be re-evaluated at every read; re-reading a non-volatile parameter mid-operation is equally wrong when the contract requires a stable value. Verify that each read site's timing matches the declared volatility and the intended contract.
- Resolve INI configuration inheritance and wildcard precedence. Compare explicit overrides with inferred defaults and confirm the setting reaches the intended module instances.
- Check feature-off and optional-submodule configurations, including missing gates or empty typenames.
- Change `.msg` sources rather than generated `_m.h` or `_m.cc` files. Trace generated ownership, copying, packing/unpacking, descriptors, and consumers when a field or inheritance relationship changes.
- For every semantically consumed generated field, audit factories, success/reject paths, copies, and reconstruction paths for deliberate initialization or copying. If an optional field's schema default is also a valid value, require explicit presence or an out-of-domain sentinel only when the consumer must distinguish absence. Example: constructing a radio command to change bitrate must not make a default channel value look like an explicit channel request.

## Focused verification

Use a filtered module test or one Cmdenv configuration/run/seed when kernel behavior is necessary to prove the path. High-value cases include:

| Mechanism | High-value check |
| --- | --- |
| Initialization dependency | normal, delayed/unavailable publication, dynamic creation, `numInitStages()` match |
| Deterministic execution | pointer-key container iteration vs stable ordering across runs |
| Timer lifecycle | absolute/relative input, replace/retain/reject, stale expiry, shutdown, duplicate terminal event |
| Same-time progress | finite zero-delay chain, permanently blocked retry, response/timeout collision |
| Re-entrant signal | listener removes current object or a sibling synchronously |
| Module deletion | normal finish and runtime deletion with child teardown |
| Configuration resolution | inherited default, explicit override, wildcard collision, feature off |
| MSG change | copy, parsim pack/unpack, and derived type dispatch |

When the change can alter event trajectories, identify the exact fingerprint rows and ingredients. A passing fingerprint is regression evidence, not proof of semantic correctness. Explain the first causal divergence before attributing a mismatch, and never update fingerprint CSV files during review. Example: inserting an otherwise inert submodule may change module IDs or event-number ingredients without changing packet behavior, while a changed TXOP calculation that sends one fewer frame has a behavioral first divergence.
