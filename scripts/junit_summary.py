"""Convert a JUnit XML report into a Markdown summary.

Usage: python scripts/junit_summary.py test-results/junit.xml

The summary is printed to stdout. In GitHub Actions it is appended
to $GITHUB_STEP_SUMMARY and shown on the workflow run page.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


STATUS_ICONS = {
    "passed": "✅",
    "failed": "❌",
    "error": "💥",
    "skipped": "⏭️",
}


def get_status(testcase: ET.Element) -> str:
    """Return the status of a single test case."""

    if testcase.find("failure") is not None:
        return "failed"

    if testcase.find("error") is not None:
        return "error"

    if testcase.find("skipped") is not None:
        return "skipped"

    return "passed"


def get_message(testcase: ET.Element) -> str:
    """Return the first line of the failure or error message."""

    for tag in ("failure", "error"):
        element = testcase.find(tag)

        if element is not None:
            message = element.get("message") or element.text or ""
            first_line = message.strip().splitlines()[0] if message.strip() else ""

            return first_line.replace("|", "\\|")[:200]

    return ""


def build_summary(report_path: Path) -> str:
    """Build a Markdown summary from the JUnit XML report."""

    testcases = list(ET.parse(report_path).getroot().iter("testcase"))

    results = [
        (f"{case.get('classname')}::{case.get('name')}", get_status(case), case)
        for case in testcases
    ]

    counts = {status: 0 for status in STATUS_ICONS}

    for _, status, _ in results:
        counts[status] += 1

    total_time = sum(float(case.get("time", 0)) for case in testcases)

    lines = [
        "## Test results",
        "",
        "| Total | ✅ Passed | ❌ Failed | 💥 Errors | ⏭️ Skipped | Time |",
        "|---|---|---|---|---|---|",
        f"| {len(results)} | {counts['passed']} | {counts['failed']} "
        f"| {counts['error']} | {counts['skipped']} | {total_time:.1f}s |",
        "",
    ]

    problems = [
        (name, status, case)
        for name, status, case in results
        if status in ("failed", "error")
    ]

    if problems:
        lines += [
            "### Failed tests",
            "",
            "| Test | Message |",
            "|---|---|",
        ]
        lines += [
            f"| {STATUS_ICONS[status]} `{name}` | {get_message(case)} |"
            for name, status, case in problems
        ]
        lines += [
            "",
            "Screenshots and traces of failed UI tests are in the "
            "`test-results` artifact (`playwright/` folder).",
            "",
        ]

    lines += [
        "<details><summary>All tests</summary>",
        "",
        "| Status | Test | Time |",
        "|---|---|---|",
    ]
    lines += [
        f"| {STATUS_ICONS[status]} | `{name}` | {float(case.get('time', 0)):.2f}s |"
        for name, status, case in results
    ]
    lines += ["", "</details>"]

    return "\n".join(lines)


def main():
    # The summary contains emoji, which the Windows console cannot encode by default.
    sys.stdout.reconfigure(encoding="utf-8")

    report_path = Path(sys.argv[1] if len(sys.argv) > 1 else "test-results/junit.xml")

    if not report_path.exists():
        print(f"## Test results\n\nJUnit report not found: `{report_path}`")
        return

    print(build_summary(report_path))


if __name__ == "__main__":
    main()
