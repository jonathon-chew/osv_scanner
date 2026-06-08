from dataclasses import dataclass
from typing import Optional


@dataclass
class Vulnerability:
    id: str
    cve: Optional[str]
    summary: str
    cvss: Optional[float]
    fixed_version: Optional[str]


def _extract_cvss(severity_list):
    """
    CVSS could be in different styles, look for the type to get the right score
    CVSS 4 > CVSS 3 > CVSS 2
    """
    priority = ["CVSS_V4", "CVSS_V3", "CVSS_V2"]

    for p in priority:
        for sev in severity_list:
            if sev.get("type") == p:
                return float(sev["score"].split("/", 1)[0].split(":", 1)[1])

    return None


def parse_osv(response: dict) -> list[Vulnerability]:
    """
    Parse the OSV response for the relevent information, and print to the screen
    """
    vulns = []

    for item in response.get("vulns", []):
        cve = next((a for a in item.get("aliases", []) if a.startswith("CVE-")), None)

        cvss = _extract_cvss(item.get("severity", []))

        fixed = None
        for affected in item.get("affected", []):
            for r in affected.get("ranges", []):
                for event in r.get("events", []):
                    if "fixed" in event:
                        fixed = event["fixed"]
                        break

        vulns.append(
            Vulnerability(
                id=item["id"],
                cve=cve,
                summary=item.get("summary", ""),
                cvss=cvss,
                fixed_version=fixed,
            )
        )

    return vulns
