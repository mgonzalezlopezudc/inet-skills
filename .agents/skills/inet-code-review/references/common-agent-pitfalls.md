# Common agent pitfalls

Recurring patterns where agents produce false positives, miss real findings, or misjudge scope during INET code reviews. Update this file when a new pattern is observed repeatedly.

## False positives — findings agents file that are not defects

### Retained state misidentified as a leak

Agents frequently flag `std::map` or `std::vector` entries that are retained for the lifetime of a module as memory leaks. In INET, many modules intentionally retain state (registered protocols, interface entries, cached agreements) until `finish()`, destruction, or an applicable lifecycle-operation handler. **Before calling something a leak:** trace the owner, the real cleanup path, and whether supported model cardinality bounds growth.

### Cached chunk access misidentified as a dangling pointer

The chunk API returns shared `Ptr` values. An agent that sees a raw `Chunk *` derived with `.get()` from a `Ptr` returned by `peekAtFront()` may flag it as dangling merely because the packet is later modified. **Trace whether a `Ptr` owner is retained across the access:** replacing the packet's reference does not destroy the chunk while another `Ptr` owns it, but a raw pointer that outlives every such owner is unsafe.

### Intentional tag clearing treated as data loss

Several INET modules deliberately clear sender-local tags (e.g., `DispatchProtocolReq`, `SocketReq`) after consuming them. Agents sometimes flag this as "losing metadata needed downstream." **Verify that downstream consumers actually need the tag** before filing. In most cases the tag's contract ends at the consuming module.

### Module path assumptions in unfamiliar NED compositions

Agents may assert that a module lookup like `getModuleByPath("^.interfaceTable")` is fragile or broken based on a different NED composition than the one actually in use. **Resolve the NED inheritance chain and the effective network** before claiming a path is wrong.

### Pre-existing issues outside the reviewed change

A common over-reach is to flag code that existed before the reviewed change. The review scope is the diff; pre-existing code is inspected only where the change calls it, depends on it, or makes an old defect newly material. **If the defect existed and was not worsened by the change, note it as residual risk, not a finding.**

### Undocumented-but-correct cyclic sequence comparison

Agents often flag `(a - b) & 0xFFF` or `seqGt()` style comparisons as "wrapping bugs" or "unchecked arithmetic." In IEEE 802.11, 12-bit sequence numbers use modular arithmetic with a defined half-space. **Verify the comparison against the standard's cyclic ordering definition** before claiming it is wrong.

### Multi-stage initialization stage index assumptions

Agents sometimes flag `stage == 1` or `stage == 2` in `initialize(int stage)` as out-of-order or invalid because they assume OMNeT++ uses only a single stage. In INET, initialization stages are globally coordinated across layers (e.g., `INITSTAGE_LOCAL`, `INITSTAGE_NETWORK_INTERFACE`, `INITSTAGE_APPLICATION`). **Check `src/inet/common/InitStages.h`** to see where the module fits in the multi-stage lifecycle before claiming an initialization stage index is wrong.

## Missed findings — defects agents tend to overlook

### Sibling paths not covered by a change

When a change modifies one dispatch branch (e.g., the data-frame path), agents often verify that branch thoroughly but forget to check whether the management-frame, control-frame, or error-handling sibling needs the same change. **Enumerate affected siblings explicitly.**

### Signal emission missing from new terminal paths

A new early-return, error, or lifecycle path may skip signal emissions that the normal path performs. Agents tend to verify the happy path and miss that a subscriber will never see the completion event on the new path. **Trace every terminal route for paired signal completeness.**

### Stale state after lifecycle stop/restart

Agents verify runtime behavior well but often skip the lifecycle dimension. After a supported stop/start cycle, a module must re-establish its documented operational invariants without stale timers, callbacks, or transaction generations; persistent configuration or statistics need not be reset unless their contract says so. **Check whether the change introduces state that persists incorrectly across lifecycle boundaries.**

### Non-deterministic container iteration and pointer ordering

Agents frequently overlook behavioral iteration over unordered containers and ordering by raw pointer value. An unordered container's order is unspecified for every key type, and pointer addresses vary across processes, operating systems, and allocators even in `std::map<T *, ...>`. Either can change forwarding, selection, timer scheduling, tie-breaking, or RNG-draw order. **When iteration influences the trajectory, require an explicit sort by stable semantic keys; do not recommend an ordered pointer-keyed container as the fix.**

### Insufficient effective initialization-stage count

When a class starts handling a later initialization stage, authors may forget that the effective `numInitStages()` must cover it, causing that branch to be skipped. The opposite false positive is demanding a local override even though a base class already returns enough stages. **Trace the inherited count and compare it with the highest named stage handled by the class; require a local override only when the effective count is insufficient.**

### Generated code consumers not updated

When a `.msg` field changes, agents verify the generated `_m.h` but often miss that downstream consumers (serializers, printers, dissectors, factories, or copy paths) still reference the old field name, type, or semantics. **Trace every consumer of the changed field.**

### Ownership transfer in callbacks and notifications

When a callback or listener receives an object, agents often assume it is borrowed, but INET callback APIs differ: some retain ownership at the caller while others transfer a packet or message to the callee. **Trace the concrete interface and its callers before deciding the ownership contract of any callback parameter; signal payloads remain borrowed for the emission call unless their documented contract says otherwise.**

## Calibration errors — findings that use the wrong severity or scope

### Minor issues filed as blockers

An undeclared `@unit` on a dimensionless count or a missing `@display` icon is a real convention violation but not a blocker. Use the severity calibration in [finding-quality.md](finding-quality.md) — blocker is for unavoidable corruption, crash, or invalid wire behavior.

### Architectural noncompliance reported as a correctness finding

A missing serializer or a visualization dependency in protocol code is an architectural rule violation, not a correctness defect (unless it causes runtime misbehavior). **Route these to the architectural checklist** (`AR-OBS-INTROSPECTION`, `AR-ORG-VIS-SPLIT`, etc.) rather than the correctness findings section.

### Test coverage gaps filed as standalone findings

A missing test is not a correctness finding in `inet-code-review` — it belongs in the architectural checklist under `AR-QUAL-TESTS` or `AR-WLAN-QUAL-TESTS`. Report it as residual risk in the correctness review, not as a blocking finding.
