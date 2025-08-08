# Filename: tools/testing/validate_constitution.py
#
# 🔱 CHORUS Office of the Constitutional Guardian
# This script is the master validator for all programmatic axioms.

import ast
import os
import sys
from collections import defaultdict
from pathlib import Path

# --- CONFIGURATION ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "chorus_engine"
DOCKERFILE_PATH = PROJECT_ROOT / "Dockerfile"
HARVESTER_DIR = SOURCE_DIR / "adapters" / "harvesters"

# --- Axiom 8: The Architect (Dependency Rule) ---
LAYERS = {"core": 0, "app": 1, "adapters": 2, "infrastructure": 3}

def get_layer(module_path: str) -> int | None:
    parts = module_path.split('.')
    if len(parts) > 1 and parts[0] == 'chorus_engine':
        return LAYERS.get(parts[1])
    return None

def analyze_file_imports(file_path: Path) -> set:
    imports = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError:
            return imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith('chorus_engine'):
                    imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith('chorus_engine'):
                imports.add(node.module)
    return imports

def validate_dependency_rule(dependencies: dict) -> list:
    violations = []
    for module, deps in dependencies.items():
        source_layer = get_layer(module)
        if source_layer is None: continue
        for dep in deps:
            dep_layer = get_layer(dep)
            if dep_layer is None: continue
            if source_layer < dep_layer:
                violations.append(
                    f"Axiom 8 Violation: {module} (Layer {source_layer}) "
                    f"imports from {dep} (Layer {dep_layer})."
                )
    return violations

# --- Axiom 12: The Lexicographer (Acyclic Dependencies) ---
def validate_acyclic_dependencies(dependencies: dict) -> list:
    path, visited, violations = set(), set(), []
    sorted_modules = sorted(list(dependencies.keys()))

    def visit(module):
        path.add(module)
        visited.add(module)
        for neighbour in sorted(list(dependencies.get(module, []))):
            if neighbour in path:
                cycle_str = " -> ".join(list(path)[list(path).index(neighbour):]) + f" -> {neighbour}"
                violations.append(f"Axiom 12 Violation: Circular import detected: {cycle_str}")
            if neighbour not in visited:
                visit(neighbour)
        path.remove(module)

    for module in sorted_modules:
        if module not in visited:
            visit(module)
    return sorted(list(set(violations)))

# --- Axiom 32: The Quartermaster (Pragmatic Harvesting) ---
def validate_pragmatic_harvesting() -> list:
    violations = []
    harvester_files = list(HARVESTER_DIR.glob("*.py"))
    for file_path in harvester_files:
        if file_path.name == "__init__.py": continue
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("search_"):
                    arg_names = [arg.arg for arg in node.args.args]
                    if "max_results" not in arg_names:
                        violations.append(
                            f"Axiom 32 Violation in {file_path.name}: Method '{node.name}' "
                            f"must have a 'max_results' parameter."
                        )
    return violations

# --- Axiom 54: The Artificer (Lean Artifact) ---
def validate_lean_artifact() -> list:
    violations = []
    forbidden_copy = ["tests/", "tools/", "docs/", "Makefile", "pytest.ini"]
    forbidden_run = ["build-essential", "git", "gcc"]
    
    with open(DOCKERFILE_PATH, 'r') as f:
        lines = f.readlines()
    
    final_stage_index = -1
    for i, line in enumerate(lines):
        if line.strip().upper().startswith("FROM"):
            final_stage_index = i
            
    if final_stage_index != -1:
        for i, line in enumerate(lines[final_stage_index:], start=final_stage_index):
            line_upper = line.strip().upper()
            if line_upper.startswith("COPY"):
                for forbidden in forbidden_copy:
                    if forbidden in line:
                        violations.append(f"Axiom 54 Violation in Dockerfile (line {i+1}): Forbidden COPY of '{forbidden}' in final stage.")
            if line_upper.startswith("RUN"):
                for forbidden in forbidden_run:
                    if forbidden in line:
                        violations.append(f"Axiom 54 Violation in Dockerfile (line {i+1}): Forbidden installation of '{forbidden}' in final stage.")
    return violations

# --- Main Execution ---
def main():
    print("--- 🔱 CHORUS Office of the Constitutional Guardian ---")
    all_violations = []
    
    # Build dependency graph
    dependencies = defaultdict(set)
    py_files = sorted(list(SOURCE_DIR.rglob('*.py')))
    for file_path in py_files:
        module_name = str(file_path.relative_to(PROJECT_ROOT)).replace(os.sep, '.').removesuffix('.py')
        dependencies[module_name].update(analyze_file_imports(file_path))

    # Run Validators
    print("[*] The Architect is verifying the Dependency Rule (Axiom 8)...")
    all_violations.extend(validate_dependency_rule(dependencies))
    
    print("[*] The Lexicographer is verifying for Acyclic Dependencies (Axiom 12)...")
    all_violations.extend(validate_acyclic_dependencies(dependencies))

    print("[*] The Quartermaster is verifying Pragmatic Harvesting (Axiom 32)...")
    all_violations.extend(validate_pragmatic_harvesting())
    
    print("[*] The Artificer is verifying the Lean Artifact (Axiom 54)...")
    all_violations.extend(validate_lean_artifact())

    # Report Verdict
    if not all_violations:
        print("\n" + "="*80)
        print("✅ SUCCESS: All programmatic axioms verified. The Constitution is upheld.")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print(f"❌ FAILURE: Found {len(all_violations)} constitutional violation(s).")
        print("="*80)
        for v in sorted(all_violations):
            print(f"  - {v}")
        print("\n" + "="*80)
        sys.exit(1)

if __name__ == "__main__":
    main()