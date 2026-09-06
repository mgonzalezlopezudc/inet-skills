---
name: omnetpp-eventlog-analysis
description: Reconstruct OMNeT++ simulator-level message and event causality from event logs. Use to trace scheduling, sending, delivery, cancellation, timer behavior, self-messages, or event ordering that Cmdenv logs and packet captures do not explain.
---

# Analyze OMNeT++ event logs

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's current scope, correlation, and evidence guidance. Use an event log when simulator scheduling or message
movement is the missing evidence, and enable it only for the selected reproduction:

```sh
--record-eventlog=true
--eventlog-file="logs/<config>-<run>.elog"
```

Restrict time only if the failure still occurs. Event-log format varies by OMNeT++ version, so inspect it before relying on text patterns.

1. Identify the wrong or missing event, timeout, or packet transition.
2. Locate its event number, time, module, and message/tree/encapsulation identity.
3. Trace backward to scheduling or send and forward to delivery, cancellation, deletion, timeout, or drop.
4. Correlate Cmdenv by event/time and PCAP by timestamp when relevant.
5. Use LLDB only after identifying the source path or state requiring inspection.

Return the shortest event-log causal chain and classify it under the canonical diagnosis guide.
