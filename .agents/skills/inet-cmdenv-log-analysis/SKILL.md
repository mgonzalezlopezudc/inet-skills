---
name: inet-cmdenv-log-analysis
description: Analyze INET and OMNeT++ Cmdenv logs. Use to find module behavior, packet-processing decisions, drops, errors, warnings, event numbers, simulation times, or targeted log context in saved Cmdenv output.
---

# Analyze Cmdenv logs

Save diagnostic output and target only the relevant module subtree. Useful overrides are:

```sh
--cmdenv-express-mode=false
--cmdenv-event-banners=false
'--cmdenv-log-prefix=[%l] event=%e time=%t module=%M: '
'--**.cmdenv-log-level=off'
'--<instantiated-module-path>.cmdenv-log-level=debug'
```

Adapt the module path; do not assume example node names exist.

Search for the first error or decision, then correlate by packet identity, simulation time, event number, and module:

```sh
rg -n -i 'error|warning|drop|fail|exception|runtime error' <log>
rg -n -i -C 10 '<packet|sequence|address|retry|timeout|queue>' <log>
rg -n -C 20 'event=<number>|time=<time>' <log>
```

For runtime failures, distinguish initialization from event processing and move to `inet-lldb-debugging` when source state is required. For packet behavior, trace enqueue/dequeue, transmit/receive, drop, timeout/retry, and state transitions; confirm headers with PCAP and aggregates with results when needed.

Do not confuse OMNeT++ event numbers with TShark frame numbers or infer causality from one isolated line. Return the shortest evidence-backed timeline and label inference.
