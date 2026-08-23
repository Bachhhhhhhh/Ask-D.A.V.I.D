"""Credential-free provider configuration for the four reasoning roles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ProviderName = Literal["openai", "novita"]


@dataclass(frozen=True, slots=True)
class ReasoningProviderConfig:
    provider: ProviderName
    model: str
    credential_env_var: str


SUPERVISOR_PROVIDER = ReasoningProviderConfig(
    provider="openai",
    model="configured-at-deployment",
    credential_env_var="ASK_DAVID_OPENAI_SECRET_REFERENCE",
)
SPECIALIZED_PROVIDER = ReasoningProviderConfig(
    provider="novita",
    model="configured-at-deployment",
    credential_env_var="ASK_DAVID_NOVITA_SECRET_REFERENCE",
)
