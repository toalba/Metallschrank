# Providers package
from app.providers.base import BaseProvider, ProviderResult
from app.providers.registry import provider_registry, ProviderRegistry
from app.providers.openfoodfacts import OpenFoodFactsProvider
from app.providers.opengtindb import OpenGTINDBProvider
from app.providers.upcitemdb import UPCItemDBProvider

# Register providers in fallback order: OpenFoodFacts -> OpenGTINDB -> UPCitemdb
provider_registry.register(OpenFoodFactsProvider())
provider_registry.register(OpenGTINDBProvider())
provider_registry.register(UPCItemDBProvider())

__all__ = [
    "BaseProvider",
    "ProviderResult",
    "ProviderRegistry",
    "provider_registry",
    "OpenFoodFactsProvider",
    "OpenGTINDBProvider",
    "UPCItemDBProvider",
]
