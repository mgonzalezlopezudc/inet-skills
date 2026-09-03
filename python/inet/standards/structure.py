"""Contextual structural analysis for extracted standards pages.

Detection in this module is intentionally permissive.  Every detected candidate is
retained as a source occurrence and then classified using page and document context.
Only canonical occurrences become :class:`StandardNode` values.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

try:
    from .model import (
        HeadingCandidate,
        NodeKind,
        OccurrenceClassification,
        SourceOccurrence,
        SourceSpan,
        StandardDocument,
        StandardNode,
        canonical_node_id,
    )
except ImportError:
    from model import (
        HeadingCandidate,
        NodeKind,
        OccurrenceClassification,
        SourceOccurrence,
        SourceSpan,
        StandardDocument,
        StandardNode,
        canonical_node_id,
    )


TABLE_FIGURE_RE = re.compile(
    r"^(?P<indent>\s*)(?P<kind>Table|Figure)\s+"
    r"(?P<label>(?:[A-Z]{1,2}|\d+)-\d+[A-Za-z]?)"
    r"(?P<separator>[\u2013\u2014-]|\s{2,})(?P<title>.*\S)\s*$"
)
NESTED_CLAUSE_RE = re.compile(
    r"^(?P<indent>\s*)(?P<label>(?:\d{1,2}|[A-Z]{1,2})(?:\.\d+){1,8})"
    r"(?P<separator>\s+)(?P<title>.*\S)\s*$"
)
TOP_LEVEL_CLAUSE_RE = re.compile(
    r"^(?P<indent>\s*)(?P<label>\d{1,2})\."
    r"(?P<separator>\s+)(?P<title>.*\S)\s*$"
)
ANNEX_RE = re.compile(r"^(?P<indent>\s*)Annex\s+(?P<label>[A-Z]{1,2})\s*$")
INDEX_LEADER_RE = re.compile(r"\.{4,}\s*\d+\s*$")
CONTINUED_RE = re.compile(r"\(continued\)\s*$", re.IGNORECASE)
MEASUREMENT_TITLE_RE = re.compile(
    r"^(?:\([^)]*\)\s*)?(?:GHz|MHz|kHz|Hz|THz|dB(?:m|i)?|Mb/s|Gb/s|kb/s|"
    r"ms|[\u00b5\u03bc]s|ns|ps|TU|V|mV|A|mA|W|mW|m|cm|mm)\b",
    re.IGNORECASE,
)
PAGE_HEADER_RE = re.compile(
    r"^(?:IEEE Std |IEEE Standard for |Part 11:|Copyright|Authorized licensed use)",
    re.IGNORECASE,
)
REFERENCE_CONTINUATION_RE = re.compile(
    r"^(?:and|or|to|through|is|are|was|were|has|have|provides?|specifies?|"
    r"using|used|for|from|with|where|when|which|that|of|in|on|as|except)\b"
    r"|^Case [A-Z]\.\s|^[\[(]|^[\u00d7\u00f7=<>]"
)


class PageRegion(str, Enum):
    BODY = "body"
    INDEX = "index"


class DiagnosticSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class StructureDiagnostic:
    code: str
    severity: DiagnosticSeverity
    message: str
    document_id: str
    node_id: str | None = None
    span: SourceSpan | None = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "severity": self.severity.value,
            "message": self.message,
            "document_id": self.document_id,
            "node_id": self.node_id,
            "span": self.span.to_dict() if self.span is not None else None,
        }


@dataclass(frozen=True)
class DetectedHeading:
    candidate: HeadingCandidate
    page_region: PageRegion
    line_number: int
    separator_width: int
    explicit_continuation: bool
    index_evidence: bool


@dataclass(frozen=True)
class StructureAnalysis:
    document: StandardDocument
    text: str
    detected: tuple[DetectedHeading, ...]
    occurrences: tuple[SourceOccurrence, ...]
    nodes: tuple[StandardNode, ...]
    diagnostics: tuple[StructureDiagnostic, ...]

    @property
    def classification_counts(self) -> dict[str, int]:
        counts = Counter(occurrence.classification.value for occurrence in self.occurrences)
        return dict(sorted(counts.items()))


@dataclass(frozen=True)
class _Page:
    number: int
    text: str
    start_offset: int
    end_offset: int
    region: PageRegion


@dataclass(frozen=True)
class _Line:
    page: _Page
    number: int
    text: str
    start_offset: int
    index_evidence: bool


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _index_line(lines: list[str], index: int) -> bool:
    if INDEX_LEADER_RE.search(lines[index]):
        return True
    # Long table and figure titles commonly wrap before the dotted leader.
    return any(
        INDEX_LEADER_RE.search(lines[next_index])
        for next_index in range(index + 1, min(index + 3, len(lines)))
    )


def _page_region(lines: list[str]) -> PageRegion:
    index_lines = sum(bool(INDEX_LEADER_RE.search(line)) for line in lines)
    normalized = {" ".join(line.lower().split()) for line in lines if line.strip()}
    explicit_index_heading = bool(
        normalized.intersection(
            {"contents", "table of contents", "list of tables", "list of figures"}
        )
    )
    if explicit_index_heading or index_lines >= 2:
        return PageRegion.INDEX
    return PageRegion.BODY


def _prepare_pages(
    document: StandardDocument, pages: Iterable[tuple[int, str]]
) -> tuple[str, tuple[_Page, ...], tuple[_Line, ...]]:
    supplied = tuple(pages)
    numbers = tuple(number for number, _ in supplied)
    if not supplied:
        raise ValueError("pages must not be empty")
    if numbers != tuple(sorted(set(numbers))):
        raise ValueError("page numbers must be sorted and unique")
    if any(
        isinstance(number, bool)
        or not isinstance(number, int)
        or number <= 0
        or number > document.pdf_page_count
        for number in numbers
    ):
        raise ValueError("page numbers must be positive and within the document")
    if document.extracted_pdf_pages is not None and numbers != document.extracted_pdf_pages:
        raise ValueError("supplied pages must match document.extracted_pdf_pages")
    if any(not isinstance(text, str) for _, text in supplied):
        raise TypeError("page text must be a string")

    text_parts: list[str] = []
    page_records: list[_Page] = []
    line_records: list[_Line] = []
    offset = 0
    for page_index, (number, page_text) in enumerate(supplied):
        if page_index:
            text_parts.append("\f")
            offset += 1
        start_offset = offset
        text_parts.append(page_text)
        lines = page_text.splitlines(keepends=True)
        plain_lines = [line.rstrip("\r\n") for line in lines]
        page = _Page(
            number=number,
            text=page_text,
            start_offset=start_offset,
            end_offset=start_offset + len(page_text),
            region=_page_region(plain_lines),
        )
        page_records.append(page)
        line_offset = start_offset
        for line_number, line in enumerate(lines, 1):
            plain_line = line.rstrip("\r\n")
            line_records.append(
                _Line(
                    page=page,
                    number=line_number,
                    text=plain_line,
                    start_offset=line_offset,
                    index_evidence=_index_line(plain_lines, line_number - 1),
                )
            )
            line_offset += len(line)
        # splitlines() produces no record for a non-newline empty page, which is fine.
        offset += len(page_text)
    return "".join(text_parts), tuple(page_records), tuple(line_records)


def _clean_title(title: str) -> str:
    title = INDEX_LEADER_RE.sub("", title)
    return " ".join(title.split())


def _annex_title(lines: tuple[_Line, ...], index: int, label: str) -> str:
    page = lines[index].page
    for following in lines[index + 1 : index + 7]:
        if following.page != page:
            break
        text = following.text.strip()
        if not text or re.fullmatch(r"\((?:normative|informative)\)", text, re.IGNORECASE):
            continue
        if PAGE_HEADER_RE.match(text) or NESTED_CLAUSE_RE.match(following.text):
            break
        return _clean_title(text)
    return f"Annex {label}"


def _candidate_from_line(
    document: StandardDocument,
    lines: tuple[_Line, ...],
    index: int,
) -> DetectedHeading | None:
    line = lines[index]
    match = TABLE_FIGURE_RE.match(line.text)
    kind: NodeKind
    label: str
    title: str
    separator: str
    if match:
        kind = NodeKind.TABLE if match.group("kind") == "Table" else NodeKind.FIGURE
        label = match.group("label")
        title = _clean_title(match.group("title"))
        separator = match.group("separator")
    else:
        match = NESTED_CLAUSE_RE.match(line.text)
        if match:
            kind = NodeKind.CLAUSE
            label = match.group("label")
            title = _clean_title(match.group("title"))
            separator = match.group("separator")
        else:
            match = TOP_LEVEL_CLAUSE_RE.match(line.text)
            if match:
                kind = NodeKind.CLAUSE
                label = match.group("label")
                title = _clean_title(match.group("title"))
                separator = match.group("separator")
            else:
                match = ANNEX_RE.match(line.text)
                if not match:
                    return None
                kind = NodeKind.CLAUSE
                label = match.group("label")
                title = _annex_title(lines, index, label)
                separator = " "

    raw_heading = line.text.strip()
    leading = len(line.text) - len(line.text.lstrip())
    trailing = len(line.text.rstrip())
    start_offset = line.start_offset + leading
    end_offset = line.start_offset + trailing
    span = SourceSpan(
        document_id=document.document_id,
        pdf_page_start=line.page.number,
        pdf_page_end=line.page.number,
        start_offset=start_offset,
        end_offset=end_offset,
        text_sha256=_sha256(raw_heading),
    )
    index_evidence = line.page.region == PageRegion.INDEX or line.index_evidence
    separator_width = len(separator) if separator.isspace() else 1
    confidence = 0.9
    if kind == NodeKind.CLAUSE:
        confidence = 0.96 if "." not in label else 0.92
    if index_evidence:
        confidence = min(confidence, 0.65)
    if kind == NodeKind.CLAUSE and MEASUREMENT_TITLE_RE.match(title):
        confidence = 0.05
    elif separator_width > 4:
        confidence = min(confidence, 0.2)
    return DetectedHeading(
        candidate=HeadingCandidate(
            kind=kind,
            label=label,
            title=title,
            raw_heading=raw_heading,
            span=span,
            confidence=confidence,
        ),
        page_region=line.page.region,
        line_number=line.number,
        separator_width=separator_width,
        explicit_continuation=bool(CONTINUED_RE.search(title)),
        index_evidence=index_evidence,
    )


def detect_heading_candidates(
    document: StandardDocument, pages: Iterable[tuple[int, str]]
) -> tuple[DetectedHeading, ...]:
    """Return permissively detected headings with source and page evidence."""

    _, _, lines = _prepare_pages(document, pages)
    return tuple(
        detected
        for index in range(len(lines))
        if (detected := _candidate_from_line(document, lines, index)) is not None
    )


def _local_rejection(detected: DetectedHeading) -> str | None:
    candidate = detected.candidate
    if candidate.kind == NodeKind.CLAUSE and MEASUREMENT_TITLE_RE.match(candidate.title):
        return "numeric label is followed by a measurement unit"
    if detected.separator_width > 4:
        return "wide column gap is characteristic of a table row, not a heading"
    if candidate.kind == NodeKind.CLAUSE and candidate.title[:1].islower():
        return "lowercase text after the numeric label continues a reference or sentence"
    if candidate.kind == NodeKind.CLAUSE and REFERENCE_CONTINUATION_RE.match(
        candidate.title
    ):
        return "text after the numeric label continues a reference or sentence"
    if (
        candidate.kind == NodeKind.CLAUSE
        and "." not in candidate.label
        and detected.line_number > 12
    ):
        return "top-level clause or annex is not positioned as a page heading"
    return None


def _section_span(
    document: StandardDocument,
    text: str,
    pages: tuple[_Page, ...],
    start: int,
    requested_end: int,
) -> SourceSpan:
    start_page_index = next(
        (
            index
            for index, page in enumerate(pages)
            if page.start_offset <= start < page.end_offset
        ),
        None,
    )
    if start_page_index is None:
        raise AssertionError("a canonical heading must overlap an extracted page")
    end = requested_end
    end_page = pages[start_page_index]
    for index in range(start_page_index + 1, len(pages)):
        previous = pages[index - 1]
        page = pages[index]
        if page.start_offset >= requested_end:
            break
        if page.number != previous.number + 1:
            end = min(end, previous.end_offset)
            break
        end_page = page
    end = max(start + 1, end)
    if end <= end_page.start_offset:
        end_page = pages[start_page_index]
    return SourceSpan(
        document_id=document.document_id,
        pdf_page_start=pages[start_page_index].number,
        pdf_page_end=end_page.number,
        start_offset=start,
        end_offset=end,
        text_sha256=_sha256(text[start:end]),
    )


def _parent_label(label: str) -> str | None:
    if "." not in label:
        return None
    return label.rsplit(".", 1)[0]


def analyze_structure(
    document: StandardDocument,
    pages: Iterable[tuple[int, str]],
    *,
    tiny_node_characters: int = 20,
    oversized_node_characters: int = 200_000,
) -> StructureAnalysis:
    """Detect, classify, link, and diagnose structural occurrences in one document."""

    if tiny_node_characters < 0:
        raise ValueError("tiny_node_characters must be non-negative")
    if oversized_node_characters <= tiny_node_characters:
        raise ValueError("oversized_node_characters must exceed tiny_node_characters")

    supplied = tuple(pages)
    text, page_records, lines = _prepare_pages(document, supplied)
    detected = tuple(
        item
        for index in range(len(lines))
        if (item := _candidate_from_line(document, lines, index)) is not None
    )
    grouped: dict[tuple[NodeKind, str], list[int]] = defaultdict(list)
    for index, item in enumerate(detected):
        grouped[(item.candidate.kind, item.candidate.label)].append(index)

    classifications: list[OccurrenceClassification | None] = [None] * len(detected)
    reasons: list[str | None] = [None] * len(detected)
    canonical_indexes: set[int] = set()
    diagnostics: list[StructureDiagnostic] = []

    for (kind, label), indexes in grouped.items():
        if len(indexes) > 1:
            diagnostics.append(
                StructureDiagnostic(
                    code="duplicate-label-candidates",
                    severity=DiagnosticSeverity.INFO,
                    message=f"{kind.value} {label} has {len(indexes)} source occurrences",
                    document_id=document.document_id,
                )
            )
        viable: list[int] = []
        for index in indexes:
            item = detected[index]
            if item.index_evidence:
                classifications[index] = OccurrenceClassification.INDEX_ENTRY
                continue
            rejection = _local_rejection(item)
            if rejection is not None:
                classifications[index] = OccurrenceClassification.REJECTED
                reasons[index] = rejection
                diagnostics.append(
                    StructureDiagnostic(
                        code="false-heading-candidate",
                        severity=DiagnosticSeverity.WARNING,
                        message=f"rejected {kind.value} {label}: {rejection}",
                        document_id=document.document_id,
                        span=item.candidate.span,
                    )
                )
            else:
                viable.append(index)

        non_continued = [index for index in viable if not detected[index].explicit_continuation]
        continued = [index for index in viable if detected[index].explicit_continuation]
        if len(non_continued) == 1:
            canonical = non_continued[0]
            classifications[canonical] = OccurrenceClassification.CANONICAL
            canonical_indexes.add(canonical)
            for index in continued:
                classifications[index] = OccurrenceClassification.CONTINUATION
        elif (
            kind in {NodeKind.TABLE, NodeKind.FIGURE}
            and len(non_continued) > 1
            and all(
                detected[right].candidate.span.pdf_page_start
                == detected[left].candidate.span.pdf_page_start + 1
                for left, right in zip(non_continued, non_continued[1:])
            )
        ):
            canonical = non_continued[0]
            classifications[canonical] = OccurrenceClassification.CANONICAL
            canonical_indexes.add(canonical)
            for index in non_continued[1:] + continued:
                classifications[index] = OccurrenceClassification.CONTINUATION
        elif not non_continued and len(continued) == 1:
            index = continued[0]
            reason = "continuation caption has no canonical body caption in the selected pages"
            classifications[index] = OccurrenceClassification.AMBIGUOUS
            reasons[index] = reason
        elif viable:
            reason = "multiple plausible body headings share the same document, kind, and label"
            for index in viable:
                classifications[index] = OccurrenceClassification.AMBIGUOUS
                reasons[index] = reason

        for index in viable:
            if classifications[index] == OccurrenceClassification.AMBIGUOUS:
                diagnostics.append(
                    StructureDiagnostic(
                        code="unresolved-heading-ambiguity",
                        severity=DiagnosticSeverity.ERROR,
                        message=f"ambiguous {kind.value} {label}: {reasons[index]}",
                        document_id=document.document_id,
                        span=detected[index].candidate.span,
                    )
                )

    # Classification is total by construction; keep an assertion close to that contract.
    if any(classification is None for classification in classifications):
        raise AssertionError("every detected heading must be classified")

    canonical_order = sorted(
        canonical_indexes, key=lambda index: detected[index].candidate.span.start_offset
    )
    node_ids = {
        index: canonical_node_id(
            document.document_id,
            detected[index].candidate.kind,
            detected[index].candidate.label,
        )
        for index in canonical_order
    }
    node_id_by_key = {
        (detected[index].candidate.kind, detected[index].candidate.label): node_ids[index]
        for index in canonical_order
    }

    occurrences: list[SourceOccurrence] = []
    for index, item in enumerate(detected):
        classification = classifications[index]
        key = (item.candidate.kind, item.candidate.label)
        node_id = None
        reason = reasons[index]
        if classification == OccurrenceClassification.CANONICAL:
            node_id = node_ids[index]
        elif classification == OccurrenceClassification.CONTINUATION:
            node_id = node_id_by_key[key]
        elif classification == OccurrenceClassification.INDEX_ENTRY:
            node_id = node_id_by_key.get(key)
            if node_id is None:
                reason = "index entry has no canonical body object in the selected pages"
        occurrences.append(
            SourceOccurrence(
                candidate=item.candidate,
                classification=classification,
                node_id=node_id,
                reason=reason,
            )
        )

    body_boundary_indexes = sorted(
        (
            index
            for index, classification in enumerate(classifications)
            if classification
            in {
                OccurrenceClassification.CANONICAL,
                OccurrenceClassification.CONTINUATION,
                OccurrenceClassification.AMBIGUOUS,
            }
        ),
        key=lambda index: detected[index].candidate.span.start_offset,
    )
    node_spans: dict[str, list[SourceSpan]] = defaultdict(list)
    for boundary_index, index in enumerate(body_boundary_indexes):
        classification = classifications[index]
        if classification not in {
            OccurrenceClassification.CANONICAL,
            OccurrenceClassification.CONTINUATION,
        }:
            continue
        candidate = detected[index].candidate
        requested_end = (
            detected[body_boundary_indexes[boundary_index + 1]].candidate.span.start_offset
            if boundary_index + 1 < len(body_boundary_indexes)
            else len(text)
        )
        requested_end = max(requested_end, candidate.span.end_offset)
        node_id = node_id_by_key[(candidate.kind, candidate.label)]
        node_spans[node_id].append(
            _section_span(
                document,
                text,
                page_records,
                candidate.span.start_offset,
                requested_end,
            )
        )

    provisional: dict[int, dict] = {}
    canonical_clause_by_label = {
        detected[index].candidate.label: (index, node_ids[index])
        for index in canonical_order
        if detected[index].candidate.kind == NodeKind.CLAUSE
    }
    preceding_clause_id: str | None = None
    for index in canonical_order:
        candidate = detected[index].candidate
        start = candidate.span.start_offset
        section_spans = tuple(node_spans[node_ids[index]])

        parent_id: str | None = None
        if candidate.kind == NodeKind.CLAUSE:
            expected_parent = _parent_label(candidate.label)
            if expected_parent is not None:
                parent = canonical_clause_by_label.get(expected_parent)
                if (
                    parent is not None
                    and detected[parent[0]].candidate.span.start_offset < start
                ):
                    parent_id = parent[1]
                else:
                    diagnostics.append(
                        StructureDiagnostic(
                            code="missing-parent",
                            severity=DiagnosticSeverity.WARNING,
                            message=(
                                f"clause {candidate.label} has no canonical parent "
                                f"clause {expected_parent} in this document selection"
                            ),
                            document_id=document.document_id,
                            node_id=node_ids[index],
                            span=candidate.span,
                        )
                    )
            preceding_clause_id = node_ids[index]
        else:
            parent_id = preceding_clause_id

        size = sum(span.end_offset - span.start_offset for span in section_spans)
        if size < tiny_node_characters:
            diagnostics.append(
                StructureDiagnostic(
                    code="tiny-node",
                    severity=DiagnosticSeverity.WARNING,
                    message=f"{node_ids[index]} contains only {size} extracted characters",
                    document_id=document.document_id,
                    node_id=node_ids[index],
                    span=section_spans[0],
                )
            )
        if size > oversized_node_characters:
            diagnostics.append(
                StructureDiagnostic(
                    code="oversized-node",
                    severity=DiagnosticSeverity.WARNING,
                    message=f"{node_ids[index]} contains {size} extracted characters",
                    document_id=document.document_id,
                    node_id=node_ids[index],
                    span=section_spans[0],
                )
            )
        provisional[index] = {
            "candidate": candidate,
            "spans": section_spans,
            "parent_id": parent_id,
        }

    children: dict[str, list[str]] = defaultdict(list)
    for index in canonical_order:
        parent_id = provisional[index]["parent_id"]
        if parent_id is not None:
            children[parent_id].append(node_ids[index])

    nodes = tuple(
        StandardNode(
            document_id=document.document_id,
            kind=provisional[index]["candidate"].kind,
            label=provisional[index]["candidate"].label,
            title=provisional[index]["candidate"].title,
            source_spans=provisional[index]["spans"],
            source_sha256=document.source_sha256,
            confidence=provisional[index]["candidate"].confidence,
            parent_id=provisional[index]["parent_id"],
            child_ids=tuple(children[node_ids[index]]),
        )
        for index in canonical_order
    )
    return StructureAnalysis(
        document=document,
        text=text,
        detected=detected,
        occurrences=tuple(occurrences),
        nodes=nodes,
        diagnostics=tuple(diagnostics),
    )
