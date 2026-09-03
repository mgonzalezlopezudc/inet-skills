"""Conservative definitions and cross-references over canonical structure."""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from dataclasses import dataclass, replace
from typing import Mapping

try:
    from .model import (
        CrossReference,
        NodeKind,
        ReferenceStatus,
        SourceSpan,
        StandardNode,
        normalize_node_label,
    )
    from .structure import (
        DiagnosticSeverity,
        StructureAnalysis,
        StructureDiagnostic,
    )
except ImportError:
    from model import (
        CrossReference,
        NodeKind,
        ReferenceStatus,
        SourceSpan,
        StandardNode,
        normalize_node_label,
    )
    from structure import (
        DiagnosticSeverity,
        StructureAnalysis,
        StructureDiagnostic,
    )


CLAUSE_LABEL_PATTERN = r"\d{1,2}(?:\.\d+){1,8}"
EXPLICIT_CLAUSE_RE = re.compile(
    r"\b(?:Clause|Subclause)[ \t]+"
    r"(?P<label>\d{1,2}(?:\.\d+){0,8})",
    re.IGNORECASE,
)
EXPLICIT_TABLE_RE = re.compile(
    r"\bTable[ \t]+(?P<label>(?:[A-Z]{1,2}|\d+)-\d+[A-Za-z]?)",
    re.IGNORECASE,
)
EXPLICIT_FIGURE_RE = re.compile(
    r"\bFigure[ \t]+(?P<label>(?:[A-Z]{1,2}|\d+)-\d+[A-Za-z]?)",
    re.IGNORECASE,
)
EXPLICIT_ANNEX_RE = re.compile(
    r"\bAnnex[ \t]+(?P<label>[A-Z]{1,2}(?:\.\d+)*)",
    re.IGNORECASE,
)
CUE_REFERENCE_RE = re.compile(
    r"\b(?:see|defined in|described in|specified in|according to|"
    r"procedures? (?:in|of)|rules? (?:in|of))\s+"
    rf"(?P<series>{CLAUSE_LABEL_PATTERN}"
    rf"(?:\s*,\s*(?:and\s+)?{CLAUSE_LABEL_PATTERN})*)",
    re.IGNORECASE,
)
CLAUSE_LABEL_RE = re.compile(CLAUSE_LABEL_PATTERN)
EXTERNAL_BEFORE_RE = re.compile(
    r"(?:IEEE(?:\s+Std)?|ISO(?:/IEC)?|IEC|IETF|RFC)\b[^\n]{0,48}$",
    re.IGNORECASE,
)
EXTERNAL_AFTER_RE = re.compile(
    r"^\s+(?:of|in)\s+(?:IEEE(?:\s+Std)?|ISO(?:/IEC)?|IEC|IETF|RFC)\b",
    re.IGNORECASE,
)
MEASUREMENT_AFTER_RE = re.compile(
    r"^\s*(?:GHz|MHz|kHz|Hz|THz|dB(?:m|i)?|Mb/s|Gb/s|kb/s|ms|"
    r"[\u00b5\u03bc]s|ns|ps|TU|V|mV|A|mA|W|mW|m|cm|mm)\b",
    re.IGNORECASE,
)
DEFINITION_RE = re.compile(
    r"^(?P<leading>[ \t]*)(?P<term>[^\n:][^:]{0,239}?):[ \t]+"
    r"(?P<body>\S.*)$",
    re.DOTALL,
)
NON_TERM_RE = re.compile(
    r"^(?:NOTE(?:\s+\d+)?|IEEE Std|For the purposes|Change the following|"
    r"\d+\.?\s|Copyright|Part 11)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class _PageOffset:
    number: int
    start: int
    end: int


@dataclass(frozen=True)
class _ReferenceCandidate:
    raw_text: str
    target_kind: NodeKind
    target_label: str
    start: int
    end: int
    unsafe_reason: str | None = None


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _page_offsets(analysis: StructureAnalysis) -> tuple[_PageOffset, ...]:
    page_texts = analysis.text.split("\f")
    page_numbers = tuple(analysis.document.page_numbers)
    if len(page_texts) != len(page_numbers):
        raise ValueError(
            f"{analysis.document.document_id}: canonical text/page count mismatch"
        )
    result = []
    offset = 0
    for index, (number, text) in enumerate(zip(page_numbers, page_texts)):
        if index:
            offset += 1
        result.append(_PageOffset(number=number, start=offset, end=offset + len(text)))
        offset += len(text)
    return tuple(result)


def _source_span(
    analysis: StructureAnalysis,
    pages: tuple[_PageOffset, ...],
    start: int,
    end: int,
) -> SourceSpan:
    if not 0 <= start < end <= len(analysis.text):
        raise ValueError("semantic source span is outside canonical text")
    start_page = next((page for page in pages if page.start <= start < page.end), None)
    end_page = next((page for page in pages if page.start <= end - 1 < page.end), None)
    if start_page is None or end_page is None:
        raise ValueError("semantic source span overlaps a page separator")
    return SourceSpan(
        document_id=analysis.document.document_id,
        pdf_page_start=start_page.number,
        pdf_page_end=end_page.number,
        start_offset=start,
        end_offset=end,
        text_sha256=_sha256(analysis.text[start:end]),
    )


def _paragraphs(text: str, start: int, end: int):
    cursor = start
    while cursor < end:
        while cursor < end and text[cursor] in "\r\n":
            cursor += 1
        if cursor >= end:
            break
        match = re.search(r"\n[ \t]*\n", text[cursor:end])
        paragraph_end = end if match is None else cursor + match.start()
        yield cursor, paragraph_end, text[cursor:paragraph_end]
        cursor = end if match is None else cursor + match.end()


def _definition_nodes(
    analysis: StructureAnalysis,
) -> tuple[StructureAnalysis, tuple[StructureDiagnostic, ...]]:
    pages = _page_offsets(analysis)
    definition_parents = tuple(
        node
        for node in analysis.nodes
        if node.kind == NodeKind.CLAUSE
        and node.label.startswith("3.")
        and "definition" in node.title.casefold()
    )
    candidates: list[tuple[str, SourceSpan, str]] = []
    for parent in definition_parents:
        for parent_span in parent.source_spans:
            for start, end, paragraph in _paragraphs(
                analysis.text, parent_span.start_offset, parent_span.end_offset
            ):
                match = DEFINITION_RE.fullmatch(paragraph.rstrip())
                if match is None:
                    continue
                term = " ".join(match.group("term").split())
                if (
                    not term
                    or not term[0].isalpha()
                    or NON_TERM_RE.match(term)
                    or any(character in term for character in ".?!;")
                ):
                    continue
                source_start = start + match.start("term")
                source_end = start + len(paragraph.rstrip())
                span = _source_span(analysis, pages, source_start, source_end)
                candidates.append((normalize_node_label(term), span, parent.node_id))

    by_term: dict[str, list[tuple[str, SourceSpan, str]]] = defaultdict(list)
    for candidate in candidates:
        by_term[candidate[0].casefold()].append(candidate)

    diagnostics = []
    definitions = []
    for duplicate_key, grouped in by_term.items():
        if len(grouped) != 1:
            diagnostics.append(
                StructureDiagnostic(
                    code="ambiguous-definition",
                    severity=DiagnosticSeverity.ERROR,
                    message=(
                        f"definition term {grouped[0][0]!r} has {len(grouped)} "
                        "source entries and was not canonicalized"
                    ),
                    document_id=analysis.document.document_id,
                    span=grouped[0][1],
                )
            )
            continue
        term, span, parent_id = grouped[0]
        definitions.append(
            StandardNode(
                document_id=analysis.document.document_id,
                kind=NodeKind.DEFINITION,
                label=term,
                title=term,
                source_spans=(span,),
                source_sha256=analysis.document.source_sha256,
                confidence=0.98,
                parent_id=parent_id,
            )
        )

    added_children: dict[str, list[str]] = defaultdict(list)
    for definition in definitions:
        added_children[definition.parent_id].append(definition.node_id)
    updated_nodes = []
    for node in analysis.nodes:
        child_ids = added_children.get(node.node_id)
        updated_nodes.append(
            replace(node, child_ids=node.child_ids + tuple(child_ids))
            if child_ids
            else node
        )
    updated_nodes.extend(definitions)
    updated_nodes.sort(
        key=lambda node: (
            node.source_spans[0].start_offset,
            0 if node.kind == NodeKind.CLAUSE else 1,
            node.node_id,
        )
    )
    return (
        replace(
            analysis,
            nodes=tuple(updated_nodes),
            diagnostics=analysis.diagnostics + tuple(diagnostics),
        ),
        tuple(diagnostics),
    )


def _unsafe_reference_reason(text: str, start: int, end: int) -> str | None:
    before = text[max(0, start - 80) : start]
    after = text[end : min(len(text), end + 80)]
    if EXTERNAL_BEFORE_RE.search(before) or EXTERNAL_AFTER_RE.match(after):
        return "reference is qualified by an external standards document"
    if MEASUREMENT_AFTER_RE.match(after):
        return "numeric token is followed by a measurement unit"
    return None


def _reference_candidates(
    analysis: StructureAnalysis, node: StandardNode
) -> tuple[_ReferenceCandidate, ...]:
    candidates = []
    explicit_patterns = (
        (EXPLICIT_CLAUSE_RE, NodeKind.CLAUSE),
        (EXPLICIT_TABLE_RE, NodeKind.TABLE),
        (EXPLICIT_FIGURE_RE, NodeKind.FIGURE),
        (EXPLICIT_ANNEX_RE, NodeKind.CLAUSE),
    )
    for node_span in node.source_spans:
        text = analysis.text[node_span.start_offset : node_span.end_offset]
        for pattern, target_kind in explicit_patterns:
            for match in pattern.finditer(text):
                target_label = normalize_node_label(match.group("label"))
                absolute_start = node_span.start_offset + match.start()
                absolute_end = node_span.start_offset + match.end()
                if (
                    absolute_start == node_span.start_offset
                    and node.kind == target_kind
                    and node.label.casefold() == target_label.casefold()
                ):
                    continue
                candidates.append(
                    _ReferenceCandidate(
                        raw_text=match.group(),
                        target_kind=target_kind,
                        target_label=target_label,
                        start=absolute_start,
                        end=absolute_end,
                        unsafe_reason=_unsafe_reference_reason(
                            analysis.text, absolute_start, absolute_end
                        ),
                    )
                )

        for match in CUE_REFERENCE_RE.finditer(text):
            series = match.group("series")
            series_start = node_span.start_offset + match.start("series")
            for label_match in CLAUSE_LABEL_RE.finditer(series):
                absolute_start = series_start + label_match.start()
                absolute_end = series_start + label_match.end()
                candidates.append(
                    _ReferenceCandidate(
                        raw_text=label_match.group(),
                        target_kind=NodeKind.CLAUSE,
                        target_label=normalize_node_label(label_match.group()),
                        start=absolute_start,
                        end=absolute_end,
                        unsafe_reason=_unsafe_reference_reason(
                            analysis.text, absolute_start, absolute_end
                        ),
                    )
                )

    by_span = {}
    for candidate in sorted(candidates, key=lambda item: (item.start, item.end)):
        by_span.setdefault((candidate.start, candidate.end), candidate)
    return tuple(by_span.values())


def _resolve_reference(
    analysis: StructureAnalysis,
    source_node: StandardNode,
    candidate: _ReferenceCandidate,
    pages: tuple[_PageOffset, ...],
    catalog: Mapping[tuple[str, NodeKind, str], str],
    global_catalog: Mapping[tuple[NodeKind, str], tuple[str, ...]],
) -> CrossReference:
    label_key = candidate.target_label.casefold()
    global_candidates = global_catalog.get((candidate.target_kind, label_key), ())
    common = {
        "source_node_id": source_node.node_id,
        "raw_text": candidate.raw_text,
        "source_span": _source_span(
            analysis, pages, candidate.start, candidate.end
        ),
        "target_kind": candidate.target_kind,
        "target_label": candidate.target_label,
    }
    if candidate.unsafe_reason is not None:
        return CrossReference(
            **common,
            status=ReferenceStatus.UNRESOLVED,
            candidate_target_ids=global_candidates,
            reason=candidate.unsafe_reason,
        )

    local = catalog.get(
        (analysis.document.document_id, candidate.target_kind, label_key)
    )
    if local is not None:
        return CrossReference(
            **common,
            status=ReferenceStatus.RESOLVED,
            target_node_id=local,
        )

    amended_targets = tuple(
        target
        for document_id in analysis.document.amends
        if (
            target := catalog.get(
                (document_id, candidate.target_kind, label_key)
            )
        )
        is not None
    )
    if len(amended_targets) == 1:
        return CrossReference(
            **common,
            status=ReferenceStatus.RESOLVED,
            target_node_id=amended_targets[0],
        )
    if len(amended_targets) > 1:
        return CrossReference(
            **common,
            status=ReferenceStatus.AMBIGUOUS,
            candidate_target_ids=amended_targets,
            reason="target occurs in multiple documents declared by amends",
        )
    if len(global_candidates) > 1:
        return CrossReference(
            **common,
            status=ReferenceStatus.AMBIGUOUS,
            candidate_target_ids=global_candidates,
            reason="target occurs in multiple documents outside the resolution scope",
        )
    return CrossReference(
        **common,
        status=ReferenceStatus.UNRESOLVED,
        candidate_target_ids=global_candidates,
        reason=(
            "target exists outside the source or declared amended documents"
            if global_candidates
            else "no canonical target with this kind and label"
        ),
    )


def analyze_semantics(
    analyses: Mapping[str, StructureAnalysis],
) -> tuple[dict[str, StructureAnalysis], dict[str, tuple[CrossReference, ...]]]:
    """Add definitions, resolve conservative references, and emit lint findings."""

    augmented = {}
    for document_id, analysis in analyses.items():
        augmented[document_id], _ = _definition_nodes(analysis)

    catalog = {}
    global_targets: dict[tuple[NodeKind, str], list[str]] = defaultdict(list)
    for analysis in augmented.values():
        for node in analysis.nodes:
            key = (node.document_id, node.kind, node.label.casefold())
            if key in catalog:
                raise ValueError(f"duplicate canonical node after semantics: {node.node_id}")
            catalog[key] = node.node_id
            if node.kind != NodeKind.DEFINITION:
                global_targets[(node.kind, node.label.casefold())].append(node.node_id)
    global_catalog = {
        key: tuple(sorted(node_ids)) for key, node_ids in global_targets.items()
    }

    references_by_document = {}
    for document_id, analysis in augmented.items():
        pages = _page_offsets(analysis)
        references = []
        diagnostics = list(analysis.diagnostics)
        for node in analysis.nodes:
            if node.kind == NodeKind.DEFINITION:
                continue
            for candidate in _reference_candidates(analysis, node):
                reference = _resolve_reference(
                    analysis,
                    node,
                    candidate,
                    pages,
                    catalog,
                    global_catalog,
                )
                references.append(reference)
                if reference.status != ReferenceStatus.RESOLVED:
                    diagnostics.append(
                        StructureDiagnostic(
                            code=f"{reference.status.value}-reference",
                            severity=(
                                DiagnosticSeverity.ERROR
                                if reference.status == ReferenceStatus.AMBIGUOUS
                                else DiagnosticSeverity.WARNING
                            ),
                            message=(
                                f"{reference.raw_text!r} from {reference.source_node_id} "
                                f"was not resolved: {reference.reason}"
                            ),
                            document_id=document_id,
                            node_id=reference.source_node_id,
                            span=reference.source_span,
                        )
                    )
        references.sort(
            key=lambda reference: (
                reference.source_span.start_offset,
                reference.source_span.end_offset,
            )
        )
        augmented[document_id] = replace(
            analysis,
            diagnostics=tuple(diagnostics),
        )
        references_by_document[document_id] = tuple(references)
    return augmented, references_by_document
