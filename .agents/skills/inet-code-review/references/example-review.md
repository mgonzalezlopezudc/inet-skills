# Example review — Block Ack agreement lifetime change

This is a worked example showing the expected depth, format, and evidence standard for an INET code review. The diff is realistic but synthetic; the findings illustrate the layered review approach and composition with the architectural checklist.

## Reviewed change (synthetic)

The change modifies `RecipientBlockAckAgreementHandler` to persist the received Block Ack agreement state across reassociation events, so that a STA that roams back to the same AP does not need to renegotiate agreements from scratch.

```diff
--- a/src/inet/linklayer/ieee80211/mac/blockack/RecipientBlockAckAgreementHandler.cc
+++ b/src/inet/linklayer/ieee80211/mac/blockack/RecipientBlockAckAgreementHandler.cc
@@ -85,8 +85,11 @@ void RecipientBlockAckAgreementHandler::processReceivedAddbaRequest(
     auto agreement = new RecipientBlockAckAgreement(...);
     agreement->calculateExpirationTime();
-    blockAckAgreements[{addr, tid}] = agreement;
+    auto key = std::make_pair(addr, tid);
+    if (auto it = blockAckAgreements.find(key); it != blockAckAgreements.end()) {
+        preservedAgreements[key] = it->second;   // keep old for roam-back
+    }
+    blockAckAgreements[key] = agreement;
     emit(blockAckAgreementAddedSignal, agreement);

@@ -112,6 +115,9 @@ void RecipientBlockAckAgreementHandler::processReceivedDelba(
     auto it = blockAckAgreements.find({addr, tid});
     if (it != blockAckAgreements.end()) {
+        // Also remove any preserved copy
+        preservedAgreements.erase({addr, tid});
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
+}
+
+RecipientBlockAckAgreement *RecipientBlockAckAgreementHandler::findPreservedAgreement(
+        const MacAddress& addr, int tid) {
+    auto it = preservedAgreements.find({addr, tid});
+    if (it != preservedAgreements.end())
+        return it->second;
+    return nullptr;
 }
```

The header adds `preservedAgreements` (a `std::map`) and the `findPreservedAgreement` accessor.

## Layer selection

| Layer | Applied? | Reason |
|---|---|---|
| General C++ | Yes | Ownership, container, lifetime |
| OMNeT++ | Yes | Signal emission, module lifecycle |
| INET | No | No packet/chunk/tag/queue/serializer contract change |
| IEEE 802.11 | Yes | Block Ack agreement lifecycle, association, duplicate detection |

## Findings

### [major] Preserved agreements are never deleted — unbounded memory growth

`RecipientBlockAckAgreementHandler.cc:140` moves agreements into `preservedAgreements` on disassociation but no path ever deletes them. `processReceivedDelba` erases the key but only when a DELBA arrives for the *current* agreement (line 117); a preserved agreement whose peer never reassociates is retained for the life of the simulation. When `handleDisassociation` is called repeatedly for the same peer with different TIDs — or for many peers in a high-mobility scenario — `preservedAgreements` grows without bound.

**Invariant:** every owned object must be reachable by exactly one cleanup path (general C++ ownership).
**Trigger:** any scenario where a STA associates, establishes Block Ack, disassociates, and never returns. Reachable with ≥2 APs and one mobile STA.
**Mechanism:** `preservedAgreements` retains `new`-allocated agreements; no expiration timer, destructor cleanup, or lifecycle-stop handler covers them.
**Consequence:** monotonic memory growth proportional to `(peers × TIDs × disassociation events)`.

Correct this by adding expiration for preserved agreements (e.g., reuse the same inactivity timeout), and by deleting all remaining entries in the destructor and in `handleLifecycleOperation(STOP)`. Add a module test with 3 association/disassociation cycles and assert the count of live agreements returns to zero.

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

