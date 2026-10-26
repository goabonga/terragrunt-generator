# SPDX-License-Identifier: MIT
# Copyright (c) 2024-2026 Chris <goabonga@pm.me>

import importlib.util
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "format_summary.py"
spec = importlib.util.spec_from_file_location("format_summary", SCRIPT)
assert spec is not None and spec.loader is not None
fs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fs)


@pytest.fixture
def report(tmp_path: Path) -> Callable[[str, Any], str]:
    def write(name: str, content: Any) -> str:
        path = tmp_path / name
        _ = path.write_text(
            content if isinstance(content, str) else json.dumps(content)
        )
        return str(path)

    return write


@pytest.fixture
def summary_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(path))
    return path


def test_table_escapes_cells() -> None:
    assert (
        fs.table(["a", "b"], [("x|y", "l1\nl2")])
        == "| a | b |\n| --- | --- |\n| x\\|y | l1 l2 |"
    )


def test_fenced_keeps_the_tail() -> None:
    text = fs.fenced("\n".join(str(n) for n in range(100)), limit=3)
    assert text == "```text\n... 97 earlier lines omitted\n97\n98\n99\n```"
    assert fs.fenced("one") == "```text\none\n```"


def test_relative_paths(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    assert fs.relative(str(tmp_path / "src" / "a.py")) == "src/a.py"
    assert fs.relative("/elsewhere/a.py") == "/elsewhere/a.py"


@pytest.mark.parametrize(
    "call",
    [
        fs.ruff_check,
        fs.ruff_format,
        fs.license_headers,
        fs.bandit_summary,
        fs.pip_audit_summary,
    ],
)
def test_a_missing_report_is_explained(call: Callable[[str | None], str]) -> None:
    assert "No report was produced" in call("/nonexistent/report")
    assert "No report was produced" in call(None)


def finding(
    code: str | None = "F401", filename: str = "src/a.py", row: int = 3
) -> dict[str, Any]:
    return {
        "code": code,
        "filename": filename,
        "location": {"row": row, "column": 1},
        "message": "unused | import",
    }


def test_ruff_check_without_findings(report: Callable[[str, Any], str]) -> None:
    assert "✅ ruff check" in fs.ruff_check(report("r.json", []))


def test_ruff_check_lists_findings_in_order(report: Callable[[str, Any], str]) -> None:
    text = fs.ruff_check(
        report("r.json", [finding(row=9), finding("E1", "src/a.py", 2)])
    )
    assert text.startswith("## ❌ ruff check\n\n2 finding(s).")
    assert text.index("a.py:2") < text.index("a.py:9")
    assert "unused \\| import" in text


def test_ruff_annotations(report: Callable[[str, Any], str]) -> None:
    path = report("r.json", [finding(), finding(code=None)])
    lines = fs.ruff_annotations(path).splitlines()
    assert lines[0] == "::error file=src/a.py,line=3,col=1,title=F401::unused | import"
    assert "title=ruff::" in lines[1]
    assert fs.ruff_annotations("/nonexistent") == ""


def test_ruff_format_clean(report: Callable[[str, Any], str]) -> None:
    assert "29 files already formatted" in fs.ruff_format(
        report("f.txt", "29 files already formatted\n")
    )
    assert "Nothing to format" in fs.ruff_format(report("e.txt", ""))


def test_ruff_format_lists_files(report: Callable[[str, Any], str]) -> None:
    text = fs.ruff_format(
        report(
            "f.txt",
            "Would reformat: src/a.py\nWould reformat: src/b.py\n2 files would be reformatted\n",
        )
    )
    assert "2 file(s) would be reformatted" in text
    assert "- `src/a.py`" in text


def test_license_headers_clean(report: Callable[[str, Any], str]) -> None:
    text = fs.license_headers(report("h.txt", "All files have license headers.\n" * 5))
    assert "5 location(s) checked" in text


def test_license_headers_missing(report: Callable[[str, Any], str]) -> None:
    text = fs.license_headers(
        report("h.txt", "All files have license headers.\nMissing header: src/a.py\n")
    )
    assert text.startswith("## ❌ SPDX license headers")
    assert "Missing header: src/a.py" in text


JUNIT = """<testsuites><testsuite name="pytest" tests="4" failures="1" errors="1" skipped="1" time="1.5">
<testcase classname="t.a" name="ok"/>
<testcase classname="t.a" name="bad"><failure message="boom">trace</failure></testcase>
<testcase classname="t.a" name="err"><error message="oops">trace</error></testcase>
<testcase classname="t.a" name="skip"><skipped/></testcase></testsuite></testsuites>"""

COVERAGE = """<coverage line-rate="0.75"><packages><package><classes>
<class filename="src/full.py"><lines><line number="1" hits="1"/></lines></class>
<class filename="src/gap.py"><lines><line number="1" hits="1"/><line number="2" hits="0"/><line number="3" hits="0"/><line number="4" hits="1"/></lines></class>
<class filename="src/empty.py"><lines/></class>
</classes></package></packages></coverage>"""


def test_pytest_summary_with_failures_and_gaps(
    report: Callable[[str, Any], str],
) -> None:
    text = fs.pytest_summary(report("j.xml", JUNIT), report("c.xml", COVERAGE))
    assert text.startswith("## ❌ pytest")
    assert "| 4 | 1 | 2 | 1 | 1.50s |" in text
    assert "| t.a::bad | boom |" in text
    assert "| t.a::err | oops |" in text
    assert "Coverage: 75.0%" in text
    assert "| src/gap.py | 50.0% | 2, 3 |" in text
    assert "full.py" not in text


def test_pytest_summary_passing_and_fully_covered(
    report: Callable[[str, Any], str],
) -> None:
    junit = '<testsuite tests="2" failures="0" errors="0" skipped="0" time="0.1"><testcase classname="a" name="b"/></testsuite>'
    coverage = '<coverage line-rate="1"><packages><package><classes><class filename="a.py"><lines><line number="1" hits="1"/></lines></class></classes></package></packages></coverage>'
    text = fs.pytest_summary(report("j.xml", junit), report("c.xml", coverage))
    assert text.startswith("## ✅ pytest")
    assert "Every file is fully covered." in text


def test_pytest_summary_without_coverage_or_junit(
    report: Callable[[str, Any], str],
) -> None:
    junit = '<testsuite tests="1" failures="0" errors="0" skipped="0" time="0"/>'
    assert "Coverage" not in fs.pytest_summary(report("j.xml", junit), None)
    assert "No report was produced" in fs.pytest_summary("/nonexistent", None)


def test_bandit_clean_and_dirty(report: Callable[[str, Any], str]) -> None:
    assert "628 lines scanned" in fs.bandit_summary(
        report("b.json", {"results": [], "metrics": {"_totals": {"loc": 628}}})
    )
    assert "No security issue found.\n" in fs.bandit_summary(
        report("b.json", {"results": []})
    )
    result = {
        "issue_severity": "HIGH",
        "test_id": "B602",
        "filename": "src/a.py",
        "line_number": 4,
        "issue_text": "shell",
    }
    text = fs.bandit_summary(report("b.json", {"results": [result]}))
    assert "## ❌ bandit" in text
    assert "| HIGH | B602 | src/a.py:4 | shell |" in text


def test_pip_audit(report: Callable[[str, Any], str]) -> None:
    assert "2 audited dependencies" in fs.pip_audit_summary(
        report(
            "a.json",
            {
                "dependencies": [
                    {"name": "a", "version": "1", "vulns": []},
                    {"name": "b", "version": "2"},
                ]
            },
        )
    )
    assert "no third-party dependency" in fs.pip_audit_summary(
        report("a.json", {"dependencies": []})
    )
    dirty: dict[str, Any] = {
        "dependencies": [
            {
                "name": "a",
                "version": "1",
                "vulns": [
                    {"id": "CVE-1", "fix_versions": ["2"]},
                    {"id": "CVE-2", "fix_versions": []},
                ],
            }
        ]
    }
    text = fs.pip_audit_summary(report("a.json", dirty))
    assert "| a | 1 | CVE-1 | 2 |" in text
    assert "| a | 1 | CVE-2 | no fix yet |" in text


@pytest.mark.parametrize(
    ("status", "icon"), [("success", "✅"), ("failure", "❌"), ("cancelled", "⚠️")]
)
def test_text_summary(
    report: Callable[[str, Any], str], status: str, icon: str
) -> None:
    assert fs.text_summary("osv", report("o.txt", "output"), status).startswith(
        f"## {icon} osv"
    )


def test_text_summary_without_output(report: Callable[[str, Any], str]) -> None:
    assert "printed nothing" in fs.text_summary("osv", report("o.txt", " "), "success")
    assert "printed nothing" in fs.text_summary("osv", "/nonexistent", "success")


def test_release_summary(report: Callable[[str, Any], str]) -> None:
    assert "Nothing to release" in fs.release_summary("/nonexistent")
    assert "Nothing to release" in fs.release_summary(report("r.json", {"bumps": {}}))
    text = fs.release_summary(
        report(
            "r.json",
            {
                "bumps": {
                    "x": {"current_version": "0.1.0", "next_version": "0.2.0"},
                    "y": {},
                }
            },
        )
    )
    assert "| x | 0.1.0 | 0.2.0 |" in text
    assert "| y |  |  |" in text


def test_emit_appends_to_the_step_summary(summary_file: Path) -> None:
    fs.emit("one")
    fs.emit("two")
    assert summary_file.read_text() == "one\ntwo\n"


def test_emit_prints_without_a_step_summary(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    fs.emit("one")
    assert capsys.readouterr().out == "one\n"


def test_main_dispatches_every_command(
    report: Callable[[str, Any], str],
    summary_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv("JOB_STATUS", "success")
    ruff = report("r.json", [finding()])
    fs.main(["ruff-check", ruff])
    assert "::error file=src/a.py" in capsys.readouterr().out
    fs.main(["ruff-check", report("clean.json", [])])
    assert capsys.readouterr().out == ""
    fs.main(["ruff-format", report("f.txt", "1 file already formatted")])
    fs.main(["headers", report("h.txt", "All files have license headers.")])
    fs.main(["bandit", report("b.json", {"results": []})])
    fs.main(["pip-audit", report("a.json", {"dependencies": []})])
    fs.main(["release", report("rel.json", {"bumps": {}})])
    fs.main(["text", "osv-scanner", report("o.txt", "ok")])
    junit = '<testsuite tests="1" failures="0" errors="0" skipped="0" time="0"/>'
    fs.main(["pytest", "--junit", report("j.xml", junit)])
    content = summary_file.read_text()
    for title in (
        "ruff check",
        "ruff format",
        "SPDX license headers",
        "bandit",
        "pip-audit",
        "release",
        "osv-scanner",
        "pytest",
    ):
        assert f" {title}\n" in content


def test_main_requires_a_command() -> None:
    with pytest.raises(SystemExit):
        fs.main([])


@pytest.fixture
def dist(tmp_path: Path) -> Path:
    directory = tmp_path / "dist"
    directory.mkdir()
    _ = (directory / "demo-1.2.3.tar.gz").write_bytes(b"x" * 2048)
    _ = (directory / "demo-1.2.3-py3-none-any.whl").write_bytes(b"y" * 1024)
    _ = (directory / ".gitignore").write_text("*\n")
    return directory


def test_publish_lists_the_distributions_and_their_links(dist: Path) -> None:
    text = fs.publish_summary(str(dist), "demo", "1.2.3", "owner/demo", "success")
    assert text.startswith("## ✅ PyPI publish\n\n`demo` 1.2.3\n")
    assert "| `demo-1.2.3-py3-none-any.whl` | 1.0 KiB |" in text
    assert "| `demo-1.2.3.tar.gz` | 2.0 KiB |" in text
    assert ".gitignore" not in text
    assert "<https://pypi.org/project/demo/1.2.3/>" in text
    assert "<https://github.com/owner/demo/releases/tag/1.2.3>" in text


def test_publish_flags_a_failed_job(dist: Path) -> None:
    text = fs.publish_summary(str(dist), "demo", "1.2.3", "", "failure")
    assert text.startswith("## ❌ PyPI publish")
    assert "GitHub release" not in text


def test_publish_without_distributions_reports_the_missing_build(
    tmp_path: Path,
) -> None:
    assert "No report was produced" in fs.publish_summary(
        str(tmp_path / "dist"), "demo", "1.2.3", "owner/demo", "failure"
    )


def test_main_publish_reads_the_job_environment(
    dist: Path, summary_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/demo")
    monkeypatch.setenv("JOB_STATUS", "success")
    fs.main(["publish", str(dist), "--package", "demo", "--version", "1.2.3"])
    assert "releases/tag/1.2.3" in summary_file.read_text()


def pyright_report(
    *diagnostics: dict[str, Any], errors: int = 0, warnings: int = 0
) -> Any:
    return {
        "generalDiagnostics": list(diagnostics),
        "summary": {
            "filesAnalyzed": 8,
            "errorCount": errors,
            "warningCount": warnings,
            "timeInSec": 0.94,
        },
    }


def diagnostic(
    file: str = "src/a.py",
    line: int = 3,
    severity: str = "error",
    rule: str | None = "reportX",
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "file": file,
        "severity": severity,
        "message": "first line\n  second line",
        "range": {"start": {"line": line, "character": 0}},
    }
    if rule:
        item["rule"] = rule
    return item


def test_pyright_without_diagnostics(report: Callable[[str, Any], str]) -> None:
    text = fs.pyright_summary(report("p.json", pyright_report()))
    assert text == "## ✅ pyright\n\nNo type error. 8 file(s) analysed in 0.9s.\n"


def test_pyright_lists_the_diagnostics_by_file_and_line(
    report: Callable[[str, Any], str],
) -> None:
    path = report(
        "p.json",
        pyright_report(
            diagnostic("src/b.py", 1),
            diagnostic("src/a.py", 9, rule=None),
            diagnostic("src/a.py", 2),
            errors=3,
        ),
    )
    text = fs.pyright_summary(path)
    assert text.startswith("## ❌ pyright\n\n3 error(s), 0 warning(s). 8 file(s)")
    rows = text.splitlines()[-3:]
    assert rows[0].startswith("| error | reportX | src/a.py:3 | first line |")
    assert rows[1].startswith("| error |  | src/a.py:10 |")
    assert rows[2].startswith("| error | reportX | src/b.py:2 |")
    assert "second line" not in text


def test_pyright_warnings_alone_are_not_a_failure(
    report: Callable[[str, Any], str],
) -> None:
    path = report("p.json", pyright_report(diagnostic(severity="warning"), warnings=1))
    assert fs.pyright_summary(path).startswith(
        "## ⚠️ pyright\n\n0 error(s), 1 warning(s)"
    )


def test_pyright_without_a_report_says_so() -> None:
    assert "No report was produced" in fs.pyright_summary("/nonexistent/p.json")


def test_main_pyright_appends_its_summary(
    report: Callable[[str, Any], str], summary_file: Path
) -> None:
    fs.main(["pyright", report("p.json", pyright_report())])
    assert " pyright\n" in summary_file.read_text()
