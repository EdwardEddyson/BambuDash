# Architectural Specification — Phase 4: Frontend Development & Live-Check Fixes

This specification describes the requirements for Phase 4 frontend development and location-aware live feasibility check integration for **BambuDash**.

---

## 🔧 Cross-Cutting Concerns

### 0a. Typed API Client Layer
- Refactor `src/lib/api-client.ts` into a structured, typed API client.
- Create TypeScript interfaces for all Backend-Responses (Filament, Project, Order, User, Printer, etc.).
- Provide namespace-grouped methods: `api.filaments.list()`, `api.filaments.enrich(id, data)`, `api.orders.getCart()`, `api.projects.checkFeasibility(id)`, etc.
- All API errors must be handled consistently (typed error responses).

### 0b. Mock-Daten-Kennzeichnung
- Alle Stellen im Frontend, die aktuell Testdaten/Mock-Daten verwenden, müssen visuell klar als `[TESTDATEN]` gekennzeichnet sein.
- Verwende ein einheitliches UI-Element (z.B. ein kleines oranges Badge `TESTDATEN` oder einen gestrichelten Rahmen) an jeder Komponente, die Mock-Daten zeigt.
- Dies gilt für: Dashboard-KPIs (soweit nicht aus API), Printer-Telemetrie, Activity-Feed, und alle anderen Mock-Daten.
- Wenn eine Seite echte API-Daten nutzt, soll keine Kennzeichnung erscheinen.

### 0c. Makerworld API-Proxy (Backend — nachholen aus Phase 3)
- Der Makerworld-Endpoint (`/api/v1/makerworld/search`) existiert nicht im Backend, obwohl er in der Roadmap als erledigt markiert war.
- **Backend muss nachgebaut werden:** `GET /api/v1/makerworld/search?q=<query>` — Proxy zur Makerworld API, gibt Modell-Titel, Preview-Thumbnail-URL, Designer-Name, und Makerworld-URL zurück.
- Wird als Dependency für das Projekt-Kanban-Board benötigt.

---

## 🏗️ Requirements

