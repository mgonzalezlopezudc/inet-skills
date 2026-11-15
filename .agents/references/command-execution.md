# Reliable command execution

Apply these rules across builds, tests, Git operations, searches, and repository scripts to avoid repeated command failures.

## Stateless shells and OMNeT++ environment

Each command invocation runs in a fresh shell session; exported variables and `source` calls do not persist across separate commands.

- When OMNeT++ or `opp_repl` tools (`opp_featuretool`, `opp_makemake`, `opp_msgtool`, `opp_run`, `opp_run_dbg`, `opp_test`, `opp_scavetool`, `opp_repl`, `opp_run_*_tests`, `opp_update_*_test_results`) are not already on `PATH` inside the command environment, load the checkout's `.envrc` or run `source "$OMNETPP_ROOT/setenv" && source setenv` in the **same** command from the INET root.
- If `OMNETPP_ROOT` is unset, read `.envrc` or the checkout's installation/build documentation instead of probing guessed paths.
- Check tool availability once with `command -v <tool>`.

## Workspace-isolated sandboxes and external paths

In workspace-isolated sandboxes, external toolchains and repository metadata outside the workspace root are hidden unless explicitly mounted:

- **OMNeT++ and `opp_repl` toolchains**: `OMNETPP_ROOT` and its Python `.venv` typically reside outside the INET workspace. Check once whether `opp_featuretool` or the required `opp_run_*_tests` executable is accessible inside the sandbox. If that single check fails with `command not found` or `No such file or directory` because `OMNETPP_ROOT` is outside the sandbox, do **not** keep trying `make` (which calls `opp_featuretool` and `opp_makemake`), `opp_*`, or `inet` inside the sandbox first — run those toolchain commands directly with sandbox bypass (`BypassSandbox: true` where supported). Keep file searches and workspace-local commands sandboxed.
- **Git worktrees and mutating Git commands**: When `.git` is a regular file (`gitdir: ...`) pointing to a main repository `.git/worktrees/...` directory outside the worktree workspace, `git` commands fail inside a workspace-isolated sandbox with `fatal: not a git repository: ...`, and scripts that invoke `git` (such as commit or series checks) also fail. Similarly, when `.git/` is mounted read-only in a sandbox, mutating `git` commands (`git add`, `git commit`, `git checkout`, `git rebase`) fail with `Read-only file system`. Check once with `test -f .git` or one `git status`. Once confirmed, run subsequent `git` commands (or mutating `git` operations) and git-dependent repository scripts directly outside the sandbox (`BypassSandbox: true` where supported).
- **External sibling repositories**: When `statistics`, `media`, or `standards` paths resolve outside the workspace and fail inside the sandbox, run commands that read or update those paths outside the sandbox rather than retrying in the sandbox.

## Repository script flags

- Before running a checkout's helper or enforcement script (such as commit, link, seal, or pull-request checks discovered through `doc/project/README.md`) with arguments, inspect its `--help` or script header first instead of guessing positional arguments versus named flags (e.g., `--base`).
- For parallel builds, prefer `-j$(nproc)` so the job count adapts to the active host.
