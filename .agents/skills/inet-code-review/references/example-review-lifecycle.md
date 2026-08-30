# Example review — Packet queue lifecycle and drop-signal change

This is a worked example showing the expected depth, format, and evidence standard for a non-802.11 INET code review involving queue lifecycle and packet drop signals.

## Reviewed change (synthetic)

The change modifies `PacketQueue` to add a high-water mark drop policy when the queue reaches capacity, but introduces state handling across `ILifecycle` transitions.

```diff
--- a/src/inet/queueing/queue/PacketQueue.cc
+++ b/src/inet/queueing/queue/PacketQueue.cc
@@ -45,6 +45,9 @@ void PacketQueue::pushPacket(Packet *packet, cGate *gate)
     if (packetCapacity != -1 && getNumPackets() >= packetCapacity) {
+        dropCount++;
+        emit(packetDroppedSignal, packet);
+        delete packet;
+        return;
     }
     queue.insert(packet);
     emit(packetPushedSignal, packet);
@@ -88,6 +91,12 @@ void PacketQueue::handleLifecycleOperation(LifecycleOperation *operation)
 {
+    if (operation->getType() == LifecycleOperation::STAGE_LOCAL) {
+        // Clear queue on crash/stop
+        queue.clear();
+    }
 }
```

## Layer selection

| Layer | Applied? | Reason |
|---|---|---|
| General C++ | Yes | Memory ownership of packets in container |
| OMNeT++ | Yes | Signal emission, lifecycle operation handling |
| INET | Yes | `Packet` ownership, drop details, `PacketDropDetails` tag |
| IEEE 802.11 | No | Not in WLAN subtree; wire contracts unchanged |

## Findings

### [blocker] `queue.clear()` leaks all queued `Packet` pointers on lifecycle stop

`PacketQueue.cc:93` calls `queue.clear()` on lifecycle stop without deleting the queued packets. `cQueue::clear()` only removes elements from the container without deleting owned `cObject`/`Packet` pointers. When a node stops or crashes, all in-flight packets held in the queue are orphaned, causing memory leaks and preventing associated packet buffer accounting from reaching zero.

**Invariant:** every packet in `PacketQueue` must be deleted via `delete packet` or passed to a drop handler on queue clear/destruction (General C++, INET queue contracts).
**Trigger:** any simulation scenario where a node containing a non-empty `PacketQueue` undergoes `handleLifecycleOperation` (e.g. node crash/stop).
**Mechanism:** `queue.clear()` empties the container without freeing elements.
**Consequence:** unbounded memory leak proportional to queued packets at crash time; stale buffer references.

Correct this by iterating over the queue and deleting each packet (or calling an explicit `clearAndPurge()` helper) before clearing the container. Add a lifecycle test verifying memory clean state after crash with 10 packets queued.

---

### [major] `emit(packetDroppedSignal, packet)` missing required `PacketDropDetails` object

`PacketQueue.cc:47` emits `packetDroppedSignal` passing only the raw `Packet*` pointer. In INET 4.x, `packetDroppedSignal` subscribers (e.g. `PacketDropVisualizer`, drop statistics collectors) expect a `PacketDropDetails` object containing the drop reason and owning module.

**Invariant:** `packetDroppedSignal` must provide `PacketDropDetails` with an explicit reason code (e.g. `QUEUE_OVERFLOW`) (INET layer, AR-OBS-SIGNALS).
**Trigger:** any packet push when `getNumPackets() >= packetCapacity`.
**Mechanism:** `emit(packetDroppedSignal, packet)` violates the subscriber signal payload contract.
**Consequence:** `check_and_cast<PacketDropDetails *>` runtime crash in connected statistics or visualizer listeners.

Correct this by creating a `PacketDropDetails` instance with reason `PacketDropReason::QUEUE_OVERFLOW` and passing it to `emit(packetDroppedSignal, packet, details)`. Add a test with a signal listener checking the drop reason.

## Reviewed scope

- Files: `src/inet/queueing/queue/PacketQueue.cc` (diff only).
- Pre-existing code inspected: `initialize`, `handleMessage`, `popPacket`, `finish`.
- Validation: debug build with focused queue test filter.

## Residual risks

- The change does not update data-rate capacity limits (`dataCapacity`), only packet counts (`packetCapacity`).

## Architecture checklist (composed with `inet-architectural-requirements`)

```
PASS — AR-ORG-VIS-SPLIT
PASS — AR-ORG-KERNEL
PASS — AR-MOD-COMPOSITION
N/A — AR-COM-SOCKETS — queue operates below transport socket boundary
PASS — AR-COM-DIRECT
PASS — AR-OBS-NED-TRUTH
PASS — AR-OBS-INTROSPECTION
PASS — AR-CFG-INFER / DRY
PASS — AR-CFG-PARAMS
PASS — AR-EXT-NOCORE
PASS — AR-BUILD-DECLARATIVE
PASS — AR-QUAL-NAMING
PASS — AR-QUAL-LOGGING
FLAG — AR-QUAL-TESTS — no unit test accompanies lifecycle stop drop verification
PASS — AR-QUAL-DISPLAY

REVIEW: 13 PASS, 1 FLAG, 0 QUESTION, 1 N/A
```
