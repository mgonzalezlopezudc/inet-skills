# Example Pre-Write Implementation Contracts

This reference provides realistic worked examples of filled-in implementation contracts for INET C++ changes.

---

## Example 1: Full Contract (Medium / Complex Change)

### Scenario
Adding proper `ILifecycle` handling (`STOP` and `START`) and timer cancellation to `UdpEchoApp` so that node crash/restart or interface shutdown does not trigger assertion failures or leak pending timers.

```text
### Pre-Write Implementation Contract
- Invariant & Owner:
  * Invariant: When node stops or crashes, all active timers (e.g., self-messages for scheduled echo responses) must be canceled; no state mutations or packet sends may occur while STOPPED.
  * Invariant: On START, the application returns to a clean initial state ready to accept sockets and schedule events.
  * Owner: `UdpEchoApp` (inherits `OperationalBase`, implements `ILifecycle`).

- Entry Point & Control Path:
  * Lifecycle operations enter via `handleLifecycleOperation(LifecycleOperation *operation)`.
  * Production call chain: `NodeBase::handleMessage` -> `LifecycleController` -> `ILifecycle::handleLifecycleOperation`.
  * Normal event path: `handleMessageWhenUp(cMessage *msg)` processes socket data and echo timers.

- Affected Consumers & Artifacts:
  * C++: `src/inet/applications/udpapp/UdpEchoApp.h`, `UdpEchoApp.cc`.
  * NED: `src/inet/applications/udpapp/UdpEchoApp.ned` (verify `@lifecycleSupport` property if present).
  * Serializers/Registrations: None affected.
  * Sibling applications: Verify `UdpSinkApp` and `UdpBasicApp` for parallel lifecycle patterns.

- Siblings & Terminal Paths:
  * STOP operation (crash or graceful stop): Must call `cancelAndDelete(timer)` / `cancelEvent(timer)`, close active socket via `socket.close()`, and mark `isUp = false`.
  * START operation: Must reopen socket if configured to bind on startup, reset counters, and invoke `OperationalBase::handleStartOperation`.
  * Timeout expiry while stopping: Timer must be canceled before lifecycle stage transition completes.
  * Re-entrant calls: Sockets callbacks triggered during socket close must not reschedule timers.

- Boundaries & Units:
  * Time units: `simtime_t` for timers; preserve `SimTime::ZERO` vs positive delay.
  * Sockets ID: `socketId` generation tuple preserved; ensure stale socket callbacks from previous session are ignored.
  * Lifecycle stages: Stage 0 (stop application layer before transport/network shutdown).

- Mapped Verification:
  * Test command: Run lifecycle unit test or focused module test:
    `./run_unit_tests -f "inet::UdpEchoApp_Lifecycle"`
  * Reproduction: Simulation with `ScenarioManager` triggering node crash at t=5s and restart at t=10s while echo traffic is in flight.
```

---

## Example 2: Lightweight Contract (Trivial / Bounded Change)

### Scenario
Fixing an off-by-one boundary check in `ChunkBuffer::replace()` for a 1-line range condition.

```text
### Lightweight Pre-Write Contract
- Target: `src/inet/common/packet/buffer/ChunkBuffer.cc:78`
- Bug / Invariant: Offset comparison used `<` instead of `<=` causing last valid byte of chunk boundary to be rejected during replacement.
- Change: Update `offset + length < bufferLength` to `offset + length <= bufferLength`.
- Affected Siblings: Verified `ChunkBuffer::insert()` and `ChunkBuffer::remove()` already use correct boundary semantics.
- Direct Verification: Run unit test `./run_unit_tests -f "inet::ChunkBuffer_ReplaceAtBoundary"`.
```
