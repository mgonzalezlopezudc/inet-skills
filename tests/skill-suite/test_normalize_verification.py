from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".agents" / "scripts" / "normalize_verification.py"
SPEC = importlib.util.spec_from_file_location("normalize_verification", SCRIPT)
assert SPEC and SPEC.loader
NORMALIZER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NORMALIZER)
FIXTURES = ROOT / "tests" / "skill-suite" / "fixtures" / "verification"
SCHEMA = json.loads(
    (ROOT / ".agents" / "schemas" / "verification-result-v1.schema.json").read_text()
)


class VerificationNormalizerTest(unittest.TestCase):
    def normalize(self, fixture: str, runner: str, exit_code: int) -> dict:
        result = NORMALIZER.normalize(
            text=(FIXTURES / fixture).read_text(),
            runner=runner,
            command=f"run {runner}",
            working_directory="/work/inet",
            build_mode="debug",
            selector="Focused.*",
            configuration="Demo" if runner in {"fingerprint", "opp_repl"} else None,
            run=0 if runner in {"fingerprint", "opp_repl"} else None,
            seed=1 if runner in {"fingerprint", "opp_repl"} else None,
            exit_code=exit_code,
            artifacts=["/tmp/run.log"],
            flaky=False,
        )
        jsonschema.validate(result, SCHEMA)
        return result

    def test_unit_pass(self) -> None:
        result = self.normalize("unit-pass.log", "unit", 0)
        self.assertEqual("PASS", result["status"])
        self.assertEqual(2, result["cases_executed"])
        self.assertIsNone(result["first_causal_failure"])

    def test_assertion_failure(self) -> None:
        result = self.normalize("unit-assertion-failure.log", "unit", 1)
        self.assertEqual("FAIL", result["status"])
        self.assertEqual("assertion", result["first_causal_failure"]["kind"])

    def test_module_build_error(self) -> None:
        result = self.normalize("module-build-error.log", "module", 2)
        self.assertEqual("ERROR", result["status"])
        self.assertEqual("build", result["first_causal_failure"]["kind"])

    def test_zero_selection_is_not_run(self) -> None:
        result = self.normalize("zero-selection.log", "unit", 0)
        self.assertEqual("NOT_RUN", result["status"])
        self.assertEqual(0, result["cases_executed"])

    def test_malformed_output_is_inconclusive(self) -> None:
        result = self.normalize("malformed-output.log", "unit", 0)
        self.assertEqual("INCONCLUSIVE", result["status"])
        self.assertIsNone(result["cases_executed"])

    def test_missing_capability_is_explicit_not_run(self) -> None:
        result = NORMALIZER.normalize(
            text="opp_repl: command not found",
            runner="opp_repl",
            command="opp_repl",
            working_directory="/work/inet",
            build_mode="debug",
            selector=None,
            configuration=None,
            run=None,
            seed=None,
            exit_code=127,
            artifacts=[],
            flaky=False,
            not_run_reason="opp_repl executable unavailable",
        )
        jsonschema.validate(result, SCHEMA)
        self.assertEqual("NOT_RUN", result["status"])
        self.assertIsNone(result["cases_executed"])
        self.assertEqual("opp_repl executable unavailable", result["not_run_reason"])

    def test_expected_approved_baseline_change_remains_fact_only(self) -> None:
        result = NORMALIZER.normalize(
            text=(FIXTURES / "fingerprint-expected-change.log").read_text(),
            runner="fingerprint",
            command="update_fingerprint_test_results(...) ",
            working_directory="/work/inet",
            build_mode="debug",
            selector="Demo",
            configuration="Demo",
            run=0,
            seed=1,
            exit_code=0,
            artifacts=["/work/inet/tests/fingerprint/fingerprint.json"],
            flaky=False,
            changed_result_expected=True,
            changed_result_approved=True,
        )
        jsonschema.validate(result, SCHEMA)
        self.assertEqual("INCONCLUSIVE", result["status"])
        self.assertEqual(
            {"observed": True, "expected": True, "approved": True},
            result["changed_result"],
        )

    def test_fingerprint_mismatch(self) -> None:
        result = self.normalize("fingerprint-failure.log", "fingerprint", 1)
        self.assertEqual("FAIL", result["status"])
        self.assertTrue(result["changed_result"]["observed"])

    def test_opp_repl_pass_and_error(self) -> None:
        passed = self.normalize("opp-repl-pass.log", "opp_repl", 0)
        errored = self.normalize("opp-repl-error.log", "opp_repl", 1)
        self.assertEqual(("PASS", 3), (passed["status"], passed["cases_executed"]))
        self.assertEqual(("ERROR", 1), (errored["status"], errored["cases_executed"]))

    def test_opp_repl_single_result_repr(self) -> None:
        passed = self.normalize("opp-repl-single-pass.log", "opp_repl", 0)
        failed = self.normalize("opp-repl-single-fail.log", "opp_repl", 1)
        self.assertEqual(("PASS", 1), (passed["status"], passed["cases_executed"]))
        self.assertEqual(("FAIL", 1), (failed["status"], failed["cases_executed"]))

    def test_nonzero_exit_overrides_single_pass_summary(self) -> None:
        result = self.normalize("opp-repl-single-pass.log", "opp_repl", 1)
        self.assertEqual(("ERROR", 1), (result["status"], result["cases_executed"]))

    def test_nonzero_exit_overrides_aggregate_pass_summary(self) -> None:
        result = self.normalize("opp-repl-pass.log", "opp_repl", 1)
        self.assertEqual(("ERROR", 3), (result["status"], result["cases_executed"]))

    def test_opp_repl_empty_result_is_not_run(self) -> None:
        empty = self.normalize("opp-repl-empty.log", "opp_repl", 0)
        self.assertEqual(("NOT_RUN", 0), (empty["status"], empty["cases_executed"]))

    def test_fingerprint_expected_result_semantics(self) -> None:
        expected = self.normalize("fingerprint-expected-results.log", "fingerprint", 0)
        unexpected = self.normalize("fingerprint-unexpected-pass.log", "fingerprint", 1)
        self.assertEqual(("PASS", 3), (expected["status"], expected["cases_executed"]))
        self.assertEqual(("FAIL", 1), (unexpected["status"], unexpected["cases_executed"]))

    def test_cli_default_schema_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(
                0,
                NORMALIZER.main(
                    [
                        "--runner",
                        "unit",
                        "--input",
                        str(FIXTURES / "unit-pass.log"),
                        "--command",
                        "unit command",
                        "--working-directory",
                        "/work/inet",
                        "--exit-code",
                        "0",
                        "--output",
                        str(Path(directory) / "result.json"),
                    ]
                ),
            )


if __name__ == "__main__":
    unittest.main()
