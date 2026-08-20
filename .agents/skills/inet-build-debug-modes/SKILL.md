---
name: inet-build-debug-modes
description: Build and diagnose INET debug artifacts, generated code, and model libraries. Use to troubleshoot stale objects, generated message code, opp_makemake or make issues, library naming, custom project libraries, or accidental release/debug mismatches before running tests or LLDB.
---

# INET debug builds

Use debug mode for every build and execution, with this consistent toolchain:

- build: `make MODE=debug -j$(nproc)`;
- launcher: `inet --debug`;
- runner and INET library: `opp_run_dbg` and `src/libINET_dbg.so`;
- custom project libraries: their debug variants.

Do not build or execute release artifacts. Treat a resolved release runner or library as a mode mismatch and correct it before continuing. Use `opp_run_dbg` directly only when LLDB or an exact runner/library command requires it. Use `inet --debug --printcmd` to inspect launcher resolution.

After compiled source or generated-code inputs change, rebuild the affected debug library before tests or simulations. Test-local compilation does not prove that `libINET_dbg.so` is fresh. Check custom project libraries and generated MSG/NED artifacts in debug mode.

When LLDB cannot resolve source, locals, or breakpoints, inspect debug symbols, optimization, loaded images, and source/binary revision:

```text
(lldb) image list
(lldb) image lookup --name '<symbol>'
```

Do not infer freshness from an existing library or mix debug and release artifacts. Use `inet-unit-tests` for build-before-test commands and `inet-simulation-run` for run commands.
