"""Static Goal 6 repository-scope tests."""

# Embedded shell fixtures intentionally preserve exact long command strings.
# ruff: noqa: E501

import json
import os
import re
import subprocess
from pathlib import Path

from scripts.validate_goal6 import validate_goal6_repository

ROOT = Path(__file__).resolve().parents[2]


def test_goal6_repository_contract_passes() -> None:
    assert validate_goal6_repository(ROOT) == []


def test_goal6_is_disabled_by_default() -> None:
    variables = (ROOT / "infrastructure/environments/development/goal6_variables.tf").read_text(
        encoding="utf-8"
    )
    assert 'variable "goal_6_enabled"' in variables
    assert "default     = false" in variables
    assert 'variable "goal_6_verifier_tasks_enabled"' in variables


def test_goal6_uses_separate_cost_conscious_private_nodes() -> None:
    source = (ROOT / "infrastructure/modules/doris-serving/main.tf").read_text(encoding="utf-8")
    host_template = (
        ROOT / "infrastructure/modules/doris-serving/templates/doris-host.sh.tftpl"
    ).read_text(encoding="utf-8")
    variables = (ROOT / "infrastructure/environments/development/goal6_variables.tf").read_text(
        encoding="utf-8"
    )

    assert source.count('resource "aws_instance"') == 2
    assert source.count("associate_public_ip_address = false") == 2
    assert variables.count('default     = "m7i.xlarge"') == 2
    assert 'variable "goal_6_fe_private_ip"' in variables
    assert 'default     = "10.42.64.238"' in variables
    assert 'variable "goal_6_be_private_ip"' in variables
    assert 'default     = "10.42.71.97"' in variables
    assert "private_ip                  = var.fe_private_ip" in source
    assert "private_ip                  = var.be_private_ip" in source
    assert "expected_private_ip = var.fe_private_ip" in source
    assert "expected_private_ip = var.be_private_ip" in source
    assert "precondition {" in source
    assert "selected_subnet_ipv4_hosts" in source
    assert 'can(regex("/20$", data.aws_subnet.selected[0].cidr_block))' in source
    assert "range(0, 16)" in source
    assert "range(0, 256)" in source
    assert "cidrhost(" in source
    assert "data.aws_subnet.selected[0].cidr_block" in source
    assert "contains(local.selected_subnet_ipv4_hosts, var.fe_private_ip)" in source
    assert "contains(local.selected_subnet_ipv4_hosts, var.be_private_ip)" in source
    assert "cidrcontains(" not in source
    assert "private-ip-configured" in host_template
    assert "private-ip-mismatch" in host_template
    assert "enable_ssl = true" in host_template
    assert "priority_networks" in host_template
    assert "fe_custom.conf" in host_template
    assert "be_custom.conf" in host_template
    assert "timeout --foreground --kill-after=10s 120s docker run" in host_template
    assert "container-launch-failed" in host_template


def test_goal6_bootstrap_recovery_uses_adequate_root_storage_and_replaces_hosts() -> None:
    source = (ROOT / "infrastructure/modules/doris-serving/main.tf").read_text(encoding="utf-8")
    variables = (ROOT / "infrastructure/environments/development/goal6_variables.tf").read_text(
        encoding="utf-8"
    )
    wiring = (ROOT / "infrastructure/environments/development/goal6.tf").read_text(encoding="utf-8")

    assert "volume_size = var.fe_root_volume_gib" in source
    assert "volume_size = var.be_root_volume_gib" in source
    assert source.count("user_data_replace_on_change = true") == 2
    assert "Goal 6 BE bootstrap generation: ${var.be_bootstrap_generation}" in source
    assert "Goal 6 FE bootstrap generation: ${var.fe_bootstrap_generation}" in source
    assert 'variable "goal_6_fe_root_volume_gib"' in variables
    assert 'variable "goal_6_be_root_volume_gib"' in variables
    assert 'variable "goal_6_be_bootstrap_generation"' in variables
    assert 'variable "goal_6_fe_bootstrap_generation"' in variables
    assert variables.count("default     = 30") == 2
    assert "default     = 2" in variables
    assert "fe_root_volume_gib        = var.goal_6_fe_root_volume_gib" in wiring
    assert "be_root_volume_gib        = var.goal_6_be_root_volume_gib" in wiring
    assert "be_bootstrap_generation   = var.goal_6_be_bootstrap_generation" in wiring
    assert "fe_bootstrap_generation   = var.goal_6_fe_bootstrap_generation" in wiring


def test_goal6_rendered_ec2_user_data_has_a_fail_closed_aws_size_guard() -> None:
    source = (ROOT / "infrastructure/modules/doris-serving/main.tf").read_text(encoding="utf-8")

    assert 'check "ec2_user_data_is_within_aws_limit"' in source
    assert "length(local.fe_user_data_size_check) <= 16384" in source
    assert "length(local.be_user_data_size_check) <= 16384" in source
    assert 'volume_id           = "vol-0123456789abcdef0"' in source
    assert "user_data                   = local.fe_user_data" in source
    assert "user_data                   = local.be_user_data" in source


def test_goal6_disabled_module_skips_counted_bootstrap_dependencies() -> None:
    source = (ROOT / "infrastructure/modules/doris-serving/main.tf").read_text(encoding="utf-8")

    assert 'fe_user_data = var.enabled ? join("\\n", [' in source
    assert 'be_user_data = var.enabled ? join("\\n", [' in source
    assert 'fe_user_data_size_check = var.enabled ? join("\\n", [' in source
    assert 'be_user_data_size_check = var.enabled ? join("\\n", [' in source
    assert source.count(']) : ""') >= 4


def test_goal6_serving_state_rebuild_is_explicit_and_preserves_old_volumes() -> None:
    variables = (ROOT / "infrastructure/environments/development/goal6_variables.tf").read_text(
        encoding="utf-8"
    )
    source = (ROOT / "infrastructure/modules/doris-serving/main.tf").read_text(encoding="utf-8")
    wiring = (ROOT / "infrastructure/environments/development/goal6.tf").read_text(encoding="utf-8")

    assert 'variable "goal_6_rebuild_serving_state"' in variables
    assert "default     = false" in variables
    assert "rebuild_serving_state     = var.goal_6_rebuild_serving_state" in wiring
    assert 'resource "aws_ebs_volume" "fe_data_rebuild"' in source
    assert 'resource "aws_ebs_volume" "be_data_rebuild"' in source
    assert source.count("prevent_destroy = true") >= 4
    assert "var.enabled && var.rebuild_serving_state" in source
    assert "frontend-metadata-rebuild" in source
    assert "backend-serving-data-rebuild" in source
    assert 'StateRecovery = "explicit-goal6-rebuild"' in source
    assert "var.rebuild_serving_state ? aws_ebs_volume.fe_data_rebuild[0].id" in source
    assert "var.rebuild_serving_state ? aws_ebs_volume.be_data_rebuild[0].id" in source


