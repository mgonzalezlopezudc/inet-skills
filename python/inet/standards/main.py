"""Command-line interface for the canonical IEEE 802.11 corpus."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from . import processor
    from .model import NodeKind
except ImportError:
    import processor
    from model import NodeKind


STRUCTURAL_KINDS = tuple(kind.value for kind in NodeKind)


def add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--standards-dir",
        default=str(processor.DEFAULT_STANDARDS_DIR),
        help="directory containing source PDFs",
    )
    parser.add_argument(
        "--output",
        default=str(processor.DEFAULT_OUTPUT_DIR),
        help="generated corpus directory",
    )


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and navigate a canonical IEEE 802.11 standards corpus."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser(
        "build", help="atomically build canonical text, relations, and search index"
    )
    add_common_options(build_parser)
    build_parser.add_argument(
        "--pdf", action="append", default=None, help="reviewed PDF to process; repeatable"
    )
    build_parser.add_argument(
        "--pages", help="partial single-document PDF pages, e.g. 1-5,10"
    )
    build_parser.add_argument("--force", action="store_true")

    status_parser = subparsers.add_parser(
        "status", help="report corpus compatibility and freshness"
    )
    add_common_options(status_parser)
    status_parser.add_argument("--pdf", action="append", default=None)
    status_parser.add_argument("--json", action="store_true")

    lint_parser = subparsers.add_parser("lint", help="report corpus diagnostics")
    add_common_options(lint_parser)
    lint_parser.add_argument("--document")
    lint_parser.add_argument(
        "--minimum-severity", choices=("info", "warning", "error"), default="warning"
    )
    lint_parser.add_argument("-n", "--limit", type=int, default=100)
    lint_parser.add_argument("--json", action="store_true")

    get_parser = subparsers.add_parser(
        "get", help="retrieve an exact clause, table, figure, definition, node id, or source span"
    )
    add_common_options(get_parser)
    get_parser.add_argument(
        "target", help="node kind, canonical node id, or document@start:end locator"
    )
    get_parser.add_argument("label", nargs="?", help="exact label after a node kind")
    get_parser.add_argument("--document")
    get_parser.add_argument("--children", action="store_true")
    get_parser.add_argument("--ancestors", action="store_true")
    get_parser.add_argument("--context", type=int, default=0, metavar="CHARACTERS")
    get_parser.add_argument("--json", action="store_true")

    search_parser = subparsers.add_parser("search", help="search canonical structural nodes")
    add_common_options(search_parser)
    search_parser.add_argument("query")
    search_parser.add_argument("-n", "--limit", type=int, default=10)
    search_parser.add_argument("--document")
    search_parser.add_argument("--kind", choices=STRUCTURAL_KINDS)
    search_parser.add_argument("--json", action="store_true")

    for command, help_text in (
        ("refs", "list outgoing cross-references for an exact node"),
        (
            "referenced-by",
            "list resolved cross-references that target an exact node",
        ),
    ):
        reference_parser = subparsers.add_parser(command, help=help_text)
        add_common_options(reference_parser)
        reference_parser.add_argument(
            "target", help="node kind or canonical node id"
        )
        reference_parser.add_argument(
            "label", nargs="?", help="exact label after a node kind"
        )
        reference_parser.add_argument("--document")
        reference_parser.add_argument("-n", "--limit", type=int, default=100)
        reference_parser.add_argument("--json", action="store_true")

    define_parser = subparsers.add_parser(
        "define", help="retrieve the exact definition of a term"
    )
    add_common_options(define_parser)
    define_parser.add_argument("term")
    define_parser.add_argument("--document")
    define_parser.add_argument("--json", action="store_true")
    return parser


def _pages(item: dict) -> str:
    start, end = item["page_start"], item["page_end"]
    return f"p{start}" if start == end else f"pp{start}-{end}"


def print_build_result(result: dict) -> None:
    print(f"{result['status']}: {result['output_dir']}")
    for document in result["documents"]:
        extracted = document.get("extracted_pdf_pages")
        pages = len(extracted) if extracted is not None else document["pdf_page_count"]
        print(
            f"{document['document_id']}: pages={pages} "
            f"nodes={document.get('node_count', '?')} "
            f"occurrences={document.get('occurrence_count', '?')} "
            f"references={document.get('reference_count', '?')} "
            f"sha256={document['source_sha256'][:12]}"
        )


def print_status(result: dict) -> None:
    print(
        f"corpus={result['corpus_state']} format={result['format']}/"
        f"{result['format_version']} extractor={result['extractor_state']} "
        f"output={result['output_dir']}"
    )
    if result["corpus_error"]:
        print(f"corpus_error: {result['corpus_error']}")
    for document in result["documents"]:
        print(
            f"{document['state']:8} {document['document_id']:20} "
            f"pages={document['pdf_page_count']} sha256={document['source_sha256'][:12]}"
        )
    for error in result["source_errors"]:
        print(f"source_error {error['source_path']}: {error['error']}")


def print_search_results(rows: list[dict]) -> None:
    for row in rows:
        print(
            f"{row['node_id']}  {_pages(row)}  "
            f"{row['kind']} {row['label']} — {row['title']}"
        )
        if row["snippet"]:
            print(f"  {row['snippet']}")


def print_get_result(item: dict) -> None:
    if item.get("type") == "source-span":
        print(f"{item['locator']}")
    else:
        print(f"{item['node_id']}  {_pages(item)}  {item['title']}")
        for span in item["source_spans"]:
            print(f"  source: {span['locator']} pp{span['pdf_page_start']}-{span['pdf_page_end']}")
    print()
    print(item["text"].rstrip())


def print_lint_result(result: dict) -> None:
    print(f"diagnostics={result['total']} returned={len(result['findings'])}")
    for severity, codes in result["counts"].items():
        print(f"{severity}: " + ", ".join(f"{code}={count}" for code, count in codes.items()))
    for finding in result["findings"]:
        location = ""
        if finding["pdf_page_start"] is not None:
            location = f" p{finding['pdf_page_start']}"
        print(
            f"{finding['severity']} {finding['document_id']}{location} "
            f"{finding['code']}: {finding['message']}"
        )


def print_reference_result(result: dict) -> None:
    print(
        f"{result['direction']} references for {result['node']['node_id']}: "
        f"total={result['total']} returned={len(result['references'])}"
    )
    for reference in result["references"]:
        target = reference["target_node_id"] or (
            f"{reference['target_kind']} {reference['target_label']}"
        )
        reason = f" ({reference['reason']})" if reference["reason"] else ""
        print(
            f"{reference['status']:10} {reference['raw_text']!r} -> {target} "
            f"at {reference['source_span']['locator']}{reason}"
        )


def _get_arguments(args: argparse.Namespace) -> dict:
    common = {
        "output_dir": Path(args.output),
        "document_id": args.document,
        "include_children": args.children,
        "include_ancestors": args.ancestors,
        "context_characters": args.context,
    }
    if args.target in STRUCTURAL_KINDS:
        if args.label is None:
            raise ValueError(f"{args.target} lookup requires an exact label")
        return {**common, "kind": args.target, "label": args.label}
    if args.label is not None:
        raise ValueError("a second argument is only valid after a structural node kind")
    if "@" in args.target:
        return {**common, "source_span": args.target}
    return {**common, "node_id": args.target}


def _reference_arguments(args: argparse.Namespace) -> dict:
    common = {
        "output_dir": Path(args.output),
        "document_id": args.document,
        "limit": args.limit,
    }
    if args.target in STRUCTURAL_KINDS:
        if args.label is None:
            raise ValueError(f"{args.target} lookup requires an exact label")
        return {**common, "kind": args.target, "label": args.label}
    if args.label is not None:
        raise ValueError("a second argument is only valid after a structural node kind")
    return {**common, "node_id": args.target}


def print_json_or(value, json_output: bool, plain_printer) -> None:
    if json_output:
        print(json.dumps(value, indent=2, ensure_ascii=False))
    else:
        plain_printer(value)


def main(argv=None) -> int:
    args = create_parser().parse_args(argv)
    try:
        if args.command == "build":
            result = processor.build(
                output_dir=Path(args.output),
                standards_dir=Path(args.standards_dir),
                pdfs=args.pdf,
                page_spec=args.pages,
                force=args.force,
            )
            print_build_result(result)
        elif args.command == "status":
            result = processor.status(
                output_dir=Path(args.output),
                standards_dir=Path(args.standards_dir),
                pdfs=args.pdf,
            )
            print_json_or(result, args.json, print_status)
        elif args.command == "lint":
            result = processor.lint(
                output_dir=Path(args.output),
                document_id=args.document,
                minimum_severity=args.minimum_severity,
                limit=args.limit,
            )
            print_json_or(result, args.json, print_lint_result)
        elif args.command == "get":
            result = processor.get(**_get_arguments(args))
            print_json_or(result, args.json, print_get_result)
        elif args.command == "search":
            rows = processor.search(
                output_dir=Path(args.output),
                query=args.query,
                limit=args.limit,
                document_id=args.document,
                kind=args.kind,
            )
            print_json_or(rows, args.json, print_search_results)
        elif args.command == "refs":
            result = processor.refs(**_reference_arguments(args))
            print_json_or(result, args.json, print_reference_result)
        elif args.command == "referenced-by":
            result = processor.referenced_by(**_reference_arguments(args))
            print_json_or(result, args.json, print_reference_result)
        elif args.command == "define":
            result = processor.define(
                output_dir=Path(args.output),
                term=args.term,
                document_id=args.document,
            )
            print_json_or(result, args.json, print_get_result)
        return 0
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
