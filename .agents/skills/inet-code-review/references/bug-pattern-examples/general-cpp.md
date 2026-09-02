# General C++ bug-pattern examples

These hypothetical examples illustrate the named `RP-*` prompts. They are not findings by
themselves; establish the actual contract, reachable trigger, failure mechanism, and consequence in
the reviewed change.

## 2. Callback registration outlives its target

**Related prompts:** `RP-CPP-CALLBACK-REGISTRATION-LIFETIME`, `RP-CPP-BORROWED-LIFETIME`

A coordinator stores raw callback pointers registered by replaceable contention modules. One module
is deleted during reconfiguration, but its registration remains, so the next notification dispatches
through a pointer to the destroyed target.

## 3. Erasing the iterator that the loop later increments

**Related prompts:** `RP-CPP-COLLECTION-MUTATION`, `RP-CPP-CALLBACK-REENTRANCY`

A reorder buffer deletes the packets in a map entry and calls `buffer.erase(it)`, after which the
loop performs `++it`. The increment operates on an invalid iterator; a callback that removes the
current or a sibling entry can create the same failure indirectly.

## 4. Crossing an index or cyclic-order boundary

**Related prompts:** `RP-CPP-NUMERIC-BOUNDARIES`, `RP-WLAN-SEQUENCE-WRAPAROUND`, `RP-WLAN-WINDOW-BOUNDARIES`

A bitmap has fragment positions 0 through 15, but a loop accepts position 16. In the same helper,
ordinary integer comparison treats sequence distance 2048 as unambiguously ordered in a 12-bit
cyclic space. Boundary cases around 0, the maximum value, wrap, and the half-space expose the two
different mistakes.

## 5. Treating a missing lookup as an impossible state

**Related prompts:** `RP-CPP-NULLABLE-RESULT`, `RP-CPP-API-OUTCOMES`, `RP-CPP-ASSERT-BOUNDARY`

`findAgreement(peer, tid)` returns null for a late or unsolicited response, but the caller passes it
to code that asserts non-null and then dereferences it. Whether absence should be ignored, rejected,
or reported comes from the public transaction contract, not from the lookup implementation.

## 6. Retaining a reference across container mutation

**Related prompts:** `RP-CPP-BORROWED-LIFETIME`, `RP-CPP-OWNERSHIP-RETURN`

`getAddress(index)` returns a reference to an element of a vector. The caller retains it while
another operation appends and sorts addresses; vector reallocation invalidates the reference before
its next use.

## 7. Retrying without a progress measure

**Related prompts:** `RP-CPP-FINITE-PROGRESS`

A frame-sequence function recursively retries whenever its child produces no step while eligibility
remains true. A permanently ineligible child keeps that predicate true without consuming input,
changing state, or reaching a terminal result, so recursion is unbounded.

## 8. A callback interrupts a multi-object ownership transfer

**Related prompts:** `RP-CPP-OWNERSHIP-DISPOSITION`, `RP-CPP-OWNERSHIP-TRANSITIONS`, `RP-CPP-ATOMIC-STATE`, `RP-CPP-CALLBACK-REENTRANCY`

A buffer detaches several victim packets and notifies their queues one by one before completing the
ownership transfer. If the second callback exits abnormally or re-enters cleanup, some packets can
be detached from the buffer while their queues still record them, leaving inconsistent ownership
and state.

## 14. A completion callback installs replacement state

**Related prompts:** `RP-CPP-CALLBACK-REENTRANCY`, `RP-CPP-ATOMIC-STATE`, `RP-WLAN-STATE-BEFORE-CALLBACK`

A contention object invokes `channelAccessGranted()` and clears its callback member afterward. The
callback synchronously begins a new contention and installs a new callback, which the returning old
handler then clears because it did not detach the completed state before external code ran.

## 17. A lookup compares only part of the identity

**Related prompts:** `RP-CPP-LOOKUP-ORDERING`, `RP-INET-STATE-SCOPING`, `RP-WLAN-STATE-CONTEXT`

