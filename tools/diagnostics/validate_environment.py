# Filename: tools/diagnostics/validate_environment.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This script is the "Constitutional Guardian." It validates the project's
# health and integrity by statically analyzing all Python files to ensure
# all internal imports are valid and resolve to real modules.

import ast
import os
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# --- Helper Functions ---

def get_git_file_list() -> set[str]:
    """Gets the ground-truth list of all files tracked by git."""
    try:
        output = subprocess.check_output(['git', 'ls-files'], cwd=PROJECT_ROOT, text=True)
        return {str(Path(p)) for p in output.strip().split('\n')}
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("[!] FATAL: Could not execute `git ls-files`. Is `git` installed in the container?", file=sys.stderr)
        print(f"    Underlying error: {e}", file=sys.stderr)
        sys.exit(1)

def validate_imports() -> list[str]:
    """
    Statically analyzes all Python files for invalid internal imports.
    """
    errors = []
    python_files = [p for p in get_git_file_list() if p.endswith('.py')]
    
    known_modules = set()
    for file_path_str in python_files:
        file_path = Path(file_path_str)
        module_path_str = str(file_path.with_suffix('')).replace(os.sep, '.')
        known_modules.add(module_path_str)
        # Add parent packages as well
        for parent in file_path.parents:
            if parent == PROJECT_ROOT or parent == Path('.'):
                break
            init_file = parent / "__init__.py"
            if init_file.exists():
                parent_module_str = str(parent).replace(os.sep, '.')
                known_modules.add(parent_module_str)

    for file_str in python_files:
        file_path = Path(file_str)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                module_to_check = None
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        module_to_check = alias.name
                elif isinstance(node, ast.ImportFrom) and node.module is not None:
                    if node.level > 0:
                        # Resolve relative imports
                        base_path = file_path.parent
                        for _ in range(node.level - 1):
                            base_path = base_path.parent
                        # Reconstruct the absolute module path from the relative path
                        abs_module_path = str(base_path / node.module.replace('.', os.sep)).replace(os.sep, '.')
                        module_to_check = abs_module_path
                    else:
                        module_to_check = node.module

                if module_to_check and module_to_check.startswith('chorus_engine'):
                    if module_to_check not in known_modules:
                        errors.append(f"Broken Import in '{file_str}' (line {node.lineno}): Cannot resolve module '{module_to_check}'")

        except (SyntaxError, UnicodeDecodeError) as e:
            errors.append(f"Cannot parse '{file_str}': {e}")
        except Exception as e:
            errors.append(f"Unexpected error processing '{file_str}': {e}")

    return errors

# --- Main Execution ---

def main():
    """Runs all validation checks and reports the results."""
    print("--- 🔱 CHORUS System Health & Integrity Validation Suite ---")
    all_errors = []

    print("\n[*] Statically analyzing Python imports for correctness...")
    import_errors = validate_imports()
    if not import_errors:
        print("  - ✅ OK: All internal imports are valid.")
    else:
        all_errors.extend(import_errors)

    print("\n" + "="*60)
    if not all_errors:
        print("✅ SUCCESS: System validation passed. Architecture is sound.")
        print("="*60)
        sys.exit(0)
    else:
        print(f"❌ FAILURE: System validation failed with {len(all_errors)} error(s).")
        print("="*60)
        for error in all_errors:
            print(f"  - {error}")
        sys.exit(1)

if __name__ == "__main__":
    main()