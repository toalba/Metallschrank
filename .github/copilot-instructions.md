# Metallschrank Inventory System

## Architecture Overview
SvelteKit + FastAPI + PostgreSQL monorepo for barcode-based inventory. Barcodes are looked up via local DB first, then external providers (OpenFoodFacts, etc.), then saved for future lookups.

```
/frontend    # SvelteKit (TypeScript) - /scan, /inventory pages
/backend     # FastAPI (Python 3.11+) - async API + provider pattern
/infra       # nginx.conf, init.sql
```

## Core Data Flow: `/api/lookup`
See [lookup.py](backend/app/api/routes/lookup.py) - the central endpoint:
1. Query local DB by GTIN → return if found
2. Call `provider_registry.lookup(code)` → tries providers in `BARCODE_PROVIDERS` order
3. Save new Product with `source` enum + `raw_payload` (JSONB) for debugging
4. Frontend receives product → user creates InventoryItem with location

## Key Patterns

### Provider Pattern (Backend)
All barcode APIs implement `BaseProvider` ([base.py](backend/app/providers/base.py)):
```python
class YourProvider(BaseProvider):
    TIMEOUT = 5.0  # Required: 3-5s timeout
    
    @property
    def provider_name(self) -> str: return "yourprovider"
    
    async def lookup(self, code: str) -> Optional[ProviderResult]:
        # Use httpx async client, return ProviderResult or None
```
Register in [registry.py](backend/app/providers/registry.py), add to `ProductSource` enum in [product.py](backend/app/models/product.py), enable via `BARCODE_PROVIDERS` env var.

### Async SQLAlchemy
All DB operations use async patterns. See [database.py](backend/app/core/database.py):
```python
async with AsyncSessionLocal() as session:
    result = await db.execute(select(Product).where(...))
```

### Frontend API Client
[api.ts](frontend/src/lib/api.ts) wraps all endpoints with auth. Uses `PUBLIC_API_BASE_URL` env var (defaults to `/api`).

### Authentication
Simple HTTP Basic Auth for all API routes (except `/api/ping`). See [auth.py](backend/app/core/auth.py):
- Credentials via env vars: `ADMIN_USERNAME`, `ADMIN_PASSWORD` (default: admin/admin)
- Frontend stores credentials in localStorage via [auth.ts](frontend/src/lib/auth.ts)
- All API calls include `Authorization: Basic <base64>` header automatically
- 401 response → auto-logout and redirect to `/login`

## Development Commands
```bash
# Full stack (runs migrations automatically)
docker compose up --build

# Access points:
# - https://localhost (nginx proxy, self-signed SSL)
# - http://localhost:8000/docs (FastAPI Swagger, direct)
# - http://localhost:5173 (Vite dev server, if running locally)

# New migration after model changes
cd backend && alembic revision --autogenerate -m "description"
```

## Conventions
- **Location format**: German hierarchy "Schrank A / Fach 3 / Box 2"
- **Provider timeouts**: Always 3-5s, fail gracefully returning `None`
- **raw_payload**: Store full provider response for debugging/reprocessing
- **Enums**: `ProductSource` for data origin, `TransactionReason` for inventory changes
- **UUIDs**: All primary keys use `uuid4`
