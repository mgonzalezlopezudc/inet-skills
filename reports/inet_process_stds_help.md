The `inet_process_standards` tool turns standards PDFs into an addressable, auditable corpus. It organizes information around standards objects—clauses, tables, figures, and definitions.

```text
Reviewed PDFs
    ↓ extract text, pages, metadata, hashes
Documents
    ↓ detect and classify headings
Canonical nodes + occurrences + diagnostics
    ↓ recognize definitions and references
Reference graph
    ↓ build navigation/search index
get · search · refs · referenced-by · define · lint
```

## 1. Documents remain separate

Each PDF becomes a document with a stable identity, regardless of its filename:

- `ieee80211-2024` — the base standard
- `ieee80211be-2024` — an amendment of `ieee80211-2024`

The document record contains its title, revision, type, source hash, page count, and amendment relationship.

This prevents an important ambiguity: Clause 10.1 in the base standard and Clause 10.1 in an amendment are different objects.

The manifest also records the extraction tool, its arguments, and its version. `status` uses this information to detect a changed PDF, stale extractor, incompatible corpus, or partial build.

## 2. Canonical nodes represent standards objects

The processor recognizes four node types:

- Clause
- Table
- Figure
- Definition

Every node receives a canonical ID constructed from its document, type, and published label:

```text
ieee80211-2024:clause:10.25.2
ieee80211-2024:table:9-467
ieee80211-2024:figure:10-17
ieee80211-2024:definition:frame
```

For example, Table 9-467 is represented approximately as:

```yaml
node_id: ieee80211-2024:table:9-467
kind: table
label: 9-467
title: ADDBA Response frame Action field format
parent: ieee80211-2024:clause:9.6.4.3
pdf_pages: 1651-1652
source: ieee80211-2024@7025638:7028821
```

The parent and child links create a navigable hierarchy. Tables and figures are attached to their surrounding clause; subclauses are attached according to their numbering.

If a parent cannot be proven, the tool records a warning instead of inventing the relationship.

## 3. An occurrence is not necessarily a node

PDF extraction produces many things that look like headings:

- The real heading in the body
- A table-of-contents entry
- A repeated caption on the next page
- A number at the beginning of a table row
- A measurement such as “2.4 GHz”
- Two genuinely plausible copies

Therefore, every detected candidate is retained and classified as one of:

```text
canonical     the real body object
index-entry   a TOC or index mention
continuation  another part of the same object
rejected      a recognized false positive
ambiguous     the processor could not safely choose
```

For example, Table 6-1 appears once in the table index, once as the canonical caption, and repeatedly on pages 457–462. All those occurrences point to the single node:

```text
ieee80211-2024:table:6-1
```

Conversely, the text beginning with “2.4 GHz” was retained as a candidate but classified as rejected because the number is followed by a measurement unit.

This distinction is central: the corpus preserves what the extractor saw without turning every apparent heading into a false standards object.

## 4. Every result points back to exact source evidence

A node contains one or more source spans. A span records:

- Physical PDF page range
- Start and end offsets in canonical extracted text
- SHA-256 of the selected text
- Optional printed-page information

A locator such as:

```text
ieee80211-2024@7025638:7028821
```

means “characters 7,025,638 through 7,028,821 in the canonical text for this document.”

When retrieving a node, the tool reads that exact portion of `text.txt` and verifies its hash. This makes stale or corrupted evidence detectable.

## 5. Definitions and cross-references add semantic structure

Definitions found in the Clause 3 definition sections become ordinary canonical nodes. For example:

```text
ieee80211-2024:definition:frame
```

References are extracted only after all canonical nodes exist. Each reference stores:

- The source node
- The exact reference text and hashed source span
- Expected target type and label
- Resolution status
- Resolved target, or candidates and an explanation

Possible statuses are `resolved`, `unresolved`, and `ambiguous`.

For example, Clause 10.25.2 contains 16 detected outgoing references:

- 15 resolve to canonical clause nodes.
- `31.2.3` remains explicitly unresolved because no canonical target exists.

The processor does not choose a merely plausible target. `referenced-by` then derives incoming relationships exclusively from successfully resolved references.

## 6. Storage and search

The generated corpus has this shape:

```text
processed/
├── corpus.json
├── documents/
│   └── <document>/
│       ├── text.txt
│       └── pages/page-000001.txt ...
├── structure/
│   └── <document>/
│       ├── nodes.jsonl
│       ├── occurrences.jsonl
│       ├── diagnostics.jsonl
│       └── references.jsonl
└── index.sqlite
```

The JSONL files are the explicit structural records. SQLite provides fast lookup, hierarchy navigation, reverse-reference queries, diagnostics, and full-text search. Exact labels and titles rank ahead of ordinary full-text relevance.

The current corpus contains:

| Document | Nodes | Definitions included | References | Resolved |
|---|---:|---:|---:|---:|
| Base 802.11-2024 | 11,187 | 743 | 19,013 | 18,793 |
| 802.11be-2024 | 1,745 | 66 | 3,758 | 3,571 |

## Illustrative commands

```bash
# Confirm that PDFs and generated data are current
bin/inet_process_standards status \
  --standards-dir ../inet-pr-doc-project/standards \
  --output ../inet-pr-doc-project/standards/processed

# Retrieve one exact clause
bin/inet_process_standards get clause 10.25.2 \
  --document ieee80211-2024 \
  --output ../inet-pr-doc-project/standards/processed

# Retrieve by canonical ID
bin/inet_process_standards get ieee80211-2024:table:9-467 \
  --output ../inet-pr-doc-project/standards/processed

# Retrieve the exact text behind a stored source locator
bin/inet_process_standards get ieee80211-2024@7025638:7028821 \
  --output ../inet-pr-doc-project/standards/processed

# Search when the exact label is not known
bin/inet_process_standards search "ADDBA Response" \
  --document ieee80211-2024 \
  --output ../inet-pr-doc-project/standards/processed

# Follow semantic relationships
bin/inet_process_standards refs clause 10.25.2 \
  --document ieee80211-2024 \
  --output ../inet-pr-doc-project/standards/processed

# Retrieve an exact definition
bin/inet_process_standards define frame \
  --document ieee80211-2024 \
  --output ../inet-pr-doc-project/standards/processed

# Show ambiguities, rejected candidates, missing parents, and unresolved references
bin/inet_process_standards lint \
  --document ieee80211-2024 \
  --output ../inet-pr-doc-project/standards/processed
```

The Phase 5 `inet_spec` tool is a separate layer. `inet_process_standards` records what can be objectively extracted from the source; `inet_spec` records a reviewed, explicitly non-authoritative interpretation of selected behavior and points back to these canonical nodes and source hashes.

Canonical node IDs and source-span locators are the public retrieval identities. The central implementation is in [processor.py](/home/user/omnetpp_ws/inet-skills/python/inet/standards/processor.py:317), with identities in [model.py](/home/user/omnetpp_ws/inet-skills/python/inet/standards/model.py:91), classification in [structure.py](/home/user/omnetpp_ws/inet-skills/python/inet/standards/structure.py:414), and reference resolution in [semantics.py](/home/user/omnetpp_ws/inet-skills/python/inet/standards/semantics.py:412).
