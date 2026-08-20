# Goal 6 private admin-refresh retry — client-option blocker

Date: 2026-08-13
Environment: development only (`736956442295`, `ap-southeast-1`)
Task definition: `ask-david-development-doris-admin-refresh:2`
Image digest: `sha256:41095093cb0cc820eb8b15afedacf97333ba443de8216de9dc40b950becee57d`

## Execution evidence

Exactly one post-remediation private ECS task was launched after explicit
approval:

- cluster: `ask-david-development-cluster`;
- task ARN:
  `arn:aws:ecs:ap-southeast-1:736956442295:task/ask-david-development-cluster/2bc021ad5b834f8fa8abfbca432a32a5`;
- subnet: `subnet-034f5f1c9bca753f1`;
- private IPv4: `10.42.30.171`;
- security group: `sg-07a0dd2e8af8aa178`;
- `assignPublicIp=DISABLED`.

The task reached `STOPPED` with `EssentialContainerExited` and container exit
code `7`. No retry was performed.

## Sanitized CloudWatch result

```text
mysql: Deprecated program name. It will be removed in a future release, use '/usr/bin/mariadb' instead
mysql: unknown variable 'ssl-mode=REQUIRED'
```

The required `admin-refresh` completed marker was absent. The failure is a
client compatibility defect: the image installs Alpine `mariadb-client`, whose
`mysql` binary rejects the MySQL-specific `--ssl-mode=REQUIRED` option used by
the Goal 6 runners. Doris, Unity Catalog, S3, and network interoperability
remain unverified.

## Stop condition

The task was not retried. The next step is an offline remediation design that
chooses and statically validates the MariaDB-compatible TLS option, updates all
affected Goal 6 runners and regression tests, rebuilds/scans/pushes a new
immutable image, and obtains separate approvals for any subsequent task
definition plan/apply and one retry. No source or AWS mutation was performed
for this diagnosis.
