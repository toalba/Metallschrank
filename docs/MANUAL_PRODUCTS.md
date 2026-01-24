# Manuelle Produkterfassung

## Übersicht
Das Metallschrank-System bietet zwei Wege, Produkte manuell ohne automatische Barcode-Erkennung hinzuzufügen:

1. **Nach fehlgeschlagenem Barcode-Lookup**: Wenn ein Barcode nicht gefunden wird
2. **Ohne Barcode**: Für Produkte die keinen Barcode haben (handgemachte Waren, lose Artikel, etc.)

## Funktionsweise

### Szenario 1: Barcode nicht gefunden

```
Benutzer scannt/gibt Barcode ein
  ↓
System sucht in allen Providern (OpenFoodFacts, OpenGTINDB, UPCitemdb)
  ↓
Nicht gefunden → "Nicht gefunden" Meldung
  ↓
Button: "Produkt manuell hinzufügen"
  ↓
Formular öffnet sich mit vorausgefülltem Barcode
  ↓
Benutzer gibt Name, Marke (optional), Bild-URL (optional) ein
  ↓
Produkt wird mit dem Barcode als "manual" source erstellt
```

### Szenario 2: Produkt ohne Barcode

```
Benutzer klickt "Neues Produkt ohne Barcode anlegen" (unten auf Scan-Seite)
  ↓
Formular öffnet sich mit leerem Barcode-Feld
  ↓
Benutzer gibt Name, optional Marke, Bild-URL ein
  ↓
Barcode-Feld leer lassen
  ↓
Produkt wird ohne GTIN erstellt (gtin = null)
```

## UI-Komponenten

### Scan-Seite Erweiterungen

**"Nicht gefunden" Bereich:**
```svelte
<div class="not-found-message">
  <p>Kein Produkt für diesen Code gefunden.</p>
  <button on:click={showManualProductForm}>
    Produkt manuell hinzufügen
  </button>
</div>
```

**Manuelles Produktformular:**
```svelte
<form on:submit={handleCreateManualProduct}>
  <input bind:value={manualProduct.gtin} placeholder="Barcode (optional)" />
  <input bind:value={manualProduct.name} placeholder="Produktname *" required />
  <input bind:value={manualProduct.brand} placeholder="Marke (optional)" />
  <input bind:value={manualProduct.image_url} placeholder="Bild-URL (optional)" />
  
  <button type="submit">Produkt erstellen</button>
  <button type="button" on:click={cancelManualForm}>Abbrechen</button>
</form>
```

**"Ohne Barcode" Bereich:**
```svelte
<div class="no-barcode-section">
  <h2>Produkt ohne Barcode hinzufügen</h2>
  <p>Für handgemachte Produkte, lose Waren oder Artikel ohne Barcode</p>
  <button on:click={() => { barcodeInput = ''; showManualProductForm(); }}>
    Neues Produkt ohne Barcode anlegen
  </button>
</div>
```

## Backend API

### POST /api/products

**Request Body:**
```json
{
  "gtin": "4006040038043",  // Optional, kann null sein
  "name": "Apfelsaft naturtrüb",  // Required
  "brand": "Valensina",  // Optional
  "image_url": "https://...",  // Optional
  "source": "manual"  // Automatisch gesetzt
}
```

**Response:**
```json
{
  "id": "uuid",
  "gtin": "4006040038043",  // oder null
  "name": "Apfelsaft naturtrüb",
  "brand": "Valensina",
  "image_url": "https://...",
  "source": "manual"
}
```

**Validierung:**
- GTIN muss unique sein (falls angegeben)
- Name ist Pflichtfeld
- Source wird automatisch auf "manual" gesetzt

## Datenmodell

### Product.gtin Feld

```python
gtin: Mapped[str | None] = mapped_column(
    String(50),
    unique=True,  # Unique constraint
    index=True,   # Indexed für schnelle Suche
    nullable=True # Kann NULL sein
)
```

**Wichtig:**
- `nullable=True` erlaubt Produkte ohne Barcode
- `unique=True` verhindert Duplikate (NULL-Werte gelten als unique in PostgreSQL)
- Index ermöglicht schnelle Barcode-Lookups

### ProductSource Enum

```python
class ProductSource(str, enum.Enum):
    MANUAL = "manual"  # Manuell vom Benutzer erstellt
    OPENFOODFACTS = "openfoodfacts"
    OPENGTINDB = "opengtindb"
    UPCITEMDB = "upcitemdb"
    # ...
```

## Workflow

### Kompletter Ablauf: Barcode → Manuell → Inventar

1. **Barcode scannen/eingeben**
   ```
   Benutzer: Gibt "1234567890" ein → Nicht gefunden
   ```

2. **Manuelles Formular ausfüllen**
   ```
   GTIN: 1234567890 (vorausgefüllt)
   Name: "Selbstgemachte Marmelade"
   Marke: "" (leer)
   Bild: "" (leer)
   ```

3. **Produkt erstellen**
   ```
   POST /api/products
   → Product ID: abc-123
   → Source: manual
   ```

4. **Automatische Weiterleitung zu Inventar-Formular**
   ```
   lookupResult = { status: "created", product: {...} }
   → Inventar-Formular erscheint
   ```

5. **Zum Inventar hinzufügen**
   ```
   Standort: Metallschrank/Fach2
   Menge: 3
   Einheit: Glas
   Notizen: "Erdbeere"
   ```

