"""Analyze failed tests with the Claude API and write a Markdown report.

Usage: python scripts/failure_analyzer.py [failures.json] [report.md]

Defaults: test-results/failures.json -> test-results/failure_analysis.md

The input is the file written by collect_test_failures.py. Claude sorts
every failed test into a category (application bug, test bug,
environment issue, flaky test, insufficient evidence), describes the
observed and expected behavior, quotes the evidence and suggests the
next steps. The report is printed to stdout too, so in GitHub Actions
it can be appended to $GITHUB_STEP_SUMMARY.

Needs the ANTHROPIC_API_KEY environment variable. ANTHROPIC_MODEL can
choose another model. Without the key, or when no test failed, the
script does nothing and exits with code 0, so it never makes the CI
job fail.
"""

import json
import os
import sys
from pathlib import Path

import anthropic


MODEL = os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")

MAX_TOKENS = 16000

CATEGORY_LABELS = {
    "application_bug": "🐞 Application bug",
    "test_bug": "🧪 Test bug",
    "environment_issue": "🐳 Environment issue",
    "flaky_test": "🎲 Flaky test",
    "insufficient_evidence": "❓ Insufficient evidence",
}

SYSTEM_PROMPT = """\
You are an AI QA Failure Analysis Agent for a Course Platform built
with FastAPI and PostgreSQL. The tests use pytest, Playwright (UI),
Requests (API) and psycopg2 (database) and run in Docker Compose in
GitHub Actions.

You get a JSON document with the failed tests. For every failure it
contains the test cases it covers with the expected result, the error
message, the end of the traceback, the source code of the test and the
logs captured for the test. run.tests lists all tests of the run in
execution order with their status, which can show that an earlier test
left data that a later test depends on.

Analyze every failed test using only the provided evidence. Do not
invent facts. Distinguish confirmed facts from hypotheses:
observed_behavior, expected_behavior and evidence contain only facts
from the document, possible_root_cause is your hypothesis.

Classify every failure as one of:
- application_bug: the application behaves differently than the
  expected result of the test case says.
- test_bug: the test itself is wrong (wrong assertion, wrong locator,
  wrong test data, missing cleanup) while the application behaves as
  the test case expects.
- environment_issue: the service or database was not available,
  connection errors, Docker or configuration problems.
- flaky_test: timing or ordering problem, e.g. a timeout while waiting
  for an element, a race condition, data left by another test.
- insufficient_evidence: the data is not enough to decide.

Use insufficient_evidence when the evidence supports two or more causes
from different categories about equally well. Do not pick one of them
anyway; name all of them in possible_root_cause and say which evidence
would decide. When the evidence clearly points to one cause and the
others are only theoretically possible, choose the category of that
cause and lower the confidence instead. Several possible causes within
one category do not make the evidence insufficient, and neither does a
detail you cannot confirm.

When several tests fail for the same reason, say so in the summary.
Write the texts in English.
"""

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {
            "type": "string",
            "description": "Two or three sentences about the whole run.",
        },
        "failures": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "test_name": {"type": "string", "description": "The test_id from the document."},
                    "failure_category": {"type": "string", "enum": list(CATEGORY_LABELS)},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "observed_behavior": {"type": "string"},
                    "expected_behavior": {"type": "string"},
                    "evidence": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lines quoted from the message, traceback or logs.",
                    },
                    "possible_root_cause": {"type": "string"},
                    "recommended_next_steps": {"type": "array", "items": {"type": "string"}},
                },
                "required": [
                    "test_name",
                    "failure_category",
                    "confidence",
                    "observed_behavior",
                    "expected_behavior",
                    "evidence",
                    "possible_root_cause",
                    "recommended_next_steps",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["summary", "failures"],
    "additionalProperties": False,
}


def build_prompt(document: dict) -> str:
    """Build the user message from the failures document."""

    # The paths of screenshots and traces mean nothing to the model.
    failures = [
        {key: value for key, value in failure.items() if key != "artifacts"}
        for failure in document["failures"]
    ]

    data = json.dumps({"run": document["run"], "failures": failures}, indent=2, ensure_ascii=False)

    return f"Analyze these failed tests:\n\n<failures>\n{data}\n</failures>"


def analyze(document: dict) -> dict:
    """Send the failures to Claude and return the parsed analysis."""

    client = anthropic.Anthropic()

    # On a refusal the API repeats the request on a fallback model.
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=SYSTEM_PROMPT,
        output_config={
            "effort": "high",
            "format": {"type": "json_schema", "schema": ANALYSIS_SCHEMA},
        },
        messages=[{"role": "user", "content": build_prompt(document)}],
    )

    if response.stop_reason == "refusal":
        raise RuntimeError("Claude refused to analyze the failures")

    if response.stop_reason == "max_tokens":
        raise RuntimeError(f"The analysis is longer than {MAX_TOKENS} tokens")

    text = next(block.text for block in response.content if block.type == "text")

    return json.loads(text)


def to_markdown(document: dict, analysis: dict) -> str:
    """Format the analysis as a Markdown report."""

    run = document["run"]
    failures_by_id = {failure["test_id"]: failure for failure in document["failures"]}

    lines = [
        "## 🤖 AI analysis of test failures",
        "",
        f"Failed: {run['failed']}, errors: {run['error']}, total: {run['total']}. Model: `{MODEL}`.",
        "",
        analysis["summary"],
        "",
        "| Test | Category | Confidence |",
        "| --- | --- | --- |",
    ]

    for item in analysis["failures"]:
        lines.append(
            f"| `{item['test_name']}` | {CATEGORY_LABELS[item['failure_category']]} | {item['confidence']} |"
        )

    for item in analysis["failures"]:
        test_cases = failures_by_id.get(item["test_name"], {}).get("test_cases", [])
        test_case_ids = ", ".join(case["id"] for case in test_cases if case.get("id"))

        lines += ["", f"### `{item['test_name']}`", ""]

        if test_case_ids:
            lines += [f"**Test cases:** {test_case_ids}", ""]

        lines += [
            f"**Category:** {CATEGORY_LABELS[item['failure_category']]} ({item['confidence']})",
            "",
            f"**Observed behavior:** {item['observed_behavior']}",
            "",
            f"**Expected behavior:** {item['expected_behavior']}",
            "",
            "**Evidence:**",
            "",
            "```text",
            *item["evidence"],
            "```",
            "",
            f"**Possible root cause (hypothesis):** {item['possible_root_cause']}",
            "",
            "**Recommended next steps:**",
            "",
            *[f"- {step}" for step in item["recommended_next_steps"]],
        ]

    lines += ["", "_The analysis was generated by AI and can be wrong. Check it before you act on it._"]

    return "\n".join(lines) + "\n"


def main():
    input_path = Path(sys.argv[1] if len(sys.argv) > 1 else "test-results/failures.json")
    output_path = Path(sys.argv[2] if len(sys.argv) > 2 else "test-results/failure_analysis.md")

    # A report left from an earlier run would describe failures that are already fixed.
    output_path.unlink(missing_ok=True)

    if not input_path.exists():
        print(f"Failures file not found: {input_path}")
        return

    document = json.loads(input_path.read_text(encoding="utf-8"))

    if not document["failures"]:
        print("No failed tests, nothing to analyze.")
        return

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY is not set, skipping the AI analysis.")
        return

    try:
        analysis = analyze(document)
    except (anthropic.APIError, RuntimeError) as error:
        print(f"AI analysis failed: {error}")
        return

    report = to_markdown(document, analysis)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    # The Windows console does not use UTF-8 and cannot print the emoji.
    sys.stdout.reconfigure(encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
