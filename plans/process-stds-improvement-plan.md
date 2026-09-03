## Verdict

Adopt the proposal’s central architecture, but change its execution order:

1. Make structural detection trustworthy.
2. Add stable per-document nodes and exact navigation.
3. Add cross-references and diagnostics.
4. Pilot a small, non-authoritative ADDBA specification.
5. Only then decide whether protocol IR becomes canonical INET documentation.

Do not begin with MCP, a large multi-file IR, or new implementation skills.

The public contract consists of reviewed document identities, canonical structural nodes, exact
source spans, diagnostics, definitions, cross-references, and the command surface documented below.
The ignored generated corpus is published atomically, and every in-repository caller uses that
contract.

## Architectural conclusions

- Structural recognition requires contextual classification because the same apparent label can
  occur in indexes, body headings, continued captions, table rows, and measurements. Examples
  include:
  - `Table 9-45` in both the table list and the body.
  - `Figure 10-17` in both the figure list and the body.
  - `2.16 GHz ...` as a numeric token that is not a clause heading.
- Hierarchy must be evidence-backed. Missing immediate parents are diagnostics rather than grounds
  to fabricate links.
- Filename stems are unsuitable as authoritative document identities. `80211ax-2024.pdf` is titled
  IEEE Std 802.11-2024, while `80211be-2024.pdf` is an amendment
  ([corpus.json](/home/user/omnetpp_ws/inet-pr-doc-project/standards/processed/corpus.json:1)).
- `doc/project/spec/` is not currently a free extension point. `doc/project/` has a defined documentation chain, closed document-kind vocabulary, and unique identifier ownership ([README.md](/home/user/omnetpp_ws/inet-pr-doc-project/doc/project/README.md:15), [documentation.md](/home/user/omnetpp_ws/inet-pr-doc-project/doc/project/rule/documentation.md:116)). A canonical protocol IR there requires an explicit project-documentation decision.
- A new `inet-80211-feature-implementation` skill would duplicate the existing authoring, architectural, and WLAN regression skills ([inet-code-authoring](/home/user/omnetpp_ws/inet-skills/.agents/skills/inet-code-authoring/SKILL.md:40), [inet-80211-regression-testing](/home/user/omnetpp_ws/inet-skills/.agents/skills/inet-80211-regression-testing/SKILL.md:8)).
- Normativity is generally statement-level, not safely represented by a boolean on an entire clause. Defer `--normative` filtering until normative statements themselves are modeled.

## Actionable plan

### Phase 1 — Establish the structural contract

Repository: `inet-skills`

Status: completed on 2026-09-03 in
[`model.py`](../python/inet/standards/model.py),
[`corpus.py`](../python/inet/standards/corpus.py), and their focused tests. The contract is active in
the processor, index, CLI, and generated corpus.

Define before implementation:

- `document_id`: reviewed canonical identity such as `ieee80211-2024`; filename stems are input
  metadata, not public identities.
- Document kind: base standard, amendment, corrigendum, or supporting document.
- Amendment relationship without attempting a merged effective-standard view.
- Separate:
  - heading candidates;
  - source occurrences;
  - accepted canonical nodes.
- Canonical node fields:
  - document, kind, label, title;
  - parent and children;
  - source spans and physical pages;
  - nullable printed-page number;
  - confidence, with classification retained on source occurrences;
  - source hash.
- Define a versioned corpus layout with one canonical textual extraction and page/source-span
  views. Structural records should reference those spans rather than duplicate the standard text.
- Separate corpus format version, extractor version, and source-document hashes so each freshness
  reason is explicit.

Acceptance:

- A build transaction publishes the complete generated corpus as one unit.
- Corpus metadata, required artifacts, extractor identity, and source hashes are validated before
  queries rely on the corpus.
- IDs never depend on extraction sequence or PDF page number.
- Ambiguity is reported rather than silently resolved.

### Phase 2 — Fix candidate recognition before issuing stable IDs

