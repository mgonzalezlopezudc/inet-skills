---
name: inet-build-debug-modes
description: Build INET debug artifacts, generated code, and model libraries. Diagnose stale objects, generated message code, opp_makemake or make failures, library names, and custom libraries. Use before tests or LLDB when release/debug components do not match.
---

# INET debug builds

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the active checkout's required build modes, freshness obligations, and release gates, and apply [command-execution.md](../../references/command-execution.md) for stateless `setenv` loading and external `OMNETPP_ROOT` sandbox handling. Select the mode and toolchain from that guidance for the requested operation. The following is the technical debug shape; project guidance decides when it is required:

- build: `make MODE=debug -j$(nproc)`;
- launcher: `inet --debug`;
- runner and INET library: `opp_run_dbg` and `src/libINET_dbg.so`;
- custom project libraries: their debug variants.

If a debug invocation resolves a release runner or library, the modes do not match. Correct the mismatch before the next diagnostic step. Use `opp_run_dbg` directly only when LLDB or an exact runner/library command requires it. Use `inet --debug --printcmd` to inspect launcher resolution.

For an additional model library, pass its stem to `-l` so OMNeT++ adds the platform prefix, mode suffix, and extension. For example, `inet --debug -l ./PassiveScanAudit ...` resolves `./libPassiveScanAudit_dbg.so` on Linux. A stem such as `./libPassiveScanAudit_dbg` duplicates the prefix and debug suffix. If the invocation requires an exact file, pass its path including the extension.

Apply the discovered build-freshness requirement. Test-local compilation does not rebuild `libINET_dbg.so`. For stale debug output, check custom project libraries and generated MSG/NED artifacts.

When LLDB cannot resolve source, locals, or breakpoints, inspect debug symbols, optimization, loaded images, and source/binary revision:

```text
(lldb) image list
(lldb) image lookup --name '<symbol>'
```

Do not infer freshness from an existing library. Do not mix modes within one diagnostic invocation. Use `inet-unit-tests` for filtered test commands. Use `inet-simulation-run` for run commands.
