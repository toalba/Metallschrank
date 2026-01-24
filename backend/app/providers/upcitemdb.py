from typing import Optional
import httpx
from app.providers.base import BaseProvider, ProviderResult


class UPCItemDBProvider(BaseProvider):
    """Provider for UPCitemdb API"""
    
    BASE_URL = "https://api.upcitemdb.com/prod/trial"
    TIMEOUT = 5.0
    
    @property
    def provider_name(self) -> str:
        return "upcitemdb"
    
    async def lookup(self, code: str) -> Optional[ProviderResult]:
        """
        Lookup product on UPCitemdb.
        
        API docs: https://www.upcitemdb.com/api/explorer
        Note: Trial API has rate limits
        """
        url = f"{self.BASE_URL}/lookup"
        
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT) as client:
                response = await client.get(
                    url,
                    params={"upc": code},
                    headers={"User-Agent": "MetallschrankInventory/1.0"}
                )
                response.raise_for_status()
                data = response.json()
                
                # Check if product was found
                if data.get("code") != "OK" or "items" not in data or not data["items"]:
                    return None
                
                # Get first item
                item = data["items"][0]
                
                # Extract and normalize data
                name = item.get("title") or item.get("description") or "Unknown Product"
                brand = item.get("brand")
                
                # UPCitemdb has images array
                images = item.get("images")
                image_url = images[0] if images and len(images) > 0 else None
                
                return ProviderResult(
                    code=code,
                    name=name,
                    provider_name=self.provider_name,
                    brand=brand,
                    image_url=image_url,
                    raw_data=data
                )
                
        except httpx.TimeoutException:
            print(f"UPCitemdb timeout for code {code}")
            return None
        except httpx.HTTPError as e:
            print(f"UPCitemdb HTTP error for code {code}: {e}")
            return None
        except Exception as e:
            print(f"UPCitemdb unexpected error for code {code}: {e}")
            return None
