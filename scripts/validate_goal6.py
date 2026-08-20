"""Offline static validation for the Goal 6 Apache Doris serving contract."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _read(root: Path, relative_path: str, errors: list[str]) -> str:
    path = root / relative_path
    if not path.is_file():
        errors.append(f"missing Goal 6 source: {relative_path}")
        return ""
    return path.read_text(encoding="utf-8")


def validate_goal6_repository(repository_root: Path = REPOSITORY_ROOT) -> list[str]:
    """Return deterministic Goal 6 contract errors without cloud access."""
    errors: list[str] = []
    required_paths = (
        "infrastructure/environments/development/goal6.tf",
        "infrastructure/environments/development/goal6_reconciliation_imports.tf",
        "infrastructure/environments/development/goal6_variables.tf",
        "infrastructure/environments/development/goal6_secrets.tf",
        "infrastructure/modules/doris-serving/main.tf",
        "infrastructure/modules/doris-verifier/main.tf",
        "infrastructure/modules/network/outputs.tf",
        "infrastructure/modules/kms/outputs.tf",
        "infrastructure/modules/iam/main.tf",
        "infrastructure/modules/iam/variables.tf",
        "infrastructure/modules/databricks-identities/main.tf",
        "infrastructure/modules/databricks-lakehouse/main.tf",
        "infrastructure/modules/databricks-lakehouse/variables.tf",
        "databricks/databricks.yml",
        "databricks/bundles/goal_06_doris/resources.yml",
        "databricks/sql/goal_06/01_apply_controlled_increment.sql",
        "databricks/sql/goal_06/02_verify_controlled_increment.sql",
        "doris/catalogs/unity_catalog_iceberg_rest.properties.tmpl",
        "doris/schemas/01_serving_database.sql",
        "doris/schemas/02_readonly_workload_and_audit.sql",
        "doris/migrations/01_bootstrap_internal_serving.sql",
        "doris/migrations/04_recreate_authorization_probe.sql",
        "doris/materialized_views/01_serving_data_freshness.sql",
        "doris/migrations/02_refresh_from_unity_catalog.sql.tmpl",
        "doris/migrations/03_rebuild_internal_serving.sql",
        "docker/Dockerfile.doris-verifier",
        "docker/doris-verifier/doris-admin-refresh",
        "docker/doris-verifier/doris-readonly-verify",
        "docker/doris-verifier/doris-rbac-verify",
        "docker/doris-verifier/doris-query-limit-verify",
        "docker/doris-verifier/doris-audit-verify",
        "docker/doris-verifier/doris-rebuild-serving",
        "infrastructure/scripts/run-goal6-admin-refresh.ps1",
        "infrastructure/scripts/run-goal6-admin-refresh.sh",
        "infrastructure/scripts/run-goal6-admin-operation.sh",
        "infrastructure/scripts/run-goal6-verifier.sh",
        "infrastructure/scripts/run-goal6-fe-health.ps1",
        "infrastructure/scripts/run-goal6-readiness-markers.ps1",
        "infrastructure/scripts/run-goal6-readiness-markers.sh",
        "synthetic_data/goal_06/structured/goal6_increment.csv",
    )
    sources = {relative: _read(repository_root, relative, errors) for relative in required_paths}
    if errors:
        return errors

    variables = sources["infrastructure/environments/development/goal6_variables.tf"]
    goal6_tf = sources["infrastructure/environments/development/goal6.tf"]
    reconciliation_imports = sources[
        "infrastructure/environments/development/goal6_reconciliation_imports.tf"
    ]
    serving = sources["infrastructure/modules/doris-serving/main.tf"]
    verifier = sources["infrastructure/modules/doris-verifier/main.tf"]
    network_outputs = sources["infrastructure/modules/network/outputs.tf"]
    kms_outputs = sources["infrastructure/modules/kms/outputs.tf"]
    iam = sources["infrastructure/modules/iam/main.tf"]
    iam_variables = sources["infrastructure/modules/iam/variables.tf"]
    development_main = _read(
        repository_root, "infrastructure/environments/development/main.tf", errors
    )
    if not development_main:
        return errors
    identities = sources["infrastructure/modules/databricks-identities/main.tf"]
    lakehouse = sources["infrastructure/modules/databricks-lakehouse/main.tf"]
    lakehouse_variables = sources["infrastructure/modules/databricks-lakehouse/variables.tf"]
    root_bundle = sources["databricks/databricks.yml"]
    bundle = sources["databricks/bundles/goal_06_doris/resources.yml"]
    increment_sql = sources["databricks/sql/goal_06/01_apply_controlled_increment.sql"]
    verify_sql = sources["databricks/sql/goal_06/02_verify_controlled_increment.sql"]
    catalog_template = sources["doris/catalogs/unity_catalog_iceberg_rest.properties.tmpl"]
    serving_ddl = sources["doris/schemas/01_serving_database.sql"]
    security_ddl = sources["doris/schemas/02_readonly_workload_and_audit.sql"]
    bootstrap_manifest = sources["doris/migrations/01_bootstrap_internal_serving.sql"]
    probe_migration = sources["doris/migrations/04_recreate_authorization_probe.sql"]
    refresh_ddl = sources["doris/migrations/02_refresh_from_unity_catalog.sql.tmpl"]
    rebuild_ddl = sources["doris/migrations/03_rebuild_internal_serving.sql"]
    admin_task_wrapper = sources["infrastructure/scripts/run-goal6-admin-refresh.ps1"]
    admin_task_shell_wrapper = sources[
        "infrastructure/scripts/run-goal6-admin-refresh.sh"
    ]
    admin_operation_shell_wrapper = sources[
        "infrastructure/scripts/run-goal6-admin-operation.sh"
    ]
    verifier_task_shell_wrapper = sources[
        "infrastructure/scripts/run-goal6-verifier.sh"
    ]
    health_task_wrapper = sources["infrastructure/scripts/run-goal6-fe-health.ps1"]
    readiness_marker_wrapper = sources[
        "infrastructure/scripts/run-goal6-readiness-markers.ps1"
    ]
    readiness_marker_shell_wrapper = sources[
        "infrastructure/scripts/run-goal6-readiness-markers.sh"
    ]
    dockerfile = sources["docker/Dockerfile.doris-verifier"]
    fixture = sources["synthetic_data/goal_06/structured/goal6_increment.csv"]

    if not re.search(r'variable\s+"goal_6_enabled".*?default\s*=\s*false', variables, re.DOTALL):
        errors.append("goal_6_enabled must default to false")
    if not re.search(
        r'variable\s+"goal_6_verifier_tasks_enabled".*?default\s*=\s*false',
        variables,
        re.DOTALL,
    ):
        errors.append(
            "Goal 6 verifier task definitions must default to false until ECR push approval"
        )
    for marker in (
        'default     = "m7i.xlarge"',
        "goal_6_fe_instance_type",
        "goal_6_be_instance_type",
    ):
        if marker not in variables:
            errors.append("Goal 6 must use the approved m7i.xlarge development sizing")
    if "@sha256:[a-f0-9]{64}$" not in variables:
        errors.append("Goal 6 must require digest-pinned images when enabled")
    if (
        "var.goal_6_fe_data_volume_gib >= 20" not in variables
        or "var.goal_6_be_data_volume_gib >= 50" not in variables
    ):
        errors.append("Goal 6 must retain encrypted FE 20 GiB and BE 50 GiB minimum volumes")
    for marker in (
        'variable "goal_6_rebuild_serving_state"',
        "default     = false",
        "rebuild_serving_state     = var.goal_6_rebuild_serving_state",
    ):
        if marker not in variables + goal6_tf:
            errors.append(f"Goal 6 serving-state rebuild gate is missing: {marker}")
    for marker in (
        'variable "goal_6_fe_root_volume_gib"',
        'variable "goal_6_be_root_volume_gib"',
        'variable "goal_6_fe_private_ip"',
        'variable "goal_6_be_private_ip"',
        'default     = "10.42.64.238"',
        'default     = "10.42.71.97"',
        'variable "goal_6_be_bootstrap_generation"',
        'variable "goal_6_fe_bootstrap_generation"',
        "default     = 30",
        "default     = 2",
        "var.goal_6_fe_root_volume_gib >= 30",
        "var.goal_6_be_root_volume_gib >= 30",
    ):
        if marker not in variables:
            errors.append(f"Goal 6 bootstrap remediation is missing root-volume guard: {marker}")
    for marker in (
        "module.doris_serving.aws_instance.fe[0]",
        "i-074e456efa350b444",
        "module.doris_serving.aws_volume_attachment.fe[0]",
        "/dev/sdf:vol-012bc3410278ed85e:i-074e456efa350b444",
        "module.doris_serving.aws_volume_attachment.be[0]",
        "/dev/sdf:vol-01e9b0ed05f7b92b9:i-05b409f7992294844",
    ):
        if marker not in reconciliation_imports:
            errors.append(f"Goal 6 partial-apply reconciliation is missing import target: {marker}")
    if reconciliation_imports.count("for_each = var.goal_6_enabled") != 3:
        errors.append("Goal 6 partial-apply imports must remain disabled with the foundation gate")

    for marker in (
        'module "doris_serving"',
        'module "doris_verifier"',
        "private_ip                  = var.fe_private_ip",
        "private_ip                  = var.be_private_ip",
        "expected_private_ip = var.fe_private_ip",
        "expected_private_ip = var.be_private_ip",
        "precondition {",
        "selected_subnet_ipv4_hosts",
        'can(regex("/20$", data.aws_subnet.selected[0].cidr_block))',
        "range(0, 16)",
        "range(0, 256)",
        "cidrhost(",
        "data.aws_subnet.selected[0].cidr_block",
        "contains(local.selected_subnet_ipv4_hosts, var.fe_private_ip)",
        "contains(local.selected_subnet_ipv4_hosts, var.be_private_ip)",
        "associate_public_ip_address = false",
        'server_side_encryption = "aws:kms"',
        "goal6_increment.csv",
        ):
        if marker not in goal6_tf + serving:
            errors.append(
                f"Goal 6 Terraform is missing required private/synthetic control: {marker}"
            )
    for marker in (
        "fe_private_ip             = var.goal_6_fe_private_ip",
        "be_private_ip             = var.goal_6_be_private_ip",
    ):
        if marker not in goal6_tf:
            errors.append(f"Goal 6 environment wiring is missing Terraform-managed private IP: {marker}")
    if "0.0.0.0/0" in serving and not re.search(r"from_port\s*=\s*443", serving):
        errors.append("Goal 6 may use public CIDR only for outbound HTTPS, never ingress")
    if re.search(r"aws_vpc_security_group_ingress_rule[\\s\\S]{0,500}cidr_ipv4", serving):
        errors.append("Goal 6 FE/BE ingress must use dedicated security groups, not CIDRs")
    scoped_trivy_exceptions = (
        '#trivy:ignore:AVD-AWS-0104\nresource "aws_vpc_security_group_egress_rule" "fe_https"',
        '#trivy:ignore:AVD-AWS-0104\nresource "aws_vpc_security_group_egress_rule" "be_https"',
    )
    if any(exception not in serving for exception in scoped_trivy_exceptions):
        errors.append("Goal 6 must scope the HTTPS-only Trivy exception to each egress resource")
    if serving.count("#trivy:ignore:AVD-AWS-0104") != 2:
        errors.append("Goal 6 must not expand the Trivy exception beyond FE and BE HTTPS egress")
    if serving.count('cidr_ipv4         = "0.0.0.0/0"') != 2:
        errors.append("Goal 6 must retain exactly two public-CIDR rules for private HTTPS egress")
    if serving.count("from_port         = 443") != 2:
        errors.append("Goal 6 must retain exactly two HTTPS-only public-CIDR egress rules")
    if "There is no public ingress on this resource." not in serving:
        errors.append("Goal 6 must document why its scoped Trivy exception is safe")
    if not all(
        port in goal6_tf + serving
        for port in ("8030", "8040", "9030", "9020", "9050", "9060", "8060", "9010")
    ):
        errors.append("Goal 6 must declare only the documented private Doris FE/BE ports")
    for marker in (
        'resource "aws_vpc_security_group_ingress_rule" "be_to_fe_registration"',
        'resource "aws_vpc_security_group_egress_rule" "be_to_fe_registration"',
        'resource "aws_vpc_security_group_ingress_rule" "be_to_fe_rpc"',
        'resource "aws_vpc_security_group_egress_rule" "be_to_fe_rpc"',
        'resource "aws_vpc_security_group_egress_rule" "fe_to_be"',
        'referenced_security_group_id = aws_security_group.fe[0].id',
        'referenced_security_group_id = aws_security_group.be[0].id',
        'from_port                    = 9030',
        'from_port                    = 9020',
        'toset(["8040", "9050", "9060", "8060"])',
    ):
        if marker not in serving:
            errors.append(
                f"Goal 6 is missing a private bidirectional Doris cluster rule: {marker}"
            )
    if 'metadata_options { http_tokens = "required" }' not in serving:
        errors.append("Goal 6 EC2 instances must require IMDSv2")
    if "encrypted         = true" not in serving or 'type              = "gp3"' not in serving:
        errors.append("Goal 6 EBS volumes must be encrypted gp3")
    for marker in (
        'resource "aws_ebs_volume" "fe_data_rebuild"',
        'resource "aws_ebs_volume" "be_data_rebuild"',
        "var.enabled && var.rebuild_serving_state",
        "frontend-metadata-rebuild",
        "backend-serving-data-rebuild",
        "StateRecovery = \"explicit-goal6-rebuild\"",
        "prevent_destroy = true",
        "var.rebuild_serving_state ? aws_ebs_volume.fe_data_rebuild[0].id",
        "var.rebuild_serving_state ? aws_ebs_volume.be_data_rebuild[0].id",
    ):
        if marker not in serving:
            errors.append(f"Goal 6 rebuild must preserve old volumes and gate new state: {marker}")
    for marker in (
        "volume_size = var.fe_root_volume_gib",
        "volume_size = var.be_root_volume_gib",
        'fe_user_data = var.enabled ? join("\\n", [',
        'be_user_data = var.enabled ? join("\\n", [',
        'fe_user_data_size_check = var.enabled ? join("\\n", [',
        'be_user_data_size_check = var.enabled ? join("\\n", [',
        'check "ec2_user_data_is_within_aws_limit"',
        "length(local.fe_user_data_size_check) <= 16384",
        "length(local.be_user_data_size_check) <= 16384",
        'volume_id           = "vol-0123456789abcdef0"',
        "user_data                   = local.fe_user_data",
        "user_data                   = local.be_user_data",
        "user_data_replace_on_change = true",
        "Goal 6 BE bootstrap generation: ${var.be_bootstrap_generation}",
        "Goal 6 FE bootstrap generation: ${var.fe_bootstrap_generation}",
    ):
        if marker not in serving:
            errors.append(f"Goal 6 EC2 bootstrap remediation is missing {marker}")
    if serving.count("user_data_replace_on_change = true") != 2:
        errors.append("Goal 6 listener remediation must force reviewed FE and BE bootstrap replacements")
    if serving.count(']) : ""') < 4:
        errors.append("Goal 6 disabled mode must skip all four FE/BE bootstrap template renders")
    host_template = _read(
        repository_root,
        "infrastructure/modules/doris-serving/templates/doris-host.sh.tftpl",
        errors,
    )
    for marker in (
        "priority_networks",
        "enable_ssl = true",
        "fe_custom.conf",
        "be_custom.conf",
        "CONFIG_VOLUME=",
        "storage_root_path",
        "medium:hdd",
        "be-storage-root-writable",
        "be-storage-root-unavailable",
        "be-storage-capacity-ready",
        "be-storage-capacity-unavailable",
        "SHOW BACKENDS;",
        "BE_BACKEND_CAPACITY_READY",
        "FE_SERVERS",
        "FE_ID=1",
        "BE_ADDR",
        "doris-port-ready",
        "doris-port-unavailable",
        'ROOT_BOOTSTRAP_LOG="/var/log/goal6-doris-bootstrap.log"',
        "emit_early_status",
        "bootstrap-invoked",
        "bootstrap-failed",
        "goal6_on_exit",
        'trap \'goal6_on_exit "$?"\' EXIT',
        'cat "$ROOT_BOOTSTRAP_LOG" >> "$BOOTSTRAP_STATUS_FILE"',
        "BOOTSTRAP_STATUS_FILE=\"$MOUNT_PATH/$ROLE-log/bootstrap-status.log\"",
        "emit_status",
        "bootstrap-started",
        "container-exited",
        "container-launch-failed",
        "container-diagnostics-summary",
        "host-prerequisites-ready",
        "host-prerequisites-failed",
        "vm.max_map_count = $DORIS_VM_MAX_MAP_COUNT",
        "sysctl -w \"vm.max_map_count=$DORIS_VM_MAX_MAP_COUNT\"",
        "LimitNOFILE=$DORIS_NOFILE_LIMIT",
        "--ulimit \"nofile=$DORIS_NOFILE_LIMIT:$DORIS_NOFILE_LIMIT\"",
        "CONTAINER_DIAGNOSTICS_FILE=\"$MOUNT_PATH/$ROLE-log/container-diagnostics.log\"",
        "DOCKER_RUN_OUTPUT_FILE=\"$MOUNT_PATH/$ROLE-log/docker-run.log\"",
        "timeout --foreground --kill-after=10s 120s docker run",
        "DOCKER_RUN_STATUS=",
        '"force_flush_interval": 5',
        "bootstrap-status.log",
        "bootstrap-root",
        "private-ip-diagnostics.log",
        "container-diagnostics.log",
        "docker-run.log",
        "EXPECTED_PRIVATE_IP",
        "PRIVATE_IP_DIAGNOSTICS_FILE=\"$MOUNT_PATH/$ROLE-log/private-ip-diagnostics.log\"",
        'emit_status "private-ip-configured" "$DORIS_PORT"',
        'emit_status "private-ip-mismatch" "$DORIS_PORT"',
        'emit_status "fe-registration-port-waiting" "$FE_REGISTRATION_PORT"',
        'emit_status "fe-registration-port-ready" "$FE_REGISTRATION_PORT"',
        'emit_status "fe-registration-port-unavailable" "$FE_REGISTRATION_PORT"',
        "FE_REGISTRATION_READY=\"false\"",
        "for _ in $(seq 1 120)",
        "timeout 2 bash -c",
        "docker inspect --format",
        "docker logs --tail 200",
        "emit_container_diagnostic_summary",
        'local listener_state="$${1:-unknown}"',
        'local error_present="false"',
        'local redacted_log_lines="0"',
        'local log_signal="none"',
        'status\\":\\"container-diagnostics-summary',
        'log_signal\\":\\"$log_signal',
        "/dev/tcp/127.0.0.1/$DORIS_PORT",
    ):
        if marker not in serving + host_template:
            errors.append(f"Goal 6 host bootstrap must configure {marker}")

    if "aws_ecr_repository" not in verifier or 'image_tag_mutability = "IMMUTABLE"' not in verifier:
        errors.append("Goal 6 verifier must use an immutable private ECR repository")
    if (
        'requires_compatibilities = ["FARGATE"]' not in verifier
        or 'network_mode             = "awsvpc"' not in verifier
    ):
        errors.append("Goal 6 verifier must be a private Fargate task definition")
    if "assignPublicIp" in verifier:
        errors.append("Goal 6 task definitions must not override private task networking")
    for forbidden in ("s3:GetObject", "s3:PutObject", "secretsmanager:*", "AdministratorAccess"):
        if forbidden in verifier:
            errors.append(f"Goal 6 verifier roles must not contain {forbidden}")
    if "ReadExactAdminSecrets" not in verifier or "ReadExactQuerySecret" not in verifier:
        errors.append("Goal 6 admin and verifier roles must retain distinct exact-secret grants")
    if verifier.count("var.enabled && var.task_definitions_enabled") != 2:
        errors.append(
            "Goal 6 task definitions must be gated until the reviewed ECR image digest exists"
        )

    for marker in (
        'output "aws_endpoints_security_group_id"',
        'output "secrets_key_arn"',
        'variable "goal6_secret_arns"',
        'variable "goal6_secrets_kms_key_arn"',
        'resource "aws_iam_role_policy" "task_execution_goal6_secrets"',
        '"secretsmanager:GetSecretValue"',
        '"kms:Decrypt"',
        'name = "read-goal6-secret-containers"',
    ):
        if marker not in network_outputs + kms_outputs + iam + iam_variables:
            errors.append(f"Goal 6 ECS secret-injection remediation is missing {marker}")
    if 'Resource = var.goal6_secret_arns' not in iam:
        errors.append("Goal 6 execution-role secret access must use exact secret ARN inputs")
    if 'Resource = var.goal6_secrets_kms_key_arn' not in iam:
        errors.append("Goal 6 execution-role KMS access must use the exact secrets key ARN")
    if "secretsmanager:*" in iam or 'Action   = ["kms:*"]' in iam:
        errors.append("Goal 6 execution-role remediation must not grant wildcard secret/KMS actions")
    for marker in (
        'module.network.aws_endpoints_security_group_id',
        'module.doris_verifier.admin_security_group_id',
        'module.doris_verifier.verifier_security_group_id',
        'resource "aws_vpc_security_group_ingress_rule" "goal6_admin_to_aws_endpoints"',
        'resource "aws_vpc_security_group_ingress_rule" "goal6_verifier_to_aws_endpoints"',
        'description                  = "Goal 6 admin task access to existing private AWS interface endpoints only."',
        'description                  = "Goal 6 read-only verifier access to existing private AWS interface endpoints only."',
    ):
        if marker not in goal6_tf:
            errors.append(f"Goal 6 private endpoint remediation is missing {marker}")
    if "cidr_ipv4" in goal6_tf:
        errors.append("Goal 6 interface-endpoint remediation must use SG references, never CIDR ingress")
    if goal6_tf.count('_to_aws_endpoints"') != 2 or goal6_tf.count(
        "security_group_id            = module.network.aws_endpoints_security_group_id"
    ) != 2:
        errors.append(
            "Goal 6 interface-endpoint remediation must contain exactly the admin and verifier SG-to-endpoint rules"
        )
    for marker in (
        'goal6_secret_arns = var.goal_6_enabled ? [',
        'module.secrets.secret_arns["doris/admin"]',
        'module.secrets.secret_arns["doris/external-read-oauth"]',
        'module.secrets.secret_arns["doris/query"]',
        'goal6_secrets_kms_key_arn = var.goal_6_enabled ? module.kms.secrets_key_arn : null',
    ):
        if marker not in development_main:
            errors.append(f"Goal 6 execution-role wiring is missing {marker}")

    if 'resource "databricks_service_principal_secret" "doris_external_read"' not in identities:
        errors.append("Goal 6 must Terraform-manage its Databricks OAuth service-principal secret")
    if 'lifetime             = "2592000s"' not in identities:
        errors.append("Goal 6 OAuth secret must have a bounded lifetime")
    for privilege in ('["USE_CATALOG"]', '["EXTERNAL_USE_SCHEMA", "USE_SCHEMA"]', '["SELECT"]'):
        if privilege not in lakehouse:
            errors.append(f"Goal 6 is missing required least-privilege UC grant {privilege}")
    if not re.search(
        r'variable\s+"doris_external_read_enabled".*?type\s*=\s*bool',
        lakehouse_variables,
        re.DOTALL,
    ):
        errors.append("Goal 6 must use a known Boolean gate for Doris UC grants")
    if "var.doris_external_read_service_principal_application_id != null" in lakehouse:
        errors.append("Goal 6 must not derive grant cardinality from an unknown principal ID")
    if "var.doris_external_read_enabled" not in lakehouse:
        errors.append("Goal 6 must gate Doris UC grants with the known Boolean input")
    for forbidden in ("EXTERNAL_USE_LOCATION", "MODIFY", "CREATE_TABLE"):
        doris_grant_section = lakehouse.split(
            'resource "databricks_grants" "doris_source_table"', 1
        )[-1]
        if forbidden in doris_grant_section:
            errors.append(f"Goal 6 Doris principal must not receive {forbidden}")

    for marker in (
        "iceberg.catalog.type=rest",
        "iceberg.rest.vended-credentials-enabled=true",
        "api/2.1/unity-catalog/iceberg-rest",
        "s3.region=ap-southeast-1",
    ):
        if marker not in catalog_template:
            errors.append(f"Goal 6 Unity Catalog REST template is missing {marker}")
    if re.search(r"(?i)(aws_access_key|secret_access_key|pat\s*=)", catalog_template):
        errors.append("Goal 6 catalog template must not contain static cloud credentials or PATs")
    if (
        "ask_david_serving_development" not in serving_ddl
        or '"replication_num" = "1"' not in serving_ddl
    ):
        errors.append("Goal 6 serving DDL must remain a one-replica, internal development copy")
    for marker in (
        "doris/schemas/01_serving_database.sql",
        "doris/schemas/02_readonly_workload_and_audit.sql",
        "doris/materialized_views/01_serving_data_freshness.sql",
    ):
        if marker not in bootstrap_manifest:
            errors.append(f"Goal 6 bootstrap manifest is missing ordered migration: {marker}")
    if "SOURCE " in bootstrap_manifest:
        errors.append("Goal 6 migration manifest must not depend on a client-only SOURCE command")
    for marker in (
        "CREATE WORKLOAD GROUP IF NOT EXISTS goal6_readonly",
        '"max_concurrency" = "2"',
        '"queue_timeout" = "5000"',
        "SET GLOBAL enable_audit_plugin = true",
    ):
        if marker not in security_ddl:
            errors.append(f"Goal 6 must configure read-only workload/audit control: {marker}")
    if "goal5_structured_business_metrics" not in refresh_ddl or "green_sm_raw" in refresh_ddl:
        errors.append("Goal 6 refresh may read only the allowlisted Business source table")
    for marker in ("TRUNCATE TABLE", "serving_refresh_state", "'SUCCESS'"):
        if marker not in refresh_ddl:
            errors.append(f"Goal 6 controlled serving refresh is missing {marker}")
    if "ask_david_serving_development" not in rebuild_ddl or "green_sm_" in rebuild_ddl:
        errors.append("Goal 6 rebuild may drop only internal serving objects")
    if "goal6_authorization_probe" not in serving_ddl or "goal6_authorization_probe" not in rebuild_ddl:
        errors.append(
            "Goal 6 disposable authorization probe must be created and removed with serving state"
        )

    for marker in (
        "bundles/goal_06_doris/resources.yml",
        "goal6_increment_source_uri:",
        "sql/goal_06/*.sql",
    ):
        if marker not in root_bundle:
            errors.append(f"shared Databricks bundle root is missing Goal 6 marker: {marker}")
    if (
        "goal6_apply_controlled_increment" not in bundle
        or "warehouse_id: ${var.warehouse_id}" not in bundle
    ):
        errors.append("Goal 6 must reuse the approved existing SQL warehouse")
    if re.search(r"(?i)\b(cluster|new_cluster|warehouse)\s*:", bundle):
        errors.append("Goal 6 bundle must not create any cluster or warehouse")
    for marker in (
        "max_concurrent_runs: 1",
        "queue:\n        enabled: false",
        "task_key: apply_controlled_increment",
        "task_key: verify_controlled_increment",
        "depends_on:",
    ):
        if marker not in bundle:
            errors.append(
                f"Goal 6 controlled increment job is missing execution guard: {marker}"
            )
    if "goal6.synthetic.serving.increment" not in increment_sql:
        errors.append("Goal 6 increment SQL must identify only its neutral synthetic dataset")
    for marker in (
        "goal5/structured/goal6_increment\\.csv$",
        "target.dataset_id = source.dataset_id AND target.record_hash = source.record_hash",
        "target.dataset_id = source.dataset_id AND target.event_id = source.event_id",
        "target.dataset_id = source.dataset_id AND target.metric_date = source.metric_date AND target.category = source.category",
    ):
        if marker not in increment_sql:
            errors.append(
                f"Goal 6 controlled increment is missing idempotent source contract: {marker}"
            )
    if increment_sql.count("MERGE INTO IDENTIFIER") != 3:
        errors.append("Goal 6 increment must mutate exactly Raw, Curated, and Business")
    if increment_sql.count("WHEN MATCHED THEN UPDATE SET *") != 3:
        errors.append("Goal 6 increment must remain rerunnable without duplicate inserts")
    if increment_sql.count("WHEN NOT MATCHED THEN INSERT *") != 3:
        errors.append("Goal 6 increment must retain all three deterministic insert paths")
    increment_executable = "\n".join(
        line
        for line in (increment_sql + "\n" + verify_sql).splitlines()
        if not line.lstrip().startswith("--")
    )
    if "doris" in increment_executable.lower():
        errors.append("Goal 6 authoritative increment SQL must never access Doris")
    for table in (
        "goal5_structured_raw_events",
        "goal5_structured_curated_events",
        "goal5_structured_business_metrics",
    ):
        if table not in increment_sql or table not in verify_sql:
            errors.append(f"Goal 6 SQL must demonstrate Raw -> Curated -> Business for {table}")
    if "SUM(metric_total) = CAST(42 AS DOUBLE)" not in verify_sql:
        errors.append(
            "Goal 6 Business acceptance must retain the deterministic synthetic aggregate"
        )
    if "Green SM" in fixture or "customer" in fixture.lower():
        errors.append("Goal 6 fixture must remain neutral synthetic technical data")
    fixture_lines = [line for line in fixture.splitlines() if line]
    if fixture_lines != [
        "event_id,entity_id,event_time,category,metric_value",
        "goal6-event-001,goal6-entity-001,2026-08-13T12:00:00Z,synthetic-serving-increment,42.0",
    ]:
        errors.append("Goal 6 increment fixture must remain one exact neutral record")

    if "mariadb-client" not in dockerfile or "USER 65532:65532" not in dockerfile:
        errors.append(
            "Goal 6 verifier image must use a MySQL-compatible client and non-root runtime user"
        )
    for relative in (
        "docker/doris-verifier/doris-admin-refresh",
        "docker/doris-verifier/doris-readonly-verify",
        "docker/doris-verifier/doris-rbac-verify",
        "docker/doris-verifier/doris-query-limit-verify",
        "docker/doris-verifier/doris-audit-verify",
        "docker/doris-verifier/doris-rebuild-serving",
    ):
        runner = sources[relative]
        for marker in ("--ssl --protocol=TCP", "set -eu"):
            if marker not in runner:
                errors.append(f"Goal 6 runner must fail closed and require TLS: {relative}")
        if "--ssl-mode" in runner:
            errors.append(f"Goal 6 runner must use the MariaDB TLS option, not --ssl-mode: {relative}")
    admin_runner = sources["docker/doris-verifier/doris-admin-refresh"]
    for marker in (
        "iceberg.rest.vended-credentials-enabled",
        "DROP CATALOG IF EXISTS",
        "goal5_structured_business_metrics",
    ):
        if marker not in admin_runner:
            errors.append(f"Goal 6 admin runner is missing controlled refresh guard: {marker}")
    for marker in (
        'workspace_origin="${DATABRICKS_WORKSPACE_HOST%/}"',
        r"^https://[A-Za-z0-9][A-Za-z0-9.-]*\.cloud\.databricks\.com$",
        '"$workspace_origin/oidc/v1/token"',
        "'$workspace_origin/api/2.1/unity-catalog/iceberg-rest/'",
        '"status":"invalid-workspace-origin"',
    ):
        if marker not in admin_runner:
            errors.append(f"Goal 6 admin runner must normalize and validate workspace origin: {marker}")
    if "https://$DATABRICKS_WORKSPACE_HOST" in admin_runner:
        errors.append("Goal 6 admin runner must not prepend HTTPS to an HTTPS workspace origin")
    if "GRANT ADMIN_PRIV ON *.*.* TO '$admin_user'@'%';" not in admin_runner:
        errors.append(
            "Goal 6 admin runner must grant ADMIN_PRIV only at the Doris global *.*.* scope"
        )
    if "GRANT ADMIN_PRIV ON *.* TO '$admin_user'@'%';" in admin_runner:
        errors.append("Goal 6 admin runner must not use invalid two-level ADMIN_PRIV scope")
    for marker in (
        "run_sql_file /app/doris/schemas/01_serving_database.sql",
        "run_sql_file /app/doris/migrations/04_recreate_authorization_probe.sql",
        "run_sql_file /app/doris/schemas/02_readonly_workload_and_audit.sql",
        "run_sql_file /app/doris/materialized_views/01_serving_data_freshness.sql",
        "SHOW VARIABLES LIKE 'enable_audit_plugin'",
        '"status":"audit-plugin-disabled"',
        '"status":"audit-plugin-unreadable"',
        "SET PROPERTY FOR '$query_user' 'query_timeout' = '30'",
        "GRANT USAGE_PRIV ON WORKLOAD GROUP 'goal6_readonly'",
    ):
        if marker not in admin_runner:
            errors.append(f"Goal 6 admin runner is missing operational guardrail: {marker}")
    verifier_runner = sources["docker/doris-verifier/doris-readonly-verify"]
    for marker in (
        "SET workload_group = 'goal6_readonly'",
        "SELECT LAST_QUERY_ID()",
        "source_dataset",
        "query_result",
        "refresh_timestamp",
        "executed_query_id",
        "row_count",
        "execution_duration",
        "session_result",
    ):
        if marker not in verifier_runner:
            errors.append(f"Goal 6 verifier evidence contract is missing {marker}")
    if verifier_runner.count("mysql --ssl --protocol=TCP") != 1:
        errors.append(
            "Goal 6 read-only verifier must collect result and LAST_QUERY_ID in one Doris session"
        )
    rbac_runner = sources["docker/doris-verifier/doris-rbac-verify"]
    serving_schema = sources["doris/schemas/01_serving_database.sql"]
    for marker in (
        "SHOW GRANTS;",
        "goal6_authorization_probe",
        "WHERE FALSE",
        "delete_lower_sentinel_id=126",
        "delete_probe_id=127",
        "delete_upper_sentinel_id=128",
        "SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = $1;",
        "DELETE FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = ${delete_probe_id}",
        "delete-probe-precondition-failed",
        '"status":"delete-probe-guard"',
        "lower-sentinel-missing",
        "upper-sentinel-missing",
        "CREATE TEMPORARY TABLE",
        "INSERT INTO",
        "UPDATE ",
        "DELETE FROM",
        "ALTER TABLE",
        "DROP TABLE",
        "wrong-rejection-layer",
        "unauthorized_database",
        "doris_privilege_token",
        "denial_evidence",
        '"denied_statement_classes"',
    ):
        if marker not in rbac_runner:
            errors.append(f"Goal 6 RBAC verifier is missing safe negative-test control: {marker}")
    if (
        "DELETE FROM ask_david_serving_development.goal6_authorization_probe WHERE FALSE"
        in rbac_runner
    ):
        errors.append(
            "Goal 6 RBAC DELETE probe must not use Doris's constant-false authorization-bypass path"
        )
    if "disable_empty_partition_prune" in rbac_runner:
        errors.append(
            "Goal 6 RBAC DELETE probe must not rely on the ineffective empty-partition session setting"
        )
    if "probe_id SMALLINT NOT NULL" not in serving_schema:
        errors.append("Goal 6 disposable authorization probe must use SMALLINT for sentinel 128")
    for migration_marker in (
        "DROP TABLE IF EXISTS ask_david_serving_development.goal6_authorization_probe;",
        "CREATE TABLE ask_david_serving_development.goal6_authorization_probe",
        "probe_id SMALLINT NOT NULL",
        "(126, 'goal6_guard_lower')",
        "(128, 'goal6_guard_upper')",
    ):
        if migration_marker not in probe_migration:
            errors.append(
                "Goal 6 disposable authorization probe migration is missing "
                f"required marker: {migration_marker}"
            )
    if "green_sm_" in rbac_runner or "DORIS_ADMIN_SECRET" in rbac_runner:
        errors.append(
            "Goal 6 RBAC verifier must use only the query identity and internal disposable objects"
        )
    query_limit_runner = sources["docker/doris-verifier/doris-query-limit-verify"]
    for marker in (
        "SHOW PROPERTY LIKE",
        "query_timeout",
        "SELECT SLEEP(31);",
        "timeout 40 mysql",
        '"enforcement":"timeout"',
    ):
        if marker not in query_limit_runner:
            errors.append(f"Goal 6 query-limit verifier is missing bounded control: {marker}")
    if "SHOW PROPERTY FOR" in query_limit_runner:
        errors.append(
            "Goal 6 query-limit verifier must inspect the current identity, not another user"
        )
    if re.search(r"(?i)(insert|update|delete|drop|alter|create)", query_limit_runner):
        errors.append("Goal 6 query-limit verifier must remain read-only")
    audit_runner = sources["docker/doris-verifier/doris-audit-verify"]
    for marker in (
        "EXPECTED_QUERY_ID",
        "SHOW VARIABLES LIKE 'enable_audit_plugin'",
        "SELECT COUNT(*) FROM internal.__internal_schema.audit_log;",
        '"status":"audit-plugin-disabled"',
        '"status":"audit-plugin-unreadable"',
        '"status":"audit-log-empty"',
        "internal.__internal_schema.audit_log",
        "query_id",
        "query_time",
        "workload_group",
        'state" != "EOF"',
        '"identity_match":true',
        '"target_match":true',
        '"workload_group_match":true',
    ):
        if marker not in audit_runner:
            errors.append(f"Goal 6 audit verifier is missing evidence control: {marker}")
    if re.search(r"(?i)(insert|update|delete|drop|alter|create)", audit_runner):
        errors.append("Goal 6 audit verifier must remain read-only")
    for runner_name in (
        "/app/doris-rbac-verify",
        "/app/doris-query-limit-verify",
        "/app/doris-audit-verify",
    ):
        if runner_name not in dockerfile:
            errors.append(f"Goal 6 verifier image must install runtime runner: {runner_name}")
    if re.search(r"(?i)(insert|update|delete|drop|alter|create)", verifier_runner):
        errors.append("Goal 6 read-only verifier runner must not contain a write or DDL statement")
    rebuild_runner = sources["docker/doris-verifier/doris-rebuild-serving"]
    if "/app/doris/migrations/03_rebuild_internal_serving.sql" not in rebuild_runner:
        errors.append("Goal 6 rebuild runner must use only the versioned internal rebuild SQL")

    for marker in (
        "Set-StrictMode -Version Latest",
        "ConfirmGoal6AdminRefresh",
        'if ($Region -ne \"ap-southeast-1\")',
        "aws sts get-caller-identity",
        "aws ecs describe-task-definition",
        "ExpectedRevision",
        "ExpectedImage",
        "assignPublicIp=DISABLED",
        "aws ecs run-task",
        "aws ecs wait tasks-stopped",
        "aws ecs describe-tasks",
        "aws logs describe-log-streams",
        "aws logs get-log-events",
        '"status":"completed"',
        "No retry is performed",
    ):
        if marker not in admin_task_wrapper:
            errors.append(f"Goal 6 admin task wrapper is missing fail-closed control: {marker}")
    for forbidden in ("terraform", "databricks", "get-secret-value", "s3 cp", "aws s3"):
        if forbidden.lower() in admin_task_wrapper.lower():
            errors.append(f"Goal 6 admin task wrapper must not perform {forbidden} operations")
    if "securityGroups=[$AdminSecurityGroupId]" not in admin_task_wrapper:
        errors.append("Goal 6 admin task wrapper must pass only the approved admin security group")
    if "ApplicationSubnetIds" not in admin_task_wrapper or "privateSubnetId" not in admin_task_wrapper:
        errors.append("Goal 6 admin task wrapper must constrain and report private subnet evidence")

    for marker in (
        "--confirm-goal6-admin-refresh",
        '[[ "$region" == "ap-southeast-1" ]]',
        "expected_fe_host",
        "expected_be_host",
        "expected_workspace_host",
        "aws sts get-caller-identity",
        "aws ecs describe-task-definition",
        "expected_revision",
        "expected_image",
        'command == ["/app/doris-admin-refresh"]',
        "DATABRICKS_OAUTH_SECRET",
        "DORIS_ADMIN_SECRET",
        "DORIS_QUERY_SECRET",
        "assignPublicIp=DISABLED",
        "securityGroups=[$admin_security_group_id]",
        "aws ecs run-task",
        "aws ecs wait tasks-stopped",
        "aws logs get-log-events",
        'operation:\"admin-refresh\"',
        'cloudWatchCompletionStatus:"completed"',
        "no retry is performed",
    ):
        if marker not in admin_task_shell_wrapper:
            errors.append(
                f"Goal 6 admin task shell wrapper is missing fail-closed control: {marker}"
            )
    for forbidden in (
        "terraform",
        "get-secret-value",
        "s3 cp",
        "aws s3",
        "--overrides",
    ):
        if forbidden.lower() in admin_task_shell_wrapper.lower():
            errors.append(
                f"Goal 6 admin task shell wrapper must not perform {forbidden} operations"
            )
    if re.search(r"(?m)^\s*databricks\s", admin_task_shell_wrapper, re.IGNORECASE):
        errors.append("Goal 6 admin task shell wrapper must not invoke Databricks CLI")
    if "application_subnet_ids" not in admin_task_shell_wrapper or "subnet_id" not in admin_task_shell_wrapper:
        errors.append(
            "Goal 6 admin task shell wrapper must constrain and report private subnet evidence"
        )

    for marker in (
        "--confirm-goal6-verifier",
        '[[ "$region" == "ap-southeast-1" ]]',
        'readonly)',
        'rbac)',
        'query-limit)',
        "/app/doris-readonly-verify",
        "/app/doris-rbac-verify",
        "/app/doris-query-limit-verify",
        "aws sts get-caller-identity",
        "aws ecs describe-task-definition",
        "expected_revision",
        "expected_image",
        'command == ["/app/doris-readonly-verify"]',
        "DORIS_QUERY_SECRET",
        "assignPublicIp=DISABLED",
        "securityGroups=[$verifier_security_group_id]",
        "aws ecs run-task",
        "--overrides",
        "aws ecs wait tasks-stopped",
        "aws logs get-log-events",
        'operationEvidence:$operation_evidence',
        "no retry is performed",
    ):
        if marker not in verifier_task_shell_wrapper:
            errors.append(
                "Goal 6 verifier shell wrapper is missing fail-closed control: "
                f"{marker}"
            )
    for forbidden in (
        "terraform",
        "get-secret-value",
        "s3 cp",
        "aws s3",
        "DORIS_ADMIN_SECRET",
        "DATABRICKS_OAUTH_SECRET",
    ):
        if forbidden.lower() in verifier_task_shell_wrapper.lower():
            errors.append(
                f"Goal 6 verifier shell wrapper must not perform or receive {forbidden}"
            )
    if re.search(r"(?m)^\s*databricks\s", verifier_task_shell_wrapper, re.IGNORECASE):
        errors.append("Goal 6 verifier shell wrapper must not invoke Databricks CLI")
    if (
        "application_subnet_ids" not in verifier_task_shell_wrapper
        or "private_ipv4_address" not in verifier_task_shell_wrapper
    ):
        errors.append(
            "Goal 6 verifier shell wrapper must constrain and report private ENI evidence"
        )

    for marker in (
        "--confirm-goal6-rebuild",
        "--confirm-goal6-audit",
        '[[ "$region" == "ap-southeast-1" ]]',
        'rebuild)',
        'audit)',
        "/app/doris-rebuild-serving",
        "/app/doris-audit-verify",
        "EXPECTED_QUERY_ID",
        "aws sts get-caller-identity",
        "aws ecs describe-task-definition",
        "expected_revision",
        "expected_image",
        'command == ["/app/doris-admin-refresh"]',
        "DATABRICKS_OAUTH_SECRET",
        "DORIS_ADMIN_SECRET",
        "DORIS_QUERY_SECRET",
        "assignPublicIp=DISABLED",
        "securityGroups=[$admin_security_group_id]",
        "aws ecs run-task",
        "--overrides",
        "aws ecs wait tasks-stopped",
        "aws logs get-log-events",
        'operationEvidence:$operation_evidence',
        "no retry is performed",
    ):
        if marker not in admin_operation_shell_wrapper:
            errors.append(
                "Goal 6 admin-operation shell wrapper is missing fail-closed "
                f"control: {marker}"
            )
    for forbidden in (
        "terraform",
        "get-secret-value",
        "s3 cp",
        "aws s3",
    ):
        if forbidden.lower() in admin_operation_shell_wrapper.lower():
            errors.append(
                f"Goal 6 admin-operation shell wrapper must not perform {forbidden}"
            )
    if re.search(r"(?m)^\s*databricks\s", admin_operation_shell_wrapper, re.IGNORECASE):
        errors.append("Goal 6 admin-operation shell wrapper must not invoke Databricks CLI")
    if (
        "application_subnet_ids" not in admin_operation_shell_wrapper
        or "private_ipv4_address" not in admin_operation_shell_wrapper
    ):
        errors.append(
            "Goal 6 admin-operation shell wrapper must constrain and report private ENI evidence"
        )

    for marker in (
        "ConfirmGoal6FeHealth",
        'if ($Region -ne \"ap-southeast-1\")',
        "ExpectedFeHost",
        "aws sts get-caller-identity",
        "aws ecs describe-task-definition",
        "ExpectedRevision",
        "ExpectedImage",
        "assignPublicIp=DISABLED",
        'command = @(\"-c\", $healthCommand)',
        "$null -ne $container.entryPoint",
        "mysqladmin --ssl --protocol=TCP",
        "aws ecs run-task",
        "aws ecs wait tasks-stopped",
        "aws ecs describe-tasks",
        "aws logs describe-log-streams",
        "aws logs get-log-events",
        "mysqld is alive",
        "Access denied for user",
        "cloudWatchHealthStatus = \"listener-reachable\"",
        "No retry is performed",
    ):
        if marker not in health_task_wrapper:
            errors.append(f"Goal 6 FE health wrapper is missing fail-closed control: {marker}")
    for forbidden in ("terraform", "databricks", "get-secret-value", "s3 cp", "aws s3", "mysql -e"):
        if forbidden.lower() in health_task_wrapper.lower():
            errors.append(f"Goal 6 FE health wrapper must not perform {forbidden} operations")
    if 'command = @(\"/bin/sh\", \"-c\", $healthCommand)' in health_task_wrapper:
        errors.append("Goal 6 FE health wrapper must not duplicate the /bin/sh entrypoint")
    if "securityGroups=[$VerifierSecurityGroupId]" not in health_task_wrapper:
        errors.append("Goal 6 FE health wrapper must pass only the approved verifier security group")
    if "ApplicationSubnetIds" not in health_task_wrapper or "privateSubnetId" not in health_task_wrapper:
        errors.append("Goal 6 FE health wrapper must constrain and report private subnet evidence")

    for marker in (
        "ConfirmGoal6ReadinessMarkers",
        'if ($Region -ne "ap-southeast-1")',
        "ExpectedFeHost",
        "ExpectedBeHost",
        "aws sts get-caller-identity",
        "aws ecs describe-task-definition",
        "ExpectedRevision",
        "ExpectedImage",
        "assignPublicIp=DISABLED",
        'command = @("-c", $markerCommand)',
        "$null -ne $container.entryPoint",
        "SHOW BACKENDS;",
        '"listener_state":"ready"',
        '"marker":"doris-port-ready"',
        '"marker":"be-storage-capacity-ready"',
        "aws ecs run-task",
        "aws ecs wait tasks-stopped",
        "aws logs get-log-events",
        "No retry is performed",
    ):
        if marker not in readiness_marker_wrapper:
            errors.append(
                f"Goal 6 readiness-marker wrapper is missing fail-closed control: {marker}"
            )
    for forbidden in (
        "terraform",
        "databricks",
        "get-secret-value",
        "s3 cp",
        "aws s3",
        "ALTER SYSTEM",
        "CREATE ",
        "DROP ",
        "INSERT ",
        "UPDATE ",
        "DELETE ",
        "GRANT ",
        "REVOKE ",
    ):
        if forbidden.lower() in readiness_marker_wrapper.lower():
            errors.append(
                f"Goal 6 readiness-marker wrapper must not perform {forbidden} operations"
            )
    if 'command = @("/bin/sh", "-c", $markerCommand)' in readiness_marker_wrapper:
        errors.append("Goal 6 readiness-marker wrapper must not duplicate the /bin/sh entrypoint")
    if "securityGroups=[$AdminSecurityGroupId]" not in readiness_marker_wrapper:
        errors.append("Goal 6 readiness-marker wrapper must pass only the approved admin security group")
    if (
        "ApplicationSubnetIds" not in readiness_marker_wrapper
        or "privateSubnetId" not in readiness_marker_wrapper
    ):
        errors.append(
            "Goal 6 readiness-marker wrapper must constrain and report private subnet evidence"
        )

    for marker in (
        "--confirm-goal6-readiness-markers",
        '[[ "$region" == "ap-southeast-1" ]]',
        "expected_fe_host",
        "expected_be_host",
        "aws sts get-caller-identity",
        "aws ecs describe-task-definition",
        "expected_revision",
        "expected_image",
        "assignPublicIp=DISABLED",
        'command:["-c",$command]',
        "SHOW BACKENDS;",
        '"listener_state":"ready"',
        '"marker":"doris-port-ready"',
        '"marker":"be-storage-capacity-ready"',
        "aws ecs run-task",
        "aws ecs wait tasks-stopped",
        "aws logs get-log-events",
        "no retry is performed",
    ):
        if marker not in readiness_marker_shell_wrapper:
            errors.append(
                f"Goal 6 readiness-marker shell wrapper is missing fail-closed control: {marker}"
            )
    for forbidden in (
        "terraform",
        "databricks",
        "get-secret-value",
        "s3 cp",
        "aws s3",
        "ALTER SYSTEM",
        "CREATE ",
        "DROP ",
        "INSERT ",
        "UPDATE ",
        "DELETE ",
        "GRANT ",
        "REVOKE ",
    ):
        if forbidden.lower() in readiness_marker_shell_wrapper.lower():
            errors.append(
                f"Goal 6 readiness-marker shell wrapper must not perform {forbidden} operations"
            )
    if 'command:["/bin/sh","-c",$command]' in readiness_marker_shell_wrapper:
        errors.append(
            "Goal 6 readiness-marker shell wrapper must not duplicate the /bin/sh entrypoint"
        )
    if "securityGroups=[$admin_security_group_id]" not in readiness_marker_shell_wrapper:
        errors.append(
            "Goal 6 readiness-marker shell wrapper must pass only the approved admin security group"
        )
    if "application_subnet_ids" not in readiness_marker_shell_wrapper or "subnet_id" not in readiness_marker_shell_wrapper:
        errors.append(
            "Goal 6 readiness-marker shell wrapper must constrain and report private subnet evidence"
        )

    forbidden_scope = re.compile(
        r"(?i)(opensearch|langgraph|supervisor|agent runtime|goal[-_ ]?7|goal[-_ ]?8)"
    )
    for relative, source in sources.items():
        if forbidden_scope.search(source):
            errors.append(f"Goal 6 source contains deferred scope: {relative}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, default=REPOSITORY_ROOT)
    arguments = parser.parse_args()
    errors = validate_goal6_repository(arguments.repository_root.resolve())
    if errors:
        print("Goal 6 static validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Goal 6 static validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
