import unittest

try:
    from . import model
except ImportError:
    import model


DOCUMENT_HASH = "a" * 64
SPAN_HASH = "b" * 64


class StandardsModelTest(unittest.TestCase):
    def span(self, page=10, start=100, end=140):
        return model.SourceSpan(
            document_id="ieee80211-2024",
            pdf_page_start=page,
            pdf_page_end=page,
            start_offset=start,
            end_offset=end,
            text_sha256=SPAN_HASH,
        )

    def test_document_identity_is_independent_of_source_filename(self):
        document = model.StandardDocument(
            document_id="ieee80211-2024",
            title="IEEE wireless LAN standard",
            revision="2024",
            kind=model.DocumentKind.BASE_STANDARD,
            source_path="standards/misleading-local-name.pdf",
            source_sha256=DOCUMENT_HASH,
            pdf_page_count=5000,
        )

        self.assertEqual("ieee80211-2024", document.document_id)
        self.assertEqual(range(1, 5001), document.page_numbers)

    def test_amendments_identify_the_document_they_amend(self):
        with self.assertRaisesRegex(model.ModelValidationError, "identify what they amend"):
            model.StandardDocument(
                document_id="ieee80211be-2024",
                title="EHT amendment",
                revision="2024",
                kind=model.DocumentKind.AMENDMENT,
                source_path="standards/80211be-2024.pdf",
                source_sha256=DOCUMENT_HASH,
                pdf_page_count=1000,
            )

    def test_partial_page_selection_is_sorted_unique_and_bounded(self):
        document = model.StandardDocument(
            document_id="ieee80211-2024",
            title="IEEE wireless LAN standard",
            revision="2024",
            kind=model.DocumentKind.BASE_STANDARD,
            source_path="standard.pdf",
            source_sha256=DOCUMENT_HASH,
            pdf_page_count=20,
            extracted_pdf_pages=(3, 4, 10),
        )
        self.assertEqual((3, 4, 10), document.page_numbers)

        with self.assertRaisesRegex(model.ModelValidationError, "sorted and unique"):
            model.StandardDocument(
                document_id="ieee80211-2024",
                title="IEEE wireless LAN standard",
                revision="2024",
                kind=model.DocumentKind.BASE_STANDARD,
                source_path="standard.pdf",
                source_sha256=DOCUMENT_HASH,
                pdf_page_count=20,
                extracted_pdf_pages=(4, 3),
            )

    def test_node_identity_does_not_depend_on_title_page_or_sequence(self):
        first = model.StandardNode(
            document_id="ieee80211-2024",
            kind=model.NodeKind.CLAUSE,
            label="10.25.2",
            title="First extracted title",
            source_spans=(self.span(page=100),),
            source_sha256=DOCUMENT_HASH,
            confidence=0.95,
        )
        second = model.StandardNode(
            document_id="ieee80211-2024",
            kind=model.NodeKind.CLAUSE,
            label="10.25.2",
            title="Corrected extracted title",
            source_spans=(self.span(page=200, start=500, end=550),),
            source_sha256=DOCUMENT_HASH,
            confidence=1,
        )

        self.assertEqual("ieee80211-2024:clause:10.25.2", first.node_id)
        self.assertEqual(first.node_id, second.node_id)

    def test_structural_records_round_trip_without_recomputing_identity_from_position(self):
        node = model.StandardNode(
            document_id="ieee80211-2024",
            kind=model.NodeKind.CLAUSE,
            label="10.25.2",
            title="Block Ack parameters",
            source_spans=(self.span(),),
            source_sha256=DOCUMENT_HASH,
            confidence=0.95,
            parent_id="ieee80211-2024:clause:10.25",
        )

        restored = model.StandardNode.from_dict(node.to_dict())

        self.assertEqual(node, restored)
        self.assertEqual("ieee80211-2024:clause:10.25.2", restored.node_id)

        changed = node.to_dict()
        changed["node_id"] = "ieee80211-2024:clause:10.25.3"
        with self.assertRaisesRegex(model.ModelValidationError, "canonical identity"):
            model.StandardNode.from_dict(changed)

    def test_node_id_encodes_non_structural_labels_canonically(self):
        identifier = model.canonical_node_id(
            "ieee80211-2024", model.NodeKind.DEFINITION, "Block   Ack agreement"
        )

        self.assertEqual(
            "ieee80211-2024:definition:Block%20Ack%20agreement", identifier
        )
        self.assertEqual(
            ("ieee80211-2024", model.NodeKind.DEFINITION, "Block Ack agreement"),
            model.parse_node_id(identifier),
        )

    def test_ambiguous_occurrence_requires_reason_and_has_no_node(self):
        candidate = model.HeadingCandidate(
            kind=model.NodeKind.TABLE,
            label="9-45",
            title="Feedback encoding",
            raw_heading="Table 9-45—Feedback encoding",
            span=self.span(),
            confidence=0.5,
        )

        with self.assertRaisesRegex(model.ModelValidationError, "require a reason"):
            model.SourceOccurrence(
                candidate=candidate,
                classification=model.OccurrenceClassification.AMBIGUOUS,
            )

        occurrence = model.SourceOccurrence(
            candidate=candidate,
            classification=model.OccurrenceClassification.AMBIGUOUS,
            reason="both a body caption and an index entry remain plausible",
        )
        self.assertIsNone(occurrence.node_id)
        self.assertEqual(
            occurrence, model.SourceOccurrence.from_dict(occurrence.to_dict())
        )

    def test_canonical_occurrence_requires_same_document_node(self):
        candidate = model.HeadingCandidate(
            kind=model.NodeKind.CLAUSE,
            label="10.25.2",
            title="Block Ack parameters",
            raw_heading="10.25.2 Block Ack parameters",
            span=self.span(),
            confidence=1,
        )

        with self.assertRaisesRegex(model.ModelValidationError, "source document"):
            model.SourceOccurrence(
                candidate=candidate,
                classification=model.OccurrenceClassification.CANONICAL,
                node_id="ieee80211be-2024:clause:10.25.2",
            )

        with self.assertRaisesRegex(model.ModelValidationError, "kind and label"):
            model.SourceOccurrence(
                candidate=candidate,
                classification=model.OccurrenceClassification.CANONICAL,
                node_id="ieee80211-2024:clause:10.25.3",
            )

    def test_cross_reference_round_trip_preserves_resolution_evidence(self):
        reference = model.CrossReference(
            source_node_id="ieee80211-2024:clause:10.25.2",
            raw_text="10.25.3",
            source_span=self.span(start=120, end=127),
            target_kind=model.NodeKind.CLAUSE,
            target_label="10.25.3",
            status=model.ReferenceStatus.RESOLVED,
            target_node_id="ieee80211-2024:clause:10.25.3",
        )

        self.assertEqual(
            "ieee80211-2024:reference:120-127", reference.reference_id
        )
        self.assertEqual(
            reference, model.CrossReference.from_dict(reference.to_dict())
        )

    def test_unresolved_reference_requires_reason_and_ambiguous_candidates(self):
        common = {
            "source_node_id": "ieee80211-2024:clause:10.25.2",
            "raw_text": "10.1",
            "source_span": self.span(start=120, end=124),
            "target_kind": model.NodeKind.CLAUSE,
            "target_label": "10.1",
        }
        with self.assertRaisesRegex(model.ModelValidationError, "require a reason"):
            model.CrossReference(
                **common,
                status=model.ReferenceStatus.UNRESOLVED,
            )
        with self.assertRaisesRegex(
            model.ModelValidationError, "at least two candidate"
        ):
            model.CrossReference(
                **common,
                status=model.ReferenceStatus.AMBIGUOUS,
                candidate_target_ids=("ieee80211-2024:clause:10.1",),
                reason="more than one document may own the target",
            )


if __name__ == "__main__":
    unittest.main()
