---
name: ieee80211-standards
description: Search and inspect IEEE 802.11 standards stored in this repository. Use for questions about clauses, tables, figures, fields, procedures, or normative behavior in 802.11 standards, especially 802.11ax and 802.11be.
---

# IEEE 802.11 standards corpus

Use `doc/project/domain/ieee80211.md` and `doc/project/rule/quality.md` for INET's normative
traceability requirements. This skill adds corpus search, PDF fallback, and citation evidence.

Use the tracked launcher `./bin/inet_process_standards` from the `inet-skills` repository root; do
not rely on a similarly named command from `PATH`. Locate the standards checkout from the current
workspace or repository context rather than assuming a home-directory layout, and confirm its root:

```sh
git -C <standards-checkout> rev-parse --show-toplevel
./bin/inet_process_standards status \
  --standards-dir <standards-root> --output <standards-root>/processed
```

If status reports a missing or stale corpus, build it, recheck status, and repeat the search:

```sh
./bin/inet_process_standards build \
  --standards-dir <standards-root> --output <standards-root>/processed
./bin/inet_process_standards search "<clause, table, field, or distinctive phrase>" \
  --standards-dir <standards-root> --output <standards-root>/processed --json
./bin/inet_process_standards show <document:chunk:id> \
  --standards-dir <standards-root> --output <standards-root>/processed --json
```

Search definitions and cross-references when one chunk is insufficient, and confirm the result belongs to the requested standard revision.

The generated corpus is `<standards-root>/processed/`. It is ignored build output: do not edit or
commit it.

Consult a source PDF under `<standards-root>/` only when the corpus cannot answer the question,
visual structure or page verification matters, extraction appears wrong, or the user requests the
original. Record the document revision, clause or annex, and page.

Report the revision, clause/table/figure, normative/informative status, corpus chunk identifiers,
material cross-references or ambiguity, and whether PDF inspection was needed.
