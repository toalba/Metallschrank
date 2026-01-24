from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderResult:
    """Result from a barcode provider lookup"""
    code: str
    name: str
    provider_name: str  # Name of the provider that returned this result
    brand: Optional[str] = None
    image_url: Optional[str] = None
    raw_data: Optional[dict] = None


class BaseProvider(ABC):
    """Abstract base class for barcode providers"""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g., 'openfoodfacts')"""
        pass
    
    @abstractmethod
    async def lookup(self, code: str) -> Optional[ProviderResult]:
        """
        Look up a barcode.
        
        Args:
            code: The barcode/GTIN to lookup
            
        Returns:
            ProviderResult if found, None otherwise
        """
        pass
