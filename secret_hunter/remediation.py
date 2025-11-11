import json

def generate_report(findings, output_file):
    """Generates a JSON report of the findings."""
    report = {
        "findings": findings
    }
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report generated at {output_file}")
