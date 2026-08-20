## INET and OMNeT++ workflows

Use repository skills for detailed procedures. Keep project-wide policy here and task-specific commands in the skill that owns them.

### Delegation

Use `inet-agent-orchestration` for nontrivial work with independent evidence lanes, production C++/NED/MSG changes, unexplained runtime behavior, standards-to-implementation analysis, statistical analysis, or independent regression/review. Keep simple lookups and obvious one-file edits in the root thread.

### Skill-path access
- Use the canonical path `/home/user/omnetpp_ws/inet-skills/.agents/...`.
- For the first skill read, invoke the read with the required path access/escalation immediately; do not probe the symlink first with `ls`, `wc`, or `realpath`.
- If the sandbox rejects the command before execution, retry the identical read using required path access.

### Codex path to project `config.toml` and agent definitions `.toml` files 
- Use the canonical path `/home/user/omnetpp_ws/inet-skills/.codex/...`.
- For the agent definition read, invoke the read with the required path access/escalation immediately; do not probe the symlink first with `ls`, `wc`, or `realpath`.
- If the sandbox rejects the command before execution, retry the identical read using required path access.

### Repository rules

- Before changing anything under `src/inet/`, use `inet-architectural-requirements` to check sealing, architecture, naming, exception-ledger, audit, and review requirements.
- Use Cmdenv for automated and reproducible runs. Use Qtenv only for interactive inspection or when requested.
- Use command-line overrides for temporary logging, tracing, capture, and result recording; do not edit `omnetpp.ini` only to enable diagnostics.
- Start investigations with one configuration and one run/seed. Expand only when the task requires a campaign or the narrow case is understood.
- Base claims about delivery, loss, retransmission, scheduling, or protocol behavior on logs, captures, event logs, results, source inspection, or debugger evidence.
- Use debug mode for every INET/OMNeT++ build, simulation, and test run, with matching debug runners and libraries (`MODE=debug`, `inet --debug`, `-m debug`, `opp_run_dbg`, and `libINET_dbg.so` as applicable). Never build or execute release-mode artifacts. Use `-j$(nproc)` for parallel builds unless the user requests otherwise.
- For code changes, run only unit, module, and fingerprint tests that are directly related to the changed paths, symbols, or behavioral contracts. Record that mapping and invoke an explicit filter; never run an unfiltered or broader suite. If no directly related test can be identified, report the coverage gap instead of broadening the test selection.
- Never update fingerprint CSV files without explicit user approval after explaining the changed trajectory.
- Report reproducible commands with their working directory, configuration, run/seed, build mode, exit status, and artifact paths when applicable.

### Persisting reusable lessons

Unless the user directly requested the documentation change, ask before editing `AGENTS.md` or a skill to record a lesson. Propose the target, intended text, and why it is reusable. Store project-wide policy here, workflows in the owning `SKILL.md`, and detailed material in that skill's `references/`; do not persist one-off facts, guesses, logs, or guidance already documented nearby.
