import tempfile
import unittest
from pathlib import Path
from unittest import mock

try:
    from . import corpus, model
except ImportError:
    import corpus
    import model


DOCUMENT_HASH = "a" * 64


class StandardsCorpusTest(unittest.TestCase):
    def manifest(self):
        return corpus.CorpusManifest(
            generated_at="2026-09-03T12:00:00+00:00",
            extractor=corpus.ExtractionRecord(
                implementation="poppler-pdftotext",
                version="1",
                arguments=("-layout",),
                tool_versions=(("pdftotext", "26.01.0"),),
            ),
            documents=(
                model.StandardDocument(
                    document_id="ieee80211-2024",
                    title="IEEE wireless LAN standard",
                    revision="2024",
                    kind=model.DocumentKind.BASE_STANDARD,
                    source_path="standards/local-standard.pdf",
                    source_sha256=DOCUMENT_HASH,
                    pdf_page_count=2,
                ),
            ),
        )

    def write_complete_corpus(self, root):
        manifest = self.manifest()
        layout = corpus.CorpusLayout(Path(root))
        layout.text("ieee80211-2024").parent.mkdir(parents=True)
        layout.text("ieee80211-2024").write_text("page one\fpage two\n", encoding="utf-8")
        for page in (1, 2):
            layout.page("ieee80211-2024", page).parent.mkdir(parents=True, exist_ok=True)
            layout.page("ieee80211-2024", page).write_text(
                f"page {page}\n", encoding="utf-8"
            )
        layout.nodes("ieee80211-2024").parent.mkdir(parents=True)
        layout.nodes("ieee80211-2024").write_text("", encoding="utf-8")
        layout.occurrences("ieee80211-2024").write_text("", encoding="utf-8")
        layout.diagnostics("ieee80211-2024").write_text("", encoding="utf-8")
        layout.references("ieee80211-2024").write_text("", encoding="utf-8")
        layout.index.write_bytes(b"sqlite placeholder")
        corpus.write_manifest(layout.root, manifest)
        return manifest

    def test_manifest_round_trip_preserves_extraction_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            expected = self.write_complete_corpus(Path(directory))

            actual = corpus.load_manifest(Path(directory))

        self.assertEqual(expected, actual)
        self.assertEqual("1", actual.extractor.version)

    def test_unsupported_manifest_format_is_rejected_with_rebuild_instruction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "corpus.json").write_text(
                '{"format": "inet-standards-corpus", "format_version": 999}\n',
                encoding="utf-8",
            )

            with self.assertRaisesRegex(corpus.IncompatibleCorpusError, "rebuild"):
                corpus.load_manifest(root)

    def test_incomplete_stage_does_not_replace_existing_corpus(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "processed"
            target.mkdir()
            (target / "active-marker").write_text("active\n", encoding="utf-8")

            with corpus.CorpusBuildTransaction(target) as transaction:
                corpus.write_manifest(transaction.layout.root, self.manifest())
                with self.assertRaises(corpus.IncompleteCorpusError):
                    transaction.commit()

            self.assertEqual(
                "active\n", (target / "active-marker").read_text(encoding="utf-8")
            )

    def test_reference_artifact_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            self.write_complete_corpus(Path(directory))
            layout = corpus.CorpusLayout(Path(directory))
            layout.references("ieee80211-2024").unlink()

            with self.assertRaisesRegex(
                corpus.IncompleteCorpusError, "references.jsonl"
            ):
                corpus.validate_complete_corpus(Path(directory))

    def test_commit_replaces_the_whole_generated_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "processed"
            target.mkdir()
            (target / "active-marker").write_text("active\n", encoding="utf-8")

            with corpus.CorpusBuildTransaction(target) as transaction:
                self.write_complete_corpus(transaction.layout.root)
                published = transaction.commit()

            self.assertEqual(target, published.root)
            self.assertFalse((target / "active-marker").exists())
            self.assertTrue(published.manifest.is_file())
            self.assertTrue(published.nodes("ieee80211-2024").is_file())
            self.assertTrue(published.references("ieee80211-2024").is_file())

    def test_publish_failure_restores_the_active_corpus(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "processed"
            target.mkdir()
            (target / "active-marker").write_text("active\n", encoding="utf-8")
            real_replace = corpus.os.replace
            replace_count = 0

            def fail_publishing_staging(source, destination):
                nonlocal replace_count
                replace_count += 1
                if replace_count == 2:
                    raise OSError("simulated publication failure")
                return real_replace(source, destination)

            with corpus.CorpusBuildTransaction(target) as transaction:
                self.write_complete_corpus(transaction.layout.root)
                with mock.patch.object(
                    corpus.os, "replace", side_effect=fail_publishing_staging
                ):
                    with self.assertRaisesRegex(OSError, "simulated publication failure"):
                        transaction.commit()

            self.assertEqual(
                "active\n", (target / "active-marker").read_text(encoding="utf-8")
            )

    def test_aborted_transaction_leaves_the_active_corpus_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "processed"
            target.mkdir()
            (target / "active-marker").write_text("active\n", encoding="utf-8")

            with corpus.CorpusBuildTransaction(target) as transaction:
                staging = transaction.layout.root
                (staging / "partial").write_text("partial\n", encoding="utf-8")

            self.assertEqual(
                "active\n", (target / "active-marker").read_text(encoding="utf-8")
            )
            self.assertFalse(staging.exists())


if __name__ == "__main__":
    unittest.main()
