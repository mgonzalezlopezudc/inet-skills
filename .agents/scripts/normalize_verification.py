#!/usr/bin/env python3
"""Normalize unit/module, fingerprint, and opp_repl output into schema v1 envelopes."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import jsonschema


ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
COUNT_PATTERNS = (
    re.compile(r"\bRan\s+(\d+)\s+tests?\b", re.IGNORECASE),
    re.compile(r"\bSelected\s+(\d+)\s+(?:test|case)s?\b", re.IGNORECASE),
    re.compile(r"\b(\d+)\s+TOTAL\b", re.IGNORECASE),
)
RESULT_COUNT_RE = re.compile(
    r"\b(\d+)\s+(PASS|FAIL(?:ED)?|ERROR|SKIP|CANCEL|KEEP|INSERT|UPDATE)\b"
    r"(?:\s+\((expected|unexpected)\))?",
    re.IGNORECASE,
)
SINGLE_RESULT_RE = re.compile(
    r"(?i)\bresult:\s*"
    r"(PASS|FAIL(?:ED)?|ERROR|KEEP|INSERT|UPDATE)\b"
    r"(?:\s+\((expected|unexpected)\))?"
)
ZERO_PATTERNS = (
    re.compile(r"\bno tests? (?:selected|matched|found)\b", re.IGNORECASE),
    re.compile(r"\b0 tests?\b", re.IGNORECASE),
    re.compile(r"\b(?:testing|tested|updating)\b[^\n]*:\s*empty\b", re.IGNORECASE),
    re.compile(r"\bEmpty\s+[^\n]*\s+result\b", re.IGNORECASE),
)
BUILD_ERROR_PATTERNS = (
    re.compile(r"\b(?:fatal )?error:", re.IGNORECASE),
    re.compile(r"\bundefined reference\b", re.IGNORECASE),
    re.compile(r"\bcompilation terminated\b", re.IGNORECASE),
    re.compile(r"\bmake(?:\[\d+\])?: \*\*\*", re.IGNORECASE),
    re.compile(r"\bbuild failed\b", re.IGNORECASE),
)
ASSERTION_PATTERNS = (
    re.compile(r"\bassert(?:ion)?(?: failed| failure)?\b", re.IGNORECASE),
    re.compile(r"\bexpected\b.*\b(?:actual|got|but)\b", re.IGNORECASE),
)
MISMATCH_PATTERNS = (
    re.compile(r"\bfingerprint mismatch\b", re.IGNORECASE),
    re.compile(r"\b(?:DIVERGENT|DIFFERENT|UPDATE|INSERT)\b", re.IGNORECASE),
    re.compile(r"\bunexpected\b", re.IGNORECASE),
)
RUNNER_ERROR_PATTERNS = (
    re.compile(r"\bERROR\b"),
    re.compile(r"\bnon-zero exit code\b", re.IGNORECASE),
    re.compile(r"\bmalformed\b", re.IGNORECASE),
)
FAIL_PATTERNS = (
    re.compile(r"\bFAILED?\b", re.IGNORECASE),
    re.compile(r"\bfailures?\s*[=:]", re.IGNORECASE),
)
PASS_PATTERNS = (
    re.compile(r"^OK$", re.MULTILINE),
    re.compile(r"\bPASS(?:ED)?\b", re.IGNORECASE),
    re.compile(r"\bKEEP\b"),
)


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text).replace("\r\n", "\n")


def parse_cases(text: str) -> int | None:
    values: list[int] = []
    for pattern in COUNT_PATTERNS:
        values.extend(int(match.group(1)) for match in pattern.finditer(text))
    if values:
        return values[-1]

    result_lines = [line for line in text.splitlines() if RESULT_COUNT_RE.search(line)]
    if result_lines:
        counts = RESULT_COUNT_RE.findall(result_lines[-1])
        total = sum(
            int(count)
            for count, result, _ in counts
            if normalize_result_name(result) not in {"SKIP", "CANCEL"}
        )
        return total
    if SINGLE_RESULT_RE.search(text):
        return 1
    if any(pattern.search(text) for pattern in ZERO_PATTERNS):
        return 0
    return None


def normalize_result_name(result: str) -> str:
    return "FAIL" if result.upper() == "FAILED" else result.upper()


def result_counts(text: str) -> dict[tuple[str, str | None], int]:
    lines = [line for line in text.splitlines() if RESULT_COUNT_RE.search(line)]
    if not lines:
        return {}
    counts: dict[tuple[str, str | None], int] = {}
    for count, result, expectation in RESULT_COUNT_RE.findall(lines[-1]):
        key = (normalize_result_name(result), expectation.lower() or None)
        counts[key] = counts.get(key, 0) + int(count)
    return counts


def single_result(text: str) -> tuple[str, str | None] | None:
    matches = list(SINGLE_RESULT_RE.finditer(text))
    if not matches:
        return None
    result, expectation = matches[-1].groups()
    return normalize_result_name(result), expectation.lower() if expectation else None


def first_failure(text: str) -> dict[str, Any] | None:
    classified = (
        ("build", BUILD_ERROR_PATTERNS),
        ("assertion", ASSERTION_PATTERNS),
        ("mismatch", MISMATCH_PATTERNS),
        ("runner", RUNNER_ERROR_PATTERNS),
    )
    candidates: list[tuple[int, int, str, str]] = []
    lines = text.splitlines()
    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        for priority, (kind, patterns) in enumerate(classified):
            if any(pattern.search(stripped) for pattern in patterns):
                candidates.append((line_number, priority, kind, stripped[:500]))
                break
    if not candidates:
        return None
    line_number, _, kind, summary = min(candidates)
    return {"kind": kind, "summary": summary, "source_line": line_number}


def detect_changed_result(text: str, runner: str) -> bool | None:
    if runner not in {"fingerprint", "opp_repl"}:
        return None
    if re.search(r"\b(?:UPDATE|INSERT|DIVERGENT|DIFFERENT|fingerprint mismatch)\b", text, re.IGNORECASE):
        return True
    if re.search(r"\bKEEP\b|\bPASS\b", text):
        return False
    return None


def classify_status(text: str, runner: str, exit_code: int | None, cases: int | None) -> str:
    counts = result_counts(text)
    single = single_result(text)
    if cases == 0:
        return "NOT_RUN"
    if "Test results equals to expected results" in text:
        return "PASS" if exit_code in (None, 0) else "ERROR"
    if "Test results differ from expected results" in text:
        if re.search(r"\bERROR\b(?!\s*\(expected\))", text):
            return "ERROR"
        return "FAIL"
    if runner in {"fingerprint", "opp_repl"} and (
        any(
            counts.get((result, expectation), 0)
            for result in {"UPDATE", "INSERT"}
            for expectation in {None, "expected", "unexpected"}
        )
        or (single is not None and single[0] in {"UPDATE", "INSERT"})
        or re.search(r"\b(?:DIVERGENT|DIFFERENT)\b", text)
    ):
        return "INCONCLUSIVE"
    if counts:
        if counts.get(("ERROR", "unexpected"), 0):
            return "ERROR"
        if any(
            counts.get((result, "unexpected"), 0)
            for result in {"PASS", "FAIL", "SKIP", "CANCEL"}
        ):
            return "FAIL"
        if all(
            expectation == "expected" or result in {"PASS", "KEEP"}
            for result, expectation in counts
        ):
            return "PASS" if exit_code in (None, 0) else "ERROR"
        if counts.get(("ERROR", None), 0):
            return "ERROR"
        if counts.get(("FAIL", None), 0):
            return "FAIL"
    if single is not None:
        result, expectation = single
        if expectation == "expected":
            return "PASS"
        if expectation == "unexpected":
            return "ERROR" if result == "ERROR" else "FAIL"
        if result == "ERROR":
            return "ERROR"
        if result == "FAIL":
            return "FAIL"
        if result in {"PASS", "KEEP"}:
            return "PASS" if exit_code in (None, 0) else "ERROR"
    if any(pattern.search(text) for pattern in BUILD_ERROR_PATTERNS):
        return "ERROR"
    if any(pattern.search(text) for pattern in RUNNER_ERROR_PATTERNS):
        return "ERROR"
    if any(pattern.search(text) for pattern in FAIL_PATTERNS):
        return "FAIL"
    if exit_code not in (None, 0):
        return "ERROR"
    if cases is not None and cases > 0 and any(pattern.search(text) for pattern in PASS_PATTERNS):
        return "PASS"
    return "INCONCLUSIVE"


def normalize(
    *,
    text: str,
    runner: str,
    command: str,
    working_directory: str,
    build_mode: str | None,
    selector: str | None,
    configuration: str | None,
    run: int | str | None,
    seed: int | None,
    exit_code: int | None,
    artifacts: list[str],
    flaky: bool,
    not_run_reason: str | None = None,
    changed_result_observed: bool | None = None,
    changed_result_expected: bool | None = None,
    changed_result_approved: bool | None = None,
) -> dict[str, Any]:
    if runner not in {"unit", "module", "fingerprint", "opp_repl"}:
        raise ValueError(f"unsupported runner: {runner}")
    clean = strip_ansi(text)
    parsed_cases = parse_cases(clean)
    cases = parsed_cases
    status = "NOT_RUN" if not_run_reason else classify_status(clean, runner, exit_code, cases)
    if status == "NOT_RUN" and not_run_reason is None:
        not_run_reason = "zero cases selected by runner"
    failure = first_failure(clean) if status in {"FAIL", "ERROR"} else None
    observed = (
        changed_result_observed
        if changed_result_observed is not None
        else detect_changed_result(clean, runner)
    )
    return {
        "schema_version": 1,
        "command": command,
        "working_directory": working_directory,
        "build_mode": build_mode,
        "runner": runner,
        "selector": selector,
        "configuration": configuration,
        "run": run,
        "seed": seed,
        "cases_executed": cases,
        "status": status,
        "exit_code": exit_code,
        "not_run_reason": not_run_reason,
        "first_causal_failure": failure,
        "artifacts": list(dict.fromkeys(artifacts)),
        "flaky": flaky,
        "changed_result": {
            "observed": observed,
            "expected": changed_result_expected,
            "approved": changed_result_approved,
        },
        "adapter": {"name": "normalize_verification", "version": 1},
    }


def optional_bool(value: str) -> bool | None:
    return {"true": True, "false": False, "unknown": None}[value]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner", required=True, choices=["unit", "module", "fingerprint", "opp_repl"])
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--command", required=True)
    parser.add_argument("--working-directory", required=True)
    parser.add_argument("--build-mode")
    parser.add_argument("--selector")
    parser.add_argument("--configuration")
    parser.add_argument("--run", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--exit-code", type=int)
    parser.add_argument("--artifact", action="append", default=[])
    parser.add_argument("--flaky", action="store_true")
    parser.add_argument(
        "--not-run-reason",
        help="explicit missing capability or selection reason that makes the result NOT_RUN",
    )
    parser.add_argument("--changed-result-observed", choices=["true", "false", "unknown"])
    parser.add_argument("--changed-result-expected", choices=["true", "false", "unknown"])
    parser.add_argument("--changed-result-approved", choices=["true", "false", "unknown"])
    parser.add_argument("--schema", type=Path, help="schema path; defaults to repository schema v1")
    parser.add_argument("--output", type=Path, help="write JSON here instead of stdout")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    result = normalize(
        text=args.input.read_text(encoding="utf-8", errors="replace"),
        runner=args.runner,
        command=args.command,
        working_directory=args.working_directory,
        build_mode=args.build_mode,
        selector=args.selector,
        configuration=args.configuration,
        run=args.run,
        seed=args.seed,
        exit_code=args.exit_code,
        artifacts=args.artifact,
        flaky=args.flaky,
        not_run_reason=args.not_run_reason,
        changed_result_observed=(
            optional_bool(args.changed_result_observed)
            if args.changed_result_observed is not None
            else None
        ),
        changed_result_expected=(
            optional_bool(args.changed_result_expected)
            if args.changed_result_expected is not None
            else None
        ),
        changed_result_approved=(
            optional_bool(args.changed_result_approved)
            if args.changed_result_approved is not None
            else None
        ),
    )
    schema_path = args.schema or (
        Path(__file__).resolve().parents[1]
        / "schemas"
        / "verification-result-v1.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(result, schema)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    else:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
