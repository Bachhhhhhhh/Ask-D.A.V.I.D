"""Regression checks for the Goal 3B PowerShell runtime smoke wrapper."""

from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_SMOKE_SCRIPT = REPOSITORY_ROOT / "infrastructure/scripts/run-runtime-smoke.ps1"


def test_runtime_smoke_avoids_post_stop_eni_lookup_race() -> None:
    """Stopped-task validation must use durable ECS attachment metadata."""
    script = RUNTIME_SMOKE_SCRIPT.read_text(encoding="utf-8")

    assert "assignPublicIp=DISABLED" in script
    assert '$_.name -eq "privateIPv4Address"' in script
    assert "describe-network-interfaces" not in script
    assert "private ECS ENI attachment" in script
