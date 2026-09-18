"""Landmarks checked against IEEE Std 802.15.4-2024 physical PDF pages.

The licensed source is not embedded in tests. Set INET_STANDARDS_CORPUS to a
complete generated corpus containing ieee802154-2024 to run these checks.
"""

import os
import unittest
from pathlib import Path

try:
    from . import index
except ImportError:
    import index


@unittest.skipUnless(os.environ.get("INET_STANDARDS_CORPUS"), "requires generated corpus")
class Ieee802154CorpusTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(os.environ["INET_STANDARDS_CORPUS"])
        self.document = "ieee802154-2024"

    def test_exact_navigation_uses_body_pages_not_contents_entries(self):
        for kind, label, page, title in (
            ("clause", "6.3.2.1", 63, "CSMA-CA algorithm"),
            ("table", "7-1", 79, "Values of the Frame Type field"),
            ("figure", "6-2", 64, "CSMA-CA algorithm"),
            ("clause", "13", 614, "O-QPSK PHY"),
            ("clause", "16", 641, "HRP UWB PHY"),
        ):
            with self.subTest(kind=kind, label=label):
                node = index.get_node(self.root, node_id=f"{self.document}:{kind}:{label}")
                self.assertEqual(page, node["page_start"])
                self.assertEqual(title, node["title"])
                self.assertEqual(self.document, node["document_id"])

    def test_definition_and_search_are_document_scoped(self):
        definition = index.define(self.root, "ASSOCIATION", document_id=self.document)
        self.assertEqual(43, definition["page_start"])
        self.assertEqual(f"{self.document}:clause:3.1", definition["parent_id"])
        results = index.search(self.root, "CSMA-CA", document_id=self.document)
        self.assertTrue(results)
        self.assertTrue(all(row["document_id"] == self.document for row in results))

    def test_csma_references_stay_in_the_802154_document(self):
        result = index.references(
            self.root, kind="clause", label="6.3.2.1", document_id=self.document
        )
        self.assertEqual(
            {
                ("10.22.4.1", "resolved", f"{self.document}:clause:10.22.4.1"),
                ("10.11", "resolved", f"{self.document}:clause:10.11"),
                ("Figure 6-2", "resolved", f"{self.document}:figure:6-2"),
            },
            {(r["raw_text"], r["status"], r["target_node_id"]) for r in result["references"]},
        )


if __name__ == "__main__":
    unittest.main()