Status: completed on 2026-09-03 in
[`structure.py`](../python/inet/standards/structure.py) and
[`test_structure.py`](../python/inet/standards/test_structure.py). The analyzer remains dormant until
the atomic Phase 3 storage and CLI cutover.

Separate candidate detection from contextual classification.

Add fixtures for:

- table/figure lists versus body captions;
- `2.16 GHz` and similar decimal quantities;
- repeated and continued table captions;
- top-level clauses;
- annex headings;
- base/amendment duplicate clause labels;
- partial-page builds.

Add corpus diagnostics for duplicate labels, false candidates, missing parents, oversized/tiny
nodes, and unresolved ambiguity.

Also make corpus rebuilding transactional enough that a failed rebuild cannot leave an index paired
with artifacts from another build.

Acceptance:

- `Table 9-45` and `Figure 10-17` resolve to their body objects.
- Known decimal-unit examples are not clauses.
- Every structural candidate has one explicit classification: canonical, index entry, continuation,
  rejected with a reason, or ambiguous with a reason.
- Tests cover the structural contract and the failure modes above.

Completed evidence:

- Candidate detection preserves source offsets, page evidence, separator layout, and continuation
  evidence before classification.
- Contextual classification distinguishes index entries, body captions, explicit and repeated
  continuations, decimal quantities, table rows, line-wrapped references, top-level clauses, and
  annex headings.
- Canonical nodes receive hierarchy links and one or more contiguous source spans; a partial-page
  selection does not fabricate a span across unextracted physical pages.
- Diagnostics cover duplicate labels, rejected false candidates, missing parents, tiny and oversized
  nodes, and unresolved ambiguity.
- The focused standards suite passes 35 tests (one opt-in real-corpus test is skipped by default).
  With `INET_STANDARDS_PAGES` set, the real-corpus landmark test also passes.
- A full local audit classified all 20,283 base-standard candidates and all 3,712 amendment
  candidates. `Table 9-45` resolves to PDF page 741, `Figure 10-17` to PDF page 1913, top-level
  clause `10` to PDF page 1874, and Annex D to PDF page 5642. No `2.16 GHz` occurrence receives a
  clause node. Remaining duplicate-number cases are emitted as explicit ambiguity diagnostics.

### Phase 3 — Add structural storage and exact navigation

Status: completed on 2026-09-03. The processor publishes canonical document text,
physical-page views, per-document node/occurrence/diagnostic JSONL, and a relational SQLite index
with contentless FTS. The CLI, standards skill, generated agent metadata, and command tests share
the same contract.

Suggested incremental modules:

```text
python/inet/standards/
    model.py
    structure.py
    index.py
```

Avoid splitting `processor.py` further until responsibilities actually require it.

Add generated artifacts such as:

```text
processed/structure/<document>.jsonl
```

Extend SQLite with documents, canonical nodes, occurrences, and hierarchy edges.

Add:

```text
inet_process_standards get clause 10.25.2 --document ieee80211-2024
inet_process_standards get table 9-45 --document ieee80211-2024
inet_process_standards get figure 10-17 --document ieee80211-2024
```

Options can then include `--children`, `--ancestors`, `--context`, and `--json`.

Acceptance:

- Canonical node IDs are unique within a document.
- Cross-document ambiguity requires `--document`.
- Missing parents become lint findings, not fabricated links.
- Node IDs and source-span locators are the public retrieval identities.
- `build`, `status`, `lint`, `get`, and `search` form the structural CLI. Phase 4 extends this
  contract with graph and definition operations.

Integration requirements:

- Update `ieee80211-standards`, `.agents/skill-suite.yaml`, CLI tests, and all tracked command examples
  with the command contract.
- Use `inet_process_standards` as the tracked launcher name in every caller and example.

Completed evidence:

- The focused standards suite passes 47 tests (one opt-in landmark test is skipped by default), and
  the repository skill suite passes all 22 tests.
- A whole-corpus build atomically published 10,444 base-standard
  nodes from 20,283 classified occurrences and 1,679 amendment nodes from 3,712 occurrences.
