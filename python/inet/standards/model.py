"""Canonical identities and structural records for a standards corpus."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from urllib.parse import quote, unquote


DOCUMENT_ID_RE = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CONTROL_CHARACTER_RE = re.compile(r"[\x00-\x1f\x7f]")


class ModelValidationError(ValueError):
    """Raised when a structural record violates the corpus contract."""


class DocumentKind(str, Enum):
    BASE_STANDARD = "base-standard"
    AMENDMENT = "amendment"
    CORRIGENDUM = "corrigendum"
    SUPPORTING_DOCUMENT = "supporting-document"


class NodeKind(str, Enum):
    CLAUSE = "clause"
    TABLE = "table"
    FIGURE = "figure"
    DEFINITION = "definition"


class OccurrenceClassification(str, Enum):
    CANONICAL = "canonical"
    INDEX_ENTRY = "index-entry"
    CONTINUATION = "continuation"
    REJECTED = "rejected"
    AMBIGUOUS = "ambiguous"


class ReferenceStatus(str, Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    AMBIGUOUS = "ambiguous"


def require_text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ModelValidationError(f"{field} must be a non-empty string")
    if CONTROL_CHARACTER_RE.search(value):
        raise ModelValidationError(f"{field} must not contain control characters")
    return value.strip()


def validate_document_id(document_id: str) -> str:
    document_id = require_text(document_id, "document_id")
    if not DOCUMENT_ID_RE.fullmatch(document_id):
        raise ModelValidationError(
            "document_id must contain lowercase alphanumeric segments separated by '.' or '-'"
        )
    return document_id


def validate_sha256(value: str, field: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise ModelValidationError(f"{field} must be a lowercase SHA-256 hex digest")
    return value


def validate_confidence(value: float) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not 0 <= value <= 1
    ):
        raise ModelValidationError("confidence must be between 0 and 1")
    return value


def is_integer(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def normalize_node_label(label: str) -> str:
    label = require_text(label, "label")
    label = label.replace("\u2013", "-").replace("\u2014", "-")
    return " ".join(label.split())


def canonical_node_id(document_id: str, kind: NodeKind, label: str) -> str:
    document_id = validate_document_id(document_id)
    if not isinstance(kind, NodeKind):
        raise ModelValidationError("kind must be a NodeKind")
    label = normalize_node_label(label)
    return f"{document_id}:{kind.value}:{quote(label, safe='._-~')}"


def parse_node_id(identifier: str) -> tuple[str, NodeKind, str]:
    identifier = require_text(identifier, "node_id")
    parts = identifier.split(":", 2)
    if len(parts) != 3:
        raise ModelValidationError("node_id must contain document, kind, and label segments")
    document_id = validate_document_id(parts[0])
    try:
        kind = NodeKind(parts[1])
    except ValueError as error:
        raise ModelValidationError(f"unknown node kind in node_id: {parts[1]}") from error
    label = unquote(parts[2])
    if canonical_node_id(document_id, kind, label) != identifier:
        raise ModelValidationError("node_id is not in canonical form")
    return document_id, kind, label


def canonical_reference_id(document_id: str, start_offset: int, end_offset: int) -> str:
    document_id = validate_document_id(document_id)
    if not is_integer(start_offset) or start_offset < 0:
        raise ModelValidationError("reference start_offset must be a non-negative integer")
    if not is_integer(end_offset) or end_offset <= start_offset:
        raise ModelValidationError("reference end_offset must be greater than start_offset")
    return f"{document_id}:reference:{start_offset}-{end_offset}"


def parse_reference_id(identifier: str) -> tuple[str, int, int]:
    identifier = require_text(identifier, "reference_id")
    match = re.fullmatch(
        r"(?P<document>[a-z0-9]+(?:[.-][a-z0-9]+)*):reference:"
        r"(?P<start>\d+)-(?P<end>\d+)",
        identifier,
    )
    if match is None:
        raise ModelValidationError(
            "reference_id must contain document and source-offset segments"
        )
    document_id = validate_document_id(match.group("document"))
    start_offset = int(match.group("start"))
    end_offset = int(match.group("end"))
    if canonical_reference_id(document_id, start_offset, end_offset) != identifier:
        raise ModelValidationError("reference_id is not in canonical form")
    return document_id, start_offset, end_offset


@dataclass(frozen=True)
class StandardDocument:
    document_id: str
    title: str
    revision: str
    kind: DocumentKind
    source_path: str
    source_sha256: str
    pdf_page_count: int
    amends: tuple[str, ...] = ()
    extracted_pdf_pages: tuple[int, ...] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "document_id", validate_document_id(self.document_id))
        object.__setattr__(self, "title", require_text(self.title, "title"))
        object.__setattr__(self, "revision", require_text(self.revision, "revision"))
        if not isinstance(self.kind, DocumentKind):
            raise ModelValidationError("kind must be a DocumentKind")
        object.__setattr__(self, "source_path", require_text(self.source_path, "source_path"))
        object.__setattr__(
            self, "source_sha256", validate_sha256(self.source_sha256, "source_sha256")
        )
        if not is_integer(self.pdf_page_count) or self.pdf_page_count <= 0:
            raise ModelValidationError("pdf_page_count must be a positive integer")

        amends = tuple(validate_document_id(item) for item in self.amends)
        if len(set(amends)) != len(amends):
            raise ModelValidationError("amends must not contain duplicates")
        if self.document_id in amends:
            raise ModelValidationError("a document cannot amend itself")
        if self.kind in {DocumentKind.AMENDMENT, DocumentKind.CORRIGENDUM} and not amends:
            raise ModelValidationError(f"{self.kind.value} documents must identify what they amend")
        if self.kind == DocumentKind.BASE_STANDARD and amends:
            raise ModelValidationError("a base standard must not identify an amended document")
        object.__setattr__(self, "amends", amends)

        if self.extracted_pdf_pages is not None:
            pages = tuple(self.extracted_pdf_pages)
            if not pages:
                raise ModelValidationError("extracted_pdf_pages must be None or a non-empty tuple")
            if any(not is_integer(page) or page <= 0 for page in pages):
                raise ModelValidationError("extracted_pdf_pages must contain positive integers")
            if pages != tuple(sorted(set(pages))):
                raise ModelValidationError("extracted_pdf_pages must be sorted and unique")
            if pages[-1] > self.pdf_page_count:
                raise ModelValidationError("extracted_pdf_pages exceeds pdf_page_count")
            object.__setattr__(self, "extracted_pdf_pages", pages)

    @property
    def page_numbers(self) -> tuple[int, ...] | range:
        if self.extracted_pdf_pages is not None:
            return self.extracted_pdf_pages
        return range(1, self.pdf_page_count + 1)

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "title": self.title,
            "revision": self.revision,
            "kind": self.kind.value,
            "source_path": self.source_path,
            "source_sha256": self.source_sha256,
            "pdf_page_count": self.pdf_page_count,
            "amends": list(self.amends),
            "extracted_pdf_pages": (
                list(self.extracted_pdf_pages)
                if self.extracted_pdf_pages is not None
                else None
            ),
        }

    @classmethod
    def from_dict(cls, value: dict) -> "StandardDocument":
        try:
            return cls(
                document_id=value["document_id"],
                title=value["title"],
                revision=value["revision"],
                kind=DocumentKind(value["kind"]),
                source_path=value["source_path"],
                source_sha256=value["source_sha256"],
                pdf_page_count=value["pdf_page_count"],
                amends=tuple(value.get("amends", ())),
                extracted_pdf_pages=(
                    tuple(value["extracted_pdf_pages"])
                    if value.get("extracted_pdf_pages") is not None
                    else None
                ),
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, ModelValidationError):
                raise
            raise ModelValidationError(f"invalid document record: {error}") from error


@dataclass(frozen=True)
class SourceSpan:
    document_id: str
    pdf_page_start: int
    pdf_page_end: int
    start_offset: int
    end_offset: int
    text_sha256: str
    printed_page_start: str | None = None
    printed_page_end: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "document_id", validate_document_id(self.document_id))
        if not is_integer(self.pdf_page_start) or self.pdf_page_start <= 0:
            raise ModelValidationError("pdf_page_start must be a positive integer")
        if not is_integer(self.pdf_page_end) or self.pdf_page_end < self.pdf_page_start:
            raise ModelValidationError("pdf_page_end must not precede pdf_page_start")
        if not is_integer(self.start_offset) or self.start_offset < 0:
            raise ModelValidationError("start_offset must be a non-negative integer")
        if not is_integer(self.end_offset) or self.end_offset <= self.start_offset:
            raise ModelValidationError("end_offset must be greater than start_offset")
        object.__setattr__(
            self, "text_sha256", validate_sha256(self.text_sha256, "text_sha256")
        )
        if (self.printed_page_start is None) != (self.printed_page_end is None):
            raise ModelValidationError("printed page bounds must be both present or both absent")
        if self.printed_page_start is not None:
            object.__setattr__(
                self,
                "printed_page_start",
                require_text(self.printed_page_start, "printed_page_start"),
            )
            object.__setattr__(
                self,
                "printed_page_end",
                require_text(self.printed_page_end, "printed_page_end"),
            )

    def to_dict(self) -> dict:
        return {
            "document_id": self.document_id,
            "pdf_page_start": self.pdf_page_start,
            "pdf_page_end": self.pdf_page_end,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "text_sha256": self.text_sha256,
            "printed_page_start": self.printed_page_start,
            "printed_page_end": self.printed_page_end,
        }

    @classmethod
    def from_dict(cls, value: dict) -> "SourceSpan":
        try:
            return cls(
                document_id=value["document_id"],
                pdf_page_start=value["pdf_page_start"],
                pdf_page_end=value["pdf_page_end"],
                start_offset=value["start_offset"],
                end_offset=value["end_offset"],
                text_sha256=value["text_sha256"],
                printed_page_start=value.get("printed_page_start"),
                printed_page_end=value.get("printed_page_end"),
            )
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            if isinstance(error, ModelValidationError):
                raise
            raise ModelValidationError(f"invalid source span: {error}") from error


@dataclass(frozen=True)
class CrossReference:
    source_node_id: str
    raw_text: str
    source_span: SourceSpan
    target_kind: NodeKind
    target_label: str
    status: ReferenceStatus
    target_node_id: str | None = None
    candidate_target_ids: tuple[str, ...] = ()
    reason: str | None = None

    def __post_init__(self) -> None:
        source = parse_node_id(self.source_node_id)
        object.__setattr__(self, "raw_text", require_text(self.raw_text, "raw_text"))
        if not isinstance(self.source_span, SourceSpan):
            raise ModelValidationError("source_span must be a SourceSpan")
        if source[0] != self.source_span.document_id:
            raise ModelValidationError(
                "source_node_id and source_span must belong to the same document"
            )
        if not isinstance(self.target_kind, NodeKind):
            raise ModelValidationError("target_kind must be a NodeKind")
        if self.target_kind == NodeKind.DEFINITION:
            raise ModelValidationError("cross-reference targets must be structural nodes")
        object.__setattr__(
            self, "target_label", normalize_node_label(self.target_label)
        )
        if not isinstance(self.status, ReferenceStatus):
            raise ModelValidationError("status must be a ReferenceStatus")
        if self.reason is not None:
            object.__setattr__(self, "reason", require_text(self.reason, "reason"))

        target = None
        if self.target_node_id is not None:
            target = parse_node_id(self.target_node_id)
            if (
                target[1] != self.target_kind
                or target[2].casefold() != self.target_label.casefold()
            ):
                raise ModelValidationError(
                    "target_node_id must match target_kind and target_label"
                )

        candidates = tuple(self.candidate_target_ids)
        if len(set(candidates)) != len(candidates):
            raise ModelValidationError("candidate_target_ids must not contain duplicates")
        for candidate_id in candidates:
            candidate = parse_node_id(candidate_id)
            if (
                candidate[1] != self.target_kind
                or candidate[2].casefold() != self.target_label.casefold()
            ):
                raise ModelValidationError(
                    "candidate targets must match target_kind and target_label"
                )
        object.__setattr__(self, "candidate_target_ids", candidates)

        if self.status == ReferenceStatus.RESOLVED:
            if target is None:
                raise ModelValidationError("resolved references require target_node_id")
            if candidates or self.reason is not None:
                raise ModelValidationError(
                    "resolved references must not retain candidates or a reason"
                )
        else:
            if target is not None:
                raise ModelValidationError(
                    f"{self.status.value} references must not identify a target node"
                )
            if self.reason is None:
                raise ModelValidationError(
                    f"{self.status.value} references require a reason"
                )
            if self.status == ReferenceStatus.AMBIGUOUS and len(candidates) < 2:
                raise ModelValidationError(
                    "ambiguous references require at least two candidate targets"
                )

    @property
    def reference_id(self) -> str:
        return canonical_reference_id(
            self.source_span.document_id,
            self.source_span.start_offset,
            self.source_span.end_offset,
        )

    def to_dict(self) -> dict:
        return {
            "reference_id": self.reference_id,
            "source_node_id": self.source_node_id,
            "raw_text": self.raw_text,
            "source_span": self.source_span.to_dict(),
            "target_kind": self.target_kind.value,
            "target_label": self.target_label,
            "status": self.status.value,
            "target_node_id": self.target_node_id,
            "candidate_target_ids": list(self.candidate_target_ids),
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, value: dict) -> "CrossReference":
        try:
            reference = cls(
                source_node_id=value["source_node_id"],
                raw_text=value["raw_text"],
                source_span=SourceSpan.from_dict(value["source_span"]),
                target_kind=NodeKind(value["target_kind"]),
                target_label=value["target_label"],
                status=ReferenceStatus(value["status"]),
                target_node_id=value.get("target_node_id"),
                candidate_target_ids=tuple(value.get("candidate_target_ids", ())),
                reason=value.get("reason"),
            )
            if value["reference_id"] != reference.reference_id:
                raise ModelValidationError(
                    f"reference_id does not match canonical identity: "
                    f"{reference.reference_id}"
                )
            return reference
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            if isinstance(error, ModelValidationError):
                raise
            raise ModelValidationError(f"invalid cross-reference: {error}") from error


@dataclass(frozen=True)
class HeadingCandidate:
    kind: NodeKind
    label: str
    title: str
    raw_heading: str
    span: SourceSpan
    confidence: float

    def __post_init__(self) -> None:
        if not isinstance(self.kind, NodeKind):
            raise ModelValidationError("kind must be a NodeKind")
        object.__setattr__(self, "label", normalize_node_label(self.label))
        if not isinstance(self.title, str) or CONTROL_CHARACTER_RE.search(self.title):
            raise ModelValidationError("title must be a string without control characters")
        object.__setattr__(self, "title", self.title.strip())
        object.__setattr__(
            self, "raw_heading", require_text(self.raw_heading, "raw_heading")
        )
        if not isinstance(self.span, SourceSpan):
            raise ModelValidationError("span must be a SourceSpan")
        object.__setattr__(self, "confidence", validate_confidence(self.confidence))

    def to_dict(self) -> dict:
        return {
            "kind": self.kind.value,
            "label": self.label,
            "title": self.title,
            "raw_heading": self.raw_heading,
            "span": self.span.to_dict(),
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, value: dict) -> "HeadingCandidate":
        try:
            return cls(
                kind=NodeKind(value["kind"]),
                label=value["label"],
                title=value["title"],
                raw_heading=value["raw_heading"],
                span=SourceSpan.from_dict(value["span"]),
                confidence=value["confidence"],
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, ModelValidationError):
                raise
            raise ModelValidationError(f"invalid heading candidate: {error}") from error


@dataclass(frozen=True)
class SourceOccurrence:
    candidate: HeadingCandidate
    classification: OccurrenceClassification
    node_id: str | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.candidate, HeadingCandidate):
            raise ModelValidationError("candidate must be a HeadingCandidate")
        if not isinstance(self.classification, OccurrenceClassification):
            raise ModelValidationError("classification must be an OccurrenceClassification")
        if self.reason is not None:
            object.__setattr__(self, "reason", require_text(self.reason, "reason"))

        target = None
        if self.node_id is not None:
            target = parse_node_id(self.node_id)
        if self.classification in {
            OccurrenceClassification.CANONICAL,
            OccurrenceClassification.CONTINUATION,
        } and target is None:
            raise ModelValidationError(f"{self.classification.value} occurrences require node_id")
        if self.classification in {
            OccurrenceClassification.REJECTED,
            OccurrenceClassification.AMBIGUOUS,
        }:
            if target is not None:
                raise ModelValidationError(
                    f"{self.classification.value} occurrences must not identify a canonical node"
                )
            if self.reason is None:
                raise ModelValidationError(
                    f"{self.classification.value} occurrences require a reason"
                )
        if (
            target is not None
            and self.classification
            in {OccurrenceClassification.CANONICAL, OccurrenceClassification.CONTINUATION}
            and target[0] != self.candidate.span.document_id
        ):
            raise ModelValidationError(
                f"{self.classification.value} occurrences must target their source document"
            )
        if target is not None and (
            target[1] != self.candidate.kind or target[2] != self.candidate.label
        ):
            raise ModelValidationError(
                "occurrence node_id must match the candidate kind and label"
            )

    def to_dict(self) -> dict:
        return {
            "candidate": self.candidate.to_dict(),
            "classification": self.classification.value,
            "node_id": self.node_id,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, value: dict) -> "SourceOccurrence":
        try:
            return cls(
                candidate=HeadingCandidate.from_dict(value["candidate"]),
                classification=OccurrenceClassification(value["classification"]),
                node_id=value.get("node_id"),
                reason=value.get("reason"),
            )
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            if isinstance(error, ModelValidationError):
                raise
            raise ModelValidationError(f"invalid source occurrence: {error}") from error


@dataclass(frozen=True)
class StandardNode:
    document_id: str
    kind: NodeKind
    label: str
    title: str
    source_spans: tuple[SourceSpan, ...]
    source_sha256: str
    confidence: float
    parent_id: str | None = None
    child_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "document_id", validate_document_id(self.document_id))
        if not isinstance(self.kind, NodeKind):
            raise ModelValidationError("kind must be a NodeKind")
        object.__setattr__(self, "label", normalize_node_label(self.label))
        object.__setattr__(self, "title", require_text(self.title, "title"))
        spans = tuple(self.source_spans)
        if not spans:
            raise ModelValidationError("source_spans must not be empty")
        if any(not isinstance(span, SourceSpan) for span in spans):
            raise ModelValidationError("source_spans must contain SourceSpan values")
        if any(span.document_id != self.document_id for span in spans):
            raise ModelValidationError("source_spans must belong to the node document")
        if len(set(spans)) != len(spans):
            raise ModelValidationError("source_spans must not contain duplicates")
        object.__setattr__(self, "source_spans", spans)
        object.__setattr__(
            self, "source_sha256", validate_sha256(self.source_sha256, "source_sha256")
        )
        object.__setattr__(self, "confidence", validate_confidence(self.confidence))

        if self.parent_id is not None:
            parent = parse_node_id(self.parent_id)
            if parent[0] != self.document_id:
                raise ModelValidationError("parent_id must belong to the node document")
            if self.parent_id == self.node_id:
                raise ModelValidationError("a node cannot be its own parent")

        children = tuple(self.child_ids)
        if len(set(children)) != len(children):
            raise ModelValidationError("child_ids must not contain duplicates")
        for child_id in children:
            child = parse_node_id(child_id)
            if child[0] != self.document_id:
                raise ModelValidationError("child_ids must belong to the node document")
            if child_id == self.node_id:
                raise ModelValidationError("a node cannot be its own child")
        object.__setattr__(self, "child_ids", children)

    @property
    def node_id(self) -> str:
        return canonical_node_id(self.document_id, self.kind, self.label)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "document_id": self.document_id,
            "kind": self.kind.value,
            "label": self.label,
            "title": self.title,
            "source_spans": [span.to_dict() for span in self.source_spans],
            "source_sha256": self.source_sha256,
            "confidence": self.confidence,
            "parent_id": self.parent_id,
            "child_ids": list(self.child_ids),
        }

    @classmethod
    def from_dict(cls, value: dict) -> "StandardNode":
        try:
            node = cls(
                document_id=value["document_id"],
                kind=NodeKind(value["kind"]),
                label=value["label"],
                title=value["title"],
                source_spans=tuple(
                    SourceSpan.from_dict(span) for span in value["source_spans"]
                ),
                source_sha256=value["source_sha256"],
                confidence=value["confidence"],
                parent_id=value.get("parent_id"),
                child_ids=tuple(value.get("child_ids", ())),
            )
            if value["node_id"] != node.node_id:
                raise ModelValidationError(
                    f"node_id does not match canonical identity: {node.node_id}"
                )
            return node
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, ModelValidationError):
                raise
            raise ModelValidationError(f"invalid standard node: {error}") from error
