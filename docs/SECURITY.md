# Development security rules

## Secrets

- Do not commit `.env` files, credentials, private keys, tokens, or connection
  passwords.
- `.env.example` may contain only non-secret development defaults.
- Use secret references and workload identity in later deployment goals; this
  repository does not implement them yet.
- Report an exposed secret through the project security process and rotate it
  outside this repository before removing it from history.

## Automated checks

Pre-commit runs file hygiene, YAML validation, Ruff, mypy, and
`detect-secrets`. Local `security` runs Bandit, pip-audit, and detect-secrets.
CI adds Gitleaks and CodeQL. Dependency and action updates are reviewed through
Dependabot.

## Local services

Docker Compose binds local dependencies to `127.0.0.1`. Its PostgreSQL trust
mode exists only to avoid checked-in passwords and must not be used in staging
or production. The generic mock fixtures are not service contracts and contain
no real data.
