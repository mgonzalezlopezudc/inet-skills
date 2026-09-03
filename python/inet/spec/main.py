"""Command-line interface for non-authoritative feature manifests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from .validator import load_feature, trace_feature, validate_feature
except ImportError:
    from validator import load_feature, trace_feature, validate_feature


def _feature_path(value: str) -> Path:
    path = Path(value)
    return path / "feature.yaml" if path.is_dir() else path


def _common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--feature",
        default=".",
        help="feature.yaml or its containing directory (default: current directory)",
    )
    parser.add_argument("--corpus", type=Path, help="standards corpus format-2 directory")
    parser.add_argument("--inet-root", type=Path, help="INET checkout used to resolve code and test targets")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate and trace non-authoritative protocol feature manifests."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="validate one feature manifest")
    _common_options(validate_parser)
    trace_parser = subparsers.add_parser("trace", help="trace one stable semantic id")
    trace_parser.add_argument("identifier")
    _common_options(trace_parser)
    return parser


def _print_validation(path: Path, result, json_output: bool) -> None:
    payload = {"feature": str(path), **result.to_dict()}
    if json_output:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return
    print(f"{'valid' if result.valid else 'invalid'}: {path}")
    for warning in result.warnings:
        print(f"warning: {warning}")
    for error in result.errors:
        print(f"error: {error}")


def main(argv=None) -> int:
    args = create_parser().parse_args(argv)
    path = _feature_path(args.feature)
    try:
        feature = load_feature(path)
        result = validate_feature(feature, corpus_root=args.corpus, inet_root=args.inet_root)
        if args.command == "validate":
            _print_validation(path, result, args.json)
            return 0 if result.valid else 1
        if not result.valid:
            _print_validation(path, result, args.json)
            return 1
        trace = trace_feature(feature, args.identifier)
        payload = {
            "feature": str(path),
            "warnings": result.warnings,
            "trace": trace,
        }
        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(f"{trace['entity_type']} {trace['id']} at {trace['path']}")
            print(json.dumps(trace["entity"], indent=2, ensure_ascii=False))
            print("references: " + (", ".join(trace["references"]) or "none"))
            print("referenced-by: " + (", ".join(trace["referenced_by"]) or "none"))
            for warning in result.warnings:
                print(f"warning: {warning}")
        return 0
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
