import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

try:
    from . import main
except ImportError:
    import main


class StandardsMainTest(unittest.TestCase):
    def test_command_surface(self):
        parser = main.create_parser()
        choices = next(
            action.choices
            for action in parser._actions
            if getattr(action, "choices", None)
        )
        self.assertEqual(
            {
                "build",
                "status",
                "lint",
                "get",
                "search",
                "refs",
                "referenced-by",
                "define",
            },
            set(choices),
        )

    def test_get_exact_clause_dispatches_document_and_options(self):
        item = {
            "node_id": "ieee80211-2024:clause:10.25.2",
            "page_start": 1,
            "page_end": 1,
            "title": "Block Ack",
            "source_spans": [],
            "text": "body",
        }
        with mock.patch.object(main.processor, "get", return_value=item) as get:
            with redirect_stdout(io.StringIO()):
                result = main.main(
                    [
                        "get",
                        "clause",
                        "10.25.2",
                        "--document",
                        "ieee80211-2024",
                        "--children",
                        "--json",
                    ]
                )
        self.assertEqual(0, result)
        get.assert_called_once_with(
            output_dir=main.Path("standards/processed"),
            document_id="ieee80211-2024",
            include_children=True,
            include_ancestors=False,
            context_characters=0,
            kind="clause",
            label="10.25.2",
        )

    def test_get_reports_invalid_node_identifier(self):
        with mock.patch.object(
            main.processor, "get", side_effect=ValueError("node_id is not canonical")
        ):
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                result = main.main(["get", "invalid-node-id"])
        self.assertEqual(1, result)
        self.assertIn("node_id is not canonical", stderr.getvalue())

    def test_refs_dispatches_the_exact_node_selector(self):
        result_value = {
            "node": {"node_id": "ieee80211-2024:clause:10.25.2"},
            "direction": "outgoing",
            "total": 0,
            "limit": 20,
            "references": [],
        }
        with mock.patch.object(
            main.processor, "refs", return_value=result_value
        ) as refs:
            with redirect_stdout(io.StringIO()):
                result = main.main(
                    [
                        "refs",
                        "clause",
                        "10.25.2",
                        "--document",
                        "ieee80211-2024",
                        "--limit",
                        "20",
                        "--json",
                    ]
                )
        self.assertEqual(0, result)
        refs.assert_called_once_with(
            output_dir=main.Path("standards/processed"),
            document_id="ieee80211-2024",
            limit=20,
            kind="clause",
            label="10.25.2",
        )

    def test_define_dispatches_term_and_document(self):
        item = {
            "node_id": "ieee80211-2024:definition:access%20point",
            "page_start": 1,
            "page_end": 1,
            "title": "access point",
            "source_spans": [],
            "text": "access point: definition",
        }
        with mock.patch.object(main.processor, "define", return_value=item) as define:
            with redirect_stdout(io.StringIO()):
                result = main.main(
                    [
                        "define",
                        "access point",
                        "--document",
                        "ieee80211-2024",
                        "--json",
                    ]
                )
        self.assertEqual(0, result)
        define.assert_called_once_with(
            output_dir=main.Path("standards/processed"),
            term="access point",
            document_id="ieee80211-2024",
        )


if __name__ == "__main__":
    unittest.main()
