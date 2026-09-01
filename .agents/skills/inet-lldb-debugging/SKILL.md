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
3. Set a targeted breakpoint before running when the path is known.
4. At the first relevant stop, record the stop reason and full backtrace.
5. Select the first INET/project frame exposing invalid state; inspect locals before expressions.
6. Use conditional breakpoints or watchpoints to find the first divergence.
7. Correlate with simulation time, event number, module, and packet/message identity.

Useful commands:

```lldb
process status
thread backtrace all
frame select <index>
frame variable --show-types
source list
breakpoint set --name <function>
breakpoint set --file <file> --line <line>
watchpoint set variable <variable>
continue
```

A pointer-variable watchpoint detects reassignment, not destruction of its pointee. For dangling pointers, identify the object address while valid and break on deletion or ownership transfer.

Prefer side-effect-free expressions and never mutate simulation state unless the user explicitly requests an experiment. Use `inet-packet-tag-debugging` for packet metadata and the Wi-Fi debugging references for 802.11 breakpoints.

Use Cmdenv by default. Use Qtenv with `lldb-dap` only when topology/animation or event-by-event interaction is necessary.

Do not continue from a trap before capturing stack and locals, treat the trap frame as root cause, or patch before the evidence identifies a defect.
