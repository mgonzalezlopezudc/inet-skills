import os
import unittest
from pathlib import Path

try:
    from . import model, structure
except ImportError:
    import model
    import structure


DOCUMENT_HASH = "a" * 64


class StandardsStructureTest(unittest.TestCase):
    def document(
        self,
        *,
        document_id="ieee80211-2024",
        kind=model.DocumentKind.BASE_STANDARD,
        amends=(),
        extracted_pdf_pages=None,
    ):
        return model.StandardDocument(
            document_id=document_id,
            title="IEEE wireless LAN standard",
            revision="2024",
            kind=kind,
            source_path=f"standards/{document_id}.pdf",
            source_sha256=DOCUMENT_HASH,
            pdf_page_count=6000,
            amends=amends,
            extracted_pdf_pages=extracted_pdf_pages,
        )

    def occurrence(self, analysis, kind, label, classification):
        return next(
            occurrence
            for occurrence in analysis.occurrences
            if occurrence.candidate.kind == kind
            and occurrence.candidate.label == label
            and occurrence.classification == classification
        )

    def test_table_and_figure_indexes_resolve_to_body_objects(self):
        pages = (
            (
                111,
                "Table 9-44—STA Info subfields ................................ 738\n"
                "Table 9-45—Feedback encoding for HE TB\n"
                "sounding ................................................... 740\n",
            ),
            (
                220,
                "Figure 10-16—EDMG transmission ............................ 1912\n"
                "Figure 10-17—HE MU PPDU transmission\n"
                "with acknowledgment ....................................... 1912\n",
            ),
            (741, "Table 9-45—Feedback encoding for HE TB sounding\n0 0 SU\n"),
            (1913, "Figure 10-17—HE MU PPDU transmission with acknowledgment\n"),
        )

        analysis = structure.analyze_structure(self.document(), pages)

        table_index = self.occurrence(
            analysis,
            model.NodeKind.TABLE,
            "9-45",
            model.OccurrenceClassification.INDEX_ENTRY,
        )
        table_body = self.occurrence(
            analysis,
            model.NodeKind.TABLE,
            "9-45",
            model.OccurrenceClassification.CANONICAL,
        )
        figure_index = self.occurrence(
            analysis,
            model.NodeKind.FIGURE,
            "10-17",
            model.OccurrenceClassification.INDEX_ENTRY,
        )
        figure_body = self.occurrence(
            analysis,
            model.NodeKind.FIGURE,
            "10-17",
            model.OccurrenceClassification.CANONICAL,
        )
        self.assertEqual(table_body.node_id, table_index.node_id)
        self.assertEqual(figure_body.node_id, figure_index.node_id)
        table_node = next(
            node for node in analysis.nodes if node.node_id == table_body.node_id
        )
        figure_node = next(
            node for node in analysis.nodes if node.node_id == figure_body.node_id
        )
        self.assertEqual(741, table_node.source_spans[0].pdf_page_start)
        self.assertEqual(741, table_node.source_spans[0].pdf_page_end)
        self.assertEqual(1, len(table_node.source_spans))
        self.assertEqual(1913, figure_node.source_spans[0].pdf_page_start)

    def test_decimal_measurements_are_retained_as_rejected_candidates(self):
        pages = (
            (
                280,
                "2.16 GHz mask physical layer protocol data unit\n"
                "5.5 MHz channel width\n"
                "2.16 Genuine structural heading\n",
            ),
        )

        analysis = structure.analyze_structure(self.document(), pages)

        rejected = [
            occurrence
            for occurrence in analysis.occurrences
            if occurrence.classification == model.OccurrenceClassification.REJECTED
        ]
        self.assertEqual({"2.16", "5.5"}, {item.candidate.label for item in rejected})
        self.assertTrue(all("measurement unit" in item.reason for item in rejected))
        self.assertIn(
            "ieee80211-2024:clause:2.16",
            {node.node_id for node in analysis.nodes},
        )

    def test_repeated_continued_caption_targets_one_canonical_node(self):
        pages = (
            (10, "Table 9-45—Feedback encoding\nfirst part\n"),
            (11, "Table 9-45—Feedback encoding (continued)\nsecond part\n"),
        )

        analysis = structure.analyze_structure(self.document(), pages)

        self.assertEqual(1, len(analysis.nodes))
        self.assertEqual(
            [
                model.OccurrenceClassification.CANONICAL,
                model.OccurrenceClassification.CONTINUATION,
            ],
            [occurrence.classification for occurrence in analysis.occurrences],
        )
        self.assertEqual(
            analysis.occurrences[0].node_id, analysis.occurrences[1].node_id
        )

    def test_duplicate_body_captions_remain_explicitly_ambiguous(self):
        pages = (
            (10, "Table 9-45—First plausible caption\n"),
            (30, "Table 9-45—Second plausible caption\n"),
        )

        analysis = structure.analyze_structure(self.document(), pages)

        self.assertFalse(analysis.nodes)
        self.assertTrue(
            all(
                occurrence.classification
                == model.OccurrenceClassification.AMBIGUOUS
                for occurrence in analysis.occurrences
            )
        )
        self.assertIn(
            "unresolved-heading-ambiguity",
            {diagnostic.code for diagnostic in analysis.diagnostics},
        )

    def test_identical_table_caption_on_next_page_is_implicit_continuation(self):
        pages = (
            (10, "Table 9-45—Feedback encoding\nfirst part\n"),
            (11, "Table 9-45—Feedback encoding\nsecond part\n"),
        )

        analysis = structure.analyze_structure(self.document(), pages)

        self.assertEqual(1, len(analysis.nodes))
        self.assertEqual(
            [
                model.OccurrenceClassification.CANONICAL,
                model.OccurrenceClassification.CONTINUATION,
            ],
            [occurrence.classification for occurrence in analysis.occurrences],
        )
        self.assertEqual(2, len(analysis.nodes[0].source_spans))

    def test_line_wrapped_reference_is_rejected_without_hiding_real_clause(self):
        pages = (
            (20, "19.3.5 and physical layer formats described elsewhere\n"),
            (200, "19.3.5 Modulation and coding scheme (MCS)\n"),
        )

        analysis = structure.analyze_structure(self.document(), pages)

        self.assertEqual(1, len(analysis.nodes))
        self.assertEqual(200, analysis.nodes[0].source_spans[0].pdf_page_start)
        self.assertEqual(
            model.OccurrenceClassification.REJECTED,
            analysis.occurrences[0].classification,
        )
        self.assertIn("reference or sentence", analysis.occurrences[0].reason)

    def test_top_level_clause_builds_hierarchy_and_owns_body_objects(self):
        page = (
            "IEEE Std 802.11-2024\n\n"
            "10. MAC sublayer functional description\n"
            "introductory text\n"
            "10.1 General\n"
            "general text\n"
            "10.1.1 Detailed behavior\n"
            "Table 10-1—Detailed values\n"
        )

        analysis = structure.analyze_structure(self.document(), ((1874, page),))
        nodes = {node.node_id: node for node in analysis.nodes}

        self.assertIn("ieee80211-2024:clause:10", nodes)
        self.assertEqual(
            "ieee80211-2024:clause:10",
            nodes["ieee80211-2024:clause:10.1"].parent_id,
        )
        self.assertEqual(
            "ieee80211-2024:clause:10.1",
            nodes["ieee80211-2024:clause:10.1.1"].parent_id,
        )
        self.assertEqual(
            "ieee80211-2024:clause:10.1.1",
            nodes["ieee80211-2024:table:10-1"].parent_id,
        )
        self.assertIn(
            "ieee80211-2024:clause:10.1",
            nodes["ieee80211-2024:clause:10"].child_ids,
        )

    def test_annex_heading_uses_title_and_parents_annex_clause(self):
        page = (
            "IEEE Std 802.11-2024\n\n"
            "Annex D\n"
            "(normative)\n\n"
            "Regulatory references\n"
            "D.1 External regulatory references\n"
        )

        analysis = structure.analyze_structure(self.document(), ((5642, page),))
        nodes = {node.node_id: node for node in analysis.nodes}

        self.assertEqual("Regulatory references", nodes["ieee80211-2024:clause:D"].title)
        self.assertEqual(
            "ieee80211-2024:clause:D",
            nodes["ieee80211-2024:clause:D.1"].parent_id,
        )

    def test_annex_reference_late_on_page_does_not_compete_with_annex_heading(self):
        reference_page = "\n".join(["table row"] * 20 + ["Annex D"]) + "\n"
        body_page = "IEEE Std 802.11-2024\n\nAnnex D\n(normative)\n\nTitle\n"

        analysis = structure.analyze_structure(
            self.document(), ((100, reference_page), (200, body_page))
        )

        self.assertEqual(1, len(analysis.nodes))
        self.assertEqual(200, analysis.nodes[0].source_spans[0].pdf_page_start)
        self.assertEqual(
            model.OccurrenceClassification.REJECTED,
            analysis.occurrences[0].classification,
        )

    def test_same_clause_label_in_base_and_amendment_has_separate_identity(self):
        base = structure.analyze_structure(
            self.document(), ((100, "10.25.2 Block Ack parameters\n"),)
        )
        amendment = structure.analyze_structure(
            self.document(
                document_id="ieee80211be-2024",
                kind=model.DocumentKind.AMENDMENT,
                amends=("ieee80211-2024",),
            ),
            ((100, "10.25.2 Block Ack parameters\n"),),
        )

        self.assertEqual("ieee80211-2024:clause:10.25.2", base.nodes[0].node_id)
        self.assertEqual(
            "ieee80211be-2024:clause:10.25.2", amendment.nodes[0].node_id
        )

    def test_partial_index_page_does_not_fabricate_body_node(self):
        document = self.document(extracted_pdf_pages=(111,))
        page = (
            "Table 9-44—STA Info subfields ................................. 738\n"
            "Table 9-45—Feedback encoding .................................. 740\n"
        )

        analysis = structure.analyze_structure(document, ((111, page),))

        self.assertFalse(analysis.nodes)
        self.assertTrue(
            all(
                occurrence.classification
                == model.OccurrenceClassification.INDEX_ENTRY
                for occurrence in analysis.occurrences
            )
        )
        self.assertTrue(all(occurrence.reason for occurrence in analysis.occurrences))

    def test_partial_page_selection_must_match_document_contract(self):
        document = self.document(extracted_pdf_pages=(10, 20))

        with self.assertRaisesRegex(ValueError, "extracted_pdf_pages"):
            structure.analyze_structure(document, ((10, "10.1 General\n"),))

    def test_diagnostics_cover_false_missing_small_large_and_duplicate_nodes(self):
        page = (
            "2.16 GHz channel\n"
            "10.2.1 Child without selected parent\n"
            "body text that makes the first node longer\n"
            "Table 10-1—One caption\n"
            "Table 10-1—Another caption\n"
            "Figure 10-2—X\n"
        )

        analysis = structure.analyze_structure(
            self.document(),
            ((20, page),),
            tiny_node_characters=30,
            oversized_node_characters=45,
        )
        codes = {diagnostic.code for diagnostic in analysis.diagnostics}

        self.assertTrue(
            {
                "false-heading-candidate",
                "missing-parent",
                "tiny-node",
                "oversized-node",
                "duplicate-label-candidates",
                "unresolved-heading-ambiguity",
            }.issubset(codes)
        )

    def test_wide_table_row_is_a_diagnosed_false_candidate(self):
        analysis = structure.analyze_structure(
            self.document(), ((4989, "23.5            CFS1G: M\n"),)
        )

        self.assertEqual(1, len(analysis.occurrences))
        self.assertEqual(
            model.OccurrenceClassification.REJECTED,
            analysis.occurrences[0].classification,
        )
        self.assertIn("wide column gap", analysis.occurrences[0].reason)

    def test_every_detected_candidate_has_exactly_one_classification(self):
        pages = (
            (
                1,
                "10. General\n"
                "10.1 Detail\n"
                "Table 10-1—Values\n"
                "2.16 GHz channel\n",
            ),
        )

        analysis = structure.analyze_structure(self.document(), pages)

        self.assertEqual(len(analysis.detected), len(analysis.occurrences))
        self.assertEqual(len(analysis.detected), sum(analysis.classification_counts.values()))


