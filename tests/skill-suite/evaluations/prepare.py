#!/usr/bin/env python3
"""Materialize raw behavioral fixtures in a new isolated directory, without the grading rubric."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new directory outside deployment trees")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    here = Path(__file__).resolve().parent
    for name, content in json.loads((here / "project-files.json").read_text()).items():
        path = args.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    for case in json.loads((here / "cases.json").read_text())["cases"]:
        folder = args.output / "cases" / case["id"]
        folder.mkdir(parents=True)
        for name, content in case["artifacts"].items():
            (folder / name).write_text(content)
        (folder / "TASK.md").write_text(case["request"] + "\n\nSkills to apply: " +
                                       ", ".join(case["skills"]) + "\n")


if __name__ == "__main__":
    main()
