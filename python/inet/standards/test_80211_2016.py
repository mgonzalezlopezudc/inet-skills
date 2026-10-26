"""Check IEEE Std 802.11-2016 landmarks against physical PDF pages.

The tests contain no licensed source text. Set INET_STANDARDS_CORPUS to a
complete generated corpus with the 2016 and 2024 editions.
"""

import json
import os
import unittest
from collections import Counter
from pathlib import Path

try:
    from . import index
except ImportError:
    import index


@unittest.skipUnless(os.environ.get("INET_STANDARDS_CORPUS"), "requires generated corpus")
class Ieee802112016CorpusTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(os.environ["INET_STANDARDS_CORPUS"])
        self.document = "ieee80211-2016"

    def test_exact_navigation_uses_body_pages_not_contents_entries(self):
        for kind, label, page, title in (
            ("clause", "3.1", 129, "Definitions"),
            ("clause", "2", 126, "Normative references"),
            ("clause", "3", 129, "Definitions, acronyms, and abbreviations"),
            ("clause", "1.5", 125, "Terminology for mathematical, logical, and bit operations"),
            ("clause", "10.24", 1416, "Block acknowledgment (block ack)"),
            ("clause", "10.24.2", 1417, "Setup and modification of the block ack parameters"),
            ("clause", "19", 2335, "High-throughput (HT) PHY specification"),
            ("clause", "21", 2498, "Very high throughput (VHT) PHY specification"),
            ("table", "9-45", 729, "Reason codes"),
            ("figure", "10-17", 1328, "Backoff procedure for DMG STAs"),
            ("figure", "10-79", 1566, "Example beam"),
            ("clause", "9.7.1", 1288, "A-MPDU format"),
            ("clause", "14.10.10.3", 2184, "Conditions for generating and sending a PREP element"),
            ("clause", "20.3.6.4.2", 2449, "hFilt definition"),
            ("clause", "20.6.3.2.4.2", 2476, "π/2-BPSK modulation"),
            ("clause", "C", 2777, "ASN.1 encoding of the MAC and PHY MIB"),
        ):
            with self.subTest(kind=kind, label=label):
                node = index.get_node(
                    self.root, kind=kind, label=label, document_id=self.document
                )
                self.assertEqual(page, node["page_start"])
                self.assertEqual(title, node["title"])
                self.assertEqual(self.document, node["document_id"])

    def test_definition_and_search_are_document_scoped(self):
        definition = index.define(
            self.root, "ACCESS POINT (AP)", document_id=self.document
        )
        self.assertEqual(129, definition["page_start"])
        self.assertEqual(f"{self.document}:clause:3.1", definition["parent_id"])
        results = index.search(self.root, "Block Ack", document_id=self.document)
        self.assertTrue(results)
        self.assertTrue(all(row["document_id"] == self.document for row in results))

    def test_repeated_label_requires_an_explicit_document(self):
        with self.assertRaises(index.StandardsIndexError):
            index.get_node(self.root, kind="table", label="9-45")
        old = index.get_node(
            self.root, kind="table", label="9-45", document_id=self.document
        )
        new = index.get_node(
            self.root, kind="table", label="9-45", document_id="ieee80211-2024"
        )
        self.assertNotEqual(old["node_id"], new["node_id"])
        self.assertNotEqual(old["title"], new["title"])

    def test_addba_reference_stays_in_the_2016_edition(self):
        result = index.references(
            self.root, kind="clause", label="10.24.2", document_id=self.document
        )
        self.assertEqual(
            [("10.24.3", "resolved", f"{self.document}:clause:10.24.3")],
            [(r["raw_text"], r["status"], r["target_node_id"]) for r in result["references"]],
        )

    def test_all_resolved_references_stay_in_the_2016_edition(self):
        path = self.root / "structure" / self.document / "references.jsonl"
        resolved = []
        for line in path.read_text(encoding="utf-8").splitlines():
            reference = json.loads(line)
            if reference["status"] == "resolved":
                resolved.append(reference)
                self.assertTrue(reference["target_node_id"].startswith(self.document + ":"))
        self.assertTrue(resolved)

    def test_no_heading_or_reference_remains_ambiguous(self):
        result = index.lint(self.root, document_id=self.document, limit=1)
        self.assertNotIn("unresolved-heading-ambiguity", result["counts"].get("error", {}))
        self.assertNotIn("ambiguous-reference", result["counts"].get("error", {}))

    def test_wrapped_pics_clause_has_two_source_spans(self):
        node = index.get_node(
            self.root, kind="clause", label="B.4.14", document_id=self.document
        )
        self.assertEqual([2726, 2727], [s["pdf_page_start"] for s in node["source_spans"]])
        self.assertTrue(node["title"].endswith("(HCCA)"))

    def test_superscript_footnotes_do_not_change_clause_targets(self):
        for source, page, target in (("3.1", 129, "12.6.10.2"), ("10.22.3.1", 1394, "10.4")):
            result = index.references(
                self.root, kind="clause", label=source, document_id=self.document, limit=1000
            )
            matches = [r for r in result["references"]
                       if r["raw_text"] == target and r["source_span"]["pdf_page_start"] == page]
            self.assertEqual(1, len(matches))
            self.assertEqual("resolved", matches[0]["status"])
            self.assertEqual(f"{self.document}:clause:{target}", matches[0]["target_node_id"])

    def test_unresolved_references_match_the_reviewed_source_gaps(self):
        path = self.root / "structure" / self.document / "references.jsonl"
        unresolved = Counter()
        for line in path.read_text(encoding="utf-8").splitlines():
            reference = json.loads(line)
            if reference["status"] != "resolved":
                unresolved[(reference["source_span"]["pdf_page_start"], reference["raw_text"])] += 1
        self.assertEqual(Counter({
            (151, "5.8.1.9"): 1,
            (185, "Clause 12"): 1,
            (197, "clause 58"): 1,
            (646, "Clause 8"): 1,
            (1011, "8.3"): 1,
            (1146, "Table 9-629"): 1,
            (1284, "8.4.2.2"): 1,
            (1301, "8.6.8"): 1,
            (1591, "Clause 8"): 1,
            (1653, "11.5.18"): 1,
            (1657, "11.5.18"): 1,
            (1662, "21.7"): 1,
            (1667, "Clause 35"): 2,
            (1790, "Clause 12"): 1,
            (1840, "8.4"): 2,
            (2020, "11.2"): 1,
            (2633, "9.1710.20"): 1,
            (3469, "Annex A"): 1,
        }), unresolved)


if __name__ == "__main__":
    unittest.main()