- `status` reports both documents fresh under canonical identities `ieee80211-2024` and
  `ieee80211be-2024`, while extractor freshness remains a separate result.
- Exact retrieval resolves clause 10.25.2 to PDF pages 2051–2056, Table 9-45 to page 741, and
  Figure 10-17 to pages 1913–1914. Cross-document clause 10.1 fails without `--document`.
- Lint exposes unresolved ambiguities and 68 missing-parent findings without fabricating hierarchy
  edges. Malformed node identifiers fail canonical node-ID validation.

### Phase 4 — Cross-references, definitions, and lint

Status: completed on 2026-09-03. The corpus adds a conservative semantic pass after all
canonical nodes exist, publishes exact definition and reference evidence, and derives incoming
edges only from references with resolved targets. The standards skill and generated agent metadata
describe the complete command surface.

Extract references only after canonical nodes exist.

Store:

- raw reference text and source span;
- resolved target when unambiguous;
- unresolved or ambiguous status otherwise;
- derived reverse edges.

Add `refs`, `referenced-by`, `define`, and `lint`.

After this phase, `build`, `status`, `lint`, `get`, `search`, `refs`, `referenced-by`, and `define`
form the complete planned CLI contract. Extend the standards skill and its command tests in the same
commit as these new operations.

For a curated ADDBA reference sample, require zero incorrectly resolved edges; incomplete resolution is acceptable if reported explicitly.

Improve lexical search only where evaluation demonstrates a failure. Exact labels and headings should outrank BM25. Embeddings remain out of scope.

Completed evidence:

- Definitions are canonical nodes extracted from paragraph entries under Clause 3 definition
  sections. Exact, case-insensitive `define` lookup requires `--document` when base and amendment
  terms overlap; the rebuilt corpus contains 743 base definitions and 66 amendment definitions.
- Cross-reference records retain raw source text, exact hashed spans, resolution status, candidates,
  and reasons. Resolution prefers the source document and then its declared `amends` documents;
  external qualifiers, missing targets, and uncertain candidates are never guessed.
- The rebuilt corpus contains 19,013 base references (18,793 resolved, 220 unresolved) and 3,758
  amendment references (3,571 resolved, 187 unresolved). A whole-artifact audit round-tripped every
  JSONL record and verified every source hash and stored node target.
- The curated real Clause 10.25.2 ADDBA sample has 15 correctly resolved occurrences and one
  explicitly unresolved occurrence (`31.2.3`), with zero incorrectly resolved edges. The same
  precision rule is covered by a license-safe synthetic fixture.
- `refs` returns outgoing resolved, unresolved, and ambiguous records; `referenced-by` derives only
  incoming resolved edges. Exact definition headings outrank BM25 in the evaluated search case.
- The complete CLI is `build`, `status`, `lint`, `get`, `search`, `refs`, `referenced-by`, and
  `define`.
- The focused standards suite passes 58 tests with two real-corpus checks skipped by default; both
  real-corpus checks pass when enabled. The repository skill suite passes all 22 tests, generated
  metadata is in sync, and the standards skill passes its focused validator.

### Phase 5 — Non-authoritative ADDBA IR pilot

Repository ownership:

- Schema and validator: `inet-skills/python/inet/spec/`.
- Source-derived pilot: ignored local output under `../inet-pr-doc-project/standards/processed/spec-pilot/addba/`.
- Commit only license-safe synthetic fixtures and an evaluation report.

Start with one `feature.yaml`, not six synchronized files. Include sections for:

- source obligations;
- roles, conditions, actions, and qualifiers;
- state transitions and exchange steps;
- invariants;
- INET path/symbol mappings;
- test/configuration/selector mappings.

Use stable semantic slugs rather than sequential `BA-001` identifiers. Avoid calling these project `requirements`; that term already has canonical `R-*` ownership.

Track independent axes instead of one overloaded status:

```text
source review: draft / source-checked / disputed
implementation: unmapped / mapped / implemented
verification: uncovered / covered / verified
```

