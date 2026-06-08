from datetime import datetime, timezone
import json
import random
import time

import requests

from parse_osv import parse_osv
import log


def make_request(version:str, package_name:str, ecosystem: str, VERBOSE: bool, DEBUG: bool = False):
    """
    Make a request to the OSV database for the package, version and eco system
    """
    # Load # {"version": "2.4.1", "package": {"name": "jinja2", "ecosystem": "PyPI"}}
    payload = {"version": f"{version}", "package": {"name": f"{package_name}", "ecosystem": f"{ecosystem}"}}

    if DEBUG:
        print(payload)
        return

    # Being a good citizen
    time.sleep(random.randrange(0, 2))

    r = requests.post(url="https://api.osv.dev/v1/query", data=json.dumps(payload))

    log.log(f"TIME: {datetime.now(timezone.utc)} | REQUEST: {json.dumps(payload)} | STATUS: {r.status_code}")

    r.raise_for_status()

    with open(f"./docs/{package_name}_response.json", "w") as w:
        w.write(json.dumps(r.json()))

    if len(r.json().keys()) == 0:
        if VERBOSE:
            print(f"No issues with {package_name} on version {version}")
        return
    else:
        print(f"Issue with {package_name} on version {version}")

    for vuln in parse_osv(r.json()):
        print(f"{vuln.id}")
        print(f"  CVE: {vuln.cve}")
        print(f"  Score: {vuln.cvss}")
        print(f"  Fixed in: {vuln.fixed_version}")
        print()
