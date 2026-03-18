# Rubric

## Diagnosis

- Full credit: Identifies the incompatible dependency upgrade in `billing-worker` as the root cause of message deserialization failures and resulting queue backlog.
- Partial credit: Recognizes the worker rollout as causal but does not isolate the dependency compatibility problem.
- Failure: Attributes the incident to database locks, queue infra outage, or generic worker overload without evidence.

## Evidence Use

- Full credit: Uses the rollout timing, deserialization log details, and absence of database contention to support the diagnosis.
- Partial credit: Uses some evidence but fails to rule out the main distractor.
- Failure: Ignores source data or cites nonexistent evidence.

## Remediation

- Full credit: Recommends rollback or dependency pinning, then safe job reprocessing and compatibility validation.
- Partial credit: Suggests rollback but omits follow-up validation or reprocessing.
- Failure: Recommends irrelevant database tuning or blind worker restarts.

## Uncertainty Handling

- Full credit: Notes any remaining uncertainty around exact version boundaries while still recommending a safe rollback path.
- Partial credit: Mentions uncertainty without a next check.
- Failure: Overstates confidence without validating the dependency change.
