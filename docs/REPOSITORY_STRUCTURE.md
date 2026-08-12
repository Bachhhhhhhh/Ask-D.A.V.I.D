# Repository structure

| Path | Current purpose | Planned owner |
| --- | --- | --- |
| `packages/` | Shared typed Python foundations using `src` layout | Goal 2 |
| `infrastructure/` | Terraform modules for verified Goal 3 and staged Goal 4 AWS/Unity Catalog administration | Goals 3–4 |
| `databricks/` | Goal 4 Declarative Automation Bundle and neutral managed-Iceberg SQL | Goal 4 |
| `doris/` | Reserved for rebuildable serving definitions | Goal 6 |
| `opensearch/` | Reserved for retrieval-layer assets | Goal 7 |
| `services/` | Reserved for controlled tool services | Goal 8 |
| `agents/` | Reserved for the approved LangGraph runtime | Goal 9 |
| `api/` and `frontend/` | Reserved for experience-layer implementation | Goal 11 |
| `policies/` | Reserved for deterministic policy artifacts | Goal 12 |
| `synthetic_data/` and `evaluation/` | Reserved for neutral synthetic assets and release gates | Goal 13 |
| `observability/` | Reserved for cross-cutting tracing and monitoring | Goal 12 |
| `tests/` | Offline smoke and unit tests; future integration/cloud tests are marked | Goal 2 onward |

Every future deployable Python component must be a `uv` workspace member with
its own `pyproject.toml` and `src/<package_name>/` directory. Shared code
belongs in an explicitly versioned common package, not in directory-relative
imports. Goal 4 uses `databricks/databricks.yml` as its single bundle root,
resource declarations under `databricks/bundles/goal_04_lakehouse/`, and
versioned SQL under `databricks/sql/goal_04/`. It does not place Goal 5+
implementation in any reserved area.
