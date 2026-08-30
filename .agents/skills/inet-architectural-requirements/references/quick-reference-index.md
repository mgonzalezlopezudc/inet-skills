# Quick-reference index — change type to applicable requirements

Use this index to identify the most relevant `AR-*` and `AR-WLAN-*` requirements for a given change before reading the full reference documents. Load only the sections you need; read the complete documents for audits, sealing, or unfamiliar territory.

## General INET changes

| Change type | Primary requirements | Also check |
|---|---|---|
| **New NED module** | AR-MOD-COMPOSITION, AR-MOD-PLUGGABLE, AR-OBS-NED-TRUTH, AR-QUAL-NAMING, AR-QUAL-DISPLAY | AR-CFG-PARAMS, AR-OBS-SIGNALS |
| **New compound module / node type** | AR-MOD-NODEBASE, AR-MOD-COMPOSITION, AR-MOD-PLUGGABLE | AR-CFG-INFER |
| **New protocol implementation** | AR-EXT-NOCORE, AR-COM-REGISTRY, AR-COM-DISPATCH, AR-OBS-INTROSPECTION | AR-ORG-CONTRACTS, AR-QUAL-TESTS |
| **New application** | AR-COM-SOCKETS, AR-MOD-COMPOSITION | AR-CFG-PARAMS, AR-QUAL-TESTS |
| **New serializer / dissector / printer** | AR-PKT-DUAL, AR-OBS-INTROSPECTION | AR-PKT-CHUNKS |
| **New .msg file or field change** | AR-PKT-CHUNKS, AR-PKT-TAGS, AR-QUAL-NAMING | AR-PKT-DUAL (if header) |
| **Packet / chunk / tag change** | AR-PKT-CHUNKS, AR-PKT-TAGS | AR-PKT-ERRORS, AR-OBS-FLOWS |
| **Lifecycle operation change** | AR-LIFE-OPERATIONS, AR-LIFE-STAGES | AR-QUAL-TESTS |
| **Queue / scheduler / shaper change** | AR-QUEUE-ROLES, AR-QUEUE-STREAMING | AR-COM-DIRECT |
| **Signal / statistic change** | AR-OBS-SIGNALS, AR-OBS-NED-TRUTH | AR-ORG-VIS-SPLIT |
| **Visualization change** | AR-ORG-VIS-SPLIT, AR-OBS-SIGNALS | — |
| **Build / feature change** | AR-BUILD-DECLARATIVE, AR-BUILD-OUTOFTREE, AR-EXT-FEATURES | — |
| **Configuration / parameter change** | AR-CFG-PARAMS, AR-CFG-INFER | AR-OBS-NED-TRUTH |
| **Cross-module coordination** | AR-COM-DIRECT, AR-COM-DISPATCH | AR-COM-REGISTRY |
| **Dependency / include change** | AR-ORG-DOMAINS, AR-EXT-ATTACH | Run `check-architecture.sh` |
| **Naming / renaming** | AR-QUAL-NAMING | [naming-conventions.md](naming-conventions.md), [naming-exceptions.md](naming-exceptions.md) |
| **Test change** | AR-QUAL-TESTS, AR-QUAL-FINGERPRINT, AR-QUAL-TRACEABILITY | AR-QUAL-DETERMINISM |
| **Physical layer / signal change** | AR-PKT-SIGNAL, AR-MOD-FIDELITY | AR-PKT-ERRORS |

## IEEE 802.11 changes

| Change type | Primary requirements | Also check |
|---|---|---|
| **New frame / header / IE** | AR-WLAN-FRAME-REPRESENTATION, AR-WLAN-STD-TRACE | AR-PKT-DUAL, AR-OBS-INTROSPECTION |
| **MAC state machine change** | AR-WLAN-MAC-EXCHANGE, AR-WLAN-ARCH-OWNERSHIP, AR-WLAN-ARCH-BOUNDARIES | AR-WLAN-OBS-EVENTS |
| **Block Ack / sequence change** | AR-WLAN-MAC-SEQUENCE, AR-WLAN-ARCH-OWNERSHIP | AR-WLAN-QUAL-TESTS |
| **QoS / EDCA change** | AR-WLAN-MAC-QOS, AR-WLAN-ARCH-OWNERSHIP | AR-WLAN-MAC-EXCHANGE |
| **PHY mode / rate change** | AR-WLAN-PHY-AUTHORITY, AR-WLAN-PHY-TIMING | AR-WLAN-STD-GATING |
| **Timing / IFS / timeout change** | AR-WLAN-PHY-TIMING, AR-WLAN-MAC-EXCHANGE | AR-WLAN-STD-TRACE |
| **Association / management change** | AR-WLAN-ARCH-BOUNDARIES, AR-WLAN-ARCH-OWNERSHIP, AR-WLAN-STD-GATING | AR-WLAN-QUAL-TESTS |
| **MU-MIMO / OFDMA change** | AR-WLAN-MAC-MULTIUSER, AR-WLAN-ARCH-BOUNDARIES | AR-WLAN-STD-GATING |
| **New amendment gating** | AR-WLAN-STD-GATING, AR-WLAN-ARCH-VARIANTS | AR-WLAN-QUAL-TESTS |
| **802.11 signal / statistic** | AR-WLAN-OBS-EVENTS | AR-OBS-SIGNALS |

## When to read the full document

Always read the full [architectural-requirements.md](architectural-requirements.md) and/or [ieee80211-architectural-requirements.md](ieee80211-architectural-requirements.md) when:

- performing a full subsystem audit or sealing review;
- the change crosses multiple areas in the table above;
- you encounter an unfamiliar `AR-*` identifier;
- the change is architectural in nature (new contracts, dependency direction, composition patterns).
