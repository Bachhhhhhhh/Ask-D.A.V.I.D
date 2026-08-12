# Development security rules

## Secrets

- Do not commit `.env` files, credentials, private keys, tokens, or connection
  passwords.
- `.env.example` may contain only non-secret development defaults.
- Use secret references and workload identity for deployments. Goal 4 models
  an AWS IAM role behind a Unity Catalog storage credential. Its initial trust
  allows only the Databricks UC principal with the exact external ID; a second
  approved in-place update adds self-assumption after the role exists. It never
  stores static AWS keys, PATs, OAuth tokens, or service-principal secrets in
  Terraform or bundle inputs.
- Report an exposed secret through the project security process and rotate it
  outside this repository before removing it from history.

## Automated checks

Pre-commit runs file hygiene, YAML validation, Ruff, mypy, and
`detect-secrets`. Local `security` runs Bandit, pip-audit, and detect-secrets.
CI adds Gitleaks and CodeQL. Dependency and action updates are reviewed through
Dependabot.

Goal 4 grants data access only through Unity Catalog. Its IAM policy is limited
to approved managed prefixes and the existing storage KMS key. Data users and
service principals receive no direct external-location, S3, or KMS access.
Terraform owns one zero-byte, trailing-slash marker in each approved managed
root so Databricks can validate path existence without weakening IAM scope.
Markers use the existing storage KMS key and contain no synthetic records.
The denied test principal has SQL/workspace entitlement only and is expected
to fail both protected-table and direct-path queries. An error caused by
syntax, networking, or missing objects is not authorization evidence.

## Local services

Docker Compose binds local dependencies to `127.0.0.1`. Its PostgreSQL trust
mode exists only to avoid checked-in passwords and must not be used in staging
or production. The generic mock fixtures are not service contracts and contain
no real data.