REAL_PAGES_ROOT = os.environ.get("INET_STANDARDS_PAGES")


@unittest.skipUnless(REAL_PAGES_ROOT, "set INET_STANDARDS_PAGES for corpus landmark checks")
class RealCorpusStructureLandmarkTest(unittest.TestCase):
    def test_known_base_standard_landmarks(self):
        root = Path(REAL_PAGES_ROOT)
        page_numbers = (111, 220, 280, 741, 1874, 1913, 5642)
        pages = tuple(
            (page, (root / f"page-{page:06d}.txt").read_text(encoding="utf-8"))
            for page in page_numbers
        )
        document = model.StandardDocument(
            document_id="ieee80211-2024",
            title="IEEE Std 802.11-2024",
            revision="2024",
            kind=model.DocumentKind.BASE_STANDARD,
            source_path="standards/80211ax-2024.pdf",
            source_sha256=DOCUMENT_HASH,
            pdf_page_count=5956,
            extracted_pdf_pages=page_numbers,
        )

        analysis = structure.analyze_structure(document, pages)
        occurrences = {
            (item.candidate.kind, item.candidate.label, item.classification): item
            for item in analysis.occurrences
        }
        nodes = {node.node_id: node for node in analysis.nodes}

        self.assertEqual(
            741,
            nodes["ieee80211-2024:table:9-45"].source_spans[0].pdf_page_start,
        )
        self.assertEqual(
            1913,
            nodes["ieee80211-2024:figure:10-17"].source_spans[0].pdf_page_start,
        )
        self.assertEqual(
            "ieee80211-2024:table:9-45",
            occurrences[
                (
                    model.NodeKind.TABLE,
                    "9-45",
                    model.OccurrenceClassification.INDEX_ENTRY,
                )
            ].node_id,
        )
        self.assertEqual(
            "ieee80211-2024:figure:10-17",
            occurrences[
                (
                    model.NodeKind.FIGURE,
                    "10-17",
                    model.OccurrenceClassification.INDEX_ENTRY,
                )
            ].node_id,
        )
        self.assertIn("ieee80211-2024:clause:10", nodes)
        self.assertIn("ieee80211-2024:clause:D", nodes)
        self.assertEqual(
            model.OccurrenceClassification.REJECTED,
            occurrences[
                (
                    model.NodeKind.CLAUSE,
                    "2.16",
                    model.OccurrenceClassification.REJECTED,
                )
            ].classification,
        )


if __name__ == "__main__":
    unittest.main()
