# FITGATE – Judgment Framework

## 1. Purpose

The Judgment Framework explains how responsibilities are divided between the LLM, Python and the nurse.

| Component | Responsibility | Why this choice? |
|---|---|---|
| LLM symptom classification | Identifies symptoms, category, priority and affected abilities | Informal notes can be written in different ways and languages. |
| JSON validation | Python checks required fields and allowed values | Invalid responses must never be trusted. |
| Retry and fallback | Python retries once and uses today if the response remains invalid | A failed API response must not crash the application or become routine. |
| Red-flag detection | Python checks the original note | Critical warning phrases must be checked independently of the LLM. |
| Job-ability matching | Python compares affected abilities with job requirements | Job mappings must remain outside the LLM. |
| Priority raising | Python raises but never lowers priority | A potentially dangerous case must not be downgraded. |
| Diagnosis protection | Python checks summaries for diagnostic language | The application must never diagnose workers. |
| Queue sorting | Python sorts all workers by priority and arrival time | Sorting should be consistent and repeatable. |
| Medical decisions | Nurse | Only the nurse can assess workers and decide what care is required. |

## 2. Why a Priority That Is Too Low Is More Dangerous

A worker with chest pain or breathing difficulty may be placed behind less urgent cases if the priority is too low.

This could delay human attention when it is needed most.

A priority that is too high may cause a worker to be seen earlier than necessary. This can inconvenience the clinic, but a priority that is too low may create a serious safety risk.

Therefore, FITGATE follows a raise-only priority rule.

## 3. Human Checkpoint

The nurse sees every worker in nurse_queue.csv and makes every medical decision.

FITGATE only organises the queue and displays job-related hold warnings.

It never contacts workers, supervisors or doctors and never removes a worker from the queue.