Pilot scope:

- successful ADDBA setup;
- refusal;
- response timeout;
- DELBA/termination;
- originator and recipient state;
- relevant capability and TID conditions.

Acceptance:

- Every obligation is atomic and has a canonical source node and reviewed source hash.
- Every mapped implementation/test target resolves or is explicitly recorded as a gap.
- No substantial verbatim IEEE text is committed.
- A second source-check pass records omitted qualifications and disagreements instead of silently resolving them.
- `inet_spec validate` and `inet_spec trace <id>` work on the pilot.

Completed evidence:

- `python/inet/spec/feature-v1.schema.json` defines a strict single-file, non-authoritative feature
  manifest. `bin/inet_spec` validates the schema, semantic links, two-pass review, independent
  status axes, source spans and hashes, and optional INET code/test targets; `trace` returns forward
  and reverse links for any stable semantic ID.
- A license-safe synthetic handshake fixture exercises the complete source-to-code-to-test chain.
  The focused suite passes 25 tests, including negative cases for authority promotion, sequential
  identifiers, dangling links, inconsistent status axes, source drift, missing target symbols, and
  absent second-pass qualifications.
- The ignored ADDBA pilot at
  `../inet-pr-doc-project/standards/processed/spec-pilot/addba/feature.yaml` validates with no errors
  or warnings against corpus format 2 and INET checkout
  `61c17cfa70558b4e1ff2788f475e22a016ea0302`.
- The pilot records 12 atomic obligations, 10 transitions, 5 exchanges, and 3 invariants. Source
  review classifies 11 obligations as `source-checked` and one response-timeout interpretation as
  `disputed`; implementation is 4 `implemented` and 8 `mapped`; verification is 4 `covered` and 8
  `uncovered`, with none overstated as `verified`.
- The second source pass explicitly excludes specialized Block Ack variants and agreement
  modification, preserves capability/TID/token/status as independent conditions, and records that
  the 2024 corpus exposes only a deprecated response-timeout MIB attribute rather than an identified
  setup-procedure outcome.
- The evaluation report in `reports/addba-ir-pilot-evaluation-20260903.md` recommends passing the
  value gate while deferring canonical placement, approval ownership, and the new skill to Phase 6.

### Phase 6 — Productize only after the pilot

If the pilot demonstrates value:

- Decide and document the permanent INET location and identifier ownership.
- Create `inet-80211-feature-specification`.
- Add the new skill to `.agents/skill-suite.yaml`, its deployment profile, and positive/negative activation fixtures.
- Reuse `inet-code-authoring` for implementation; do not create a separate feature-implementation skill.
- Treat Mermaid as a generated view, never authoritative source.

This follows the skill-creator principle of proving a distinct workflow before adding another automatically discoverable skill.

## Deferred decision gates

Defer until demonstrated demand:

- MCP façade: after the Python service API has at least two real consumers.
- Printed-page recovery: after structural IDs work.
- Structured table cells or Docling: only for documented extraction failures.
- Embeddings: only if structural and lexical retrieval miss real queries.
- Formal models, TLA+, or UPPAAL: only for a selected feature whose state complexity warrants them.
- Neo4j: unnecessary while SQLite handles the traceability graph.

## Recommended commit series

In `inet-skills`:

1. `standards: add corpus diagnostics and parser fixtures`
2. `standards: add the canonical document and node model`
3. `standards: integrate corpus storage, CLI, index, and standards skill`
4. `standards: add reference navigation and definition lookup`
5. `spec: add feature manifest schema and validator`
6. `spec: evaluate the ADDBA pilot`
7. `skills: add feature-specification workflow` — only after the pilot gate

In `inet-pr-doc-project`, later and separately:

1. Record the project decision governing protocol-spec authority and placement.
2. Add the reviewed ADDBA specification and traceability mappings.

Baseline checks pass: all standards processor tests pass, and the skill suite validates with only
the expected missing-walkthrough-analyzer warnings. These results record the verification state of
the documented interface.
