#!/usr/bin/env python3

# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

"""Turn the report of a CI tool into a GitHub job summary.

Each command reads the machine-readable report of one tool and appends a
Markdown section to ``$GITHUB_STEP_SUMMARY`` (to stdout when unset). It only
formats: the tool step has already decided whether the job fails.
"""

import argparse
import hashlib
import json
import os
import sys
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from pathlib import Path
from typing import NotRequired, TypedDict, cast


class RuffLocation(TypedDict):
    row: int
    column: int


class RuffFinding(TypedDict):
    code: str | None
    filename: str
    location: RuffLocation
    message: str


class BanditResult(TypedDict):
    issue_severity: str
    test_id: str
    filename: str
    line_number: int
    issue_text: str


class BanditTotals(TypedDict):
    loc: NotRequired[int]


class BanditMetrics(TypedDict):
    _totals: NotRequired[BanditTotals]


class BanditReport(TypedDict):
    results: list[BanditResult]
    metrics: NotRequired[BanditMetrics]


class Vulnerability(TypedDict):
    id: str
    fix_versions: NotRequired[list[str] | None]


class Dependency(TypedDict):
    name: str
    version: str
    vulns: NotRequired[list[Vulnerability]]


class AuditReport(TypedDict):
    dependencies: list[Dependency]


class Bump(TypedDict):
    current_version: NotRequired[str]
    next_version: NotRequired[str]


class ReleaseReport(TypedDict):
    bumps: NotRequired[dict[str, Bump]]


class JunitTotals(TypedDict):
    tests: int
    failures: int
    errors: int
    skipped: int
    time: float


class Arguments(argparse.Namespace):
    """The parsed command line, typed."""

    command: str = ""
    report: str = ""
    junit: str = ""
    coverage: str | None = None
    title: str = ""
    package: str = ""
    version: str = ""


OK, FAIL, WARN = "✅", "❌", "⚠️"
TAIL_LINES = 40


def load_json(path: str | None) -> object | None:
    """The parsed report, which callers cast to the shape their tool writes."""
    if not (path and Path(path).is_file()):
        return None
    return cast(object, json.loads(Path(path).read_text()))


def read_text(path: str | None) -> str | None:
    return Path(path).read_text() if path and Path(path).is_file() else None


