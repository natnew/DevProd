# Rubric

## Diagnosis

- Full credit: Identifies the disabled hot cache path as the root cause of the latency spike and scopes the problem to `catalog-api` cache behavior.
- Partial credit: Recognizes a cache problem but does not isolate the configuration change.
- Failure: Blames traffic spikes, database pressure, or generic Redis instability without supporting evidence.

## Evidence Use

- Full credit: Uses the config change timing, cache miss surge, and Redis timeout logs together.
- Partial credit: Uses some evidence but does not tie it into a causal story.
- Failure: Ignores the key cache-path evidence or cites absent artifacts.

## Remediation

- Full credit: Recommends restoring the cache path, validating hit ratio and latency, and adding config safeguards.
- Partial credit: Suggests rollback without follow-up validation.
- Failure: Recommends scaling traffic, tuning databases, or flushing caches without evidence.

## Uncertainty Handling

- Full credit: Notes any uncertainty around secondary Redis pressure while keeping the main fix focused on the cache config.
- Partial credit: Mentions uncertainty without a check plan.
- Failure: Avoids action despite clear config correlation.
