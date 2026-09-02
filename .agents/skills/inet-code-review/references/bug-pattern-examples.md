# Bug-pattern example index

Use these catalogs only when a selected `RP-*` investigation prompt is too abstract to apply
confidently or when a concrete counterexample would help challenge a reachable path. The examples
illustrate triggers and failure mechanisms; they do not establish project requirements, severity,
reachability, or a mandatory correction.

The catalogs preserve all 48 examples from the historical migration source. Entries retain their
original numbers for provenance and list the most closely related maintained prompts.
Choose the catalog by the mechanism being investigated, not merely by the changed file type.

| Primary mechanism | Catalog | Source examples |
| --- | --- | --- |
| C++ APIs, ownership, containers, algorithms, and callbacks | [General C++ examples](bug-pattern-examples/general-cpp.md) | 2–8, 14, 17, 24, 25, 28, 36, 40–45 |
| OMNeT++ lifecycle, events, timers, generated messages, signals, and inspection | [OMNeT++ examples](bug-pattern-examples/omnetpp.md) | 9, 10, 16, 20, 22, 29, 32, 35, 37–39, 47 |
| INET packets, chunks, tags, queues, lifecycle, configuration, and dispatch | [INET examples](bug-pattern-examples/inet.md) | 1, 18, 19, 21, 23, 26, 27, 30, 31, 33, 34, 46, 48 |
| IEEE 802.11 transactions, reassembly, and management wire formats | [IEEE 802.11 examples](bug-pattern-examples/ieee80211.md) | 11–13, 15 |

Read only the catalog selected by the primary mechanism. Add another catalog only when the actual
contract crosses that boundary; overlapping prompt IDs in an entry are navigation aids, not a
requirement to load every named layer.
