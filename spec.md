# FITGATE – Job-Aware Clinic Visit Sorter

## 1. Purpose

FITGATE is a console-based Python application for a factory clinic. It uses an LLM to classify workers' informal clinic notes and Python safety rules to organise the nurse's queue according to urgency and job-related risks.

It helps the nurse identify workers who may need attention sooner during short factory breaks.

FITGATE never diagnoses, treats or advises workers. It never removes anyone from the queue. The nurse makes every medical decision.

## 2. Input

The application reads one file: visits.csv.

The file contains at least 20 worker records with these columns:

- id
- time
- job
- note

Notes may be written in English, Tamil or Tanglish.

The input includes red flags, an empty note, duplicate IDs, an unknown job and out-of-order arrival times.

## 3. LLM Output Contract

The LLM must return one JSON object containing exactly:

- category: injury, fever_cold, stomach, pain, allergy or other
- priority: see_now, today or routine
- affects: a list containing vision, balance, grip, alertness, breathing, walking or none
- summary: symptoms only, maximum 12 words

The LLM must never diagnose, advise or treat. It must never see the Python job-needs mappings.

Invalid JSON or invalid fields are retried once. If the response is still invalid, the application uses category other, priority today and an empty affects list.

## 4. Python Safety Rules

- Red-flag phrases always raise priority to see_now.
- Job-ability matches raise priority to at least today.
- For drivers and forklift operators, vision, balance or alertness matches raise priority to see_now.
- Python may raise priority but never lower it.
- Unknown jobs are flagged.
- Duplicate IDs are flagged; no records are removed.
- Unreadable times are flagged as unknown hour.
- Empty notes receive today priority.
- API failures and invalid responses use a today fallback.
- Disease names and diagnostic language are removed from summaries.

## 5. Red Flags

English and Tamil/Tanglish phrases include:

chest pain, trouble breathing, fainting, heavy bleeding, lip or face swelling, cannot stand, chemical in eye, electric shock, crushed or cut finger, large burn, nenju vali, moochu, mayakkam and rattham.

## 6. Outputs

The program creates:

1. nurse_queue.csv – all workers sorted by priority and arrival time, including their original notes, job hold flags, reasons and warnings. Nurse only.
2. summary.txt – counts by priority, category, arrival hour, job and workers held per job. It contains no notes, names or IDs.

## 7. Human Checkpoint

The nurse reviews every worker and makes every medical decision. FITGATE only organises the queue and identifies possible job-related safety concerns.
