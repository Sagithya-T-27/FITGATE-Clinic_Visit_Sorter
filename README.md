# FITGATE – Job-Aware Clinic Visit Sorter

## Project Overview

FITGATE is a console-based Python application that uses an LLM and Python safety rules to organise a factory clinic's worker queue.

The application classifies informal clinic notes, checks job-related ability risks, detects red flags and sorts workers into see_now, today and routine priorities.

FITGATE does not diagnose, advise or treat workers. The nurse makes every medical decision.

## Features

- LLM-based symptom classification
- English, Tamil and Tanglish input
- JSON validation and retry
- Safe fallback for API failures
- Python red-flag scanner
- Job-ability matching
- Raise-only priority rules
- Duplicate ID detection
- Arrival-time sorting
- Nurse queue generation
- Privacy-safe summary generation

## Project Structure

```text
FITGATE/
├── README.md
├── spec.md
├── visits.csv
├── system_prompt.txt
├── fitgate.py
├── eval_harness.py
├── requirements.txt
├── .env
├── .gitignore
├── outputs/
└── docs/
    ├── eval_results.md
    ├── red_team.md
    ├── judgment_framework.md
    ├── cost_latency_note.md
    ├── ai_decision_journal.md
    └── reflection.md
```

## Installation

Install Python 3.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```text
GEMINI_API_KEY=your_actual_key
GEMINI_MODEL=gemini-2.5-flash
```

Never upload your API key.

## Run the Application

```bash
python3 fitgate.py
```

## Run Evaluation

```bash
python3 eval_harness.py
```

## Output Files

- outputs/nurse_queue.csv
- outputs/summary.txt

## Human Oversight

The nurse sees every worker and makes every medical decision. FITGATE only organises the queue and displays job-related hold warnings.

## Author

Sagithya T

## Course

CIT AI-Native Engineering Programme – Semester 1
