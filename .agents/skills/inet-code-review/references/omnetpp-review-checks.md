# OMNeT++ review checks

Apply these checks to OMNeT++ simulation-kernel contracts and model configuration. Keep INET packet and protocol semantics in the INET layer and Wi-Fi behavior in the IEEE 802.11 layer.

## Module lifecycle and initialization

- Trace the exact initialization stage that establishes each field, subscription, module reference, and published value. Determine whether an event or synchronous call can observe partially initialized state.
- Check `initialize()` staging, `finish()`, dynamic module creation/deletion, and destructor behavior separately. Do not assume normal end-of-simulation order matches runtime deletion.
- Respect OMNeT++ deletion order. Cleanup that traverses child modules may be safe in `finish()` or `preDelete()` but unsafe in a destructor after descendants have been destroyed.
- For cross-module calls, verify module/gate discovery direction, method-entry requirements such as `Enter_Method`, and whether the callee may retain or delete arguments.
- Check runtime parameter changes or rebuilt module relationships when the model supports them; do not validate initialization only once.

## Events, messages, and timers

- State what each self-message or timer means: whole transaction, latest attempt, inactivity, delayed work, or response wait. Verify scheduling, rescheduling, cancellation, ownership, and stale delivery against that meaning.
- Exercise every terminal route: success, error, timeout, cancellation, shutdown, and late or duplicate events. Cleanup and completion must happen exactly once.
- Trace event ordering when correctness depends on which same-time event executes first. Do not infer ordering from source layout.
- Verify that a handler cannot access a message after sending, scheduling, deleting, or transferring it, and that canceled messages retain the ownership the cleanup path expects.

## Signals, callbacks, and observability

- Test protocol or state-machine behavior when an observation listener is absent, registered later, or invoked in a different order. Report a correctness finding only when a supported behavior changes; route observer-neutrality noncompliance without a proven behavioral consequence to `AR-OBS-SIGNALS`.
- Assume signal listeners and callbacks can synchronously re-enter the emitter. Establish state or detach all affected objects before notifying when a listener can remove them.
- Verify paired semantic signal contracts. Emit removal only for an object whose addition was observable, preserve exactly-once counts, and order state establishment before re-entrant emission.
- Check signal type, source module, subscription scope, details object lifetime, and whether emitted pointers remain valid for the documented callback duration.
- Review recorded statistics for the actual signal path and recorder expression, not merely for a declaration in NED.

## NED, INI, and MSG integration

- Resolve NED inheritance, default expressions, gate/vector paths, parameters, `typename`, and submodule replacement against the instantiated network.
- Resolve INI configuration inheritance and wildcard precedence. Compare explicit overrides with inferred defaults and confirm the setting reaches the intended module instances.
- Check feature-off and optional-submodule configurations, including missing gates or empty typenames.
- Change `.msg` sources rather than generated `_m.h` or `_m.cc` files. Trace generated ownership, copying, packing/unpacking, descriptors, and consumers when a field or inheritance relationship changes.

## Focused verification

Use a filtered module test or one Cmdenv configuration/run/seed when kernel behavior is necessary to prove the path. High-value cases include:

| Mechanism | High-value check |
| --- | --- |
| Initialization dependency | normal, delayed/unavailable publication, dynamic creation |
| Timer lifecycle | reschedule, cancel, stale expiry, shutdown, duplicate terminal event |
| Re-entrant signal | listener removes current object or a sibling synchronously |
| Module deletion | normal finish and runtime deletion with child teardown |
| Configuration resolution | inherited default, explicit override, wildcard collision, feature off |
| MSG change | copy, parsim pack/unpack, and derived type dispatch |

When the change can alter event trajectories, identify the exact fingerprint rows and ingredients. A passing fingerprint is regression evidence, not proof of semantic correctness. Explain the first causal divergence before attributing a mismatch, and never update fingerprint CSV files during review.
