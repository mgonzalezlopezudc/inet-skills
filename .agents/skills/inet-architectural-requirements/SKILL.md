---
name: inet-architectural-requirements
description: Apply INET architectural requirements, naming conventions, exception ledgers, enforcement checks, and source-file sealing policy. Use to design, implement, refactor, audit, or review C++, NED, MSG, configuration, build, or package changes under src/inet; evaluate INET dependency direction, contracts, composition, protocol interaction, packet representation, observability, extensibility, determinism, testing, or naming; or check, propose, grant, or remove a seal.
---

# INET architectural requirements

## Sealing guard

Before adding, editing, moving, renaming, or deleting anything under `src/inet/`:

1. Read [sealing.md](references/sealing.md) and [sealing-status.md](references/sealing-status.md).
2. Resolve every target against exact-file and recursive ancestor-directory entries; status paths are relative to `src/inet/`.
3. Treat new files under sealed directories as sealed and generated `_m.h`/`_m.cc` files as covered by their source `.msg` seal.
4. For each sealed target, stop before writing and request explicit file-specific permission in the current conversation.
5. After approval, keep the seal and re-audit the change. Change sealing status only when the user explicitly requests it.

Assume unlisted files are unsealed only after checking the current status file.

## Load applicable references

- [requirements.md](references/requirements.md): user-facing modeling scope, execution, results, visualization, emulation, documentation, and compatibility.
- [architectural-requirements.md](references/architectural-requirements.md): production design/review and `AR-*` rules.
- [ieee80211-architectural-requirements.md](references/ieee80211-architectural-requirements.md): production changes in the IEEE 802.11 subtrees and `AR-WLAN-*` rules.
- [naming-conventions.md](references/naming-conventions.md): every new or renamed artifact.
- [architecture-exceptions.md](references/architecture-exceptions.md) and [naming-exceptions.md](references/naming-exceptions.md): existing exception/violation ledgers.
- [agent-review-checklist.md](references/enforcement/agent-review-checklist.md): every semantic diff review.
- [ieee80211-agent-review-checklist.md](references/enforcement/ieee80211-agent-review-checklist.md): semantic reviews of 802.11 production diffs.

Use prior reports only for the unchanged scope they cover; revalidate anything that may have changed.

## Apply and validate

1. Establish affected paths and whether the task is design, implementation, focused review, audit, naming, or sealing.
2. Pass the sealing guard, then map applicable `R-*`, `AR-*`, and, for 802.11 production scope, `AR-WLAN-*` identifiers.
3. Inspect the C++, NED, MSG, configuration, registration, build, and test artifacts that establish behavior.
4. Reconcile findings with both ledgers; do not reclassify recorded reality as a new violation.
5. Keep unrelated violations outside the patch and validate the changed contracts.

For architecture-sensitive changes, run from the repository root:

```sh
bash .agents/skills/inet-architectural-requirements/references/enforcement/check-architecture.sh
bash .agents/skills/inet-architectural-requirements/references/enforcement/check-architecture.sh src/inet/<focused-subtree>
```

Use the focused form for a bounded subtree and the repository-wide form for full or cross-cutting audits. The script reports known non-allowlisted violations; reconcile them with the architecture ledger.

For semantic review, emit every general checklist item and its prescribed `REVIEW: n PASS, n FLAG, n QUESTION` footer. For an 802.11 production diff, follow it with every WLAN checklist item and the prescribed `WLAN REVIEW: n PASS, n FLAG, n QUESTION` footer. Keep ordinary correctness findings before these checklist sections.

## Ledgers and sealing

Use stable `AS-*`/`AV-*` identifiers for architecture exceptions/violations and `NS-*`/`NV-*` for naming. Never silently edit, delete, or reuse ledger entries; propose changes and obtain explicit approval.

Seal only after auditing the entire requested scope, resolving every finding, recording approved exceptions, and receiving explicit approval. Never seal with an open `AV-*` or `NV-*` finding.

Report scope and seal status, applicable identifiers, `file:line` findings and ledger dispositions, validation evidence, required approvals, and the compliance verdict.
