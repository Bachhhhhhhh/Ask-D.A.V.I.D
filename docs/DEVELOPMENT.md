# Development setup

## Supported environment

The repository targets Python 3.12 and uses `uv` for dependency resolution,
virtual environments, and the checked-in `uv.lock` file. Docker Compose is
used only for local PostgreSQL, Redis, and a generic HTTP mock server.

On Windows, use PowerShell:

```powershell
.\scripts\dev.ps1 setup
.\scripts\dev.ps1 format
.\scripts\dev.ps1 lint
.\scripts\dev.ps1 typecheck
.\scripts\dev.ps1 test
.\scripts\dev.ps1 check
.\scripts\dev.ps1 databricks-static
.\scripts\dev.ps1 goal5-static
.\scripts\dev.ps1 local-up
.\scripts\dev.ps1 local-down
.\scripts\dev.ps1 clean
```

On GNU Make environments, use the equivalent `make` commands. Both wrappers
dispatch to `scripts/dev.py`; command behavior must remain identical.

## Configuration

Copy `.env.example` to `.env` only when a local override is necessary. The
example contains non-secret loopback hosts, ports, and local identifiers only.
`validate-env` validates required values and port ranges without contacting a
network service:

```powershell
.\scripts\dev.ps1 validate-env
```

Never commit `.env`, passwords, tokens, AWS credentials, Databricks tokens,
database credentials, or generated local configuration.

## Testing

`test` runs offline smoke and unit tests, excluding `integration` and `cloud`
markers. It creates a coverage report and requires 90% branch coverage for the
platform-foundation and ingestion packages. Future local-service tests must use the `integration`
marker; tests that need cloud credentials must use the `cloud` marker.

`check` runs format verification, linting, strict typing, tests, Goal 4 and
Goal 5 static contracts, and local security checks. `pre-commit run --all-files` executes the same style and
secret-protection hooks used before review.

`databricks-static` is credential-free. It checks the approved catalog/schema
hierarchy, staged Terraform gate, existing-metastore and warehouse references,
bundle job/file contract, seven explicit `USING ICEBERG` table definitions,
absence of `LOCATION` and Delta substitutions, negative-test definitions, and
common credential assignments. It does not authenticate, validate against a
workspace, deploy a bundle, start a warehouse, or execute SQL.

`goal5-static` validates the synthetic contracts, fixtures, managed-table SQL,
bundle resource, and Terraform source-object boundary. It is also
credential-free and does not contact AWS or Databricks.

## Local limitations

Compose services are local development dependencies only. PostgreSQL and Redis
are not substitutes for managed production services. MockServer is generic and
does not emulate AWS, Databricks, Doris, OpenSearch Serverless, controlled tool
services, agents, data access, or Green SM behavior. Do not use local trust
authentication outside loopback development.
