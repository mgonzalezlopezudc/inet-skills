---
name: ieee80211-standards
description: Search and inspect IEEE 802.11 standards stored in this repository. Use for questions about clauses, tables, figures, fields, procedures, or normative behavior in 802.11 standards, especially 802.11ax and 802.11be.
---

# IEEE 802.11 standards corpus

Use the shared [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to
read the active checkout's project entry point and discover any current normative traceability
guidance. This skill adds corpus search, PDF fallback, and citation evidence.

Use the tracked launcher `./bin/inet_process_standards` from the `inet-skills` repository root; do
not rely on a similarly named command from `PATH`. Locate the INET worktree from the current
workspace or repository context rather than assuming a home-directory layout, confirm its root,
and set `<standards-root>` to its `standards/` directory:

```sh
git -C <inet-worktree> rev-parse --show-toplevel
./bin/inet_process_standards status \
  --standards-dir <standards-root> --output <standards-root>/processed
```

If status reports a missing, stale, partial, or incompatible corpus, rebuild it and run the
corpus linter before relying on retrieval:

```sh
./bin/inet_process_standards build \
  --standards-dir <standards-root> --output <standards-root>/processed
./bin/inet_process_standards lint \
  --standards-dir <standards-root> --output <standards-root>/processed --json
```

Use exact structural navigation when the clause, table, or figure label is known. Base standards
and amendments are separate documents; include `--document` whenever a label may occur in both:

```sh
./bin/inet_process_standards get clause 10.25.2 --document ieee80211-2024 \
  --standards-dir <standards-root> --output <standards-root>/processed --json
./bin/inet_process_standards get table 9-45 --document ieee80211-2024 \
  --standards-dir <standards-root> --output <standards-root>/processed --json
./bin/inet_process_standards get figure 10-17 --document ieee80211-2024 \
  --standards-dir <standards-root> --output <standards-root>/processed --json
```

Use `define` for an exact, case-insensitive term lookup. A term changed by an amendment is
intentionally ambiguous without `--document`:

```sh
./bin/inet_process_standards define "access point" --document ieee80211-2024 \
  --standards-dir <standards-root> --output <standards-root>/processed --json
```

Use `refs` to inspect every extracted outgoing reference, including unresolved and ambiguous
records. Use `referenced-by` for derived incoming edges; it contains only references that resolved
to the requested canonical node:

```sh
./bin/inet_process_standards refs clause 10.25.2 --document ieee80211-2024 \
  --standards-dir <standards-root> --output <standards-root>/processed --json
./bin/inet_process_standards referenced-by clause 10.25.3 --document ieee80211-2024 \
  --standards-dir <standards-root> --output <standards-root>/processed --json
```

When the label is unknown, search first, then retrieve the returned canonical node ID. Use
`--children`, `--ancestors`, or `--context <characters>` only when that extra evidence is needed:

```sh
./bin/inet_process_standards search "<clause, table, field, or distinctive phrase>" \
  --standards-dir <standards-root> --output <standards-root>/processed --json
./bin/inet_process_standards get <canonical-node-id> \
  --standards-dir <standards-root> --output <standards-root>/processed --json
```

Search related terms when one node is insufficient, and confirm every result belongs to the
requested document and revision. Treat ambiguity and lint findings as evidence to inspect, not as
permission to choose a plausible occurrence silently. Cross-references are extracted
conservatively: an unresolved edge is a coverage gap, while an ambiguous edge is not a target.

The generated corpus is `<standards-root>/processed/`. It is ignored build output: do not edit or
commit it.

Consult a source PDF under `<standards-root>/` only when the corpus cannot answer the question,
visual structure or page verification matters, extraction appears wrong, or the user requests the
original. Record the document revision, clause or annex, and page.

Report the document ID and revision, clause/table/figure/definition, normative/informative status,
canonical node ID, physical PDF pages or source-span locator, material cross-references and their
resolution status, and whether PDF inspection was needed.
