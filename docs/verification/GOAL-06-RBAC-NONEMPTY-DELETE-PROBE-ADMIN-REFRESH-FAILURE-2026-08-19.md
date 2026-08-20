# Goal 6 non-empty DELETE probe admin-refresh failure — 2026-08-19

## Approved scope

One private, no-retry admin-refresh using:

- task definition `ask-david-development-doris-admin-refresh:13`;
- ECR digest `sha256:b2a4629e1e207fa9b2d06cdca5956472f6e4f94e4f40723a5bc45f1a18b17a73`;
- cluster `ask-david-development-cluster`;
- approved private application subnets and admin security group;
- FE `10.42.64.238` and BE `10.42.71.97`.

The task was permitted to apply controlled, versioned disposable-Doris schema
migrations and refresh the one allowlisted serving copy. It was not permitted
to write Unity Catalog, S3, or the authoritative lakehouse source.

## Connected evidence

| Check | Result |
| --- | --- |
| Task | `940a073e99c74c2ba67129130549e830` |
| Task-definition revision | PASS — `13` |
| Placement | PASS — private subnet `subnet-034f5f1c9bca753f1`, ENI `eni-0ff4a6208fd4b4ca2`, private IPv4 `10.42.21.33` |
| Public IP | PASS — disabled by approved `awsvpc` configuration |
| Task outcome | FAIL — container `doris-admin` exited `1` |
| Retry | PASS — none |
| Completion marker | FAIL — absent |

Raw CloudWatch events were intentionally not printed because task logs must
never be treated as safe containers for credentials. Read-only, count-only
inspection established one `ERROR 1105` event and a `TINYINT` error marker.

## Confirmed mismatch

The version-controlled schema defines the disposable probe key as:

```sql
probe_id TINYINT NOT NULL
```

The same manifest then inserts neutral upper sentinel `128`. Apache Doris
signed `TINYINT` values end at `127`; therefore the controlled sentinel cannot
be stored in this schema. This is consistent with the safe CloudWatch error
classification and occurs before the task can emit its completion marker.

No authoritative source, Unity Catalog object, S3 object, AWS infrastructure
resource, or task definition was changed by this failed task.

## Required next step

Do not retry. A separate approval is required for offline analysis and a
declarative remediation that changes only the disposable Doris authorization
probe schema/migration, adds static regression coverage, and runs offline
validation. A new task execution must require a separate approval after review.
