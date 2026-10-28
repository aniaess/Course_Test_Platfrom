# v2 – strict rule for insufficient_evidence

- **Date:** 2026-10-28
- **Model:** claude-opus-5-5
- **Analyzer:** commit `cfe6b3a`
- **Dataset:** 16 cases, 19 diagnoses (the same as v1)
- **Run:** [40671218345](https://github.com/aniaess/Course_Test_Platfrom/actions/runs/40671218345)
- **Reports and scores:** `evaluation/results/2026-10-28_claude-opus-5-5_cfe6b3a/`

## Prompt change

Added to the system prompt after the list of categories:

> Use insufficient_evidence when the plausible causes belong to different categories and nothing in the document rules out all but one of them. Do not pick the most likely of them anyway; name all of them in possible_root_cause and say which evidence would decide. Several possible causes within one category do not make the evidence insufficient, and neither does a detail you cannot confirm.

## Result

| Metric | v1 | v2 |
| --- | --- | --- |
| Analyzed diagnoses | 19 | 19 |
| Correct failure category | 17/19 (89.5%) | 16/19 (84.2%) |
| Correct root cause | 15/19 (78.9%), 4 partial | 13/19 (68.4%), 6 partial |
| Diagnoses supported by evidence | 19/19 (100%) | 19/19 (100%) |
| Insufficient evidence recognized | 0/2 | 2/2 |
| insufficient_evidence chosen for a case with enough evidence | 0 | 3 |

## Changed categories

| Case | Expected | v1 | v2 |
| --- | --- | --- | --- |
| IE-01 | insufficient_evidence | application_bug ❌ | insufficient_evidence ✅ |
| IE-02 | insufficient_evidence | environment_issue ❌ | insufficient_evidence ✅ |
| ENV-03 | environment_issue | environment_issue ✅ | insufficient_evidence ❌ |
| FL-01 | flaky_test | flaky_test ✅ | insufficient_evidence ❌ |
| FL-02 | flaky_test | flaky_test ✅ | insufficient_evidence ❌ |

## Where the AI was wrong

- **ENV-03, FL-01, FL-02** – wrong category. The model names the right cause first (missing schema, text_content() without waiting, the 100 ms timeout), but adds an alternative from another category that nothing in the evidence points to: for FL-02 "the backend may not reject the duplicate email with the expected error". Root cause is scored partial, because the right mechanism is not chosen.
- **AB-04, ENV-01, FL-03** – partial root cause, the same weaknesses as in v1.

IE-01 and IE-02 are now correct in category and cause: IE-01 says the test runner's database connection "does not prove the API container uses the same connection or configuration" and asks for the API container logs.

## Conclusion

The rule overcorrected. "Nothing rules out the other causes" is almost always true, so the model counted merely theoretical alternatives. A rule should only allow insufficient_evidence when the alternatives are really supported by the evidence.
