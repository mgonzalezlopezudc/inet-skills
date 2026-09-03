import tempfile
import unittest
from pathlib import Path

try:
    from . import corpus, index, model, semantics, structure
except ImportError:
    import corpus
    import index
    import model
    import semantics
    import structure


HASH = "a" * 64


class StandardsIndexTest(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.layout = corpus.CorpusLayout(self.root)
        self.base = model.StandardDocument(
            document_id="ieee80211-2024",
            title="IEEE Std 802.11-2024",
            revision="2024",
            kind=model.DocumentKind.BASE_STANDARD,
            source_path="base.pdf",
            source_sha256=HASH,
            pdf_page_count=1,
        )
        self.amendment = model.StandardDocument(
            document_id="ieee80211be-2024",
            title="IEEE Std 802.11be-2024",
            revision="2024",
            kind=model.DocumentKind.AMENDMENT,
            source_path="amendment.pdf",
            source_sha256="b" * 64,
            pdf_page_count=1,
            amends=("ieee80211-2024",),
        )
        base_text = (
            "3. Terms and definitions\n"
            "3.1 Definitions\n\n"
            "association: The service that establishes a mapping.\n\n"
            "10. Medium access control\n"
            "Overview text.\n"
            "10.1 Block Ack overview\n"
            "Block Ack setup behavior and dialog tokens are described in 11.2.\n"
            "11.2 Orphan child\n"
            "Orphan text.\n"
        )
        amendment_text = (
            "3. Terms and definitions\n"
            "3.1 Definitions\n\n"
            "association: The amended service that establishes a mapping.\n\n"
            "10. Amendment material\n"
            "Amendment overview.\n"
            "10.1 Block Ack overview\n"
            "Enhanced Block Ack setup behavior is described in 11.2.\n"
        )
        structural_analyses = {
            self.base.document_id: structure.analyze_structure(
                self.base, [(1, base_text)]
            ),
            self.amendment.document_id: structure.analyze_structure(
                self.amendment, [(1, amendment_text)]
            ),
        }
        self.analyses, self.references = semantics.analyze_semantics(
            structural_analyses
        )
        self.manifest = corpus.CorpusManifest(
            generated_at="2026-09-03T12:00:00+00:00",
            extractor=corpus.ExtractionRecord(
                implementation="test", version="1", arguments=()
            ),
            documents=(self.base, self.amendment),
        )
        for document in self.manifest.documents:
            analysis = self.analyses[document.document_id]
            self.layout.text(document.document_id).parent.mkdir(parents=True)
            self.layout.text(document.document_id).write_text(
                analysis.text, encoding="utf-8"
            )
        corpus.write_manifest(self.root, self.manifest)
        index.build_index(
            self.layout, self.manifest, self.analyses, self.references
        )

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_exact_lookup_requires_document_for_cross_document_label(self):
        with self.assertRaisesRegex(index.StandardsIndexError, "specify --document"):
            index.get_node(self.root, kind="clause", label="10.1")

        item = index.get_node(
            self.root,
            kind="clause",
            label="10.1",
            document_id="ieee80211-2024",
            include_ancestors=True,
        )

        self.assertEqual("ieee80211-2024:clause:10.1", item["node_id"])
        self.assertIn("Block Ack setup behavior", item["text"])
        self.assertEqual("10", item["ancestors"][0]["label"])

    def test_children_and_source_span_locator_are_exact(self):
        parent = index.get_node(
            self.root,
            kind="clause",
            label="10",
            document_id="ieee80211-2024",
            include_children=True,
        )
        self.assertEqual(["10.1"], [child["label"] for child in parent["children"]])

        locator = parent["source_spans"][0]["locator"]
        span = index.get_source_span(self.root, locator, context_characters=5)
        self.assertEqual(parent["text"], span["text"])
        self.assertIn("context", span)

    def test_search_returns_canonical_nodes_and_exact_label_first(self):
        results = index.search(
            self.root, "Block Ack setup", document_id="ieee80211-2024"
        )
        self.assertEqual("10.1", results[0]["label"])
        self.assertIn("Block Ack setup", results[0]["snippet"])

        exact = index.search(self.root, "clause 10.1")
        self.assertTrue(all(result["label"] == "10.1" for result in exact[:2]))

    def test_lint_exposes_missing_parent_without_fabricating_link(self):
        report = index.lint(
            self.root, document_id="ieee80211-2024", minimum_severity="info"
        )
        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("missing-parent", codes)
        orphan = index.get_node(
            self.root,
            kind="clause",
            label="11.2",
            document_id="ieee80211-2024",
        )
        self.assertIsNone(orphan["parent_id"])

    def test_refs_and_referenced_by_use_resolved_relational_edges(self):
        outgoing = index.references(
            self.root,
            kind="clause",
            label="10.1",
            document_id="ieee80211-2024",
        )
        self.assertEqual(1, outgoing["total"])
        self.assertEqual("resolved", outgoing["references"][0]["status"])
        self.assertEqual(
            "ieee80211-2024:clause:11.2",
            outgoing["references"][0]["target_node_id"],
        )

        incoming = index.referenced_by(
            self.root,
            kind="clause",
            label="11.2",
            document_id="ieee80211-2024",
        )
        self.assertEqual(2, incoming["total"])
        self.assertEqual(
            {
                "ieee80211-2024:clause:10.1",
                "ieee80211be-2024:clause:10.1",
            },
            {
                reference["source_node_id"]
                for reference in incoming["references"]
            },
        )

    def test_reference_query_verifies_raw_source_span_hash(self):
        result = index.references(
            self.root,
            kind="clause",
            label="10.1",
            document_id="ieee80211-2024",
        )
        span = result["references"][0]["source_span"]
        path = self.layout.text("ieee80211-2024")
        text = path.read_text(encoding="utf-8")
        start = span["start_offset"]
        replacement = "X" if text[start] != "X" else "Y"
        path.write_text(text[:start] + replacement + text[start + 1 :], encoding="utf-8")

        with self.assertRaisesRegex(index.StandardsIndexError, "hash mismatch"):
            index.references(
                self.root,
                kind="clause",
                label="10.1",
                document_id="ieee80211-2024",
            )

    def test_define_is_case_insensitive_and_requires_document_when_ambiguous(self):
        with self.assertRaisesRegex(index.StandardsIndexError, "specify --document"):
            index.define(self.root, "association")

        definition = index.define(
            self.root, "Association", document_id="ieee80211-2024"
        )
        self.assertEqual("definition", definition["kind"])
        self.assertEqual("association", definition["label"])
        self.assertTrue(definition["text"].startswith("association:"))

    def test_index_stores_relations_but_not_a_second_copy_of_node_text(self):
        connection = index.sqlite3.connect(self.layout.index)
        try:
            node_columns = {
                row[1] for row in connection.execute("PRAGMA table_info(nodes)")
            }
            fts_sql = connection.execute(
                "SELECT sql FROM sqlite_master WHERE name = 'node_fts'"
            ).fetchone()[0]
        finally:
            connection.close()
        self.assertNotIn("text", node_columns)
        self.assertIn("content=''", fts_sql)

    def test_document_counts_do_not_multiply_relations(self):
        counts = index.document_counts(self.root)
        self.assertEqual(
            len(self.analyses[self.base.document_id].nodes),
            counts[self.base.document_id]["nodes"],
        )
        self.assertEqual(
            len(self.analyses[self.base.document_id].occurrences),
            counts[self.base.document_id]["occurrences"],
        )
        self.assertEqual(
            len(self.references[self.base.document_id]),
            counts[self.base.document_id]["references"],
        )


if __name__ == "__main__":
    unittest.main()
