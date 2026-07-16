# Architectural Specification — Phase 4: Frontend Development & Live-Check Fixes

This specification describes the requirements for Phase 4 frontend development and location-aware live feasibility check integration for **BambuDash**.

---

## 🏗️ Requirements

### 1. Location-Aware Live Feasibility Check (Backend Fix)
- Fix the existing feasibility check endpoint [projects.py](file:///c:/Users/Edwar/Documents/dev/BambuDash/backend/app/api/v1/endpoints/projects.py#L32).
- The feasibility check must verify if there is enough total available filament weight (`remaining_weight_g`) in the inventory (spools with status `AVAILABLE` or `IN_USE` at the target location) for *every* filament requirement (material and color hex) specified in `ProjectFilamentRequirement`.
- Feasibility check accepts a `location` parameter. If a project is assigned to a printer, the printer's location is used; otherwise, it uses the globally selected location.

### 2. Frontend: Filament Inventory View
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

### 3. Frontend: Project Kanban Board & MakerWorld Visual Integration
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

### 4. Frontend: Order Management & Store-Assisted Cart
- **Order List:** Display current and historical orders with statuses (`PLANNING`, `ORDERED`, `DELIVERED`).
- **Store-Assisted Add:**
  - When adding items to the active cart, let the user search for a product slug (or paste a Bambu Lab Store URL).
  - Query `/api/v1/store/lookup/{product_slug}` to fetch variants and prices.
  - Auto-populate variants (e.g., PLA Basic Black, price, SKU) in the form.
  - The user then sets quantity and configures user split percentages.