An acknowledgment-state map is identified by receiver, TID, sequence number, and fragment number.
A BAR update compares only TID and sequence/fragment, so entries for another receiver with matching
numbers transition as well.

## 24. An unsigned counter wraps during repeated cleanup

**Related prompts:** `RP-CPP-NUMERIC-BOUNDARIES`, `RP-CPP-CLEANUP-IDEMPOTENCE`

A duplicate terminal callback decrements an already-zero unsigned `numPending`, wrapping it to a
large value and making the queue appear permanently nonempty. A reverse loop using `size_t i >= 0`
has the analogous non-terminating zero boundary.

## 25. Two terminal paths clean the same state

**Related prompts:** `RP-CPP-CLEANUP-IDEMPOTENCE`, `RP-OMNET-TERMINAL-EVENTS`, `RP-OMNET-SIGNAL-PAIRING`

A DELBA transmit completion and an inactivity timeout both terminate the same agreement. The first
path erases it and emits removal; the second assumes it still exists, dereferences the missing result,
or emits removal a second time.

## 28. A changed virtual signature leaves a hidden overload

**Related prompts:** `RP-CPP-API-SIGNATURE-ENUM`, `RP-CPP-API-IMPLEMENTATIONS`

A base queue changes `remove(Packet *)` to `remove(const Packet *)`, while a derived class retains
the old signature without `override`. The derived declaration is now a different overload, and calls
through the base interface no longer reach the intended implementation.

## 36. A new enum value misses classifiers and diagnostics

**Related prompts:** `RP-CPP-API-SIGNATURE-ENUM`

`AckStatus` gains `BLOCK_ACK_NOT_ARRIVED`, but `getStatusString()` and `isTerminal()` still cover
only the old values. One path fails while formatting the value and another silently classifies the
new terminal state as nonterminal.

## 40. Inconsistent meaning for a failed dynamic cast

**Related prompts:** `RP-CPP-API-OUTCOMES`, `RP-INET-PROVIDER-OUTCOMES`

A scheduler dynamically casts each connected provider to `IPacketCollection`. One operation treats
a null result as an optional capability with unknown count, while another dereferences it. The
contract must first distinguish invalid configuration from supported absence before either behavior
can be judged.

## 41. A predicate changes the state it is querying

**Related prompts:** `RP-CPP-QUERY-PURITY`, `RP-OMNET-HOT-CALLBACK`

`isFrameEligible(packet)` consumes a retry token. A search may evaluate it twice, skip it through
short-circuiting, or reorder it, so merely inspecting the queue changes which packet can transmit.
An adapter that casts away `const` and attaches a tag during the query creates the same contract
violation through a deeper call.

## 42. A read-like map lookup inserts state

**Related prompts:** `RP-CPP-QUERY-PURITY`, `RP-CPP-LOOKUP-ORDERING`

An AP evaluates `stations[address] == ASSOCIATED`. For an unknown address, `operator[]` inserts a
default station record, which later cleanup and observability code treats as a real protocol entity.

## 43. An assertion rejects supported external ordering

**Related prompts:** `RP-CPP-ASSERT-BOUNDARY`, `RP-WLAN-FRAGMENT-REASSEMBLY`

Reassembly code asserts that every received fragment number equals `nextExpected`. A supported
out-of-order fragment therefore aborts a debug simulation even though the protocol path should
buffer, reject, or otherwise handle it according to its external-input contract.

## 44. Empty, absent, and invalid providers collapse together

**Related prompts:** `RP-CPP-API-OUTCOMES`, `RP-INET-PROVIDER-OUTCOMES`

A priority scheduler reports a connected-but-empty collection as an invalid provider, while another
operation reports a provider lacking the required interface as simply empty. Count, peek, remove,
and clear consequently disagree about the same configuration.

## 45. Move-assigning an object to itself destroys its source

**Related prompts:** `RP-CPP-SELF-ALIASING`

A cache entry's move assignment first deletes destination-owned reception objects and then copies
raw pointers from the source. For `entry = std::move(entry)`, source and destination alias, so the
operation reads and retains pointers it just invalidated.