### Ablauf: Ohne Barcode

1. **Button klicken**
   ```
   "Neues Produkt ohne Barcode anlegen"
   → Formular öffnet sich
   → barcodeInput = ""
   → manualProduct.gtin = ""
   ```

2. **Formular ausfüllen**
   ```
   GTIN: (leer lassen)
   Name: "Lose Äpfel"
   Marke: "Bio-Hof Müller"
   ```

3. **Produkt mit gtin=null erstellen**
   ```
   POST /api/products { gtin: undefined, name: "Lose Äpfel", ... }
   → Product mit gtin=null in DB
   ```

4. **Direkt zu Inventar**
   ```
   lookupResult gesetzt → Inventar-Formular erscheint
   ```

## State Management

### Frontend State Variables

```typescript
// Manual product creation state
let showManualForm = false;  // Formular anzeigen/verstecken
let manualProduct = {
  name: '',
  brand: '',
  image_url: '',
  gtin: ''  // Vorausgefüllt mit barcodeInput wenn "nicht gefunden"
};
let isCreatingProduct = false;  // Loading state
let productError: string | null = null;  // Fehler-Nachricht
```

### Funktionen

**showManualProductForm():**
- Setzt `showManualForm = true`
- Füllt `manualProduct.gtin` mit aktuellem `barcodeInput`
- Nützlich wenn Barcode nicht gefunden wurde

**cancelManualForm():**
- Schließt Formular
- Reset aller Felder
- Löscht Fehlermeldungen

**handleCreateManualProduct():**
- Validiert Input (Name required)
- Sendet POST /api/products
- Bei Erfolg: Setzt `lookupResult` → Inventar-Formular erscheint
- Lädt existierendes Inventar für dieses Produkt
- Reset Formular

## Styling

### Visuelle Trennung

**Dashed Border für "manuelle" Bereiche:**
```css
.manual-product-section,
.no-barcode-section {
  border: 2px dashed #dee2e6;  /* Unterscheidet von normalen Bereichen */
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
}
```

**"oder" Divider:**
```
━━━━━━━━ oder ━━━━━━━━
```

Trennt visually Scanner/Lookup von manuellen Optionen.

### Mobile Optimierung

- Touch-friendly Buttons (min-height: 44px)
- Responsive Formular-Layouts
- Stack Buttons vertikal bei <768px

## Fehlerbehandlung

### Validierung Frontend

```typescript
if (!manualProduct.name.trim()) {
  productError = 'Produktname ist erforderlich';
  return;
}
```

### Validierung Backend

**Duplikat-GTIN:**
```python
if product.gtin:
    result = await db.execute(
        select(Product).where(Product.gtin == product.gtin)
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "Product with GTIN already exists")
```

**Fehler wird im Frontend als `productError` angezeigt.**

## Verwendungsszenarien

### 1. Unbekannter Barcode
- Produkt aus lokalem Laden
- Neue/seltene Produkte nicht in APIs
- Import-Produkte mit unbekannten Barcodes

### 2. Produkte ohne Barcode
- Selbstgemachte Waren (Marmelade, Kuchen)
- Lose Waren (Obst, Gemüse vom Markt)
- Haushaltsartikel ohne Verpackung
- Handwerkliche Produkte
- Second-Hand Artikel

### 3. Barcode temporär nicht lesbar
- Beschädigte Verpackung
- Verwischter/verschmierter Barcode
- Kamera funktioniert nicht

## Testing

### Test 1: Nicht gefundener Barcode

```bash
# Barcode eingeben der in keiner API existiert
1. Gib "9999999999999" ein
2. "Nicht gefunden" Meldung erscheint
3. Klick "Produkt manuell hinzufügen"
4. Formular hat "9999999999999" vorausgefüllt
5. Füge Name hinzu → Erstellen
6. Inventar-Formular erscheint
```

### Test 2: Ohne Barcode

```bash
1. Scrolle zu "Produkt ohne Barcode hinzufügen"
2. Klick Button
3. Formular öffnet mit leerem GTIN
4. Fülle Name, Marke aus
5. GTIN leer lassen → Erstellen
6. Produkt mit gtin=null in DB
7. Inventar-Formular erscheint
```

### Test 3: Duplikat-Erkennung

```bash
1. Erstelle Produkt mit GTIN "1234567890"
2. Versuche zweites Produkt mit selber GTIN
3. Fehler: "Product with GTIN already exists"
```

## Vorteile

✅ **Flexibilität**: Auch Produkte ohne Barcode erfassen
✅ **Schnell**: Direkt nach Creation zu Inventar-Formular
✅ **Benutzfreundlich**: Barcode vorausgefüllt wenn "nicht gefunden"
✅ **Vollständig**: Alle Felder optional außer Name
✅ **Eindeutig**: GTIN-Unique-Constraint verhindert Duplikate
✅ **Nachverfolgbar**: Source="manual" kennzeichnet manuell erstellte Produkte

## Erweiterungsmöglichkeiten

### Zukünftige Features

1. **Bild-Upload**: Foto vom Produkt direkt hochladen statt URL
2. **Batch-Import**: CSV-Datei mit mehreren manuellen Produkten
3. **Barcode-Generator**: QR-Code für Produkte ohne Barcode generieren
4. **Kategorien**: Tags/Kategorien für manuelle Produkte
5. **Duplikat-Vorschläge**: "Ähnliche Produkte existieren bereits" Warning
