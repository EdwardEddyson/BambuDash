# 🚀 GitHub Issues Report — Phase 4: Frontend Development & Live-Check Fixes

All requirements specified in [arch_spec.md](file:///c:/Users/Edwar/Documents/dev/BambuDash/docs/arch_spec.md) have been analyzed and decomposed into 18 discrete GitHub Issues. These issues have been successfully created using the `gh` CLI with 4-level tagging (priority, skill, effort, status) under the `epic:phase4-frontend` epic.

## 📋 Created Issues Summary

| Key | Issue | Title | Skill | Priority | Effort | Status | Dependencies |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1.1** | [#3](https://github.com/EdwardEddyson/BambuDash/issues/3) | Database: Add printer association to PrintProject | `skill:database` | `prio:high` | `effort:S` | `status:ready` | - |
| **1.2** | [#4](https://github.com/EdwardEddyson/BambuDash/issues/4) | Backend: Implement location-aware filament aggregation and check logic | `skill:backend` | `prio:high` | `effort:M` | `status:blocked` | [#3](https://github.com/EdwardEddyson/BambuDash/issues/3) |
| **1.3** | [#5](https://github.com/EdwardEddyson/BambuDash/issues/5) | Backend: Update project feasibility check endpoint for location context | `skill:backend` | `prio:high` | `effort:S` | `status:blocked` | [#4](https://github.com/EdwardEddyson/BambuDash/issues/4) |
| **2.1** | [#6](https://github.com/EdwardEddyson/BambuDash/issues/6) | Frontend: Filament Inventory Spool List View | `skill:frontend` | `prio:high` | `effort:M` | `status:ready` | - |
| **2.2** | [#7](https://github.com/EdwardEddyson/BambuDash/issues/7) | Backend: API endpoint for finding matching unlinked delivered spools | `skill:backend` | `prio:high` | `effort:S` | `status:ready` | - |
| **2.3** | [#8](https://github.com/EdwardEddyson/BambuDash/issues/8) | Backend: Update filament enrichment endpoint to support spool merging | `skill:backend` | `prio:high` | `effort:S` | `status:blocked` | [#7](https://github.com/EdwardEddyson/BambuDash/issues/7) |
| **2.4** | [#9](https://github.com/EdwardEddyson/BambuDash/issues/9) | Frontend: Filament Enrichment Modal with order-matching suggestions | `skill:frontend` | `prio:high` | `effort:M` | `status:blocked` | [#6](https://github.com/EdwardEddyson/BambuDash/issues/6), [#8](https://github.com/EdwardEddyson/BambuDash/issues/8) |
| **2.5** | [#10](https://github.com/EdwardEddyson/BambuDash/issues/10) | Backend: Create API endpoints for manual AMS slot assignment and removal | `skill:backend` | `prio:medium` | `effort:S` | `status:ready` | - |
| **2.6** | [#11](https://github.com/EdwardEddyson/BambuDash/issues/11) | Frontend: Manual AMS slot assignment component | `skill:frontend` | `prio:medium` | `effort:M` | `status:blocked` | [#10](https://github.com/EdwardEddyson/BambuDash/issues/10), [#6](https://github.com/EdwardEddyson/BambuDash/issues/6) |
| **2.7** | [#12](https://github.com/EdwardEddyson/BambuDash/issues/12) | Backend: Handle AMS spool removal in MQTT parsing logic | `skill:mqtt-realtime` | `prio:medium` | `effort:S` | `status:ready` | - |
| **3.1** | [#13](https://github.com/EdwardEddyson/BambuDash/issues/13) | Frontend: Project Kanban Board View | `skill:frontend` | `prio:high` | `effort:L` | `status:ready` | - |
| **3.2** | [#14](https://github.com/EdwardEddyson/BambuDash/issues/14) | Frontend: MakerWorld Search Dialog in New Project Modal | `skill:frontend` | `prio:medium` | `effort:M` | `status:blocked` | [#13](https://github.com/EdwardEddyson/BambuDash/issues/13) |
| **3.3** | [#15](https://github.com/EdwardEddyson/BambuDash/issues/15) | Frontend: Project Filament Consumption Input Form | `skill:frontend` | `prio:high` | `effort:M` | `status:blocked` | [#13](https://github.com/EdwardEddyson/BambuDash/issues/13) |
| **3.4** | [#16](https://github.com/EdwardEddyson/BambuDash/issues/16) | Backend: API endpoints for managing project filament requirements | `skill:backend` | `prio:high` | `effort:S` | `status:ready` | - |
| **3.5** | [#17](https://github.com/EdwardEddyson/BambuDash/issues/17) | Frontend: Global Location Selector & Project Feasibility Badges | `skill:frontend` | `prio:high` | `effort:M` | `status:blocked` | [#5](https://github.com/EdwardEddyson/BambuDash/issues/5), [#13](https://github.com/EdwardEddyson/BambuDash/issues/13), [#15](https://github.com/EdwardEddyson/BambuDash/issues/15) |
| **4.1** | [#18](https://github.com/EdwardEddyson/BambuDash/issues/18) | Frontend: Order List and Management View | `skill:frontend` | `prio:medium` | `effort:M` | `status:ready` | - |
| **4.2** | [#19](https://github.com/EdwardEddyson/BambuDash/issues/19) | Frontend: Store-Assisted Add-to-Cart dialog | `skill:frontend` | `prio:medium` | `effort:M` | `status:ready` | - |
| **4.3** | [#20](https://github.com/EdwardEddyson/BambuDash/issues/20) | Frontend: Split Billing UI inside Shopping Cart | `skill:frontend` | `prio:medium` | `effort:S` | `status:blocked` | [#19](https://github.com/EdwardEddyson/BambuDash/issues/19) |

## 🔗 Dependency Trees & Flow

```mermaid
graph TD
    %% Section 1: Location-Aware Feasibility Check
    subgraph Location-Aware Feasibility Check (Backend Fix)
        I11[#3 DB: Add printer association] --> I12[#4 Backend: Location-aware weight aggregation]
        I12 --> I13[#5 Backend: Update project feasibility endpoint]
    end

    %% Section 2: Filament Inventory View
    subgraph Filament Inventory View
        I21[#6 FE: Filament Inventory Spool List View]
        I22[#7 Backend: Find matching unlinked delivered spools] --> I23[#8 Backend: Support spool merging in enrich]
        I21 --> I24[#9 FE: Filament Enrichment Modal with suggestions]
        I23 --> I24

        I25[#10 Backend: Manual AMS slot assignment/removal] --> I26[#11 FE: Manual AMS slot assignment component]
        I21 --> I26

        I27[#12 Backend: Handle AMS spool removal in MQTT]
    end

    %% Section 3: Project Kanban & MakerWorld
    subgraph Project Kanban Board & MakerWorld Visual Integration
        I31[#13 FE: Project Kanban Board View] --> I32[#14 FE: MakerWorld Search Dialog]
        I31 --> I33[#15 FE: Project Filament Consumption Input Form]
        I34[#16 Backend: API endpoints for project requirements]

        I13 --> I35[#17 FE: Global Location Selector & Feasibility Badges]
        I31 --> I35
        I33 --> I35
    end

    %% Section 4: Order Management
    subgraph Order Management & Store Cart
        I41[#18 FE: Order List and Management View]
        I42[#19 FE: Store-Assisted Add-to-Cart dialog] --> I43[#20 FE: Split Billing UI in Cart]
    end
```
