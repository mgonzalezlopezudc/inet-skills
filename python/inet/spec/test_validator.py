from __future__ import annotations

import copy
import unittest
from pathlib import Path

from validator import load_feature, trace_feature, validate_feature


FIXTURE_ROOT = Path(__file__).with_name("fixtures") / "example"
FEATURE_PATH = FIXTURE_ROOT / "feature.yaml"
CORPUS_ROOT = FIXTURE_ROOT / "corpus"
PROJECT_ROOT = FIXTURE_ROOT / "project"


class FeatureValidatorTest(unittest.TestCase):
    def setUp(self):
        self.feature = load_feature(FEATURE_PATH)

    def validate(self, feature=None, *, external=True):
        arguments = {}
        if external:
            arguments = {"corpus_root": CORPUS_ROOT, "inet_root": PROJECT_ROOT}
        return validate_feature(feature or self.feature, **arguments)

    def test_license_safe_fixture_passes_all_checks(self):
        result = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertEqual([], result.warnings)

    def test_external_checks_can_be_deferred_with_explicit_warnings(self):
        result = self.validate(external=False)
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(2, len(result.warnings))

    def test_authority_must_remain_non_authoritative(self):
        self.feature["authority"]["status"] = "authoritative"
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("non-authoritative", "\n".join(result.errors))

    def test_sequential_numeric_ids_are_rejected(self):
        self.feature["obligations"][0]["id"] = "sample-001"
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("does not match", "\n".join(result.errors))

    def test_duplicate_semantic_ids_are_rejected(self):
        self.feature["conditions"][0]["id"] = "sender"
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("duplicate semantic id", "\n".join(result.errors))

    def test_unknown_cross_reference_is_rejected(self):
        self.feature["obligations"][0]["conditions"] = ["missing-condition"]
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("unknown condition id", "\n".join(result.errors))

    def test_transition_state_must_exist(self):
        self.feature["transitions"][0]["to"] = "missing-state"
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("state is not declared", "\n".join(result.errors))

    def test_mapping_links_are_bidirectional(self):
        self.feature["obligations"][0]["implementation_mappings"] = []
        result = self.validate()
        self.assertFalse(result.valid)
        messages = "\n".join(result.errors)
        self.assertIn("status needs a resolved target", messages)
        self.assertIn("not cited back", messages)

    def test_obligation_link_must_be_cited_by_mapping(self):
        mapping = self.feature["implementation_mappings"][0]
        mapping["obligations"] = ["receiver-accepts-matching-session"]
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("does not cite the obligation back", "\n".join(result.errors))

    def test_mapped_status_needs_resolved_target(self):
        mapping = self.feature["implementation_mappings"][0]
        mapping.clear()
        mapping.update(
            {
                "id": "handshake-implementation",
                "obligations": [
                    "sender-offers-ready-session",
                    "receiver-accepts-matching-session",
                ],
                "resolution": "gap",
                "gap": "No synthetic implementation target.",
            }
        )
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("needs at least one resolved mapping", "\n".join(result.errors))

    def test_verified_status_needs_passing_evidence(self):
        del self.feature["verification_mappings"][0]["evidence"]
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("verified status needs passing evidence", "\n".join(result.errors))

    def test_implemented_status_needs_realizing_mapping(self):
        self.feature["implementation_mappings"][0]["relation"] = "partial"
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("implemented status needs a realizing mapping", "\n".join(result.errors))

    def test_disagreement_requires_disputed_status(self):
        finding = self.feature["reviews"][1]["findings"][0]
        finding["kind"] = "disagreement"
        finding["disposition"] = "disputed"
        finding["obligations"] = ["sender-offers-ready-session"]
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("requires disputed status", "\n".join(result.errors))

    def test_second_pass_must_record_qualifications(self):
        self.feature["reviews"][1]["findings"][0]["kind"] = "confirmation"
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("pass 2 must record", "\n".join(result.errors))

    def test_each_source_must_appear_in_both_review_passes(self):
        self.feature["reviews"][1]["sources"] = ["missing-source"]
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("missing from source-check pass 2", "\n".join(result.errors))

    def test_reviewed_source_hash_is_checked(self):
        self.feature["sources"][0]["reviewed_text_sha256"] = "f" * 64
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("reviewed hash does not match", "\n".join(result.errors))

    def test_source_node_must_resolve(self):
        self.feature["sources"][0]["node_id"] = "example-1:clause:missing"
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("canonical source node is absent", "\n".join(result.errors))

    def test_target_symbol_is_checked(self):
        self.feature["implementation_mappings"][0]["symbol"] = "Missing::symbol"
        result = self.validate()
        self.assertFalse(result.valid)
        self.assertIn("is absent from", "\n".join(result.errors))

    def test_trace_returns_forward_and_reverse_links(self):
        trace = trace_feature(self.feature, "receiver-accepts-matching-session")
        self.assertEqual("obligations", trace["entity_type"])
        self.assertIn("example-clause", trace["references"])
        self.assertIn("receiver-accepts-transition", trace["referenced_by"])

    def test_trace_rejects_unknown_id(self):
        with self.assertRaisesRegex(ValueError, "unknown feature semantic id"):
            trace_feature(self.feature, "missing-obligation")

    def test_validation_does_not_mutate_input(self):
        before = copy.deepcopy(self.feature)
        self.validate()
        self.assertEqual(before, self.feature)


if __name__ == "__main__":
    unittest.main()
