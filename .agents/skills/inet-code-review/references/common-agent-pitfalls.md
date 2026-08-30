# Common agent pitfalls

Recurring patterns where agents produce false positives, miss real findings, or misjudge scope during INET code reviews. Update this file when a new pattern is observed repeatedly.

## False positives — findings agents file that are not defects

### Retained state misidentified as a leak

Agents frequently flag `std::map` or `std::vector` entries that are retained for the lifetime of a module as memory leaks. In INET, many modules intentionally retain state (registered protocols, interface entries, cached agreements) until `finish()` or destructor cleanup. **Before calling something a leak:** trace the owner, the cleanup path (destructor, `finish()`, `handleLifecycleOperation(STOP)`), and whether the growth is bounded.

### Cached chunk access misidentified as a dangling pointer

The chunk API uses shared-pointer semantics internally. An agent that sees a raw `Chunk *` returned from `peekAtFront()` may flag it as dangling after the packet is modified. **Check whether the pointer was obtained from a `SharedPtr`-backed operation** — the chunk remains live as long as the shared pointer does.

### Intentional tag clearing treated as data loss

Several INET modules deliberately clear sender-local tags (e.g., `DispatchProtocolReq`, `SocketReq`) after consuming them. Agents sometimes flag this as "losing metadata needed downstream." **Verify that downstream consumers actually need the tag** before filing. In most cases the tag's contract ends at the consuming module.

### Module path assumptions in unfamiliar NED compositions

Agents may assert that a module lookup like `getModuleByPath("^.interfaceTable")` is fragile or broken based on a different NED composition than the one actually in use. **Resolve the NED inheritance chain and the effective network** before claiming a path is wrong.

### Pre-existing issues outside the reviewed change

A common over-reach is to flag code that existed before the reviewed change. The review scope is the diff; pre-existing code is inspected only where the change calls it, depends on it, or makes an old defect newly material. **If the defect existed and was not worsened by the change, note it as residual risk, not a finding.**

### Undocumented-but-correct cyclic sequence comparison

Agents often flag `(a - b) & 0xFFF` or `seqGt()` style comparisons as "wrapping bugs" or "unchecked arithmetic." In IEEE 802.11, 12-bit sequence numbers use modular arithmetic with a defined half-space. **Verify the comparison against the standard's cyclic ordering definition** before claiming it is wrong.

## Missed findings — defects agents tend to overlook

### Sibling paths not covered by a change

When a change modifies one dispatch branch (e.g., the data-frame path), agents often verify that branch thoroughly but forget to check whether the management-frame, control-frame, or error-handling sibling needs the same change. **Enumerate affected siblings explicitly.**

### Signal emission missing from new terminal paths

A new early-return, error, or lifecycle path may skip signal emissions that the normal path performs. Agents tend to verify the happy path and miss that a subscriber will never see the completion event on the new path. **Trace every terminal route for paired signal completeness.**

### Stale state after lifecycle stop/restart

Agents verify runtime behavior well but often skip the lifecycle dimension. After `STOP` + `START`, modules should behave as if freshly initialized. **Check whether the change introduces state that persists incorrectly across lifecycle boundaries.**

### Generated code consumers not updated

When a `.msg` field changes, agents verify the generated `_m.h` but often miss that downstream consumers (serializers, printers, dissectors, factories, or copy paths) still reference the old field name, type, or semantics. **Trace every consumer of the changed field.**

### Ownership transfer in callbacks and notifications

When a callback or signal listener receives an object, agents often assume it is borrowed. But some INET APIs transfer ownership (e.g., `handleWithLifecycle` of lifecycle operations). **Check the documented ownership contract of every callback parameter.**

## Calibration errors — findings that use the wrong severity or scope

### Minor issues filed as blockers

An undeclared `@unit` on a dimensionless count or a missing `@display` icon is a real convention violation but not a blocker. Use the severity calibration in [finding-quality.md](finding-quality.md) — blocker is for unavoidable corruption, crash, or invalid wire behavior.

### Architectural noncompliance reported as a correctness finding

A missing serializer or a visualization dependency in protocol code is an architectural rule violation, not a correctness defect (unless it causes runtime misbehavior). **Route these to the architectural checklist** (`AR-OBS-INTROSPECTION`, `AR-ORG-VIS-SPLIT`, etc.) rather than the correctness findings section.

### Test coverage gaps filed as standalone findings

A missing test is not a correctness finding in `inet-code-review` — it belongs in the architectural checklist under `AR-QUAL-TESTS` or `AR-WLAN-QUAL-TESTS`. Report it as residual risk in the correctness review, not as a blocking finding.
