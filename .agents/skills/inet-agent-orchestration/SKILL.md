---
name: inet-agent-orchestration
description: Route and coordinate project-scoped specialist agents across Codex, Antigravity, and Kimi for nontrivial OMNeT++/INET and IEEE 802.11 work. Use for multi-stage debugging, standards-to-implementation analysis, C++/NED/MSG changes, Wi-Fi packet or PHY/MAC investigations, regression design, result analysis, patch review, or any task with multiple independent evidence lanes or specialist handoffs.
---

# INET agent orchestration

Keep requirements, decisions, and synthesis in the root thread. Delegate bounded evidence or execution outcomes when independent lanes reduce risk or latency.

## Constraints

- Keep depth at one; specialists must not delegate.
- Use at most one production-code writer.
- Do not duplicate assignments or delegate work simpler than the handoff.
- Do not let extraction-only agents infer causality, normative meaning, or correctness.
- Stop opening lanes once decisive evidence exists.

## Tiers and agents

| Tier | Appropriate work | Codex agent |
| --- | --- | --- |
| Chimp 🐒 | Ambiguous standards/MAC/PHY reasoning, difficult runtime causality, final review | `inet-wifi-specialist`, `inet-simulation-detective`, `inet-reviewer` |
| Dog 🐕 |  |  |
| Fish 🐟 | Cross-file architecture and NED/INI tracing, production implementation, established regression and result-analysis workflows | `inet-navigator`, `inet-implementer`, `inet-regression-guard`, `inet-results-analyst` |
| Ant 🐜 | Explicit searches, inventories, filtering, and structured extraction | `inet-evidence-miner` |

| Tier | Antigravity | Kimi Code CLI |
| --- | --- | --- |
| Chimp | `gemini-3.7-flash`, `high` | `kimi-code/k3`, `max` |
| Dog | `gemini-3.7-flash`, `medium` | `kimi-code/k3`, `high` |
| Fish | `gemini-3.7-flash`, `medium` | `kimi-code/kimi-for-coding`, `high` |
| Ant | `gemini-3.7-flash`, `low` | `kimi-code/kimi-for-coding`, thinking on |

If a binding is unavailable, move upward in capability. Never silently downgrade Chimp work; disclose the actual model and verification used.

Use workspace-local `.codex/agents/<agent-name>.toml` as the canonical role definition, including Codex model settings. On Codex, spawn that registered type. On prompt-persona runtimes, prepend its `description` and `developer_instructions`. On Kimi, use `explore` for read-only work and `coder` for runs, artifacts, or edits; report inherited model/effort when per-agent selection is unavailable.

## Routing

- **Architecture/configuration:** use `inet-navigator`; add `inet-reviewer` for a formal compliance verdict and `inet-wifi-specialist` only when 802.11 semantics matter.
- **Standards/model gap:** use `inet-wifi-specialist`; add `inet-navigator` when the implementation path is broad or unclear.
- **Runtime failure:** lead with `inet-simulation-detective`; add configuration, Wi-Fi, or extraction lanes only for distinct questions.
- **Production change:** establish the mechanism and change surface, then assign exactly one `inet-implementer`. Use `inet-regression-guard` for behavior changes and `inet-reviewer` for architecture-sensitive, nontrivial, or 802.11 changes.
- **Results/plots:** use `inet-results-analyst`; use `inet-evidence-miner` only for bounded metadata inventory.

For any `src/inet/` change, the architecture skill owns seal checks, requirement maps, ledgers, fitness checks, and semantic checklist contracts. For 802.11 production changes, it also owns `AR-WLAN-*` mapping and WLAN checklist requirements; normative changes additionally require an IEEE revision and clause.

## Assignments and gates

Every delegated prompt must say to follow `AGENTS.md` and the applicable repository skills, not spawn sub-agents, and return to the parent. Specify one deliverable, exact scope and inputs, write authority, exclusions, required evidence, definition of done, and concise return shape. Include paths, symbols, configuration, run/seed, and artifacts when relevant. Reuse a specialist for related follow-up work.

Gate handoffs as follows:

1. Diagnose → implement: demonstrated mechanism, bounded change surface, architecture/seal decision, and any required approval.
2. Implement → verify: stable diff and explicit behavior claim.
3. Verify → conclude: focused evidence that exercises the claim; for behavior-affecting production changes, complete repository unit and fingerprint suites using their owning skills.
4. Architecture review → conclude: required fitness checks and exact semantic checklist verdicts.
5. Fingerprint update or sealing change: explicit user approval after the evidence is presented.

Resolve disagreements by reproducible runtime/debugger evidence, packet/event/result evidence, effective configuration, checked-out source, then hypothesis. IEEE text governs normative behavior; source and observed runs govern implementation behavior.