def relative(path: str | Path) -> str:
    """Paths in tool reports are absolute; show them from the workspace root."""
    try:
        return str(Path(path).relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def cell(value: object) -> str:
    """A value that is safe inside a Markdown table cell."""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def table(headers: list[str], rows: Iterable[Iterable[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines += ["| " + " | ".join(cell(value) for value in row) + " |" for row in rows]
    return "\n".join(lines)


def fenced(text: str, limit: int = TAIL_LINES) -> str:
    lines = text.strip().splitlines()
    if len(lines) > limit:
        lines = [f"... {len(lines) - limit} earlier lines omitted", *lines[-limit:]]
    return "```text\n" + "\n".join(lines) + "\n```"


def missing_report(title: str, path: str | None) -> str:
    return f"## {WARN} {title}\n\nNo report was produced (`{path}`): the tool did not run to completion.\n"


def ruff_check(path: str | None) -> str:
    findings = cast("list[RuffFinding] | None", load_json(path))
    if findings is None:
        return missing_report("ruff check", path)
    if not findings:
        return f"## {OK} ruff check\n\nNo lint finding.\n"
    rows = [
        (f["code"], f"{relative(f['filename'])}:{f['location']['row']}", f["message"])
        for f in sorted(findings, key=lambda f: (f["filename"], f["location"]["row"]))
    ]
    return (
        f"## {FAIL} ruff check\n\n{len(findings)} finding(s).\n\n"
        + table(["Rule", "Location", "Message"], rows)
        + "\n"
    )


def ruff_annotations(path: str | None) -> str:
    """Workflow annotations, so findings show inline on the pull request."""
    lines: list[str] = []
    findings = cast("list[RuffFinding]", load_json(path) or [])
    for f in findings:
        location = f["location"]
        title = f["code"] or "ruff"
        message = f["message"].replace("%", "%25").replace("\n", "%0A")
        lines.append(
            f"::error file={relative(f['filename'])},line={location['row']},col={location['column']},title={title}::{message}"
        )
    return "\n".join(lines)


def ruff_format(path: str | None) -> str:
    text = read_text(path)
    if text is None:
        return missing_report("ruff format", path)
    files = [
        line.split(": ", 1)[1] for line in text.splitlines() if line.startswith("Would reformat: ")
    ]
    if not files:
        return f"## {OK} ruff format\n\n{text.strip().splitlines()[-1] if text.strip() else 'Nothing to format.'}\n"
    items = "\n".join(f"- `{name}`" for name in files)
    return f"## {FAIL} ruff format\n\n{len(files)} file(s) would be reformatted; run `uv run ruff format`.\n\n{items}\n"


def license_headers(path: str | None) -> str:
    text = read_text(path)
    if text is None:
        return missing_report("SPDX license headers", path)
    lines = [line for line in text.splitlines() if line.strip()]
    passed = sum(line.startswith("All files have license headers") for line in lines)
    problems = [line for line in lines if not line.startswith("All files have license headers")]
    if not problems:
        return f"## {OK} SPDX license headers\n\n{passed} location(s) checked, every file has its header.\n"
    return (
        f"## {FAIL} SPDX license headers\n\n{passed} location(s) fully headed; the others report:\n\n"
        + fenced("\n".join(problems))
        + "\n\nFix with `scripts/add_license_header.py` (without `--check`).\n"
    )


def junit_totals(path: str) -> tuple[JunitTotals, list[tuple[str, str]]]:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    totals = JunitTotals(
        tests=sum(int(s.get("tests", 0)) for s in suites),
        failures=sum(int(s.get("failures", 0)) for s in suites),
        errors=sum(int(s.get("errors", 0)) for s in suites),
        skipped=sum(int(s.get("skipped", 0)) for s in suites),
        time=sum(float(s.get("time", 0)) for s in suites),
    )
    failed: list[tuple[str, str]] = []
    for case in root.iter("testcase"):
        problem = case.find("failure") if case.find("failure") is not None else case.find("error")
        if problem is not None:
            failed.append(
                (f"{case.get('classname', '')}::{case.get('name', '')}", problem.get("message", ""))
            )
    return totals, failed


def coverage_files(path: str) -> tuple[float, list[tuple[str, float, str]]]:
    root = ET.parse(path).getroot()
    rows: list[tuple[str, float, str]] = []
    for item in root.iter("class"):
        lines = [line for line in item.iter("line")]
        missed = [line.attrib["number"] for line in lines if line.get("hits") == "0"]
        percent = 100 * (len(lines) - len(missed)) / len(lines) if lines else 100.0
        rows.append((item.get("filename", ""), percent, ", ".join(missed)))
    return float(root.get("line-rate", 0)) * 100, sorted(rows)


def pytest_summary(junit: str | None, coverage: str | None) -> str:
    if not (junit and Path(junit).is_file()):
        return missing_report("pytest", junit)
    totals, failed = junit_totals(junit)
    bad = totals["failures"] + totals["errors"]
    passed = totals["tests"] - bad - totals["skipped"]
    text = f"## {FAIL if bad else OK} pytest\n\n"
    text += table(
        ["Tests", "Passed", "Failed", "Skipped", "Time"],
        [(totals["tests"], passed, bad, totals["skipped"], f"{totals['time']:.2f}s")],
    )
    if failed:
        text += "\n\n### Failed tests\n\n" + table(["Test", "Message"], failed)
    if coverage and Path(coverage).is_file():
        total, files = coverage_files(coverage)
        text += f"\n\n### Coverage: {total:.1f}%\n\n"
        gaps = [(name, f"{pct:.1f}%", missing) for name, pct, missing in files if pct < 100]
        text += (
            table(["File", "Cover", "Missing lines"], gaps)
            if gaps
            else "Every file is fully covered."
        )
    return text + "\n"


def bandit_summary(path: str | None) -> str:
    report = cast("BanditReport | None", load_json(path))
    if report is None:
        return missing_report("bandit", path)
    results = report["results"]
    if not results:
        totals = report.get("metrics", {}).get("_totals", {})
        loc = totals.get("loc")
        scanned = f" {loc} lines scanned." if loc else ""
        return f"## {OK} bandit\n\nNo security issue found.{scanned}\n"
    rows = [
        (r["issue_severity"], r["test_id"], f"{r['filename']}:{r['line_number']}", r["issue_text"])
        for r in results
    ]
    return (
        f"## {FAIL} bandit\n\n{len(results)} issue(s).\n\n"
        + table(["Severity", "Test", "Location", "Issue"], rows)
        + "\n"
    )


def pip_audit_summary(path: str | None) -> str:
    report = cast("AuditReport | None", load_json(path))
    if report is None:
        return missing_report("pip-audit", path)
    dependencies = report["dependencies"]
    rows = [
        (
            dep["name"],
            dep["version"],
            vuln["id"],
            ", ".join(vuln.get("fix_versions") or ["no fix yet"]),
        )
        for dep in dependencies
        for vuln in dep.get("vulns", [])
    ]
    if not rows:
        audited = (
            f"{len(dependencies)} audited dependencies"
            if dependencies
            else "the environment (no third-party dependency)"
        )
        return f"## {OK} pip-audit\n\nNo known vulnerability in {audited}.\n"
    return (
        f"## {FAIL} pip-audit\n\n{len(rows)} known vulnerability(ies).\n\n"
        + table(["Package", "Version", "Advisory", "Fixed in"], rows)
        + "\n"
    )


def text_summary(title: str, path: str | None, status: str) -> str:
    """A tool without a structured report: its status and the end of its output."""
    text = read_text(path)
    icon = OK if status == "success" else FAIL if status == "failure" else WARN
    body = fenced(text) if text and text.strip() else "The tool printed nothing."
    return f"## {icon} {title}\n\n{body}\n"


def release_summary(path: str | None) -> str:
    report = cast("ReleaseReport | None", load_json(path))
    if not report or not report.get("bumps"):
        return f"## {OK} release\n\nNothing to release: no `feat`, `fix` or `perf` commit since the last tag.\n"
    rows = [
        (name, bump.get("current_version", ""), bump.get("next_version", ""))
        for name, bump in report.get("bumps", {}).items()
    ]
    return f"## {OK} release\n\n" + table(["Component", "From", "To"], rows) + "\n"


def publish_summary(
    path: str | None, package: str, version: str, repository: str, status: str
) -> str:
    """The distributions built for a release and where they were published."""
    # `uv build` drops a .gitignore next to the distributions.
    files = (
        sorted(f for f in Path(path).iterdir() if not f.name.startswith("."))
        if path and Path(path).is_dir()
        else []
    )
    if not files:
        return missing_report("PyPI publish", path)
    icon = OK if status == "success" else FAIL if status == "failure" else WARN
    rows = [
        (
            f"`{file.name}`",
            f"{file.stat().st_size / 1024:.1f} KiB",
            hashlib.sha256(file.read_bytes()).hexdigest()[:16],
        )
        for file in files
    ]
    links = [f"- PyPI: <https://pypi.org/project/{package}/{version}/>"]
    if repository:
        links.append(f"- GitHub release: <https://github.com/{repository}/releases/tag/{version}>")
    return (
        f"## {icon} PyPI publish\n\n`{package}` {version}\n\n"
        + table(["File", "Size", "SHA-256"], rows)
        + "\n\n"
        + "\n".join(links)
        + "\n"
    )


def emit(text: str) -> None:
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if target:
        with Path(target).open("a") as stream:
            _ = stream.write(text + "\n")
    else:
        _ = sys.stdout.write(text + "\n")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("ruff-check", "ruff-format", "headers", "bandit", "pip-audit", "release"):
        _ = sub.add_parser(name).add_argument("report")
    pytest = sub.add_parser("pytest")
    _ = pytest.add_argument("--junit", required=True)
    _ = pytest.add_argument("--coverage")
    text = sub.add_parser("text")
    _ = text.add_argument("title")
    _ = text.add_argument("report")
    publish = sub.add_parser("publish")
    _ = publish.add_argument("report")
    _ = publish.add_argument("--package", required=True)
    _ = publish.add_argument("--version", required=True)
    args = parser.parse_args(argv, namespace=Arguments())
    if args.command == "ruff-check":
        annotations = ruff_annotations(args.report)
        if annotations:
            print(annotations)
        emit(ruff_check(args.report))
    elif args.command == "pytest":
        emit(pytest_summary(args.junit, args.coverage))
    elif args.command == "text":
        emit(text_summary(args.title, args.report, os.environ.get("JOB_STATUS", "")))
    elif args.command == "publish":
        repository = os.environ.get("GITHUB_REPOSITORY", "")
        status = os.environ.get("JOB_STATUS", "")
        emit(publish_summary(args.report, args.package, args.version, repository, status))
    else:
        formatters = {
            "ruff-format": ruff_format,
            "headers": license_headers,
            "bandit": bandit_summary,
            "pip-audit": pip_audit_summary,
            "release": release_summary,
        }
        emit(formatters[args.command](args.report))


if __name__ == "__main__":
    main()
