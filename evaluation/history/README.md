# Evaluation history of the AI failure analysis

One file per evaluated version of the analyzer (`scripts/failure_analyzer.py`), added only after the evaluation was actually run. Each file names the commit, the model, the dataset and the CI run, and points to the reports and `scores.json` in `evaluation/results/`.

Versions can only be compared on the same dataset. When cases are added to `evaluation/references_cause.json`, the dataset gets a new number and the current prompt has to be evaluated on it again before the next change.

## Scoring

- **One diagnosis = one failed test.** MIX-01 has four diagnoses, each scored against the case named in its `expected` map.
- **Category** is correct when it equals `actual_category` or is in `acceptable_categories`.
- **Root cause** is judged manually against `actual_root_cause`: correct, partial (the mechanism is only one of several alternatives or a key part is missing) or wrong.
- **Evidence** is supported when every quoted line is in failures.json, apart from whitespace and JSON fields restated in another format.

## Dataset 1: 16 cases, 19 diagnoses

AB-01..04, TB-01..03, ENV-01..03, FL-01..03, IE-01..02, MIX-01.

| Version | Change | Category | Root cause | Evidence | Insufficient evidence recognized | insufficient_evidence for a case with enough evidence |
| --- | --- | --- | --- | --- | --- | --- |
| [v1](v1-baseline.md) | baseline | 17/19 | 15/19 (+4 partial) | 19/19 | 0/2 | 0 |
| [v2](v2-strict-insufficient-evidence.md) | strict rule for insufficient_evidence | 16/19 | 13/19 (+6 partial) | 19/19 | 2/2 | 3 |
| [v3](v3-equal-support-rule.md) | insufficient_evidence only for equally supported causes | 17/19 | 14/19 (+5 partial) | 19/19 | 0/2 | 0 |

## Dataset 2: 19 cases, 22 diagnoses

Dataset 1 plus IE-03..05 (`references_cause.json` version 2).

| Version | Change | Category | Root cause | Evidence | Insufficient evidence recognized | insufficient_evidence for a case with enough evidence |
| --- | --- | --- | --- | --- | --- | --- |