def test_goal6_doris_docker_bootstrap_supplies_discovery_and_listener_guards() -> None:
    source = (ROOT / "infrastructure/modules/doris-serving/main.tf").read_text(encoding="utf-8")
    template = (
        ROOT / "infrastructure/modules/doris-serving/templates/doris-host.sh.tftpl"
    ).read_text(encoding="utf-8")

    assert "fe_private_ip       = var.fe_private_ip" in source
    assert "FE_SERVERS" in template
    assert "FE_ID=1" in template
    assert "BE_ADDR" in template
    assert '"$${DOCKER_ENV[@]}"' in template
    assert "/dev/tcp/127.0.0.1/$DORIS_PORT" in template
    assert 'BOOTSTRAP_STATUS_FILE="$MOUNT_PATH/$ROLE-log/bootstrap-status.log"' in template
    assert "emit_status" in template
    assert 'ROOT_BOOTSTRAP_LOG="/var/log/goal6-doris-bootstrap.log"' in template
    assert "emit_early_status" in template
    assert 'emit_early_status "bootstrap-invoked" "none"' in template
    assert 'emit_early_status "bootstrap-failed" "none" "$exit_code"' in template
    assert "goal6_on_exit" in template
    assert "trap 'goal6_on_exit \"$?\"' EXIT" in template
    assert 'cat "$ROOT_BOOTSTRAP_LOG" >> "$BOOTSTRAP_STATUS_FILE"' in template
    assert 'log_stream_name": "{instance_id}/$ROLE/bootstrap-root"' in template
    assert 'emit_status "bootstrap-started" "none"' in template
    assert 'emit_status "container-exited" "$DORIS_PORT"' in template
    assert 'emit_status "container-launch-failed" "$DORIS_PORT"' in template
    assert "emit_container_diagnostic_summary" in template
    assert 'status\\":\\"container-diagnostics-summary' in template
    assert 'local listener_state="$${1:-unknown}"' in template
    assert 'local error_present="false"' in template
    assert 'local redacted_log_lines="0"' in template
    assert 'local log_signal="none"' in template
    assert 'log_signal\\":\\"$log_signal' in template
    assert 'log_signal="bind"' in template
    assert 'log_signal="metadata"' in template
    assert 'log_signal="configuration"' in template
    assert 'log_signal="exception"' in template
    assert 'emit_container_diagnostic_summary "starting"' in template
    assert 'emit_container_diagnostic_summary "unavailable"' in template
    assert 'emit_container_diagnostic_summary "ready"' in template
    assert 'emit_status "doris-port-ready" "$DORIS_PORT"' in template
    assert 'emit_status "doris-port-unavailable" "$DORIS_PORT"' in template
    assert "storage_root_path = /opt/apache-doris/be/storage,medium:hdd" in template
    assert 'install -d -m 0750 "$MOUNT_PATH/be-storage"' in template
    assert 'emit_status "be-storage-root-writable" "$DORIS_PORT"' in template
    assert 'emit_status "be-storage-root-unavailable" "$DORIS_PORT"' in template
    assert 'emit_status "be-storage-capacity-ready" "$DORIS_PORT"' in template
    assert 'emit_status "be-storage-capacity-unavailable" "$DORIS_PORT"' in template
    assert "SHOW BACKENDS;" in template
    assert "BE_BACKEND_CAPACITY_READY" in template
    assert 'docker exec "$CONTAINER_ID" sh -ec' in template
    assert 'emit_status "fe-registration-port-waiting" "$FE_REGISTRATION_PORT"' in template
    assert 'emit_status "fe-registration-port-ready" "$FE_REGISTRATION_PORT"' in template
    assert 'emit_status "fe-registration-port-unavailable" "$FE_REGISTRATION_PORT"' in template
    assert 'FE_REGISTRATION_READY="false"' in template
    assert "for _ in $(seq 1 120)" in template
    assert "timeout 2 bash -c" in template
    assert 'emit_status "host-prerequisites-ready" "none"' in template
    assert 'emit_status "host-prerequisites-failed" "none"' in template
    assert "DORIS_VM_MAX_MAP_COUNT=2000000" in template
    assert "vm.max_map_count = $DORIS_VM_MAX_MAP_COUNT" in template
    assert "LimitNOFILE=$DORIS_NOFILE_LIMIT" in template
    assert '--ulimit "nofile=$DORIS_NOFILE_LIMIT:$DORIS_NOFILE_LIMIT"' in template
    assert "container-diagnostics.log" in template
    assert "docker-run.log" in template
    assert '"force_flush_interval": 5' in template
    assert 'bootstrap-status.log",' in template
    assert 'private-ip-diagnostics.log",' in template
    assert 'container-diagnostics.log",' in template
    assert 'docker-run.log",' in template
    assert "fe_custom.conf:/opt/apache-doris/fe/conf/fe_custom.conf:ro" in template
    assert "be_custom.conf:/opt/apache-doris/be/conf/be_custom.conf:ro" in template
    assert "docker inspect --format" in template
    assert "docker logs --tail 200" in template
    assert "EXPECTED_PRIVATE_IP" in template
    assert (
        'PRIVATE_IP_DIAGNOSTICS_FILE="$MOUNT_PATH/$ROLE-log/private-ip-diagnostics.log"' in template
    )


def test_goal6_be_storage_readiness_requires_real_usable_capacity() -> None:
    template = (
        ROOT / "infrastructure/modules/doris-serving/templates/doris-host.sh.tftpl"
    ).read_text(encoding="utf-8")

    assert "storage_root_path = /opt/apache-doris/be/storage,medium:hdd" in template
    assert 'install -d -m 0750 "$MOUNT_PATH/be-storage"' in template
    assert 'docker exec "$CONTAINER_ID" sh -ec' in template
    assert "SHOW BACKENDS;" in template
    assert "total_capacity = $17" in template
    assert 'tolower($10) == "true"' in template
    assert 'tolower($11) == "false"' in template
    assert 'emit_status "be-storage-capacity-unavailable" "$DORIS_PORT" >&2' in template
    assert 'emit_status "be-storage-capacity-ready" "$DORIS_PORT"' in template


def test_goal6_trivy_exception_is_scoped_to_https_egress_only() -> None:
    source = (ROOT / "infrastructure/modules/doris-serving/main.tf").read_text(encoding="utf-8")

    assert source.count("#trivy:ignore:AVD-AWS-0104") == 2
    assert (
        '#trivy:ignore:AVD-AWS-0104\nresource "aws_vpc_security_group_egress_rule" "fe_https"'
        in source
    )
    assert (
        '#trivy:ignore:AVD-AWS-0104\nresource "aws_vpc_security_group_egress_rule" "be_https"'
        in source
    )
    assert source.count('cidr_ipv4         = "0.0.0.0/0"') == 2
    assert source.count("from_port         = 443") == 2
    assert "There is no public ingress on this resource." in source


def test_goal6_private_cluster_rules_cover_initiated_traffic_both_directions() -> None:
    source = (ROOT / "infrastructure/modules/doris-serving/main.tf").read_text(encoding="utf-8")

    assert 'resource "aws_vpc_security_group_ingress_rule" "be_to_fe_registration"' in source
    assert 'resource "aws_vpc_security_group_egress_rule" "be_to_fe_registration"' in source
    assert 'resource "aws_vpc_security_group_ingress_rule" "be_to_fe_rpc"' in source
    assert 'resource "aws_vpc_security_group_egress_rule" "be_to_fe_rpc"' in source
    assert 'resource "aws_vpc_security_group_egress_rule" "fe_to_be"' in source
    assert source.count('toset(["8040", "9050", "9060", "8060"])') == 2
    assert (
        source.count(
            'description                  = "Documented Doris FE-to-BE membership traffic."'
        )
        == 2
    )
    assert (
        source.count(
            'description                  = "Private Doris BE callbacks to the FE RPC listener."'
        )
        == 2
    )
    assert source.count("from_port                    = 9030") >= 2
    assert source.count("from_port                    = 9020") == 2
    assert source.count("to_port                      = 9020") == 2
    assert "AuditLoader sends an HTTP stream-load batch" in source
    assert source.count("referenced_security_group_id = aws_security_group.fe[0].id") >= 2
    assert source.count("referenced_security_group_id = aws_security_group.be[0].id") >= 4


