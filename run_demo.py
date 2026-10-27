"""
NexusCTI Interactive Demo Runner.
Executes multi-modal cyber-threat attribution and exports verifiable briefs.
"""

import sys
from pathlib import Path

# Ensure UTF-8 output on Windows terminals
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from nexuscti.service import get_service
from nexuscti.fusion.report_generator import AttributionReportGenerator
from nexuscti.config import ARTIFACTS_DIR


def main():
    print("=" * 70)
    print("[*] NEXUS-CTI: DUAL-LAYER ATTRIBUTION ENGINE DEMO")
    print("=" * 70)

    service = get_service()

    # Default incident query: Multi-hop secondary pivot from SolarWinds
    query = "185.225.17.42"
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])

    print(f"\n[+] Analyzing Incident Telemetry: '{query}'...")
    result = service.analyze(query)

    # Generate Reports
    md_report = AttributionReportGenerator.generate_markdown_report(result)
    json_report = AttributionReportGenerator.generate_json_report(result)

    # Save to artifacts
    md_path = ARTIFACTS_DIR / "attribution_brief.md"
    json_path = ARTIFACTS_DIR / "attribution_brief.json"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)

    import json
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_report, f, indent=2)

    print("\n" + md_report)
    print("=" * 70)
    print(f"✅ Attribution Brief exported to:\n  - Markdown: {md_path}\n  - JSON:     {json_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
