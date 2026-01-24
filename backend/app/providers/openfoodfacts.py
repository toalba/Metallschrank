from typing import Optional
import httpx
from app.providers.base import BaseProvider, ProviderResult


class OpenFoodFactsProvider(BaseProvider):
    """Provider for Open Food Facts API"""
    
    BASE_URL = "https://world.openfoodfacts.org/api/v2"
    TIMEOUT = 5.0
    
    @property
    def provider_name(self) -> str:
        return "openfoodfacts"
    
    async def lookup(self, code: str) -> Optional[ProviderResult]:
        """
        Lookup product on Open Food Facts.
        
        API docs: https://openfoodfacts.github.io/openfoodfacts-server/api/
        """
        url = f"{self.BASE_URL}/product/{code}"
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": "MetallschrankInventory/1.0"}
                )
                response.raise_for_status()
                data = response.json()
                
                # Check if product was found
                if data.get("status") != 1 or "product" not in data:
                    return None
                
                product = data["product"]
                
                # Extract and normalize data
                name = (
                    product.get("product_name") or
                    product.get("product_name_en") or
                    product.get("generic_name") or
                    "Unknown Product"
                )
                
                brand = product.get("brands", "").split(",")[0].strip() if product.get("brands") else None
                
                image_url = (
                    product.get("image_url") or
                    product.get("image_front_url") or
                    None
                )
                
                return ProviderResult(
                    code=code,
                    name=name,
                    provider_name=self.provider_name,
                    brand=brand,
                    image_url=image_url,
                    raw_data=data
                )
                
        except httpx.TimeoutException:
            print(f"OpenFoodFacts timeout for code {code}")
            return None
        except httpx.HTTPError as e:
            print(f"OpenFoodFacts HTTP error for code {code}: {e}")
            return None
        except Exception as e:
            print(f"OpenFoodFacts unexpected error for code {code}: {e}")
            return None
