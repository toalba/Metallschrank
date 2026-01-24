# Metallschrank Inventory System

## Project Overview
SvelteKit + FastAPI + PostgreSQL monorepo for barcode-based inventory management. Users scan barcodes (mobile-friendly), lookup products via local DB or public APIs (OpenFoodFacts), then create inventory items with location tracking.

## Architecture

### Monorepo Structure
```
/frontend    # SvelteKit (TypeScript) - barcode scanning UI
/backend     # FastAPI (Python 3.11+) - async API + barcode providers
/infra       # Docker setup, init scripts
docker-compose.yml
```

### Data Model (SQLAlchemy async + asyncpg)
- **Product**: gtin (EAN/UPC), name, brand, image_url, source (enum: manual|openfoodfacts|...), raw_payload (jsonb)
- **InventoryItem**: product_id (FK), location (string: "Schrank A / Fach 3"), quantity, unit, notes
- **InventoryTransaction**: inventory_item_id (FK), delta (int), reason (enum: add|remove|adjust)

### Key API Flow: POST /api/lookup
1. Check local DB for existing product by code
2. If not found: call configured providers (OpenFoodFacts first)
3. Normalize response → create Product with source + raw_payload
4. Return product to frontend for inventory creation

## Tech Stack Specifics

### Backend (FastAPI)
- **Async everything**: SQLAlchemy 2.0 async engine, httpx for provider calls
- **Migrations**: Alembic (`alembic upgrade head` on startup)
- **Settings**: pydantic-settings from .env (BARCODE_PROVIDERS, DATABASE_URL)
- **Provider pattern**: BaseProvider.lookup(code) → ProviderResult | None
  - Implement OpenFoodFacts provider with 3-5s timeout
  - Store raw_payload for debugging/reprocessing
- **Lint**: ruff + black

### Frontend (SvelteKit)
- **Barcode scanning**: @zxing/browser for camera stream + manual fallback
- **Key pages**: /scan (camera + lookup + "add to inventory" form), /inventory (list + quick adjust ±1)
- **API integration**: VITE_API_BASE_URL env var, handle CORS in dev
- **Lint**: eslint + prettier

### Docker Compose
- Services: postgres:15, backend (uvicorn), frontend (Vite dev or build), nginx (reverse proxy)
- Init: backend runs `alembic upgrade head` on container start
- One command: `docker compose up --build` → full stack running
- **CORS strategy**: 
  - Development: FastAPI CORS middleware allows `http://localhost:5173`
  - Production: nginx proxies `/api/*` → backend:8000, serves frontend static files
  - nginx config: `infra/nginx.conf` with proxy_pass for API routes

## Development Workflows

### Initial Setup
```bash
cp .env.example .env
docker compose up --build
# Backend auto-runs migrations
# Nginx: http://localhost (proxies to frontend + /api/ to backend)
# Direct access: Frontend :5173, Backend :8000/docs (dev only)
```

### CORS Configuration
- **Dev mode**: FastAPI app includes CORS middleware with origins from `CORS_ORIGINS` env var
- **Production**: nginx reverse proxy eliminates CORS (same-origin for browser)
- Example nginx location blocks:
  ```nginx
  location /api/ { proxy_pass http://backend:8000; }
  location / { proxy_pass http://frontend:5173; }  # or serve static
  ```

### Adding a New Barcode Provider
1. Create `backend/app/providers/your_provider.py` implementing `BaseProvider`
2. Add normalization logic for name/brand/image_url
3. Register in settings: `BARCODE_PROVIDERS="openfoodfacts,your_provider"`
4. Add unit test mocking HTTP response

### Testing
- Backend: `pytest` with async fixtures, mock httpx calls for providers
- Critical tests: lookup local hit, provider hit (mocked), not found scenario

## Project Conventions
- **German location strings**: "Schrank A / Fach 3 / Box 2" (cabinet/shelf/box hierarchy)
- **Type hints everywhere**: Python mypy-compatible, TypeScript strict mode
- **Error handling**: 3-5s provider timeouts, graceful fallback to "not_found"
- **No aspirational caching**: rely on Product DB persistence (no Redis initially)

## Common Tasks
- **Add product manually**: POST /api/products with gtin, name, brand
- **Adjust inventory**: POST /api/inventory/{id}/adjust with delta (±quantity)
- **Debug barcode lookup**: check Product.raw_payload jsonb field for provider response
