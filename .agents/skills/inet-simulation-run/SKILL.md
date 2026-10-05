---
name: inet-simulation-run
description: Run INET simulations with the INET launcher (`inet`) and Cmdenv or Qtenv. Use for normal execution, short diagnostic runs, initialization failures, runtime errors, or interactive graphical debugging.
---

# Run INET simulations

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's current reproduction and evidence guidance. This skill adds launcher,
working-directory, and Cmdenv/Qtenv mechanics.

Invoke the `inet` launcher directly from the intended working directory. Diagnose environment setup only after a concrete launcher failure.

Keep relative INI, result, NED, image, and library paths consistent with that working directory. Quote manually supplied semicolon-separated NED paths. Add project-specific NED roots and model libraries to the launcher defaults when required.

Use Cmdenv for automated runs:

```sh
inet --debug -u Cmdenv -f omnetpp.ini -c <config> -r <run>
```

Use Qtenv only for interactive topology, animation, state inspection, or event stepping:

```sh
inet --debug -u Qtenv -f omnetpp.ini -c <config> -r <run> --debug-on-errors=true
```

Select the build mode required by the active project guidance.
Record the mode and the project libraries that use it.
If the active launcher supports `inet --debug --printcmd`, use it to inspect runner, NED/image path, or library resolution when necessary.
`--debug-on-errors=true` creates a debugger trap; it does not launch a debugger. Use
`inet-lldb-debugging` when source-level inspection is required.

Use the dedicated configuration, log, capture, event-log, result, or LLDB skill for deeper diagnosis.
