import os
import re
import yaml
from math import log2

def calculate_entropy(text):
    """Calculates the Shannon entropy of a string."""
    if not text:
        return 0
    entropy = 0
    for char_code in range(256):
        char = chr(char_code)
        frequency = text.count(char) / len(text)
        if frequency > 0:
            entropy -= frequency * log2(frequency)
    return entropy

def scan_file(filepath, rules):
    """Scans a single file for secrets."""
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_number, line in enumerate(f, 1):
                for rule in rules:
                    if re.search(rule["regex"], line):
                        findings.append({
                            "id": rule["id"],
                            "file": filepath,
                            "line": line_number,
                            "snippet": line.strip(),
                            "type": rule["type"],
                            "confidence": rule["confidence"],
                        })
    except Exception as e:
        print(f"Error scanning file {filepath}: {e}")
    return findings

def scan_directory(directory, rules_file, whitelist_file, no_decompile, max_depth):
    """Scans a directory for secrets."""
    with open(rules_file, "r") as f:
        rules = yaml.safe_load(f)["rules"]

    findings = []
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            findings.extend(scan_file(filepath, rules))

    return findings
