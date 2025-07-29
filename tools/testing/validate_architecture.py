# Filename: tools/testing/validate_architecture.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This script programmatically validates the project's architecture against
# the rules defined in the CHORUS Constitution.

import os
import ast
from collections import defaultdict
import sys
from pathlib import Path

# Define the layers. Lower number is a higher-level policy (more central).
# This is the ground truth for our architecture.
LAYERS = {
    "core": 0,
    "app": 1,
    "adapters": 2,
    "infrastructure": 3,
}

def get_layer(module_path: str) -> int | None:
    """Determines the architectural layer of a given module path."""
    parts = module_path.split('.')
    if len(parts) > 1 and parts[0] == 'chorus_engine':
        component = parts[1]
        return LAYERS.get(component)
    return None

def analyze_imports(file_path: Path, project_root: Path) -> set:
    """Parses a Python file and returns a set of its internal project imports."""
    imports = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=str(file_path))
        except SyntaxError as e:
            print(f"Warning: Skipping file with syntax error: {file_path} - {e}", file=sys.stderr)
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

def check_dependency_rule(dependencies: dict) -> list:
    """Validates that all dependencies point inwards."""
    violations = []
    for module, deps in dependencies.items():
        source_layer = get_layer(module)
        if source_layer is None:
            continue
        for dep in deps:
            dep_layer = get_layer(dep)
            if dep_layer is None:
                continue
            if source_layer < dep_layer:
                violations.append(
                    f"Dependency Rule Violation: {module} (Layer {source_layer}) "
                    f"cannot import from {dep} (Layer {dep_layer})."
                )
    return violations

def check_acyclic_dependencies(dependencies: dict) -> list:
    """Checks for circular dependencies in the graph."""
    path = set()
    visited = set()
    violations = []

    def visit(module):
        path.add(module)
        visited.add(module)
        for neighbour in dependencies.get(module, []):
            # Only check cycles within our engine
            if not neighbour.startswith('chorus_engine'):
                continue
            if neighbour in path:
                cycle_path = list(path)
                try:
                    start_index = cycle_path.index(neighbour)
                    cycle_str = " -> ".join(cycle_path[start_index:]) + f" -> {neighbour}"
                    violations.append(f"Acyclic Dependency Violation: Circular import detected: {cycle_str}")
                except ValueError:
                    pass # Should not happen
                continue # Don't recurse further on a found cycle
            if neighbour not in visited:
                visit(neighbour)
        path.remove(module)

    sorted_modules = sorted(list(dependencies.keys()))
    for module in sorted_modules:
        if module not in visited:
            visit(module)
    
    return sorted(list(set(violations)))

def main():
    """Main function to run the architectural validation."""
    project_root = Path(__file__).resolve().parent.parent.parent
    source_dir = project_root / 'chorus_engine'
    
    dependencies = defaultdict(set)
    
    print("[*] Analyzing source files for imports...")
    py_files = sorted(list(source_dir.rglob('*.py')))

    for file_path in py_files:
        module_name = str(file_path.relative_to(project_root)).replace(os.sep, '.').removesuffix('.py')
        
        if module_name.endswith('__init__'):
            content = file_path.read_text(encoding='utf-8').strip()
            if not content or all(line.strip().startswith('#') for line in content.splitlines()):
                continue

        imports = analyze_imports(file_path, project_root)
        if imports:
            dependencies[module_name].update(imports)

    print("[+] Import analysis complete. Validating architecture...")
    
    dep_rule_violations = check_dependency_rule(dependencies)
    acyclic_violations = check_acyclic_dependencies(dependencies)
    
    all_violations = dep_rule_violations + acyclic_violations
    
    if not all_violations:
        print("\n" + "="*80)
        print("✅ SUCCESS: Architectural validation passed.")
        print("   - No illegal cross-layer dependencies found (Dependency Rule).")
        print("   - No circular dependencies found (Acyclic Dependencies Principle).")
        print("="*80)
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("❌ FAILURE: Architectural validation failed.")
        print("="*80)
        if dep_rule_violations:
            print("\n[!] Dependency Rule Violations (imports must point inwards):")
            for v in sorted(dep_rule_violations):
                print(f"  - {v}")
        if acyclic_violations:
            print("\n[!] Acyclic Dependency Violations (no circular imports allowed):")
            for v in sorted(acyclic_violations):
                print(f"  - {v}")
        print("\n" + "="*80)
        sys.exit(1)

if __name__ == "__main__":
    main()
