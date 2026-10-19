"""Collect failed tests from the JUnit XML report into a JSON file.

Usage: python scripts/collect_test_failures.py [junit.xml] [output.json]

Defaults: test-results/junit.xml -> test-results/failures.json

For every failed test the JSON contains the test cases it covers (with
the expected result, from docs/**/test_cases.md), the error message,
the end of the traceback, the source code of the test, the logs
captured for that test and the paths of the Playwright screenshot and
trace. The file is the input for the AI analysis of test failures, so
long texts are shortened and secrets are masked.
"""

import ast
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from junit_summary import get_status


MAX_MESSAGE_CHARS = 2000
MAX_TRACEBACK_LINES = 60
MAX_LOG_LINES = 80
MAX_CODE_LINES = 120

TEST_CASES_GLOB = "docs/**/test_cases.md"

SECRET_ENV_VARS = ("DB_PASSWORD", "POSTGRES_PASSWORD", "ANTHROPIC_API_KEY")

PASSWORD_PATTERN = re.compile(r"""(['"]?password['"]?[ \t]*[:=][ \t]*['"]?)[^'",\s}]+""", re.IGNORECASE)

SECTION_HEADER_PATTERN = re.compile(r"^-+ Captured Log -+$", re.MULTILINE)

SEPARATOR_PATTERN = re.compile(r"\| separator \| =+$")

LOG_RECORD_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \| ")


def mask_secrets(text: str) -> str:
    """Replace passwords and secret environment values with ***."""

    for name in SECRET_ENV_VARS:
        value = os.getenv(name)

        if value:
            text = text.replace(value, "***")

    return PASSWORD_PATTERN.sub(r"\1***", text)


def keep_last_lines(text: str, max_lines: int) -> str:
    """Keep only the last lines of a text, where the error usually is."""

    lines = text.strip().splitlines()

    if len(lines) <= max_lines:
        return "\n".join(lines)

    skipped = len(lines) - max_lines

    return "\n".join([f"... ({skipped} lines skipped)"] + lines[-max_lines:])


def get_test_id(testcase: ET.Element) -> str:
    """Build a pytest node id, e.g. tests/ui/test_register.py::test_name."""

    parts = testcase.get("classname", "").split(".")

    # The classname is "package.module" or "package.module.Class".
    for index in range(len(parts), 0, -1):
        module_path = "/".join(parts[:index]) + ".py"

        if Path(module_path).exists():
            return "::".join([module_path, *parts[index:], testcase.get("name", "")])

    return "/".join(parts) + ".py::" + testcase.get("name", "")


def get_test_type(test_id: str) -> str:
    """Return the test type from its folder: api, db or ui."""

    parts = test_id.split("/")

    return parts[1] if len(parts) > 2 and parts[0] == "tests" else "other"


def get_logs(testcase: ET.Element) -> list[str]:
    """
    Return the log lines captured for a test.

    With junit_logging = log pytest writes the logs of a test to its
    <system-out> element, in the format set by log_format in pytest.ini.
    """

    element = testcase.find("system-out")
    logs = SECTION_HEADER_PATTERN.sub("", element.text or "") if element is not None else ""

    lines = []
    in_traceback = False

    for line in logs.splitlines():
        # conftest logs the traceback again, it is already in "traceback".
        if LOG_RECORD_PATTERN.match(line):
            in_traceback = line.endswith("TRACEBACK:")

            if in_traceback:
                continue

        elif in_traceback:
            continue

        if line.strip() and not SEPARATOR_PATTERN.search(line.rstrip()):
            lines.append(line)

    return keep_last_lines(mask_secrets("\n".join(lines)), MAX_LOG_LINES).splitlines()


def get_artifacts(testcase: ET.Element) -> dict[str, list[str]]:
    """Return paths of Playwright screenshots and traces saved for a test."""

    artifacts = {"screenshots": [], "traces": []}

    for prop in testcase.iter("property"):
        if prop.get("name") == "playwright_screenshot":
            artifacts["screenshots"].append(prop.get("value"))

        elif prop.get("name") == "playwright_trace":
            artifacts["traces"].append(prop.get("value"))

    return artifacts


