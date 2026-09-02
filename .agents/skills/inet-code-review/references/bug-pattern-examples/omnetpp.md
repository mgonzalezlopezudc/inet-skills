# OMNeT++ bug-pattern examples

These hypothetical examples illustrate the named `RP-*` prompts. They are not findings by
themselves; establish the actual contract, reachable trigger, failure mechanism, and consequence in
the reviewed change.

## 9. Zero-delay retry prevents simulation-time progress

**Related prompts:** `RP-OMNET-SAME-TIME-PROGRESS`, `RP-CPP-FINITE-PROGRESS`

A queue finds its downstream module busy and immediately sends itself another zero-delay retry. The
downstream module becomes available only at a later simulation time, which the unbounded same-time
event chain prevents the simulation from reaching.

## 10. An absolute deadline is used as a relative duration

**Related prompts:** `RP-OMNET-DEADLINE-DURATION`

At simulation time 10 s, a caller computes an absolute expiration of 12 s and passes it to a helper
that calls `rescheduleAfter(12 s, timer)`. The event is scheduled at 22 s because the two sides of
the helper disagree about whether the value is a deadline or a duration.

## 16. A generated field keeps an unintended default

**Related prompts:** `RP-OMNET-MSG-FIELD-INITIALIZATION`, `RP-OMNET-MSG-GENERATED-CONSUMERS`

An ADDBA response builder sets receiver, TID, buffer size, and timeout but never copies the request's
dialog token or initializes the status. Tests using the generated defaults pass, while a nondefault
token or rejection path exposes incorrect response contents.

## 20. Equal-looking timestamps have different provenance

**Related prompts:** `RP-OMNET-TIME-COMPARISON`

A receiver recomputes an expected end time through `double` bitrate arithmetic, while the scheduled
timer used a quantized `simtime_t` duration. Exact equality can miss by one simulation tick even
though the calculations describe the same nominal physical interval.

## 22. An old timeout races a response for a new attempt

**Related prompts:** `RP-OMNET-TIMER-ROLE`, `RP-OMNET-SAME-TIME-ORDER`, `RP-OMNET-TERMINAL-EVENTS`, `RP-WLAN-TRANSACTION-TIMERS`

An association retry allocates a new response timeout without canceling or superseding the earlier
attempt's timeout. A valid response and the stale timeout arrive at the same simulation time, making
success depend on event insertion order.

## 29. A valid generated default also means “not supplied”

**Related prompts:** `RP-OMNET-MSG-FIELD-INITIALIZATION`, `RP-CPP-API-SIGNATURE-ENUM`

A generated radio command defaults its channel field to 0, and the consumer treats every
nonnegative channel as an explicit request. Constructing the command only to change bitrate also
moves the radio to channel 0 because absence and a valid value share one representation.

## 32. Two paths schedule the same self-message

**Related prompts:** `RP-OMNET-TIMER-RESCHEDULING`, `RP-OMNET-TIMER-ROLE`

A start handler schedules `beaconTimer`, and a parameter-change callback later calls `scheduleAt`
on the same still-scheduled message. OMNeT++ rejects the second schedule; whether the new request
should replace, retain, or reject the old deadline must be decided from the timer's role.

## 35. A fingerprint changes for behavioral or ingredient reasons

**Related prompts:** `RP-OMNET-RNG-DRAW-ORDER`

A TXOP calculation sends one fewer frame, changing both the event trajectory and fingerprint. In a
different change, an empty helper module shifts module IDs while packet delivery and timing remain
equivalent. A stable new hash alone does not distinguish these cases; stochastic changes can also
shift later behavior merely by changing RNG draw order.

## 37. A signal reports a transition that did not occur

**Related prompts:** `RP-OMNET-SIGNAL-PAIRING`, `RP-OMNET-SIGNAL-PAYLOAD`, `RP-OMNET-STATISTIC-PATH`

A MAC emits `agreementAdded` for every received request, including rejected and duplicate requests.
A statistic derived as additions minus deletions therefore drifts upward even though protocol state
contains no corresponding new agreements.

## 38. A consumer can initialize before its provider is ready

**Related prompts:** `RP-OMNET-INIT-STAGE-DEPENDENCIES`, `RP-OMNET-INIT-STAGE-COUNT`

A management module reads an address from a shared MIB at one initialization stage, while the MAC
publishes it at a different stage. A composition or stage-count change makes the consumer observe a
default address because the required ordering was assumed rather than established from the active
stage definitions and dependencies.

## 39. Gate traversal assumes one concrete topology

**Related prompts:** `RP-OMNET-CROSS-MODULE-CALLS`, `RP-OMNET-OPTIONAL-CONFIGURATION`, `RP-INET-NED-COMPOSITION`

A MAC follows its upper gate, takes the next owner module, and casts it to an LLC interface. A valid
custom NED composition inserts a relay or leaves an optional path disconnected, so initialization
fails even though the traversal contract never established that exact neighbor type.

## 47. Inspection retains a pointer after object destruction

**Related prompts:** `RP-OMNET-OBSERVER-POINTER-LIFETIME`, `RP-OMNET-SIGNAL-REENTRANCY`, `RP-OMNET-SIGNAL-PAYLOAD`

A `WATCH_PTRVECTOR` still contains a packet pointer when cleanup deletes the packet and emits a
synchronous signal. An inspector, listener, or deferred log dereferences the stale pointer only in
verbose or interactive execution, making the defect configuration-sensitive.
