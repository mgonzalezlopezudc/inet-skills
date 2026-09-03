"""Standards corpus layout and whole-directory publication contract."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from uuid import uuid4

try:
    from .model import ModelValidationError, StandardDocument, validate_document_id
except ImportError:
    from model import ModelValidationError, StandardDocument, validate_document_id


CORPUS_FORMAT = "inet-standards-corpus"
CORPUS_FORMAT_VERSION = 2
MANIFEST_FILENAME = "corpus.json"
REBUILD_INSTRUCTION = "rebuild the standards corpus with inet_process_standards build"


class CorpusError(RuntimeError):
    """Base class for corpus layout and publication failures."""


class IncompatibleCorpusError(CorpusError):
    """Raised when a query encounters an unsupported corpus format."""


class IncompleteCorpusError(CorpusError):
    """Raised when a staged corpus does not contain every required artifact."""


@dataclass(frozen=True)
class ExtractionRecord:
    implementation: str
    version: str
    arguments: tuple[str, ...]
    tool_versions: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.implementation, str) or not self.implementation.strip():
            raise ModelValidationError("extractor implementation must be a non-empty string")
        if not isinstance(self.version, str) or not self.version.strip():
            raise ModelValidationError("extractor version must be a non-empty string")
        arguments = tuple(self.arguments)
        if any(not isinstance(argument, str) for argument in arguments):
            raise ModelValidationError("extractor arguments must be strings")
        object.__setattr__(self, "arguments", arguments)
        tool_versions = tuple((name, version) for name, version in self.tool_versions)
        if any(not name or not version for name, version in tool_versions):
            raise ModelValidationError("tool versions must contain non-empty names and versions")
        if len({name for name, _ in tool_versions}) != len(tool_versions):
            raise ModelValidationError("tool version names must be unique")
        object.__setattr__(self, "tool_versions", tool_versions)

    def to_dict(self) -> dict:
        return {
            "implementation": self.implementation,
            "version": self.version,
            "arguments": list(self.arguments),
            "tool_versions": dict(self.tool_versions),
        }

    @classmethod
    def from_dict(cls, value: dict) -> "ExtractionRecord":
        try:
            return cls(
                implementation=value["implementation"],
                version=value["version"],
                arguments=tuple(value.get("arguments", ())),
                tool_versions=tuple(value.get("tool_versions", {}).items()),
            )
        except (AttributeError, KeyError, TypeError, ValueError) as error:
            if isinstance(error, ModelValidationError):
                raise
            raise ModelValidationError(f"invalid extraction record: {error}") from error


@dataclass(frozen=True)
class CorpusManifest:
    generated_at: str
    extractor: ExtractionRecord
    documents: tuple[StandardDocument, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.generated_at, str):
            raise ModelValidationError("generated_at must be an ISO-8601 string")
        try:
            generated = datetime.fromisoformat(self.generated_at)
        except ValueError as error:
            raise ModelValidationError("generated_at must be an ISO-8601 timestamp") from error
        if generated.tzinfo is None:
            raise ModelValidationError("generated_at must include a timezone")
        if not isinstance(self.extractor, ExtractionRecord):
            raise ModelValidationError("extractor must be an ExtractionRecord")
        documents = tuple(self.documents)
        if not documents:
            raise ModelValidationError("documents must not be empty")
        if any(not isinstance(document, StandardDocument) for document in documents):
            raise ModelValidationError("documents must contain StandardDocument values")
        document_ids = [document.document_id for document in documents]
        if len(set(document_ids)) != len(document_ids):
            raise ModelValidationError("document identifiers must be unique")
        object.__setattr__(self, "documents", documents)

    def to_dict(self) -> dict:
        return {
            "format": CORPUS_FORMAT,
            "format_version": CORPUS_FORMAT_VERSION,
            "generated_at": self.generated_at,
            "extractor": self.extractor.to_dict(),
            "documents": [document.to_dict() for document in self.documents],
        }

    @classmethod
    def from_dict(cls, value: dict) -> "CorpusManifest":
        if not isinstance(value, dict):
            raise IncompatibleCorpusError(
                f"unsupported standards corpus manifest; {REBUILD_INSTRUCTION}"
            )
        if value.get("format") != CORPUS_FORMAT:
            raise IncompatibleCorpusError(
                f"unsupported standards corpus format; {REBUILD_INSTRUCTION}"
            )
        if value.get("format_version") != CORPUS_FORMAT_VERSION:
            raise IncompatibleCorpusError(
                "unsupported standards corpus format version "
                f"{value.get('format_version')!r}; {REBUILD_INSTRUCTION}"
            )
        try:
            return cls(
                generated_at=value["generated_at"],
                extractor=ExtractionRecord.from_dict(value["extractor"]),
                documents=tuple(
                    StandardDocument.from_dict(document)
                    for document in value["documents"]
                ),
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, ModelValidationError):
                raise
            raise ModelValidationError(f"invalid corpus manifest: {error}") from error


@dataclass(frozen=True)
class CorpusLayout:
    root: Path

    @property
    def manifest(self) -> Path:
        return self.root / MANIFEST_FILENAME

    @property
    def index(self) -> Path:
        return self.root / "index.sqlite"

    def document_root(self, document_id: str) -> Path:
        return self.root / "documents" / validate_document_id(document_id)

    def text(self, document_id: str) -> Path:
        return self.document_root(document_id) / "text.txt"

    def pages(self, document_id: str) -> Path:
        return self.document_root(document_id) / "pages"

    def page(self, document_id: str, pdf_page: int) -> Path:
        if isinstance(pdf_page, bool) or not isinstance(pdf_page, int) or pdf_page <= 0:
            raise ModelValidationError("pdf_page must be a positive integer")
        return self.pages(document_id) / f"page-{pdf_page:06d}.txt"

    def structure_root(self, document_id: str) -> Path:
        return self.root / "structure" / validate_document_id(document_id)

    def nodes(self, document_id: str) -> Path:
        return self.structure_root(document_id) / "nodes.jsonl"

    def occurrences(self, document_id: str) -> Path:
        return self.structure_root(document_id) / "occurrences.jsonl"

    def diagnostics(self, document_id: str) -> Path:
        return self.structure_root(document_id) / "diagnostics.jsonl"

    def references(self, document_id: str) -> Path:
        return self.structure_root(document_id) / "references.jsonl"


def write_manifest(root: Path, manifest: CorpusManifest) -> Path:
    layout = CorpusLayout(Path(root))
    layout.manifest.parent.mkdir(parents=True, exist_ok=True)
    layout.manifest.write_text(
        json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return layout.manifest


def load_manifest(root: Path) -> CorpusManifest:
    root = Path(root)
    path = CorpusLayout(root).manifest
    if not path.is_file():
        raise CorpusError(f"missing standards corpus manifest: {path}; {REBUILD_INSTRUCTION}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CorpusError(
            f"cannot read standards corpus manifest {path}: {error}; {REBUILD_INSTRUCTION}"
        ) from error
    try:
        return CorpusManifest.from_dict(value)
    except ModelValidationError as error:
        raise IncompatibleCorpusError(
            f"invalid standards corpus manifest: {error}; {REBUILD_INSTRUCTION}"
        ) from error


def validate_complete_corpus(root: Path) -> CorpusManifest:
    layout = CorpusLayout(Path(root))
    manifest = load_manifest(layout.root)
    missing = []
    if not layout.index.is_file():
        missing.append(layout.index)
    for document in manifest.documents:
        if not layout.text(document.document_id).is_file():
            missing.append(layout.text(document.document_id))
        if not layout.nodes(document.document_id).is_file():
            missing.append(layout.nodes(document.document_id))
        if not layout.occurrences(document.document_id).is_file():
            missing.append(layout.occurrences(document.document_id))
        if not layout.diagnostics(document.document_id).is_file():
            missing.append(layout.diagnostics(document.document_id))
        if not layout.references(document.document_id).is_file():
            missing.append(layout.references(document.document_id))
        for page in document.page_numbers:
            if not layout.page(document.document_id, page).is_file():
                missing.append(layout.page(document.document_id, page))
    if missing:
        sample = ", ".join(str(path) for path in missing[:5])
        suffix = "" if len(missing) <= 5 else f" and {len(missing) - 5} more"
        raise IncompleteCorpusError(f"staged standards corpus is incomplete: {sample}{suffix}")
    return manifest


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


class CorpusBuildTransaction:
    """Build beside the active corpus and publish the complete directory as one unit."""

    def __init__(self, target: Path):
        self.target = Path(target)
        if self.target.parent == self.target:
            raise ValueError("the filesystem root cannot be a corpus target")
        self.staging: Path | None = None
        self.committed = False

    def __enter__(self) -> "CorpusBuildTransaction":
        self.target.parent.mkdir(parents=True, exist_ok=True)
        self.staging = Path(
            tempfile.mkdtemp(
                prefix=f".{self.target.name}.build-",
                dir=self.target.parent,
            )
        )
        return self

    @property
    def layout(self) -> CorpusLayout:
        if self.staging is None:
            raise RuntimeError("corpus transaction has not started")
        return CorpusLayout(self.staging)

    def commit(self) -> CorpusLayout:
        if self.staging is None:
            raise RuntimeError("corpus transaction has not started")
        if self.committed:
            raise RuntimeError("corpus transaction has already committed")
        validate_complete_corpus(self.staging)

        backup = self.target.with_name(f".{self.target.name}.previous-{uuid4().hex}")
        had_target = self.target.exists() or self.target.is_symlink()
        if had_target:
            os.replace(self.target, backup)
        try:
            os.replace(self.staging, self.target)
        except BaseException:
            if had_target and (backup.exists() or backup.is_symlink()):
                os.replace(backup, self.target)
            raise

        self.committed = True
        self.staging = None
        if had_target:
            try:
                remove_path(backup)
            except OSError:
                pass
        return CorpusLayout(self.target)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.staging is not None:
            remove_path(self.staging)
            self.staging = None
