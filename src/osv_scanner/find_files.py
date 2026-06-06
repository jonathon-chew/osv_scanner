import os
import time
import random
import json
from collections import defaultdict

import make_requests

def find(location: str, VERBOSE: bool):

    python_files = ["pyvenv.cfg", "bin/activate", "poetry.lock", "Pipfile.lock", "conda-meta/", "requirements.txt"]
    versions: dict[str, str] = defaultdict()

    for root, _, files in os.walk(location):
        
        for file in files:
            file_name = os.path.join(root, file)
            
            if file in python_files or file == "go.mod":
                with open(file_name, "r") as r:
                    contents = r.read()
            else:
                continue

            if VERBOSE:
                print(f"Found {file} in {root}")

            match file:
                case "pyvenv.cfg":
                    pass
                case "bin/activate":
                    pass
                case "poetry.lock":
                    pass
                case "Pipfile.lock":
                    pass
                case "conda-meta/":
                    pass
                case "requirements.txt":
                    for package in contents.split("\n"):
                        if "=" in package and not contents[0] == "[":
                            package_name, version = package.split("==", 2)

                            remember_package = f"{package_name}_{version}"

                            if versions.get(remember_package, None) == version:
                                # Already checked
                                if VERBOSE:
                                    print("Already checked: ", remember_package)
                                break
                            else:
                                versions[remember_package] = version

                            make_requests.make_request(version=version, package_name=package_name, ecosystem="PyPI", VERBOSE=VERBOSE)
                        if contents[0] == "[": # Checking for is this pip list --format=JSON
                            json_file = json.loads(contents)
                            for each_pacakge in json_file:
                                make_requests.make_request(version=each_pacakge.get("version"), package_name=each_pacakge.get("name"), ecosystem="PyPi", VERBOSE=VERBOSE)
                case "go.mod":
                    # to impliment
                    pass
                    """ for package in contents.split("\n"):
                        _, package_name, version = package.split(" ")
                        make_requests.make_request(version=version, package_name=package_name, ecosystem="Go") """
                case _:
                    pass

            time.sleep(random.randrange(0, 2))