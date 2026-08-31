# Verified non-WLAN contract example

This example shows how to fill and validate the full contract without inventing coverage. It was checked against INET commit `f07d0e7662dbd3d671495109326821716be82668`; reverify every fact in the active checkout before adapting it.

## Request being planned

Fix `PacketQueue::removeAllPackets()` so a queue containing more than one packet is fully drained. The current loop compares its index with the shrinking `getNumPackets()` result, so it can terminate before popping every packet.

## Filled contract

```text
### Pre-Write Implementation Contract
- Invariant & Owner: `inet::queueing::PacketQueue` owns its `cPacketQueue queue`. After `IPacketCollection::removeAllPackets()` returns, `PacketQueue::getNumPackets()` must be zero; every removed packet must produce `packetRemovedSignal` and be deleted exactly once. Preserve the existing external-buffer callback behavior.
- Entry Point & Control Path: callers invoke the virtual `IPacketCollection::removeAllPackets()` contract; dispatch reaches `PacketQueue::removeAllPackets()` in `src/inet/queueing/queue/PacketQueue.cc`. That method drains `queue`, calls `PacketBuffer::removeAllPackets()` when `buffer` is configured, emits through `PacketQueueBase::emit()`, and deletes the locally collected packets.
- Affected Consumers & Artifacts: production change is confined to `src/inet/queueing/queue/PacketQueue.cc`; the declaration in `src/inet/queueing/queue/PacketQueue.h` and interface in `src/inet/queueing/contract/IPacketCollection.h` remain unchanged. Existing `tests/queueing/Queue_1.test` exercises `PacketQueue` push/pull behavior but not this removal path.
- Siblings & Terminal Paths: preserve `removePacket()`, `pullPacket()`, `handlePacketRemoved()`, empty-queue behavior, `buffer == nullptr`, and configured-buffer behavior. Confirm each queued packet leaves the internal queue before notification/deletion and that buffer callbacks cannot cause a second removal.
- Boundaries & Units: zero and one packet already complete; two or more packets expose the shrinking-bound failure. Packet order and pointer identity must be preserved for notification/deletion; time, TID, wrap, and unit conversion are reasoned N/A because this path does not inspect those domains.
- Mapped Verification: from the INET root, `bin/inet_run_queueing_tests -m debug -f 'Queue_1[.]test$'` is an existing filtered debug regression for the same owner, but it is not direct behavioral proof. Coverage gap: no existing queueing test invokes `removeAllPackets()` on a multi-packet `PacketQueue`; add a directly focused test and update this field with its exact existing path/filter before claiming the invariant is verified. Build-only success must not close this gap.
```

## Validation result

- PASS: every field is populated without placeholders; reasoned `N/A` is limited to irrelevant boundary domains.
- PASS: the owner, interface, entry point, sibling methods, buffer callback, signal path, and named files exist in the verified checkout.
- PASS: the named command, debug flag, filter option, and `Queue_1.test` exist.
- GAP RECORDED: the existing test does not reach the defect, so implementation may not report behavioral verification until a direct filtered test is added and run.
