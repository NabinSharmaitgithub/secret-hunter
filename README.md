# secret-hunter

**secret-hunter** is a tool for performing authorized static analysis of software packages to find exposed API keys and secrets. It produces actionable, step-by-step remediation guides for each finding.

## IMPORTANT: Authorization Required

This tool is intended **ONLY** for lawful, authorized security assessments. Before running a scan, you will be required to confirm the following:

```
--------------------------------------------------------------------------------
IMPORTANT: AUTHORIZATION REQUIRED
--------------------------------------------------------------------------------
You are about to run a security analysis tool. Please confirm the following:

[ ] I have WRITTEN PERMISSION from the owner of the target system to perform this analysis.
[ ] I will ONLY use this tool for lawful, authorized security assessments.
[ ] I understand that unauthorized scanning is illegal and unethical.
[ ] I will NOT use this tool to bypass DRM, authentication, or other protections.

Type "I AUTHORIZE" to continue:
```

If you are fetching a remote source, you will also be required to confirm the license agreement.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/NabinSharmaitgithub/secret-hunter.git
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command-Line Interface (CLI)

#### Local Scanning

```bash
python -m secret_hunter.cli --target /path/to/your/project --confirm-authorization
```

#### Remote Scanning

```bash
python -m secret_hunter.cli --fetch --source-url "https://github.com/example/repo" --confirm-authorization --verify-license
```

### Graphical User Interface (GUI)

To launch the GUI, run:

```bash
python -m secret_hunter.gui
```

The GUI provides an easy-to-use interface for selecting a local target or specifying a remote URL to scan.

## Assumptions

- The tool is intended only for public/open-source projects or projects the user is authorized to download and analyze.
- Network downloads may be blocked in some environments; the tool will surface helpful errors.
- Default thresholds (e.g., max download size) are conservative and configurable.

## Safety Notes

- The fetcher will refuse to download anything unless the `--fetch` flag is provided.
- The fetcher will display size limits and require confirmation for large downloads.
- The fetcher will never attempt to access private endpoints without explicit credentials.
- Optional metadata enrichment (e.g., scraping for stars, READMEs) is not implemented by default and would require an explicit opt-in.
