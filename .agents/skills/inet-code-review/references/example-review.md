# Example review — Block Ack agreement lifetime change

This is a worked example of `doc/project/guide/review-a-code-change.md`. The diff is realistic but
synthetic; canonical architecture and WLAN checklist output is intentionally not copied here.

## Reviewed change (synthetic)

The change modifies `RecipientBlockAckAgreementHandler` to persist the received Block Ack agreement state across reassociation events, so that a STA that roams back to the same AP does not need to renegotiate agreements from scratch.

```diff
--- a/src/inet/linklayer/ieee80211/mac/blockack/RecipientBlockAckAgreementHandler.cc
+++ b/src/inet/linklayer/ieee80211/mac/blockack/RecipientBlockAckAgreementHandler.cc
@@ -85,8 +85,16 @@ void RecipientBlockAckAgreementHandler::processReceivedAddbaRequest(
+    auto key = std::make_pair(addr, tid);
+    RecipientBlockAckAgreement *agreement;
+    if (auto it = preservedAgreements.find(key); it != preservedAgreements.end()) {
+        agreement = it->second;              // reuse on roam-back
+        preservedAgreements.erase(it);
+    }
+    else
+        agreement = new RecipientBlockAckAgreement(...);
     agreement->calculateExpirationTime();
+    blockAckAgreements[key] = agreement;
     emit(blockAckAgreementAddedSignal, agreement);

@@ -112,6 +115,8 @@ void RecipientBlockAckAgreementHandler::processReceivedDelba(
+    // Also remove any preserved copy
+    preservedAgreements.erase({addr, tid});
     auto it = blockAckAgreements.find({addr, tid});
     if (it != blockAckAgreements.end()) {
         emit(blockAckAgreementDeletedSignal, it->second);
         delete it->second;
         blockAckAgreements.erase(it);

@@ -130,6 +136,18 @@ void RecipientBlockAckAgreementHandler::handleDisassociation(const MacAddress& a
-    // nothing — agreements expire on their own
+    for (auto it = blockAckAgreements.begin(); it != blockAckAgreements.end(); ) {
+        if (it->first.first == addr) {
+            preservedAgreements[it->first] = it->second;
+            it = blockAckAgreements.erase(it);
+        } else
+            ++it;
+    }
 }
```

The header adds `preservedAgreements` (a `std::map`). In this synthetic subsystem, the existing signal declaration and subscribers define added/deleted events as membership changes in the active `blockAckAgreements` map.

## Layer selection

| Layer | Applied? | Reason |
|---|---|---|
| General C++ | Yes | Ownership, container, lifetime |
| OMNeT++ | Yes | Signal emission, module lifecycle |
| INET | No | No packet/chunk/tag/queue/serializer contract change |
| IEEE 802.11 | Yes | Block Ack agreement lifecycle, association, duplicate detection |

## Findings

### [major] DELBA erases an owned preserved agreement without deletion

`preservedAgreements` owns the raw agreement pointers placed into it, but `processReceivedDelba` erases a preserved entry directly at line 115 without disposing of the object.

**Invariant:** every owned object must be reachable by exactly one cleanup path (general C++ ownership).
**Trigger:** establish an agreement, disassociate so it moves to `preservedAgreements`, then receive a delayed DELBA for that peer/TID before reassociation.
**Mechanism:** `std::map::erase` does not delete the pointed-to object; after the erase no owner can reach the allocation.
**Consequence:** one agreement allocation leaks per such delayed DELBA even though the map's key count may remain bounded.

Correct this by representing map ownership with `std::unique_ptr`, or by explicitly deleting before erase and cleaning up remaining entries at destruction and any applicable lifecycle teardown. Separately decide whether preservation needs expiry based on the supported roaming model; retention alone is not a leak while it remains owned and bounded. Add a module test that delivers DELBA after disassociation, destroys the module, and asserts the agreement live-object count returns to zero.

---

### [major] Signal `blockAckAgreementDeletedSignal` not emitted when agreement is moved to preserved

`RecipientBlockAckAgreementHandler.cc:140` removes agreements from the active map without emitting `blockAckAgreementDeletedSignal`. Any subscriber tracking the active-agreement count (statistics, visualizers, or the MAC state machine) will observe an addition without a matching deletion, producing a monotonically growing count that never reflects reality.

**Invariant:** paired semantic signals must be emitted exactly once per lifecycle event, in order: added before deleted (OMNeT++ signals, AR-WLAN-OBS-EVENTS).
**Trigger:** any disassociation while a Block Ack agreement exists.
**Mechanism:** `handleDisassociation` erases from `blockAckAgreements` without emitting the deletion signal; the agreement is still alive (moved, not deleted), but it is no longer "active" from any subscriber's perspective.
**Consequence:** observer state drift; `@statistic` recording incorrect agreement count.

Emit `blockAckAgreementDeletedSignal` for each agreement moved out of the active map. When a preserved agreement is later restored, emit `blockAckAgreementAddedSignal` again. Add a test that subscribes to both signals and verifies the count reaches zero after disassociation.

---

### [moderate] Preserved agreement uses stale reorder-window state on restoration

The new reuse branch restores the original `RecipientBlockAckAgreement` object, whose reorder window (`startingSequenceNumber`, received-bitmap) reflects the last frame received before disassociation. If the peer's new ADDBA request supplies a different starting sequence number, the preserved window is never reinitialized from that request and can classify frames against the previous agreement context.

**Invariant:** Block Ack reorder-window state must reflect the current agreement context; sequence comparison uses cyclic ordering with the defined half-space (IEEE 802.11 layer, `ieee80211-review-checks.md` §Sequence, retry, and Block Ack state).
**Trigger:** peer disassociates, advances its sequence counter, then reassociates and sends a new ADDBA whose starting sequence number is ahead of the preserved window.
**Mechanism:** the reuse branch removes the old object from `preservedAgreements` and installs it as active after updating only expiration; it does not reset its reorder window from the new request.
**Consequence:** frames with sequence numbers in the gap between old window and new starting sequence are treated as "before window start" and silently dropped. Effective throughput drops until the window catches up.

Correct this by resetting the reorder window to the starting sequence number from the new ADDBA request when restoring a preserved agreement. Add a focused module test: establish agreement with SSN=0, send frames 0–10, disassociate, reassociate with SSN=100, send frame 100, and assert it is delivered (not dropped as duplicate).

## Reviewed scope

- Files: `RecipientBlockAckAgreementHandler.cc`, `.h` (diff only).
- Pre-existing code inspected: `processReceivedAddbaRequest`, `processReceivedDelba`, destruction and lifecycle handlers, signal declarations.
- Validation: read-only inspection. Runtime verification was not run, so the focused reproductions
  named above are `not verified`.

## Residual risks

- The change does not update the originator side (`OriginatorBlockAckAgreementHandler`). If the originator also persists agreements, the same leak and signal issues likely apply. Not reviewed (outside diff scope).
- No test accompanies the change; existing fingerprint coverage does not exercise reassociation with active Block Ack agreements.

## Canonical checklist output

Omitted from this mechanics example. In an actual review, any checklist `FLAG` for a mechanism
already proved above would reference the corresponding correctness finding rather than repeat it.
