## INET and OMNeT++ workflows

Use repository skills for task-specific mechanics. Contributor policy is canonical in the active
INET checkout under `doc/project/`; point to it here instead of copying it.

### Delegation

Use `inet-agent-orchestration` for nontrivial work with independent evidence lanes, production C++/NED/MSG changes, unexplained runtime behavior, standards-to-implementation analysis, statistical analysis, or independent regression/review. Keep simple lookups and obvious one-file edits in the root thread.

### Repository rules

- Before changing anything under `src/inet/`, use `inet-architectural-requirements` to check sealing, architecture, naming, exception-ledger, audit, and review requirements.
- Before making a semantic change under `src/inet/`, use `inet-code-authoring` to define the implementation contract, apply the relevant preventive correctness checks, and self-audit the stable diff before handoff.
- Apply the active INET checkout's `doc/project/rule/testing.md`,
  `doc/project/guide/change-a-baseline.md`, and
  `doc/project/guide/run-the-gates.md` for test selection, baseline changes, and contributor gates.
- Apply its `doc/project/guide/diagnose-a-simulation.md` for diagnostic scope, evidence, comparison,
  and reporting; use the evidence skills for tool-specific commands.
- Apply its `doc/project/guide/analyze-simulation-results.md` for result comparisons, derived metrics,
  uncertainty, and reporting; use the result skills for extraction and plotting mechanics.

### Agent execution constraints

- Use Cmdenv for automated and reproducible runs. Use Qtenv only for interactive inspection or when requested.
- Use command-line overrides for temporary logging, tracing, capture, and result recording; do not edit `omnetpp.ini` only to enable diagnostics.
- When an agent builds or executes INET/OMNeT++ during a task, use debug mode with matching runners
  and libraries (`MODE=debug`, `inet --debug`, `-m debug`, `opp_run_dbg`, and `libINET_dbg.so` as
  applicable). Use `-j$(nproc)` unless the user requests otherwise. This is an agent execution
  constraint, not the contributor gate: it does not satisfy the debug-and-release build required by
  `doc/project/guide/run-the-gates.md`.

### Persisting reusable lessons

Unless the user directly requested the documentation change, ask before editing `AGENTS.md`,
`doc/project/`, or a skill to record a lesson. Propose the target, intended text, and why it is
reusable. Store contributor policy in the active INET checkout's `doc/project/`, repository agent
routing here, workflows in the owning `SKILL.md`, and detailed mechanics in that skill's
`references/`; do not persist one-off facts, guesses, logs, or guidance already documented nearby.
