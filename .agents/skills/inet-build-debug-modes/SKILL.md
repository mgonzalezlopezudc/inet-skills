---
name: inet-build-debug-modes
description: Build and diagnose INET debug artifacts, generated code, and model libraries. Use to troubleshoot stale objects, generated message code, opp_makemake or make issues, library naming, custom project libraries, or accidental release/debug mismatches before running tests or LLDB.
---

# INET debug builds

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to discover the
active checkout's required build modes, freshness obligations, and release gates. Select the mode
and toolchain from that guidance for the requested operation. The following is the technical debug
shape; project guidance decides when it is required:

- build: `make MODE=debug -j$(nproc)`;
- launcher: `inet --debug`;
- runner and INET library: `opp_run_dbg` and `src/libINET_dbg.so`;
- custom project libraries: their debug variants.

Treat a release runner or library resolved for one of these debug invocations as a mode mismatch and
correct it before continuing. Use `opp_run_dbg` directly only when LLDB or an exact runner/library
command requires it. Use `inet --debug --printcmd` to inspect launcher resolution.

Apply the discovered build-freshness requirement. Test-local compilation
does not rebuild `libINET_dbg.so`; check custom project libraries and generated MSG/NED artifacts
when diagnosing stale debug output.

When LLDB cannot resolve source, locals, or breakpoints, inspect debug symbols, optimization, loaded images, and source/binary revision:

```text
(lldb) image list
(lldb) image lookup --name '<symbol>'
```

Do not infer freshness from an existing library or mix modes within one diagnostic invocation. Use
`inet-unit-tests` for filtered test commands and `inet-simulation-run` for run commands.
