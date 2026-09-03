"""Extraction, publication, and query facade for the standards corpus."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    from . import corpus
    from . import index as structural_index
    from .model import DocumentKind, StandardDocument
    from .semantics import analyze_semantics
    from .structure import StructureAnalysis, analyze_structure
except ImportError:
    import corpus
    import index as structural_index
    from model import DocumentKind, StandardDocument
    from semantics import analyze_semantics
    from structure import StructureAnalysis, analyze_structure


DEFAULT_STANDARDS_DIR = Path("standards")
DEFAULT_OUTPUT_DIR = DEFAULT_STANDARDS_DIR / "processed"
EXTRACTOR_IMPLEMENTATION = "poppler-pdftotext"
EXTRACTOR_VERSION = "1"
PDFTOTEXT_ARGS = ("-layout",)
LICENSE_FOOTER_RE = re.compile(
    r"^\s*Authorized licensed use limited to: .* Downloaded on .* "
    r"IEEE Xplore\. Restrictions apply\.\s*$"
)


@dataclass(frozen=True)
class DocumentProfile:
    document_id: str
    title: str
    revision: str
    kind: DocumentKind
    amends: tuple[str, ...] = ()


# Reviewed identity contracts. Supporting PDFs are deliberately not auto-ingested
# by the IEEE 802.11 structural recognizer.
DOCUMENT_PROFILES = {
    "80211ax-2024.pdf": DocumentProfile(
        document_id="ieee80211-2024",
        title="IEEE Std 802.11-2024",
        revision="2024",
        kind=DocumentKind.BASE_STANDARD,
    ),
    "80211be-2024.pdf": DocumentProfile(
        document_id="ieee80211be-2024",
        title="IEEE Std 802.11be-2024",
        revision="2024",
        kind=DocumentKind.AMENDMENT,
        amends=("ieee80211-2024",),
    ),
}


def discover_pdfs(standards_dir: Path) -> list[Path]:
    root = Path(standards_dir)
    return [root / name for name in DOCUMENT_PROFILES if (root / name).is_file()]


def profile_for_pdf(path: Path) -> DocumentProfile:
    try:
        return DOCUMENT_PROFILES[Path(path).name]
    except KeyError as error:
        supported = ", ".join(DOCUMENT_PROFILES)
        raise ValueError(
            f"no reviewed document profile for {Path(path).name}; supported PDFs: {supported}"
        ) from error


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_command(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def command_text(args: list[str]) -> str:
    completed = run_command(args)
    return (completed.stdout + completed.stderr).decode(
        "utf-8", errors="replace"
    ).strip()


def tool_version(name: str) -> str:
    try:
        return command_text([name, "-v"]).splitlines()[0]
    except Exception as error:
        return f"unavailable: {error}"


def pdfinfo(path: Path) -> dict[str, str]:
    values = {}
    for line in command_text(["pdfinfo", str(path)]).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def parse_page_spec(page_spec: str | None) -> tuple[int, ...] | None:
    if page_spec is None:
        return None
    pages: list[int] = []
    for component in page_spec.split(","):
        component = component.strip()
        if not component:
            raise ValueError("page specification contains an empty component")
        if "-" in component:
            start_text, end_text = component.split("-", 1)
            start, end = int(start_text), int(end_text)
            if start <= 0 or end < start:
                raise ValueError(f"invalid page range: {component}")
            pages.extend(range(start, end + 1))
        else:
            page = int(component)
            if page <= 0:
                raise ValueError(f"invalid page number: {component}")
            pages.append(page)
    return tuple(sorted(set(pages)))


def contiguous_ranges(values: tuple[int, ...]) -> list[tuple[int, int]]:
    if not values:
        return []
    ranges = []
    start = previous = values[0]
    for value in values[1:]:
        if value == previous + 1:
            previous = value
            continue
        ranges.append((start, previous))
        start = previous = value
    ranges.append((start, previous))
    return ranges


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def is_license_footer_line(line: str) -> bool:
    stripped = line.strip()
    return bool(
        LICENSE_FOOTER_RE.match(stripped)
        or "Authorized licensed use limited to:" in stripped
        or "IEEE Xplore. Restrictions apply." in stripped
        or "Downloaded onrights reserved." in stripped
        or re.search(r"©\s+\d{4}\s+IEEE\. All", stripped)
        or re.search(r"Downloaded on .* IEEE Xplore", stripped)
        or stripped == "Copyright"
    )


def clean_page_text(text: str) -> str:
    lines = [
        line.rstrip()
        for line in normalize_text(text).splitlines()
        if not is_license_footer_line(line)
    ]
    return "\n".join(lines).strip()


def split_pages(text: str) -> list[str]:
    pages = normalize_text(text).split("\f")
    if pages and pages[-1] == "":
        pages.pop()
    return pages


def extract_pdf_pages(
    pdf_path: Path, pages: tuple[int, ...] | None, pdf_page_count: int
) -> list[tuple[int, str]]:
    page_numbers = pages or tuple(range(1, pdf_page_count + 1))
    if page_numbers and page_numbers[-1] > pdf_page_count:
        raise ValueError(
            f"requested PDF page {page_numbers[-1]} exceeds {pdf_page_count} pages"
        )
    extracted: list[tuple[int, str]] = []
    for start, end in contiguous_ranges(page_numbers):
        completed = run_command(
            [
                "pdftotext",
                *PDFTOTEXT_ARGS,
                "-f",
                str(start),
                "-l",
                str(end),
                str(pdf_path),
                "-",
            ]
        )
        segment_pages = split_pages(
            completed.stdout.decode("utf-8", errors="replace")
        )
        expected_numbers = list(range(start, end + 1))
        if len(segment_pages) != len(expected_numbers):
            raise RuntimeError(
                f"{pdf_path.name}: extracted {len(segment_pages)} pages for PDF range "
                f"{start}-{end}, expected {len(expected_numbers)}"
            )
        extracted.extend(
            (number, clean_page_text(text))
            for number, text in zip(expected_numbers, segment_pages)
        )
    return extracted


def extraction_record() -> corpus.ExtractionRecord:
    return corpus.ExtractionRecord(
        implementation=EXTRACTOR_IMPLEMENTATION,
        version=EXTRACTOR_VERSION,
        arguments=PDFTOTEXT_ARGS,
        tool_versions=(
            ("pdftotext", tool_version("pdftotext")),
            ("pdfinfo", tool_version("pdfinfo")),
            ("sqlite", sqlite3.sqlite_version),
        ),
    )


def expected_document(
    pdf_path: Path, requested_pages: tuple[int, ...] | None
) -> StandardDocument:
    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"missing standards PDF: {path}")
    profile = profile_for_pdf(path)
    information = pdfinfo(path)
    page_count = int(information.get("Pages", "0"))
    if page_count <= 0:
        raise RuntimeError(f"pdfinfo did not report a positive page count for {path}")
    if requested_pages and requested_pages[-1] > page_count:
        raise ValueError(
            f"requested PDF page {requested_pages[-1]} exceeds {path.name}'s {page_count} pages"
        )
    return StandardDocument(
        document_id=profile.document_id,
        title=information.get("Title") or profile.title,
        revision=profile.revision,
        kind=profile.kind,
        source_path=str(path.resolve()),
        source_sha256=sha256_file(path),
        pdf_page_count=page_count,
        amends=profile.amends,
        extracted_pdf_pages=requested_pages,
    )


def _pdf_paths(standards_dir: Path, pdfs: list[str] | None) -> list[Path]:
    paths = [Path(pdf) for pdf in pdfs] if pdfs else discover_pdfs(standards_dir)
    if not paths:
        raise RuntimeError(f"no reviewed standards PDFs found in {standards_dir}")
    for path in paths:
        profile_for_pdf(path)
    document_ids = [profile_for_pdf(path).document_id for path in paths]
    if len(document_ids) != len(set(document_ids)):
        raise ValueError("the PDF selection contains duplicate document identities")
    return paths


def _write_jsonl(path: Path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")


def _write_analysis(
    layout: corpus.CorpusLayout,
    analysis: StructureAnalysis,
    pages: list[tuple[int, str]],
    references,
) -> None:
    document_id = analysis.document.document_id
    layout.text(document_id).parent.mkdir(parents=True, exist_ok=True)
    layout.text(document_id).write_text(analysis.text, encoding="utf-8")
    layout.pages(document_id).mkdir(parents=True, exist_ok=True)
    for page_number, page_text in pages:
        layout.page(document_id, page_number).write_text(page_text, encoding="utf-8")
    _write_jsonl(layout.nodes(document_id), analysis.nodes)
    _write_jsonl(layout.occurrences(document_id), analysis.occurrences)
    _write_jsonl(layout.diagnostics(document_id), analysis.diagnostics)
    _write_jsonl(layout.references(document_id), references)


def _is_fresh(
    output_dir: Path,
    expected_documents: tuple[StandardDocument, ...],
    extractor: corpus.ExtractionRecord,
) -> bool:
    try:
        manifest = corpus.validate_complete_corpus(output_dir)
    except (corpus.CorpusError, ValueError, OSError):
        return False
    return manifest.documents == expected_documents and manifest.extractor == extractor


def build(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    standards_dir: Path = DEFAULT_STANDARDS_DIR,
    pdfs: list[str] | None = None,
    page_spec: str | None = None,
    force: bool = False,
) -> dict:
    paths = _pdf_paths(Path(standards_dir), pdfs)
    requested_pages = parse_page_spec(page_spec)
    if requested_pages is not None and len(paths) != 1:
        raise ValueError("--pages requires exactly one selected PDF")
    documents = tuple(expected_document(path, requested_pages) for path in paths)
    extractor = extraction_record()
    if not force and _is_fresh(Path(output_dir), documents, extractor):
        return {
            "status": "fresh",
            "output_dir": str(output_dir),
            "documents": [document.to_dict() for document in documents],
        }

    analyses: dict[str, StructureAnalysis] = {}
    pages_by_document: dict[str, list[tuple[int, str]]] = {}
    with corpus.CorpusBuildTransaction(Path(output_dir)) as transaction:
        for path, document in zip(paths, documents):
            pages = extract_pdf_pages(
                path, document.extracted_pdf_pages, document.pdf_page_count
            )
            analyses[document.document_id] = analyze_structure(document, pages)
            pages_by_document[document.document_id] = pages
        analyses, references_by_document = analyze_semantics(analyses)
        for document in documents:
            _write_analysis(
                transaction.layout,
                analyses[document.document_id],
                pages_by_document[document.document_id],
                references_by_document[document.document_id],
            )
        manifest = corpus.CorpusManifest(
            generated_at=datetime.now(timezone.utc).isoformat(),
            extractor=extractor,
            documents=documents,
        )
        corpus.write_manifest(transaction.layout.root, manifest)
        structural_index.build_index(
            transaction.layout, manifest, analyses, references_by_document
        )
        published = transaction.commit()

    return {
        "status": "built",
        "output_dir": str(published.root),
        "documents": [
            {
                **document.to_dict(),
                "node_count": len(analyses[document.document_id].nodes),
                "occurrence_count": len(analyses[document.document_id].occurrences),
                "diagnostic_count": len(analyses[document.document_id].diagnostics),
                "reference_count": len(references_by_document[document.document_id]),
            }
            for document in documents
        ],
    }


def search(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    query: str | None = None,
    limit: int = 10,
    document_id: str | None = None,
    kind: str | None = None,
) -> list[dict]:
    if not query:
        raise ValueError("missing search query")
    return structural_index.search(
        Path(output_dir), query, limit=limit, document_id=document_id, kind=kind
    )


def get(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    kind: str | None = None,
    label: str | None = None,
    document_id: str | None = None,
    node_id: str | None = None,
    source_span: str | None = None,
    include_children: bool = False,
    include_ancestors: bool = False,
    context_characters: int = 0,
) -> dict:
    if source_span is not None:
        return structural_index.get_source_span(
            Path(output_dir), source_span, context_characters=context_characters
        )
    return structural_index.get_node(
        Path(output_dir),
        kind=kind,
        label=label,
        document_id=document_id,
        node_id=node_id,
        include_children=include_children,
        include_ancestors=include_ancestors,
        context_characters=context_characters,
    )


def lint(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    document_id: str | None = None,
    minimum_severity: str = "warning",
    limit: int = 100,
) -> dict:
    return structural_index.lint(
        Path(output_dir),
        document_id=document_id,
        minimum_severity=minimum_severity,
        limit=limit,
    )


def refs(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    kind: str | None = None,
    label: str | None = None,
    document_id: str | None = None,
    node_id: str | None = None,
    limit: int = 100,
) -> dict:
    return structural_index.references(
        Path(output_dir),
        kind=kind,
        label=label,
        document_id=document_id,
        node_id=node_id,
        limit=limit,
    )


def referenced_by(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    kind: str | None = None,
    label: str | None = None,
    document_id: str | None = None,
    node_id: str | None = None,
    limit: int = 100,
) -> dict:
    return structural_index.referenced_by(
        Path(output_dir),
        kind=kind,
        label=label,
        document_id=document_id,
        node_id=node_id,
        limit=limit,
    )


def define(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    term: str,
    document_id: str | None = None,
) -> dict:
    return structural_index.define(
        Path(output_dir), term, document_id=document_id
    )


def status(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    standards_dir: Path = DEFAULT_STANDARDS_DIR,
    pdfs: list[str] | None = None,
) -> dict:
    current_extractor = extraction_record()
    paths = [Path(pdf) for pdf in pdfs] if pdfs else discover_pdfs(standards_dir)
    expected = []
    source_errors = []
    for path in paths:
        try:
            expected.append(expected_document(path, None))
        except Exception as error:
            source_errors.append({"source_path": str(path), "error": str(error)})

    manifest = None
    corpus_state = "missing"
    corpus_error = None
    try:
        manifest = corpus.validate_complete_corpus(Path(output_dir))
        corpus_state = "ready"
    except corpus.IncompatibleCorpusError as error:
        corpus_state = "incompatible"
        corpus_error = str(error)
    except corpus.CorpusError as error:
        corpus_error = str(error)

    counts = {}
    if corpus_state == "ready":
        try:
            counts = structural_index.document_counts(Path(output_dir))
        except Exception as error:
            corpus_state = "incompatible"
            corpus_error = str(error)

    recorded = (
        {document.document_id: document for document in manifest.documents}
        if manifest is not None
        else {}
    )
    extractor_state = "missing"
    if manifest is not None:
        extractor_state = (
            "fresh" if manifest.extractor == current_extractor else "stale"
        )
    rows = []
    for document in expected:
        saved = recorded.get(document.document_id)
        if saved is None:
            state = "missing"
        elif saved.source_sha256 != document.source_sha256:
            state = "stale"
        elif extractor_state == "stale":
            state = "stale"
        elif saved.extracted_pdf_pages is not None:
            state = "partial"
        elif corpus_state != "ready":
            state = corpus_state
        else:
            state = "fresh"
        rows.append({**document.to_dict(), "state": state})

    return {
        "output_dir": str(output_dir),
        "corpus_state": corpus_state,
        "corpus_error": corpus_error,
        "format": corpus.CORPUS_FORMAT,
        "format_version": corpus.CORPUS_FORMAT_VERSION,
        "extractor_version": EXTRACTOR_VERSION,
        "extractor_state": extractor_state,
        "tool_versions": dict(current_extractor.tool_versions),
        "manifest": manifest.to_dict() if manifest is not None else None,
        "documents": rows,
        "corpus_documents": counts,
        "source_errors": source_errors,
    }
