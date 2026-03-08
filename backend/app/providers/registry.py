import asyncio
import logging
from typing import List, Optional

from app.providers.base import BaseProvider, ProviderResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry for managing barcode providers"""

    def __init__(self):
        self._providers: dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider):
        """Register a provider"""
        self._providers[provider.provider_name] = provider

    def get_provider(self, name: str) -> Optional[BaseProvider]:
        """Get a specific provider by name"""
        return self._providers.get(name)

    def get_active_providers(self) -> List[BaseProvider]:
        """Get list of active providers based on settings"""
        active = []
        for provider_name in settings.provider_list:
            provider = self._providers.get(provider_name)
            if provider:
                active.append(provider)
        return active

    async def _safe_lookup(self, provider: BaseProvider, code: str) -> Optional[ProviderResult]:
        """Lookup with error handling for a single provider."""
        try:
            return await provider.lookup(code)
        except Exception as e:
            logger.warning(f"Provider {provider.provider_name} failed for {code}: {e}")
            return None

    async def lookup(self, code: str) -> Optional[ProviderResult]:
        """
        Query all active providers concurrently.
        Returns the first successful result (in provider priority order).
        """
        providers = self.get_active_providers()
        if not providers:
            return None

        # Run all providers concurrently
        results = await asyncio.gather(
            *(self._safe_lookup(p, code) for p in providers)
        )

        # Return first non-None result in priority order
        for result in results:
            if result:
                return result
        return None


# Global registry instance
provider_registry = ProviderRegistry()
