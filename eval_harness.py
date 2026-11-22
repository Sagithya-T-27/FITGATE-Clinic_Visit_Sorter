import os
from dotenv import load_dotenv
from google import genai

from fitgate import (
    load_prompt,
    classify,
    raise_priority
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_CASES = [
    {
        "note": "My ankle is swollen after playing football",
        "category": "injury",
        "priority": "today"
    },
    {
        "note": "Feeling feverish and sneezing",
        "category": "fever_cold",
        "priority": "today"
    },
    {
        "note": "Chest pain and difficulty breathing",
        "category": "pain",
        "priority": "see_now"
    },
    {
        "note": "Stomach pain since morning",
        "category": "stomach",
        "priority": "today"
    },
    {
        "note": "My eyes are itchy and watery",
        "category": "allergy",
        "priority": "routine"
    }
]


def run_eval():
    load_dotenv(os.path.join(BASE_DIR, ".env"))

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Missing API key")

    client = genai.Client(api_key=api_key)
    prompt = load_prompt()

    passed = 0

    print("\nFITGATE EVALUATION REPORT")
    print("=" * 75)

    print(
        f"{'Test':<8}{'Expected':<25}"
        f"{'Actual':<25}{'Result'}"
    )

    for number, case in enumerate(TEST_CASES, start=1):
        result, reason = classify(
            client, prompt, case["note"]
        )

        actual_priority = result["priority"]

        # Apply the red-flag Python safety rule.
        from fitgate import contains_red_flag

        if contains_red_flag(case["note"]):
            actual_priority = raise_priority(
                actual_priority, "see_now"
            )

        correct = (
            result["category"] == case["category"]
            and actual_priority == case["priority"]
        )

        if correct:
            passed += 1

        expected = (
            f"{case['category']} / {case['priority']}"
        )

        actual = (
            f"{result['category']} / {actual_priority}"
        )

        print(
            f"{number:<8}{expected:<25}"
            f"{actual:<25}"
            f"{'PASS' if correct else 'FAIL'}"
        )

    accuracy = round(
        passed / len(TEST_CASES) * 100, 2
    )

    print("\nRESULT")
    print(f"Correct: {passed}/{len(TEST_CASES)}")
    print(f"Accuracy: {accuracy}%")


if __name__ == "__main__":
    run_eval()

import os
from dotenv import load_dotenv
from google import genai

from fitgate import (
    load_prompt,
    classify,
    raise_priority
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TEST_CASES = [
    {
        "note": "My ankle is swollen after playing football",
        "category": "injury",
        "priority": "today"
    },
    {
        "note": "Feeling feverish and sneezing",
        "category": "fever_cold",
        "priority": "today"
    },
    {
        "note": "Chest pain and difficulty breathing",
        "category": "pain",
        "priority": "see_now"
    },
    {
        "note": "Stomach pain since morning",
        "category": "stomach",
        "priority": "today"
    },
    {
        "note": "My eyes are itchy and watery",
        "category": "allergy",
        "priority": "routine"
    }
]


def run_eval():
    load_dotenv(os.path.join(BASE_DIR, ".env"))

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("Missing API key")

    client = genai.Client(api_key=api_key)
    prompt = load_prompt()

    passed = 0

    print("\nFITGATE EVALUATION REPORT")
    print("=" * 75)

    print(
        f"{'Test':<8}{'Expected':<25}"
        f"{'Actual':<25}{'Result'}"
    )

    for number, case in enumerate(TEST_CASES, start=1):
        result, reason = classify(
            client, prompt, case["note"]
        )

        actual_priority = result["priority"]

        # Apply the red-flag Python safety rule.
        from fitgate import contains_red_flag

        if contains_red_flag(case["note"]):
            actual_priority = raise_priority(
                actual_priority, "see_now"
            )

        correct = (
            result["category"] == case["category"]
            and actual_priority == case["priority"]
        )

        if correct:
            passed += 1

        expected = (
            f"{case['category']} / {case['priority']}"
        )

        actual = (
            f"{result['category']} / {actual_priority}"
        )

        print(
            f"{number:<8}{expected:<25}"
            f"{actual:<25}"
            f"{'PASS' if correct else 'FAIL'}"
        )

    accuracy = round(
        passed / len(TEST_CASES) * 100, 2
    )

    print("\nRESULT")
    print(f"Correct: {passed}/{len(TEST_CASES)}")
    print(f"Accuracy: {accuracy}%")


if __name__ == "__main__":
    run_eval()
