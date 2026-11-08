from datetime import datetime, timezone
import json
import os
import random
import time
from dataclasses import dataclass, asdict
from typing import Optional

import requests

import log


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


def _parse_osv(response: dict) -> list[Vulnerability]:
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


def make_request(
    version: str,
    package_name: str,
    ecosystem: str,
    file_name: str,
    root_folder: str,
    VERBOSE: bool,
    DEBUG: bool = False,
):
    """
    Make a request to the OSV database for the package, version and eco system
    """
    # Load # {"version": "2.4.1", "package": {"name": "jinja2", "ecosystem": "PyPI"}}
    payload = {
        "version": f"{version}",
        "package": {"name": f"{package_name}", "ecosystem": f"{ecosystem}"},
    }

    if DEBUG:
        print(payload)
        return

    # Being a good citizen
    time.sleep(random.randrange(0, 2))

    docs_folder = f"{os.path.sep}".join(
        os.path.split(os.path.dirname(os.path.realpath(__file__)))[:-2]
    )
    record_of_request_file = (
        f"./{docs_folder}/docs/{package_name}_response_{version}.json"
    )

    r = "" # just to stop pylance from complaining
    status = "" # just to stop pylance from complaining

    # (#1) TODO: Add a command for no cache so it always requests fresh
    # (#2) TODO: Add a command for how long ago the file could be cached, and a default of say a month
    if not os.path.exists(record_of_request_file):
        req = requests.post(
            url="https://api.osv.dev/v1/query", data=json.dumps(payload)
        )
        req.raise_for_status()
        r = req.json()
        status = req.status_code

        with open(record_of_request_file, "w") as w:
            w.write(json.dumps(r))
    else:
        try:
            with open(record_of_request_file, "r") as rr:
                r = json.loads(rr.read())
                status = "file"
        except:
            os.remove(record_of_request_file)
            make_request(
                version=version,
                package_name=package_name,
                ecosystem=ecosystem,
                file_name=file_name,
                root_folder=root_folder,
                VERBOSE=VERBOSE,
                DEBUG=DEBUG,
            )

    full_file_path = os.path.join(root_folder, file_name)

    log.log(
        f"TIME: {datetime.now(timezone.utc)} | REQUEST: {json.dumps(payload)} | STATUS: {status} | FILE: {full_file_path}",
        full_file_path,
    )

    if isinstance(r, dict):
        if len(r.keys()) == 0:
            if VERBOSE:
                print(f"No issues with {package_name} on version {version}")
            return
        else:
            print(f"Issue with {package_name} on version {version}")

        for vuln in _parse_osv(r):
            print(f"{vuln.id}")
            print(f"  CVE: {vuln.cve}")
            print(f"  Score: {vuln.cvss}")
            print(f"  Fixed in: {vuln.fixed_version}")
            print()

            log.log(json.dumps(asdict(vuln)), full_file_path)
    else:
        print(f"[ERROR]: could not parse information, {r}")
