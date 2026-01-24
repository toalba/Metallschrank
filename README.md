# Metallschrank Inventory System

Barcode-based inventory management system built with SvelteKit (frontend), FastAPI (backend), and PostgreSQL (database).

## Features

- 📱 Mobile-friendly barcode scanning using device camera
- 🔍 Automatic product lookup via Open Food Facts API
- 📦 Inventory tracking with location hierarchy (Schrank/Fach/Box)
- ➕➖ Quick inventory adjustments
- 🗄️ Local product database with caching
- 🐳 Complete Docker Compose setup

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **SQLAlchemy 2.0** - Async ORM with asyncpg driver
- **Alembic** - Database migrations
- **PostgreSQL 15** - Database
- **httpx** - Async HTTP client for provider APIs

### Frontend
- **SvelteKit** - Modern Svelte framework with TypeScript
- **@zxing/browser** - Barcode scanning library
- **Vite** - Build tool and dev server

### Infrastructure
- **Docker Compose** - Container orchestration
- **nginx** - Reverse proxy for API and frontend

## Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) Node.js 20+ and Python 3.11+ for local development

### Setup and Run

1. **Clone the repository**
   ```bash
   cd /root/metallschrank
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env if needed (defaults work for local development)
   ```

3. **Start all services**
   ```bash
   docker compose up --build
   ```

   This will:
   - Start PostgreSQL database
   - Run database migrations automatically
   - Start FastAPI backend on port 8000
   - Start SvelteKit frontend on port 5173
   - Start nginx reverse proxy on port 80

4. **Access the application**
   - **Main app**: http://localhost
   - **API docs**: http://localhost/docs
   - **Direct backend**: http://localhost:8000 (dev only)
   - **Direct frontend**: http://localhost:5173 (dev only)

## Project Structure

```
/root/metallschrank/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # API routes (lookup, products, inventory)
│   │   ├── core/        # Config, database setup
│   │   ├── models/      # SQLAlchemy models
│   │   ├── providers/   # Barcode lookup providers
│   │   └── schemas/     # Pydantic schemas
│   ├── alembic/         # Database migrations
│   ├── tests/           # pytest tests
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # SvelteKit application
│   ├── src/
│   │   ├── lib/         # Components and utilities
│   │   │   ├── components/  # Svelte components
│   │   │   └── api.ts       # API client
│   │   └── routes/      # SvelteKit pages
│   │       ├── scan/    # Barcode scanning page
│   │       └── inventory/   # Inventory list page
│   ├── Dockerfile
│   └── package.json
├── infra/               # Infrastructure configs
│   ├── nginx.conf       # Reverse proxy config
│   └── init.sql         # PostgreSQL init script
├── docker-compose.yml   # Container orchestration
└── .env.example         # Environment template
```

## Development Workflows

### Backend Development

1. **Install dependencies**
   ```bash
   cd backend
   source /path/to/venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```

2. **Create database migration**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Description"
   ```

3. **Apply migrations**
   ```bash
   alembic upgrade head
   ```

4. **Run tests**
   ```bash
   pytest
   ```

### Frontend Development

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run dev server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

4. **Lint and format**
   ```bash
   npm run lint
   npm run format
   ```

### Adding a New Barcode Provider

1. Create provider class in `backend/app/providers/your_provider.py`:
   ```python
   from app.providers.base import BaseProvider, ProviderResult
   
   class YourProvider(BaseProvider):
       @property
       def provider_name(self) -> str:
           return "your_provider"
       
       async def lookup(self, code: str) -> Optional[ProviderResult]:
           # Implement API call and normalization
           pass
   ```

2. Register in `backend/app/providers/__init__.py`:
   ```python
   from app.providers.your_provider import YourProvider
   provider_registry.register(YourProvider())
   ```

3. Enable in `.env`:
   ```
   BARCODE_PROVIDERS=openfoodfacts,your_provider
   ```

## API Endpoints

### Barcode Lookup
- `POST /api/lookup` - Lookup barcode (checks DB, then providers)
  ```json
  {"code": "4012345678901"}
  ```

### Products
- `GET /api/products` - List products (with optional `?query=` search)
- `POST /api/products` - Manually create product
- `GET /api/products/{id}` - Get product by ID

### Inventory
- `GET /api/inventory` - List inventory items (with optional `?location=` filter)
- `POST /api/inventory` - Create inventory item
- `GET /api/inventory/{id}` - Get inventory item
- `POST /api/inventory/{id}/adjust` - Adjust quantity (±delta)
  ```json
  {"delta": 5, "reason": "add"}
  ```

## Database Schema

### Product
- `id` (UUID, primary key)
- `gtin` (string, unique, indexed) - EAN/UPC barcode
- `name` (string) - Product name
- `brand` (string, nullable)
- `image_url` (string, nullable)
- `source` (enum: manual|openfoodfacts|...)
- `raw_payload` (JSONB, nullable) - Original provider response
- `created_at`, `updated_at` (timestamps)

### InventoryItem
- `id` (UUID, primary key)
- `product_id` (FK → Product)
- `location` (string) - e.g., "Schrank A / Fach 3 / Box 2"
- `quantity` (numeric)
- `unit` (string, default "pcs")
- `notes` (text, nullable)
- `created_at`, `updated_at` (timestamps)

### InventoryTransaction
- `id` (UUID, primary key)
- `inventory_item_id` (FK → InventoryItem)
- `delta` (integer) - Quantity change
- `reason` (enum: add|remove|adjust)
- `created_at` (timestamp)

## Configuration

### Environment Variables

```bash
# Database
POSTGRES_USER=inventory
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=inventory
DATABASE_URL=postgresql+asyncpg://inventory:your_secure_password_here@postgres:5432/inventory

# Backend
BARCODE_PROVIDERS=openfoodfacts,opengtindb,upcitemdb  # Comma-separated list
CORS_ORIGINS=http://localhost:5173,http://localhost

# Frontend
VITE_API_BASE_URL=/api
```

## Troubleshooting

### Database connection fails
- Ensure PostgreSQL container is healthy: `docker compose ps`
- Check logs: `docker compose logs postgres`

### Migrations not applied
- Backend runs `alembic upgrade head` on startup
- Check backend logs: `docker compose logs backend`
- Manually run: `docker compose exec backend alembic upgrade head`

### CORS errors
- In development: Backend CORS middleware should allow origins from `CORS_ORIGINS`
- In production: nginx proxies all requests (same-origin, no CORS needed)

### Camera not working
- HTTPS required for camera access (or localhost)
- Check browser permissions
- Use manual input as fallback

## License

[Your License Here]

## Contributors

[Your Team/Name Here]
