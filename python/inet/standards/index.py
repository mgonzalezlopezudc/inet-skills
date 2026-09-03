"""SQLite persistence and query operations for the canonical standards corpus."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path

try:
    from . import corpus
    from .model import CrossReference, NodeKind, StandardNode, parse_node_id
except ImportError:
    import corpus
    from model import CrossReference, NodeKind, StandardNode, parse_node_id


INDEX_SCHEMA_VERSION = 2
SOURCE_SPAN_RE = re.compile(
    r"^(?P<document>[a-z0-9]+(?:[.-][a-z0-9]+)*)@(?P<start>\d+):(?P<end>\d+)$"
)
SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}


class StandardsIndexError(RuntimeError):
    """Raised when a structural index cannot satisfy a query."""


def ensure_fts5_available() -> None:
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE VIRTUAL TABLE fts_probe USING fts5(body)")
    except sqlite3.OperationalError as error:
        raise StandardsIndexError("SQLite was built without FTS5 support") from error
    finally:
        connection.close()


def _node_text(canonical_text: str, node: StandardNode) -> str:
    return "\n\n".join(
        canonical_text[span.start_offset : span.end_offset]
        for span in node.source_spans
    )


def build_index(
    layout: corpus.CorpusLayout, manifest, analyses, references_by_document
) -> Path:
    """Build the relational and full-text index inside a staged corpus."""

    ensure_fts5_available()
    layout.index.parent.mkdir(parents=True, exist_ok=True)
    if layout.index.exists():
        layout.index.unlink()
    connection = sqlite3.connect(layout.index)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(
            """
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE documents (
                document_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                revision TEXT NOT NULL,
                kind TEXT NOT NULL,
                source_path TEXT NOT NULL,
                source_sha256 TEXT NOT NULL,
                pdf_page_count INTEGER NOT NULL,
                amends_json TEXT NOT NULL,
                extracted_pdf_pages_json TEXT
            );
            CREATE TABLE nodes (
                rowid INTEGER PRIMARY KEY,
                node_id TEXT NOT NULL UNIQUE,
                document_id TEXT NOT NULL REFERENCES documents(document_id),
                kind TEXT NOT NULL,
                label TEXT NOT NULL,
                title TEXT NOT NULL,
                parent_id TEXT REFERENCES nodes(node_id),
                source_sha256 TEXT NOT NULL,
                confidence REAL NOT NULL,
                UNIQUE(document_id, kind, label)
            );
            CREATE TABLE node_spans (
                node_id TEXT NOT NULL REFERENCES nodes(node_id),
                ordinal INTEGER NOT NULL,
                pdf_page_start INTEGER NOT NULL,
                pdf_page_end INTEGER NOT NULL,
                start_offset INTEGER NOT NULL,
                end_offset INTEGER NOT NULL,
                text_sha256 TEXT NOT NULL,
                printed_page_start TEXT,
                printed_page_end TEXT,
                PRIMARY KEY(node_id, ordinal)
            );
            CREATE TABLE hierarchy_edges (
                parent_id TEXT NOT NULL REFERENCES nodes(node_id),
                child_id TEXT NOT NULL UNIQUE REFERENCES nodes(node_id),
                ordinal INTEGER NOT NULL,
                PRIMARY KEY(parent_id, child_id)
            );
            CREATE TABLE occurrences (
                occurrence_id INTEGER PRIMARY KEY,
                document_id TEXT NOT NULL REFERENCES documents(document_id),
                kind TEXT NOT NULL,
                label TEXT NOT NULL,
                title TEXT NOT NULL,
                raw_heading TEXT NOT NULL,
                pdf_page_start INTEGER NOT NULL,
                pdf_page_end INTEGER NOT NULL,
                start_offset INTEGER NOT NULL,
                end_offset INTEGER NOT NULL,
                text_sha256 TEXT NOT NULL,
                confidence REAL NOT NULL,
                classification TEXT NOT NULL,
                node_id TEXT REFERENCES nodes(node_id),
                reason TEXT
            );
            CREATE TABLE diagnostics (
                diagnostic_id INTEGER PRIMARY KEY,
                document_id TEXT NOT NULL REFERENCES documents(document_id),
                code TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                node_id TEXT,
                pdf_page_start INTEGER,
                pdf_page_end INTEGER,
                start_offset INTEGER,
                end_offset INTEGER
            );
            CREATE TABLE cross_references (
                reference_id TEXT PRIMARY KEY,
                source_document_id TEXT NOT NULL REFERENCES documents(document_id),
                source_node_id TEXT NOT NULL REFERENCES nodes(node_id),
                raw_text TEXT NOT NULL,
                pdf_page_start INTEGER NOT NULL,
                pdf_page_end INTEGER NOT NULL,
                start_offset INTEGER NOT NULL,
                end_offset INTEGER NOT NULL,
                text_sha256 TEXT NOT NULL,
                target_kind TEXT NOT NULL,
                target_label TEXT NOT NULL,
                status TEXT NOT NULL,
                target_node_id TEXT REFERENCES nodes(node_id),
                candidate_target_ids_json TEXT NOT NULL,
                reason TEXT
            );
            CREATE INDEX nodes_lookup ON nodes(kind, label, document_id);
            CREATE INDEX nodes_parent ON nodes(parent_id);
            CREATE INDEX occurrences_lookup ON occurrences(document_id, kind, label);
            CREATE INDEX diagnostics_lookup ON diagnostics(severity, code, document_id);
            CREATE INDEX references_source ON cross_references(source_node_id, start_offset);
            CREATE INDEX references_target ON cross_references(target_node_id, start_offset);
            CREATE VIRTUAL TABLE node_fts USING fts5(
                kind,
                label,
                title,
                body,
                content=''
            );
            """
        )
        connection.executemany(
            "INSERT INTO metadata(key, value) VALUES (?, ?)",
            (
                ("index_schema_version", str(INDEX_SCHEMA_VERSION)),
                ("corpus_format", corpus.CORPUS_FORMAT),
                ("corpus_format_version", str(corpus.CORPUS_FORMAT_VERSION)),
            ),
        )

        for document in manifest.documents:
            connection.execute(
                """
                INSERT INTO documents(
                    document_id, title, revision, kind, source_path, source_sha256,
                    pdf_page_count, amends_json, extracted_pdf_pages_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document.document_id,
                    document.title,
                    document.revision,
                    document.kind.value,
                    document.source_path,
                    document.source_sha256,
                    document.pdf_page_count,
                    json.dumps(document.amends),
                    (
                        json.dumps(document.extracted_pdf_pages)
                        if document.extracted_pdf_pages is not None
                        else None
                    ),
                ),
            )

        # Parent foreign keys can point forward, so insert nodes without parent links first.
        for document in manifest.documents:
            analysis = analyses[document.document_id]
            canonical_text = analysis.text
            for node in analysis.nodes:
                cursor = connection.execute(
                    """
                    INSERT INTO nodes(
                        node_id, document_id, kind, label, title, parent_id,
                        source_sha256, confidence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        node.node_id,
                        node.document_id,
                        node.kind.value,
                        node.label,
                        node.title,
                        None,
                        node.source_sha256,
                        node.confidence,
                    ),
                )
                connection.execute(
                    "INSERT INTO node_fts(rowid, kind, label, title, body) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        cursor.lastrowid,
                        node.kind.value,
                        node.label,
                        node.title,
                        _node_text(canonical_text, node),
                    ),
                )
                for ordinal, span in enumerate(node.source_spans):
                    connection.execute(
                        """
                        INSERT INTO node_spans(
                            node_id, ordinal, pdf_page_start, pdf_page_end,
                            start_offset, end_offset, text_sha256,
                            printed_page_start, printed_page_end
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            node.node_id,
                            ordinal,
                            span.pdf_page_start,
                            span.pdf_page_end,
                            span.start_offset,
                            span.end_offset,
                            span.text_sha256,
                            span.printed_page_start,
                            span.printed_page_end,
                        ),
                    )

        for document in manifest.documents:
            analysis = analyses[document.document_id]
            for node in analysis.nodes:
                if node.parent_id is not None:
                    connection.execute(
                        "UPDATE nodes SET parent_id = ? WHERE node_id = ?",
                        (node.parent_id, node.node_id),
                    )
                for ordinal, child_id in enumerate(node.child_ids):
                    connection.execute(
                        "INSERT INTO hierarchy_edges(parent_id, child_id, ordinal) "
                        "VALUES (?, ?, ?)",
                        (node.node_id, child_id, ordinal),
                    )

            for occurrence in analysis.occurrences:
                candidate = occurrence.candidate
                span = candidate.span
                connection.execute(
                    """
                    INSERT INTO occurrences(
                        document_id, kind, label, title, raw_heading,
                        pdf_page_start, pdf_page_end, start_offset, end_offset,
                        text_sha256, confidence, classification, node_id, reason
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        span.document_id,
                        candidate.kind.value,
                        candidate.label,
                        candidate.title,
                        candidate.raw_heading,
                        span.pdf_page_start,
                        span.pdf_page_end,
                        span.start_offset,
                        span.end_offset,
                        span.text_sha256,
                        candidate.confidence,
                        occurrence.classification.value,
                        occurrence.node_id,
                        occurrence.reason,
                    ),
                )

            for diagnostic in analysis.diagnostics:
                span = diagnostic.span
                connection.execute(
                    """
                    INSERT INTO diagnostics(
                        document_id, code, severity, message, node_id,
                        pdf_page_start, pdf_page_end, start_offset, end_offset
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        diagnostic.document_id,
                        diagnostic.code,
                        diagnostic.severity.value,
                        diagnostic.message,
                        diagnostic.node_id,
                        span.pdf_page_start if span is not None else None,
                        span.pdf_page_end if span is not None else None,
                        span.start_offset if span is not None else None,
                        span.end_offset if span is not None else None,
                    ),
                )

            for reference in references_by_document[document.document_id]:
                if not isinstance(reference, CrossReference):
                    raise TypeError("reference records must be CrossReference values")
                span = reference.source_span
                connection.execute(
                    """
                    INSERT INTO cross_references(
                        reference_id, source_document_id, source_node_id, raw_text,
                        pdf_page_start, pdf_page_end, start_offset, end_offset,
                        text_sha256, target_kind, target_label, status,
                        target_node_id, candidate_target_ids_json, reason
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        reference.reference_id,
                        span.document_id,
                        reference.source_node_id,
                        reference.raw_text,
                        span.pdf_page_start,
                        span.pdf_page_end,
                        span.start_offset,
                        span.end_offset,
                        span.text_sha256,
                        reference.target_kind.value,
                        reference.target_label,
                        reference.status.value,
                        reference.target_node_id,
                        json.dumps(reference.candidate_target_ids),
                        reference.reason,
                    ),
                )
        connection.commit()
    finally:
        connection.close()
    return layout.index


def _connect(root: Path) -> tuple[corpus.CorpusLayout, sqlite3.Connection]:
    layout = corpus.CorpusLayout(Path(root))
    corpus.load_manifest(layout.root)
    if not layout.index.is_file():
        raise StandardsIndexError(
            f"missing structural index: {layout.index}; {corpus.REBUILD_INSTRUCTION}"
        )
    connection = sqlite3.connect(layout.index)
    connection.row_factory = sqlite3.Row
    try:
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
    except sqlite3.Error as error:
        connection.close()
        raise StandardsIndexError(
            f"invalid standards index schema; {corpus.REBUILD_INSTRUCTION}"
        ) from error
    if (
        metadata.get("index_schema_version") != str(INDEX_SCHEMA_VERSION)
        or metadata.get("corpus_format") != corpus.CORPUS_FORMAT
        or metadata.get("corpus_format_version")
        != str(corpus.CORPUS_FORMAT_VERSION)
    ):
        connection.close()
        raise StandardsIndexError(
            f"unsupported standards index schema; {corpus.REBUILD_INSTRUCTION}"
        )
    return layout, connection


def _span_rows(connection: sqlite3.Connection, node_id: str) -> list[dict]:
    document_id = parse_node_id(node_id)[0]
    rows = connection.execute(
        "SELECT * FROM node_spans WHERE node_id = ? ORDER BY ordinal", (node_id,)
    )
    return [
        {
            "document_id": document_id,
            "pdf_page_start": row["pdf_page_start"],
            "pdf_page_end": row["pdf_page_end"],
            "start_offset": row["start_offset"],
            "end_offset": row["end_offset"],
            "text_sha256": row["text_sha256"],
            "printed_page_start": row["printed_page_start"],
            "printed_page_end": row["printed_page_end"],
            "locator": f"{document_id}@{row['start_offset']}:{row['end_offset']}",
        }
        for row in rows
    ]


def _node_summary(connection: sqlite3.Connection, row: sqlite3.Row) -> dict:
    spans = _span_rows(connection, row["node_id"])
    return {
        "node_id": row["node_id"],
        "document_id": row["document_id"],
        "kind": row["kind"],
        "label": row["label"],
        "title": row["title"],
        "parent_id": row["parent_id"],
        "confidence": row["confidence"],
        "source_spans": spans,
        "page_start": spans[0]["pdf_page_start"],
        "page_end": spans[-1]["pdf_page_end"],
    }


def _read_spans(layout, summary: dict, context_characters: int = 0) -> tuple[str, list[dict]]:
    text_path = layout.text(summary["document_id"])
    canonical_text = text_path.read_text(encoding="utf-8")
    parts = []
    context = []
    for span in summary["source_spans"]:
        start = span["start_offset"]
        end = span["end_offset"]
        part = canonical_text[start:end]
        if hashlib.sha256(part.encode("utf-8")).hexdigest() != span["text_sha256"]:
            raise StandardsIndexError(
                f"source span hash mismatch for {span['locator']}; {corpus.REBUILD_INSTRUCTION}"
            )
        parts.append(part)
        if context_characters:
            context.append(
                {
                    "locator": span["locator"],
                    "before": canonical_text[max(0, start - context_characters) : start],
                    "after": canonical_text[end : end + context_characters],
                }
            )
    return "\n\n".join(parts), context


def _select_node_row(
    connection: sqlite3.Connection,
    *,
    kind: str | None = None,
    label: str | None = None,
    document_id: str | None = None,
    node_id: str | None = None,
) -> sqlite3.Row:
    if node_id is not None:
        parse_node_id(node_id)
        rows = connection.execute(
            "SELECT * FROM nodes WHERE node_id = ?", (node_id,)
        ).fetchall()
    else:
        if kind is None or label is None:
            raise ValueError("kind and label are required for structural lookup")
        try:
            node_kind = NodeKind(kind)
        except ValueError as error:
            raise ValueError(f"unsupported node kind: {kind}") from error
        parameters = [node_kind.value, label]
        sql = "SELECT * FROM nodes WHERE kind = ? AND label = ?"
        if document_id is not None:
            sql += " AND document_id = ?"
            parameters.append(document_id)
        rows = connection.execute(sql, parameters).fetchall()

    if not rows:
        target = node_id or f"{kind} {label}"
        suffix = f" in {document_id}" if document_id else ""
        raise StandardsIndexError(f"unknown standards node: {target}{suffix}")
    if len(rows) > 1:
        documents = ", ".join(sorted(row["document_id"] for row in rows))
        raise StandardsIndexError(
            f"standards node is ambiguous across {documents}; specify --document"
        )
    return rows[0]


def get_node(
    root: Path,
    *,
    kind: str | None = None,
    label: str | None = None,
    document_id: str | None = None,
    node_id: str | None = None,
    include_children: bool = False,
    include_ancestors: bool = False,
    context_characters: int = 0,
) -> dict:
    if context_characters < 0:
        raise ValueError("context_characters must be non-negative")
    layout, connection = _connect(root)
    try:
        row = _select_node_row(
            connection,
            kind=kind,
            label=label,
            document_id=document_id,
            node_id=node_id,
        )
        summary = _node_summary(connection, row)
        summary["text"], context = _read_spans(
            layout, summary, context_characters=context_characters
        )
        if context:
            summary["context"] = context
        if include_children:
            child_rows = connection.execute(
                """
                SELECT child.* FROM hierarchy_edges edge
                JOIN nodes child ON child.node_id = edge.child_id
                WHERE edge.parent_id = ? ORDER BY edge.ordinal
                """,
                (summary["node_id"],),
            )
            summary["children"] = [
                _node_summary(connection, child) for child in child_rows
            ]
        if include_ancestors:
            ancestors = []
            parent_id = summary["parent_id"]
            while parent_id is not None:
                parent = connection.execute(
                    "SELECT * FROM nodes WHERE node_id = ?", (parent_id,)
                ).fetchone()
                if parent is None:
                    raise StandardsIndexError(
                        f"broken hierarchy link from {summary['node_id']} to {parent_id}"
                    )
                parent_summary = _node_summary(connection, parent)
                ancestors.append(parent_summary)
                parent_id = parent["parent_id"]
            summary["ancestors"] = ancestors
        return summary
    finally:
        connection.close()


def get_source_span(root: Path, locator: str, context_characters: int = 0) -> dict:
    if context_characters < 0:
        raise ValueError("context_characters must be non-negative")
    match = SOURCE_SPAN_RE.fullmatch(locator)
    if match is None:
        raise ValueError("source span must have the form document@start:end")
    start = int(match.group("start"))
    end = int(match.group("end"))
    if end <= start:
        raise ValueError("source span end must be greater than start")
    layout, connection = _connect(root)
    try:
        document_id = match.group("document")
        exists = connection.execute(
            "SELECT 1 FROM documents WHERE document_id = ?", (document_id,)
        ).fetchone()
        if exists is None:
            raise StandardsIndexError(f"unknown standards document: {document_id}")
        canonical_text = layout.text(document_id).read_text(encoding="utf-8")
        if end > len(canonical_text):
            raise StandardsIndexError(
                f"source span exceeds {document_id} text length {len(canonical_text)}"
            )
        result = {
            "type": "source-span",
            "locator": locator,
            "document_id": document_id,
            "start_offset": start,
            "end_offset": end,
            "text": canonical_text[start:end],
        }
        if context_characters:
            result["context"] = {
                "before": canonical_text[max(0, start - context_characters) : start],
                "after": canonical_text[end : end + context_characters],
            }
        return result
    finally:
        connection.close()


def _fts_query(user_query: str) -> tuple[str, list[str]]:
    tokens = re.findall(r"[\w]+", user_query, flags=re.UNICODE)
    if not tokens:
        raise ValueError("search query did not contain searchable terms")
    return " AND ".join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens), tokens


def _snippet(text: str, tokens: list[str], width: int = 240) -> str:
    flattened = " ".join(text.split())
    if len(flattened) <= width:
        return flattened
    lower = flattened.lower()
    positions = [lower.find(token.lower()) for token in tokens]
    positions = [position for position in positions if position >= 0]
    center = min(positions) if positions else 0
    start = max(0, center - width // 3)
    end = min(len(flattened), start + width)
    prefix = "..." if start else ""
    suffix = "..." if end < len(flattened) else ""
    return prefix + flattened[start:end] + suffix


def search(
    root: Path,
    query: str,
    *,
    limit: int = 10,
    document_id: str | None = None,
    kind: str | None = None,
) -> list[dict]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    match_query, tokens = _fts_query(query)
    exact_match = re.fullmatch(
        r"(?i)(clause|table|figure|definition)\s+(.+)", query.strip()
    )
    exact_kind = exact_match.group(1).lower() if exact_match else kind
    exact_label = exact_match.group(2).strip() if exact_match else query.strip()

    layout, connection = _connect(root)
    try:
        sql = """
            SELECT n.*,
                   CASE
                       WHEN lower(n.kind) = lower(?) AND lower(n.label) = lower(?) THEN 0
                       WHEN lower(n.label) = lower(?) THEN 1
                       WHEN lower(n.title) = lower(?) THEN 2
                       ELSE 3
                   END AS exact_rank,
                   bm25(node_fts, 1.0, 8.0, 5.0, 1.0) AS score
            FROM node_fts
            JOIN nodes n ON n.rowid = node_fts.rowid
            WHERE node_fts MATCH ?
        """
        parameters = [exact_kind or "", exact_label, exact_label, query.strip(), match_query]
        if document_id is not None:
            sql += " AND n.document_id = ?"
            parameters.append(document_id)
        if kind is not None:
            node_kind = NodeKind(kind)
            sql += " AND n.kind = ?"
            parameters.append(node_kind.value)
        sql += " ORDER BY exact_rank, score, n.document_id, n.kind, n.label LIMIT ?"
        parameters.append(limit)
        rows = connection.execute(sql, parameters).fetchall()
        results = []
        for row in rows:
            summary = _node_summary(connection, row)
            text, _ = _read_spans(layout, summary)
            summary["snippet"] = _snippet(text, tokens)
            summary["score"] = row["score"]
            results.append(summary)
        return results
    finally:
        connection.close()


def _reference_summary(
    layout: corpus.CorpusLayout,
    connection: sqlite3.Connection,
    row: sqlite3.Row,
) -> dict:
    locator = (
        f"{row['source_document_id']}@{row['start_offset']}:{row['end_offset']}"
    )
    canonical_text = layout.text(row["source_document_id"]).read_text(encoding="utf-8")
    source_text = canonical_text[row["start_offset"] : row["end_offset"]]
    if hashlib.sha256(source_text.encode("utf-8")).hexdigest() != row["text_sha256"]:
        raise StandardsIndexError(
            f"source span hash mismatch for {locator}; {corpus.REBUILD_INSTRUCTION}"
        )
    if source_text != row["raw_text"]:
        raise StandardsIndexError(
            f"reference text mismatch for {locator}; {corpus.REBUILD_INSTRUCTION}"
        )
    source_row = connection.execute(
        "SELECT * FROM nodes WHERE node_id = ?", (row["source_node_id"],)
    ).fetchone()
    if source_row is None:
        raise StandardsIndexError(
            f"broken reference source link to {row['source_node_id']}"
        )
    target = None
    if row["target_node_id"] is not None:
        target_row = connection.execute(
            "SELECT * FROM nodes WHERE node_id = ?", (row["target_node_id"],)
        ).fetchone()
        if target_row is None:
            raise StandardsIndexError(
                f"broken reference target link to {row['target_node_id']}"
            )
        target = _node_summary(connection, target_row)
    return {
        "reference_id": row["reference_id"],
        "source_node_id": row["source_node_id"],
        "source": _node_summary(connection, source_row),
        "raw_text": row["raw_text"],
        "source_span": {
            "document_id": row["source_document_id"],
            "pdf_page_start": row["pdf_page_start"],
            "pdf_page_end": row["pdf_page_end"],
            "start_offset": row["start_offset"],
            "end_offset": row["end_offset"],
            "text_sha256": row["text_sha256"],
            "locator": locator,
        },
        "target_kind": row["target_kind"],
        "target_label": row["target_label"],
        "status": row["status"],
        "target_node_id": row["target_node_id"],
        "target": target,
        "candidate_target_ids": json.loads(row["candidate_target_ids_json"]),
        "reason": row["reason"],
    }


def _reference_result(
    root: Path,
    *,
    incoming: bool,
    kind: str | None,
    label: str | None,
    document_id: str | None,
    node_id: str | None,
    limit: int,
) -> dict:
    if limit <= 0:
        raise ValueError("limit must be positive")
    layout, connection = _connect(root)
    try:
        node_row = _select_node_row(
            connection,
            kind=kind,
            label=label,
            document_id=document_id,
            node_id=node_id,
        )
        column = "target_node_id" if incoming else "source_node_id"
        total = connection.execute(
            f"SELECT count(*) FROM cross_references WHERE {column} = ?",
            (node_row["node_id"],),
        ).fetchone()[0]
        rows = connection.execute(
            f"SELECT * FROM cross_references WHERE {column} = ? "
            "ORDER BY source_document_id, start_offset, reference_id LIMIT ?",
            (node_row["node_id"], limit),
        ).fetchall()
        return {
            "node": _node_summary(connection, node_row),
            "direction": "incoming" if incoming else "outgoing",
            "total": total,
            "limit": limit,
            "references": [
                _reference_summary(layout, connection, row) for row in rows
            ],
        }
    finally:
        connection.close()


def references(
    root: Path,
    *,
    kind: str | None = None,
    label: str | None = None,
    document_id: str | None = None,
    node_id: str | None = None,
    limit: int = 100,
) -> dict:
    """Return outgoing references, including unresolved and ambiguous records."""

    return _reference_result(
        root,
        incoming=False,
        kind=kind,
        label=label,
        document_id=document_id,
        node_id=node_id,
        limit=limit,
    )


def referenced_by(
    root: Path,
    *,
    kind: str | None = None,
    label: str | None = None,
    document_id: str | None = None,
    node_id: str | None = None,
    limit: int = 100,
) -> dict:
    """Return derived incoming edges from references resolved to one node."""

    return _reference_result(
        root,
        incoming=True,
        kind=kind,
        label=label,
        document_id=document_id,
        node_id=node_id,
        limit=limit,
    )


def define(
    root: Path,
    term: str,
    *,
    document_id: str | None = None,
) -> dict:
    normalized = " ".join(term.split())
    if not normalized:
        raise ValueError("definition term must not be empty")
    layout, connection = _connect(root)
    try:
        parameters = [NodeKind.DEFINITION.value, normalized]
        sql = "SELECT * FROM nodes WHERE kind = ? AND lower(label) = lower(?)"
        if document_id is not None:
            sql += " AND document_id = ?"
            parameters.append(document_id)
        rows = connection.execute(sql, parameters).fetchall()
        if not rows:
            suffix = f" in {document_id}" if document_id else ""
            raise StandardsIndexError(f"unknown standards definition: {normalized}{suffix}")
        if len(rows) > 1:
            documents = ", ".join(sorted(row["document_id"] for row in rows))
            raise StandardsIndexError(
                f"standards definition is ambiguous across {documents}; specify --document"
            )
        summary = _node_summary(connection, rows[0])
        summary["text"], _ = _read_spans(layout, summary)
        return summary
    finally:
        connection.close()


def lint(
    root: Path,
    *,
    document_id: str | None = None,
    minimum_severity: str = "warning",
    limit: int = 100,
) -> dict:
    if minimum_severity not in SEVERITY_ORDER:
        raise ValueError(f"unknown diagnostic severity: {minimum_severity}")
    if limit <= 0:
        raise ValueError("limit must be positive")
    _, connection = _connect(root)
    try:
        where = ""
        parameters: list = []
        if document_id is not None:
            where = " WHERE document_id = ?"
            parameters.append(document_id)
        count_rows = connection.execute(
            "SELECT severity, code, count(*) AS count FROM diagnostics"
            + where
            + " GROUP BY severity, code ORDER BY severity, code",
            parameters,
        )
        counts: dict[str, dict[str, int]] = {}
        for row in count_rows:
            counts.setdefault(row["severity"], {})[row["code"]] = row["count"]

        severities = [
            severity
            for severity, rank in SEVERITY_ORDER.items()
            if rank >= SEVERITY_ORDER[minimum_severity]
        ]
        placeholders = ",".join("?" for _ in severities)
        finding_sql = f"SELECT * FROM diagnostics WHERE severity IN ({placeholders})"
        finding_parameters: list = list(severities)
        if document_id is not None:
            finding_sql += " AND document_id = ?"
            finding_parameters.append(document_id)
        finding_sql += (
            " ORDER BY CASE severity WHEN 'error' THEN 0 WHEN 'warning' THEN 1 ELSE 2 END, "
            "document_id, code, diagnostic_id LIMIT ?"
        )
        finding_parameters.append(limit)
        findings = [dict(row) for row in connection.execute(finding_sql, finding_parameters)]
        total = sum(sum(code_counts.values()) for code_counts in counts.values())
        return {
            "counts": counts,
            "total": total,
            "minimum_severity": minimum_severity,
            "limit": limit,
            "findings": findings,
        }
    finally:
        connection.close()


def document_counts(root: Path) -> dict[str, dict[str, int]]:
    _, connection = _connect(root)
    try:
        result = {}
        for row in connection.execute(
            """
            SELECT d.document_id,
                   (SELECT count(*) FROM nodes n
                    WHERE n.document_id = d.document_id) AS nodes,
                   (SELECT count(*) FROM occurrences o
                    WHERE o.document_id = d.document_id) AS occurrences,
                   (SELECT count(*) FROM diagnostics x
                    WHERE x.document_id = d.document_id) AS diagnostics,
                   (SELECT count(*) FROM cross_references r
                    WHERE r.source_document_id = d.document_id) AS reference_count
            FROM documents d
            ORDER BY d.document_id
            """
        ):
            result[row["document_id"]] = {
                "nodes": row["nodes"],
                "occurrences": row["occurrences"],
                "diagnostics": row["diagnostics"],
                "references": row["reference_count"],
            }
        return result
    finally:
        connection.close()
