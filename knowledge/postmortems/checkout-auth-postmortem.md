# Checkout Auth Mismatch Postmortem

An environment configuration drift introduced a staging token issuer into the production checkout service. The issue was mitigated by reverting the configuration and adding a release validation check.
