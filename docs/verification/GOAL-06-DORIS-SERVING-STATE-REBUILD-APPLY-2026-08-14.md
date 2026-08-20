# Goal 6 Doris serving-state rebuild — apply evidence

Date: 2026-08-14
Environment: development only (`736956442295`, `ap-southeast-1`)
Saved-plan SHA-256: `ce05eb8cd3b1a90b3c80b424bdae8bf99bc6a909e9a7e55dd27b3cd0c976da6c`

## Authorization and apply result

The exact saved plan was approved for the reviewed account and region. The
artifact hash matched immediately before apply. Terraform reported:

```text
Apply complete! Resources: 6 added, 0 changed, 4 destroyed.
```

The four destroys were the old FE/BE instance attachments and old FE/BE EC2
instances required by replacement. The two old serving-data EBS volumes were
not deleted. No task, SQL/job, bundle, ECR, Databricks, IAM, KMS, network,
security-group, production, or public-exposure operation was performed.

## New resources

| Component | Result |
| --- | --- |
| FE instance | `i-090c3b9f82d518c68`, running, private `10.42.64.238`, no public IP |
| BE instance | `i-0770ba92b183cbdb8`, running, private `10.42.71.97`, no public IP |
| FE root volume | `vol-0aa76293eb6ddae3d`, encrypted gp3, 30 GiB, `/dev/xvda`, `DeleteOnTermination=true` |
| BE root volume | `vol-04d445b3f20bf2b80`, encrypted gp3, 30 GiB, `/dev/xvda`, `DeleteOnTermination=true` |
| FE fresh data volume | `vol-0e8c9175fe79619be`, encrypted gp3, 20 GiB, `/dev/sdf`, `DeleteOnTermination=false` |
| BE fresh data volume | `vol-0b4799bdf2215d397`, encrypted gp3, 50 GiB, `/dev/sdf`, `DeleteOnTermination=false` |
| EC2 health | Both `SystemStatus=ok` and `InstanceStatus=ok` at inspection time |

The old data volumes remain available and preserved:

- FE: `vol-012bc3410278ed85e`, 20 GiB, encrypted, detached;
- BE: `vol-01e9b0ed05f7b92b9`, 50 GiB, encrypted, detached.

No cleanup plan has been created or applied.

## Listener verification

| Check | Result |
| --- | --- |
| FE host prerequisites/private IP | PASS — console evidence shows the expected private-IP and host-prerequisite markers |
| FE container | PASS — running, exit code 0, no reported Docker error |
| FE port 9030 | PASS — console output contains the serial-console-mangled equivalent of the `doris-port-ready` marker |
| BE host prerequisites/private IP | PASS — console evidence shows the expected private-IP and host-prerequisite markers |
| BE container | PARTIAL — running, exit code 0, no reported Docker error |
| BE port 9050 | FAIL — after the bounded guard, console evidence reports `listener_state=unavailable` and the `doris-port-unavailable` marker for 9050 |

The prior 8 GiB root-disk failure is not present: both replacement root
volumes are encrypted 30 GiB gp3 volumes and the console output contains no
`no space left on device` or Docker image-unpack failure. This does not prove
BE application readiness. The BE container remains running with exit code 0,
but its bounded local listener guard failed and cloud-init reports the
`scripts-user` module failure caused by that non-zero bootstrap result. The
redacted diagnostic classification is `log_signal=configuration`; no raw
secret-bearing logs were retrieved.

Because this result occurred on a newly created 50 GiB BE data volume, the
earlier persisted-volume/metadata hypothesis is not sufficient to explain the
BE failure. The next remediation must inspect or correct the declarative BE
startup/configuration path (including the image entrypoint's FE registration
handshake and TLS-compatible control connection) rather than delete another
serving-data volume.

## Checkpoint

Goal 6 remains **BLOCKED** at BE listener readiness. Do not run either ECS
verifier/admin task, delete the preserved old volumes, or perform another
Terraform plan/apply until the BE readiness evidence is reviewed and a
separate approval is given for any remediation.
