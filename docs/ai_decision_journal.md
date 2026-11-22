# FITGATE – AI Decision Journal

## Decision 1 – Using an LLM for Symptom Classification

I chose an LLM because workers may describe symptoms informally in English, Tamil or Tanglish. The LLM can interpret these descriptions and return structured labels.

## Decision 2 – Keeping Job Mappings in Python

I decided that job-needs mappings should remain in Python instead of being given to the LLM. This makes job-related checks consistent and prevents the LLM from independently deciding workplace safety restrictions.

## Decision 3 – Using a Raise-Only Priority Rule

I chose a raise-only rule because a priority that is too low could delay attention for a worker with serious symptoms. Python can increase priority but cannot reduce it.

## Decision 4 – Adding a Red-Flag Scanner

I added a separate Python red-flag scanner so important phrases in the original note are checked independently of the LLM's classification.

## Decision 5 – Adding Validation and Fallback

I chose to validate every response and retry once. If the response is still invalid or the API fails, the program uses the today fallback.

## Decision 6 – Protecting Worker Information

I separated the nurse queue from the summary report. The nurse queue contains original notes, while the summary contains aggregate counts without notes, names or IDs.

## Decision 7 – Keeping the Nurse in Control

I decided that the nurse must review every worker and make every medical decision. FITGATE is an organisational tool, not a replacement for medical judgement.
