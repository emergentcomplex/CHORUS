# Filename: tools/forge/reorganize_missions.py
# 🔱 The CHORUS Mission Reorganization Protocol (Python Edition)
# This script safely and deterministically reorganizes the docs/missions directory.

import os
import shutil
from pathlib import Path

def main():
    """
    Executes the full mission reorganization protocol.
    """
    # Ensure we are running from the project root
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    missions_dir = Path("docs/missions")
    archive_dir = missions_dir / "archive"

    if not missions_dir.is_dir() or not archive_dir.is_dir():
        print(f"❌ ERROR: Could not find {missions_dir} or {archive_dir}. Run from project root.")
        return

    print("[*] Beginning mission reorganization protocol...")

    # --- Step 1: Archive all obsolete and superseded mission files ---
    obsolete_files = [
        "03_phase_ui_and_dialectic.md",
        "04_phase_dynamic_learning.md",
        "05_phase_governance_and_observatory.md",
        "01_mandate_of_the_timeless_oracle.md",
        "11_mandate_of_temporal_cognition.md",
        "01_mandate_of_the_bge_oracle.md",
    ]

    print("[*] Archiving obsolete missions...")
    for filename in obsolete_files:
        source_path = missions_dir / filename
        dest_path = archive_dir / filename
        if source_path.exists():
            shutil.move(source_path, dest_path)
            print(f"  -> Archived {filename}")
        else:
            print(f"  -> Skipping {filename} (already archived or does not exist)")
    print("[+] Obsolete files have been archived.")

    # --- Step 2: Rename and re-number the active missions into the canonical order ---
    # The list is a tuple of (old_name, new_name)
    renaming_map = [
        ("00_mandate_of_gnosis.md", "00_mandate_of_the_forge.md"),
        # Phase 2 - no changes, but listed for completeness
        ("01_mandate_of_first_light.md", "01_mandate_of_first_light.md"),
        ("02_mandate_of_synthesis.md", "02_mandate_of_synthesis.md"),
        ("03_mandate_of_judgment.md", "03_mandate_of_judgment.md"),
        # Phase 3
        ("07_mandate_of_the_dialectic_chamber.md", "04_mandate_of_the_dialectic_chamber.md"),
        ("08_mandate_of_the_red_team.md", "05_mandate_of_the_red_team.md"),
        # Phase 4
        ("00_mandate_of_the_living_architecture.md", "06_mandate_of_the_living_architecture.md"),
        ("06_mandate_of_recursive_cognition.md", "07_mandate_of_recursive_cognition.md"),
        # Phase 5
        ("09_mandate_of_the_world_model.md", "08_mandate_of_the_world_model.md"),
        ("10_mandate_of_cognitive_governance.md", "09_mandate_of_cognitive_governance.md"),
        ("12_mandate_of_the_cognitive_synapse.md", "10_mandate_of_the_cognitive_synapse.md"),
        # Phase 6
        ("02_mandate_of_the_knowledge_graph.md", "11_mandate_of_the_knowledge_graph.md"),
    ]

    print("[*] Re-numbering active missions...")
    for old_name, new_name in renaming_map:
        if old_name == new_name:
            continue
        source_path = missions_dir / old_name
        dest_path = missions_dir / new_name
        if source_path.exists():
            os.rename(source_path, dest_path)
            print(f"  -> Renamed {old_name} to {new_name}")
        else:
            print(f"  -> Skipping {old_name} (already renamed or does not exist)")
    print("[+] Active missions have been re-numbered.")

    # --- Step 3: Final Verification ---
    print("\n[*] Verifying final state...")
    os.system("tree docs/missions")

    print("\n✅ SUCCESS: Mission reorganization is complete.")

if __name__ == "__main__":
    main()