# Filename: scripts/generate_keywords_from_dictionary.py
# The definitive keyword generator. It reads the ground-truth dictionaries
# from the factored DSV file to create the master keyword list.
# This approach is comprehensive, fast, and leverages existing work.

import os
import json
import re

# --- CONFIGURATION ---
# Path to the Rosetta Stone
FACTORED_DSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'darpa', 'DARPA_Semantic_Vectors_factored.dsv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "ai_generated_keywords.json")

# Keywords to exclude (generic terms, formatting artifacts, etc.)
EXCLUSION_LIST = {
    'UNCLASSIFIED', 'UNCLASSIFIEDUNCLASSIFIED', '[TEXT CHUNK TO ANALYZE END]',
    'Accomplishments', 'Plans', 'Not Applicable', 'Project', 'Program', 'System',
    'Technology', 'Systems', 'Research', 'Development', 'PE', 'FY', 'The', 'This',
    'A', 'An', 'And', 'Of', 'For', 'With', 'In', 'On', 'As', 'By'
}

def main():
    """
    Parses the DICTIONARIES section of the DSV file to generate the master keyword list.
    """
    print("="*60)
    print("=  CHORUS DICTIONARY SPARK GENERATION (GROUND TRUTH)  =")
    print("="*60)

    if not os.path.exists(FACTORED_DSV_PATH):
        print(f"[!] FATAL: Factored DSV file not found at '{FACTORED_DSV_PATH}'")
        print("    Please run the full DARPA ingestion pipeline first.")
        return

    print(f"[*] Reading dictionaries from: {FACTORED_DSV_PATH}")

    actions = []
    objects = []
    attributes = []

    in_dictionaries_section = False
    with open(FACTORED_DSV_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line == "[DICTIONARIES]":
                in_dictionaries_section = True
                continue
            if line.startswith('['):
                in_dictionaries_section = False
                continue
            
            if in_dictionaries_section:
                try:
                    # Format is TYPE:INDEX:TERM
                    parts = line.split(':', 2)
                    if len(parts) == 3:
                        type_char, _, term = parts
                        # Clean the term: remove extra spaces and filter
                        term = term.strip()
                        if term and term not in EXCLUSION_LIST and len(term) > 2:
                            if type_char == 'A':
                                actions.append(term)
                            elif type_char == 'O':
                                objects.append(term)
                            elif type_char == 'T':
                                attributes.append(term)
                except ValueError:
                    continue # Skip malformed lines

    print(f"[*] Found {len(actions)} Actions, {len(objects)} Objects, and {len(attributes)} Attributes.")

    # For the scrapers, we are primarily interested in the "things" and "concepts".
    # Objects and Attributes are the most valuable keywords.
    combined_keywords = objects + attributes
    
    # Deduplicate and sort the final list
    unique_keywords = sorted(list(set(combined_keywords)))

    # We can also create a specific list of organizations from the Objects list
    # This is a simple heuristic, but effective.
    organizations = sorted(list(set([
        term for term in objects 
        if any(sub in term for sub in ['University', 'Institute', 'Center', 'Agency', 'Command'])
        or re.match(r'^[A-Z][a-z]+(\s[A-Z][a-z]+)*(\sInc\.|\sLLC)?$', term) # Proper nouns
    ])))

    final_output = {
        "keywords": unique_keywords,
        "involved_organizations": organizations
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(final_output, f, indent=2)

    print("\n" + "="*60)
    print("✅ SUCCESS: Ground truth keyword generation complete.")
    print(f"   Total unique keywords generated: {len(unique_keywords)}")
    print(f"   Identified potential organizations: {len(organizations)}")
    print(f"   Master keyword file saved to: {OUTPUT_PATH}")
    print("="*60)

if __name__ == "__main__":
    main()
