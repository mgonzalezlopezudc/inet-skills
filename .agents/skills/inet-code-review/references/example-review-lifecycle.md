# Example review — UDP application timer lifetime

This non-WLAN example demonstrates a lifecycle and ownership finding under the active project review route.
The proposed diff is hypothetical.
Every named path, class, method, API, and existing test filter was checked against INET commit `f07d0e7662dbd3d671495109326821716be82668`.

## Reviewed change (hypothetical)

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

The application owns a timer across stop and restart.
The class stores the timer as `ClockEvent *selfMsg` and creates it during `INITSTAGE_LOCAL`.
The destructor `UdpBasicApp::~UdpBasicApp()` deletes it with `cancelAndDelete(selfMsg)`.
The start handler `handleStartOperation()` and the self-message path also use the same pointer.

This review applies the General C++, OMNeT++, and INET lifecycle layers.
IEEE 802.11 is not applicable.

## Finding

### [major] Lifecycle stop leaves `selfMsg` dangling

The stop handler deletes the timer but leaves its address in `selfMsg`.
The hypothetical edit at `src/inet/applications/udpapp/UdpBasicApp.cc:234` causes this error.
After shutdown, destruction still sees the same non-null pointer.
The destructor passes that invalid pointer to `cancelAndDelete()` again.
This can cause invalid message access or a second deletion of the same object.

A supported restart before destruction also uses the invalid pointer.
The start path passes it to `setKind()` and `scheduleClockEventAt()`.
Both paths require a live timer with one owner.

Keep the reusable timer owned by the application across lifecycle stop/start.
Cancel it without deletion, as the baseline does.
If the intended contract instead requires release on stop, clear the member after deletion.
Recreate the timer before every later use, including restart.
Extend the focused lifecycle case with shutdown followed by startup to cover destruction and reuse.

## Scope and verification

- Reviewed file: `src/inet/applications/udpapp/UdpBasicApp.cc`.
- Source evidence: `UdpBasicApp::~UdpBasicApp()`, `initialize(int)`, `handleMessageWhenUp(cMessage *)`, `handleStartOperation(LifecycleOperation *)`, and `handleStopOperation(LifecycleOperation *)` in that file.
- Existing focused test: `tests/module/udpapp_lifecycle_6.test` initializes the client up and shuts it down at `2s`.
  This reaches the changed production handler and later module teardown.
  The test checks for undisposed objects but does not restart the client.
  Restart coverage remains the required extension.
- Debug command, from `tests/module` after sourcing OMNeT++, `opp_repl`, and INET environments:

  ```bash
  opp_run_opp_tests -m debug --no-concurrent -f 'udpapp_lifecycle_6'
  ```

Expected result: the existing case should pass on the clean baseline.
Under the hypothetical diff, it should fail at or before teardown.
The added stop/start variant should fail at the first timer access after restart.
It should pass once timer ownership and recreation or reuse are correct.
Neither command ran for this example, so runtime behavior is `not verified`.

## Review result

One major actionable finding. No IEEE 802.11 checklist applies. Residual risk: the existing filtered
test covers shutdown and teardown but not restart, so the correction needs the focused stop/start
extension described above.
