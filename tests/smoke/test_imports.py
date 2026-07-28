"""Smoke tests that never require network access or cloud credentials."""

from ask_david_foundation import Environment, PlatformSettings


def test_foundation_package_exports_typed_configuration() -> None:
    """The shared foundation package is importable by future workspace members."""
    assert Environment.DEVELOPMENT == "development"
    assert PlatformSettings.__name__ == "PlatformSettings"
