# Reliable command execution

Apply these rules across builds, tests, Git operations, searches, and repository scripts to avoid repeated command failures.

## Stateless shells and OMNeT++ environment

Each command invocation runs in a fresh shell session; exported variables and `source` calls do not persist across separate commands.

- When OMNeT++ or `opp_repl` tools (`opp_featuretool`, `opp_makemake`, `opp_msgtool`, `opp_run`, `opp_run_dbg`, `opp_test`, `opp_scavetool`, `opp_repl`, `opp_run_*_tests`, `opp_update_*_test_results`) are not already on `PATH` inside the command environment, load the checkout's `.envrc` or run `source "$OMNETPP_ROOT/setenv" && source setenv` in the **same** command from the INET root.
- If `OMNETPP_ROOT` is unset, read `.envrc` or the checkout's installation/build documentation instead of probing guessed paths.
- Check tool availability once with `command -v <tool>`.
- A linked worktree may lack a local, untracked `.envrc`. Read the known working checkout's setup to locate the OMNeT++ installation, then source that installation's `setenv` and the target worktree's `setenv`. Check that `INET_ROOT` points to the target before building or running tests.

## Python tools and checkout gates

An activated OMNeT++ virtual environment may supply `opp_repl` while lacking PyYAML or other dependencies of the repository scripts. Check the actual interpreter with `command -v python3` and probe the required imports. For example, `python3 -c 'import yaml, jsonschema'` checks the skill-suite tools' dependencies. Use a verified interpreter explicitly for a Python script. For a shell wrapper that invokes `python3` through `PATH`, scope the interpreter choice to that command. For example, after verifying `/usr/bin/python3 -c 'import yaml'`, prefix the discovered PR gate command with `PATH="/usr/bin:$PATH"`. Keep the OMNeT++ environment for simulation and test commands.

When an installed Python API rejects an import, keyword or result field, inspect the active installation with `python3 -c 'import opp_repl; print(opp_repl.__file__)'` and `inspect.signature` or the local source. If command help crashes, find the installed parser or a working invocation in the checkout's tests or workflows. Recheck after a runner revision change.

## Workspace-isolated sandboxes and external paths

In workspace-isolated sandboxes, external toolchains and repository metadata outside the workspace root are hidden unless explicitly mounted:

- **OMNeT++ and `opp_repl` toolchains**: `OMNETPP_ROOT` and its Python `.venv` typically reside outside the INET workspace. Check once whether `opp_featuretool` or the required `opp_run_*_tests` executable is accessible inside the sandbox. If that single check fails with `command not found` or `No such file or directory` because `OMNETPP_ROOT` is outside the sandbox, do **not** keep trying `make` (which calls `opp_featuretool` and `opp_makemake`), `opp_*`, or `inet` inside the sandbox first — run those toolchain commands directly with sandbox bypass (`BypassSandbox: true` where supported). Keep file searches and workspace-local commands sandboxed.
- **Git worktrees and mutating Git commands**: When `.git` is a regular file (`gitdir: ...`) pointing to a main repository `.git/worktrees/...` directory outside the worktree workspace, `git` commands fail inside a workspace-isolated sandbox with `fatal: not a git repository: ...`, and scripts that invoke `git` (such as commit or series checks) also fail. Similarly, when `.git/` is mounted read-only in a sandbox, mutating `git` commands (`git add`, `git commit`, `git checkout`, `git rebase`) fail with `Read-only file system`. Check once with `test -f .git` or one `git status`. Once confirmed, run subsequent `git` commands (or mutating `git` operations) and git-dependent repository scripts directly outside the sandbox (`BypassSandbox: true` where supported).
- **External sibling repositories**: When `statistics`, `media`, or `standards` paths resolve outside the workspace and fail inside the sandbox, run commands that read or update those paths outside the sandbox rather than retrying in the sandbox.

## Worktrees and filesystems

`git worktree move` can fail with `Invalid cross-device link` across mounts. If a runner expects a pinned `statistics` or `media` checkout at a relative path and that path is free, a symlink to the existing pinned worktree can provide it. Check the resolved path and SHA with `git -C <path> rev-parse --show-toplevel HEAD`. Keep writable comparison outputs isolated, including chart exports next to the baseline images.

## Repository script flags

- Before running a checkout's helper or enforcement script with arguments, read the usage in its script header or project guide. Use `--help` if implemented. For example, the source-seal checker accepts `--base "$base" --head "$head"` for the committed range or `--diff` for local changes. Run them separately when both checks apply.
- When reading across worktrees or revisions, find the current path with `rg --files` or `git ls-tree -r --name-only "$ref"` before opening it. A remembered path may have moved or may be local to a different worktree.
- For parallel builds, prefer `-j$(nproc)` so the job count adapts to the active host.
