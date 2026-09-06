# Reuse builds across history verification

Read this before building cleanup commits, rebase attempts, controls, or final-series sweeps.
The active project's build-freshness requirement means artifacts must match the checked-out inputs.
A successful incremental build satisfies it; a clean rebuild at each
stage is unnecessary.

## Keep the build workspace warm

- Prefer an existing, task-owned compatible build workspace. Otherwise create one verification
  worktree for the workflow and retain it through attempts, repairs, controls, and finalization.
  A new worktree may need one initial full build; do not recreate it for every SHA.
- Preserve immutable attempt and safe-point branches plus their logs independently of the build
  workspace. Switch the reusable worktree to the next attempt or detach at the required SHA;
  this does not move the preserved refs. Save work and evidence before switching.
- Walk final commits oldest to newest in the same worktree. If separate groups or controls need
  their own workspaces, retain a small reusable set. Concurrent builds/tests need separate mutable
  artifacts; never switch a worktree while its build or simulation is running.
- Retain object files, dependency files, generated code, generated makefiles, and libraries between
  stages. Do not use `make clean`, `cleanall`, `make -B`, delete `out/`, or run `git clean -xfd` as
  routine stage preparation. Do not rewrite or touch unchanged source files to populate a stage.
- Reuse an available compiler cache such as ccache through the configured toolchain, particularly
  when a separate worktree is necessary. Do not clear it between stages or weaken its correctness
  checks. Sharing a compiler cache is preferable to copying or symlinking mutable build outputs
  between worktrees with different source paths or inputs.

## Build the changed state

1. Record the workspace's last successful build SHA/tree and build configuration: mode, compiler,
   OMNeT++ installation, flags, enabled features, and dependent project libraries. Compare the next
   state with the state actually built there, not merely the next commit's parent. Include local
   build settings and uncommitted inputs when verifying a candidate before committing it.
2. Inspect the active `.opp` recipe and build wrapper once for clean/rebuild operations, forced
   compilation, temporary checkouts, and output-directory deletion. Use their supported incremental
   path. Discover the installed API before choosing options; do not guess `opp_repl` keywords.
3. Run the normal dependency-aware build in that workspace, in the mode the tests will load:

   ```bash
   make MODE=debug -j$(nproc)
   ```

   Use release when the contract requires it, with its separate outputs. Let make rebuild affected
   dependents and relink; a header change can legitimately rebuild many files. A no-op successful
   build is valid. For configuration, script, baseline, or documentation-only transitions with
   unchanged compiled inputs, retain the matching library and record why compilation is unnecessary.
4. Run the required scoped tests against that workspace's matching library and custom libraries.
   If `opp_repl` already performs the incremental build, use that build result without a redundant
   manual build. If it always cleans, use a supported build/test separation after an explicit
   successful incremental build; never skip freshness verification just to save time. Refresh
   long-lived project/recipe state after a checkout when paths, features, or Python code changed.
5. Keep the exact build command/status, workspace, tested SHA/tree, configuration, and build log
   with the existing verification record. Briefly record reuse or the reason for invalidation.
   Reusing compilation does not waive per-commit/stage tests or permit results from another tree.

## Invalidate only what changed

Ordinary C++ and header edits use the existing dependency graph. For MSG or other generated inputs,
regenerate affected outputs and rebuild their consumers. When sources are added, removed, renamed,
or feature selection/build rules change, refresh the source list and generated makefiles through
the checked-out build's normal mechanism. Remove orphaned generated outputs from deleted/renamed
inputs and ensure affected libraries are relinked when their object list shrinks; retained files
must not silently bring removed code into a historical revision.

Do not restore old source timestamps or touch outputs to make stale artifacts look current. When
switching backward or revisiting a SHA, reconcile it with the last built state just as for a forward
transition. If timestamps or missing dependencies make freshness uncertain, invalidate the affected
generated files, objects, or library and rebuild them.

Compiler/ABI, OMNeT++, compile flags, or feature changes that the build system does not track require
invalidation of incompatible outputs or another retained workspace for that configuration. Use a
full clean rebuild only when incompatibility is global, stale artifacts cannot be isolated, or a
specific verification requirement calls for one. Record that reason; a new commit, failed test,
new attempt branch, or middle-commit spot check alone is not a reason to discard the whole build.
