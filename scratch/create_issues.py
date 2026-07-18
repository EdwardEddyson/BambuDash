import subprocess
import json

issues = [
    {
        "title": "Backend: Location-Aware Live Feasibility Check",
        "body": "### Beschreibung\nFix the existing feasibility check endpoint `projects.py`.\n\n### Akzeptanzkriterien\n- [ ] Verify if there is enough total available filament weight (`remaining_weight_g`) in the inventory (spools with status `AVAILABLE` or `IN_USE` at the target location) for every filament requirement.\n- [ ] Feasibility check accepts a `location` parameter.\n- [ ] If a project is assigned to a printer, the printer's location is used; otherwise, it uses the globally selected location.",
        "labels": "prio:high,skill:backend,effort:S,status:ready,epic:phase4-frontend"
    },
    {
        "title": "Frontend: Filament Inventory View - Spool List & Filter",
        "body": "### Beschreibung\nCreate the spool list UI.\n\n### Akzeptanzkriterien\n- [ ] Display all spools in a clean, modern grid or table.\n- [ ] Groupable and filterable by status (`DRAFT`, `AVAILABLE`, `IN_USE`, `SPENT`).\n- [ ] Groupable and filterable by location (`Zwickau`, `Plauen`, `Standby`).",
        "labels": "prio:medium,skill:frontend,effort:M,status:ready,epic:phase4-frontend"
    },
    {
        "title": "Frontend: Filament Inventory View - Enrichment Modal",
        "body": "### Beschreibung\nModal for enriching newly discovered DRAFT spools.\n\n### Akzeptanzkriterien\n- [ ] Clicking an MQTT-discovered `DRAFT` spool opens a modal.\n- [ ] Call backend endpoint to find matching unlinked delivered spools (same material, similar color) from recent orders.\n- [ ] Suggest unlinked spools to user; if selected, auto-link physical spool (updates status to `AVAILABLE`, links `owner_id` and `price`).\n- [ ] Allow user to manually select an owner and input price if no link is chosen.",
        "labels": "prio:high,skill:frontend,effort:M,status:ready,epic:phase4-frontend"
    },
    {
        "title": "Frontend: Filament Inventory View - Non-RFID Slot Assignment",
        "body": "### Beschreibung\nUI for manual assignment of non-RFID spools.\n\n### Akzeptanzkriterien\n- [ ] Provide UI option to manually assign an existing spool to a printer's AMS slot.\n- [ ] Updates the spool's `bambu_tray_id` to match the slot's fallback ID.\n- [ ] If a spool is removed from the AMS, set its `bambu_tray_id` to null.",
        "labels": "prio:medium,skill:frontend,effort:M,status:ready,epic:phase4-frontend"
    },
    {
        "title": "Frontend: Project Kanban Board UI & Location Selector",
        "body": "### Beschreibung\nCreate the Kanban board for projects and a global location selector.\n\n### Akzeptanzkriterien\n- [ ] Kanban Board with columns: `Idea`, `Planned`, `Printing`, `Completed`, and `Archived`.\n- [ ] Global location selector in dashboard header ('Zwickau', 'Plauen', 'Alle') that triggers recalculation of project feasibility.",
        "labels": "prio:high,skill:frontend,effort:M,status:ready,epic:phase4-frontend"
    },
    {
        "title": "Frontend: Project Management - MakerWorld Search & Consumption Form",
        "body": "### Beschreibung\nIntegration of MakerWorld search and filament consumption inputs.\n\n### Akzeptanzkriterien\n- [ ] Search bar in the 'New Project' modal querying `/api/v1/makerworld/search`.\n- [ ] Displays search results (model title, preview thumbnail, designer).\n- [ ] Clicking a model creates a project, auto-populating title, URL, and preview image.\n- [ ] Prompt user to input required filaments (estimated weight, material type, color hex) immediately after selecting a model.",
        "labels": "prio:medium,skill:frontend,effort:M,status:ready,epic:phase4-frontend"
    },
    {
        "title": "Frontend: Order Management & Store-Assisted Cart",
        "body": "### Beschreibung\nOrder list and store integration for creating new orders.\n\n### Akzeptanzkriterien\n- [ ] Display current and historical orders with statuses (`PLANNING`, `ORDERED`, `DELIVERED`).\n- [ ] When adding items to active cart, let user search for product slug or URL.\n- [ ] Query `/api/v1/store/lookup/{product_slug}` to fetch variants and prices.\n- [ ] Auto-populate variants in form. Let user set quantity and user split percentages.",
        "labels": "prio:medium,skill:frontend,effort:L,status:ready,epic:phase4-frontend"
    }
]

# We need an extra task that depends on Task 1
dependent_task = {
    "title": "Frontend: Project Kanban Board - Feasibility Badges",
    "body": "Depends on #{dep_id}\n\n### Beschreibung\nDisplay feasibility badges on Kanban cards.\n\n### Akzeptanzkriterien\n- [ ] Each card must display small badges for required filaments (e.g. PLA Black [50g] in Green if available, Red if missing).\n- [ ] Overall project indicator (icon or border color) shows if project is printable.",
    "labels": "prio:high,skill:frontend,effort:S,status:blocked,epic:phase4-frontend"
}

created_issues = []

for issue in issues:
    cmd = [
        "gh", "issue", "create",
        "--title", issue["title"],
        "--body", issue["body"],
        "--label", issue["labels"]
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    # Output is the issue URL, e.g., https://github.com/user/repo/issues/123
    url = result.stdout.strip()
    issue_number = url.split("/")[-1]
    created_issues.append({"title": issue["title"], "number": issue_number, "url": url})
    print(f"Created: {url}")

# Create dependent task
dep_id = created_issues[0]["number"]  # Task 1 is Backend Feasibility Check
dependent_task["body"] = dependent_task["body"].format(dep_id=dep_id)

cmd = [
    "gh", "issue", "create",
    "--title", dependent_task["title"],
    "--body", dependent_task["body"],
    "--label", dependent_task["labels"]
]
result = subprocess.run(cmd, capture_output=True, text=True, check=True)
url = result.stdout.strip()
issue_number = url.split("/")[-1]
created_issues.append({"title": dependent_task["title"], "number": issue_number, "url": url})
print(f"Created: {url}")

# Generate report
report_content = "# Phase 4 Frontend & Live-Check Issues Report\n\n"
report_content += "| Issue ID | Title | Labels |\n"
report_content += "|---|---|---|\n"

for i, issue in enumerate(issues):
    report_content += f"| #{created_issues[i]['number']} | [{issue['title']}]({created_issues[i]['url']}) | `{issue['labels']}` |\n"

report_content += f"| #{created_issues[-1]['number']} | [{dependent_task['title']}]({created_issues[-1]['url']}) | `{dependent_task['labels']}` |\n"

with open("docs/phase4_issues_report.md", "w") as f:
    f.write(report_content)

print("\nReport written to docs/phase4_issues_report.md")
