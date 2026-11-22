# FITGATE – Evaluation Results

## 1. Purpose

The evaluation harness tests whether FITGATE correctly classifies worker notes according to the expected category and priority.

Five predefined test notes were used.

## 2. Test Results

| Test | Input | Expected | Actual | Result |
|---|---|---|---|---|
| 1 | My ankle is swollen after playing football | injury / today | [Actual] | [PASS/FAIL] |
| 2 | Feeling feverish and sneezing | fever_cold / today | [Actual] | [PASS/FAIL] |
| 3 | Chest pain and difficulty breathing | pain / see_now | [Actual] | [PASS/FAIL] |
| 4 | Stomach pain since morning | stomach / today | [Actual] | [PASS/FAIL] |
| 5 | My eyes are itchy and watery | allergy / routine | [Actual] | [PASS/FAIL] |

## 3. Accuracy

Accuracy = (Number of correct predictions / Total test cases) × 100

Correct predictions: [Enter number]

Total test cases: 5

Accuracy: [Enter actual percentage]

## 4. Observations

[Explain which tests passed and which tests failed.]

## 5. Improvements

[Describe the prompt or Python changes made after testing.]

## 6. Conclusion

The evaluation results show how accurately FITGATE handled the five selected test inputs. This is a small test set and does not prove that the application is always correct or medically reliable.