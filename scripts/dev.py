"""Cross-platform, non-business developer command dispatcher."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
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
    subprocess.run(command, cwd=REPOSITORY_ROOT, check=True)


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
    """Run strict mypy checks over foundation package code."""
    run(["uv", "run", "mypy"])


def test() -> None:
    """Run default offline unit tests with coverage."""
    run(["uv", "run", "pytest"])


def validate_environment() -> None:
    """Validate only the safe checked-in local example configuration."""
    run(["uv", "run", "ask-david-validate-environment", "--env-file", ".env.example"])


def security() -> None:
    """Run source, dependency, and secret checks without cloud credentials."""
    run(["uv", "run", "bandit", "-q", "-r", "packages"])
    run(["uv", "run", "pip-audit"])
    run(["uv", "run", "detect-secrets-hook", "--baseline", ".secrets.baseline"])


def check() -> None:
    """Run the repository's non-mutating quality and security gate."""
    format_check()
    lint()
    typecheck()
    test()
    security()


TERRAFORM_DEVELOPMENT = "infrastructure/environments/development"


def infra_format() -> None:
    """Check Terraform formatting without modifying configuration."""
    run(["terraform", f"-chdir={TERRAFORM_DEVELOPMENT}", "fmt", "-check", "-recursive"])


def infra_validate() -> None:
    """Initialize local provider cache only and validate Terraform syntax."""
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
    "infra-validate": infra_validate,
    "infra-test": infra_test,
    "infra-lint": infra_lint,
    "infra-security": infra_security,
    "infra-plan": infra_plan,
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
