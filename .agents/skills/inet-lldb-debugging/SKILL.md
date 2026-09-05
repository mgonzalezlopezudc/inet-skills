---
name: inet-lldb-debugging
description: Debug INET and OMNeT++ simulations at the C++ source level with LLDB. Use for runtime errors, crashes, aborts, segfaults, unresolved hangs, targeted breakpoints or watchpoints, and local-variable inspection after logs, captures, event logs, or results are insufficient; use Cmdenv by default and Qtenv only when interactive visualization is also needed.
---

# Debug INET with LLDB

Select the reproduction and report the evidence under
`doc/project/guide/diagnose-a-simulation.md`. This skill adds debugger mechanics.

Use matching debug components: `opp_run_dbg`, `libINET_dbg.so`, and debug project libraries. `--debug-on-errors=true` creates a trap but does not launch LLDB.

## Workflow

1. Preserve the simulator arguments of the reproduction selected under the canonical guide.
2. Resolve the full debug command with `inet --debug --printcmd`, then launch its `opp_run_dbg` target under LLDB while retaining the resolved NED and library arguments. Put simulator arguments after LLDB's `--`:

   ```sh
   lldb -- opp_run_dbg <resolved NED/library arguments> \
     -u Cmdenv -f <ini> -c <config> -r <run> --debug-on-errors=true
   ```

   For automated capture, use `lldb -b -o run -o bt -- ...`. If an interactive transport handshake fails, use batch LLDB or direct Cmdenv rather than retrying unchanged.

3. At the first relevant stop, capture the stop reason and backtrace before continuing. Select the
   first INET/project frame exposing the suspicious state and inspect locals with `frame variable`
   before evaluating expressions that may call methods. A debugger trap identifies the stop site,
   not necessarily the defect.
4. For a lifetime investigation, trace the object address through deletion or ownership transfer.
   A watchpoint on a pointer variable detects reassignment, not destruction of its pointee.

Correlate the stopped INET/project frame with simulation time, event number, module, and packet/message identity.

Prefer side-effect-free expressions and never mutate simulation state unless the user explicitly requests an experiment. Use `inet-packet-tag-debugging` for packet metadata and the Wi-Fi debugging references for 802.11 breakpoints.

Use Cmdenv by default. Use Qtenv with `lldb-dap` only when topology/animation or event-by-event interaction is necessary.
