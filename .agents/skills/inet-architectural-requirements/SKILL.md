---
name: inet-architectural-requirements
description: Apply INET architectural requirements, naming conventions, exception ledgers, enforcement checks, and source-file sealing policy. Use to design, implement, refactor, audit, or review C++, NED, MSG, configuration, build, or package changes under src/inet; evaluate INET dependency direction, contracts, composition, protocol interaction, packet representation, observability, extensibility, determinism, testing, or naming; or check, propose, grant, or remove a seal.
---

# INET architectural requirements

## Sealing guard

Before adding, editing, moving, renaming, or deleting anything under `src/inet/`:

1. Run `check-sealing.sh` from the repository root to automatically check affected paths against [sealing-status.md](references/sealing-status.md):
   ```sh
   bash .agents/skills/inet-architectural-requirements/references/enforcement/check-sealing.sh <affected-files...>
   # Or to check current git changes:
   bash .agents/skills/inet-architectural-requirements/references/enforcement/check-sealing.sh --diff
   ```
2. **If no sealed path overlaps**, proceed — the guard is satisfied. Skip loading `sealing.md`.
3. **If a sealed path overlaps**, read [sealing.md](references/sealing.md) for the full policy, then:
   - Resolve every target against exact-file and recursive ancestor-directory entries; status paths are relative to `src/inet/`.
   - Treat new files under sealed directories as sealed and generated `_m.h`/`_m.cc` files as covered by their source `.msg` seal.
   - For each sealed target, stop before writing and request explicit file-specific permission in the current conversation.
   - After approval, keep the seal and re-audit the change. Change sealing status only when the user explicitly requests it.

Assume unlisted files are unsealed only after checking the current status file.

## Load applicable references (Tiered Loading)

To optimize context budget, use tiered loading rather than loading all references at once:

- **Tier 1 (Always for any src/inet/ change):** [quick-reference-index.md](references/quick-reference-index.md) to identify which `AR-*` and `AR-WLAN-*` requirements apply.
- **Tier 2 (Focused by change type):** Load only the specific sections from:
  - [requirements.md](references/requirements.md): user-facing modeling scope, execution, results, visualization, emulation, documentation, and compatibility.
  - [architectural-requirements.md](references/architectural-requirements.md): production design/review and `AR-*` rules.
  - [ieee80211-architectural-requirements.md](references/ieee80211-architectural-requirements.md): production changes in the IEEE 802.11 subtrees and `AR-WLAN-*` rules.
  - [naming-conventions.md](references/naming-conventions.md): only when introducing new files, classes, signals, or parameters.
  - [architecture-exceptions.md](references/architecture-exceptions.md) and [naming-exceptions.md](references/naming-exceptions.md): only when checking for pre-existing violations.
- **Tier 3 (Semantic review / audit):**
  - [agent-review-checklist.md](references/enforcement/agent-review-checklist.md): every semantic diff review.
  - [ieee80211-agent-review-checklist.md](references/enforcement/ieee80211-agent-review-checklist.md): semantic reviews of 802.11 production diffs.

For recurring false-positive and missed-finding patterns, see [common-agent-pitfalls.md](../inet-code-review/references/common-agent-pitfalls.md) in the code-review skill.

Use prior reports (in [reports/](references/reports/)) only for the unchanged scope they cover; revalidate anything that may have changed.

## Apply and validate

1. Establish affected paths and whether the task is design, implementation, focused review, audit, naming, or sealing.
2. Pass the sealing guard (`check-sealing.sh`), then map applicable `R-*`, `AR-*`, and, for 802.11 production scope, `AR-WLAN-*` identifiers.
3. Inspect the C++, NED, MSG, configuration, registration, build, and test artifacts that establish behavior.
4. Reconcile findings with both ledgers; do not reclassify recorded reality as a new violation.
5. Keep unrelated violations outside the patch and validate the changed contracts.

For architecture-sensitive changes, run from the repository root:

```sh
bash .agents/skills/inet-architectural-requirements/references/enforcement/check-architecture.sh
bash .agents/skills/inet-architectural-requirements/references/enforcement/check-architecture.sh src/inet/<focused-subtree>
```

Use the focused form for a bounded subtree and the repository-wide form for full or cross-cutting audits.

### Reconciling `check-architecture.sh` output

The script reports non-allowlisted `#include` violations. For each reported violation:

1. Check [architecture-exceptions.md](references/architecture-exceptions.md) — if the coupling is already recorded as `AS-*` (sanctioned) or `AV-*` (known violation), reference the existing entry.
2. If the coupling is **new and introduced by the reviewed change**: report it as a finding and propose either a fix direction or a new `AV-*` violation row.
3. If the coupling is **new but pre-existing** (not introduced by the change): note it as a pre-existing violation outside the reviewed scope; do not block the review on it.
4. If the coupling is a **deliberate, permanent framework-wide dependency**: propose a new `AS-*` sanctioned-exception row and an allowlist addition in the script.

Never silently add allowlist entries or ledger rows — propose them and await user approval.

For semantic review, emit every general checklist item using `PASS`, `N/A — <reason>`, `FLAG — <file:line> — <reason>`, or `QUESTION — <file:line> — <what to check>`, followed by its prescribed `REVIEW: n PASS, n FLAG, n QUESTION, n N/A` footer. For an 802.11 production diff, follow it with every WLAN checklist item and the prescribed `WLAN REVIEW: n PASS, n FLAG, n QUESTION, n N/A` footer.

This skill owns architectural, naming, and sealing metadata, required-artifact policy, and checklist verdicts; it does not replace correctness review. When composed with `inet-code-review`, keep its correctness findings before the checklist sections. If a checklist `FLAG` describes the same mechanism as a correctness finding, reference that finding instead of duplicating it; the finding's correction direction and focused verification satisfy any checklist requirement to provide a correction, while the checklist still supplies the requirement identifier and ledger disposition.

## Ledgers and sealing

Use stable `AS-*`/`AV-*` identifiers for architecture exceptions/violations and `NS-*`/`NV-*` for naming. Never silently edit, delete, or reuse ledger entries; propose changes and obtain explicit approval.

Seal only after auditing the entire requested scope, resolving every finding, recording approved exceptions, and receiving explicit approval. Never seal with an open `AV-*` or `NV-*` finding.

Report scope and seal status, applicable identifiers, `file:line` findings and ledger dispositions, validation evidence, required approvals, and the compliance verdict.
