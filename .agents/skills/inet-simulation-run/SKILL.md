---
name: inet-simulation-run
description: Run and diagnose INET simulations using the INET launcher (`inet`) with Cmdenv or Qtenv. Use for normal simulation execution, short diagnostic runs, initialization failures, runtime errors, or requests for interactive graphical debugging.
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

Select the build mode required by the active project guidance and record it with the matching project
libraries. Use `inet --debug --printcmd` when the resolved runner, NED/image paths, or libraries
matter, if that option exists in the active launcher.
`--debug-on-errors=true` creates a debugger trap; it does not launch a debugger. Use
`inet-lldb-debugging` when source-level inspection is required.

Use the dedicated configuration, log, capture, event-log, result, or LLDB skill for deeper diagnosis.