### 1. Location-Aware Live Feasibility Check (Backend Fix)
- Fix the existing feasibility check endpoint [projects.py](file:///c:/Users/Edwar/Documents/dev/BambuDash/backend/app/api/v1/endpoints/projects.py#L32).
- The feasibility check must verify if there is enough total available filament weight (`remaining_weight_g`) in the inventory (spools with status `AVAILABLE` or `IN_USE` at the target location) for *every* filament requirement (material and color hex) specified in `ProjectFilamentRequirement`.
- Feasibility check accepts a `location` parameter. If a project is assigned to a printer, the printer's location is used; otherwise, it uses the globally selected location.

### 2. Dashboard Overview — Mock-Daten-Kennzeichnung
- Bestehende Mock-Daten (Printer-Telemetrie, Activity-Feed) bleiben vorerst, müssen aber klar als `[TESTDATEN]` gekennzeichnet werden (siehe 0b).
- Quick-Action-Buttons ("Enrich Draft Spool", "New Print Project") müssen auf die jeweiligen Zielseiten verlinken (`/dashboard/inventory`, `/dashboard/projects`).
- KPI-Karten, die bereits echte API-Daten nutzen (Filament Count, Project Count), bekommen KEINE Kennzeichnung.

### 3. Frontend: Filament Inventory View (`/dashboard/inventory`)
- **Spool List:** Display all spools in a clean, modern grid or table, groupable and filterable by status (`DRAFT`, `AVAILABLE`, `IN_USE`, `SPENT`) and `location` (`Zwickau`, `Plauen`, `Standby`).
- **Enrichment Modal:**
  - When clicking an MQTT-discovered `DRAFT` spool, open a modal.
  - The modal must call a backend endpoint to find matching unlinked delivered spools (same material, similar color) from recent orders.
  - Suggest these unlinked spools to the user. If selected, automatically link the physical spool (updates status to `AVAILABLE`, links `owner_id` and `price`).
  - Otherwise, let the user manually select an owner (Lukas, Max, Admin, or Communal) and input the price.
- **Non-RFID Slot Assignment:**
  - Provide a UI option to manually assign an existing spool to a printer's AMS slot.
  - This updates the spool's `bambu_tray_id` to match the slot's fallback ID.
  - If a spool is removed from the AMS (detected via MQTT or manual removal), set its `bambu_tray_id` to null (moves it to standby).

### 4. Frontend: Project Kanban Board & MakerWorld Visual Integration (`/dashboard/projects`)
- **Kanban Board:** Columns for `Idea`, `Planned`, `Printing`, `Completed`, and `Archived`.
- **MakerWorld Search Dialog:**
  - Search bar in the "New Project" modal that queries `/api/v1/makerworld/search`.
  - Displays search results (model title, preview thumbnail, designer).
  - Clicking a model creates a project, auto-populating title, URL, and preview image.
- **Consumption Form:** Immediately after selecting a model, prompt the user to input the required filaments (estimated weight in grams, material type, color hex).
- **Feasibility Badges:**
  - Each card must display small badges for required filaments (e.g. `PLA Black [50g]` in **Green** if available, **Red** if missing).
  - An overall project indicator (icon or border color) shows if the project is printable (all requirements met).
- **Global Location Selector:** A dropdown in the main dashboard header ('Zwickau', 'Plauen', 'Alle') that triggers recalculation of project feasibility based on that location's inventory.

### 5. Frontend: Order Management & Store-Assisted Cart (`/dashboard/orders`)
- **Order List:** Display current and historical orders with statuses (`PLANNING`, `ORDERED`, `DELIVERED`).
- **Store-Assisted Add:**
  - When adding items to the active cart, let the user search for a product slug (or paste a Bambu Lab Store URL).
  - Query `/api/v1/store/lookup/{product_slug}` to fetch variants and prices.
  - Auto-populate variants (e.g., PLA Basic Black, price, SKU) in the form.
  - The user then sets quantity and configures user split percentages.

### 6. Frontend: Settings Page (`/dashboard/settings`)

Die Settings-Seite ist in Sektionen aufgeteilt:

#### 6a. Sprachumschalter (i18n)
- Dropdown oder segmented control: `Deutsch` / `English`.
- Setzt Cookie `NEXT_LOCALE`, triggert Page-Reload.
- Detailliert spec'd in [arch_spec_i18n.md](file:///c:/Users/Edwar/Documents/dev/BambuDash/docs/arch_spec_i18n.md).

#### 6b. User-Profil
- Formular zum Ändern von: Name, E-Mail-Adresse, Passwort.
- Passwort-Änderung erfordert Eingabe des alten Passworts.
- Backend-Endpoints:
  - `PATCH /api/v1/users/me` — ⚠️ *existiert noch nicht, muss erstellt werden.*

#### 6c. Drucker-Verwaltung
- Liste aller registrierten Drucker mit Name, Modell, Standort, MQTT-Status.
- Drucker hinzufügen: Name, Modell, IP/Hostname, Serial, Access-Code, Standort zuweisen.
- Drucker bearbeiten: Standort ändern, Verbindungsdaten aktualisieren.
- Drucker entfernen: Mit Bestätigungsdialog.
- Backend-Endpoints:
  - `GET /api/v1/printers/` — ⚠️ *prüfen ob existiert.*
  - `POST /api/v1/printers/` — ⚠️ *prüfen ob existiert.*
  - `PATCH /api/v1/printers/{id}` — ⚠️ *prüfen ob existiert.*
  - `DELETE /api/v1/printers/{id}` — ⚠️ *prüfen ob existiert.*

#### 6d. Standort-Verwaltung
- **Entscheidung:** Standort bleibt ein einfacher String (kein eigenes DB-Modell).
- Die Settings-Seite zeigt die aktuell verwendeten Standorte (aggregiert aus `Printer.location` und `FilamentSpool.location`) als Tag-Liste.
- Neue Standorte werden implizit erstellt, wenn ein Drucker oder eine Spool einem neuen Standort-String zugewiesen wird.
- Umbenennen eines Standorts: Bulk-Update aller Printer/Spools mit dem alten Standort-String auf den neuen.
- Kein separater Backend-Endpoint nötig — die bestehenden PATCH-Endpoints für Printer und Filaments reichen.
- Ein `GET /api/v1/locations/` Convenience-Endpoint liefert die aggregierte Liste distincter Standort-Strings. ⚠️ *Muss erstellt werden.*

#### 6e. Benutzermanagement & Berechtigungs-Matrix (Admin)
- Nur für Benutzer mit `admin`-Rolle sichtbar.

**Rollen-System (Backend):**
- Neues DB-Modell `Role`:
  ```
  Role:
    id: int (PK)
    name: str (unique, z.B. "admin", "user", "viewer")
    description: str
    permissions: JSON  # Liste von Permission-Strings
    is_system: bool    # True für Default-Rollen (nicht löschbar)
  ```
- `User`-Modell bekommt ein `role_id: FK → Role`.
- Drei **Default-Rollen** (is_system=True, nicht löschbar):

| Rolle | Beschreibung | Default-Permissions |
|-------|-------------|-------------------|
| `admin` | Voller Zugriff | Alle Permissions |
| `user` | Standard-Nutzer | Alles außer Benutzerverwaltung & Rollenverwaltung |
| `viewer` | Nur Lesezugriff | Nur `*.read`-Permissions |

**Permission-Katalog:**

| Permission | Beschreibung |
|-----------|-------------|
| `filaments.read` | Filament-Inventar anzeigen |
| `filaments.write` | Spulen erstellen, anreichern, bearbeiten |
| `filaments.delete` | Spulen löschen |
| `projects.read` | Projekte anzeigen |
| `projects.write` | Projekte erstellen/bearbeiten |
| `projects.delete` | Projekte löschen/archivieren |
| `orders.read` | Bestellungen anzeigen |
| `orders.write` | Warenkorb/Bestellungen verwalten |
| `orders.delete` | Bestellungen löschen |
| `printers.read` | Drucker anzeigen |
| `printers.write` | Drucker hinzufügen/bearbeiten |
| `printers.delete` | Drucker entfernen |
| `users.read` | Benutzerliste anzeigen |
| `users.write` | Benutzer anlegen/bearbeiten |
| `users.delete` | Benutzer löschen/deaktivieren |
| `roles.read` | Rollen anzeigen |
| `roles.write` | Rollen erstellen/bearbeiten, Permissions zuweisen |
| `settings.write` | Globale Einstellungen ändern (Standorte etc.) |

**UI: Berechtigungs-Matrix (Settings → Benutzermanagement):**
- Tabellen-Darstellung:
  - **Zeilen** = Rollen (admin, user, viewer, ggf. custom)
  - **Spalten** = Permissions (gruppiert nach Feature: Filaments, Projects, Orders, etc.)
  - **Zellen** = Checkboxen (aktiv/inaktiv)
- Admin kann:
  - Bestehende Rollen bearbeiten (Permissions umschalten via Checkbox-Matrix).
  - Neue Custom-Rollen erstellen (z.B. "Besteller" — nur Orders-Rechte).
  - System-Rollen (admin, user, viewer) können nicht gelöscht werden, aber ihre Permissions können angepasst werden.
  - ⚠️ Die `admin`-Rolle kann sich selbst nicht die `roles.write`-Permission entziehen (Deadlock-Schutz).

**Benutzer-Verwaltung (Settings → Benutzermanagement):**
- Liste aller Benutzer mit Name, E-Mail, Username, zugewiesene Rolle.
- Benutzer anlegen: Name, E-Mail, Username, Passwort, Rolle zuweisen.
- Benutzer bearbeiten: Rolle ändern, Passwort zurücksetzen.
- Benutzer deaktivieren/löschen: Mit Bestätigungsdialog, Prüfung ob Bestellungen/Spulen zugewiesen. Deaktivierte User können sich nicht einloggen.

**Backend-Endpoints:**
- `GET /api/v1/users/` — ✅ *existiert.*
- `POST /api/v1/users/` — ✅ *existiert (Registration).*
- `PATCH /api/v1/users/{id}` — ⚠️ *muss erstellt werden.*
- `DELETE /api/v1/users/{id}` — ⚠️ *muss erstellt werden (Soft-Delete/Deaktivierung).*
- `GET /api/v1/roles/` — ⚠️ *muss erstellt werden.*
- `POST /api/v1/roles/` — ⚠️ *muss erstellt werden.*
- `PATCH /api/v1/roles/{id}` — ⚠️ *muss erstellt werden.*
- `DELETE /api/v1/roles/{id}` — ⚠️ *muss erstellt werden (nur non-system Rollen).*
- `GET /api/v1/permissions/` — ⚠️ *muss erstellt werden (liefert den Permission-Katalog für die Matrix-UI).*
- Alle schreibenden User/Role-Endpoints müssen mit `roles.write`-Permission geschützt sein.
- Die `get_current_user`-Dependency muss erweitert werden, um Permissions zu prüfen (z.B. `Depends(require_permission("users.write"))`).
