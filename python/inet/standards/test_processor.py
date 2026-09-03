import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

try:
    from . import corpus, model, processor
except ImportError:
    import corpus
    import model
    import processor


class StandardsProcessorTest(unittest.TestCase):
    def test_page_spec_is_sorted_unique_and_rejects_empty_components(self):
        self.assertEqual((1, 2, 4), processor.parse_page_spec("4,1-2,2"))
        with self.assertRaisesRegex(ValueError, "empty component"):
            processor.parse_page_spec("1,,2")

    def test_document_profiles_separate_base_and_amendment_identities(self):
        base = processor.profile_for_pdf(Path("80211ax-2024.pdf"))
        amendment = processor.profile_for_pdf(Path("80211be-2024.pdf"))
        self.assertEqual("ieee80211-2024", base.document_id)
        self.assertEqual(model.DocumentKind.BASE_STANDARD, base.kind)
        self.assertEqual((base.document_id,), amendment.amends)
        with self.assertRaisesRegex(ValueError, "no reviewed document profile"):
            processor.profile_for_pdf(Path("supporting.pdf"))

    def test_extraction_preserves_requested_physical_page_numbers(self):
        completed = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"first\fsecond\f", stderr=b""
        )
        with mock.patch.object(processor, "run_command", return_value=completed):
            pages = processor.extract_pdf_pages(
                Path("80211ax-2024.pdf"), (7, 8), 10
            )
        self.assertEqual([(7, "first"), (8, "second")], pages)

    def test_build_publishes_complete_structural_corpus(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pdf = root / "80211ax-2024.pdf"
            pdf.write_bytes(b"test pdf")
            output = root / "processed"
            document = model.StandardDocument(
                document_id="ieee80211-2024",
                title="IEEE Std 802.11-2024",
                revision="2024",
                kind=model.DocumentKind.BASE_STANDARD,
                source_path=str(pdf),
                source_sha256="a" * 64,
                pdf_page_count=1,
            )
            extractor = corpus.ExtractionRecord(
                implementation="test", version="1", arguments=()
            )
            page_text = "10. Medium access control\n10.1 Block Ack\nSetup text.\n"
            with (
                mock.patch.object(processor, "expected_document", return_value=document),
                mock.patch.object(processor, "extraction_record", return_value=extractor),
                mock.patch.object(
                    processor, "extract_pdf_pages", return_value=[(1, page_text)]
                ),
            ):
                result = processor.build(output_dir=output, pdfs=[str(pdf)])

            layout = corpus.CorpusLayout(output)
            self.assertEqual("built", result["status"])
            self.assertTrue(layout.nodes(document.document_id).is_file())
            self.assertTrue(layout.occurrences(document.document_id).is_file())
            self.assertTrue(layout.diagnostics(document.document_id).is_file())
            self.assertTrue(layout.references(document.document_id).is_file())
            self.assertTrue(layout.index.is_file())
            self.assertTrue(layout.manifest.is_file())

    def test_partial_build_requires_one_document(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            processor.build(
                pdfs=["80211ax-2024.pdf", "80211be-2024.pdf"],
                page_spec="1-2",
            )

    def test_status_reports_malformed_corpus_as_incompatible(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "processed"
            output.mkdir()
            (output / corpus.MANIFEST_FILENAME).write_text(
                '{"format": "inet-standards-corpus", "format_version": 2}\n',
                encoding="utf-8",
            )
            result = processor.status(
                output_dir=output, standards_dir=Path(directory) / "standards"
            )
        self.assertEqual("incompatible", result["corpus_state"])
        self.assertIn("rebuild", result["corpus_error"])

    def test_status_reports_extractor_staleness_separately_from_source_hash(self):
        document = model.StandardDocument(
            document_id="ieee80211-2024",
            title="IEEE Std 802.11-2024",
            revision="2024",
            kind=model.DocumentKind.BASE_STANDARD,
            source_path="base.pdf",
            source_sha256="a" * 64,
            pdf_page_count=1,
        )
        recorded_extractor = corpus.ExtractionRecord(
            implementation="test", version="recorded", arguments=()
        )
        current_extractor = corpus.ExtractionRecord(
            implementation="test", version="runtime", arguments=()
        )
        manifest = corpus.CorpusManifest(
            generated_at="2026-09-03T12:00:00+00:00",
            extractor=recorded_extractor,
            documents=(document,),
        )
        with (
            mock.patch.object(
                processor,
                "discover_pdfs",
                return_value=[Path("80211ax-2024.pdf")],
            ),
            mock.patch.object(processor, "expected_document", return_value=document),
            mock.patch.object(processor, "extraction_record", return_value=current_extractor),
            mock.patch.object(processor.corpus, "validate_complete_corpus", return_value=manifest),
            mock.patch.object(processor.structural_index, "document_counts", return_value={}),
        ):
            result = processor.status()
        self.assertEqual("ready", result["corpus_state"])
        self.assertEqual("stale", result["extractor_state"])
        self.assertEqual("stale", result["documents"][0]["state"])


if __name__ == "__main__":
    unittest.main()
