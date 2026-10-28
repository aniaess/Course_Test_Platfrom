# v3 – insufficient_evidence only for equally supported causes

- **Date:** 2026-10-28
- **Model:** claude-opus-5-5
- **Analyzer:** commit `4833911`
- **Dataset:** 16 cases, 19 diagnoses (the same as v1)
- **Run:** [40672030474](https://github.com/aniaess/Course_Test_Platfrom/actions/runs/40672030474)
- **Reports and scores:** `evaluation/results/2026-10-28_claude-opus-5-5_4833911/`

## Prompt change

The rule of v2 was replaced with:

> Use insufficient_evidence when the evidence supports two or more causes from different categories about equally well. Do not pick one of them anyway; name all of them in possible_root_cause and say which evidence would decide. When the evidence clearly points to one cause and the others are only theoretically possible, choose the category of that cause and lower the confidence instead. Several possible causes within one category do not make the evidence insufficient, and neither does a detail you cannot confirm.

## Result

| Metric | v1 | v2 | v3 |
| --- | --- | --- | --- |
| Analyzed diagnoses | 19 | 19 | 19 |
| Correct failure category | 17/19 (89.5%) | 16/19 (84.2%) | 17/19 (89.5%) |
| Correct root cause | 15/19 (78.9%), 4 partial | 13/19 (68.4%), 6 partial | 14/19 (73.7%), 5 partial |
| Diagnoses supported by evidence | 19/19 (100%) | 19/19 (100%) | 19/19 (100%) |
| Insufficient evidence recognized | 0/2 | 2/2 | 0/2 |
| insufficient_evidence chosen for a case with enough evidence | 0 | 3 | 0 |

The categories are the same as in v1.

## Where the AI was wrong

- **IE-01** – application_bug (medium). "An environment problem cannot be fully ruled out ... However, nothing in the logs indicates one: the API answered, and the test runner's own database connection succeeded." The test process and the API container connect to the database separately, so the test's connection says nothing about the API's. Partial root cause.
- **IE-02** – environment_issue (low). The fixture closing the page is called "a less likely alternative", although the fixture code is not in the document at all. Unlike v1, the model no longer says the data cannot decide, so the root cause drops from correct to partial.
- **AB-04, ENV-01, FL-03** – partial root cause, the same weaknesses as in v1.

## Conclusion

The weaker rule went back to v1. A rule about how likely the causes are does not separate IE-01/IE-02 from FL-01/FL-02. What separates them is that the error comes from a component whose logs or code are missing (the API server, the fixture), and the visible error only shows that something broke there, not why. A rule written this way would fit the two IE cases of the dataset too closely, so new IE cases are added before the next prompt change.
