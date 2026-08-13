# Goal 5 Phase 5-8 bundle deployment and inspection

Date: 2026-08-12  
Scope: one approved deployment of the reviewed development bundle and immediate
read-only inspection. No job or SQL task execution was authorized or performed.

## Pre-deployment guards

| Check | Result |
| --- | --- |
| Full bundle source aggregate | PASS — `eb4c7e6db55d9ec5aedf63480ecf00bb5cd404b9b64ddc1f4930d87ab1060368` |
| Databricks workspace | PASS — `7474644358733471` |
| Unity Catalog metastore | PASS — `3a7f7e7a-680b-4bd6-907a-6d5e77b43178` |
| Warehouse | PASS — `757e0335c6efb51e`, existing Serverless Small/PRO, stopped, auto-stop 10 minutes |
| New Goal 5 job before deployment | PASS — absent |

## Deployment result

The named development profile deployed the exact reviewed source set to:

```text
/Workspace/Users/bachvxuan@gmail.com/.bundle/ask-david-goal-04-lakehouse/development
```

The CLI returned:

```text
Deployment complete!
```

## Read-only post-deployment inspection

| Check | Result |
| --- | --- |
| New job | PASS — `ask-david-development-goal5-synthetic-ingestion`, ID `382877731318442` |
| Existing Goal 4 job identities | PASS — all five reviewed IDs/names unchanged; exactly one project job identity was added |
| Task graph | PASS — six SQL tasks: create tables; three parallel source ingestions; output verification; idempotency verification |
| Run-as identity | PASS — existing workflow service principal `b2bdec62-62db-432d-bc6f-1f92b78053b0` |
| Warehouse | PASS — every task references existing `757e0335c6efb51e` |
| Concurrency/queue | PASS — `max_concurrent_runs=1`, queue disabled |
| Synced files | PASS — exactly the six Goal 5 SQL files exist under `files/sql/goal_05` |
| Synced file contents | PASS — all six exported files byte-match local source |
| Job ACL | PASS — governance administrator/group manage, data-engineer group run, denied service principal view-only |
| Bundle-root/file ACL | PASS — denied service principal has view/read only, not run/manage |
| Active Goal 5 runs | PASS — none |
| Warehouse after deployment | PASS — `STOPPED`, zero active sessions, zero clusters |

The byte-matched SQL SHA-256 values are:

| File | SHA-256 |
| --- | --- |
| `01_create_goal5_tables.sql` | `6fb05cdc70e1e82be201ac9efa810e99cc34989c55b924f148075b44028104d0` |
| `02_ingest_structured_csv.sql` | `467c5500aa55f037fdd7dea6860afd621968749aafbf40eec60d375deb4e162c` |
| `03_ingest_document.sql` | `1e60974da30a6fccd7344497589a29d2ceb901a700bfd887280061fc5839c831` |
| `04_ingest_cdc.sql` | `15978eda94fc1605c076a4d55c75c4c837b0dd43293ec4a3477659935c7d0b09` |
| `05_verify_goal5_outputs.sql` | `dd70f9b21b50e8e708478ef5ab9e2d3ff500e02879441b99b055468fdbfd9eb8` |
| `06_verify_goal5_idempotency.sql` | `1a1f379726315107618a06001b37fc4fe8ddbf94f0cf48ea47976301e6094ecb` |

## Boundary

No job/SQL task ran, no warehouse or cluster was created, no Terraform or AWS
operation occurred, and no deployment retry occurred. Goal 5 remains
unverified.

The next separate approval is for exactly one run of job `382877731318442` on
the existing Serverless Small warehouse `757e0335c6efb51e`. Before that run,
report the warehouse's cost-sensitive state. Stop immediately on any failed
task; do not retry, redeploy, or mutate source/table configuration without a
new review.
