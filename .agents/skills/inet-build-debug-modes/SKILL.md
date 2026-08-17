---
name: inet-build-debug-modes
description: Diagnose INET build modes, generated code, and model libraries. Use to build or troubleshoot INET release/debug artifacts, stale objects, generated message code, opp_makemake or make issues, library naming, custom project libraries, or release/debug mismatches before running tests or LLDB.
---

# INET build and debug modes

Keep runner, INET library, project libraries, and build mode consistent:

- release: `inet --release`, `opp_run`, `src/libINET.so`;
- debug: `inet --debug`, `opp_run_dbg`, `src/libINET_dbg.so`.

Use `opp_run*` directly only when LLDB or an exact runner/library command requires it. Use `inet --release --printcmd` or `inet --debug --printcmd` to inspect launcher resolution.

After compiled source or generated-code inputs change, rebuild the affected library before tests or simulations. Test-local compilation does not prove that `libINET*` is fresh. Check custom project libraries and generated MSG/NED artifacts in the same mode.

When LLDB cannot resolve source, locals, or breakpoints, inspect debug symbols, optimization, loaded images, and source/binary revision:

```text
(lldb) image list
(lldb) image lookup --name '<symbol>'
```

Do not infer freshness from an existing library or mix modes. Use `inet-unit-tests` for build-before-test commands and `inet-simulation-run` for run commands.
