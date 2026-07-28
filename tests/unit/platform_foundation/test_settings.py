"""Unit tests for typed, non-secret configuration validation."""

import pytest
from ask_david_foundation.settings import Environment, PlatformSettings
from pydantic import ValidationError


def valid_values() -> dict[str, object]:
    """Return a complete safe configuration for unit tests."""
    return {
        "environment": "development",
        "log_level": "INFO",
        "postgres_host": "127.0.0.1",
        "postgres_port": 5432,
        "postgres_database": "ask_david_local",
        "postgres_username": "local_developer",
        "redis_host": "127.0.0.1",
        "redis_port": 6379,
    }


def test_valid_settings_are_typed_and_safely_summarized() -> None:
    """A valid configuration renders diagnostics without a credential field."""
    settings = PlatformSettings(**valid_values())

    assert settings.environment is Environment.DEVELOPMENT
    assert settings.safe_summary() == (
        "environment=development; log_level=INFO; "
        "postgres=127.0.0.1:5432/ask_david_local; redis=127.0.0.1:6379"
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("postgres_host", "   ", "must not be blank"),
        ("postgres_port", 0, "must be between 1 and 65535"),
        ("redis_port", 65_536, "must be between 1 and 65535"),
    ],
)
def test_invalid_connection_values_fail_with_clear_messages(
    field: str, value: object, message: str
) -> None:
    """Blank values and invalid ports cannot pass configuration validation."""
    values = valid_values()
    values[field] = value

    with pytest.raises(ValidationError, match=message):
        PlatformSettings(**values)


def test_missing_required_value_fails_clearly() -> None:
    """Required settings are not silently supplied with production-like defaults."""
    values = valid_values()
    del values["redis_host"]

    with pytest.raises(ValidationError, match="redis_host"):
        PlatformSettings(**values)
