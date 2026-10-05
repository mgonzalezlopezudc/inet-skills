---
name: inet-cmdenv-log-analysis
description: Analyze INET and OMNeT++ Cmdenv logs. Use for module behavior, packet decisions, drops, errors, warnings, event numbers, simulation times, or relevant context in saved output.
---

# Analyze Cmdenv logs

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's current scope, evidence, correlation, and reporting guidance. This skill adds
Cmdenv logging and search mechanics.

Save diagnostic output.
Limit the log scope to the relevant module subtree.
Useful overrides are:

```sh
--cmdenv-express-mode=false
--cmdenv-event-banners=false
'--cmdenv-log-prefix=[%l] event=%e time=%t module=%M: '
'--**.cmdenv-log-level=off'
'--<instantiated-module-path>.cmdenv-log-level=debug'
```

Search for the first error or decision.
Correlate entries by packet identity, simulation time, event number, and module:

```sh
rg -n -i 'error|warning|drop|fail|exception|runtime error' <log>
rg -n -i -C 10 '<packet|sequence|address|retry|timeout|queue>' <log>
rg -n -C 20 'event=<number>|time=<time>' <log>
```

For runtime failures, distinguish initialization from event processing.
Use `inet-lldb-debugging` when the diagnosis requires source state.
For packet behavior, trace these transitions:

- Queue insertion and removal.
- Transmission and reception.
- Drop, timeout, retry, and state changes.

Confirm headers with PCAP when necessary.
Confirm aggregate measurements with result files when necessary.

Return the shortest relevant log timeline.
Classify its evidence under the current diagnosis guide.
Correlate it as that guide requires.
