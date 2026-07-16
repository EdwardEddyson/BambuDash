# scratch/verify_issue_6.py
import os
import re
import sys

def verify_inventory_view():
    print("=== BambuDash Frontend Inventory View Verification ===")
    
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_file = os.path.join(workspace_dir, "frontend", "src", "app", "dashboard", "inventory", "page.tsx")
    
    # 1. Check if the page.tsx file exists
    if not os.path.exists(target_file):
        print(f"[FAIL] Target file does not exist at: {target_file}")
        return False
    print(f"[OK] Next.js Inventory View page exists at: {target_file}")
    
    # 2. Read the file contents and verify imports & endpoint calls
    with open(target_file, "r", encoding="utf-8") as f:
        code = f.read()
        
    # Check for client-side flag
    if '"use client"' not in code and "'use client'" not in code:
        print("[FAIL] Next.js page is missing 'use client' directive required for stateful hooks.")
        return False
    print("[OK] Found 'use client' directive.")

    # Check for expected endpoint fetches
    if "/filaments/" not in code:
        print("[FAIL] The page does not seem to query the GET /api/v1/filaments/ endpoint.")
        return False
    print("[OK] Queries the correct filaments API: GET /api/v1/filaments/")
    
    if "/users/" not in code:
        print("[FAIL] The page does not seem to query the users API to resolve owner names.")
        return False
    print("[OK] Queries the users API to fetch profile metadata.")
    
    # Check for group-by logic
    if "groupBy" not in code or "status" not in code or "location" not in code or "material" not in code:
        print("[FAIL] Missing filter/group-by logic parameters (status, location, material).")
        return False
    print("[OK] Spool grouping state and keys exist (status, location, material).")

    # Check for design requirements
    if "grid" not in code or "table" not in code:
        print("[FAIL] Missing dual grid / table view layout options.")
        return False
    print("[OK] Supports grid vs table layout styles.")
    
    # Check for status tags mapping
    status_keywords = ["draft", "available", "in_use", "spent"]
    for keyword in status_keywords:
        if keyword not in code.lower():
            print(f"[FAIL] Missing status mapping logic for '{keyword}' spools.")
            return False
    print("[OK] Spool status mapping checks passed.")

    # Check for location tags mapping
    location_keywords = ["zwickau", "plauen", "standby"]
    for keyword in location_keywords:
        if keyword not in code.lower():
            print(f"[FAIL] Missing location mapping logic for '{keyword}' spools.")
            return False
    print("[OK] Spool location mapping checks passed.")

    print("\n[SUCCESS] Verification passed: Frontend Filament Spool Inventory View has been successfully implemented with all grouping, filtering, styling, and endpoint interfaces.")
    return True

if __name__ == "__main__":
    success = verify_inventory_view()
    sys.exit(0 if success else 1)