def test_goal6_verifier_tasks_are_gated_until_the_private_ecr_digest_exists() -> None:
    variables = (ROOT / "infrastructure/environments/development/goal6_variables.tf").read_text(
        encoding="utf-8"
    )
    verifier = (ROOT / "infrastructure/modules/doris-verifier/main.tf").read_text(encoding="utf-8")

    assert 'variable "goal_6_verifier_tasks_enabled"' in variables
    assert verifier.count("var.enabled && var.task_definitions_enabled") == 2


def test_goal6_partial_apply_reconciliation_imports_are_exact_and_gated() -> None:
    imports = (
        ROOT / "infrastructure/environments/development/goal6_reconciliation_imports.tf"
    ).read_text(encoding="utf-8")

    assert imports.count("for_each = var.goal_6_enabled") == 3
    assert "module.doris_serving.aws_instance.fe[0]" in imports
    assert 'id = "i-074e456efa350b444"' in imports
    assert "module.doris_serving.aws_volume_attachment.fe[0]" in imports
    assert 'id = "/dev/sdf:vol-012bc3410278ed85e:i-074e456efa350b444"' in imports
    assert "module.doris_serving.aws_volume_attachment.be[0]" in imports
    assert 'id = "/dev/sdf:vol-01e9b0ed05f7b92b9:i-05b409f7992294844"' in imports


def test_goal6_doris_read_principal_is_scoped_to_one_business_table() -> None:
    lakehouse = (ROOT / "infrastructure/modules/databricks-lakehouse/main.tf").read_text(
        encoding="utf-8"
    )
    variables = (ROOT / "infrastructure/modules/databricks-lakehouse/variables.tf").read_text(
        encoding="utf-8"
    )

    assert "doris_source_table" in lakehouse
    assert 'privileges = ["SELECT"]' in lakehouse
    assert "EXTERNAL_USE_LOCATION" not in lakehouse
    assert "count = var.enabled && var.doris_external_read_enabled ? 1 : 0" in lakehouse
    assert "doris_external_read_service_principal_application_id != null" not in lakehouse
    assert 'variable "doris_external_read_enabled"' in variables


def test_goal6_migrations_are_ordered_and_do_not_use_client_source_commands() -> None:
    manifest = (ROOT / "doris/migrations/01_bootstrap_internal_serving.sql").read_text(
        encoding="utf-8"
    )

    assert "SOURCE " not in manifest
    assert (
        manifest.index("01_serving_database.sql")
        < manifest.index("04_recreate_authorization_probe.sql")
        < manifest.index("02_readonly_workload_and_audit.sql")
        < manifest.index("01_serving_data_freshness.sql")
    )


def test_goal6_query_role_has_a_bounded_read_only_workload() -> None:
    security = (ROOT / "doris/schemas/02_readonly_workload_and_audit.sql").read_text(
        encoding="utf-8"
    )
    runner = (ROOT / "docker/doris-verifier/doris-admin-refresh").read_text(encoding="utf-8")

    assert '"max_concurrency" = "2"' in security
    assert '"queue_timeout" = "5000"' in security
    assert "SET GLOBAL enable_audit_plugin = true" in security
    assert "GRANT SELECT_PRIV ON ask_david_serving_development.*" in runner
    assert "GRANT USAGE_PRIV ON WORKLOAD GROUP 'goal6_readonly'" in runner
    assert "'query_timeout' = '30'" in runner


def test_goal6_admin_runner_normalizes_one_https_workspace_origin() -> None:
    runner = (ROOT / "docker/doris-verifier/doris-admin-refresh").read_text(encoding="utf-8")

    assert 'workspace_origin="${DATABRICKS_WORKSPACE_HOST%/}"' in runner
    assert "^https://[A-Za-z0-9][A-Za-z0-9.-]*\\.cloud\\.databricks\\.com$" in runner
    assert '"$workspace_origin/oidc/v1/token"' in runner
    assert "'$workspace_origin/api/2.1/unity-catalog/iceberg-rest/'" in runner
    assert '"status":"invalid-workspace-origin"' in runner
    assert "https://$DATABRICKS_WORKSPACE_HOST" not in runner


def test_goal6_admin_runner_grants_admin_priv_at_global_scope() -> None:
    runner = (ROOT / "docker/doris-verifier/doris-admin-refresh").read_text(encoding="utf-8")

    assert "GRANT ADMIN_PRIV ON *.*.* TO '$admin_user'@'%';" in runner
    assert "GRANT ADMIN_PRIV ON *.* TO '$admin_user'@'%';" not in runner


def test_goal6_refresh_rebuild_and_verifier_are_separated() -> None:
    refresh = (ROOT / "doris/migrations/02_refresh_from_unity_catalog.sql.tmpl").read_text(
        encoding="utf-8"
    )
    rebuild = (ROOT / "doris/migrations/03_rebuild_internal_serving.sql").read_text(
        encoding="utf-8"
    )
    verifier = (ROOT / "docker/doris-verifier/doris-readonly-verify").read_text(encoding="utf-8")

    assert "goal5_structured_business_metrics" in refresh
    assert "green_sm_raw" not in refresh
    assert "serving_refresh_state" in refresh
    assert "ask_david_serving_development" in rebuild
    assert "green_sm_" not in rebuild
    assert "SELECT LAST_QUERY_ID()" in verifier
    assert "source_dataset" in verifier
    assert "query_result" in verifier
    assert "executed_query_id" in verifier
    assert "execution_duration" in verifier
    assert verifier.count("mysql --ssl --protocol=TCP") == 1
    assert "INSERT" not in verifier.upper()


def test_goal6_controlled_increment_is_idempotent_governed_and_doris_independent() -> None:
    bundle = (ROOT / "databricks/bundles/goal_06_doris/resources.yml").read_text(encoding="utf-8")
    increment = (ROOT / "databricks/sql/goal_06/01_apply_controlled_increment.sql").read_text(
        encoding="utf-8"
    )
    verify = (ROOT / "databricks/sql/goal_06/02_verify_controlled_increment.sql").read_text(
        encoding="utf-8"
    )
    fixture = (ROOT / "synthetic_data/goal_06/structured/goal6_increment.csv").read_text(
        encoding="utf-8"
    )

    assert "max_concurrent_runs: 1" in bundle
    assert "queue:\n        enabled: false" in bundle
    assert "task_key: apply_controlled_increment" in bundle
    assert "task_key: verify_controlled_increment" in bundle
    assert "depends_on:" in bundle
    assert "warehouse_id: ${var.warehouse_id}" in bundle
    assert "new_cluster" not in bundle

    assert "goal5/structured/goal6_increment\\.csv$" in increment
    assert increment.count("MERGE INTO IDENTIFIER") == 3
    assert increment.count("WHEN MATCHED THEN UPDATE SET *") == 3
    assert increment.count("WHEN NOT MATCHED THEN INSERT *") == 3
    assert (
        "target.dataset_id = source.dataset_id AND target.record_hash = source.record_hash"
        in increment
    )
    assert (
        "target.dataset_id = source.dataset_id AND target.event_id = source.event_id" in increment
    )
    assert (
        "target.dataset_id = source.dataset_id AND target.metric_date = source.metric_date "
        "AND target.category = source.category" in increment
    )
    executable_sql = "\n".join(
        line
        for line in (increment + "\n" + verify).splitlines()
        if not line.lstrip().startswith("--")
    )
    assert "doris" not in executable_sql.lower()
    assert "COUNT(*) = 1" in verify
    assert "SUM(metric_total) = CAST(42 AS DOUBLE)" in verify
    assert fixture.splitlines() == [
        "event_id,entity_id,event_time,category,metric_value",
        "goal6-event-001,goal6-entity-001,2026-08-13T12:00:00Z,synthetic-serving-increment,42.0",
    ]


