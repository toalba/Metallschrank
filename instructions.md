# Copilot Agent Instruction Set — Metal Cabinet Inventory (SvelteKit + FastAPI + Postgres)

## Ziel
Initialisiere ein sauberes Monorepo-Projekt für eine Inventarisierungs-Webapp (Metallschrank).
Kernfeatures:
1) Barcode/Strichcode scannen (mobilfähig) + alternative manuelle Eingabe
2) Barcode Lookup: zuerst lokale DB, falls unbekannt -> öffentliche API abfragen
3) Ergebnis als Produkt/Artikel in DB persistieren und anschließend Inventar-Buchungen ermöglichen

Technologie-Stack:
- Frontend: SvelteKit (TypeScript)
- Backend: FastAPI (Python 3.11+)
- DB: PostgreSQL
- Container: Docker Compose
- Migration: Alembic
- ORM: SQLAlchemy 2.0 (async) + asyncpg
- API Schema: Pydantic v2
- Lint/Format: ruff + black (Python), eslint + prettier (Svelte/TS)

Wichtig:
- Saubere Projektstruktur, klare Trennung FE/BE
- Offline ist "nice-to-have", aber nicht Pflicht; Fokus: zuverlässig im LAN/Internet
- Public API Provider als austauschbare Module (mindestens Open Food Facts als free option)

---

## Projektstruktur (Monorepo)
Erzeuge diese Struktur:

/inventory-app
  /frontend        # SvelteKit
  /backend         # FastAPI
  /infra           # docker, init scripts
  docker-compose.yml
  .env.example
  README.md

---

## Architektur
### Datenmodell (Minimum)
- Product:
  - id (uuid)
  - gtin (string, unique, nullable)         # EAN/UPC/GTIN
  - name (string)
  - brand (string, nullable)
  - image_url (string, nullable)
  - source (enum: "manual" | "openfoodfacts" | "upcitemdb" | "barcodelookup" | "unknown")
  - raw_payload (jsonb, nullable)           # komplette Provider-Antwort zum Debugging
  - created_at, updated_at

- InventoryItem:
  - id (uuid)
  - product_id (fk -> Product)
  - location (string)                       # z.B. "Schrank A / Fach 3 / Box 2"
  - quantity (numeric/int)
  - unit (string, default "pcs")
  - notes (text, nullable)
  - created_at, updated_at

- InventoryTransaction (optional initial, aber ideal):
  - id (uuid)
  - inventory_item_id (fk)
  - delta (int)
  - reason (enum: "add"|"remove"|"adjust")
  - created_at

### API-Flows
- POST /api/lookup
  input: { code: string }
  output:
    - if product exists: { status:"found", product:{...} }
    - else:
      - try providers (configured order)
      - if provider returns product: create Product (source=provider)
      - return { status:"created", product:{...} }
      - if not found: { status:"not_found" }

- CRUD für Product & InventoryItem minimal:
  - GET /api/products?query=
  - POST /api/products (manual)
  - GET /api/inventory
  - POST /api/inventory (create item with product reference)
  - POST /api/inventory/{id}/adjust (delta)

---

## Public Barcode APIs / Provider-Strategie
Implementiere Provider als Interface:
- BaseProvider.lookup(code)-> ProviderResult | None

Mindestens 1 Provider sofort implementieren:
- Open Food Facts (gratis) via HTTPS JSON API
  - Ergebnis normalisieren (name/brand/image_url)
  - raw_payload speichern

Provider sollen über ENV toggelbar sein:
- BARCODE_PROVIDERS="openfoodfacts"
- Optional später: upcitemdb/barcodelookup (nur wenn API key vorhanden)

---

## Backend Anforderungen (FastAPI)
1) Async FastAPI app mit Router "/api"
2) SQLAlchemy async engine, Alembic migrations
3) Settings via pydantic-settings (.env)
4) Unit Tests minimal (pytest) für:
   - lookup: local hit
   - lookup: provider hit (mock http)
   - lookup: not found
5) Saubere Error Handling / Timeouts
6) CORS für Frontend Dev

### Backend Implementationsdetails
- HTTP Client: httpx (async)
- Timeout: 3-5s
- Caching: optional simple DB-level by storing Product result; no redis initially

---

## Frontend Anforderungen (SvelteKit)
Pages:
- /scan
  - Kamera-Scan Button + Fallback Eingabefeld
  - Nach Scan: call POST /api/lookup
  - Zeige Ergebnis (Produktname/Marke/Bild)
  - Button: "Als Inventar hinzufügen" -> location + qty Form

- /inventory
  - Liste der InventoryItems, Filter/Search
  - Quick adjust (+1/-1)

Scanning:
- Verwende eine robuste JS lib (z.B. @zxing/browser).
- Implementiere einen Scan-Component, der:
  - mobile camera stream startet
  - Code erkennt
  - bei success stoppt und event dispatcht
  - fallback manual input

Frontend muss:
- API Base URL über env (VITE_API_BASE_URL oder SvelteKit env) unterstützen
- In dev: proxy oder CORS nutzen

---

## Docker Compose Anforderungen
Services:
- postgres (port 5432)
- backend (uvicorn)
- frontend (vite dev optional, oder build + node)
Für Start: compose up -> alles läuft lokal.
Erzeuge init scripts:
- backend: alembic upgrade head bei start (oder dokumentiert als step)

---

## Konventionen & Qualität
- Typed Python (mypy optional, aber type hints überall)
- Linting configs erzeugen
- README mit Setup:
  - cp .env.example .env
  - docker compose up --build
  - migrations
  - open localhost URLs

---

## Deliverables (Output)
1) Repo vollständig generiert mit Code
2) Beispiel .env.example
3) README mit Runbook
4) Funktionierender End-to-end Flow:
   - User scannt Code -> Backend lookup -> DB persist -> Inventar-Eintrag erstellen

---

## Prioritäten (Implementationsreihenfolge)
1) Docker Compose + DB + Backend skeleton + migrations
2) Product Model + /api/lookup mit local hit
3) OpenFoodFacts provider + persist
4) Frontend /scan mit manual input -> lookup
5) Camera scanning component
6) Inventar CRUD minimal

---

## Akzeptanzkriterien
- `docker compose up --build` startet ohne manuelle Eingriffe
- Scan page kann Code manuell senden und bekommt Result
- Wenn Code unbekannt:
  - Provider wird aufgerufen
  - wenn gefunden: Product wird in Postgres gespeichert
  - bei erneutem Scan: local DB hit (kein Provider call nötig)
- Inventar-Item kann mit Location + Quantity gespeichert werden
