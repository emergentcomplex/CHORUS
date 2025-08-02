# Filename: tools/analysis/calculate_slos.py
#
# 🔱 CHORUS Autonomous OSINT Engine
#
# This tool parses the structured SLI logs and the canonical SLO document
# to generate a report on the system's performance against its targets.

import json
import re
from pathlib import Path
from collections import defaultdict
import numpy as np

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SLO_DOC_PATH = PROJECT_ROOT / "docs/03_SYSTEM_SLOS.md"
SLI_LOG_PATH = PROJECT_ROOT / "logs/sli.log"

def parse_slo_document():
    """Parses the markdown SLO document to extract targets."""
    if not SLO_DOC_PATH.exists():
        raise FileNotFoundError(f"SLO document not found at: {SLO_DOC_PATH}")

    targets = {"latency": {}, "success": {}}
    with open(SLO_DOC_PATH, 'r') as f:
        content = f.read()

    # Use regex to find the latency and success tables
    latency_table_match = re.search(r"### 4.1. Latency SLOs\n\n(.*?)\n\n###", content, re.DOTALL)
    success_table_match = re.search(r"### 4.2. Availability & Success SLOs\n\n(.*?)\n\n###", content, re.DOTALL)

    if latency_table_match:
        for line in latency_table_match.group(1).splitlines():
            if line.startswith("| **"):
                parts = [p.strip().replace('**', '') for p in line.split('|')]
                if len(parts) > 3:
                    component, target_str = parts[1], parts[3]
                    value = float(re.findall(r'[\d\.]+', target_str)[0])
                    if "minute" in target_str:
                        value *= 60 * 1000  # Convert minutes to ms
                    targets["latency"][component] = value

    if success_table_match:
        for line in success_table_match.group(1).splitlines():
            if line.startswith("| **"):
                parts = [p.strip().replace('**', '') for p in line.split('|')]
                if len(parts) > 3:
                    component, target_str = parts[1], parts[3]
                    value = float(re.findall(r'[\d\.]+', target_str)[0])
                    targets["success"][component] = value
    
    return targets

def analyze_sli_logs():
    """Parses the JSON SLI log file and calculates actual metrics."""
    if not SLI_LOG_PATH.exists():
        print(f"Warning: SLI log file not found at {SLI_LOG_PATH}. No data to analyze.")
        return None

    latencies = defaultdict(list)
    success_counts = defaultdict(lambda: {'success': 0, 'total': 0})

    with open(SLI_LOG_PATH, 'r') as f:
        for line in f:
            try:
                log = json.loads(line)
                if log.get('name') != 'sli' or 'component' not in log:
                    continue
                
                component = log['component']

                if 'latency_ms' in log:
                    latencies[component].append(log['latency_ms'])
                elif 'latency_seconds' in log:
                    latencies[component].append(log['latency_seconds'] * 1000)

                if 'success' in log:
                    success_counts[component]['total'] += 1
                    if log['success']:
                        success_counts[component]['success'] += 1

            except (json.JSONDecodeError, KeyError):
                continue

    actuals = {"latency": {}, "success": {}}
    for component, values in latencies.items():
        if values:
            actuals["latency"][component] = np.percentile(values, 95)

    # Aggregate success rates for components with sub-types (e.g., J-ANLZ)
    aggregated_success = defaultdict(lambda: {'success': 0, 'total': 0})
    for component, counts in success_counts.items():
        # Generalize the aggregation: if a component name has a '(', it's a sub-type.
        base_component = component.split(' (')[0]
        aggregated_success[base_component]['success'] += counts['success']
        aggregated_success[base_component]['total'] += counts['total']

    final_success_rates = {
        comp: (data['success'] / data['total']) * 100
        for comp, data in aggregated_success.items() if data['total'] > 0
    }
    actuals["success"] = final_success_rates

    return actuals

def generate_report(targets, actuals):
    """Prints a formatted report comparing targets to actuals."""
    print("="*80)
    print("🔱 CHORUS Service Level Objective (SLO) Report 🔱")
    print("="*80)

    print("\n--- Latency (p95) ---")
    print(f"{'Component':<30} | {'Target':<15} | {'Actual':<15} | {'Status':<10}")
    print("-"*80)
    for component, target_ms in sorted(targets['latency'].items()):
        actual_ms = actuals.get('latency', {}).get(component)
        if actual_ms is not None:
            status = "✅ PASS" if actual_ms <= target_ms else "❌ FAIL"
            target_str = f"< {target_ms:,.0f}ms"
            actual_str = f"{actual_ms:,.0f}ms"
            print(f"{component:<30} | {target_str:<15} | {actual_str:<15} | {status:<10}")
        else:
            print(f"{component:<30} | {'< ' + str(int(target_ms)) + 'ms':<15} | {'N/A':<15} | {'(No Data)':<10}")

    print("\n--- Success Rate ---")
    print(f"{'Component':<30} | {'Target':<10} | {'Actual':<10} | {'Status':<10}")
    print("-"*80)
    for component, target_pct in sorted(targets['success'].items()):
        # Check for aggregated actuals (e.g., J-ANLZ)
        actual_pct = actuals.get('success', {}).get(component.split(' (')[0])
        if actual_pct is not None:
            status = "✅ PASS" if actual_pct >= target_pct else "❌ FAIL"
            target_str = f"> {target_pct:.1f}%"
            actual_str = f"{actual_pct:.1f}%"
            print(f"{component:<30} | {target_str:<10} | {actual_str:<10} | {status:<10}")
        else:
            print(f"{component:<30} | {'> ' + str(target_pct) + '%':<10} | {'N/A':<10} | {'(No Data)':<10}")
    
    print("\n" + "="*80)


def main():
    try:
        targets = parse_slo_document()
        actuals = analyze_sli_logs()
        if actuals:
            generate_report(targets, actuals)
        else:
            print("No SLI data found to generate a report.")
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
