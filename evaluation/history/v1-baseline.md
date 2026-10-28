# v1 – baseline

- **Date:** 2026-10-28
- **Model:** claude-opus-5-5
- **Analyzer:** commit `4409d35`, the prompt without any rule for insufficient_evidence
- **Dataset:** 16 cases, 19 diagnoses (15 single cases + 4 failures of MIX-01)
- **Run:** [40660225383](https://github.com/aniaess/Course_Test_Platfrom/actions/runs/40660225383)
- **Reports and scores:** `evaluation/results/2026-10-28_claude-opus-5-5/`

| Metric | Result |
| --- | --- |
| Analyzed diagnoses | 19 (16 cases) |
| Correct failure category | 17/19 (89.5%) |
| Correct root cause | 15/19 (78.9%), another 4 partial |
| Diagnoses supported by evidence | 19/19 (100%) |
| Insufficient evidence recognized | 0/2 |
| insufficient_evidence chosen for a case with enough evidence | 0 |

## Category per case

| Case | Expected | Model | Confidence | Category | Root cause |
| --- | --- | --- | --- | --- | --- |
| AB-01 | application_bug | application_bug | high | ✅ | ✅ |
| AB-02 | application_bug | application_bug | high | ✅ | ✅ |
| AB-03 | application_bug | application_bug | high | ✅ | ✅ |
| AB-04 | application_bug | application_bug | medium | ✅ | ⚠️ partial |
| TB-01 | test_bug | test_bug | high | ✅ | ✅ |
| TB-02 | test_bug | test_bug | high | ✅ | ✅ |
| TB-03 | test_bug | test_bug | high | ✅ | ✅ |
| ENV-01 | environment_issue | environment_issue | high | ✅ | ⚠️ partial |
| ENV-02 | environment_issue | environment_issue | high | ✅ | ✅ |
| ENV-03 | environment_issue | environment_issue | medium | ✅ | ✅ |
| FL-01 | flaky_test | flaky_test | medium | ✅ | ✅ |
| FL-02 | flaky_test | flaky_test | medium | ✅ | ✅ |
| FL-03 | flaky_test (or test_bug) | test_bug | medium | ✅ | ⚠️ partial |
| IE-01 | insufficient_evidence | application_bug | medium | ❌ | ⚠️ partial |
| IE-02 | insufficient_evidence | environment_issue | low | ❌ | ✅ |
| MIX-01 / AB-01 | application_bug | application_bug | high | ✅ | ✅ |
| MIX-01 / AB-03 | application_bug | application_bug | high | ✅ | ✅ |
| MIX-01 / TB-01 | test_bug | test_bug | high | ✅ | ✅ |
| MIX-01 / TB-03 | test_bug | test_bug | high | ✅ | ✅ |

## Where the AI was wrong

- **IE-01** – wrong category. The model saw HTTP 500 and wrote that "an environment cause cannot be ruled out without server logs" and that the API could have a different database configuration, which is the actual cause. It still classified the failure as `application_bug`.
- **IE-02** – wrong category. Among the alternatives it named a fixture that closes the page, which is the actual cause, and wrote "The available data cannot distinguish between these causes". It still classified the failure as `environment_issue` (low).
- **AB-04** – correct category, partial root cause. The model blames the backend or the frontend's handling of the 422 response. It does not see that the frontend validation lets a 7-character password through.
- **ENV-01** – correct category, partial root cause. It quotes `base URL: http://api:8001`, but its first hypothesis is an API container that is not running; the wrong port in the configuration is only one of the alternatives.
- **FL-03** – acceptable category (`test_bug`), partial root cause. It finds the hardcoded `shared-user@test.pl` and the committed row, but blames a previous run and does not use `run.tests`, where `test_create_user` ran just before.

## Conclusions

- The model avoids `insufficient_evidence`: in both IE cases its own reasoning says the data is not enough to decide, but it still picks a concrete category. The prompt should say explicitly to use `insufficient_evidence` when it lists several equally possible causes from different categories.
- No evidence was invented: every quoted line comes from failures.json.
- In the mixed run the four failures were not merged; the two API failures with different causes were kept apart.
