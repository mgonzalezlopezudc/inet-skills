## INET and OMNeT++ workflows

Use repository skills for detailed procedures. Keep project-wide policy here and task-specific commands in the skill that owns them.

### Delegation

Use `inet-agent-orchestration` for nontrivial work with independent evidence lanes, production C++/NED/MSG changes, unexplained runtime behavior, standards-to-implementation analysis, statistical analysis, or independent regression/review. Keep simple lookups and obvious one-file edits in the root thread.

### Repository rules

- Before changing anything under `src/inet/`, use `inet-architectural-requirements` to check sealing, architecture, naming, exception-ledger, audit, and review requirements.
- Use Cmdenv for automated and reproducible runs. Use Qtenv only for interactive inspection or when requested.
- Use command-line overrides for temporary logging, tracing, capture, and result recording; do not edit `omnetpp.ini` only to enable diagnostics.
- Start investigations with one configuration and one run/seed. Expand only when the task requires a campaign or the narrow case is understood.
- Base claims about delivery, loss, retransmission, scheduling, or protocol behavior on logs, captures, event logs, results, source inspection, or debugger evidence.
- Keep build mode, runner, and model libraries consistent. Use `-j$(nproc)` for parallel builds unless the user requests otherwise.
- Never update fingerprint CSV files without explicit user approval after explaining the changed trajectory.
- Report reproducible commands with their working directory, configuration, run/seed, build mode, exit status, and artifact paths when applicable.

### IEEE 802.11 standards

Use `ieee80211-standards` and its generated corpus before processing PDFs under `standards/`. IEEE text governs normative claims; checked-out source and observed runs govern implemented behavior.

### Persisting reusable lessons

Unless the user directly requested the documentation change, ask before editing `AGENTS.md` or a skill to record a lesson. Propose the target, intended text, and why it is reusable. Store project-wide policy here, workflows in the owning `SKILL.md`, and detailed material in that skill's `references/`; do not persist one-off facts, guesses, logs, or guidance already documented nearby.
