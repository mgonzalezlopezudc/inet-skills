# Platform Bindings for Specialist Agents

This reference documents how specialist agents are registered and invoked across supported agent runtimes (Codex, Antigravity, and Kimi).

## Agent Registration

Specific agent runner configurations and default reasoning efforts are registered in:
- Codex: `.codex/agents/<agent-name>.toml`
- Antigravity: `.antigravity/agents/<agent-name>.toml` (or skill-level `agents/antigravity.yaml`)
- OpenAI / Assistants API: `.agents/skills/<skill>/agents/openai.yaml`

For active specialist-class bindings, consult [MODELS.md](../../../../MODELS.md). Runner TOML files are authoritative when this overview and a binding disagree.

## Runtime-Specific Spawning Procedures

### Codex and Antigravity
Spawn registered agent types directly using the platform sub-agent tool or configuration name. The sub-agent inherits workspace configuration and repository rules automatically.

### Prompt-Persona Runtimes
When running on platforms without declarative agent registration, instantiate the persona by prepending:
1. The specialist agent's `description` from the class and routing tables.
2. The specialized `developer_instructions` or owning skill prompt.
3. Specific deliverable constraints (depth-one, single writer, required evidence).

### Kimi
- For read-only investigations, searches, and analysis: use `explore` mode.
- For builds, test runs, artifact creation, or edits: use `coder` mode.
- Report inherited model/effort when per-agent selection is unavailable.

## Fallback Rules
If the assigned binding is unavailable on the host platform, choose an equal- or higher-capability
model for the same specialist role. Never silently downgrade reasoning work; disclose the actual
model and verification used to the parent thread.
