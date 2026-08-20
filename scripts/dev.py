"""Cross-platform, non-business developer command dispatcher."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess  # nosec B404
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SAFE_CLEAN_PATHS = (
    ".venv",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".coverage",
    "coverage.xml",
    "htmlcov",
)


def run(command: list[str]) -> None:
    """Run a documented command without invoking a shell."""
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=REPOSITORY_ROOT, check=True)  # nosec B603


def setup() -> None:
    """Install locked development and test dependencies plus Git hooks."""
    run(["uv", "sync", "--all-packages", "--group", "dev", "--group", "test"])
    run(["uv", "run", "pre-commit", "install", "--hook-type", "pre-commit"])
    run(["uv", "run", "pre-commit", "install", "--hook-type", "pre-push"])


def format_code() -> None:
    """Apply deterministic Ruff formatting and safe lint fixes."""
    run(["uv", "run", "ruff", "format", "."])
    run(["uv", "run", "ruff", "check", "--fix", "."])


def format_check() -> None:
    """Verify formatting without modifying source files."""
    run(["uv", "run", "ruff", "format", "--check", "."])


def lint() -> None:
    """Run Ruff linting."""
    run(["uv", "run", "ruff", "check", "."])


def typecheck() -> None:
    """Run strict mypy checks over platform and ingestion package code."""
    run(["uv", "run", "mypy"])


def test() -> None:
    """Run default offline unit tests with coverage."""
    run(["uv", "run", "pytest"])


def validate_environment() -> None:
    """Validate only the safe checked-in local example configuration."""
    run(["uv", "run", "ask-david-validate-environment", "--env-file", ".env.example"])


def security() -> None:
    """Run source, dependency, and secret checks without cloud credentials."""
    run(["uv", "run", "bandit", "-q", "-r", "packages", "scripts"])
    run(["uv", "run", "pip-audit"])
    run(["uv", "run", "detect-secrets-hook", "--baseline", ".secrets.baseline"])


def check() -> None:
    """Run the repository's non-mutating quality and security gate."""
    format_check()
    lint()
    typecheck()
    test()
    databricks_static()
    goal5_static()
    goal6_static()
    security()


def databricks_static() -> None:
    """Validate Goal 4 source contracts without authentication or cloud access."""
    run(["uv", "run", "python", "scripts/validate_goal4.py"])


def goal5_static() -> None:
    """Validate Goal 5 contracts, fixtures, SQL, and scope without cloud access."""
    run(["uv", "run", "python", "scripts/validate_goal5.py"])


def goal6_static() -> None:
    """Validate Goal 6 serving contracts without credentials or cloud access."""
    run(["uv", "run", "python", "scripts/validate_goal6.py"])


TERRAFORM_DEVELOPMENT = "infrastructure/environments/development"
TERRAFORM_BOOTSTRAP = "infrastructure/bootstrap/state"
BOOTSTRAP_BACKEND_TEMPLATE = Path(TERRAFORM_BOOTSTRAP) / "backend.tf.example"

HCL_ASSIGNMENT_PATTERN = re.compile(r"(?m)^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")
KMS_KEY_ARN_PATTERN = re.compile(
    r"^arn:aws:kms:ap-southeast-1:(?P<account_id>[0-9]{12}):key/[0-9a-fA-F-]{36}$"
)
PLACEHOLDER_MARKERS = ("REPLACE_WITH", "<APPROVED", "<REPLACE", "TODO", "CHANGEME")

BOOTSTRAP_REQUIRED_VARIABLES = {
    "aws_account_id",
    "aws_region",
    "bucket_name",
    "tags",
}
DEVELOPMENT_REQUIRED_VARIABLES = {
    "aws_account_id",
    "aws_region",
    "project",
    "environment",
    "additional_tags",
    "vpc_cidr",
    "public_subnet_cidr",
    "application_subnet_cidrs",
    "data_subnet_cidrs",
    "availability_zones",
    "internal_ingress_cidrs",
    "rds_instance_class",
    "redis_node_type",
    "rds_deletion_protection",
    "rds_skip_final_snapshot",
    "log_retention_days",
    "rds_cpu_alarm_threshold_percent",
    "enable_opensearch_foundation",
    "opensearch_collection_prefix",
    "bucket_name_prefix",
}
GOAL4_BOOTSTRAP_REQUIRED_VARIABLES = {
    "databricks_governance_admin_user_name",
    "databricks_metastore_id",
    "databricks_workspace_host",
    "databricks_workspace_id",
}
GOAL4_ACTIVE_REQUIRED_VARIABLES = GOAL4_BOOTSTRAP_REQUIRED_VARIABLES | {
    "databricks_account_id",
    "databricks_sql_warehouse_id",
}
BACKEND_REQUIRED_VALUES = {
    "bucket",
    "key",
    "region",
    "encrypt",
    "use_lockfile",
    "kms_key_id",
}
MANDATORY_BOOTSTRAP_TAGS = {
    "Project",
    "Environment",
    "Component",
    "ManagedBy",
    "Owner",
    "CostCenter",
    "DataClassification",
}
MANDATORY_ADDITIONAL_TAGS = {"Owner", "CostCenter"}


