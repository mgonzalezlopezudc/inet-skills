"""Schema and semantic validation for a non-authoritative feature IR."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml
from jsonschema import Draft202012Validator, FormatChecker


SCHEMA_PATH = Path(__file__).with_name("feature-v1.schema.json")
ENTITY_SECTIONS = (
    "sources",
    "roles",
    "conditions",
    "actions",
    "qualifiers",
    "obligations",
    "state_variables",
    "transitions",
    "exchanges",
    "invariants",
    "implementation_mappings",
    "verification_mappings",
    "reviews",
)


@dataclass
class ValidationResult:
    """Collect deterministic, path-qualified validation findings."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.errors

    def error(self, path: str, message: str) -> None:
        self.errors.append(f"{path}: {message}")

    def warn(self, path: str, message: str) -> None:
        self.warnings.append(f"{path}: {message}")

    def to_dict(self) -> dict:
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def load_feature(path: Path) -> dict:
    """Load one YAML feature manifest and require a top-level mapping."""

    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ValueError(f"cannot read feature manifest {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError(f"feature manifest must contain a YAML mapping: {path}")
    return value


def _load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _json_path(parts: Iterable[object]) -> str:
    path = "$"
    for part in parts:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return path


def _validate_schema(feature: dict, result: ValidationResult) -> None:
    validator = Draft202012Validator(_load_schema(), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(feature), key=lambda error: _json_path(error.absolute_path))
    for error in errors:
        result.error(_json_path(error.absolute_path), error.message)


def _items_by_id(feature: dict, section: str) -> dict[str, dict]:
    return {
        item["id"]: item
        for item in feature.get(section, [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _iter_entities(feature: dict):
    feature_record = feature.get("feature")
    if isinstance(feature_record, dict) and isinstance(feature_record.get("id"), str):
        yield "feature", feature_record, "$.feature"
    for section in ENTITY_SECTIONS:
        for index, item in enumerate(feature.get(section, [])):
            if isinstance(item, dict) and isinstance(item.get("id"), str):
                yield section, item, f"$.{section}[{index}]"
            if section == "exchanges" and isinstance(item, dict):
                for step_index, step in enumerate(item.get("steps", [])):
                    if isinstance(step, dict) and isinstance(step.get("id"), str):
                        yield "exchange_steps", step, f"$.exchanges[{index}].steps[{step_index}]"
            if section == "reviews" and isinstance(item, dict):
                for finding_index, finding in enumerate(item.get("findings", [])):
                    if isinstance(finding, dict) and isinstance(finding.get("id"), str):
                        yield "findings", finding, f"$.reviews[{index}].findings[{finding_index}]"


def _build_registry(feature: dict, result: ValidationResult | None = None) -> dict[str, tuple]:
    registry: dict[str, tuple] = {}
    for entity_type, entity, path in _iter_entities(feature):
        identifier = entity["id"]
        if identifier in registry:
            if result is not None:
                result.error(path + ".id", f"duplicate semantic id {identifier!r}")
        else:
            registry[identifier] = (entity_type, entity, path)
    return registry


def _check_references(
    values: Iterable[str], valid: set[str], path: str, kind: str, result: ValidationResult
) -> None:
    for index, value in enumerate(values):
        if value not in valid:
            result.error(f"{path}[{index}]", f"unknown {kind} id {value!r}")


def _validate_obligations(feature: dict, result: ValidationResult) -> None:
    ids = {section: set(_items_by_id(feature, section)) for section in ENTITY_SECTIONS}
    pass_two_disputes: set[str] = set()
    for review in feature.get("reviews", []):
        if review.get("pass") == 2:
            for finding in review.get("findings", []):
                if finding.get("kind") == "disagreement":
                    pass_two_disputes.update(finding.get("obligations", []))

    for index, obligation in enumerate(feature.get("obligations", [])):
        path = f"$.obligations[{index}]"
        _check_references([obligation["subject"]], ids["roles"], path + ".subject", "role", result)
        _check_references(obligation["conditions"], ids["conditions"], path + ".conditions", "condition", result)
        _check_references([obligation["action"]], ids["actions"], path + ".action", "action", result)
        _check_references(obligation["qualifiers"], ids["qualifiers"], path + ".qualifiers", "qualifier", result)
        _check_references(obligation["sources"], ids["sources"], path + ".sources", "source", result)
        _check_references(
            obligation["implementation_mappings"],
            ids["implementation_mappings"],
            path + ".implementation_mappings",
            "implementation mapping",
            result,
        )
        _check_references(
            obligation["verification_mappings"],
            ids["verification_mappings"],
            path + ".verification_mappings",
            "verification mapping",
            result,
        )
        _validate_status(feature, obligation, path, pass_two_disputes, result)


def _mapping_records(feature: dict, section: str, identifiers: Iterable[str]) -> list[dict]:
    records = _items_by_id(feature, section)
    return [records[identifier] for identifier in identifiers if identifier in records]


def _validate_status(
    feature: dict,
    obligation: dict,
    path: str,
    pass_two_disputes: set[str],
    result: ValidationResult,
) -> None:
    status = obligation["status"]
    identifier = obligation["id"]
    disputed = identifier in pass_two_disputes
    if status["source_review"] == "disputed" and not disputed:
        result.error(path + ".status.source_review", "disputed status needs a pass-two disagreement")
    if status["source_review"] == "source-checked" and disputed:
        result.error(path + ".status.source_review", "pass-two disagreement requires disputed status")

    implementation = _mapping_records(
        feature, "implementation_mappings", obligation["implementation_mappings"]
    )
    _validate_axis(
        status["implementation"], implementation, "unmapped", path + ".status.implementation", result
    )
    if status["implementation"] == "implemented":
        if not any(item.get("relation") == "realizes" for item in implementation):
            result.error(path + ".status.implementation", "implemented status needs a realizing mapping")
        if any(item.get("relation") == "contradicts" or item.get("resolution") == "gap" for item in implementation):
            result.error(
                path + ".status.implementation",
                "implemented status cannot retain a contradiction or implementation gap",
            )
    verification = _mapping_records(
        feature, "verification_mappings", obligation["verification_mappings"]
    )
    _validate_axis(
        status["verification"], verification, "uncovered", path + ".status.verification", result
    )
    if status["verification"] == "verified":
        passed = any(
            item.get("resolution") == "resolved"
            and item.get("evidence", {}).get("result") == "pass"
            for item in verification
        )
        if not passed:
            result.error(path + ".status.verification", "verified status needs passing evidence")


def _validate_axis(
    status: str,
    mappings: list[dict],
    empty_status: str,
    path: str,
    result: ValidationResult,
) -> None:
    resolved = [mapping for mapping in mappings if mapping.get("resolution") == "resolved"]
    if not mappings:
        result.error(path, "status needs a resolved target or an explicit gap mapping")
    elif status == empty_status and resolved:
        result.error(path, f"{empty_status} status cannot cite a resolved mapping")
    elif status != empty_status and not resolved:
        result.error(path, f"{status} status needs at least one resolved mapping")


def _validate_state_and_exchange(feature: dict, result: ValidationResult) -> None:
    roles = set(_items_by_id(feature, "roles"))
    conditions = set(_items_by_id(feature, "conditions"))
    actions = set(_items_by_id(feature, "actions"))
    obligations = set(_items_by_id(feature, "obligations"))
    state_variables = _items_by_id(feature, "state_variables")

    for index, variable in enumerate(feature.get("state_variables", [])):
        path = f"$.state_variables[{index}]"
        _check_references([variable["owner"]], roles, path + ".owner", "role", result)
        if variable["initial"] not in variable["states"]:
            result.error(path + ".initial", "initial state is not declared in states")

    for index, transition in enumerate(feature.get("transitions", [])):
        path = f"$.transitions[{index}]"
        variable = state_variables.get(transition["state_variable"])
        if variable is None:
            result.error(path + ".state_variable", "unknown state variable id")
        else:
            for field_name in ("from", "to"):
                if transition[field_name] not in variable["states"]:
                    result.error(path + f".{field_name}", "state is not declared by the state variable")
        _check_references(transition["conditions"], conditions, path + ".conditions", "condition", result)
        _check_references(transition["actions"], actions, path + ".actions", "action", result)
        _check_references(transition["obligations"], obligations, path + ".obligations", "obligation", result)

    for exchange_index, exchange in enumerate(feature.get("exchanges", [])):
        path = f"$.exchanges[{exchange_index}]"
        _check_references(exchange["participants"], roles, path + ".participants", "role", result)
        for step_index, step in enumerate(exchange["steps"]):
            step_path = path + f".steps[{step_index}]"
            _check_references([step["actor"]], roles, step_path + ".actor", "role", result)
            if "peer" in step:
                _check_references([step["peer"]], roles, step_path + ".peer", "role", result)
            _check_references(step["obligations"], obligations, step_path + ".obligations", "obligation", result)


def _validate_mapping_links(feature: dict, result: ValidationResult) -> None:
    obligations = _items_by_id(feature, "obligations")
    obligation_ids = set(obligations)
    for section, field_name in (
        ("implementation_mappings", "implementation_mappings"),
        ("verification_mappings", "verification_mappings"),
    ):
        for index, mapping in enumerate(feature.get(section, [])):
            path = f"$.{section}[{index}].obligations"
            _check_references(mapping["obligations"], obligation_ids, path, "obligation", result)
            for obligation_id in mapping["obligations"]:
                if obligation_id in obligations and mapping["id"] not in obligations[obligation_id][field_name]:
                    result.error(path, f"mapping is not cited back by obligation {obligation_id!r}")
        mappings = _items_by_id(feature, section)
        for obligation_id, obligation in obligations.items():
            for mapping_id in obligation[field_name]:
                if mapping_id in mappings and obligation_id not in mappings[mapping_id]["obligations"]:
                    result.error(
                        f"$.obligations.{obligation_id}.{field_name}",
                        f"mapping {mapping_id!r} does not cite the obligation back",
                    )


def _validate_reviews_and_invariants(feature: dict, result: ValidationResult) -> None:
    source_ids = set(_items_by_id(feature, "sources"))
    obligation_ids = set(_items_by_id(feature, "obligations"))
    passes = [review.get("pass") for review in feature.get("reviews", [])]
    if sorted(passes) != [1, 2]:
        result.error("$.reviews", "exactly one source-check pass 1 and one pass 2 are required")
    second_findings = [
        finding
        for review in feature.get("reviews", [])
        if review.get("pass") == 2
        for finding in review.get("findings", [])
    ]
    if not any(item.get("kind") in {"omission", "qualification", "disagreement"} for item in second_findings):
        result.error("$.reviews", "pass 2 must record an omission, qualification, or disagreement")

    reviewed_by_pass = {
        review["pass"]: set(review["sources"])
        for review in feature.get("reviews", [])
        if review.get("pass") in {1, 2}
    }
    for source_id in source_ids:
        for pass_number in (1, 2):
            if source_id not in reviewed_by_pass.get(pass_number, set()):
                result.error(
                    "$.reviews",
                    f"source {source_id!r} is missing from source-check pass {pass_number}",
                )

    for index, review in enumerate(feature.get("reviews", [])):
        path = f"$.reviews[{index}]"
        _check_references(review["sources"], source_ids, path + ".sources", "source", result)
        for finding_index, finding in enumerate(review["findings"]):
            _check_references(
                finding["obligations"],
                obligation_ids,
                path + f".findings[{finding_index}].obligations",
                "obligation",
                result,
            )
    for index, invariant in enumerate(feature.get("invariants", [])):
        path = f"$.invariants[{index}]"
        _check_references(invariant["sources"], source_ids, path + ".sources", "source", result)
        _check_references(
            invariant["obligations"], obligation_ids, path + ".obligations", "obligation", result
        )


def _load_corpus(corpus_root: Path, result: ValidationResult) -> tuple[dict, dict]:
    manifest_path = corpus_root / "corpus.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        result.error("$external.corpus", f"cannot read {manifest_path}: {error}")
        return {}, {}
    if manifest.get("format") != "inet-standards-corpus" or manifest.get("format_version") != 2:
        result.error("$external.corpus", "source validation requires standards corpus format 2")
        return {}, {}
    documents = {item["document_id"]: item for item in manifest.get("documents", [])}
    return manifest, documents


def _load_nodes(corpus_root: Path, document: str, result: ValidationResult) -> dict[str, dict]:
    path = corpus_root / "structure" / document / "nodes.jsonl"
    nodes: dict[str, dict] = {}
    try:
        with path.open(encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                try:
                    node = json.loads(line)
                    nodes[node["node_id"]] = node
                except (json.JSONDecodeError, KeyError) as error:
                    result.error("$external.corpus", f"invalid {path}:{line_number}: {error}")
                    return {}
    except OSError as error:
        result.error("$external.corpus", f"cannot read {path}: {error}")
    return nodes


def _validate_sources(feature: dict, corpus_root: Path | None, result: ValidationResult) -> None:
    if corpus_root is None:
        result.warn("$external.corpus", "source node and reviewed hash checks were not run")
        return
    _, documents = _load_corpus(corpus_root, result)
    node_cache: dict[str, dict[str, dict]] = {}
    for index, source in enumerate(feature.get("sources", [])):
        path = f"$.sources[{index}]"
        document = source["document"]
        document_record = documents.get(document)
        if document_record is None:
            result.error(path + ".document", f"document {document!r} is absent from the corpus")
            continue
        if str(document_record.get("revision")) != source["revision"]:
            result.error(path + ".revision", "revision does not match the corpus manifest")
        if document not in node_cache:
            node_cache[document] = _load_nodes(corpus_root, document, result)
        nodes = node_cache[document]
        node = nodes.get(source["node_id"])
        if node is None:
            result.error(path + ".node_id", "canonical source node is absent from the corpus")
            continue
        if node.get("document_id") != document:
            result.error(path + ".node_id", "canonical source node belongs to another document")
        matching_spans = [
            span
            for span in node.get("source_spans", [])
            if (
                span.get("locator")
                or f"{span.get('document_id')}@{span.get('start_offset')}:{span.get('end_offset')}"
            )
            == source["locator"]
        ]
        if not matching_spans:
            result.error(path + ".locator", "locator is not a source span of the canonical node")
        elif matching_spans[0].get("text_sha256") != source["reviewed_text_sha256"]:
            result.error(path + ".reviewed_text_sha256", "reviewed hash does not match the corpus span")


def _safe_target(root: Path, relative: str) -> Path | None:
    root = root.resolve()
    target = (root / relative).resolve()
    return target if target.is_relative_to(root) else None


def _validate_targets(feature: dict, inet_root: Path | None, result: ValidationResult) -> None:
    resolved = [
        (section, index, mapping)
        for section in ("implementation_mappings", "verification_mappings")
        for index, mapping in enumerate(feature.get(section, []))
        if mapping.get("resolution") == "resolved"
    ]
    if inet_root is None:
        if resolved:
            result.warn("$external.inet", "resolved implementation and verification targets were not checked")
        return
    for section, index, mapping in resolved:
        path = f"$.{section}[{index}]"
        target = _safe_target(inet_root, mapping["path"])
        if target is None:
            result.error(path + ".path", "target escapes the INET root")
            continue
        if not target.is_file():
            result.error(path + ".path", f"target does not exist: {mapping['path']}")
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            result.error(path + ".path", f"cannot inspect target: {error}")
            continue
        checks = [("symbol", mapping.get("symbol"))]
        if section == "verification_mappings":
            checks.extend(
                [("configuration", mapping.get("configuration")), ("selector", mapping.get("selector"))]
            )
        for field_name, needle in checks:
            if needle and needle not in text:
                result.error(path + f".{field_name}", f"{needle!r} is absent from {mapping['path']}")


def validate_feature(
    feature: dict, *, corpus_root: Path | None = None, inet_root: Path | None = None
) -> ValidationResult:
    """Validate shape, traceability, statuses, and optional external targets."""

    result = ValidationResult()
    _validate_schema(feature, result)
    if result.errors:
        return result
    _build_registry(feature, result)
    _validate_obligations(feature, result)
    _validate_state_and_exchange(feature, result)
    _validate_mapping_links(feature, result)
    _validate_reviews_and_invariants(feature, result)
    _validate_sources(feature, corpus_root, result)
    _validate_targets(feature, inet_root, result)
    result.errors.sort()
    result.warnings.sort()
    return result


def _collect_semantic_ids(value, known: set[str]) -> set[str]:
    found: set[str] = set()
    if isinstance(value, str) and value in known:
        found.add(value)
    elif isinstance(value, list):
        for item in value:
            found.update(_collect_semantic_ids(item, known))
    elif isinstance(value, dict):
        for key, item in value.items():
            if key != "id":
                found.update(_collect_semantic_ids(item, known))
    return found


def trace_feature(feature: dict, identifier: str) -> dict:
    """Return one semantic entity with outbound and reverse manifest links."""

    registry = _build_registry(feature)
    if identifier not in registry:
        raise ValueError(f"unknown feature semantic id: {identifier}")
    entity_type, entity, path = registry[identifier]
    known = set(registry)
    outbound = sorted(_collect_semantic_ids(entity, known) - {identifier})
    referenced_by = sorted(
        candidate
        for candidate, (_, record, _) in registry.items()
        if candidate != identifier and identifier in _collect_semantic_ids(record, known)
    )
    return {
        "id": identifier,
        "entity_type": entity_type,
        "path": path,
        "entity": entity,
        "references": outbound,
        "referenced_by": referenced_by,
    }
