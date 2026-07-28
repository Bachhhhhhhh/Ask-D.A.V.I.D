"""Tests for the safe configuration-validation command."""

from collections.abc import Iterator

import pytest
from ask_david_foundation.validate_environment import main


@pytest.fixture()
def valid_environment(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    """Provide a complete safe local environment without reading files or the network."""
    values = {
        "PLATFORM_ENVIRONMENT": "development",
        "PLATFORM_LOG_LEVEL": "INFO",
        "PLATFORM_POSTGRES_HOST": "127.0.0.1",
        "PLATFORM_POSTGRES_PORT": "5432",
        "PLATFORM_POSTGRES_DATABASE": "ask_david_local",
        "PLATFORM_POSTGRES_USERNAME": "local_developer",
        "PLATFORM_REDIS_HOST": "127.0.0.1",
        "PLATFORM_REDIS_PORT": "6379",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    yield


def test_validation_command_reports_sanitized_success(
    valid_environment: None, capsys: pytest.CaptureFixture[str]
) -> None:
    """The command reports an explicit valid result without exposing credentials."""
    assert main() == 0

    assert capsys.readouterr().out.startswith("Configuration is valid: environment=development")


def test_validation_command_reports_missing_required_values(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The command emits a clear nonzero validation error for missing configuration."""
    for name in (
        "PLATFORM_ENVIRONMENT",
        "PLATFORM_LOG_LEVEL",
        "PLATFORM_POSTGRES_HOST",
        "PLATFORM_POSTGRES_PORT",
        "PLATFORM_POSTGRES_DATABASE",
        "PLATFORM_POSTGRES_USERNAME",
        "PLATFORM_REDIS_HOST",
        "PLATFORM_REDIS_PORT",
    ):
        monkeypatch.delenv(name, raising=False)

    assert main() == 1
    assert "Configuration validation failed" in capsys.readouterr().out


def test_validation_command_loads_the_safe_example(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The developer command can validate the checked-in non-secret example file."""
    for name in (
        "PLATFORM_ENVIRONMENT",
        "PLATFORM_LOG_LEVEL",
        "PLATFORM_POSTGRES_HOST",
        "PLATFORM_POSTGRES_PORT",
        "PLATFORM_POSTGRES_DATABASE",
        "PLATFORM_POSTGRES_USERNAME",
        "PLATFORM_REDIS_HOST",
        "PLATFORM_REDIS_PORT",
    ):
        monkeypatch.delenv(name, raising=False)

    assert main(["--env-file", ".env.example"]) == 0
    assert "Configuration is valid" in capsys.readouterr().out
