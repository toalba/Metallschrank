from typing import List, Optional
from app.providers.base import BaseProvider, ProviderResult
from app.core.config import settings


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
    
    async def lookup(self, code: str) -> Optional[ProviderResult]:
        """
        Try to lookup barcode using all active providers in order.
        Returns first successful result.
        """
        for provider in self.get_active_providers():
            try:
                result = await provider.lookup(code)
                if result:
                    return result
            except Exception as e:
                # Log error but continue to next provider
                print(f"Provider {provider.provider_name} failed: {e}")
                continue
        return None


# Global registry instance
provider_registry = ProviderRegistry()
