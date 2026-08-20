"""Goal 5 static validation must tolerate an approved later bundle include."""

from pathlib import Path

from scripts.validate_goal5 import validate_goal5_repository

ROOT = Path(__file__).resolve().parents[2]


def test_goal5_scope_guard_does_not_reject_shared_goal6_bundle_root() -> None:
    """Goal 5 owns its manifest, not the shared bundle root's future includes."""
    assert validate_goal5_repository(ROOT) == []
