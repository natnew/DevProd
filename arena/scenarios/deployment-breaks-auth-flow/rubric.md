# Rubric

## Diagnosis

- Full credit: Identifies production `AUTH_ISSUER` drift to the staging issuer as the primary root cause and scopes the issue to `checkout-api` token validation after deployment `2026.03.16-1`.
- Partial credit: Correctly identifies an authentication configuration problem but does not isolate the issuer mismatch or overstates the deployment as the sole cause.
- Failure: Attributes the incident to key rotation, identity provider outage, database issues, or generic auth instability without evidence.

## Evidence Use

- Full credit: Cites the deployment/config timestamps, issuer mismatch log message, and at least one retrieved knowledge document.
- Partial credit: Uses some raw evidence but fails to connect it into a clear causal chain or ignores retrieved knowledge.
- Failure: Makes unsupported claims or relies on evidence not present in the scenario.

## Remediation

- Full credit: Recommends correcting or rolling back `AUTH_ISSUER`, validating the production issuer after the fix, and adding deployment-time safeguards.
- Partial credit: Suggests rollback or config correction but omits verification or follow-up prevention.
- Failure: Recommends destructive or irrelevant actions such as rotating keys, restarting unrelated services, or changing databases.

## Uncertainty Handling

- Full credit: States any remaining uncertainty narrowly and proposes sensible next checks if direct config confirmation is unavailable.
- Partial credit: Acknowledges uncertainty but does not tie it to concrete follow-up checks.
- Failure: Overstates confidence without confirming the config path, or refuses to act despite sufficient evidence.
