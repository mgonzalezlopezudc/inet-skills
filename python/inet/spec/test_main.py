from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import main as spec_main


FIXTURE_ROOT = Path(__file__).with_name("fixtures") / "example"
FEATURE_PATH = FIXTURE_ROOT / "feature.yaml"
CORPUS_ROOT = FIXTURE_ROOT / "corpus"
PROJECT_ROOT = FIXTURE_ROOT / "project"


class SpecMainTest(unittest.TestCase):
    def run_main(self, *arguments):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = spec_main.main(list(arguments))
        return code, stdout.getvalue(), stderr.getvalue()

    def external_arguments(self):
        return (
            "--feature",
            str(FEATURE_PATH),
            "--corpus",
            str(CORPUS_ROOT),
            "--inet-root",
            str(PROJECT_ROOT),
        )

    def test_validate_json(self):
        code, stdout, stderr = self.run_main("validate", *self.external_arguments(), "--json")
        self.assertEqual(0, code, stderr)
        payload = json.loads(stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual([], payload["warnings"])

    def test_trace_json(self):
        code, stdout, stderr = self.run_main(
            "trace",
            "sender-offers-ready-session",
            *self.external_arguments(),
            "--json",
        )
        self.assertEqual(0, code, stderr)
        payload = json.loads(stdout)
        self.assertEqual("sender-offers-ready-session", payload["trace"]["id"])
        self.assertIn("send-offer", payload["trace"]["references"])

    def test_trace_unknown_id_fails(self):
        code, stdout, stderr = self.run_main(
            "trace", "missing-id", *self.external_arguments()
        )
        self.assertEqual(1, code)
        self.assertEqual("", stdout)
        self.assertIn("unknown feature semantic id", stderr)

    def test_directory_resolves_feature_yaml(self):
        code, stdout, stderr = self.run_main(
            "validate",
            "--feature",
            str(FIXTURE_ROOT),
            "--corpus",
            str(CORPUS_ROOT),
            "--inet-root",
            str(PROJECT_ROOT),
        )
        self.assertEqual(0, code, stderr)
        self.assertIn("valid:", stdout)


if __name__ == "__main__":
    unittest.main()
