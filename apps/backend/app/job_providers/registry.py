"""Provider registry for CareerPilot job discovery."""

from __future__ import annotations

from app.job_providers.base import JobProvider
from app.job_providers.demo import DemoProvider


class JobProviderRegistry:
    """Central registry to keep provider additions isolated and simple."""

    def __init__(self, providers: list[JobProvider] | None = None) -> None:
        self._providers = providers or [DemoProvider()]

    def list(self) -> list[JobProvider]:
        return list(self._providers)

    def get(self, provider_name: str) -> JobProvider | None:
        for provider in self._providers:
            if provider.provider_name == provider_name:
                return provider
        return None


def get_default_providers() -> list[JobProvider]:
    return [DemoProvider()]
