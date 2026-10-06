# OMNeT++ review checks

Use the shared project-guidance discovery procedure to apply the active lifecycle, observability,
configuration, determinism, and testing guidance first. This reference adds OMNeT++ kernel and
configuration failure modes.

## Determinism diagnostics

- **[RP-OMNET-RNG-DRAW-ORDER]** When a fingerprint mismatch accompanies added, removed, or reordered stochastic work, inspect RNG-draw order first: shifting one draw can change every downstream decision on that stream and obscure the local mechanism that initiated the divergence.

## Module lifecycle and initialization

- **[RP-OMNET-INIT-STAGE-DEPENDENCIES]** Trace the exact initialization stage that establishes each field, subscription, module reference, and published value. Resolve the checked-out version's registered stage dependencies; do not infer order from declaration order or a remembered stage list. Determine whether an event or synchronous call can observe partially initialized state.
- **[RP-OMNET-INIT-STAGE-COUNT]** Use the active lifecycle guidance. Identify the highest named stage the class
  actually handles and trace the effective `numInitStages()` through inheritance. Require a local
  override only when the inherited count does not cover that stage, and verify that any override is
  a stage-independent constant expression that also preserves the base requirement.
- **[RP-OMNET-LIFECYCLE-PHASES]** Check `initialize()` staging, `finish()`, dynamic module creation/deletion, and destructor behavior separately. Do not assume normal end-of-simulation order matches runtime deletion.
- **[RP-OMNET-DELETION-ORDER]** Respect OMNeT++ deletion order. Cleanup that traverses child modules may be safe in `finish()` or `preDelete()` but unsafe in a destructor after descendants have been destroyed.
- **[RP-OMNET-CROSS-MODULE-CALLS]** For cross-module calls, verify module/gate discovery direction, method-entry requirements such as `Enter_Method`, and whether the callee may retain or delete arguments.
- **[RP-OMNET-RUNTIME-RECONFIGURATION]** Check runtime parameter changes or rebuilt module relationships when the model supports them; do not validate initialization only once.

## Events, messages, and timers

- **[RP-OMNET-CALL-EVENT-BOUNDARY]** Distinguish a synchronous call chain from deferred work. Trace callbacks, signal listeners, or explicit suspension before you infer mutation within a call. Inspect event order across deferred work even when events share a timestamp. Apply the current project's simulation assumptions and minimal-design guidance.
- **[RP-OMNET-TIMER-ROLE]** Identify the protocol role and required lifetime of each timer. Check scheduling, cancellation, ownership, and reachable stale delivery against that role. Derive timer count and reuse from the actual protocol; do not impose a generic timer count per transaction or generation.
- **[RP-OMNET-DEADLINE-DURATION]** Trace absolute deadlines and relative durations through the complete call chain. Absolute values must reach `scheduleAt`/`rescheduleAt`, while durations must reach `scheduleAfter`/`rescheduleAfter`. Example: passing `simTime() + timeout` to a helper that reschedules *after* its argument delays expiry by the current simulation time a second time.
- **[RP-OMNET-TIMER-RESCHEDULING]** For a reused self-message, decide whether a second scheduling request replaces, retains, or rejects the existing event. Use scheduling and rescheduling APIs consistently with that decision; an `isScheduled()` guard that silently ignores a new deadline is not automatically correct.
- **[RP-OMNET-SAME-TIME-PROGRESS]** Prove finite progress for loops inside one event and for zero-delay event chains across events. A same-time chain is valid only when each event advances a bounded progress measure and ordering is deterministic; same-instant sibling coordination may separately violate the active direct-coordination guidance. Example: if a busy downstream module becomes available only at a later simulation time, unbounded immediate self-message retries can prevent time from reaching that event.
- **[RP-OMNET-TIME-COMPARISON]** Compare `simtime_t` or floating-derived timestamps by their provenance. Exact equality is sound when both operands reuse the same stored, quantized timestamp; independently calculated values require a justified ordering, quantization, or tolerance. Example: a timer scheduled from quantized `simtime_t` duration need not equal an end time recomputed through `double` bitrate arithmetic.
- **[RP-OMNET-TERMINAL-EVENTS]** Identify the terminal routes affected by the change and reachable under the supported contract. Check cleanup and completion on those routes. Verify cancellation through the actual owner; do not inject a callback that bypasses its cancellation guarantee. Hypothetical example: shutdown cancels a timer before expiry. A test advances simulation time beyond that expiry and verifies that the callback does not occur. This test supports the cancellation guarantee without requiring production code to handle impossible delivery.
- **[RP-OMNET-SAME-TIME-ORDER]** Trace actual event order when equal timestamps affect the result. Compare that order with the protocol requirement and supported model assumptions. Do not demand order independence unless the contract requires it. Hypothetical example: a response and timeout share a timestamp. If the contract accepts scheduler order, their different outcomes do not justify extra priority or rollback state.
- **[RP-OMNET-MESSAGE-OWNERSHIP]** Verify that a handler cannot access a message after sending, scheduling, deleting, or transferring it, and that canceled messages retain the ownership the cleanup path expects.

