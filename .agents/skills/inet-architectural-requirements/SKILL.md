---
name: inet-architectural-requirements
description: Apply INET architectural requirements, naming conventions, exception ledgers, enforcement checks, and source-file sealing policy. Use to design, implement, refactor, audit, or review C++, NED, MSG, configuration, build, or package changes under src/inet; evaluate INET dependency direction, contracts, composition, protocol interaction, packet representation, observability, extensibility, determinism, testing, or naming; or check, propose, grant, or remove a seal.
---

# INET architectural requirements

`doc/project/` in the active INET checkout is the only authority for project requirements, design,
rules, ledgers, enforcement, audit reports, and seals. Start with `doc/project/README.md`; do not use
copies from a skill package.

## Route the task

- For a source change, follow `doc/project/guide/contribute-a-change.md` and read only the rule and
  domain sections it makes applicable.
- For a pull-request review, follow `doc/project/guide/review-a-pull-request.md` and the canonical
  checklists under `doc/project/enforcement/checklist/`.
- For an audit or sealing task, follow `doc/project/guide/audit-a-subsystem.md`,
  `doc/project/rule/sealing.md`, and `doc/project/audit/seal-list.md`.
- Reconcile architecture and naming findings against the canonical ledgers under
  `doc/project/audit/`; use an existing audit report only for the unchanged commit and scope it
  records.

The following skill-only routing index selects canonical rule sections; it does not replace their
text:

| Change | Start with | Also inspect |
| --- | --- | --- |
| New NED module | `AR-MOD-COMPOSITION`, `AR-MOD-PLUGGABLE`, `AR-OBS-NED-TRUTH`, `AR-QUAL-NAMING`, `AR-QUAL-DISPLAY` | `AR-CFG-PARAMS`, `AR-OBS-SIGNALS` |
| New compound module or node type | `AR-MOD-NODEBASE`, `AR-MOD-COMPOSITION`, `AR-MOD-PLUGGABLE` | `AR-CFG-INFER` |
| New protocol implementation | `AR-EXT-NOCORE`, `AR-COM-REGISTRY`, `AR-COM-DISPATCH`, `AR-OBS-INTROSPECTION` | `AR-ORG-CONTRACTS`, `AR-QUAL-TESTS` |
| New application | `AR-COM-SOCKETS`, `AR-MOD-COMPOSITION` | `AR-CFG-PARAMS`, `AR-QUAL-TESTS` |
| New serializer, dissector, or printer | `AR-PKT-DUAL`, `AR-OBS-INTROSPECTION` | `AR-PKT-CHUNKS` |
| New `.msg` file or field change | `AR-PKT-CHUNKS`, `AR-PKT-TAGS`, `AR-QUAL-NAMING` | `AR-PKT-DUAL` for headers |
| Packet, chunk, or tag change | `AR-PKT-CHUNKS`, `AR-PKT-TAGS` | `AR-PKT-ERRORS`, `AR-OBS-FLOWS` |
| Lifecycle operation change | `AR-LIFE-OPERATIONS`, `AR-LIFE-STAGES` | `AR-QUAL-TESTS` |
| Queue, scheduler, or shaper change | `AR-QUEUE-ROLES`, `AR-QUEUE-STREAMING` | `AR-COM-DIRECT` |
| Cross-module coordination | `AR-COM-DIRECT`, `AR-COM-DISPATCH` | `AR-COM-REGISTRY` |
| Signal or statistic | `AR-OBS-SIGNALS`, `AR-OBS-NED-TRUTH` | `AR-ORG-VIS-SPLIT` |
| Visualization | `AR-ORG-VIS-SPLIT`, `AR-OBS-SIGNALS` | canonical observability rules |
| Configuration or parameter | `AR-CFG-PARAMS`, `AR-CFG-INFER` | `AR-OBS-NED-TRUTH`, naming |
| New or changed name | `AR-QUAL-NAMING`, `NR-*` | canonical naming ledger |
| Build or feature change | `AR-BUILD-DECLARATIVE`, `AR-BUILD-OUTOFTREE`, `AR-EXT-FEATURES` | canonical feature-matrix tests |
| Dependency or include change | `AR-ORG-DOMAINS`, `AR-EXT-ATTACH` | canonical architecture gates and ledger |
| Physical layer or signal change | `AR-PKT-SIGNAL`, `AR-MOD-FIDELITY` | `AR-PKT-ERRORS` |
| Test | `AR-QUAL-TESTS`, `AR-QUAL-FINGERPRINT`, `AR-QUAL-TRACEABILITY`, `TR-*` | `AR-QUAL-DETERMINISM` |
| Baseline | `TR-BASELINE-*` | baseline guide and `PR-SPLIT-BASELINE` |
| 802.11 frame, header, or IE | `AR-WLAN-FRAME-REPRESENTATION`, `AR-WLAN-STD-TRACE` | `AR-PKT-DUAL`, `AR-OBS-INTROSPECTION` |
| 802.11 MAC state machine | `AR-WLAN-MAC-EXCHANGE`, `AR-WLAN-ARCH-OWNERSHIP`, `AR-WLAN-ARCH-BOUNDARIES` | `AR-WLAN-OBS-EVENTS` |
| 802.11 association or management | `AR-WLAN-ARCH-BOUNDARIES`, `AR-WLAN-ARCH-OWNERSHIP`, `AR-WLAN-STD-GATING` | `AR-WLAN-QUAL-TESTS` |
| 802.11 Block Ack or sequence | `AR-WLAN-MAC-SEQUENCE`, `AR-WLAN-ARCH-OWNERSHIP` | `AR-WLAN-QUAL-TESTS` |
| 802.11 QoS or EDCA | `AR-WLAN-MAC-QOS`, `AR-WLAN-ARCH-OWNERSHIP` | `AR-WLAN-MAC-EXCHANGE` |
| 802.11 PHY mode or rate | `AR-WLAN-PHY-AUTHORITY`, `AR-WLAN-PHY-TIMING` | `AR-WLAN-STD-GATING` |
| 802.11 timing, IFS, or timeout | `AR-WLAN-PHY-TIMING`, `AR-WLAN-MAC-EXCHANGE` | `AR-WLAN-STD-TRACE` |
| 802.11 MU-MIMO or OFDMA | `AR-WLAN-MAC-MULTIUSER`, `AR-WLAN-ARCH-BOUNDARIES` | `AR-WLAN-STD-GATING` |
| 802.11 amendment gating | `AR-WLAN-STD-GATING`, `AR-WLAN-ARCH-VARIANTS` | `AR-WLAN-QUAL-TESTS` |
| 802.11 signal or statistic | `AR-WLAN-OBS-EVENTS` | `AR-OBS-SIGNALS` |