def test_goal6_readonly_verifier_emits_complete_result_contract(tmp_path: Path) -> None:
    fake_mysql = tmp_path / "mysql"
    fake_mysql.write_text(
        "#!/bin/sh\n"
        "printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' "
        "'2026-02-01' 'alpha' '1' '10.5' "
        "'ask_david_development.green_sm_business.goal5_structured_business_metrics' "
        "'2026-08-13T04:24:56Z' '2026-08-18T09:30:00Z'\n"
        "printf '%s\\n' '12345678-1234-1234-1234-123456789abc'\n"
        "printf '%s\\t%s\\n' '2' '2026-08-18T09:30:00Z'\n",
        encoding="utf-8",
    )
    fake_mysql.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{tmp_path}:{environment['PATH']}",
            "DORIS_FE_HOST": "10.42.64.238",
            "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
        }
    )

    completed = subprocess.run(
        ["sh", str(ROOT / "docker/doris-verifier/doris-readonly-verify")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 0, completed.stderr
    evidence = json.loads(completed.stdout)
    assert evidence["status"] == "completed"
    assert evidence["source_dataset"] == (
        "ask_david_development.green_sm_business.goal5_structured_business_metrics"
    )
    assert evidence["executed_query_id"] == "12345678-1234-1234-1234-123456789abc"
    assert evidence["row_count"] == 2
    assert evidence["query_result"] == {
        "metric_date": "2026-02-01",
        "category": "alpha",
        "event_count": 1,
        "metric_total": 10.5,
        "source_table": (
            "ask_david_development.green_sm_business.goal5_structured_business_metrics"
        ),
        "source_transformed_at": "2026-08-13T04:24:56Z",
        "refreshed_at": "2026-08-18T09:30:00Z",
    }
    assert isinstance(evidence["execution_duration"], int)


def test_goal6_runners_use_mariadb_tls_option_and_reject_mysql_ssl_mode() -> None:
    for relative in (
        "docker/doris-verifier/doris-admin-refresh",
        "docker/doris-verifier/doris-readonly-verify",
        "docker/doris-verifier/doris-rebuild-serving",
    ):
        runner = (ROOT / relative).read_text(encoding="utf-8")
        assert "--ssl --protocol=TCP" in runner
        assert "--ssl-mode" not in runner


def test_goal6_rebuild_runner_is_versioned_and_internal_only() -> None:
    runner = (ROOT / "docker/doris-verifier/doris-rebuild-serving").read_text(encoding="utf-8")

    assert "/app/doris/migrations/03_rebuild_internal_serving.sql" in runner
    assert "DATABRICKS" not in runner
    assert "aws " not in runner.lower()


def test_goal6_rbac_runner_uses_safe_disposable_negative_probes() -> None:
    schema = (ROOT / "doris/schemas/01_serving_database.sql").read_text(encoding="utf-8")
    probe_migration = (ROOT / "doris/migrations/04_recreate_authorization_probe.sql").read_text(
        encoding="utf-8"
    )
    rebuild = (ROOT / "doris/migrations/03_rebuild_internal_serving.sql").read_text(
        encoding="utf-8"
    )
    runner = (ROOT / "docker/doris-verifier/doris-rbac-verify").read_text(encoding="utf-8")

    assert "goal6_authorization_probe" in schema
    assert "goal6_authorization_probe" in rebuild
    assert "probe_id SMALLINT NOT NULL" in schema
    assert (
        "DROP TABLE IF EXISTS ask_david_serving_development.goal6_authorization_probe;"
        in probe_migration
    )
    assert "probe_id SMALLINT NOT NULL" in probe_migration
    assert "(126, 'goal6_guard_lower')" in probe_migration
    assert "(128, 'goal6_guard_upper')" in probe_migration
    assert "SHOW GRANTS;" in runner
    assert "WHERE FALSE" in runner
    assert "delete_lower_sentinel_id=126" in runner
    assert "delete_probe_id=127" in runner
    assert "delete_upper_sentinel_id=128" in runner
    assert (
        "SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe "
        "WHERE probe_id = $1;"
    ) in runner
    assert (
        "DELETE FROM ask_david_serving_development.goal6_authorization_probe "
        "WHERE probe_id = ${delete_probe_id}"
    ) in runner
    assert "delete-probe-precondition-failed" in runner
    assert '"status":"delete-probe-guard"' in runner
    assert "lower-sentinel-missing" in runner
    assert "upper-sentinel-missing" in runner
    assert (
        "DELETE FROM ask_david_serving_development.goal6_authorization_probe WHERE FALSE"
        not in runner
    )
    assert "disable_empty_partition_prune" not in runner
    assert "CREATE TEMPORARY TABLE" in runner
    for statement_class in ("insert", "update", "delete", "create", "alter", "drop"):
        assert f"assert_permission_denied {statement_class}" in runner
    assert "wrong-rejection-layer" in runner
    assert "doris_privilege_token" in runner
    assert "denial_evidence" in runner
    assert "unauthorized_database" in runner
    assert "green_sm_" not in runner
    assert "DORIS_ADMIN_SECRET" not in runner


def test_goal6_query_limit_runner_is_bounded_and_read_only() -> None:
    runner = (ROOT / "docker/doris-verifier/doris-query-limit-verify").read_text(encoding="utf-8")

    assert "SHOW PROPERTY LIKE" in runner
    assert "SHOW PROPERTY FOR" not in runner
    assert "query_timeout" in runner
    assert "SELECT SLEEP(31);" in runner
    assert "timeout 40 mysql" in runner
    assert '"enforcement":"timeout"' in runner
    for forbidden in ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"):
        assert forbidden not in runner.upper()


def test_goal6_audit_runner_matches_query_identity_target_state_and_workload() -> None:
    runner = (ROOT / "docker/doris-verifier/doris-audit-verify").read_text(encoding="utf-8")

    assert "EXPECTED_QUERY_ID" in runner
    assert "SHOW VARIABLES LIKE 'enable_audit_plugin'" in runner
    assert "SELECT COUNT(*) FROM internal.__internal_schema.audit_log;" in runner
    assert '"status":"audit-plugin-disabled"' in runner
    assert '"status":"audit-plugin-unreadable"' in runner
    assert '"status":"audit-log-empty"' in runner
    assert "internal.__internal_schema.audit_log" in runner
    assert "query_id" in runner
    assert "query_time" in runner
    assert "workload_group" in runner
    assert 'state" != "EOF"' in runner
    assert '"identity_match":true' in runner
    assert '"target_match":true' in runner
    assert '"workload_group_match":true' in runner
    for forbidden in ("INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"):
        assert forbidden not in runner.upper()


def test_goal6_verifier_image_installs_all_later_phase_runners() -> None:
    dockerfile = (ROOT / "docker/Dockerfile.doris-verifier").read_text(encoding="utf-8")

    for runner in (
        "/app/doris-rbac-verify",
        "/app/doris-query-limit-verify",
        "/app/doris-audit-verify",
    ):
        assert runner in dockerfile


def test_goal6_rbac_runner_accepts_only_permission_denials(tmp_path: Path) -> None:
    fake_mysql = tmp_path / "mysql"
    fake_mysql.write_text(
        "#!/bin/sh\n"
        'case "$*" in\n'
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.serving_metric_daily;'*) printf '2\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 126;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 127;'*) printf '0\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 128;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SHOW GRANTS;'*) printf \"goal6_reader\\tSelect_priv\\tgoal6_readonly: Usage_priv\\n\"; exit 0 ;;\n"
        "  *) printf 'ERROR 1044: Access denied; missing privilege\\n' >&2; exit 1 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_mysql.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{tmp_path}:{environment['PATH']}",
            "DORIS_FE_HOST": "10.42.64.238",
            "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
        }
    )

    completed = subprocess.run(
        ["sh", str(ROOT / "docker/doris-verifier/doris-rbac-verify")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 0, completed.stderr
    events = [json.loads(line) for line in completed.stdout.splitlines()]
    assert [event["status"] for event in events if event["status"] == "denied"] == ["denied"] * 7
    assert events[2] == {
        "goal": "goal-06",
        "operation": "rbac-verify",
        "status": "delete-probe-guard",
        "lower_sentinel_present": True,
        "target_absent": True,
        "upper_sentinel_present": True,
    }
    assert {event["denial_evidence"] for event in events if event["status"] == "denied"} == {
        "authorization_text"
    }
    assert events[-1]["status"] == "completed"
    assert events[-1]["positive_select_row_count"] == 2
    assert events[-1]["denied_statement_classes"] == [
        "insert",
        "update",
        "delete",
        "create",
        "alter",
        "drop",
        "unauthorized_database",
    ]


def test_goal6_rbac_runner_accepts_doris_privilege_token_without_raw_error(
    tmp_path: Path,
) -> None:
    fake_mysql = tmp_path / "mysql"
    fake_mysql.write_text(
        "#!/bin/sh\n"
        'case "$*" in\n'
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.serving_metric_daily;'*) printf '2\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 126;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 127;'*) printf '0\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 128;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SHOW GRANTS;'*) printf \"goal6_reader\\tSelect_priv\\tgoal6_readonly: Usage_priv\\n\"; exit 0 ;;\n"
        "  *) printf 'ERROR 1105 (HY000): requires LOAD_PRIV for this operation\\n' >&2; exit 1 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_mysql.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{tmp_path}:{environment['PATH']}",
            "DORIS_FE_HOST": "10.42.64.238",
            "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
        }
    )

    completed = subprocess.run(
        ["sh", str(ROOT / "docker/doris-verifier/doris-rbac-verify")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 0, completed.stderr
    events = [json.loads(line) for line in completed.stdout.splitlines()]
    assert {event["denial_evidence"] for event in events if event["status"] == "denied"} == {
        "doris_privilege_token"
    }
    assert "LOAD_PRIV" not in completed.stdout
    assert "test-only" not in completed.stdout


def test_goal6_rbac_runner_rejects_non_authorization_error(tmp_path: Path) -> None:
    fake_mysql = tmp_path / "mysql"
    fake_mysql.write_text(
        "#!/bin/sh\n"
        'case "$*" in\n'
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.serving_metric_daily;'*) printf '2\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 126;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 127;'*) printf '0\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 128;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SHOW GRANTS;'*) printf \"goal6_reader\\tSelect_priv\\tgoal6_readonly: Usage_priv\\n\"; exit 0 ;;\n"
        "  *) printf 'ERROR 1064 (HY000): syntax error near probe statement\\n' >&2; exit 1 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_mysql.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{tmp_path}:{environment['PATH']}",
            "DORIS_FE_HOST": "10.42.64.238",
            "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
        }
    )

    completed = subprocess.run(
        ["sh", str(ROOT / "docker/doris-verifier/doris-rbac-verify")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 1
    assert json.loads(completed.stderr)["status"] == "wrong-rejection-layer"
    assert "syntax error" not in completed.stderr


def test_goal6_rbac_runner_stops_before_delete_when_reserved_key_exists(
    tmp_path: Path,
) -> None:
    fake_mysql = tmp_path / "mysql"
    mysql_log = tmp_path / "mysql.log"
    fake_mysql.write_text(
        "#!/bin/sh\n"
        'printf \'%s\\n\' "$*" >> "$GOAL6_TEST_MYSQL_LOG"\n'
        'case "$*" in\n'
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.serving_metric_daily;'*) printf '2\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 126;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 127;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 128;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SHOW GRANTS;'*) printf \"goal6_reader\\tSelect_priv\\tgoal6_readonly: Usage_priv\\n\"; exit 0 ;;\n"
        "  *) printf 'ERROR 1044: Access denied; missing privilege\\n' >&2; exit 1 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_mysql.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{tmp_path}:{environment['PATH']}",
            "DORIS_FE_HOST": "10.42.64.238",
            "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
            "GOAL6_TEST_MYSQL_LOG": str(mysql_log),
        }
    )

    completed = subprocess.run(
        ["sh", str(ROOT / "docker/doris-verifier/doris-rbac-verify")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 1
    failure = json.loads(completed.stderr)
    assert failure == {
        "goal": "goal-06",
        "operation": "rbac-verify",
        "status": "delete-probe-precondition-failed",
        "reason": "reserved-key-not-empty",
    }
    assert "DELETE FROM" not in mysql_log.read_text(encoding="utf-8")


def test_goal6_rbac_runner_stops_before_delete_when_nonempty_guard_is_missing(
    tmp_path: Path,
) -> None:
    fake_mysql = tmp_path / "mysql"
    mysql_log = tmp_path / "mysql.log"
    fake_mysql.write_text(
        "#!/bin/sh\n"
        'printf \'%s\\n\' "$*" >> "$GOAL6_TEST_MYSQL_LOG"\n'
        'case "$*" in\n'
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.serving_metric_daily;'*) printf '2\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 126;'*) printf '0\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 127;'*) printf '0\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 128;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SHOW GRANTS;'*) printf \"goal6_reader\\tSelect_priv\\tgoal6_readonly: Usage_priv\\n\"; exit 0 ;;\n"
        "  *) printf 'ERROR 1044: Access denied; missing privilege\\n' >&2; exit 1 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_mysql.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{tmp_path}:{environment['PATH']}",
            "DORIS_FE_HOST": "10.42.64.238",
            "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
            "GOAL6_TEST_MYSQL_LOG": str(mysql_log),
        }
    )

    completed = subprocess.run(
        ["sh", str(ROOT / "docker/doris-verifier/doris-rbac-verify")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 1
    assert json.loads(completed.stderr) == {
        "goal": "goal-06",
        "operation": "rbac-verify",
        "status": "delete-probe-precondition-failed",
        "reason": "lower-sentinel-missing",
    }
    assert "DELETE FROM" not in mysql_log.read_text(encoding="utf-8")


def test_goal6_rbac_runner_sanitizes_reserved_key_query_failure(tmp_path: Path) -> None:
    fake_mysql = tmp_path / "mysql"
    mysql_log = tmp_path / "mysql.log"
    fake_mysql.write_text(
        "#!/bin/sh\n"
        'printf \'%s\\n\' "$*" >> "$GOAL6_TEST_MYSQL_LOG"\n'
        'case "$*" in\n'
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.serving_metric_daily;'*) printf '2\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 126;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 127;'*) printf 'sensitive connection detail\\n' >&2; exit 1 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 128;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SHOW GRANTS;'*) printf \"goal6_reader\\tSelect_priv\\tgoal6_readonly: Usage_priv\\n\"; exit 0 ;;\n"
        "  *) printf 'ERROR 1044: Access denied; missing privilege\\n' >&2; exit 1 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_mysql.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{tmp_path}:{environment['PATH']}",
            "DORIS_FE_HOST": "10.42.64.238",
            "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
            "GOAL6_TEST_MYSQL_LOG": str(mysql_log),
        }
    )

    completed = subprocess.run(
        ["sh", str(ROOT / "docker/doris-verifier/doris-rbac-verify")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 1
    failure = json.loads(completed.stderr)
    assert failure == {
        "goal": "goal-06",
        "operation": "rbac-verify",
        "status": "delete-probe-precondition-failed",
        "reason": "query-failed",
    }
    assert "sensitive connection detail" not in completed.stderr
    assert "DELETE FROM" not in mysql_log.read_text(encoding="utf-8")


def test_goal6_rbac_runner_fails_closed_if_absent_key_delete_is_allowed(
    tmp_path: Path,
) -> None:
    fake_mysql = tmp_path / "mysql"
    mysql_log = tmp_path / "mysql.log"
    fake_mysql.write_text(
        "#!/bin/sh\n"
        'printf \'%s\\n\' "$*" >> "$GOAL6_TEST_MYSQL_LOG"\n'
        'case "$*" in\n'
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.serving_metric_daily;'*) printf '2\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 126;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 127;'*) printf '0\\n'; exit 0 ;;\n"
        "  *'SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 128;'*) printf '1\\n'; exit 0 ;;\n"
        "  *'SHOW GRANTS;'*) printf \"goal6_reader\\tSelect_priv\\tgoal6_readonly: Usage_priv\\n\"; exit 0 ;;\n"
        "  *'DELETE FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 127'*) exit 0 ;;\n"
        "  *) printf 'ERROR 1044: Access denied; missing privilege\\n' >&2; exit 1 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_mysql.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{tmp_path}:{environment['PATH']}",
            "DORIS_FE_HOST": "10.42.64.238",
            "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
            "GOAL6_TEST_MYSQL_LOG": str(mysql_log),
        }
    )

    completed = subprocess.run(
        ["sh", str(ROOT / "docker/doris-verifier/doris-rbac-verify")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 1
    failure = json.loads(completed.stderr)
    assert failure == {
        "goal": "goal-06",
        "operation": "rbac-verify",
        "status": "unexpected-allow",
        "statement_class": "delete",
    }
    calls = mysql_log.read_text(encoding="utf-8")
    lower_sentinel = (
        "SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe "
        "WHERE probe_id = 126;"
    )
    target_absence = (
        "SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe "
        "WHERE probe_id = 127;"
    )
    upper_sentinel = (
        "SELECT COUNT(*) FROM ask_david_serving_development.goal6_authorization_probe "
        "WHERE probe_id = 128;"
    )
    delete = (
        "DELETE FROM ask_david_serving_development.goal6_authorization_probe WHERE probe_id = 127"
    )
    assert (
        calls.index(lower_sentinel)
        < calls.index(target_absence)
        < calls.index(upper_sentinel)
        < calls.index(delete)
    )
    assert calls.count(delete) == 1


def test_goal6_query_limit_runner_requires_configured_timeout_and_enforcement(
    tmp_path: Path,
) -> None:
    fake_mysql = tmp_path / "mysql"
    fake_mysql.write_text(
        "#!/bin/sh\nprintf 'query_timeout\\t30\\n'\n",
        encoding="utf-8",
    )
    fake_mysql.chmod(0o755)
    fake_timeout = tmp_path / "timeout"
    fake_timeout.write_text(
        "#!/bin/sh\nprintf 'ERROR 1105: query timeout exceeded\\n' >&2\nexit 1\n",
        encoding="utf-8",
    )
    fake_timeout.chmod(0o755)
    fake_date = tmp_path / "date"
    fake_date.write_text(
        "#!/bin/sh\n"
        'state="$GOAL6_FAKE_DATE_STATE"\n'
        "if [ -f \"$state\" ]; then printf '130\\n'; else : > \"$state\"; printf '100\\n'; fi\n",
        encoding="utf-8",
    )
    fake_date.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{tmp_path}:{environment['PATH']}",
            "DORIS_FE_HOST": "10.42.64.238",
            "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
            "GOAL6_FAKE_DATE_STATE": str(tmp_path / "date-state"),
        }
    )

    completed = subprocess.run(
        ["sh", str(ROOT / "docker/doris-verifier/doris-query-limit-verify")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 0, completed.stderr
    evidence = json.loads(completed.stdout)
    assert evidence == {
        "goal": "goal-06",
        "operation": "query-limit-verify",
        "status": "completed",
        "configured_query_timeout_seconds": 30,
        "probe_sleep_seconds": 31,
        "execution_duration_seconds": 30,
        "enforcement": "timeout",
    }


def test_goal6_audit_runner_emits_only_sanitized_contract(tmp_path: Path) -> None:
    query_id = "12345678-1234-1234-1234-123456789abc"
    fake_mysql = tmp_path / "mysql"
    fake_mysql.write_text(
        "#!/bin/sh\n"
        'case "$*" in\n'
        "  *\"SHOW VARIABLES LIKE 'enable_audit_plugin'\"*) printf 'enable_audit_plugin\\ttrue\\n' ;;\n"
        "  *\"SELECT COUNT(*) FROM internal.__internal_schema.audit_log;\"*) printf '1\\n' ;;\n"
        f"  *) printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' '{query_id}' true EOF 17 true true ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake_mysql.chmod(0o755)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{tmp_path}:{environment['PATH']}",
            "DORIS_FE_HOST": "10.42.64.238",
            "DORIS_ADMIN_SECRET": '{"username":"goal6_admin","password":"test-only"}',
            "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
            "EXPECTED_QUERY_ID": query_id,
        }
    )

    completed = subprocess.run(
        ["sh", str(ROOT / "docker/doris-verifier/doris-audit-verify")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.returncode == 0, completed.stderr
    evidence = json.loads(completed.stdout)
    assert evidence == {
        "goal": "goal-06",
        "operation": "audit-verify",
        "status": "completed",
        "executed_query_id": query_id,
        "identity_match": True,
        "target_match": True,
        "state": "EOF",
        "query_time_ms": 17,
        "workload_group_match": True,
    }
    assert "test-only" not in completed.stdout


def test_goal6_audit_runner_distinguishes_plugin_and_log_preconditions(tmp_path: Path) -> None:
    query_id = "12345678-1234-1234-1234-123456789abc"
    runner = ROOT / "docker/doris-verifier/doris-audit-verify"

    for mode, expected_marker in (
        ("disabled", '"status":"audit-plugin-disabled"'),
        ("empty", '"status":"audit-log-empty"'),
        ("unreadable", '"status":"audit-log-unreadable"'),
    ):
        fake_mysql = tmp_path / f"mysql-{mode}"
        fake_mysql.write_text(
            "#!/bin/sh\n"
            'case "$*" in\n'
            "  *enable_audit_plugin*)\n"
            "    [ \"$AUDIT_TEST_MODE\" = disabled ] && printf 'enable_audit_plugin\\tfalse\\n' && exit 0\n"
            "    printf 'enable_audit_plugin\\ttrue\\n' ;;\n"
            "  *audit_log*)\n"
            '    [ "$AUDIT_TEST_MODE" = unreadable ] && exit 1\n'
            "    [ \"$AUDIT_TEST_MODE\" = empty ] && printf '0\\n' && exit 0\n"
            "    printf '1\\n' ;;\n"
            "  *) printf 'unexpected\\n' ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        fake_mysql.chmod(0o755)
        environment = os.environ.copy()
        environment.update(
            {
                "PATH": f"{tmp_path}:{environment['PATH']}",
                "AUDIT_TEST_MODE": mode,
                "DORIS_FE_HOST": "10.42.64.238",
                "DORIS_ADMIN_SECRET": '{"username":"goal6_admin","password":"test-only"}',
                "DORIS_QUERY_SECRET": '{"username":"goal6_reader","password":"test-only"}',
                "EXPECTED_QUERY_ID": query_id,
            }
        )
        (tmp_path / "mysql").write_text(fake_mysql.read_text(encoding="utf-8"), encoding="utf-8")
        (tmp_path / "mysql").chmod(0o755)
        completed = subprocess.run(
            ["sh", str(runner)],
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )
        assert completed.returncode == 1
        assert expected_marker in completed.stderr


def test_goal6_admin_task_wrapper_is_private_revision_and_digest_bound() -> None:
    wrapper = (ROOT / "infrastructure/scripts/run-goal6-admin-refresh.ps1").read_text(
        encoding="utf-8"
    )

    assert "ConfirmGoal6AdminRefresh" in wrapper
    assert 'if ($Region -ne "ap-southeast-1")' in wrapper
    assert "aws sts get-caller-identity" in wrapper
    assert "aws ecs describe-task-definition" in wrapper
    assert "ExpectedRevision" in wrapper
    assert "ExpectedImage" in wrapper
    assert "assignPublicIp=DISABLED" in wrapper
    assert "securityGroups=[$AdminSecurityGroupId]" in wrapper
    assert "aws ecs wait tasks-stopped" in wrapper
    assert "aws logs describe-log-streams" in wrapper
    assert "aws logs get-log-events" in wrapper
    assert '"status":"completed"' in wrapper
    assert "No retry is performed" in wrapper
    assert "terraform" not in wrapper.lower()
    assert "databricks" not in wrapper.lower()
    assert "get-secret-value" not in wrapper.lower()


def test_goal6_admin_task_shell_wrapper_is_runnable_private_and_fail_closed() -> None:
    wrapper = (ROOT / "infrastructure/scripts/run-goal6-admin-refresh.sh").read_text(
        encoding="utf-8"
    )

    assert wrapper.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    assert "--confirm-goal6-admin-refresh" in wrapper
    assert '[[ "$region" == "ap-southeast-1" ]]' in wrapper
    assert "expected_fe_host" in wrapper
    assert "expected_be_host" in wrapper
    assert "expected_workspace_host" in wrapper
    assert "aws sts get-caller-identity" in wrapper
    assert "aws ecs describe-task-definition" in wrapper
    assert "expected_revision" in wrapper
    assert "expected_image" in wrapper
    assert 'command == ["/app/doris-admin-refresh"]' in wrapper
    assert "DATABRICKS_OAUTH_SECRET" in wrapper
    assert "DORIS_ADMIN_SECRET" in wrapper
    assert "DORIS_QUERY_SECRET" in wrapper
    assert "assignPublicIp=DISABLED" in wrapper
    assert "securityGroups=[$admin_security_group_id]" in wrapper
    assert "aws ecs wait tasks-stopped" in wrapper
    assert "aws logs get-log-events" in wrapper
    assert 'operation:"admin-refresh"' in wrapper
    assert 'cloudWatchCompletionStatus:"completed"' in wrapper
    assert "no retry is performed" in wrapper
    for forbidden in (
        "terraform",
        "get-secret-value",
        "s3 cp",
        "aws s3",
        "--overrides",
    ):
        assert forbidden.lower() not in wrapper.lower()
    assert not re.search(r"(?m)^\s*databricks\s", wrapper, re.IGNORECASE)


def test_goal6_verifier_shell_wrapper_is_private_allowlisted_and_fail_closed() -> None:
    wrapper = (ROOT / "infrastructure/scripts/run-goal6-verifier.sh").read_text(encoding="utf-8")

    assert wrapper.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    assert "--confirm-goal6-verifier" in wrapper
    assert '[[ "$region" == "ap-southeast-1" ]]' in wrapper
    assert "readonly)" in wrapper
    assert "rbac)" in wrapper
    assert "query-limit)" in wrapper
    assert "/app/doris-readonly-verify" in wrapper
    assert "/app/doris-rbac-verify" in wrapper
    assert "/app/doris-query-limit-verify" in wrapper
    assert "/app/doris-rebuild-serving" not in wrapper
    assert "/app/doris-audit-verify" not in wrapper
    assert "aws sts get-caller-identity" in wrapper
    assert "aws ecs describe-task-definition" in wrapper
    assert "expected_revision" in wrapper
    assert "expected_image" in wrapper
    assert 'command == ["/app/doris-readonly-verify"]' in wrapper
    assert "DORIS_QUERY_SECRET" in wrapper
    assert "DORIS_ADMIN_SECRET" not in wrapper
    assert "DATABRICKS_OAUTH_SECRET" not in wrapper
    assert "assignPublicIp=DISABLED" in wrapper
    assert "securityGroups=[$verifier_security_group_id]" in wrapper
    assert "--overrides" in wrapper
    assert "aws ecs wait tasks-stopped" in wrapper
    assert "aws logs get-log-events" in wrapper
    assert "operationEvidence:$operation_evidence" in wrapper
    assert "no retry is performed" in wrapper
    for forbidden in (
        "terraform",
        "get-secret-value",
        "s3 cp",
        "aws s3",
    ):
        assert forbidden.lower() not in wrapper.lower()
    assert not re.search(r"(?m)^\s*databricks\s", wrapper, re.IGNORECASE)


def test_goal6_admin_operation_wrapper_separates_rebuild_and_audit_approval() -> None:
    wrapper = (ROOT / "infrastructure/scripts/run-goal6-admin-operation.sh").read_text(
        encoding="utf-8"
    )

    assert wrapper.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    assert "--confirm-goal6-rebuild" in wrapper
    assert "--confirm-goal6-audit" in wrapper
    assert "rebuild)" in wrapper
    assert "audit)" in wrapper
    assert "/app/doris-rebuild-serving" in wrapper
    assert "/app/doris-audit-verify" in wrapper
    assert "/app/doris-admin-refresh" in wrapper
    assert "/app/doris-rbac-verify" not in wrapper
    assert "/app/doris-query-limit-verify" not in wrapper
    assert "EXPECTED_QUERY_ID" in wrapper
    assert '[[ "$region" == "ap-southeast-1" ]]' in wrapper
    assert "aws sts get-caller-identity" in wrapper
    assert "aws ecs describe-task-definition" in wrapper
    assert "expected_revision" in wrapper
    assert "expected_image" in wrapper
    assert 'command == ["/app/doris-admin-refresh"]' in wrapper
    assert "DATABRICKS_OAUTH_SECRET" in wrapper
    assert "DORIS_ADMIN_SECRET" in wrapper
    assert "DORIS_QUERY_SECRET" in wrapper
    assert "assignPublicIp=DISABLED" in wrapper
    assert "securityGroups=[$admin_security_group_id]" in wrapper
    assert "--overrides" in wrapper
    assert "aws ecs wait tasks-stopped" in wrapper
    assert "aws logs get-log-events" in wrapper
    assert "operationEvidence:$operation_evidence" in wrapper
    assert "no retry is performed" in wrapper
    for forbidden in (
        "terraform",
        "get-secret-value",
        "s3 cp",
        "aws s3",
    ):
        assert forbidden.lower() not in wrapper.lower()
    assert not re.search(r"(?m)^\s*databricks\s", wrapper, re.IGNORECASE)


def test_goal6_fe_health_wrapper_is_private_entrypoint_aware_and_ping_only() -> None:
    wrapper = (ROOT / "infrastructure/scripts/run-goal6-fe-health.ps1").read_text(encoding="utf-8")

    assert "ConfirmGoal6FeHealth" in wrapper
    assert 'if ($Region -ne "ap-southeast-1")' in wrapper
    assert "ExpectedFeHost" in wrapper
    assert "aws sts get-caller-identity" in wrapper
    assert "aws ecs describe-task-definition" in wrapper
    assert "ExpectedRevision" in wrapper
    assert "ExpectedImage" in wrapper
    assert 'command = @("-c", $healthCommand)' in wrapper
    assert 'command = @("/bin/sh", "-c", $healthCommand)' not in wrapper
    assert "$null -ne $container.entryPoint" in wrapper
    assert 'ENTRYPOINT ["/bin/sh"]' in wrapper
    assert "mysqladmin --ssl --protocol=TCP" in wrapper
    assert "mysql -e" not in wrapper
    assert "assignPublicIp=DISABLED" in wrapper
    assert "securityGroups=[$VerifierSecurityGroupId]" in wrapper
    assert "aws ecs wait tasks-stopped" in wrapper
    assert "aws logs describe-log-streams" in wrapper
    assert "aws logs get-log-events" in wrapper
    assert "mysqld is alive" in wrapper
    assert "Access denied for user" in wrapper
    assert 'cloudWatchHealthStatus = "listener-reachable"' in wrapper
    assert "No retry is performed" in wrapper
    assert "terraform" not in wrapper.lower()
    assert "databricks" not in wrapper.lower()
    assert "get-secret-value" not in wrapper.lower()


def test_goal6_readiness_marker_wrapper_is_private_bounded_and_read_only() -> None:
    wrapper = (ROOT / "infrastructure/scripts/run-goal6-readiness-markers.ps1").read_text(
        encoding="utf-8"
    )

    assert "ConfirmGoal6ReadinessMarkers" in wrapper
    assert 'if ($Region -ne "ap-southeast-1")' in wrapper
    assert "ExpectedFeHost" in wrapper
    assert "ExpectedBeHost" in wrapper
    assert "aws sts get-caller-identity" in wrapper
    assert "aws ecs describe-task-definition" in wrapper
    assert "ExpectedRevision" in wrapper
    assert "ExpectedImage" in wrapper
    assert 'command = @("-c", $markerCommand)' in wrapper
    assert 'command = @("/bin/sh", "-c", $markerCommand)' not in wrapper
    assert "$null -ne $container.entryPoint" in wrapper
    assert "timeout 30 mariadb --ssl --protocol=TCP" in wrapper
    assert "SHOW BACKENDS;" in wrapper
    assert '"role":"fe","listener_state":"ready"' in wrapper
    assert '"role":"fe","marker":"doris-port-ready","port":9030' in wrapper
    assert '"role":"be","listener_state":"ready"' in wrapper
    assert '"role":"be","marker":"doris-port-ready","port":9050' in wrapper
    assert '"role":"be","marker":"be-storage-capacity-ready"' in wrapper
    assert '"non_zero_total_capacity":true' in wrapper
    assert "assignPublicIp=DISABLED" in wrapper
    assert "securityGroups=[$AdminSecurityGroupId]" in wrapper
    assert "aws ecs wait tasks-stopped" in wrapper
    assert "aws logs get-log-events" in wrapper
    assert "No retry is performed" in wrapper
    for forbidden in (
        "terraform",
        "databricks",
        "get-secret-value",
        "ALTER SYSTEM",
        "CREATE ",
        "DROP ",
        "INSERT ",
        "UPDATE ",
        "DELETE ",
        "GRANT ",
        "REVOKE ",
    ):
        assert forbidden.lower() not in wrapper.lower()


def test_goal6_readiness_marker_shell_wrapper_is_runnable_and_fail_closed() -> None:
    wrapper = (ROOT / "infrastructure/scripts/run-goal6-readiness-markers.sh").read_text(
        encoding="utf-8"
    )

    assert wrapper.startswith("#!/usr/bin/env bash\nset -euo pipefail")
    assert "--confirm-goal6-readiness-markers" in wrapper
    assert '[[ "$region" == "ap-southeast-1" ]]' in wrapper
    assert "expected_fe_host" in wrapper
    assert "expected_be_host" in wrapper
    assert "aws sts get-caller-identity" in wrapper
    assert "aws ecs describe-task-definition" in wrapper
    assert "expected_revision" in wrapper
    assert "expected_image" in wrapper
    assert 'command:["-c",$command]' in wrapper
    assert 'command:["/bin/sh","-c",$command]' not in wrapper
    assert "timeout 30 mariadb --ssl --protocol=TCP" in wrapper
    assert "SHOW BACKENDS;" in wrapper
    assert '"role":"fe","listener_state":"ready"' in wrapper
    assert '"role":"fe","marker":"doris-port-ready","port":9030' in wrapper
    assert '"role":"be","listener_state":"ready"' in wrapper
    assert '"role":"be","marker":"doris-port-ready","port":9050' in wrapper
    assert '"role":"be","marker":"be-storage-capacity-ready"' in wrapper
    assert '"non_zero_total_capacity":true' in wrapper
    assert "assignPublicIp=DISABLED" in wrapper
    assert "securityGroups=[$admin_security_group_id]" in wrapper
    assert "aws ecs wait tasks-stopped" in wrapper
    assert "aws logs get-log-events" in wrapper
    assert "no retry is performed" in wrapper
    for forbidden in (
        "terraform",
        "databricks",
        "get-secret-value",
        "ALTER SYSTEM",
        "CREATE ",
        "DROP ",
        "INSERT ",
        "UPDATE ",
        "DELETE ",
        "GRANT ",
        "REVOKE ",
    ):
        assert forbidden.lower() not in wrapper.lower()


def test_goal6_secret_injection_remediation_is_exact_and_private() -> None:
    network_outputs = (ROOT / "infrastructure/modules/network/outputs.tf").read_text(
        encoding="utf-8"
    )
    kms_outputs = (ROOT / "infrastructure/modules/kms/outputs.tf").read_text(encoding="utf-8")
    iam = (ROOT / "infrastructure/modules/iam/main.tf").read_text(encoding="utf-8")
    iam_variables = (ROOT / "infrastructure/modules/iam/variables.tf").read_text(encoding="utf-8")
    goal6 = (ROOT / "infrastructure/environments/development/goal6.tf").read_text(encoding="utf-8")
    development = (ROOT / "infrastructure/environments/development/main.tf").read_text(
        encoding="utf-8"
    )

    assert 'output "aws_endpoints_security_group_id"' in network_outputs
    assert 'output "secrets_key_arn"' in kms_outputs
    assert 'variable "goal6_secret_arns"' in iam_variables
    assert 'variable "goal6_secrets_kms_key_arn"' in iam_variables
    assert 'resource "aws_iam_role_policy" "task_execution_goal6_secrets"' in iam
    assert '"secretsmanager:GetSecretValue"' in iam
    assert '"kms:Decrypt"' in iam
    assert "Resource = var.goal6_secret_arns" in iam
    assert "Resource = var.goal6_secrets_kms_key_arn" in iam
    assert 'resource "aws_vpc_security_group_ingress_rule" "goal6_admin_to_aws_endpoints"' in goal6
    assert (
        'resource "aws_vpc_security_group_ingress_rule" "goal6_verifier_to_aws_endpoints"' in goal6
    )
    assert goal6.count('_to_aws_endpoints"') == 2
    assert (
        goal6.count("security_group_id            = module.network.aws_endpoints_security_group_id")
        == 2
    )
    assert "module.network.aws_endpoints_security_group_id" in goal6
    assert "module.doris_verifier.admin_security_group_id" in goal6
    assert "module.doris_verifier.verifier_security_group_id" in goal6
    assert "cidr_ipv4" not in goal6
    assert (
        'description                  = "Goal 6 read-only verifier access to existing private AWS interface endpoints only."'
        in goal6
    )
    assert "goal6_secret_arns = var.goal_6_enabled ? [" in development
    assert 'module.secrets.secret_arns["doris/admin"]' in development
    assert 'module.secrets.secret_arns["doris/external-read-oauth"]' in development
    assert 'module.secrets.secret_arns["doris/query"]' in development
    assert (
        "goal6_secrets_kms_key_arn = var.goal_6_enabled ? module.kms.secrets_key_arn : null"
        in development
    )
