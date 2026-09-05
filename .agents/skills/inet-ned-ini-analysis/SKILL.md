---
name: inet-ned-ini-analysis
description: Analyze INET NED and omnetpp.ini configuration behavior. Use to trace module types, NED inheritance, INI config inheritance, wildcard precedence, parameter overrides, effective module paths, typename selection, radio/medium pairing, recorder paths, or configuration bugs before running or debugging simulations.
---

# Analyze NED and INI configuration

Use the NED/configuration authority described in `doc/project/design/decisions.md` and
`doc/project/rule/architecture.md`. This skill adds the concrete effective-configuration proof.

1. Identify the INI file, config/`extends` chain, run, network, and working directory.
2. Trace the relevant NED type, base types, submodule, parameter declaration/default, and `typename` assignments.
3. Evaluate every matching INI assignment using the checked-out OMNeT++ precedence rules and show why one wins.
4. Confirm paths from the actual hierarchy. `PcapRecorder.moduleNamePatterns` is relative to its containing node.
5. Check radio/medium representation compatibility and parameter units.
6. If static resolution remains ambiguous, run a short Cmdenv initialization or diagnostic.

Return the config chain, instantiated types/paths, matching assignments, winning precedence, and unresolved ambiguity.