Use `inet-code-review` as well when correctness review is requested. Keep correctness findings
before canonical checklist verdicts and cross-reference a shared mechanism instead of reporting it
twice.

## Canonical enforcement gates

Run the canonical gates from the INET repository root as selected by
`doc/project/guide/run-the-gates.md`. Policy checkers live in the active checkout under
`doc/project/enforcement/`; this skill does not carry fallback copies. Before invoking one, verify
that the canonical path exists. If it does not, report `error: canonical gate missing` with the
expected path and stop; never silently substitute a checker bundled with this skill.

```sh
# Resolve proposed or changed source paths against the canonical seal registry.
doc/project/enforcement/check-source-seals.sh <affected-files...>
doc/project/enforcement/check-source-seals.sh --diff

# Check the declaration-level NED/MSG naming subset on the working tree, index, or explicit files.
python3 doc/project/enforcement/check-ned-msg-naming.py
python3 doc/project/enforcement/check-ned-msg-naming.py --staged
python3 doc/project/enforcement/check-ned-msg-naming.py src/inet/<file>.ned

# Check dependency direction, socket contracts, and deterministic source patterns.
doc/project/enforcement/check-architecture.sh src/inet/<focused-subtree>
```

`check-source-seals.sh` returns `0` only when every target is unsealed, `1` when any target is
sealed, and `2` for invalid scope or usage. A sealed result is a hard stop pending explicit user
permission. The NED/MSG naming and architecture gates return `0` for clean, `1` for candidates, and
`2` for invalid scope or usage; reconcile their candidates with the canonical rule and exception
ledger before classifying them. The gates never authorize a seal, ledger, or allowlist change.

Report the reviewed scope, canonical identifiers applied, gate commands and statuses, findings and
ledger dispositions, required approvals, and the final compliance verdict.
