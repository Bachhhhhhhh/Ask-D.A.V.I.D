# Ask D.A.V.I.D.-Inspired Data Platform

This repository is the infrastructure-first foundation for a governed,
synthetic-data-only data and AI platform. The mandatory architecture contract
is in [`docs/MASTER_GOAL.md`](docs/MASTER_GOAL.md),
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), and the accepted ADRs.

Goal 2 provides development tooling only. It does not provision AWS resources,
configure Databricks, deploy Doris, create OpenSearch collections, implement
tool services, implement LangGraph, or contain Green SM data.

## Quick start

Prerequisites: `uv`, Docker Desktop with Docker Compose, and Python 3.12. GNU
Make is supported for Linux and CI. On this Windows workstation, use the
PowerShell wrapper instead of installing Make.

```powershell
.\scripts\dev.ps1 setup
.\scripts\dev.ps1 validate-env
.\scripts\dev.ps1 test
.\scripts\dev.ps1 local-up
.\scripts\dev.ps1 local-down
```

```bash
make setup
make validate-env
make test
make local-up
make local-down
```

See [development instructions](docs/DEVELOPMENT.md), the
[repository map](docs/REPOSITORY_STRUCTURE.md), and
[security rules](docs/SECURITY.md).
