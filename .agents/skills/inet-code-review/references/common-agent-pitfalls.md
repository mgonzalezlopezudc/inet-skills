# INET reviewer traps

Use `doc/project/guide/review-a-code-change.md` for finding thresholds and reporting.

- Modules may retain registered protocols, interface entries, and cached agreements until
  `finish()`, destruction, or a lifecycle handler. Distinguish bounded model state from growth under
  peer or transaction churn.
- Chunk APIs return shared `Ptr` values. Replacing a packet's chunk reference does not invalidate a
  raw pointer while another `Ptr` still owns that chunk; trace the retained owners across the access.
- `DispatchProtocolReq` and `SocketReq` can be deliberately cleared after consumption. Their
  sender-local contract need not extend to downstream modules.
- Resolve `getModuleByPath("^.interfaceTable")` against the effective NED composition, including
  inheritance, rather than against another node type.
- Check `src/inet/common/InitStages.h` and the inherited `numInitStages()` count. A later-stage
  branch can be unreachable; a local count override can also be unnecessary when the base covers it.
- Trace new terminal paths through paired INET signals and supported lifecycle stop/start behavior.
  Persistent configuration or statistics need not reset unless their contract requires it.
- A `.msg` field change reaches serializers, printers, dissectors, factories, and copy paths beyond
  the generated `_m.h` declaration.
- INET callback interfaces differ in packet/message ownership transfer. Signal payloads remain
  borrowed for the emission call unless their documented contract says otherwise.
- Route missing introspection artifacts or visualization dependencies to the architectural
  checklist (`AR-OBS-INTROSPECTION`, `AR-ORG-VIS-SPLIT`). A demonstrated runtime defect also belongs
  in the correctness findings, with the checklist referencing it under the canonical review guide.
