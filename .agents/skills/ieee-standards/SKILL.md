---
name: ieee-standards
description: Inspect local IEEE 802.11 and IEEE 802.15.4 standards. Use for exact clauses, tables, figures, definitions, cross-references, and normative citations.
---

# IEEE standards corpus

Use [project-guidance-discovery.md](../../references/project-guidance-discovery.md) to read the active checkout's project entry point.
Find its current guidance for evidence that supports standards requirements.
This skill supplies corpus search, PDF fallback, and citation evidence.

Use the tracked launcher `./bin/inet_process_standards` from the `inet-skills` repository root.
Do not rely on a similarly named command from `PATH`.
Locate the INET worktree from the current workspace or repository context.
Do not assume a home-directory layout.

Resolve `<standards-root>` to the directory that contains the requested PDFs.
This can be the checkout's `standards/` or a shared corpus repository identified by the workspace.
Set `<corpus-output>` to a writable, ignored output directory, normally `<inet-worktree>/standards/processed`.
The source directory may be read-only.

Read the relevant family in [documents.md](references/documents.md) before the first query:

```sh
git -C <inet-worktree> rev-parse --show-toplevel
./bin/inet_process_standards status \
  --standards-dir <standards-root> --output <corpus-output>
```

If status reports a missing, stale, partial, or incompatible corpus, rebuild it.
Run the corpus linter before retrieval:

```sh
./bin/inet_process_standards build \
  --standards-dir <standards-root> --output <corpus-output>
./bin/inet_process_standards lint \
  --standards-dir <standards-root> --output <corpus-output> --json
```

Use exact structural navigation when the clause, table, or figure label is known. Base standards
and amendments are separate documents; include `--document` whenever a label may occur in both:

```sh
./bin/inet_process_standards get clause 10.25.2 --document ieee80211-2024 \
  --standards-dir <standards-root> --output <corpus-output> --json
./bin/inet_process_standards get table 9-45 --document ieee80211-2024 \
  --standards-dir <standards-root> --output <corpus-output> --json
./bin/inet_process_standards get figure 10-17 --document ieee80211-2024 \
  --standards-dir <standards-root> --output <corpus-output> --json
```

Use `define` for an exact, case-insensitive term lookup. A term changed by an amendment is
intentionally ambiguous without `--document`:

```sh
./bin/inet_process_standards define "access point" --document ieee80211-2024 \
  --standards-dir <standards-root> --output <corpus-output> --json
```

Use `refs` to inspect every extracted outgoing reference, including unresolved and ambiguous
records. Use `referenced-by` for derived incoming edges; it contains only references that resolved
to the requested canonical node:

```sh
./bin/inet_process_standards refs clause 10.25.2 --document ieee80211-2024 \
  --standards-dir <standards-root> --output <corpus-output> --json
./bin/inet_process_standards referenced-by clause 10.25.3 --document ieee80211-2024 \
  --standards-dir <standards-root> --output <corpus-output> --json
```

When the label is unknown, search first.
Retrieve the returned canonical node ID next.
Use
`--children`, `--ancestors`, or `--context <characters>` only when that extra evidence is needed:

```sh
./bin/inet_process_standards search "<clause, table, field, or distinctive phrase>" \
  --standards-dir <standards-root> --output <corpus-output> --json
./bin/inet_process_standards get <canonical-node-id> \
  --standards-dir <standards-root> --output <corpus-output> --json
```

Search related terms when one node is insufficient.
Confirm that every result belongs to the requested document and revision.
Inspect ambiguity and lint findings.
Do not silently choose a plausible occurrence.
An unresolved cross-reference is a coverage gap.
An ambiguous cross-reference does not identify a target.

The generated corpus is `<corpus-output>/`. It is ignored build output: do not edit or
commit it.

Consult a source PDF under `<standards-root>/` only under one of these conditions:

- The corpus cannot answer the question.
- Visual structure or page verification matters.
- Extraction appears wrong.
- The user requests the original.

Record the document revision, clause or annex, and page.

Report these evidence fields:

- Document ID and revision.
- Clause, table, figure, or definition.
- Normative or informative status.
- Canonical node ID.
- Physical PDF pages or source-span locator.
- Relevant cross-references and their resolution status.
- Whether PDF inspection was necessary.
