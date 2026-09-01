---
name: ieee80211-standards
description: Search and inspect IEEE 802.11 standards stored in this repository. Use for questions about clauses, tables, figures, fields, procedures, or normative behavior in 802.11 standards, especially 802.11ax and 802.11be.
---

# IEEE 802.11 standards corpus

Use `doc/project/domain/ieee80211.md` and `doc/project/rule/quality.md` for INET's normative
traceability requirements. This skill adds corpus search, PDF fallback, and citation evidence.

Check status by running from the repository root: `inet_process_standards status`. If it reports a missing or stale corpus, run `inet_process_standards build --standards-dir $HOME$/omnetpp_ws/inet-standards --output $HOME/omnetpp_ws/inet-standards/processed`, recheck status, and repeat the search. 

For search and show, run from the repository root using the options `--standards-dir $HOME$/omnetpp_ws/inet-standards --output $HOME/omnetpp_ws/inet-standards/processed --json`

```sh
inet_process_standards search "<clause, table, field, or distinctive phrase>"
inet_process_standards show <document:chunk:id>
```

Search definitions and cross-references when one chunk is insufficient, and confirm the result belongs to the requested standard revision.

The generated corpus is under `$HOME/omnetpp_ws/inet-standards/processed/`. It is ignored build output: do not edit or commit it.

Consult a source PDF under `$HOME/omnetpp_ws/inet-standards/` only when the corpus cannot answer the question, visual structure or page verification matters, extraction appears wrong, or the user requests the original. Record the document revision, clause or annex, and page.

Report the revision, clause/table/figure, normative/informative status, corpus chunk identifiers,
material cross-references or ambiguity, and whether PDF inspection was needed.