## Signals, callbacks, and observability

- **[RP-OMNET-HOT-CALLBACK]** For predicates or callbacks reached from scheduling, channel access, queue polling, or another hot kernel path, trace call frequency, asymptotic work, allocation, mutation, signal emission, and synchronous re-entry. Confirm a cost or re-entrancy consequence with evidence before reporting a performance defect; a nominal query may be cheap in one replaceable implementation and expensive in another.
- **[RP-OMNET-LISTENER-INDEPENDENCE]** Exercise protocol or state-machine behavior with observation listeners absent, registered later, and invoked in a different order; verify that every supported arrangement preserves behavior.
- **[RP-OMNET-SIGNAL-REENTRANCY]** Trace registered behavioral listeners, callbacks, and permitted extension behavior before you infer synchronous re-entry. If a supported listener can remove an object, check state and accesses around emission. Do not invent mutation by observers whose contract forbids it.
- **[RP-OMNET-SIGNAL-PAIRING]** Verify paired semantic signal contracts. Emit removal only for an object whose addition was observable, preserve exactly-once counts, and order state establishment before re-entrant emission.
- **[RP-OMNET-SIGNAL-PAYLOAD]** Check signal type, source module, subscription scope, details object lifetime, and whether emitted pointers remain valid for the documented callback duration.
- **[RP-OMNET-OBSERVER-POINTER-LIFETIME]** Keep raw pointers retained for WATCH, inspection, deferred logging, or observer payloads live for every permitted access, and clear stale references before destroying their targets. Capture fields needed after deletion by value. Example: a watched packet pointer left in a vector during deletion can become observable only in verbose or interactive runs.
- **[RP-OMNET-STATISTIC-PATH]** Review recorded statistics for the actual signal path and recorder expression, not merely for a declaration in NED.

## NED, INI, and MSG integration

- **[RP-OMNET-PARAMETER-VOLATILITY]** Respect the evaluation semantics of `volatile` parameters. Caching a `volatile` parameter in a member during `initialize()` silently freezes a value defined to be re-evaluated at every read; re-reading a non-volatile parameter mid-operation is equally wrong when the contract requires a stable value. Verify that each read site's timing matches the declared volatility and the intended contract.
- **[RP-OMNET-OPTIONAL-CONFIGURATION]** Check feature-off and optional-submodule configurations, including missing gates or empty typenames.
- **[RP-OMNET-MSG-GENERATED-CONSUMERS]** Trace generated ownership, copying, packing/unpacking, descriptors, and consumers when a `.msg`
  field or inheritance relationship changes.
- **[RP-OMNET-MSG-FIELD-INITIALIZATION]** For every semantically consumed generated field, audit factories, success/reject paths, copies, and reconstruction paths for deliberate initialization or copying. If an optional field's schema default is also a valid value, require explicit presence or an out-of-domain sentinel only when the consumer must distinguish absence. Example: constructing a radio command to change bitrate must not make a default channel value look like an explicit channel request.

## Focused verification

Select evidence under the active test guidance. Use a filtered module test
or one Cmdenv configuration/run/seed when kernel behavior is necessary to prove the path. High-value
cases include:

| Mechanism | High-value check |
| --- | --- |
| Initialization dependency | normal, delayed/unavailable publication, dynamic creation, `numInitStages()` match |
| Timer lifecycle | absolute/relative input, replace/retain/reject, stale expiry, shutdown, duplicate terminal event |
| Same-time progress | finite zero-delay chain, permanently blocked retry, response/timeout collision |
| Re-entrant signal | listener removes current object or a sibling synchronously |
| Module deletion | normal finish and runtime deletion with child teardown |
| Configuration resolution | inherited default, explicit override, wildcard collision, feature off |
| MSG change | copy, parsim pack/unpack, and derived type dispatch |

For trajectory changes, take fingerprint meaning and baseline handling from the active project
guidance; use
`inet-fingerprint-regression` for the operational diagnosis.
