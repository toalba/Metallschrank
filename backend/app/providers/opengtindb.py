from typing import Optional
import httpx
from app.providers.base import BaseProvider, ProviderResult


class OpenGTINDBProvider(BaseProvider):
    """Provider for OpenGTINDB API"""
    
    BASE_URL = "https://opengtindb.org"
    TIMEOUT = 10.0
    
    @property
    def provider_name(self) -> str:
        return "opengtindb"
    
    async def lookup(self, code: str) -> Optional[ProviderResult]:
        """
        Lookup product on OpenGTINDB.
        
        API docs: https://opengtindb.org
        """
        url = f"{self.BASE_URL}/api/v1/search"
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    url,
                    params={"query": code},
                    headers={"User-Agent": "MetallschrankInventory/1.0"}
                )
                response.raise_for_status()
                data = response.json()
                
                # Check if product was found
                if not data or "products" not in data or not data["products"]:
                    return None
                
                # Get first product
                product = data["products"][0]
                
                # Extract and normalize data
                name = product.get("name") or product.get("product_name") or "Unknown Product"
                brand = product.get("brand") or product.get("manufacturer")
                
                # OpenGTINDB may have image_url field
                image_url = product.get("image_url") or product.get("image")
                
                return ProviderResult(
                    code=code,
                    name=name,
                    provider_name=self.provider_name,
                    brand=brand,
                    image_url=image_url,
                    raw_data=data
                )
                
        except httpx.TimeoutException:
            print(f"OpenGTINDB timeout for code {code}")
            return None
        except httpx.HTTPError as e:
            print(f"OpenGTINDB HTTP error for code {code}: {e}")
            return None
        except Exception as e:
            print(f"OpenGTINDB unexpected error for code {code}: {e}")
            return None
