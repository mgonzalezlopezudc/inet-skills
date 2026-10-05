---
name: inet-ned-ini-analysis
description: Analyze INET NED and omnetpp.ini configuration behavior before simulation execution or diagnosis. Use for module types, inheritance, wildcard precedence, parameter overrides, effective module paths, or typename selection. Also use for radio/medium compatibility, recorder paths, and configuration defects.
---

# Analyze NED and INI configuration

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to find the active checkout's NED and configuration rules.
Trace the effective configuration to prove which modules and parameter values the simulation uses.

1. Identify the INI file, config/`extends` chain, run, network, and working directory.
2. Trace the relevant NED type, base types, submodule, parameter declaration/default, and `typename` assignments.
3. Evaluate every applicable INI assignment under the checked-out OMNeT++ precedence rules.
   Explain why the selected assignment takes precedence.
4. Confirm paths from the actual module hierarchy.
   The recorder resolves `PcapRecorder.moduleNamePatterns` relative to the node that contains it.
5. Check radio/medium representation compatibility and parameter units.
6. If static resolution remains ambiguous, run a short Cmdenv initialization or diagnostic.

For example, a hypothetical node `host` contains `wlan[0]` and a recorder.
The recorder pattern `wlan[0]` selects that interface relative to `host`.
It does not require the full network path.

Return the configuration chain, instantiated types and paths, applicable assignments, precedence decision, and unresolved ambiguity.
