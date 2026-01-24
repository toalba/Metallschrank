# Barcode Provider System - Fallback Chain

## Overview
The Metallschrank inventory system uses a fallback chain of barcode providers to maximize product lookup success rates. When a barcode is scanned, the system tries multiple providers in sequence until one returns a result.

## Provider Chain (in order)

1. **OpenFoodFacts** (`openfoodfacts`)
   - Primary provider for food products
   - Base URL: `https://world.openfoodfacts.org/api/v2`
   - Free, no API key required
   - Coverage: Excellent for food/beverage items

2. **OpenGTINDB** (`opengtindb`)
   - First fallback provider
   - Base URL: `https://opengtindb.org`
   - Free, community-driven database
   - Coverage: General products, wider range than OpenFoodFacts

3. **UPCitemdb** (`upcitemdb`)
   - Final fallback provider
   - Base URL: `https://api.upcitemdb.com/prod/trial` (trial API)
   - Rate limits apply on trial tier
   - Coverage: Very wide, includes many obscure products

## How It Works

### Lookup Flow
```
User scans barcode
  ↓
Check local database
  ↓ (if not found)
Try OpenFoodFacts
  ↓ (if returns None)
Try OpenGTINDB
  ↓ (if returns None)
Try UPCitemdb
  ↓ (if returns None)
Return "not_found"
```

### Implementation
The `ProviderRegistry` class (`backend/app/providers/registry.py`) handles the fallback logic:

```python
async def lookup(self, code: str) -> Optional[ProviderResult]:
    """Try all active providers in order"""
    for provider in self.get_active_providers():
        result = await provider.lookup(code)
        if result:
            return result  # Stop on first success
    return None
```

## Provider Architecture

### Base Provider
All providers implement `BaseProvider` abstract class:

```python
class BaseProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass
    
    @abstractmethod
    async def lookup(self, code: str) -> Optional[ProviderResult]:
        pass
```

### Provider Result
Each provider returns a `ProviderResult` with normalized data:

```python
@dataclass
class ProviderResult:
    code: str              # The barcode/GTIN
    name: str              # Product name
    provider_name: str     # Which provider returned this
    brand: Optional[str]   # Brand/manufacturer
    image_url: Optional[str]  # Product image
    raw_data: Optional[dict]  # Original API response
```

## Configuration

### Environment Variables
Edit `.env` to configure active providers:

```bash
# Comma-separated list in fallback order
BARCODE_PROVIDERS=openfoodfacts,opengtindb,upcitemdb
```

To disable fallback (OpenFoodFacts only):
```bash
BARCODE_PROVIDERS=openfoodfacts
```

### Database Source Tracking
Each product stores which provider found it in the `source` field:

```python
class ProductSource(enum.Enum):
    MANUAL = "manual"           # User-entered
    OPENFOODFACTS = "openfoodfacts"
    OPENGTINDB = "opengtindb"
    UPCITEMDB = "upcitemdb"
    UNKNOWN = "unknown"
```

## Adding New Providers

### 1. Create Provider Class
Create `backend/app/providers/your_provider.py`:

```python
from app.providers.base import BaseProvider, ProviderResult

class YourProvider(BaseProvider):
    BASE_URL = "https://api.yourprovider.com"
    TIMEOUT = 5.0
    
    @property
    def provider_name(self) -> str:
        return "yourprovider"
    
    async def lookup(self, code: str) -> Optional[ProviderResult]:
        # Implementation here
        pass
```

### 2. Register Provider
Edit `backend/app/providers/__init__.py`:

```python
from app.providers.your_provider import YourProvider

provider_registry.register(YourProvider())
```

### 3. Add to Enum
Edit `backend/app/models/product.py`:

```python
class ProductSource(str, enum.Enum):
    YOURPROVIDER = "yourprovider"
```

### 4. Update Config
Edit `.env`:

```bash
BARCODE_PROVIDERS=openfoodfacts,opengtindb,upcitemdb,yourprovider
```

## API Details

### OpenFoodFacts
- **Endpoint**: `GET /api/v2/product/{barcode}.json`
- **Response**: `{"status": 1, "product": {...}}`
- **Fields**: `product_name`, `brands`, `image_url`
- **Docs**: https://wiki.openfoodfacts.org/API

### OpenGTINDB
- **Endpoint**: `GET /api/v1/search?query={barcode}`
- **Response**: `{"products": [...]}`
- **Fields**: `name`, `brand`, `image_url`
- **Note**: Actual API format may vary, implementation is based on expected structure

### UPCitemdb
- **Endpoint**: `GET /prod/trial/lookup?upc={barcode}`
- **Response**: `{"code": "OK", "items": [...]}`
- **Fields**: `title`, `brand`, `images[]`
- **Docs**: https://www.upcitemdb.com/api/explorer
- **Rate Limits**: Trial API has daily limits

## Error Handling
All providers gracefully handle:
- Timeouts (5 seconds)
- HTTP errors (404, 500, etc.)
- Invalid JSON responses
- Missing fields

Failed lookups return `None`, allowing the next provider to try.

## Testing

### Manual Testing
```bash
# Scan a barcode not in OpenFoodFacts
# System will automatically try OpenGTINDB, then UPCitemdb
# Check product.source field to see which provider found it
```

### Check Active Providers
```bash
docker compose exec backend python -c "from app.providers import provider_registry; print([p.provider_name for p in provider_registry._providers.values()])"
```

### View Logs
```bash
docker compose logs backend --tail 50 | grep -i "provider\|lookup"
```

## Performance Considerations

- **Sequential Lookup**: Providers are tried one at a time (not parallel) to respect rate limits and avoid unnecessary API calls
- **Caching**: Once found, products are stored in local database (no repeated API calls for same barcode)
- **Timeouts**: Each provider has 5-second timeout to prevent slow responses from blocking
- **Rate Limits**: UPCitemdb trial API has daily limits; consider upgrading for production

## Migration Notes

When adding the new provider enum values, a migration was created:

```bash
# Migration adds 'opengtindb' to productsource enum
docker compose exec backend alembic upgrade head
```

PostgreSQL doesn't allow removing enum values easily, so downgrade is not fully reversible.