def _read_assignments(path: Path) -> tuple[str, dict[str, str]]:
    """Read simple top-level HCL assignments without rendering their values."""
    text = path.read_text(encoding="utf-8")
    return text, {key: value.strip() for key, value in HCL_ASSIGNMENT_PATTERN.findall(text)}


def _map_keys(text: str, assignment: str) -> set[str]:
    """Return keys from the simple literal map used by local tfvars files."""
    match = re.search(
        rf"(?ms)^\s*{re.escape(assignment)}\s*=\s*\{{(?P<body>.*?)^\s*\}}\s*$",
        text,
    )
    if match is None:
        return set()
    return {key for key, _ in HCL_ASSIGNMENT_PATTERN.findall(match.group("body"))}


def _unquote(value: str) -> str:
    """Normalize a scalar HCL string for structural comparisons."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def _is_placeholder(value: str) -> bool:
    """Identify unresolved values without exposing them."""
    normalized = _unquote(value).strip()
    return not normalized or any(marker in normalized.upper() for marker in PLACEHOLDER_MARKERS)


def _missing_assignments(assignments: dict[str, str], required: set[str]) -> list[str]:
    return sorted(required.difference(assignments))


def validate_infrastructure_preflight(repository_root: Path) -> tuple[list[str], bool]:
    """Validate local pre-3B inputs without network or AWS access.

    Returns validation errors and whether the state KMS ARN is intentionally
    deferred until the approved bootstrap apply.
    """
    bootstrap_tfvars = repository_root / TERRAFORM_BOOTSTRAP / "terraform.tfvars"
    development_tfvars = repository_root / TERRAFORM_DEVELOPMENT / "terraform.tfvars"
    development_backend = repository_root / TERRAFORM_DEVELOPMENT / "backend.hcl"
    required_files = (bootstrap_tfvars, development_tfvars, development_backend)
    missing_files = [
        str(path.relative_to(repository_root)) for path in required_files if not path.is_file()
    ]
    if missing_files:
        return [f"missing required local file: {path}" for path in missing_files], False

    bootstrap_text, bootstrap = _read_assignments(bootstrap_tfvars)
    development_text, development = _read_assignments(development_tfvars)
    _, backend = _read_assignments(development_backend)
    errors: list[str] = []

    for name in _missing_assignments(bootstrap, BOOTSTRAP_REQUIRED_VARIABLES):
        errors.append(f"bootstrap terraform.tfvars is missing {name}")
    for name in _missing_assignments(development, DEVELOPMENT_REQUIRED_VARIABLES):
        errors.append(f"development terraform.tfvars is missing {name}")
    for name in _missing_assignments(backend, BACKEND_REQUIRED_VALUES):
        errors.append(f"development backend.hcl is missing {name}")

    missing_bootstrap_tags = MANDATORY_BOOTSTRAP_TAGS.difference(_map_keys(bootstrap_text, "tags"))
    if missing_bootstrap_tags:
        errors.append("bootstrap tags are missing: " + ", ".join(sorted(missing_bootstrap_tags)))
    missing_development_tags = MANDATORY_ADDITIONAL_TAGS.difference(
        _map_keys(development_text, "additional_tags")
    )
    if missing_development_tags:
        errors.append(
            "development additional_tags are missing: "
            + ", ".join(sorted(missing_development_tags))
        )

    for label, text in (
        ("bootstrap terraform.tfvars", bootstrap_text),
        ("development terraform.tfvars", development_text),
    ):
        if any(marker in text.upper() for marker in PLACEHOLDER_MARKERS):
            errors.append(f"{label} still contains placeholder values")

    goal_4_stage = _unquote(development.get("goal_4_stage", '"disabled"'))
    goal_4_self_assumption = _unquote(
        development.get("goal_4_storage_role_self_assumption_enabled", "false")
    ).lower()
    if goal_4_stage not in {"disabled", "bootstrap", "active"}:
        errors.append("development goal_4_stage must be disabled, bootstrap, or active")
    else:
        goal_4_required = (
            GOAL4_ACTIVE_REQUIRED_VARIABLES
            if goal_4_stage == "active"
            else GOAL4_BOOTSTRAP_REQUIRED_VARIABLES
            if goal_4_stage == "bootstrap"
            else set()
        )
        for name in _missing_assignments(development, goal_4_required):
            errors.append(f"development terraform.tfvars is missing Goal 4 value {name}")
        for name in goal_4_required.intersection(development):
            if _is_placeholder(development[name]):
                errors.append(f"development terraform.tfvars has unresolved Goal 4 value {name}")
        if goal_4_self_assumption not in {"true", "false"}:
            errors.append(
                "development goal_4_storage_role_self_assumption_enabled must be true or false"
            )
        elif goal_4_stage == "active" and goal_4_self_assumption != "true":
            errors.append(
                "development Goal 4 active requires "
                "goal_4_storage_role_self_assumption_enabled = true"
            )

    if not _missing_assignments(backend, BACKEND_REQUIRED_VALUES):
        for name in BACKEND_REQUIRED_VALUES.difference({"kms_key_id"}):
            if _is_placeholder(backend[name]):
                errors.append(f"development backend.hcl has an unresolved {name}")
        if _unquote(backend["key"]) != "development/terraform.tfstate":
            errors.append("development backend key must be development/terraform.tfstate")
        if _unquote(backend["region"]) != "ap-southeast-1":
            errors.append("development backend region must be ap-southeast-1")
        if _unquote(backend["encrypt"]).lower() != "true":
            errors.append("development backend encrypt must be true")
        if _unquote(backend["use_lockfile"]).lower() != "true":
            errors.append("development backend use_lockfile must be true")
        if "bucket_name" in bootstrap and backend["bucket"] != bootstrap["bucket_name"]:
            errors.append("development backend bucket must match the bootstrap bucket_name")
        if "aws_region" in bootstrap and backend["region"] != bootstrap["aws_region"]:
            errors.append("development backend region must match the bootstrap region")
        if (
            "aws_account_id" in bootstrap
            and "aws_account_id" in development
            and bootstrap["aws_account_id"] != development["aws_account_id"]
        ):
            errors.append("bootstrap and development AWS account IDs must match")
        if "aws_region" in development and backend["region"] != development["aws_region"]:
            errors.append("development backend and tfvars regions must match")

    kms_deferred = "kms_key_id" in backend and _is_placeholder(backend["kms_key_id"])
    if "kms_key_id" in backend and not kms_deferred:
        kms_key_arn = _unquote(backend["kms_key_id"])
        kms_match = KMS_KEY_ARN_PATTERN.fullmatch(kms_key_arn)
        if kms_match is None:
            errors.append("development backend kms_key_id must be an ap-southeast-1 KMS key ARN")
        elif "aws_account_id" in bootstrap and (
            kms_match.group("account_id") != _unquote(bootstrap["aws_account_id"])
        ):
            errors.append("development backend KMS key must belong to the approved AWS account")

    bootstrap_source = (repository_root / Path(TERRAFORM_BOOTSTRAP) / "versions.tf").read_text(
        encoding="utf-8"
    )
    if 'backend "s3"' in bootstrap_source:
        errors.append(
            "bootstrap versions.tf must not configure a backend before the local-state apply"
        )
    bootstrap_template = repository_root / BOOTSTRAP_BACKEND_TEMPLATE
    if not bootstrap_template.is_file() or 'backend "s3" {}' not in bootstrap_template.read_text(
        encoding="utf-8"
    ):
        errors.append("bootstrap backend.tf.example must provide the post-apply partial S3 backend")
    development_source = (repository_root / Path(TERRAFORM_DEVELOPMENT) / "versions.tf").read_text(
        encoding="utf-8"
    )
    if 'backend "s3" {}' not in development_source:
        errors.append("development versions.tf is missing the partial S3 backend declaration")

    return errors, kms_deferred


def infra_preflight(*, require_resolved_kms: bool = False) -> None:
    """Check pre-3B local configuration without contacting AWS."""
    errors, kms_deferred = validate_infrastructure_preflight(REPOSITORY_ROOT)
    if errors:
        raise RuntimeError("Infrastructure preflight failed:\n- " + "\n- ".join(errors))
    if require_resolved_kms and kms_deferred:
        raise RuntimeError(
            "Infrastructure preflight failed: kms_key_id must be populated from the "
            "approved state_kms_key_arn bootstrap output before a connected plan."
        )
    if kms_deferred:
        print(
            "Infrastructure preflight passed. kms_key_id remains intentionally deferred "
            "until the approved state bootstrap apply."
        )
    else:
        print("Infrastructure preflight passed with a structurally valid state KMS key ARN.")


def infra_format() -> None:
    """Check Terraform formatting without modifying configuration."""
    run(["terraform", "fmt", "-check", "-recursive", "infrastructure"])


def infra_validate() -> None:
    """Initialize local provider cache only and validate Terraform syntax."""
    run(["terraform", f"-chdir={TERRAFORM_BOOTSTRAP}", "init", "-backend=false"])
    run(["terraform", f"-chdir={TERRAFORM_BOOTSTRAP}", "validate"])
    run(["terraform", f"-chdir={TERRAFORM_DEVELOPMENT}", "init", "-backend=false"])
    run(["terraform", f"-chdir={TERRAFORM_DEVELOPMENT}", "validate"])


def infra_test() -> None:
    """Run mock-provider Terraform contract tests without AWS credentials."""
    run(
        [
            "terraform",
            f"-chdir={TERRAFORM_DEVELOPMENT}",
            "test",
            "-test-directory=tests",
        ]
    )


def infra_lint() -> None:
    """Run Terraform linting; tflint is an explicit development prerequisite."""
    config_path = str(REPOSITORY_ROOT / "infrastructure" / ".tflint.hcl")
    run(["tflint", "--init", f"--config={config_path}"])
    run(["tflint", "--chdir=infrastructure", "--recursive", f"--config={config_path}"])


def infra_security() -> None:
    """Run offline static IaC security checks without cloud credentials."""
    run(["trivy", "config", "--severity", "HIGH,CRITICAL", "--exit-code", "1", "infrastructure"])
    run(["uv", "run", "detect-secrets-hook", "--baseline", ".secrets.baseline"])


def infra_plan() -> None:
    """Produce a connected read-only plan only after deliberate local approval."""
    infra_preflight(require_resolved_kms=True)
    required_files = [
        REPOSITORY_ROOT / TERRAFORM_DEVELOPMENT / "terraform.tfvars",
        REPOSITORY_ROOT / TERRAFORM_DEVELOPMENT / "backend.hcl",
    ]
    has_identity = bool(
        os.environ.get("AWS_PROFILE") or os.environ.get("AWS_WEB_IDENTITY_TOKEN_FILE")
    )
    if (
        os.environ.get("ASK_DAVID_AWS_PLAN_APPROVED") != "true"
        or not has_identity
        or not all(path.exists() for path in required_files)
    ):
        raise RuntimeError(
            "infra-plan is intentionally blocked. Set ASK_DAVID_AWS_PLAN_APPROVED=true, "
            "provide AWS_PROFILE or workload identity, and create ignored terraform.tfvars "
            "and backend.hcl. "
            "This command never applies resources."
        )
    run(["terraform", f"-chdir={TERRAFORM_DEVELOPMENT}", "init", "-backend-config=backend.hcl"])
    run(["terraform", f"-chdir={TERRAFORM_DEVELOPMENT}", "plan", "-input=false"])


def local_up() -> None:
    """Start only local development dependencies and wait for health checks."""
    run(["docker", "compose", "--env-file", ".env.example", "up", "--detach", "--wait"])


def local_down() -> None:
    """Stop local development dependencies without deleting volumes."""
    run(["docker", "compose", "--env-file", ".env.example", "down"])


def local_logs() -> None:
    """Show recent logs for local development dependencies."""
    run(["docker", "compose", "--env-file", ".env.example", "logs", "--tail=100"])


def clean() -> None:
    """Remove only known local build and test artifacts."""
    for relative_path in SAFE_CLEAN_PATHS:
        path = REPOSITORY_ROOT / relative_path
        if path.is_dir():
            print(f"Removing {path.relative_to(REPOSITORY_ROOT)}")
            shutil.rmtree(path)
        elif path.is_file():
            print(f"Removing {path.relative_to(REPOSITORY_ROOT)}")
            path.unlink()


COMMANDS = {
    "setup": setup,
    "format": format_code,
    "format-check": format_check,
    "lint": lint,
    "typecheck": typecheck,
    "test": test,
    "validate-env": validate_environment,
    "security": security,
    "check": check,
    "local-up": local_up,
    "local-down": local_down,
    "local-logs": local_logs,
    "infra-format": infra_format,
    "infra-preflight": infra_preflight,
    "infra-validate": infra_validate,
    "infra-test": infra_test,
    "infra-lint": infra_lint,
    "infra-security": infra_security,
    "infra-plan": infra_plan,
    "databricks-static": databricks_static,
    "goal5-static": goal5_static,
    "goal6-static": goal6_static,
    "clean": clean,
}


def parse_args() -> argparse.Namespace:
    """Parse exactly one supported developer command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=sorted(COMMANDS))
    return parser.parse_args()


def main() -> int:
    """Dispatch the selected command and return a shell-compatible status."""
    command = parse_args().command
    COMMANDS[command]()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from error
