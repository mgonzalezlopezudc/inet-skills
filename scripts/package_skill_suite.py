#!/usr/bin/env python3
"""Assemble one declared skill-suite deployment profile without cache artifacts."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from validate_skill_suite import Validation, expand_profile, load_yaml, validate_deployment_artifacts


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, help="skill repository root")
    parser.add_argument("--project-root", type=Path, help="active INET checkout for profile gates")
    return parser.parse_args(argv)


def profile_requirements(
    name: str, profiles: dict, validation: Validation, stack: tuple[str, ...] = ()
) -> set[str]:
    if name in stack:
        validation.error(f"deployment profile inheritance cycle: {' -> '.join(stack + (name,))}")
        return set()
    profile = profiles.get(name)
    if not isinstance(profile, dict):
        validation.error(f"unknown or invalid deployment profile: {name}")
        return set()
    requirements = set(profile.get("activation_requires", {}).get("all_files", []))
    for parent in profile.get("extends", []):
        requirements.update(profile_requirements(parent, profiles, validation, stack + (name,)))
    return requirements


def package_profile(
    *, root: Path, profile_name: str, output: Path, project_root: Path | None
) -> tuple[list[str], list[str]]:
    manifest = load_yaml(root / ".agents" / "skill-suite.yaml")
    validation = Validation()
    profiles = manifest.get("profiles", {})
    skills = sorted(expand_profile(profile_name, profiles, validation))
    requirements = sorted(profile_requirements(profile_name, profiles, validation))
    if validation.errors:
        return [], validation.errors

    if requirements and project_root is None:
        validation.error(
            f"profile {profile_name} has checkout capability gates; --project-root is required"
        )
    elif project_root is not None:
        for relative in requirements:
            path = project_root / relative
            if not path.exists():
                validation.error(f"profile {profile_name} unavailable; missing {path}")
    if output.exists():
        validation.error(f"output already exists; choose a new directory: {output}")
    if validation.errors:
        return [], validation.errors

    (output / ".agents" / "skills").mkdir(parents=True)
    for skill in skills:
        source = root / ".agents" / "skills" / skill
        destination = output / ".agents" / "skills" / skill
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )

    shared_paths = sorted(
        {
            relative
            for skill in skills
            for relative in manifest["skills"][skill].get("deployment_files", [])
        }
    )
    for relative in shared_paths:
        source = root / relative
        destination = output / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(
                source,
                destination,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        else:
            shutil.copy2(source, destination)

    shutil.copytree(root / ".agents" / "schemas", output / ".agents" / "schemas")
    (output / ".agents" / "scripts").mkdir()
    shutil.copy2(
        root / ".agents" / "scripts" / "normalize_verification.py",
        output / ".agents" / "scripts" / "normalize_verification.py",
    )
    (output / ".agents" / "deployment.json").write_text(
        json.dumps(
            {"manifest_version": manifest["version"], "profile": profile_name, "skills": skills},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    validate_deployment_artifacts(output, validation)
    return skills, validation.errors


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    root = (args.root or Path(__file__).resolve().parents[1]).resolve()
    output = args.output.resolve()
    project_root = args.project_root.resolve() if args.project_root else None
    skills, errors = package_profile(
        root=root,
        profile_name=args.profile,
        output=output,
        project_root=project_root,
    )
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"packaged profile {args.profile}: {len(skills)} skills -> {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
