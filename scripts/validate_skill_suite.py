#!/usr/bin/env python3
"""Validate the INET skill suite manifest, metadata, references, and fixtures."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote

import yaml


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
REQUIRED_WORKFLOW_AREAS = {
    "authoring",
    "review",
    "debugging",
    "results",
    "regression",
    "branch-cleanup",
    "branch-rebase",
}
GENERATED_KEYS = ("display_name", "short_description", "default_prompt")
CHECKOUT_REQUIREMENT_KEYS = ("required", "optional")


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def is_safe_relative_path(value: str) -> bool:
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def load_yaml(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read YAML {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected a YAML mapping in {path}")
    return value


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(f"missing YAML frontmatter in {path}")
    try:
        value = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML frontmatter in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"frontmatter must be a mapping in {path}")
    return value


def render_metadata(metadata: dict) -> str:
    lines = ["interface:"]
    for key in GENERATED_KEYS:
        value = metadata.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"metadata.{key} must be a non-empty string")
        lines.append(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def generated_metadata_paths(root: Path, manifest: dict, skill: str) -> list[Path]:
    targets = manifest.get("generated_metadata", {}).get("targets", [])
    return [root / ".agents" / "skills" / skill / target for target in targets]


def validate_project_guidance(root: Path, manifest: dict, validation: Validation) -> None:
    """Validate the one stable project input without asserting internal document details."""
    if "project_compatibility" in manifest:
        validation.error(
            "manifest.project_compatibility is obsolete; use project_guidance.entrypoint"
        )
    guidance = manifest.get("project_guidance")
    if not isinstance(guidance, dict):
        validation.error("manifest.project_guidance must be a mapping")
        return
    entrypoint = guidance.get("entrypoint")
    if entrypoint != "doc/project/README.md":
        validation.error(
            "manifest.project_guidance.entrypoint must be the stable "
            "doc/project/README.md entry point"
        )
    resources = manifest.get("shared_resources", [])
    if not isinstance(resources, list):
        validation.error("manifest.shared_resources must be a list")
        return
    for relative in resources:
        if not isinstance(relative, str) or not relative or not is_safe_relative_path(relative):
            validation.error(f"shared resource path is invalid: {relative!r}")
        elif not (root / relative).exists():
            validation.error(f"shared resource does not resolve: {relative!r}")


def validate_frontmatter_and_metadata(
    root: Path, manifest: dict, validation: Validation, *, write_metadata: bool
) -> None:
    declared = manifest.get("skills")
    if not isinstance(declared, dict) or not declared:
        validation.error("manifest.skills must be a non-empty mapping")
        return

    skills_root = root / ".agents" / "skills"
    if not skills_root.is_dir():
        validation.error(f"missing skills directory: {skills_root.relative_to(root)}")
        return
    actual = {path.name for path in skills_root.iterdir() if path.is_dir()}
    declared_names = set(declared)
    for name in sorted(actual - declared_names):
        validation.error(f"orphan skill directory not declared in manifest: {name}")
    for name in sorted(declared_names - actual):
        validation.error(f"manifest skill has no directory: {name}")

    for name, spec in sorted(declared.items()):
        if not isinstance(spec, dict):
            validation.error(f"skills.{name} must be a mapping")
            continue
        skill_file = skills_root / name / "SKILL.md"
        if not skill_file.is_file():
            validation.error(f"missing skill entrypoint: {skill_file.relative_to(root)}")
            continue
        try:
            frontmatter = parse_frontmatter(skill_file)
        except ValueError as exc:
            validation.error(str(exc))
            continue
        if frontmatter.get("name") != name:
            validation.error(
                f"{skill_file.relative_to(root)} frontmatter name is "
                f"{frontmatter.get('name')!r}, expected {name!r}"
            )
        description = frontmatter.get("description")
        if not isinstance(description, str) or not description.strip():
            validation.error(f"{skill_file.relative_to(root)} has no non-empty description")
        elif len(description) > 600:
            validation.warn(f"{skill_file.relative_to(root)} description is unusually long")

        dependencies = spec.get("dependencies")
        tools = spec.get("required_tools")
        optional_tools = spec.get("optional_tools", [])
        checkout = spec.get("checkout_requirements")
        deployment_files = spec.get("deployment_files", [])
        if not isinstance(dependencies, list):
            validation.error(f"skills.{name}.dependencies must be a list")
        elif any(not isinstance(item, str) or not item for item in dependencies):
            validation.error(f"skills.{name}.dependencies must contain non-empty strings")
        if not isinstance(tools, list):
            validation.error(f"skills.{name}.required_tools must be a list")
        elif any(not isinstance(item, str) or not item for item in tools):
            validation.error(f"skills.{name}.required_tools must contain non-empty strings")
        if not isinstance(optional_tools, list):
            validation.error(f"skills.{name}.optional_tools must be a list")
        elif any(not isinstance(item, str) or not item for item in optional_tools):
            validation.error(f"skills.{name}.optional_tools must contain non-empty strings")
        if "required_checkout_files" in spec:
            validation.error(
                f"skills.{name}.required_checkout_files is obsolete; use "
                "checkout_requirements.required/optional"
            )
        if not isinstance(checkout, dict):
            validation.error(f"skills.{name}.checkout_requirements must be a mapping")
        else:
            unknown = set(checkout) - set(CHECKOUT_REQUIREMENT_KEYS)
            if unknown:
                validation.error(
                    f"skills.{name}.checkout_requirements has unknown keys: {sorted(unknown)}"
                )
            for key in CHECKOUT_REQUIREMENT_KEYS:
                values = checkout.get(key)
                if not isinstance(values, list):
                    validation.error(
                        f"skills.{name}.checkout_requirements.{key} must be a list"
                    )
                elif any(
                    not isinstance(item, str) or not item or not is_safe_relative_path(item)
                    for item in values
                ):
                    validation.error(
                        f"skills.{name}.checkout_requirements.{key} must contain safe relative paths"
                    )
        if not isinstance(deployment_files, list):
            validation.error(f"skills.{name}.deployment_files must be a list when present")
        else:
            for relative in deployment_files:
                if (
                    not isinstance(relative, str)
                    or not is_safe_relative_path(relative)
                    or not (root / relative).exists()
                ):
                    validation.error(
                        f"skills.{name}.deployment_files does not resolve: {relative!r}"
                    )

        try:
            expected = render_metadata(spec.get("metadata", {}))
        except ValueError as exc:
            validation.error(f"skills.{name}.{exc}")
            continue
        for target in generated_metadata_paths(root, manifest, name):
            if write_metadata:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(expected, encoding="utf-8")
            elif not target.is_file():
                validation.error(f"missing generated metadata: {target.relative_to(root)}")
            elif target.read_text(encoding="utf-8") != expected:
                validation.error(
                    f"generated metadata drift: {target.relative_to(root)} "
                    "(run with --write-metadata)"
                )


def markdown_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
    target = unquote(target).split("#", 1)[0]
    if not target or target.startswith(("http://", "https://", "mailto:")):
        return None
    candidate = Path(target)
    if candidate.is_absolute():
        return candidate.resolve()
    return (source.parent / candidate).resolve()


def validate_references(root: Path, manifest: dict, validation: Validation) -> None:
    skills_root = root / ".agents" / "skills"
    markdown_files = sorted(skills_root.rglob("*.md"))
    inbound: defaultdict[Path, list[Path]] = defaultdict(list)
    inferred_dependencies: defaultdict[str, set[str]] = defaultdict(set)
    skill_names = set(manifest.get("skills", {}))

    for source in markdown_files:
        source_skill = source.relative_to(skills_root).parts[0]
        text = source.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = markdown_target(source, raw_target)
            if target is None:
                continue
            if not target.exists():
                validation.error(
                    f"broken Markdown reference: {source.relative_to(root)} -> {raw_target}"
                )
                continue
            inbound[target].append(source)
            try:
                target_parts = target.relative_to(skills_root.resolve()).parts
            except ValueError:
                continue
            if target_parts and target_parts[0] in skill_names and target_parts[0] != source_skill:
                inferred_dependencies[source_skill].add(target_parts[0])

    exceptions = {}
    for item in manifest.get("reference_exceptions", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            validation.error("every reference_exceptions item needs path and reason")
            continue
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            validation.error(f"reference exception has no reason: {item.get('path')}")
        exceptions[(root / item["path"]).resolve()] = item.get("reason", "")

    reference_files = {path.resolve() for path in skills_root.glob("*/references/**/*") if path.is_file()}
    orphans = reference_files - set(inbound)
    for path in sorted(orphans):
        if path not in exceptions:
            validation.error(f"orphan reference with no inbound Markdown link: {path.relative_to(root)}")
    for path in sorted(exceptions):
        if not path.exists():
            validation.error(f"reference exception points to missing file: {path.relative_to(root)}")
        elif path not in orphans:
            validation.error(f"stale reference exception is no longer orphaned: {path.relative_to(root)}")

    for skill, inferred in sorted(inferred_dependencies.items()):
        declared = set(manifest["skills"][skill].get("dependencies", []))
        for missing in sorted(inferred - declared):
            validation.error(
                f"skills.{skill}.dependencies omits linked skill {missing}"
            )


def expand_profile(name: str, profiles: dict, validation: Validation, stack: tuple[str, ...] = ()) -> set[str]:
    if name in stack:
        validation.error(f"deployment profile inheritance cycle: {' -> '.join(stack + (name,))}")
        return set()
    spec = profiles.get(name)
    if not isinstance(spec, dict):
        validation.error(f"unknown or invalid deployment profile: {name}")
        return set()
    result = set(spec.get("skills", []))
    for parent in spec.get("extends", []):
        result.update(expand_profile(parent, profiles, validation, stack + (name,)))
    return result


def validate_dependency_cycles(manifest: dict, validation: Validation) -> None:
    """Reject dependency cycles so a package cannot require an unresolvable skill graph."""
    skills = manifest.get("skills", {})
    graph = {
        name: [
            dependency
            for dependency in spec.get("dependencies", [])
            if isinstance(dependency, str) and dependency in skills
        ]
        for name, spec in skills.items()
        if isinstance(spec, dict) and isinstance(spec.get("dependencies", []), list)
    }
    state: dict[str, int] = {}
    stack: list[str] = []
    reported: set[tuple[str, ...]] = set()

    def visit(name: str) -> None:
        state[name] = 1
        stack.append(name)
        for dependency in graph.get(name, []):
            if state.get(dependency, 0) == 0:
                visit(dependency)
            elif state.get(dependency) == 1:
                start = stack.index(dependency)
                cycle = tuple(stack[start:] + [dependency])
                canonical = min(cycle[i:-1] + cycle[:i] + (cycle[i],) for i in range(len(cycle) - 1))
                if canonical not in reported:
                    reported.add(canonical)
                    validation.error(f"skill dependency cycle: {' -> '.join(canonical)}")
        stack.pop()
        state[name] = 2

    for name in sorted(graph):
        if state.get(name, 0) == 0:
            visit(name)


def validate_dependencies_and_profiles(manifest: dict, validation: Validation) -> None:
    skills = manifest.get("skills", {})
    names = set(skills)
    for name, spec in sorted(skills.items()):
        if not isinstance(spec, dict):
            continue
        dependencies = spec.get("dependencies", [])
        duplicates = {item for item in dependencies if dependencies.count(item) > 1}
        if duplicates:
            validation.error(f"skills.{name}.dependencies has duplicates: {sorted(duplicates)}")
        for dependency in dependencies:
            if dependency not in names:
                validation.error(f"skills.{name} has unknown dependency: {dependency}")
            if dependency == name:
                validation.error(f"skills.{name} cannot depend on itself")
        routes_to = spec.get("routes_to", [])
        if not isinstance(routes_to, list):
            validation.error(f"skills.{name}.routes_to must be a list when present")
            continue
        for target in routes_to:
            if target not in names:
                validation.error(f"skills.{name} routes to unknown skill: {target}")
            if target == name:
                validation.error(f"skills.{name} cannot route to itself")

    validate_dependency_cycles(manifest, validation)

    profiles = manifest.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        validation.error("manifest.profiles must be a non-empty mapping")
        return
    for name in sorted(profiles):
        members = expand_profile(name, profiles, validation)
        for unknown in sorted(members - names):
            validation.error(f"profile {name} contains unknown skill: {unknown}")
        for member in sorted(members & names):
            if not isinstance(skills[member], dict):
                continue
            missing = set(skills[member].get("dependencies", [])) - members
            if missing:
                validation.error(
                    f"profile {name} contains {member} without dependencies {sorted(missing)}"
                )


def validate_fixtures(root: Path, manifest: dict, validation: Validation) -> None:
    names = set(manifest.get("skills", {}))
    activation_path = root / "tests" / "skill-suite" / "activation-cases.yaml"
    workflow_path = root / "tests" / "skill-suite" / "workflow-cases.yaml"
    routing_path = root / "tests" / "skill-suite" / "routing-cases.yaml"
    try:
        activation = load_yaml(activation_path).get("cases", [])
        workflows = load_yaml(workflow_path).get("cases", [])
        routing = load_yaml(routing_path).get("cases", [])
    except ValueError as exc:
        validation.error(str(exc))
        return

    ids: set[str] = set()
    positive_coverage: set[str] = set()
    negative_coverage: set[str] = set()
    for case in activation:
        if not isinstance(case, dict):
            validation.error("activation case must be a mapping")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            validation.error("activation case has no id")
            continue
        if case_id in ids:
            validation.error(f"duplicate activation case id: {case_id}")
        ids.add(case_id)
        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            validation.error(f"activation case {case_id} has no prompt")
        expected = set(case.get("expected_skills", []))
        forbidden = set(case.get("forbidden_skills", []))
        if not expected and not forbidden:
            validation.error(f"activation case {case_id} has no assertion")
        for unknown in sorted((expected | forbidden) - names):
            validation.error(f"activation case {case_id} names unknown skill {unknown}")
        positive_coverage.update(expected)
        negative_coverage.update(forbidden)

    for skill in sorted(names - positive_coverage):
        validation.error(f"skill has no positive activation case: {skill}")
    for skill in sorted(names - negative_coverage):
        validation.error(f"skill has no negative activation case: {skill}")

    workflow_ids: set[str] = set()
    areas: set[str] = set()
    for case in workflows:
        if not isinstance(case, dict):
            validation.error("workflow case must be a mapping")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            validation.error("workflow case has no id")
            continue
        if case_id in workflow_ids:
            validation.error(f"duplicate workflow case id: {case_id}")
        workflow_ids.add(case_id)
        areas.add(case.get("area"))
        expected = set(case.get("expected_skills", []))
        for unknown in sorted(expected - names):
            validation.error(f"workflow case {case_id} names unknown skill {unknown}")
        gates = case.get("required_gates")
        if not isinstance(gates, list) or not gates or not all(isinstance(gate, str) for gate in gates):
            validation.error(f"workflow case {case_id} needs semantic required_gates")
    missing_areas = REQUIRED_WORKFLOW_AREAS - areas
    if missing_areas:
        validation.error(f"workflow fixtures omit areas: {sorted(missing_areas)}")

    allowed_paths = {"localized", "mechanical", "semantic", "orchestrated"}
    routing_ids: set[str] = set()
    for case in routing:
        if not isinstance(case, dict):
            validation.error("routing case must be a mapping")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            validation.error("routing case has no id")
            continue
        if case_id in routing_ids:
            validation.error(f"duplicate routing case id: {case_id}")
        routing_ids.add(case_id)
        if case.get("expected_path") not in allowed_paths:
            validation.error(f"routing case {case_id} has invalid expected_path")
        expected = set(case.get("expected_skills", []))
        forbidden = set(case.get("forbidden_skills", []))
        for unknown in sorted((expected | forbidden) - names):
            validation.error(f"routing case {case_id} names unknown skill {unknown}")
        if not case.get("required_gates"):
            validation.error(f"routing case {case_id} has no required_gates")


def conditional_skill_names(manifest: dict) -> set[str]:
    names: set[str] = set()
    for profile in manifest.get("profiles", {}).values():
        if isinstance(profile, dict) and profile.get("activation_requires"):
            names.update(profile.get("skills", []))
    return names


def validate_capabilities(
    root: Path,
    project_root: Path | None,
    manifest: dict,
    validation: Validation,
    *,
    check_tools: bool,
    strict_capabilities: bool,
) -> None:
    def capability_issue(message: str) -> None:
        (validation.error if strict_capabilities else validation.warn)(message)

    if project_root is not None:
        guidance = manifest.get("project_guidance", {})
        entrypoint = guidance.get("entrypoint") if isinstance(guidance, dict) else None
        if isinstance(entrypoint, str):
            path = project_root / entrypoint
            if not path.is_file():
                # Project guidance is a safety boundary. Missing guidance never grants permission
                # for a protected action, even when optional task capabilities are being checked.
                validation.error(f"missing project guidance entrypoint: {path}")

        conditional = conditional_skill_names(manifest)
        for name, spec in manifest.get("skills", {}).items():
            if not isinstance(spec, dict):
                continue
            requirements = spec.get("checkout_requirements", {})
            if not isinstance(requirements, dict):
                continue
            for relative in requirements.get("required", []):
                path = project_root / relative
                if not path.exists():
                    message = f"skill {name} unavailable; missing checkout file {path}"
                    if name in conditional:
                        validation.warn(message)
                    else:
                        capability_issue(message)
            for relative in requirements.get("optional", []):
                path = project_root / relative
                if not path.exists():
                    validation.warn(f"optional capability unavailable for skill {name}: {path}")

        for profile_name, profile in manifest.get("profiles", {}).items():
            requirements = profile.get("activation_requires", {}) if isinstance(profile, dict) else {}
            for relative in requirements.get("all_files", []):
                path = project_root / relative
                if not path.exists():
                    validation.warn(f"profile {profile_name} unavailable; missing {path}")

    if check_tools:
        local_bins = [root / "bin"]
        if project_root is not None:
            local_bins.append(project_root / "bin")
        tools = sorted(
            {
                tool
                for spec in manifest.get("skills", {}).values()
                if isinstance(spec, dict)
                for tool in spec.get("required_tools", [])
            }
        )
        for tool in tools:
            present = shutil.which(tool) is not None or any((base / tool).is_file() for base in local_bins)
            if not present:
                capability_issue(f"required tool is unavailable in PATH or checkout bin/: {tool}")
        optional_tools = sorted(
            {
                tool
                for spec in manifest.get("skills", {}).values()
                if isinstance(spec, dict)
                for tool in spec.get("optional_tools", [])
            }
        )
        for tool in optional_tools:
            present = shutil.which(tool) is not None or any((base / tool).is_file() for base in local_bins)
            if not present:
                validation.warn(f"optional tool is unavailable in PATH or checkout bin/: {tool}")


def validate_deployment_artifacts(path: Path | None, validation: Validation) -> None:
    if path is None:
        return
    if not path.exists():
        validation.error(f"deployment root does not exist: {path}")
        return
    for artifact in path.rglob("*"):
        if artifact.name == "__pycache__" or artifact.suffix == ".pyc":
            validation.error(f"forbidden generated deployment artifact: {artifact}")
    for source in path.rglob("*.md"):
        text = source.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = markdown_target(source, raw_target)
            if target is not None and not target.exists():
                validation.error(
                    f"broken deployed Markdown reference: {source.relative_to(path)} -> {raw_target}"
                )


def validate_verification_support(root: Path, manifest: dict, validation: Validation) -> None:
    support = manifest.get("verification_results")
    if not isinstance(support, dict):
        validation.error("manifest.verification_results must be a mapping")
        return
    for key in ("schema", "adapter", "fixtures"):
        value = support.get(key)
        if not isinstance(value, str) or not (root / value).exists():
            validation.error(f"verification_results.{key} does not resolve: {value!r}")
    runners = support.get("runners")
    if not isinstance(runners, list) or not runners or any(not isinstance(item, str) for item in runners):
        validation.error("verification_results.runners must be a non-empty list of strings")
    required_fixtures = support.get("required_fixtures")
    if not isinstance(required_fixtures, dict):
        validation.error("verification_results.required_fixtures must be a mapping")
    else:
        fixture_root_value = support.get("fixtures")
        fixture_root = root / fixture_root_value if isinstance(fixture_root_value, str) else None
        for runner in runners if isinstance(runners, list) else []:
            fixtures = required_fixtures.get(runner)
            if not isinstance(fixtures, list) or not fixtures:
                validation.error(f"verification_results.required_fixtures.{runner} must be a non-empty list")
                continue
            if fixture_root is None:
                continue
            for fixture in fixtures:
                if not isinstance(fixture, str) or not fixture:
                    validation.error(
                        f"verification_results.required_fixtures.{runner} has invalid fixture: {fixture!r}"
                    )
                elif not (fixture_root / fixture).is_file():
                    validation.error(
                        f"missing verification fixture for {runner}: {fixture_root / fixture}"
                    )
        undeclared = set()
        if fixture_root is not None and fixture_root.is_dir():
            undeclared = {
                path.name for path in fixture_root.iterdir() if path.is_file()
            } - {
                fixture
                for fixtures in required_fixtures.values()
                if isinstance(fixtures, list)
                for fixture in fixtures
                if isinstance(fixture, str)
            }
        for fixture in sorted(undeclared):
            validation.warn(f"verification fixture is not declared in manifest: {fixture}")
    schema_value = support.get("schema")
    if isinstance(schema_value, str) and (root / schema_value).is_file():
        try:
            schema = json.loads((root / schema_value).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            validation.error(f"invalid verification JSON schema: {exc}")
        else:
            runner_enum = schema.get("properties", {}).get("runner", {}).get("enum", [])
            if runner_enum != support.get("runners"):
                validation.error("verification runner list differs between manifest and schema")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, help="skill repository root; defaults from this script")
    parser.add_argument("--project-root", type=Path, help="active INET checkout for capability checks")
    parser.add_argument("--check-tools", action="store_true", help="check required command availability")
    parser.add_argument(
        "--strict-capabilities",
        action="store_true",
        help="make unavailable non-conditional files and tools errors instead of warnings",
    )
    parser.add_argument(
        "--deployment-root",
        type=Path,
        help="reject __pycache__ and *.pyc under an assembled deployment tree",
    )
    parser.add_argument(
        "--write-metadata",
        action="store_true",
        help="regenerate both platform metadata targets from the manifest",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="explicit drift-check mode (the default when --write-metadata is absent)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = (args.root or Path(__file__).resolve().parents[1]).resolve()
    manifest_path = root / ".agents" / "skill-suite.yaml"
    validation = Validation()
    try:
        manifest = load_yaml(manifest_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if manifest.get("version") != 1:
        validation.error("manifest version must be 1")
    validate_project_guidance(root, manifest, validation)
    validate_frontmatter_and_metadata(
        root, manifest, validation, write_metadata=args.write_metadata
    )
    validate_references(root, manifest, validation)
    validate_dependencies_and_profiles(manifest, validation)
    validate_fixtures(root, manifest, validation)
    validate_capabilities(
        root,
        args.project_root.resolve() if args.project_root else None,
        manifest,
        validation,
        check_tools=args.check_tools,
        strict_capabilities=args.strict_capabilities,
    )
    validate_deployment_artifacts(
        args.deployment_root.resolve() if args.deployment_root else None, validation
    )
    validate_verification_support(root, manifest, validation)

    for warning in validation.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for error in validation.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if validation.errors:
        print(
            f"skill-suite validation failed: {len(validation.errors)} error(s), "
            f"{len(validation.warnings)} warning(s)",
            file=sys.stderr,
        )
        return 1
    mode = "generated and validated" if args.write_metadata else "validated"
    print(
        f"skill suite {mode}: {len(manifest.get('skills', {}))} skills, "
        f"{len(validation.warnings)} warning(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