`findPreservedAgreement` returns the original `RecipientBlockAckAgreement` object, whose reorder window (`startingSequenceNumber`, received-bitmap) reflects the last frame received before disassociation. If the peer reassociates and resumes transmission with a higher sequence number (as permitted by IEEE 802.11-2020 §10.24.7.7), the stale window will classify new frames as duplicates and drop them until the window advances past the gap.

**Invariant:** Block Ack reorder-window state must reflect the current agreement context; sequence comparison uses cyclic ordering with the defined half-space (IEEE 802.11 layer, `ieee80211-review-checks.md` §Sequence, retry, and Block Ack state).
**Trigger:** peer disassociates, advances its sequence counter (e.g., sends to another AP), then reassociates and resumes with a new ADDBA whose starting sequence number is ahead of the preserved window.
**Mechanism:** `findPreservedAgreement` returns the old object whose window has not been reset; the ADDBA processing path at line 88 installs it as-is.
**Consequence:** frames with sequence numbers in the gap between old window and new starting sequence are treated as "before window start" and silently dropped. Effective throughput drops until the window catches up.

Correct this by resetting the reorder window to the starting sequence number from the new ADDBA request when restoring a preserved agreement. Add a focused module test: establish agreement with SSN=0, send frames 0–10, disassociate, reassociate with SSN=100, send frame 100, and assert it is delivered (not dropped as duplicate).

## Reviewed scope

- Files: `RecipientBlockAckAgreementHandler.cc`, `.h` (diff only).
- Pre-existing code inspected: `processReceivedAddbaRequest`, `processReceivedDelba`, destructor, `handleLifecycleOperation`, signal declarations.
- Validation: read-only inspection; no runtime execution (findings are structural with clear reachability).

## Residual risks

- The change does not update the originator side (`OriginatorBlockAckAgreementHandler`). If the originator also persists agreements, the same leak and signal issues likely apply. Not reviewed (outside diff scope).
- No test accompanies the change; existing fingerprint coverage does not exercise reassociation with active Block Ack agreements.

## Architecture checklist (composed with `inet-architectural-requirements`)

```
PASS — AR-ORG-VIS-SPLIT
PASS — AR-ORG-KERNEL
PASS — AR-MOD-COMPOSITION
PASS — AR-COM-SOCKETS
PASS — AR-COM-DIRECT
PASS — AR-OBS-NED-TRUTH
PASS — AR-OBS-INTROSPECTION
PASS — AR-CFG-INFER / DRY
PASS — AR-CFG-PARAMS
PASS — AR-EXT-NOCORE
PASS — AR-BUILD-DECLARATIVE
PASS — AR-QUAL-NAMING
PASS — AR-QUAL-LOGGING
FLAG — AR-QUAL-TESTS — no test accompanies the change (see finding #1 verification)
PASS — AR-QUAL-DISPLAY

REVIEW: 14 PASS, 1 FLAG, 0 QUESTION
```

```
PASS — AR-WLAN-STD-TRACE
PASS — AR-WLAN-STD-GATING
PASS — AR-WLAN-ARCH-BOUNDARIES
FLAG — AR-WLAN-ARCH-OWNERSHIP — preservedAgreements duplicates agreement ownership (see finding #1)
PASS — AR-WLAN-ARCH-VARIANTS
PASS — AR-WLAN-FRAME-REPRESENTATION
PASS — AR-WLAN-PHY-AUTHORITY
PASS — AR-WLAN-PHY-TIMING
PASS — AR-WLAN-MAC-EXCHANGE
FLAG — AR-WLAN-MAC-SEQUENCE — stale reorder window on restoration (see finding #3)
PASS — AR-WLAN-MAC-QOS
PASS — AR-WLAN-MAC-MULTIUSER
FLAG — AR-WLAN-OBS-EVENTS — missing deletion signal on move-to-preserved (see finding #2)
FLAG — AR-WLAN-QUAL-TESTS — no focused test for agreement preservation lifecycle

WLAN REVIEW: 10 PASS, 4 FLAG, 0 QUESTION
```
