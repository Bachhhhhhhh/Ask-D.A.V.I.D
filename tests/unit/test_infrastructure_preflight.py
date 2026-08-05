"""Tests for the credential-free pre-3B infrastructure preflight."""

from pathlib import Path

from scripts.dev import validate_infrastructure_preflight


def write_preflight_fixture(root: Path, *, include_cost_center: bool = True) -> None:
    """Create safe local configuration fixtures without credentials or network access."""
    bootstrap = root / "infrastructure/bootstrap/state"
    development = root / "infrastructure/environments/development"
    bootstrap.mkdir(parents=True)
    development.mkdir(parents=True)
    (bootstrap / "versions.tf").write_text('terraform {\n  backend "s3" {}\n}\n', encoding="utf-8")
    (development / "versions.tf").write_text(
        'terraform {\n  backend "s3" {}\n}\n', encoding="utf-8"
    )
    (bootstrap / "terraform.tfvars").write_text(
        """aws_account_id = "123456789012"
aws_region = "ap-southeast-1"
bucket_name = "ask-david-state-example"
tags = {
  Project = "ask-david"
  Environment = "development"
  Component = "terraform-state"
  ManagedBy = "terraform"
  Owner = "platform-team"
  CostCenter = "development"
  DataClassification = "infrastructure-metadata"
}
""",
        encoding="utf-8",
    )
    cost_center = '  CostCenter = "development"\n' if include_cost_center else ""
    (development / "terraform.tfvars").write_text(
        f"""aws_account_id = "123456789012"
aws_region = "ap-southeast-1"
project = "ask-david"
environment = "development"
additional_tags = {{
  Owner = "platform-team"
{cost_center}}}
vpc_cidr = "10.42.0.0/16"
public_subnet_cidr = "10.42.0.0/24"
application_subnet_cidrs = ["10.42.16.0/20", "10.42.32.0/20"]
data_subnet_cidrs = ["10.42.64.0/20", "10.42.80.0/20"]
availability_zones = ["ap-southeast-1a", "ap-southeast-1b"]
internal_ingress_cidrs = ["10.42.0.0/16"]
rds_instance_class = "db.t4g.micro"
redis_node_type = "cache.t4g.micro"
rds_deletion_protection = true
rds_skip_final_snapshot = false
log_retention_days = 30
enable_opensearch_foundation = false
opensearch_collection_prefix = "ask-david"
bucket_name_prefix = "ask-david-example"
""",
        encoding="utf-8",
    )
    (development / "backend.hcl").write_text(
        """bucket = "ask-david-state-example"
key = "development/terraform.tfstate"
region = "ap-southeast-1"
encrypt = true
use_lockfile = true
kms_key_id = "REPLACE_WITH_STATE_KMS_KEY_ARN_OUTPUT"
""",
        encoding="utf-8",
    )


def test_preflight_accepts_intentionally_deferred_kms_output(tmp_path: Path) -> None:
    """The KMS ARN is the only value allowed to remain deferred before Goal 3B."""
    write_preflight_fixture(tmp_path)

    errors, kms_deferred = validate_infrastructure_preflight(tmp_path)

    assert errors == []
    assert kms_deferred is True


def test_preflight_rejects_missing_cost_attribution(tmp_path: Path) -> None:
    """Required ownership and cost tags cannot be silently omitted."""
    write_preflight_fixture(tmp_path, include_cost_center=False)

    errors, _ = validate_infrastructure_preflight(tmp_path)

    assert "development additional_tags are missing: CostCenter" in errors


def test_preflight_rejects_state_bucket_mismatch_without_rendering_values(tmp_path: Path) -> None:
    """Bootstrap and backend bucket names must agree without entering diagnostics."""
    write_preflight_fixture(tmp_path)
    backend = tmp_path / "infrastructure/environments/development/backend.hcl"
    backend.write_text(
        backend.read_text(encoding="utf-8").replace(
            "ask-david-state-example", "different-state-bucket"
        ),
        encoding="utf-8",
    )

    errors, _ = validate_infrastructure_preflight(tmp_path)

    assert "development backend bucket must match the bootstrap bucket_name" in errors
    assert all("different-state-bucket" not in error for error in errors)


def test_preflight_rejects_kms_key_from_another_account(tmp_path: Path) -> None:
    """The state KMS key must belong to the same approved account as the bucket."""
    write_preflight_fixture(tmp_path)
    backend = tmp_path / "infrastructure/environments/development/backend.hcl"
    backend.write_text(
        backend.read_text(encoding="utf-8").replace(
            "REPLACE_WITH_STATE_KMS_KEY_ARN_OUTPUT",
            "arn:aws:kms:ap-southeast-1:999999999999:key/12345678-1234-1234-1234-123456789012",
        ),
        encoding="utf-8",
    )

    errors, kms_deferred = validate_infrastructure_preflight(tmp_path)

    assert "development backend KMS key must belong to the approved AWS account" in errors
    assert kms_deferred is False
