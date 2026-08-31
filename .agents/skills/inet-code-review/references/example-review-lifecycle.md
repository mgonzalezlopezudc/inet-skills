# Example review — UDP application timer lifetime

This concise non-WLAN example demonstrates a lifecycle and ownership finding. The proposed diff is synthetic, but every named path, class, method, API, and existing test filter was verified against INET commit `f07d0e7662dbd3d671495109326821716be82668`.

## Reviewed change (synthetic)

The change tries to release `UdpBasicApp`'s timer as soon as a lifecycle stop begins:

```diff
--- a/src/inet/applications/udpapp/UdpBasicApp.cc
+++ b/src/inet/applications/udpapp/UdpBasicApp.cc
@@ -231,7 +231,7 @@ void UdpBasicApp::handleStopOperation(LifecycleOperation *operation)
 {
-    cancelEvent(selfMsg);
+    cancelAndDelete(selfMsg);
     socket.close();
     delayActiveOperationFinish(par("stopOperationTimeout"));
 }
```

The checked-out class stores the timer as `ClockEvent *selfMsg`, creates it during `INITSTAGE_LOCAL`, and deletes it in `UdpBasicApp::~UdpBasicApp()` with `cancelAndDelete(selfMsg)`. `handleStartOperation()` and the self-message path also continue to use the same pointer. The review therefore applies the General C++, OMNeT++, and INET lifecycle layers; IEEE 802.11 is not applicable.

## Finding

### [major] Lifecycle stop leaves `selfMsg` dangling

`src/inet/applications/udpapp/UdpBasicApp.cc:234` now deletes the object stored in `selfMsg` without clearing or replacing the owning member. When a running `UdpBasicApp` is shut down, the module later reaches destruction with the same non-null pointer, violating the invariant that an owned message is deleted exactly once. `UdpBasicApp::~UdpBasicApp()` passes that dangling pointer to `cancelAndDelete()` again, causing invalid message access or a double deletion. A later supported start before destruction would likewise pass the dangling pointer to `setKind()` and `scheduleClockEventAt()`.

Keep the reusable timer owned by the application across lifecycle stop/start and cancel it without deletion, as the baseline does. If the intended contract is instead to release it on stop, clear the member after deletion and recreate it before every later use, including restart. Extend the focused lifecycle case with shutdown followed by startup to cover both destruction and reuse.

## Scope and verification

- Reviewed file: `src/inet/applications/udpapp/UdpBasicApp.cc`.
- Source evidence: `UdpBasicApp::~UdpBasicApp()`, `initialize(int)`, `handleMessageWhenUp(cMessage *)`, `handleStartOperation(LifecycleOperation *)`, and `handleStopOperation(LifecycleOperation *)` in that file.
- Existing focused test: `tests/module/udpapp_lifecycle_6.test` initializes the client up and shuts it down at `2s`, so it reaches the changed production handler and then module teardown. It checks for undisposed objects but does not restart the stopped client; restart coverage remains the required extension.
- Debug command, from `tests/module` after sourcing OMNeT++, `opp_repl`, and INET environments:

  ```bash
  opp_run_opp_tests -m debug --no-concurrent -f 'udpapp_lifecycle_6'
  ```

The existing case should pass on the clean baseline and fail under the synthetic diff at or before teardown. The added stop/start variant should fail at the first post-restart timer access and pass once single ownership and timer recreation/reuse are correct.

## Review result

One major actionable finding. No IEEE 802.11 checklist applies. Residual risk: the existing filtered test proves shutdown and teardown but not restart, so the correction needs the focused stop/start extension described above.
