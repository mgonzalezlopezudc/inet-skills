---
name: omnetpp-eventlog-analysis
description: Reconstruct OMNeT++ message and event causality from event logs when Cmdenv logs and packet captures are insufficient. Use for event scheduling, message transmission, delivery, cancellation, timer behavior, self-messages, or event order.
---

# Analyze OMNeT++ event logs

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's current scope, correlation, and evidence guidance.
Use an event log when simulator scheduling or message movement is the missing evidence.
Enable it only for the selected reproduction:

```sh
--record-eventlog=true
--eventlog-file="logs/<config>-<run>.elog"
```

Restrict time only if the failure still occurs.
The event log format varies by OMNeT++ version.
Inspect the format before you use text patterns.

1. Identify the wrong or missing event, timeout, or packet transition.
2. Locate its event number, time, module, and message/tree/encapsulation identity.
3. Trace the earlier scheduling or send operation.
   Trace later delivery, cancellation, deletion, timeout, or drop operations.
4. Correlate Cmdenv by event/time and PCAP by timestamp when relevant.
5. Use LLDB only after you identify the source path or state that requires inspection.

Return the shortest chain of events that establishes the cause.
Classify that evidence under the current diagnosis guide.