def strip_parameters(test_id: str) -> str:
    """Remove pytest parameters, e.g. test_name[chromium] -> test_name."""

    return re.sub(r"\[.*\]$", "", test_id)


def load_test_cases() -> dict[str, list[dict]]:
    """
    Read the test case tables from docs/**/test_cases.md.

    Returns the test cases grouped by the automated test that covers
    them. A parametrized test usually covers several test cases.
    """

    test_cases = {}

    for path in sorted(Path().glob(TEST_CASES_GLOB)):
        header = None

        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                header = None
                continue

            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]

            if header is None:
                header = cells
                continue

            if all(set(cell) <= set("-: ") for cell in cells):
                continue

            row = dict(zip(header, cells))
            automated_test = row.get("Automated test", "").strip("`")

            if automated_test:
                test_cases.setdefault(automated_test, []).append({
                    "id": row.get("ID"),
                    "title": row.get("Title"),
                    "test_data": row.get("Test data"),
                    "expected_result": row.get("Expected result"),
                })

    return test_cases


def get_test_code(test_id: str) -> dict | None:
    """Return the source code of a test function with its decorators."""

    module_path, *names = strip_parameters(test_id).split("::")
    path = Path(module_path)

    if not names or not path.exists():
        return None

    source = path.read_text(encoding="utf-8")

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == names[-1]:
            start = min([node.lineno] + [decorator.lineno for decorator in node.decorator_list])
            lines = source.splitlines()[start - 1:node.end_lineno]

            if len(lines) > MAX_CODE_LINES:
                lines = lines[:MAX_CODE_LINES] + [f"... ({len(lines) - MAX_CODE_LINES} lines skipped)"]

            return {"file": module_path, "line": start, "source": "\n".join(lines)}

    return None


def collect_failure(testcase: ET.Element, status: str, test_cases: dict[str, list[dict]]) -> dict:
    """Collect all data about one failed test."""

    element = testcase.find("failure")

    if element is None:
        element = testcase.find("error")

    test_id = get_test_id(testcase)

    return {
        "test_id": test_id,
        "type": get_test_type(test_id),
        "status": status,
        "time": float(testcase.get("time", 0)),
        "test_cases": test_cases.get(strip_parameters(test_id), []),
        "message": mask_secrets(element.get("message") or "")[:MAX_MESSAGE_CHARS],
        "traceback": keep_last_lines(mask_secrets(element.text or ""), MAX_TRACEBACK_LINES),
        "test_code": get_test_code(test_id),
        "logs": get_logs(testcase),
        "artifacts": get_artifacts(testcase),
    }


def collect(report_path: Path) -> dict:
    """Build the failures document from the JUnit XML report."""

    testcases = list(ET.parse(report_path).getroot().iter("testcase"))
    statuses = [get_status(case) for case in testcases]
    test_cases = load_test_cases()

    counts = {status: statuses.count(status) for status in ("passed", "failed", "error", "skipped")}

    return {
        "run": {
            "commit": os.getenv("GITHUB_SHA"),
            "branch": os.getenv("GITHUB_REF_NAME"),
            "run_id": os.getenv("GITHUB_RUN_ID"),
            "total": len(testcases),
            **counts,
        },
        "failures": [
            collect_failure(case, status, test_cases)
            for case, status in zip(testcases, statuses)
            if status in ("failed", "error")
        ],
    }


def main():
    report_path = Path(sys.argv[1] if len(sys.argv) > 1 else "test-results/junit.xml")
    output_path = Path(sys.argv[2] if len(sys.argv) > 2 else "test-results/failures.json")

    if not report_path.exists():
        print(f"JUnit report not found: {report_path}")
        return

    document = collect(report_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Collected {len(document['failures'])} failed tests into {output_path}")


if __name__ == "__main__":
    main()
