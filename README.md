# OSV Scanner

I built this project as a small command-line security scanner for Python dependency files. It walks a directory tree, finds dependency manifests such as `requirements.txt`, sends each pinned package/version to the public [OSV](https://osv.dev/) vulnerability database, and prints a compact summary of any known issues.

The goal was to practise building a practical developer tool around a real external API: file discovery, request construction, response parsing, logging, and human-readable terminal output.

## What It Does

- Recursively scans from a user-provided base directory.
- Detects Python dependency files including `requirements.txt`.
- Supports both traditional pinned requirement lines and JSON-style package lists.
- Queries the OSV `/v1/query` API with package name, version, and ecosystem.
- Writes raw API responses to `docs/<package>_response.json` for inspection.
- Logs request payloads, timestamps, and HTTP status codes to `docs/log.log`.
- Parses OSV responses into a small `Vulnerability` dataclass containing the OSV id, CVE alias, parsed CVSS value, and fixed version when available.

## Why I Built It

I wanted a project that was small enough to understand quickly but realistic enough to show how I approach production-adjacent tooling. This scanner demonstrates that I can break a workflow into focused modules, interact with third-party APIs, preserve useful audit artifacts, and present results in a way that a developer could act on.

## Project Structure

```text
osv_scanner/
├── src/osv_scanner/
│   ├── __main__.py        # CLI argument parsing and entry point
│   ├── find_files.py      # Recursive file discovery and dependency parsing
│   ├── make_requests.py   # OSV API requests, logging, and output handling
│   ├── parse_osv.py       # OSV response parsing into typed vulnerability objects
│   └── log.py             # Append-only request logging
├── docs/                  # Saved OSV responses and request log
├── tests/
├── requirements.txt
└── README.md
```

## Requirements

```bash
pip install requests
```

The scanner expects dependency lines in this form:

```text
requests==2.34.2
urllib3==2.7.0
```

## How To Use It

From the project root:

```bash
python src/osv_scanner/__main__.py --base-location /path/to/project --verbose
```

Example target project:

```text
example-app/
└── requirements.txt
```

Example `requirements.txt`:

```text
Flask==3.1.3
Jinja2==3.1.6
requests==2.34.2
urllib3==2.7.0
```

Run the scan:

```bash
python src/osv_scanner/__main__.py --base-location ./example-app --verbose
```

## Sample Output

When the scanner finds a dependency file and OSV returns no vulnerabilities, the output looks like this:

```text
Found requirements.txt in ./example-app
No issues with Flask on version 3.1.3
No issues with Jinja2 on version 3.1.6
No issues with requests on version 2.34.2
No issues with urllib3 on version 2.7.0
```

When OSV returns vulnerabilities, the scanner prints the package, OSV id, CVE alias, parsed CVSS value, and fixed version:

```text
Found requirements.txt in ./example-app
Issue with vulnerable-package on version 1.0.0
OSV-2024-123
  CVE: CVE-2024-12345
  Score: 3.1
  Fixed in: 1.0.1
```

The scanner also saves raw API responses for later review:

```text
docs/Flask_response.json
docs/Jinja2_response.json
docs/requests_response.json
docs/urllib3_response.json
```

And it appends each API call to `docs/log.log`:

```text
TIME: 2026-06-06 20:16:38.596413+00:00 | REQUEST: {"version": "2.34.2", "package": {"name": "requests", "ecosystem": "PyPI"}} | STATUS: 200
TIME: 2026-06-06 20:16:38.862097+00:00 | REQUEST: {"version": "2.7.0", "package": {"name": "urllib3", "ecosystem": "PyPI"}} | STATUS: 200
```

## Code Example

The CLI is the main interface, but the core parser can also be used directly with an OSV-style response dictionary:

```python
from src.osv_scanner.parse_osv import parse_osv

response = {
    "vulns": [
        {
            "id": "OSV-2024-123",
            "aliases": ["CVE-2024-12345"],
            "summary": "Example vulnerability",
            "severity": [
                {"type": "CVSS_V3", "score": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"}
            ],
            "affected": [
                {
                    "ranges": [
                        {"events": [{"introduced": "0"}, {"fixed": "1.0.1"}]}
                    ]
                }
            ],
        }
    ]
}

for vuln in parse_osv(response):
    print(vuln.id)
    print(vuln.cve)
    print(vuln.cvss)
    print(vuln.fixed_version)
```

Sample output:

```text
OSV-2024-123
CVE-2024-12345
3.1
1.0.1
```

## What This Demonstrates

This project reflects how I work on developer tooling:

- I separate CLI handling, filesystem traversal, API calls, logging, and response parsing into focused modules.
- I keep raw API responses available so results can be audited instead of disappearing into terminal output.
- I use typed data structures where they make downstream code easier to reason about.
- I design the tool around a real-world workflow: scanning project dependencies before reviewing, shipping, or maintaining code.

## Current Scope

The scanner currently focuses on Python dependency discovery and OSV lookups for pinned package versions. The file walker includes placeholders for other ecosystems such as Go modules, which gives the project a clear path for future expansion.
