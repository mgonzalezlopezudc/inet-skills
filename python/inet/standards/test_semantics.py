import hashlib
import os
import unittest
from collections import Counter
from dataclasses import replace
from pathlib import Path

try:
    from . import index as standards_index
    from . import model, semantics, structure
except ImportError:
    import index as standards_index
    import model
    import semantics
    import structure


HASH = "a" * 64


class StandardsSemanticsTest(unittest.TestCase):
    def document(self, document_id="ieee80211-2024", *, amendment=False):
        return model.StandardDocument(
            document_id=document_id,
            title=document_id,
            revision="2024",
            kind=(
                model.DocumentKind.AMENDMENT
                if amendment
                else model.DocumentKind.BASE_STANDARD
            ),
            source_path=f"{document_id}.pdf",
            source_sha256=("b" if amendment else "a") * 64,
            pdf_page_count=1,
            amends=("ieee80211-2024",) if amendment else (),
        )

    def base_analysis(self):
        text = (
            "3. Terms and definitions\n"
            "3.1 Definitions\n\n"
            "access point: An entity that provides access to a distribution system.\n\n"
            "add block acknowledgment (ADDBA): The action used to establish an agreement.\n\n"
            "5.1 External collision\n"
            "Local text.\n"
            "10. Medium access control\n"
            "10.25 Block acknowledgment\n"
            "10.25.2 ADDBA setup\n"
            "The exchange is described in 10.25.3 and uses Table 9-45.\n"
            "The missing behavior is defined in 31.2.3.\n"
            "The external rule is in Clause 5.1 of IEEE Std 802.1X-2020.\n"
            "10.25.3 Data transfer\n"
            "Transfer text.\n"
            "Table 9-45—ADDBA fields\n"
            "Field text.\n"
        )
        return structure.analyze_structure(self.document(), [(1, text)])

    def test_definitions_are_exact_nodes_under_the_definition_clause(self):
        analyses, _ = semantics.analyze_semantics(
            {"ieee80211-2024": self.base_analysis()}
        )
        analysis = analyses["ieee80211-2024"]
        definitions = [
            node for node in analysis.nodes if node.kind == model.NodeKind.DEFINITION
        ]

        self.assertEqual(
            ["access point", "add block acknowledgment (ADDBA)"],
            [node.label for node in definitions],
        )
        parent = next(node for node in analysis.nodes if node.label == "3.1")
        self.assertEqual(
            [node.node_id for node in definitions],
            list(parent.child_ids),
        )
        for node in definitions:
            span = node.source_spans[0]
            source_text = analysis.text[span.start_offset : span.end_offset]
            self.assertTrue(source_text.startswith(node.label + ":"))
            self.assertEqual(
                hashlib.sha256(source_text.encode()).hexdigest(), span.text_sha256
            )

    def test_addba_reference_sample_has_no_incorrect_resolved_edges(self):
        analyses, references = semantics.analyze_semantics(
            {"ieee80211-2024": self.base_analysis()}
        )
        analysis = analyses["ieee80211-2024"]
        addba_id = "ieee80211-2024:clause:10.25.2"
        sample = [
            reference
            for reference in references["ieee80211-2024"]
            if reference.source_node_id == addba_id
        ]
        resolved = {
            reference.raw_text: reference.target_node_id
            for reference in sample
            if reference.status == model.ReferenceStatus.RESOLVED
        }

        self.assertEqual(
            {
                "10.25.3": "ieee80211-2024:clause:10.25.3",
                "Table 9-45": "ieee80211-2024:table:9-45",
            },
            resolved,
        )
        unresolved = {
            reference.raw_text: reference.reason
            for reference in sample
            if reference.status == model.ReferenceStatus.UNRESOLVED
        }
        self.assertIn("31.2.3", unresolved)
        self.assertIn("Clause 5.1", unresolved)
        self.assertIn("external standards document", unresolved["Clause 5.1"])
        self.assertTrue(
            any(
                diagnostic.code == "unresolved-reference"
                and diagnostic.node_id == addba_id
                for diagnostic in analysis.diagnostics
            )
        )

    def test_amendment_reference_resolves_only_through_declared_amends(self):
        amendment_text = (
            "10. Amendment material\n"
            "10.25.9 Changed procedure\n"
            "The exchange is described in 10.25.3.\n"
        )
        base = self.base_analysis()
        older_document = replace(
            self.document(), document_id="ieee80211-2016", revision="2016"
        )
        older_base = structure.analyze_structure(
            older_document, [(1, "10. Older base\n10.25.3 Older transfer\nOlder text.\n")]
        )
        amendment = structure.analyze_structure(
            self.document("ieee80211be-2024", amendment=True),
            [(1, amendment_text)],
        )
        _, references = semantics.analyze_semantics(
            {
                "ieee80211-2016": older_base,
                "ieee80211-2024": base,
                "ieee80211be-2024": amendment,
            }
        )

        reference = references["ieee80211be-2024"][0]
        self.assertEqual(model.ReferenceStatus.RESOLVED, reference.status)
        self.assertEqual(
            "ieee80211-2024:clause:10.25.3", reference.target_node_id
        )

    def test_missing_target_does_not_resolve_through_another_base_edition(self):
        older_document = replace(
            self.document(), document_id="ieee80211-2016", revision="2016"
        )
        older_base = structure.analyze_structure(
            older_document,
            [(1, "10. Older base\n10.24.2 Older setup\nSee 10.25.3.\n")],
        )
        _, references = semantics.analyze_semantics(
            {"ieee80211-2016": older_base, "ieee80211-2024": self.base_analysis()}
        )
        (reference,) = references["ieee80211-2016"]
        self.assertEqual(model.ReferenceStatus.UNRESOLVED, reference.status)
        self.assertIsNone(reference.target_node_id)

    def test_annex_prose_does_not_create_partial_labels(self):
        text = (
            "3. Local material\n3.1 Discussion\n"
            "This annex is informative. This annex seeks clarity. See Annex AA.\n"
            "Annex AA\n(informative)\n\nExample\n"
        )
        analysis = structure.analyze_structure(self.document(), [(1, text)])
        _, references = semantics.analyze_semantics({analysis.document.document_id: analysis})
        self.assertEqual(["Annex AA"], [r.raw_text for r in references[analysis.document.document_id]])
        self.assertEqual(model.ReferenceStatus.RESOLVED, references[analysis.document.document_id][0].status)

    def test_external_qualification_must_attach_to_the_reference(self):
        text = (
            "5. Local target\n5.1 Local rule\nRule text.\n"
            "10. Local material\n10.1 Discussion\n"
            "IEEE 802.1X authentication uses the local procedure (see 5.1).\n"
            "IEEE Std 802.11, Clause 5.1 describes the local procedure.\n"
            "IEEE Std 802.11-2024, Clause 5.1 describes the same procedure.\n"
            "Clause 5.1 of IEEE Std 802.1X-2020 describes an external procedure.\n"
            "IEEE Std 802.11-2016, Clause 5.1 belongs to another edition.\n"
        )
        analysis = structure.analyze_structure(self.document(), [(1, text)])
        _, references = semantics.analyze_semantics({analysis.document.document_id: analysis})
        self.assertEqual(
            [model.ReferenceStatus.RESOLVED] * 3 + [model.ReferenceStatus.UNRESOLVED] * 2,
            [r.status for r in references[analysis.document.document_id]],
        )

    def test_table_columns_and_protocol_terms_are_not_measurement_units(self):
        text = (
            "9. Formats\n9.4.2.1 Element\nElement text.\n"
            "10. Local material\n10.1 Discussion\n"
            "As defined in 9.4.2.1    A set of values.\n"
            "See 9.4.2.1\nA new paragraph follows.\n"
            "See Table 9-1    M    Y\nSee Annex C    M    Y\n"
            "The signal is specified in 2.16 GHz.\n"
            "Table 9-1—Values\nTable text.\n"
            "Annex C\n(normative)\n\nMIB\n"
        )
        analysis = structure.analyze_structure(self.document(), [(1, text)])
        _, references = semantics.analyze_semantics({analysis.document.document_id: analysis})
        refs = references[analysis.document.document_id]
        self.assertEqual([model.ReferenceStatus.RESOLVED] * 4, [r.status for r in refs[:4]])
        self.assertEqual(model.ReferenceStatus.UNRESOLVED, refs[4].status)
        self.assertIn("measurement unit", refs[4].reason)


