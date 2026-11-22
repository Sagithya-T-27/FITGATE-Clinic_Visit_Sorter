# FITGATE – Cost and Latency Note

## 1. API Usage

FITGATE sends one LLM request for each non-empty worker note.

For 20 worker records, the normal run requires up to 20 initial LLM calls if all notes are non-empty.

An invalid response or API failure can cause one additional retry.

Empty notes do not require an API call.

## 2. Retry Behaviour

Each note is attempted a maximum of two times.

If both attempts fail, FITGATE uses the fallback:
- category: other
- priority: today
- affects: empty list

Python still checks the original note for red flags.

## 3. Latency

Latency is the time taken for the LLM to respond to one request.

Actual response time depends on:
- Network connection
- Model selected
- API availability
- Length of the input
- Server load

Measured average response time: 3.03 seconds (average of 16 successful API requests).

Total processing time for 20 records: 43.904 seconds (including API rate-limit delays and retries).

## 4. Estimated Cost

Cost depends on the selected model and the number of input and output tokens.

Estimated daily cost:

Total input token cost + Total output token cost.

Daily cost = (Input tokens / 1,000,000 × Input price per million) + (Output tokens / 1,000,000 × Output price per million).

The model's current pricing must be checked before submitting this estimate.

## 5. Conclusion

FITGATE reduces unnecessary API calls by checking empty notes before calling the LLM.

It retries invalid responses only once and uses a safe fallback when the API fails.
