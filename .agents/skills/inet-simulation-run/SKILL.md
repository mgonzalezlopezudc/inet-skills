---
name: inet-simulation-run
description: Run and diagnose INET simulations using the INET launcher (`inet`) with Cmdenv or Qtenv. Use for normal simulation execution, short diagnostic runs, initialization failures, runtime errors, or requests for interactive graphical debugging.
---

# Run INET simulations

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

Every simulation invocation must use `inet --debug` with matching debug project libraries. Do not run release-mode simulations. Use `inet --debug --printcmd` when the resolved runner, NED/image paths, or libraries matter. `--debug-on-errors=true` creates a debugger trap; it does not launch a debugger. Use `inet-lldb-debugging` when source-level inspection is required.

Use the dedicated configuration, log, capture, event-log, result, or LLDB skill for deeper diagnosis.