@unittest.skipUnless(
    os.environ.get("INET_STANDARDS_CORPUS"),
    "set INET_STANDARDS_CORPUS for whole-corpus semantic checks",
)
class RealCorpusSemanticTest(unittest.TestCase):
    def test_curated_addba_edges_have_no_incorrect_resolution(self):
        result = standards_index.references(
            Path(os.environ["INET_STANDARDS_CORPUS"]),
            kind="clause",
            label="10.25.2",
            document_id="ieee80211-2024",
        )
        resolved = Counter(
            (reference["raw_text"], reference["target_node_id"])
            for reference in result["references"]
            if reference["status"] == "resolved"
        )
        expected = Counter(
            {
                ("10.46", "ieee80211-2024:clause:10.46"): 3,
                ("23.3.12.2.6", "ieee80211-2024:clause:23.3.12.2.6"): 1,
                ("10.25.3", "ieee80211-2024:clause:10.25.3"): 1,
                ("9.4.2.279", "ieee80211-2024:clause:9.4.2.279"): 1,
                ("10.25.6.5", "ieee80211-2024:clause:10.25.6.5"): 2,
                ("10.25.6.6", "ieee80211-2024:clause:10.25.6.6"): 1,
                ("10.25.6.7", "ieee80211-2024:clause:10.25.6.7"): 1,
                ("10.25.6", "ieee80211-2024:clause:10.25.6"): 2,
                ("10.38.7.3", "ieee80211-2024:clause:10.38.7.3"): 1,
                ("10.29", "ieee80211-2024:clause:10.29"): 1,
                ("11.5.2", "ieee80211-2024:clause:11.5.2"): 1,
                ("31.2.3", "ieee80211-2024:clause:31.2.3"): 1,
            }
        )
        self.assertEqual(expected, resolved)
        self.assertEqual(
            [],
            [
                (reference["raw_text"], reference["status"])
                for reference in result["references"]
                if reference["status"] != "resolved"
            ],
        )


if __name__ == "__main__":
    unittest.main()
