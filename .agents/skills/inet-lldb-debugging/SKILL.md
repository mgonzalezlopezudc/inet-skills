---
name: inet-lldb-debugging
description: Debug INET and OMNeT++ simulations at C++ source level with LLDB when logs, captures, event logs, or results are insufficient. Use for runtime errors, crashes, aborts, segfaults, unresolved hangs, breakpoints, watchpoints, or local-variable inspection. Use Cmdenv by default. Use Qtenv only when interactive visualization is also necessary.
---

# Debug INET with LLDB

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's current reproduction and evidence guidance. This skill adds debugger mechanics.

Use debug components from the same build configuration: `opp_run_dbg`, `libINET_dbg.so`, and debug project libraries.
The option `--debug-on-errors=true` creates a trap but does not launch LLDB.

## Workflow

1. Preserve the simulator arguments of the reproduction selected under the canonical guide.
2. Resolve the full debug command with `inet --debug --printcmd`.
   Launch its `opp_run_dbg` target under LLDB.
   Retain the resolved NED and library arguments.
   Put simulator arguments after LLDB's `--`:

   ```sh
   lldb -- opp_run_dbg <resolved NED/library arguments> \
     -u Cmdenv -f <ini> -c <config> -r <run> --debug-on-errors=true
   ```

   For automated capture, use `lldb -b -o run -o bt -- ...`.
   If an interactive transport handshake fails, use batch LLDB or direct Cmdenv.
   Do not repeat the same failed handshake without a relevant change.

3. At the first relevant stop, capture the stop reason and backtrace.
   Select the first INET/project stack frame that exposes the suspicious state.
   Inspect locals with `frame variable` before expressions that may call methods.
   A debugger trap identifies the stop site, which need not be the defect.
4. For a lifetime investigation, trace the object address through deletion or ownership transfer.
   A watchpoint on a pointer variable detects reassignment, not destruction of its pointee.

Correlate the stopped INET/project frame with simulation time, event number, module, and packet/message identity.

Prefer expressions without side effects.
Never mutate simulation state unless the user explicitly requests an experiment.
Use `inet-packet-tag-debugging` for packet metadata.
Use the Wi-Fi debugging references for 802.11 breakpoints.

Use Cmdenv by default. Use Qtenv with `lldb-dap` only when topology/animation or event-by-event interaction is necessary.
